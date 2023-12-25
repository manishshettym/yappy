import ast


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
