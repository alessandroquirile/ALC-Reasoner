from src.core.concept import AtomicConcept, Intersection, Negation, Existential, Union
from src.core.engine import TableauEngine
from src.utils.printer import pretty
from src.utils.visualizer import Visualizer

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

    is_satisfiable = engine.check_satisfiability(concept)

    if is_satisfiable:
        print("Satisfiable")
        pretty(engine.get_model())
    else:
        print("Unsatisfiable")

    # Generate visual representation of the Tableau
    if engine.root:
        visualizer = Visualizer()
        visualizer.save_png(engine.root, "output/tableau.png", "output/tableau.dot")
