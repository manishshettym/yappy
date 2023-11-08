import gast as ast
import pygraphviz

from python_graphs.program_utils import program_to_ast
from yappy.pdg.pypdg import construct_pdg
from yappy.backwardslice.utils import add_parent_info


def compute_backward_slice(pdg, target_node):
    """Compute the backward slice of a target node in a Program Dependence Graph.

    Args:
        pdg (ProgramDependenceGraph): The Program Dependence Graph.
        target_node (Node): The target node.

    Returns:
        set: The set of nodes that are in the backward slice of the target node.
    """
    visited = set()
    stack = [target_node]

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            for neighbor in pdg.outgoing_neighbors(node):
                stack.append(neighbor)

    return visited


def print_code_with_highlights(code, backward_slice):
    """Print the code with highlights for the nodes in the backward slice.

    Args:
        code (str): The code.
        backward_slice (set): a set of ast.Node objects that are in the slice
    """
    lines = code.split("\n")
    for i, line in enumerate(lines):
        node = None
        for b_node in backward_slice:
            if hasattr(b_node, "lineno"):
                if b_node.lineno == i + 1:
                    node = b_node
                    break
            elif hasattr(b_node, "parent") and hasattr(b_node.parent, "lineno"):
                if b_node.parent.lineno == i + 1:
                    node = b_node
                    break
        if node is not None:
            print(f"\033[1;31;92m{line}\033[0m")
        else:
            print(line)


############ Test ############


code = """def foo(x, y, z):
    x = x + 1
    y = y + 2
    a = 0
    for i in range(y):
        if i % 2 == 0:
            z = x + 2
        else:
            z = x + 3
        a = y + 1
    k = bar(z)
    return a
"""

# load the code from test.py
code = open("test.py").read()


program_node = program_to_ast(code)
program_node = add_parent_info(program_node)
pdg = construct_pdg(code, program_node)

# Get the target node
target_node = pdg.get_node_by_ast_node(program_node.body[0].body[-3])
print("Target:", ast.unparse(target_node.ast_node))

# Compute the backward slice
backward_slice = compute_backward_slice(pdg, target_node)
backward_slice = {node.ast_node for node in backward_slice}
print_code_with_highlights(code, backward_slice)
