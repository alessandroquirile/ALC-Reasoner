import unittest

from src.core.concept import (
    AtomicConcept,
    Intersection,
    Union,
    Negation,
    Existential,
    Universal,
    Top,
    Bottom,
    GCI,
    Equivalence
)
from src.core.parser import parse_concept, parse_tbox, ParseError


class TestALCParser(unittest.TestCase):

    def test_basic_concepts(self):
        # Constants
        self.assertEqual(parse_concept("⊤"), Top())
        self.assertEqual(parse_concept("top"), Top())
        self.assertEqual(parse_concept("TOP"), Top())
        self.assertEqual(parse_concept("⊥"), Bottom())
        self.assertEqual(parse_concept("bottom"), Bottom())
        self.assertEqual(parse_concept("BOTTOM"), Bottom())

        # Atomic Concepts
        self.assertEqual(parse_concept("Human"), AtomicConcept("Human"))
        self.assertEqual(parse_concept("Parent_Concept"), AtomicConcept("Parent_Concept"))

    def test_unary_and_binary_operators(self):
        A = AtomicConcept("A")
        B = AtomicConcept("B")

        # Negation
        self.assertEqual(parse_concept("¬A"), Negation(A))
        self.assertEqual(parse_concept("~A"), Negation(A))
        self.assertEqual(parse_concept("!A"), Negation(A))
        self.assertEqual(parse_concept("not A"), Negation(A))

        # Conjunction
        self.assertEqual(parse_concept("A ⊓ B"), Intersection(A, B))
        self.assertEqual(parse_concept("A & B"), Intersection(A, B))
        self.assertEqual(parse_concept("A and B"), Intersection(A, B))

        # Disjunction
        self.assertEqual(parse_concept("A ⊔ B"), Union(A, B))
        self.assertEqual(parse_concept("A | B"), Union(A, B))
        self.assertEqual(parse_concept("A or B"), Union(A, B))

    def test_quantifiers(self):
        A = AtomicConcept("A")

        # Existential
        self.assertEqual(parse_concept("∃R.A"), Existential("R", A))
        self.assertEqual(parse_concept("exists R.A"), Existential("R", A))
        self.assertEqual(parse_concept("∃ R . A"), Existential("R", A))

        # Universal
        self.assertEqual(parse_concept("∀R.A"), Universal("R", A))
        self.assertEqual(parse_concept("forall R.A"), Universal("R", A))
        self.assertEqual(parse_concept("∀ R . A"), Universal("R", A))

    def test_operator_precedence(self):
        A = AtomicConcept("A")
        B = AtomicConcept("B")
        C = AtomicConcept("C")

        # ∃R.A ⊓ B should parse as (∃R.A) ⊓ B (if quantified is higher than intersection)
        # In the grammar, quantified is a child of intersection, so ∃R.A ⊓ B is Intersection(Existential(R, A), B)
        self.assertEqual(
            parse_concept("∃R.A ⊓ B"),
            Intersection(Existential("R", A), B)
        )

        # ¬∃R.A should parse as ¬(∃R.A)
        self.assertEqual(
            parse_concept("¬∃R.A"),
            Negation(Existential("R", A))
        )

        # ∃R.¬A should parse as ∃R.(¬A)
        self.assertEqual(
            parse_concept("∃R.¬A"),
            Existential("R", Negation(A))
        )

        # Conjunction binds tighter than disjunction: A ⊓ B ⊔ C -> (A ⊓ B) ⊔ C
        self.assertEqual(
            parse_concept("A ⊓ B ⊔ C"),
            Union(Intersection(A, B), C)
        )

    def test_parentheses(self):
        A = AtomicConcept("A")
        B = AtomicConcept("B")
        C = AtomicConcept("C")

        # (A ⊔ B) ⊓ C
        self.assertEqual(
            parse_concept("(A ⊔ B) ⊓ C"),
            Intersection(Union(A, B), C)
        )

        # ∃R.(A ⊓ B)
        self.assertEqual(
            parse_concept("∃R.(A ⊓ B)"),
            Existential("R", Intersection(A, B))
        )

    def test_tbox_axioms(self):
        A = AtomicConcept("A")
        B = AtomicConcept("B")

        # Inclusion (GCI): A ⊑ B
        expected_gci = {GCI(A, B)}
        self.assertEqual(parse_tbox("A ⊑ B"), expected_gci)
        self.assertEqual(parse_tbox("A <= B"), expected_gci)
        self.assertEqual(parse_tbox("A sub B"), expected_gci)

        # Equivalence: A ≡ B
        expected_equiv = {Equivalence(A, B)}
        self.assertEqual(parse_tbox("A ≡ B"), expected_equiv)
        self.assertEqual(parse_tbox("A = B"), expected_equiv)
        self.assertEqual(parse_tbox("A eq B"), expected_equiv)

    def test_tbox_multi_axiom(self):
        A = AtomicConcept("A")
        B = AtomicConcept("B")
        C = AtomicConcept("C")

        # Multiple axioms separated by semicolon
        tbox = parse_tbox("A ⊑ B; B ⊑ C")
        expected = {GCI(A, B), GCI(B, C)}
        self.assertEqual(tbox, expected)

        # Multiple axioms separated by newline
        tbox = parse_tbox("A ⊑ B\nB ⊑ C")
        self.assertEqual(tbox, expected)

    def test_tbox_comments(self):
        tbox_text = """
        # Comment
        A ⊑ B // Line comment
        B ≡ C
        """
        A = AtomicConcept("A")
        B = AtomicConcept("B")
        C = AtomicConcept("C")
        expected = {
            GCI(A, B),
            Equivalence(B, C)
        }
        self.assertEqual(parse_tbox(tbox_text), expected)

    def test_error_handling(self):
        # Incomplete formulas
        with self.assertRaises(ParseError):
            parse_concept("A ⊓")

        with self.assertRaises(ParseError):
            parse_concept("∃R.")

        # Unmatched parentheses
        with self.assertRaises(ParseError):
            parse_concept("(A ⊓ B")

        # Invalid characters
        with self.assertRaises(ParseError):
            parse_concept("A % B")


if __name__ == '__main__':
    unittest.main()
