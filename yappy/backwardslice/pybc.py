import gast as ast
import pygraphviz

from yappy.ast.astutils import build_ast
from yappy.pdg.pypdg import construct_pdg
from yappy.backwardslice.utils import print_code_with_highlights


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


############ Test ############

if __name__ == "__main__":
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

    program_node = build_ast(code, use_gast=True)
    pdg = construct_pdg(program_node)

    # Get the target node
    target_ast_node = program_node.body[0].body[-1]
    target_node = pdg.get_node_by_ast_node(target_ast_node)
    print("Target:", ast.unparse(target_node.ast_node))

    # Compute the backward slice
    backward_slice = compute_backward_slice(pdg, target_node)
    backward_slice = {node.ast_node for node in backward_slice}
    print_code_with_highlights(code, backward_slice)
