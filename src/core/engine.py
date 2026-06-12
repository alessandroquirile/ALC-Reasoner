from typing import Set, Dict, Any, Optional

from src.core.concept import Concept, AtomicConcept, Negation, Intersection, Union, Existential, Universal
from src.core.node import Node


class TableauEngine:
    """
    ALC Tableau Reasoner Engine.
    
    Implements expansion rules for:
    - ⊓ (Intersection): Intersection(C, D)
    - ⊔ (Union): Union(C, D)
    - ∃ (Existential): Existential(R, C)
    - ∀ (Universal): Universal(R, C)
    - ¬ (Negation): Negation(C)
    - ⊤ (Top): Top()
    - ⊥ (Bottom): Bottom()
    - Optional TBox GCIs: C ⊑ D (handled via Union(Negation(C), D))
    """

    def __init__(self, tbox: Set[Concept]):
        self.tbox_rules = {rule.to_nnf() for rule in tbox}
        self.node_count = 0
        self.root: Optional[Node] = None

    def create_node(self, concept: Optional[Concept] = None, ancestor: Optional[Node] = None) -> Node:
        self.node_count += 1
        node = Node(f"x{self.node_count}", ancestor)
        if concept:
            node.labels.add(concept)
        for rule in self.tbox_rules:
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
            return False

        if node.is_blocked():
            return True

        # Rule Selection using Pattern Matching
        for label in list(node.labels):
            match label:
                # ⊓-rule (Deterministic Intersection)
                case Intersection(left, right):
                    if left not in node.labels or right not in node.labels:
                        node.labels.add(left)
                        node.labels.add(right)
                        return self.expand(node)

                # ⊔-rule (Non-deterministic Union)
                case Union(left, right):
                    if left not in node.labels and right not in node.labels:
                        orig_labels = node.labels.copy()
                        node.labels.add(left)
                        if self.expand(node):
                            return True
                        # Backtrack
                        node.labels = orig_labels
                        node.labels.add(right)
                        return self.expand(node)

                # ∀-rule (Universal Restriction)
                case Universal(role, concept):
                    if role in node.successors:
                        changed = False
                        for successor in node.successors[role]:
                            if concept not in successor.labels:
                                successor.labels.add(concept)
                                changed = True
                        if changed:
                            # Re-verify all affected successors
                            for successor in node.successors[role]:
                                if not self.expand(successor):
                                    return False

                # ∃-rule (Existential Restriction)
                case Existential(role, concept):
                    exists_satisfied = False
                    if role in node.successors:
                        for succ in node.successors[role]:
                            if concept in succ.labels:
                                exists_satisfied = True
                                break

                    if not exists_satisfied:
                        new_node = self.create_node(ancestor=node)
                        new_node.labels.add(concept)
                        # Propagate existing ∀-restrictions to the new successor
                        for l in node.labels:
                            match l:
                                case Universal(r, c) if r == role:
                                    new_node.labels.add(c)

                        if role not in node.successors:
                            node.successors[role] = []
                        node.successors[role].append(new_node)

                        if not self.expand(new_node):
                            return False

        return True

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

            domain.add(node.id)

            for label in node.labels:
                match label:
                    case AtomicConcept(name):
                        if name not in concept_interpretations:
                            concept_interpretations[name] = set()
                        concept_interpretations[name].add(node.id)

            for role, successors in node.successors.items():
                if role not in role_interpretations:
                    role_interpretations[role] = set()
                for succ in successors:
                    target_id = succ.blocked_by.id if succ.blocked_by else succ.id
                    role_interpretations[role].add((node.id, target_id))
                    if not succ.blocked_by:
                        nodes_to_visit.append(succ)

        return {
            "domain": domain,
            "concepts": concept_interpretations,
            "roles": role_interpretations,
            "tbox": self.tbox_rules
        }
