from typing import Optional, Set, Dict, List, Any

from src.core.concept import Bottom, Top, Negation


class Node:
    """
    Represents a node in the tableau expansion (an individual in the interpretation domain Δᴵ).
    
    Attributes:
        id: Unique identifier for the node.
        ancestor: Parent node in the tableau tree.
        labels: Set of concepts L(x) that this individual belongs to.
        successors: Successors in the interpretation Rᴵ.
        blocked_by: The ancestor node that blocks this node.
    """

    def __init__(self, identifier: str, ancestor: Optional['Node'] = None):
        self.id = identifier
        self.ancestor = ancestor
        self.labels: Set[Any] = set()
        self.successors: Dict[str, List['Node']] = {}
        self.blocked_by: Optional['Node'] = None

    def has_clash(self) -> bool:
        """
        Checks if the node contains a contradiction.
        Conditions:
        - ⊥ ∈ L(x)
        - ¬⊤ ∈ L(x)
        - {C, ¬C} ⊆ L(x)
        """
        # Clash: ⊥ ∈ L(x) or ¬⊤ ∈ L(x)
        if Bottom() in self.labels or Negation(Top()) in self.labels:
            return True

        for label in self.labels:
            match label:
                # Clash: {C, ¬C} ⊆ L(x)
                case Negation(concept):
                    if concept in self.labels:
                        return True
                case _:
                    if Negation(label) in self.labels:
                        return True
        return False

    def is_blocked(self) -> bool:
        """
        Subset Blocking Rule:
        xⱼ is blocked by xᵢ iff L(xⱼ) ⊆ L(xᵢ) and xᵢ is an ancestor of xⱼ.
        """
        current_ancestor = self.ancestor
        while current_ancestor:
            # Check L(xⱼ) ⊆ L(xᵢ)
            if self.labels.issubset(current_ancestor.labels):
                self.blocked_by = current_ancestor
                return True
            current_ancestor = current_ancestor.ancestor
        return False

    def __repr__(self):
        return f"Node({self.id}, labels={self.labels})"
