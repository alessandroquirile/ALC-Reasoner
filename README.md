# ALC-Reasoner

An $\mathcal{ALC}$ (Attributive Language with Complements) satisfiability reasoner implemented using the tableau method. This project provides tools for reasoning about Description Logic knowledge bases, featuring lazy unfolding and blocking techniques to handle cycles.

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ALC-Reasoner
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install .
   ```

## Usage

You can use the reasoner through the provided entry points. Example:

```bash
python main.py
```

## Running Tests

To run the test suite and verify the implementation:

```bash
python -m unittest discover tests
```
## Theoretical Background
For an in-depth explanation of Description Logics, $\mathcal{ALC}$, and the tableau method, please refer to [THEORY.md](THEORY.md).