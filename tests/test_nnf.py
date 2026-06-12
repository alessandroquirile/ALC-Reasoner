import unittest

from src.core.concept import AtomicConcept, Intersection, Union, Negation, Existential, Universal, Top, Bottom


class TestNNF(unittest.TestCase):
    def setUp(self):
        self.A = AtomicConcept("A")
        self.B = AtomicConcept("B")

    def test_atomic(self):
        self.assertEqual(self.A.to_nnf(), self.A)
        self.assertEqual(Negation(self.A).to_nnf(), Negation(self.A))

    def test_double_negation(self):
        # ¬¬A -> A
        self.assertEqual(Negation(Negation(self.A)).to_nnf(), self.A)

    def test_de_morgan_and(self):
        # ¬(A ⊓ B) -> ¬A ⊔ ¬B
        concept = Negation(Intersection(self.A, self.B))
        expected = Union(Negation(self.A), Negation(self.B))
        self.assertEqual(concept.to_nnf(), expected)

    def test_de_morgan_or(self):
        # ¬(A ⊔ B) -> ¬A ⊓ ¬B
        concept = Negation(Union(self.A, self.B))
        expected = Intersection(Negation(self.A), Negation(self.B))
        self.assertEqual(concept.to_nnf(), expected)

    def test_existential_negation(self):
        # ¬∃R.A -> ∀R.¬A
        concept = Negation(Existential("R", self.A))
        expected = Universal("R", Negation(self.A))
        self.assertEqual(concept.to_nnf(), expected)

    def test_universal_negation(self):
        # ¬∀R.A -> ∃R.¬A
        concept = Negation(Universal("R", self.A))
        expected = Existential("R", Negation(self.A))
        self.assertEqual(concept.to_nnf(), expected)

    def test_top_bottom_negation(self):
        self.assertEqual(Negation(Top()).to_nnf(), Bottom())
        self.assertEqual(Negation(Bottom()).to_nnf(), Top())

    def test_complex_nnf(self):
        # ¬(∃R.(A ⊓ ¬B)) -> ∀R.(¬A ⊔ B)
        concept = Negation(Existential("R", Intersection(self.A, Negation(self.B))))
        expected = Universal("R", Union(Negation(self.A), self.B))
        self.assertEqual(concept.to_nnf(), expected)


if __name__ == '__main__':
    unittest.main()
