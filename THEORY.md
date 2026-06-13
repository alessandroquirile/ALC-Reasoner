# Theoretical Background

The goal of this project is to implement a satisfiability reasoner for $\mathcal{ALC}$ (Attributive Language with Complements) description logic using the tableau method.

## Why Description Logics?
First-order logic (FOL) is highly expressive but generally undecidable. The Halting Problem, a fundamental result in theoretical computer science, implies that there is no general algorithm to decide the validity of an arbitrary FOL formula. This makes building automated reasoners for full FOL impractical for many applications.

Description Logics (DLs) are fragments of FOL designed to be decidable. They provide a structured way to represent knowledge, balancing expressiveness and computational tractability.

## Knowledge Base Components
A DL knowledge base consists of:
* TBox (Terminological Box): Contains definitions of concepts (e.g., `Man ≡ Human ⊓ Male`).
* RBox (Role Box): (Not explicitly used in basic $\mathcal{ALC}$) Contains axioms about roles (e.g., transitivity).
* ABox (Assertional Box): Contains assertions about individuals (e.g., `John : Man`).

## What is $\mathcal{ALC}$?
$\mathcal{ALC}$ is a DL which extends basic concept languages ($\mathcal{AL}$) with full negation, conjunction, disjunction, and existential/universal quantification.

Formal syntax:

$$
C, D =
$$

where $A$ is an atomic concept.

$\mathcal{ALC}$ is more expressive than simpler DLs like $\mathcal{EL}$ (which lacks negation) but less expressive than full FOL because it restricts how quantifiers can be used (specifically, it doesn't allow arbitrary variable linking).

## Interpretations and Models
An interpretation $\mathcal{I} = (\Delta^\mathcal{I}, \cdot^\mathcal{I})$ consists of a non-empty domain $\Delta^\mathcal{I}$ and an interpretation function $\cdot^\mathcal{I}$ that maps atomic concepts to subsets of $\Delta^\mathcal{I}$ and roles to binary relations on $\Delta^\mathcal{I} \times \Delta^\mathcal{I}$. A model for a knowledge base is an interpretation that satisfies all axioms in the TBox and ABox.

## The Tableau Method
The tableau method checks satisfiability by constructing a model (or discovering a contradiction) through systematically decomposing concepts.

### Derivation Sequence
The method constructs a sequence of completion trees $S_0 \to S_1 \to \dots \to S_n$, where:
* $S_0$ is the initial tree consisting of a single node $x_0$ with label $\mathcal{L}(x_0) = \{ C \}$.
* Each step $S_i \to S_{i+1}$ applies an expansion rule.
* $S_n$ is a complete tree, meaning no further expansion rules can be applied.

### Clashes and Satisfiability
A completion tree contains a clash if any of its nodes contains a contradiction (e.g., $\perp \in \mathcal{L}(x)$ or $\{ A, \neg A \} \subseteq \mathcal{L}(x)$ for some atomic concept $A$). A completion tree is clash-free if it does not contain any clash.

Because the disjunction rule ($\sqcup$) is non-deterministic, the algorithm searches a tree of alternative completion trees (search branches). The concept $C$ is satisfiable if and only if there exists at least one complete and clash-free completion tree $S_n$ derivable from $S_0$.

### Blocking
To ensure termination in the presence of cycles (e.g., TBox axioms like $C \sqsubseteq \exists R.C$), the algorithm uses blocking techniques, which detect if the tableau construction is repeating a state, thus preventing infinite expansion. A node $x_j$ is blocked by an ancestor $x_i$ if $x_i$ is an ancestor of $x_j$ and:
$$ \mathcal{L}(x_j) \subseteq \mathcal{L}(x_i) $$
where $\mathcal{L}(x)$ denotes the set of concepts asserted at node $x$.

## Formal Properties and Complexity

### Soundness and Completeness
The tableau method for $\mathcal{ALC}$ is:
* Sound: If the tableau method finds a complete and clash-free completion tree (which represents a model), then the input concept is satisfiable.
* Complete: If the input concept is satisfiable, then the tableau method is guaranteed to find at least one complete and clash-free completion tree.

### Complexity
Concept satisfiability in $\mathcal{ALC}$ without a TBox (or with only acyclic TBoxes) is PSPACE-complete. However, when general TBoxes (GCIs) are permitted, concept satisfiability becomes EXPTIME-complete. Because this reasoner supports general TBoxes (necessitating blocking to handle cycles), the worst-case complexity of the problem it solves is EXPTIME-complete.
