import unittest

from src.core.concept import AtomicConcept, Intersection, Negation, GCI, Equivalence
from src.core.engine import TableauEngine
from src.core.parser import parse_tbox


class TestLazyUnfolding(unittest.TestCase):

    def test_partitioning_simple(self):
        # A ≡ B ⊓ C should be in Tu
        tbox = parse_tbox("A ≡ B ⊓ C")
        engine = TableauEngine(tbox)
        A = AtomicConcept("A")
        self.assertIn(A, engine.tu_equiv)
        self.assertEqual(len(engine.tg_internalized), 0)

    def test_partitioning_general(self):
        # A ⊓ B ⊑ C should be in Tg because LHS is not atomic
        tbox = parse_tbox("A ⊓ B ⊑ C")
        engine = TableauEngine(tbox)
        self.assertEqual(len(engine.tu_equiv), 0)
        self.assertEqual(len(engine.tu_incl), 0)
        self.assertEqual(len(engine.tg_internalized), 1)

    def test_acyclic_check(self):
        # A ≡ B; B ≡ A should result in both in Tg (or at least the one that closes the cycle)
        tbox = parse_tbox("A ≡ B; B ≡ A")
        engine = TableauEngine(tbox)
        # One might be in Tu, but the other MUST be in Tg to avoid cycle
        self.assertEqual(len(engine.tu_equiv) + len(engine.tu_incl) + len(engine.tg_internalized), 2)
        # Total axioms processed = 2
        # If one is in Tu, say A ≡ B, then B ≡ A causes cycle and goes to Tg
        self.assertTrue(len(engine.tg_internalized) >= 1)

    def test_r1_unfolding(self):
        # TBox: A ≡ B
        # Concept: A ⊓ ¬B
        # Rule R1 should add B to L(x) if A is present, leading to clash with ¬B
        A, B = AtomicConcept("A"), AtomicConcept("B")
        tbox = {Equivalence(A, B)}
        engine = TableauEngine(tbox)
        self.assertFalse(engine.check_satisfiability(Intersection(A, Negation(B))))

    def test_r2_unfolding(self):
        # TBox: A ≡ B
        # Concept: ¬A ⊓ B
        # Rule R2 should add ¬B to L(x) if ¬A is present, leading to clash with B
        A, B = AtomicConcept("A"), AtomicConcept("B")
        tbox = {Equivalence(A, B)}
        engine = TableauEngine(tbox)
        self.assertFalse(engine.check_satisfiability(Intersection(Negation(A), B)))

    def test_r3_unfolding(self):
        # TBox: A ⊑ B
        # Concept: A ⊓ ¬B
        # Rule R3 should add B to L(x) if A is present, leading to clash with ¬B
        A, B = AtomicConcept("A"), AtomicConcept("B")
        tbox = {GCI(A, B)}
        engine = TableauEngine(tbox)
        self.assertFalse(engine.check_satisfiability(Intersection(A, Negation(B))))

    def test_lazy_not_unfolding_unnecessarily(self):
        # TBox: A ≡ B
        # Concept: C
        # A should NOT be unfolded because it's not in the labels
        A, B, C = AtomicConcept("A"), AtomicConcept("B"), AtomicConcept("C")
        tbox = {Equivalence(A, B)}
        engine = TableauEngine(tbox)
        self.assertTrue(engine.check_satisfiability(C))
        model = engine.get_model()
        self.assertNotIn("A", model["concepts"])
        self.assertNotIn("B", model["concepts"])

    def test_complex_acyclic_tu(self):
        # A ≡ B ⊓ C
        # B ≡ D
        # This is acyclic.
        tbox = parse_tbox("A ≡ B ⊓ C; B ≡ D")
        engine = TableauEngine(tbox)
        self.assertEqual(len(engine.tu_equiv), 2)
        self.assertEqual(len(engine.tg_internalized), 0)

        # Check satisfiability of A ⊓ ¬D
        # A unfolding -> B ⊓ C
        # B unfolding -> D
        # D ⊓ ¬D -> Clash
        A, D = AtomicConcept("A"), AtomicConcept("D")
        self.assertFalse(engine.check_satisfiability(Intersection(A, Negation(D))))


if __name__ == '__main__':
    unittest.main()
