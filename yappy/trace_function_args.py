import argparse
import ast
import os


def parse_python_file(file_path):
    with open(file_path, "r") as f:
        source = f.read()
    return ast.parse(source)


def build_call_graph(ast_node, file_path):
    call_graph = {}
    for node in ast.walk(ast_node):
        if isinstance(node, ast.FunctionDef):
            call_graph[node.name] = []
            for child_node in ast.walk(node):
                if isinstance(child_node, ast.Call):
                    if isinstance(child_node.func, ast.Name):
                        call_graph[node.name].append(
                            (
                                child_node.func.id,
                                file_path,
                                child_node.lineno,
                                child_node.col_offset,
                            )
                        )
                    elif isinstance(child_node.func, ast.Attribute):
                        call_graph[node.name].append(
                            (
                                child_node.func.attr,
                                file_path,
                                child_node.lineno,
                                child_node.col_offset,
                            )
                        )
    return call_graph


def build_inverse_call_graph(call_graph):
    inverse_call_graph = {}
    for key, value in call_graph.items():
        for func in value:
            if func[0] not in inverse_call_graph:
                inverse_call_graph[func[0]] = []
            inverse_call_graph[func[0]].append((key, func[1], func[2], func[3]))
    return inverse_call_graph


def build_data_flow_graph(ast_node, file_path):
    data_flow_graph = {}
    for node in ast.walk(ast_node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    data_flow_graph[target.id] = []
                    for child_node in ast.walk(node.value):
                        # print(child_node)
                        if isinstance(child_node, ast.Name):
                            data_flow_graph[target.id].append(
                                (
                                    child_node.id,
                                    file_path,
                                    child_node.lineno,
                                    child_node.col_offset,
                                )
                            )
    return data_flow_graph


def backward_trace(call_graph, data_flow_graph, target_function, target_args):
    """Traces the data flow of the target function and its arguments backwards"""
    print(f"tracing {target_function} with args {target_args}")

    visited_functions = set()
    visited_variables = set(target_args)
    queue = [(target_function, [arg]) for arg in target_args]
    traces = {arg: [] for arg in target_args}

    while queue:
        function, args = queue.pop(0)
        visited_functions.add(function)

        # update trace for each argument of the target function
        if function == target_function:
            traces[args[0]] = args[1:]

        for arg in args:
            # arg is a variable
            if arg in data_flow_graph:
                for var in data_flow_graph[arg]:
                    # print(f"{arg} <-- {var[0]} ({var[1]}:{var[2]}:{var[3]})")
                    visited_variables.add(var[0])
                    if var[0] not in args:
                        queue.append((function, args + [var[0]]))

            # arg is a callable
            if arg in call_graph:
                for func in call_graph[arg]:
                    # print(f"{arg} <== {func[0]} ({func[1]}:{func[2]}:{func[3]})")
                    if func[0] not in visited_functions:
                        queue.append((func[0], []))

    return traces


def main(repo_path, file_path, function_name):
    call_graph = {}
    data_flow_graph = {}

    function_args = []
    for node in ast.walk(parse_python_file(file_path)):
        if isinstance(node, ast.FunctionDef):
            if node.name == function_name:
                function_args = [arg.arg for arg in node.args.args]
                break

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                ast_node = parse_python_file(file_path)
                call_graph.update(build_call_graph(ast_node, file_path))
                data_flow_graph.update(build_data_flow_graph(ast_node, file_path))

    inverse_call_graph = build_inverse_call_graph(call_graph)

    with open("./results/call_graph.txt", "w") as f:
        for key, value in call_graph.items():
            f.write(f"{key} : {value}\n")

    with open("./results/inverse_call_graph.txt", "w") as f:
        for key, value in inverse_call_graph.items():
            f.write(f"{key} : {value}\n")

    with open("./results/data_flow_graph.txt", "w") as f:
        for key, value in data_flow_graph.items():
            f.write(f"{key} : {value}\n")

    if function_name not in call_graph:
        print(f"Function {function_name} not found in repository.")
        return

    traces = backward_trace(call_graph, data_flow_graph, function_name, function_args)

    for arg, trace in traces.items():
        trace_str = " <-- ".join(trace)
        print(f"{arg} <-- {trace_str}")


if __name__ == "__main__":
    repo_path = "./data/yt-fts"
    file_path = "./data/yt-fts/yt_fts/download.py"

    # function_name = "get_vid_title"
    function_name = "vtt_to_db"

    main(repo_path, file_path, function_name)
