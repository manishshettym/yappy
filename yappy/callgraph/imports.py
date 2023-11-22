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


def get_package_name(file_path):
    parts = []
    current_dir = os.path.dirname(file_path)
    while os.path.exists(os.path.join(current_dir, "__init__.py")):
        parts.append(os.path.basename(current_dir))
        current_dir = os.path.dirname(current_dir)
    return ".".join(reversed(parts))


def replace_imports(file_path):
    with open(file_path, "r") as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            raise SyntaxError("Syntax error in file: {}".format(file_path))

    for node in ast.walk(tree):
        # check if it is an importFrom node
        if isinstance(node, ast.ImportFrom):
            # find the part of the imported module
            module_parts = (node.module or "").split(".")

            # reconstruct the path to the imported module
            module_path = os.path.join(
                os.path.dirname(file_path), *[".."] * (node.level - 1), *module_parts
            )
            module_file = module_path + ".py"

            # print("Original import:", ast.unparse(node))
            # print("Module parts:", module_parts)
            # print("Module file:", module_file)

            # convert any relative imports to absolute imports
            if node.level > 0:
                # print("== Found relative import ==")
                package_name = get_package_name(file_path)

                if module_parts == [""]:
                    node.module = package_name
                else:
                    abs_parts = package_name.split(".") + module_parts[node.level - 1 :]
                    node.module = ".".join(abs_parts)

                node.level = 0
                # print("Updated relative import:", ast.unparse(node))
                # print("============================")

            # convert any wildcard imports to explicit imports
            if node.names[0].name == "*":
                # print("== Found wildcard import ==")
                if os.path.exists(module_file):
                    all_members = get_all_module_members(module_file)
                    node.names = [
                        ast.alias(name=member, asname=None) for member in all_members
                    ]
                #     print("Updated wildcard import:", ast.unparse(node))
                # print("============================")

            # print("Final import: {}\n".format(ast.unparse(node)))

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
