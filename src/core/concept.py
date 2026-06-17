from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Concept:
    """Base class for all ALC concepts."""

    def to_nnf(self) -> 'Concept':
        """Converts the concept to Negation Normal Form (NNF)."""
        return self

    def __repr__(self):
        return self.__class__.__name__


@dataclass(frozen=True)
class Top(Concept):
    def __repr__(self):
        return "⊤"


@dataclass(frozen=True)
class Bottom(Concept):
    def __repr__(self):
        return "⊥"


@dataclass(frozen=True)
class AtomicConcept(Concept):
    name: str

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class Negation(Concept):
    concept: Concept

    def to_nnf(self) -> 'Concept':
        match self.concept:
            case Negation(c):
                return c.to_nnf()
            case Intersection(l, r):
                return Union(Negation(l).to_nnf(), Negation(r).to_nnf())
            case Union(l, r):
                return Intersection(Negation(l).to_nnf(), Negation(r).to_nnf())
            case Existential(role, c):
                return Universal(role, Negation(c).to_nnf())
            case Universal(role, c):
                return Existential(role, Negation(c).to_nnf())
            case Top():
                return Bottom()
            case Bottom():
                return Top()
            case _:
                return self

    def __repr__(self):
        return f"¬{self.concept}"


@dataclass(frozen=True)
class Intersection(Concept):
    left: Concept
    right: Concept

    def to_nnf(self) -> 'Concept':
        return Intersection(self.left.to_nnf(), self.right.to_nnf())

    def __repr__(self):
        return f"({self.left} ⊓ {self.right})"


@dataclass(frozen=True)
class Union(Concept):
    left: Concept
    right: Concept

    def to_nnf(self) -> 'Concept':
        return Union(self.left.to_nnf(), self.right.to_nnf())

    def __repr__(self):
        return f"({self.left} ⊔ {self.right})"


@dataclass(frozen=True)
class Existential(Concept):
    role: str
    concept: Concept

    def to_nnf(self) -> 'Concept':
        return Existential(self.role, self.concept.to_nnf())

    def __repr__(self):
        return f"∃{self.role}.{self.concept}"


@dataclass(frozen=True)
class Universal(Concept):
    role: str
    concept: Concept

    def to_nnf(self) -> 'Concept':
        return Universal(self.role, self.concept.to_nnf())

    def __repr__(self):
        return f"∀{self.role}.{self.concept}"


@dataclass(frozen=True)
class Axiom:
    """Base class for TBox axioms."""

    def internalize(self) -> Concept:
        """Converts the axiom to its internalized concept representation in NNF."""
        raise NotImplementedError


@dataclass(frozen=True)
class GCI(Axiom):
    """
    General Concept Inclusion: left ⊑ right
    Internalized as: ¬left ⊔ right
    """
    left: Concept
    right: Concept

    def internalize(self) -> Concept:
        return Union(Negation(self.left), self.right).to_nnf()

    def __repr__(self):
        return f"{self.left} ⊑ {self.right}"


@dataclass(frozen=True)
class Equivalence(Axiom):
    """
    Concept Equivalence: left ≡ right
    Internalized as: (¬left ⊔ right) ⊓ (¬right ⊔ left)
    """
    left: Concept
    right: Concept

    def internalize(self) -> Concept:
        c1 = Union(Negation(self.left), self.right)
        c2 = Union(Negation(self.right), self.left)
        return Intersection(c1, c2).to_nnf()

    def __repr__(self):
        return f"{self.left} ≡ {self.right}"
