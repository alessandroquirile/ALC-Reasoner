from src.core.concept import AtomicConcept, Intersection, Negation, Existential, Union
from src.core.engine import TableauEngine
from src.utils.printer import pretty

if __name__ == '__main__':
    # Concept: A ⊓ B
    A = AtomicConcept("A")
    B = AtomicConcept("B")
    concept = Intersection(A, B)

    # TBox: A ⊑ ∃R.(A ⊓ B) eq ¬A ⊔ ∃R.(A ⊓ B)
    tbox = {
        Union(
            Negation(A),
            Existential("R", Intersection(A, B))
        )
    }

    engine = TableauEngine(tbox)

    print(f"Checking satisfiability of {concept} with TBox: {tbox}")

    if engine.check_satisfiability(concept):
        print("Satisfiable")
        pretty(engine.get_model())
    else:
        print("Unsatisfiable")
