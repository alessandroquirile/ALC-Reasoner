# ALC-Reasoner

An $\mathcal{ALC}$ (Attributive Language with Complements) satisfiability reasoner implemented using the tableau method.

This project provides tools for reasoning about Description Logic knowledge bases, featuring lazy unfolding and blocking
techniques to handle cycles.

## Installation

Clone this repository, create and activate a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

The reasoner can be used by defining concepts and TBox axioms as strings. You can use both Unicode symbols and ASCII aliases:

- Unicode: `⊓`, `⊔`, `¬`, `∃`, `∀`, `⊑`, `≡`
- ASCII: `and`, `or`, `not`, `exists`, `forall`, `sub`, `eq`

Example in `main.py`:

```python3
from src.core.parser import parse_concept, parse_tbox
from src.core.engine import TableauEngine
from src.utils.printer import pretty

# Define concept and TBox using either symbols or ASCII aliases
concept = parse_concept("Parent ⊓ Woman")
tbox = parse_tbox("Parent ⊑ (Human ⊓ ∃hasChild.Human)")

# Define the Tableau engine
engine = TableauEngine(tbox)

# Check SAT
is_satisfiable = engine.check_satisfiability(concept)

# Display the satisfying model (interpretation ℐ)
if is_satisfiable: 
    pretty(engine.get_model())
```

To run the example:

```bash
python main.py
```

## Running Tests

To run the test suite and verify the implementation:

```bash
python -m unittest discover tests
```

## Theoretical Background

For an in-depth explanation of Description Logics, $\mathcal{ALC}$, and the tableau method, please refer
to [THEORY.md](THEORY.md).