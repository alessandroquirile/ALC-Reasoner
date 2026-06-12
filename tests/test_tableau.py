import unittest

from src.core.concept import AtomicConcept, Intersection, Negation, Existential, Universal, Top, Bottom, Union
from src.core.engine import TableauEngine


class TestALCReasoner(unittest.TestCase):

    def test_basic_clash(self):
        # A ⊓ ¬A is unsatisfiable
        engine = TableauEngine(tbox=set())
        A = AtomicConcept("A")
        self.assertFalse(engine.check_satisfiability(Intersection(A, Negation(A))))

    def test_intersection_satisfiable(self):
        # A ⊓ B is satisfiable
        engine = TableauEngine(tbox=set())
        A, B = AtomicConcept("A"), AtomicConcept("B")
        self.assertTrue(engine.check_satisfiability(Intersection(A, B)))
        model = engine.get_model()
        self.assertIn("A", model["concepts"])
        self.assertIn("B", model["concepts"])

    def test_blocking_infinite_path(self):
        # TBox: A ⊑ ∃R.A
        # Concept: A
        A = AtomicConcept("A")
        tbox = {Union(Negation(A), Existential("R", A))}
        engine = TableauEngine(tbox=tbox)
        self.assertTrue(engine.check_satisfiability(A))
        model = engine.get_model()
        self.assertEqual(len(model["domain"]), 1)
        self.assertIn(("x1", "x1"), model["roles"]["R"])

    def test_universal_restriction(self):
        # Concept: (∀R.A) ⊓ (∃R.B) ⊓ (∀R.¬B)
        # Should be unsatisfiable because R-successor must have both B and ¬B
        engine = TableauEngine(tbox=set())
        A, B = AtomicConcept("A"), AtomicConcept("B")
        concept = Intersection(
            Universal("R", A),
            Intersection(Existential("R", B), Universal("R", Negation(B)))
        )
        self.assertFalse(engine.check_satisfiability(concept))

    def test_user_requested_case(self):
        # Concept: A ⊓ B
        # TBox: A ⊑ ∃R.(A ⊓ B)
        A, B = AtomicConcept("A"), AtomicConcept("B")
        tbox = {Union(Negation(A), Existential("R", Intersection(A, B)))}
        engine = TableauEngine(tbox=tbox)
        self.assertTrue(engine.check_satisfiability(Intersection(A, B)))
        model = engine.get_model()
        self.assertIn("x1", model["domain"])
        self.assertIn(("x1", "x1"), model["roles"]["R"])

    def test_top_and_bottom(self):
        # Top is always satisfiable
        engine = TableauEngine(tbox=set())
        self.assertTrue(engine.check_satisfiability(Top()))

        # Bottom is always unsatisfiable
        engine = TableauEngine(tbox=set())
        self.assertFalse(engine.check_satisfiability(Bottom()))

        # A and not top is unsatisfiable
        engine = TableauEngine(tbox=set())
        self.assertFalse(engine.check_satisfiability(Intersection(AtomicConcept("A"), Negation(Top()))))

    def test_union_cases(self):
        # A ⊔ B is satisfiable
        engine = TableauEngine(tbox=set())
        A, B = AtomicConcept("A"), AtomicConcept("B")
        self.assertTrue(engine.check_satisfiability(Union(A, B)))

        # (A ⊔ B) ⊓ ¬A ⊓ ¬B is unsatisfiable
        engine = TableauEngine(tbox=set())
        concept = Intersection(Union(A, B), Intersection(Negation(A), Negation(B)))
        self.assertFalse(engine.check_satisfiability(concept))

        # ¬A ⊓ (A ⊔ B) is satisfiable (should choose the B branch)
        engine = TableauEngine(tbox=set())
        concept = Intersection(Negation(A), Union(A, B))
        self.assertTrue(engine.check_satisfiability(concept))
        model = engine.get_model()
        self.assertIn("B", model["concepts"])
        self.assertNotIn("A", model["concepts"])


if __name__ == '__main__':
    unittest.main()
