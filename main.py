from src.core.engine import TableauEngine
from src.core.parser import parse_concept, parse_tbox
from src.utils.printer import pretty
from src.utils.visualizer import Visualizer

if __name__ == '__main__':
    # You can define concepts and TBoxes using both Unicode (⊓, ⊔, ¬, ∃, ∀, ⊑, ≡)
    # and ASCII aliases (and, or, not, exists, forall, sub, eq).

    # Defining Concept: Parent ⊓ Woman
    concept = parse_concept("Parent ⊓ Woman")

    # Defining TBox: Parent ⊑ (Human ⊓ ∃hasChild.Human)
    # This rule means: "Every parent must be a human and have at least one child who is also a human."
    # The satisfiability check asks: "Is it logically possible to have an individual who is both a parent and a woman,
    # while adhering to this rule?"
    tbox = parse_tbox("Parent ⊑ (Human ⊓ ∃hasChild.Human)")

    # Defining Tableau Engine
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
