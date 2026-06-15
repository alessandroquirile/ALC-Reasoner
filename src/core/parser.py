from typing import Set

from lark import Lark, Transformer, v_args

from src.core.concept import (
    Concept,
    AtomicConcept,
    Intersection,
    Union,
    Negation,
    Existential,
    Universal,
    Top,
    Bottom
)

# ALC Grammar in EBNF
ALC_GRAMMAR = r"""
    ?start: concept
          | tbox

    tbox: (axiom [";"])*

    ?axiom: concept "⊑" concept -> gci
          | concept "<=" concept -> gci
          | concept "sub" concept -> gci
          | concept "≡" concept -> equiv
          | concept "=" concept -> equiv
          | concept "eq" concept -> equiv

    ?concept: union

    ?union: intersection
           | union ("⊔" | "|" | "or") intersection -> union_op

    ?intersection: quantified
                  | intersection ("⊓" | "&" | "and") quantified -> intersection_op

    ?quantified: "∃" ID "." quantified -> existential_op
               | "exists" ID "." quantified -> existential_op
               | "∀" ID "." quantified -> universal_op
               | "forall" ID "." quantified -> universal_op
               | negated

    ?negated: ("¬" | "~" | "!" | "not") quantified -> negation_op
            | primary

    ?primary: "(" concept ")"
            | "⊤" -> top
            | "top"i -> top
            | "⊥" -> bottom
            | "bottom"i -> bottom
            | ID -> atomic

    ID: /[a-zA-Z_][a-zA-Z0-9_]*/

    %import common.WS
    %import common.CPP_COMMENT
    %import common.SH_COMMENT
    %ignore WS
    %ignore CPP_COMMENT
    %ignore SH_COMMENT
"""


@v_args(inline=True)
class ALCTransformer(Transformer):
    def atomic(self, name):
        return AtomicConcept(str(name))

    def top(self):
        return Top()

    def bottom(self):
        return Bottom()

    def negation_op(self, concept):
        return Negation(concept)

    def intersection_op(self, left, right):
        return Intersection(left, right)

    def union_op(self, left, right):
        return Union(left, right)

    def existential_op(self, role, concept):
        return Existential(str(role), concept)

    def universal_op(self, role, concept):
        return Universal(str(role), concept)

    def gci(self, left, right):
        # C ⊑ D translates to ¬C ⊔ D
        return Union(Negation(left), right)

    def equiv(self, left, right):
        # C ≡ D translates to (¬C ⊔ D) and (¬D ⊔ C)
        return [Union(Negation(left), right), Union(Negation(right), left)]

    def tbox(self, *axioms):
        flattened = []
        for ax in axioms:
            if isinstance(ax, list):
                flattened.extend(ax)
            else:
                flattened.append(ax)
        return set(flattened)

    def start(self, result):
        return result


class ParseError(Exception):
    """Exception raised for syntax and parsing errors in ALC formulas."""
    pass


def parse_concept(text: str) -> Concept:
    """
    Parses a string representation of an ALC concept.
    """
    try:
        # For single concept, we use a specific parser to avoid tbox ambiguity
        concept_parser = Lark(ALC_GRAMMAR, start='concept', parser='lalr', transformer=ALCTransformer())
        return concept_parser.parse(text)
    except Exception as e:
        raise ParseError(f"Error parsing concept '{text}': {e}")


def parse_tbox(text: str) -> Set[Concept]:
    """
    Parses a multiline TBox string containing GCIs or Equivalences.
    """
    try:
        tbox_parser = Lark(ALC_GRAMMAR, start='tbox', parser='lalr', transformer=ALCTransformer())
        return tbox_parser.parse(text)
    except Exception as e:
        raise ParseError(f"Error parsing TBox: {e}")
