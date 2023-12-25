""" Utility functions for AST manipulation. """
import ast
import gast
from typing import List, Optional


def build_ast(code: str) -> ast.AST:
    """Build an AST from a code snippet.

    Args:
        code (str): the code snippet

    Returns:
        ast.AST: the AST
    """
    astree = gast.parse(code)
    astree = add_parent_info(astree)
    return astree


def build_ast_file(file_path: str) -> ast.AST:
    """Build an AST from a file.

    Args:
        file_path (str): the file path

    Returns:
        ast.AST: the AST
    """
    with open(file_path, "r") as f:
        code = f.read()
    return build_ast(code)


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


def extract_return_annotation(node: ast.FunctionDef) -> str:
    """Extract the return annotation of a function.

    Args:
        node (ast.FunctionDef): the function

    Returns:
        str: the return annotation
    """
    if isinstance(node.returns, ast.Name):
        function_return = node.returns.id
    elif isinstance(node.returns, ast.Constant) and node.returns.value is None:
        function_return = "None"
    else:
        function_return = None

    return function_return


def extract_arg_annotation(arg: ast.arg) -> str:
    """Extract the type annotation of an argument.

    Args:
        arg (ast.arg): the argument node

    Returns:
        str: the type annotation
    """
    if isinstance(arg.annotation, ast.Name):
        return arg.annotation.id
    elif isinstance(arg.annotation, ast.Attribute):
        return arg.annotation.value.id + "." + arg.annotation.attr
    else:
        return None


def extract_arguments(function_node: ast.FunctionDef) -> List[str]:
    """Extract the arguments of a function.

    Args:
        function_node (ast.FunctionDef): the function node

    Returns:
        List[str]: list of argument names and their type annotations (if any)
    """
    arguments = []
    for arg in function_node.args.args:
        arg_name = arg.arg

        try:
            arg_type = extract_arg_annotation(arg)
        except:
            arg_type = None

        if arg_type is None:
            arguments.append(arg_name)
        else:
            arguments.append(f"{arg_name}: {arg_type}")

    for i, arg in enumerate(function_node.args.kwonlyargs):
        arg_name = arg.arg

        # type annotations
        try:
            arg_type = extract_arg_annotation(arg)
        except:
            arg_type = None

        # default values
        default = function_node.args.kw_defaults[i]

        if isinstance(default, ast.Name):
            arg_default = default.id
        elif isinstance(default, ast.Constant):
            arg_default = default.value
        else:
            arg_default = None

        if arg_default is None and arg_type is None:
            arguments.append(arg_name)
        elif arg_default is None:
            arguments.append(f"{arg_name}: {arg_type}")
        elif arg_type is None:
            arguments.append(f"{arg_name}={arg_default}")
        else:
            arguments.append(f"{arg_name}: {arg_type}={arg_default}")

    if function_node.args.kwarg is not None:
        arguments.append(f"**{function_node.args.kwarg.arg}")

    return arguments


def extract_body(function_node: ast.FunctionDef) -> str:
    """Extract the body of a function.

    Args:
        function_node (ast.FunctionDef): the function node

    Returns:
        str: the body of the function
    """
    body = []
    for stmt in function_node.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Str):
            continue
        body.append(stmt)

    return ast.unparse(body)


def find_def_node(
    astree: ast.AST, def_name: str, def_type: Optional[ast.AST] = None
) -> ast.AST:
    """Find the first definition of a function/class in an AST.

    Args:
        astree (ast.AST): the AST to search
        def_name (str): the name of the definition

    Returns:
        ast.AST: the function definition node
    """

    definition_types = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    if def_type is not None:
        definition_types = (def_type,)

    for node in ast.walk(astree):
        if (
            isinstance(
                node,
                definition_types,
            )
            and node.name == def_name
        ):
            return node

    return None


def find_all_def_nodes(
    astree: ast.AST, def_name: str, def_type: Optional[ast.AST] = None
) -> List[ast.AST]:
    """Find all matching definitions of a functions/classes in an AST.

    Args:
        astree (ast.AST): the AST to search
        def_name (str): the name of the definition

    Returns:
        List[ast.AST]: list of function definition nodes
    """

    definition_types = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    if def_type is not None:
        definition_types = (def_type,)

    def_nodes = []
    for node in ast.walk(astree):
        if (
            isinstance(
                node,
                definition_types,
            )
            and node.name == def_name
        ):
            def_nodes.append(node)

    return def_nodes
