"""
Application: Backward slicing for function arguments
Description: This script finds the backward slice of a function's arguments by
traversing the inverse call graph and program dependence graph backwards.

Yappy Modules used:
1. call graph
2. program dependence graph
3. backward slicing

TODO: complete this!!
"""

import argparse
import ast
import os
import json
import inspect


def parse_python_file(file_path):
    with open(file_path, "r") as f:
        source = f.read()
    return ast.parse(source)


def load_call_graph(file_path):
    with open(file_path, "r") as f:
        call_graph = json.load(f)

    return call_graph


def load_inverse_call_graph(file_path):
    with open(file_path, "r") as f:
        inverse_call_graph = json.load(f)

    return inverse_call_graph


def find_repo_root(repo_path):
    """Find the root of a python repository given a path to the repository

    Args:
        repo_path (str): Path to the repository

    Returns:
        str: Path to the root of the repository
    """
    # get the absolute path of the repository
    repo_path = os.path.abspath(repo_path)

    # if the path is a file, get the directory containing the file
    if os.path.isfile(repo_path):
        repo_path = os.path.dirname(repo_path)

    # check if the path is a package
    if os.path.isfile(os.path.join(repo_path, "__init__.py")):
        # if it is, get the directory containing the package
        repo_path = os.path.dirname(repo_path)

    # keep going up the directory tree until we find the root
    while True:
        if (
            os.path.isfile(os.path.join(repo_path, "setup.py"))
            or os.path.isfile(os.path.join(repo_path, "pyproject.toml"))
            or os.path.isdir(os.path.join(repo_path, ".git"))
        ):
            return repo_path

        parent_dir = os.path.dirname(repo_path)
        if parent_dir == repo_path:
            # we've reached the root directory
            return repo_path

        repo_path = parent_dir


def func_module_path(repo_path, file_path, function_name):
    """Generate function module path. A function's module path is what we would user to import the function
    at the root of the repository

    Args:
        repo_path (str): Path to the repository
        file_path (str): Path to the file containing the function
        function_name (str): Name of the function

    Returns:
        str: Function module path
    """

    repo_root = find_repo_root(repo_path)
    relative_file_path = os.path.relpath(file_path, repo_root)

    module_name = relative_file_path.replace("/", ".")
    module_name = module_name[:-3]
    complete_function_name = f"{module_name}.{function_name}"

    return complete_function_name


def get_func_args(file_path, function_name):
    """Get the arguments of a function in a python file

    Args:
        file_path (str): path to the python file
        function_name (str): name of the function
    """
    function_args = []
    for node in ast.walk(parse_python_file(file_path)):
        if isinstance(node, ast.FunctionDef):
            if node.name == function_name:
                function_args = [arg.arg for arg in node.args.args]
                break

    return function_args


def main(repo_path, file_path, function_name):
    call_graph = load_call_graph("./results/cg.json")
    inverse_call_graph = load_inverse_call_graph("./results/icg.json")

    function_args = get_func_args(file_path, function_name)
    function_name = func_module_path(repo_path, file_path, function_name)

    if function_name not in call_graph:
        print(f"Function {function_name} not found in repository.")
        return

    data_flow_graphs = {}
    # TODO: Build data flow graph for each function in the call graph

    # TODO: get the interprocedural backward slice of each argument
    traces = backward_trace(call_graph, data_flow_graphs, function_name, function_args)

    for arg, trace in traces.items():
        trace_str = " <-- ".join(trace)
        print(f"{arg} <-- {trace_str}")


if __name__ == "__main__":
    repo_path = "./data/yt-fts"
    file_path = "./data/yt-fts/yt_fts/download.py"

    # function_name = "get_vid_title"
    function_name = "vtt_to_db"

    main(repo_path, file_path, function_name)
