from typing import Set, Dict, Any, Optional, List

from src.core.concept import (
    Concept,
    AtomicConcept,
    Intersection,
    Union,
    Negation,
    Existential,
    Universal,
    Axiom,
    GCI,
    Equivalence
)
from src.core.node import Node


class TableauEngine:
    """
    ALC Tableau Reasoner Engine with Lazy Unfolding optimization.
    
    Lazy Unfolding partitions the TBox into:
    - Tu (Unfoldable): Definitions of the form A ≡ C or A ⊑ C (A atomic, unique, acyclic).
    - Tg (General): All other axioms.
    
    Expansion rules for:
    - ⊓, ⊔, ∃, ∀, ¬, ⊤, ⊥
    - Tg (General axioms): Handled via internalization.
    - Tu (Unfoldable axioms): Handled via lazy rules R1, R2, R3.
    """

    def __init__(self, tbox: Set[Axiom]):
        self.tu_equiv: Dict[AtomicConcept, Concept] = {}  # A ≡ C
        self.tu_incl: Dict[AtomicConcept, List[Concept]] = {}  # A ⊑ C
        self.tg_internalized: Set[Concept] = set()

        self._partition_tbox(tbox)

        self.node_count = 0
        self.root: Optional[Node] = None

    def _partition_tbox(self, tbox: Set[Axiom]):
        """
        Partitions the TBox into Tu (unfoldable) and Tg (general).
        Unicode: Tu ⊎ Tg = T
        """
        for axiom in tbox:
            if isinstance(axiom, (GCI, Equivalence)) and isinstance(axiom.left, AtomicConcept):
                # Try adding to Tu
                lhs = axiom.left
                if lhs not in self.tu_equiv and lhs not in self.tu_incl:
                    # Potential candidate for Tu
                    if isinstance(axiom, Equivalence):
                        self.tu_equiv[lhs] = axiom.right.to_nnf()
                    else:
                        self.tu_incl[lhs] = [axiom.right.to_nnf()]

                    if self._is_acyclic():
                        continue  # Keep in Tu
                    else:
                        # Revert
                        if isinstance(axiom, Equivalence):
                            del self.tu_equiv[lhs]
                        else:
                            del self.tu_incl[lhs]

            # If not suitable for Tu or causes cycle, add to Tg
            self.tg_internalized.add(axiom.internalize())

    def _is_acyclic(self) -> bool:
        """Checks if the current Tu definitions are acyclic."""
        adj = {}
        all_lhs = set(self.tu_equiv.keys()) | set(self.tu_incl.keys())
        for lhs in all_lhs:
            rhs_concepts = []
            if lhs in self.tu_equiv:
                rhs_concepts.append(self.tu_equiv[lhs])
            if lhs in self.tu_incl:
                rhs_concepts.extend(self.tu_incl[lhs])

            adj[lhs] = set()
            for concept in rhs_concepts:
                adj[lhs].update(self._get_atomic_concepts(concept) & all_lhs)

        # Cycle detection using DFS
        visited = set()
        path = set()

        def has_cycle(u):
            visited.add(u)
            path.add(u)
            for v in adj.get(u, []):
                if v not in visited:
                    if has_cycle(v):
                        return True
                elif v in path:
                    return True
            path.remove(u)
            return False

        for node in adj:
            if node not in visited:
                if has_cycle(node):
                    return False
        return True

    def _get_atomic_concepts(self, concept: Concept) -> Set[AtomicConcept]:
        """Helper to extract all atomic concepts from a concept."""
        atomics = set()
        match concept:
            case AtomicConcept():
                atomics.add(concept)
            case Negation(c):
                atomics.update(self._get_atomic_concepts(c))
            case Intersection(l, r) | Union(l, r):
                atomics.update(self._get_atomic_concepts(l))
                atomics.update(self._get_atomic_concepts(r))
            case Existential(_, c) | Universal(_, c):
                atomics.update(self._get_atomic_concepts(c))
        return atomics

    def create_node(self, concept: Optional[Concept] = None, ancestor: Optional[Node] = None) -> Node:
        """
        Creates a new node in the tableau.
        """
        node = Node(f"x{self.node_count}", ancestor)
        self.node_count += 1
        if concept:
            node.labels.add(concept)
        for rule in self.tg_internalized:
            node.labels.add(rule)
        return node

    def check_satisfiability(self, concept: Concept) -> bool:
        """
        Main entry point for checking satisfiability of a concept.
        Returns True if a clash-free completion exists.
        """
        nnf_concept = concept.to_nnf()
        self.root = self.create_node(nnf_concept)
        return self.expand(self.root)

    def expand(self, node: Node) -> bool:
        """
        Expands the tableau for a given node.
        Returns True if a clash-free completion exists.
        """
        if node.has_clash():
            node.status = 'clashed'
            return False

        if node.is_blocked():
            node.status = 'blocked'
            return True

        # Apply Lazy Unfolding rules (R1, R2, R3)
        if self._apply_lazy_unfolding_rules(node):
            return self.expand(node)

        for label in list(node.labels):
            match label:
                case Intersection():
                    result = self._apply_intersection_rule(node, label)
                case Union():
                    result = self._apply_union_rule(node, label)
                case Universal():
                    result = self._apply_universal_rule(node, label)
                case Existential():
                    result = self._apply_existential_rule(node, label)
                case _:
                    result = None

            if result is not None:
                if not result:
                    node.status = 'clashed'
                else:
                    node.status = 'satisfiable'
                return result

        node.status = 'satisfiable'
        return True

    def _apply_lazy_unfolding_rules(self, node: Node) -> bool:
        """
        Applies Lazy Unfolding rules:
        R1: If A ∈ L(x), (A ≡ C) ∈ Tu, C ∉ L(x) then L(x) = L(x) ∪ {C}
        R2: If ¬A ∈ L(x), (A ≡ C) ∈ Tu, ¬C ∉ L(x) then L(x) = L(x) ∪ {¬C}
        R3: If A ∈ L(x), (A ⊑ C) ∈ Tu, C ∉ L(x) then L(x) = L(x) ∪ {C}
        Returns True if any rule was applied.
        """
        changed = False
        for label in list(node.labels):
            match label:
                case AtomicConcept() as a:
                    # R1: A ∈ L(x) and (A ≡ C) ∈ Tu
                    if a in self.tu_equiv:
                        definition = self.tu_equiv[a]
                        if definition not in node.labels:
                            node.labels.add(definition)
                            changed = True
                    # R3: A ∈ L(x) and (A ⊑ C) ∈ Tu
                    if a in self.tu_incl:
                        for inclusion in self.tu_incl[a]:
                            if inclusion not in node.labels:
                                node.labels.add(inclusion)
                                changed = True
                case Negation(AtomicConcept() as a):
                    # R2: ¬A ∈ L(x) and (A ≡ C) ∈ Tu
                    if a in self.tu_equiv:
                        neg_definition = Negation(self.tu_equiv[a]).to_nnf()
                        if neg_definition not in node.labels:
                            node.labels.add(neg_definition)
                            changed = True
        return changed

    def _apply_intersection_rule(self, node: Node, label: Intersection) -> Optional[bool]:
        """
        Apply the ⊓-rule (Deterministic Intersection).
        Formal: If (C ⊓ D) ∈ L(x) and {C, D} ⊈ L(x), then L(x) = L(x) ∪ {C, D}.
        """
        if not {label.left, label.right}.issubset(node.labels):
            node.labels.update({label.left, label.right})
            return self.expand(node)
        return None

    def _apply_union_rule(self, node: Node, label: Union) -> Optional[bool]:
        """
        Apply the ⊔-rule (Non-deterministic Union) with visual forking.
        Formal: If (C ⊔ D) ∈ L(x) and {C, D} ∩ L(x) = ∅, then create two branches.
        """
        if {label.left, label.right}.isdisjoint(node.labels):
            # Create left branch node
            node_left = self.clone_node(node, f"{node.id}a")
            node_left.labels.add(label.left)

            # Create right branch node
            node_right = self.clone_node(node, f"{node.id}b")
            node_right.labels.add(label.right)

            # Record them as branch successors of the parent node
            node.branch_successors = [node_left, node_right]

            # Expand left branch
            left_res = self.expand(node_left)

            # Expand right branch
            right_res = self.expand(node_right)

            # Set parent status based on branches
            if left_res or right_res:
                node.status = 'satisfiable'
                return True
            else:
                node.status = 'clashed'
                return False
        return None

    def _apply_universal_rule(self, node: Node, label: Universal) -> Optional[bool]:
        """
        Apply the ∀-rule (Universal Restriction).
        Formal: If (∀R.C) ∈ L(x) and y is an R-successor of x and C ∉ L(y), then L(y) = L(y) ∪ {C}.
        """
        if label.role in node.successors:
            changed = False
            for successor in node.successors[label.role]:
                if label.concept not in successor.labels:
                    successor.labels.add(label.concept)
                    changed = True
            if changed:
                for successor in list(node.successors[label.role]):
                    if not self.expand(successor):
                        node.successors[label.role].remove(successor)
                        if not node.successors[label.role]:
                            del node.successors[label.role]
                        if label.role not in node.failed_successors:
                            node.failed_successors[label.role] = []
                        node.failed_successors[label.role].append(successor)
                        successor.status = 'clashed'
                        return False
        return None

    def _apply_existential_rule(self, node: Node, existential: Existential) -> Optional[bool]:
        """
        Apply the ∃-rule (Existential Restriction).
        Formal: If (∃R.C) ∈ L(x) and x has no R-successor y with C ∈ L(y), then create new y with L(y) = {C}.
        """
        exists_satisfied = False
        if existential.role in node.successors:
            for successor in node.successors[existential.role]:
                if existential.concept in successor.labels:
                    exists_satisfied = True
                    break

        if not exists_satisfied:
            new_node = self.create_node(ancestor=node)
            new_node.labels.add(existential.concept)
            # Propagate existing ∀-restrictions to the new successor: L(y) = L(y) ∪ {D | (∀R.D) ∈ L(x)}
            for label in node.labels:
                match label:
                    case Universal(role, concept) if role == existential.role:
                        new_node.labels.add(concept)

            if existential.role not in node.successors:
                node.successors[existential.role] = []

            node.successors[existential.role].append(new_node)

            if not self.expand(new_node):
                node.successors[existential.role].remove(new_node)
                if not node.successors[existential.role]:
                    del node.successors[existential.role]
                if existential.role not in node.failed_successors:
                    node.failed_successors[existential.role] = []
                node.failed_successors[existential.role].append(new_node)
                new_node.status = 'clashed'
                return False

        return None

    def clone_node(self, node: Node, new_id: str, new_ancestor: Optional[Node] = None,
                   clone_map: Optional[dict] = None) -> Node:
        """
        Recursively clones a node and its descendants to fork the expansion tree,
        updating ancestor links.
        """
        if clone_map is None:
            clone_map = {}

        ancestor = new_ancestor if new_ancestor is not None else node.ancestor
        cloned = Node(new_id, ancestor)
        cloned.original_id = node.original_id
        cloned.labels = node.labels.copy()
        cloned.status = node.status

        # Map original node to cloned node
        clone_map[node] = cloned

        # Clone successors
        for role, successors in node.successors.items():
            cloned.successors[role] = []
            for i, succ in enumerate(successors):
                cloned_succ = self.clone_node(succ, f"{new_id}_{role}_{i}", new_ancestor=cloned, clone_map=clone_map)
                cloned.successors[role].append(cloned_succ)

        # Clone failed successors
        for role, failed in node.failed_successors.items():
            cloned.failed_successors[role] = []
            for i, succ in enumerate(failed):
                cloned_succ = self.clone_node(succ, f"{new_id}_failed_{role}_{i}", new_ancestor=cloned,
                                              clone_map=clone_map)
                cloned.failed_successors[role].append(cloned_succ)

        # Clone branch successors
        cloned.branch_successors = []
        for i, succ in enumerate(node.branch_successors):
            cloned_succ = self.clone_node(succ, f"{new_id}_branch_{i}", new_ancestor=cloned, clone_map=clone_map)
            cloned.branch_successors.append(cloned_succ)

        # Update blocked_by: if blocked_by is in clone_map, use the cloned version
        if node.blocked_by:
            cloned.blocked_by = clone_map.get(node.blocked_by, node.blocked_by)

        return cloned

    def get_model(self, root: Optional[Node] = None) -> Dict[str, Any]:
        """
        Extracts the Interpretation ℐ = (Δᴵ, ⋅ᴵ) from a completed tableau.
        """
        target_root = root or self.root

        if not target_root:
            raise ValueError("No root node available. Run check_satisfiability first.")

        nodes_to_visit = [target_root]
        visited = set()
        domain = set()
        concept_interpretations: Dict[str, Set[str]] = {}
        role_interpretations: Dict[str, Set[tuple]] = {}

        while nodes_to_visit:
            node = nodes_to_visit.pop(0)
            if node.id in visited:
                continue
            visited.add(node.id)

            if node.blocked_by:
                continue

            # If node has branch successors, follow the satisfying branch
            if node.branch_successors:
                for succ in node.branch_successors:
                    if succ.status != 'clashed':
                        nodes_to_visit.append(succ)
                        break  # Only follow one satisfying branch
                continue

            domain.add(node.original_id)

            for label in node.labels:
                match label:
                    case AtomicConcept(name):
                        if name not in concept_interpretations:
                            concept_interpretations[name] = set()
                        concept_interpretations[name].add(node.original_id)

            for role, successors in node.successors.items():
                if role not in role_interpretations:
                    role_interpretations[role] = set()
                for succ in successors:
                    target_id = succ.blocked_by.original_id if succ.blocked_by else succ.original_id
                    role_interpretations[role].add((node.original_id, target_id))
                    if not succ.blocked_by:
                        nodes_to_visit.append(succ)

        return {
            "domain": domain,
            "concepts": concept_interpretations,
            "roles": role_interpretations,
            "tu_equiv": self.tu_equiv,
            "tu_incl": self.tu_incl,
            "tg": self.tg_internalized
        }
