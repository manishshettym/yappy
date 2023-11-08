import ast


def add_parent_info(tree: ast.AST) -> ast.AST:
    """Add parent information to each node in the AST.

    Args:
        tree (ast.AST): the AST

    Returns:
        ast.AST: the AST with parent information
    """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree
