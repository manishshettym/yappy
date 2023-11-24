import os
import ast
import inspect
import shutil
import importlib.util
from typing import List


def get_all_module_members(module_path: str) -> List[str]:
    """Get all members of a module.

    Args:
        module_path (str): path to the module

    Returns:
        List[str]: list of all members of the module
    """
    with open(module_path, "r") as file:
        tree = ast.parse(file.read())
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    ]


def get_package_name(file_path: str) -> str:
    """Get the name of the package the file belongs to.

    Args:
        file_path (str): path to the file

    Returns:
        str: name of the package
    """
    parts = []
    current_dir = os.path.dirname(file_path)
    while os.path.exists(os.path.join(current_dir, "__init__.py")):
        parts.append(os.path.basename(current_dir))
        current_dir = os.path.dirname(current_dir)
    return ".".join(reversed(parts))


def fix_file_imports(file_path: str) -> None:
    """Fix imports in a file.

    Args:
        file_path (str): path to the file

    Raises:
        SyntaxError: if the file has syntax errors
    """
    with open(file_path, "r") as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            raise SyntaxError("Syntax error in file: {}".format(file_path))

    for node in ast.walk(tree):
        # check if it is an importFrom node
        if isinstance(node, ast.ImportFrom):
            module_parts = (node.module or "").split(".")

            # reconstruct the path to the imported module
            module_path = os.path.join(
                os.path.dirname(file_path), *[".."] * (node.level - 1), *module_parts
            )
            module_file = module_path + ".py"

            # convert any relative imports to absolute imports
            if node.level > 0:
                package_name = get_package_name(file_path)
                abs_parts = package_name.split(".") + module_parts[node.level - 1 :]
                node.module = ".".join(abs_parts).rstrip(".")
                node.level = 0

            # convert any wildcard imports to explicit imports
            if node.names[0].name == "*":
                if os.path.exists(module_file):
                    all_members = get_all_module_members(module_file)
                    node.names = [
                        ast.alias(name=member, asname=None) for member in all_members
                    ]

    with open(file_path, "w") as file:
        file.write(ast.unparse(tree))


def fix_repo_imports(repo_path: str) -> str:
    """Fix imports in a repository.
    Fixes:
        1. relative imports -> absolute imports
        2. wildcard imports -> explicit imports

    Args:
        repo_path (str): path to the repository

    Returns:
        str: path to temp copy of the fixed repository
    """
    if os.path.exists(repo_path + "_temp"):
        shutil.rmtree(repo_path + "_temp")

    temp_path = shutil.copytree(repo_path, repo_path + "_temp")

    for root, _, files in os.walk(temp_path):
        for file in files:
            if file.endswith(".py"):
                fix_file_imports(os.path.join(root, file))

    return temp_path
