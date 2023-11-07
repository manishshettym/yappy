# Formal definitions:

# Data Dependence Graph
We formally define the data dependence graph
of a program as a directed program graph where each node is an
instructiom and there is an edge from node B to node A iff
node B is data dependent on node A.

## Data Dependence
Node B is data dependent on another node A, if there is a variable v
in `Def(A)` and `Use(B)` such that A is a `reaching definition` of v at B.

where:
- `Def(A)` is the set of all variables defined at A.
- `Use(B)` is the set of all variables used at B.
- A is a `reaching definition` of v at B, if A defines variable v 
and there is no other definition of v between A and B.

NOTE: we are only considering flow-dependence (RAW) here. We are not
considering anti-dependence and output-dependence because they
are not relevant for other analyses in this project (e.g. slicing).


# Control Dependence Graph
We formally define the control dependence graph
of a program as a directed program graph where each node is an
instructiom and there is an edge from node B to node A iff
node B is control dependent on node A.


## Control Dependence
Node B is control dependent on another node A, iff:
1. there exists a directed path from A to B in the control flow graph,
such that any C in the path is `post-dominated` by B; and
2. A is not post-dominated by B.

where:
- A is `post-dominated` by B, iff every path from B to the exit node
contains A.


# Program Dependence Graph
We formally define the program dependence graph
of a program as a directed program graph where each node is an
instructiom and there is an edge from node B to node A iff
node B is program dependent on node A.

## Program Dependence
Node B is program dependent on another node A, iff:
1. B is data dependent on A; or
2. B is control dependent on A.
