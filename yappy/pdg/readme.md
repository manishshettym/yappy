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

- $cond_1$: there exists a directed path from A to B in the control flow graph,
such that any C in the path is `post-dominated` by B; and

- $cond_2$: A is not post-dominated by B.

where: A is `post-dominated` by B, iff every path from B to the exit node
contains A.

### Implementation Logic:

Given, a CFG we add control dependence edges from some node B to A.

From $cond_1$, there must be a path from A to B in the CFG.

From $cond_2$, A must not not be post-dominated by B ==> there is a path from A to {end} that does not contain B. ==> A must have two exit edges:
- Following one will result in B being executed.
- Following the other may result in B not being executed.

Therefore:
1. A must be a branch node! So for a given node B, we need to find all branch nodes A that occur before B in the CFG.
2. Lastly we need to check that any C in the path from A to B is post-dominated by B.



# Program Dependence Graph
We formally define the program dependence graph
of a program as a directed program graph where each node is an
instructiom and there is an edge from node B to node A iff
node B is program dependent on node A.

## Program Dependence
Node B is program dependent on another node A, iff:
1. B is data dependent on A; or
2. B is control dependent on A.


#### References:
1. [Program Dependence Graphs](https://www.cs.utexas.edu/~pingali/CS395T/2009fa/papers/ferrante87.pdf)
2. [Construcing PDG](https://compilers.cs.uni-saarland.de/teaching/spa/2014/slides/ProgramDependenceGraph.pdf)
3. [Control Dependence Graphs](https://home.cs.colorado.edu/~kena/classes/5828/s00/lectures/lecture15.pdf)
4. [Control Flow Analysis](https://web.cse.ohio-state.edu/~rountev.1/788/lectures/ControlFlowAnalysis.pdf)