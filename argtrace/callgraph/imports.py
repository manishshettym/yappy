import os
import ast
import inspect
import shutil
import importlib.util


def get_all_module_members(module_path):
    with open(module_path, "r") as file:
        tree = ast.parse(file.read())
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    ]


def replace_imports(file_path):
    with open(file_path, "r") as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            raise SyntaxError("Syntax error in file: {}".format(file_path))

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names[0].name == "*":
            module_parts = (node.module or "").split(".")

            # @manish: this is slightly hacky but tested,
            # @manish: preferably use for static analysis only
            module_path = (
                os.path.join(
                    os.path.dirname(file_path),
                    *[".."] * (node.level - 1),
                    *module_parts
                )
                + ".py"
            )

            if os.path.exists(module_path):
                all_members = get_all_module_members(module_path)
                node.names = [
                    ast.alias(name=member, asname=None) for member in all_members
                ]
    with open(file_path, "w") as file:
        file.write(ast.unparse(tree))


def process_directory(dir_path):
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                replace_imports(os.path.join(root, file))


def fix_imports(repo_path):
    if os.path.exists(repo_path + "_temp"):
        shutil.rmtree(repo_path + "_temp")

    temp_path = shutil.copytree(repo_path, repo_path + "_temp")
    process_directory(temp_path)
    return temp_path
