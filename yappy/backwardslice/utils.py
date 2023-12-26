import astunparse
import gast as ast
from termcolor import colored

from yappy.callgraph.pycg import RepoEntity, RepoCallGraph


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
            print(colored(line, "green", attrs=["bold"]))
        else:
            print(colored(line, "grey"))


def get_func_code(func: RepoEntity) -> str:
    """Given a function, return its source code.

    Args:
        func (RepoEntity): The function.

    Raises:
        ValueError: If the function is not found in the module.

    Returns:
        str: The source code of the function.
    """
    func_module = func.module.file_path
    func_name = func.name

    with open(func_module, "r") as file:
        module_code = file.read()

    module_ast = ast.parse(module_code)

    class FunctionDefVisitor(ast.NodeVisitor):
        def __init__(self, func_name):
            self.func_name = func_name
            self.func_code = None

        def visit_FunctionDef(self, node):
            if node.name == self.func_name:
                self.func_code = astunparse.unparse(node)
                return

    visitor = FunctionDefVisitor(func_name)
    visitor.visit(module_ast)

    if visitor.func_code is not None:
        return visitor.func_code

    raise ValueError(f"Function '{func_name}' not found in module '{func_module}'.")


def find_callsite(caller_ast, callee_name):
    """
    Find the callsite of a function in another function's AST, including cases where
    the function might be called through a variable or a more complex expression.

    Args:
        caller_ast (ast.AST): The AST of the caller function.
        callee_name (str): The name of the called function.

    Returns:
        ast.Call: The AST node representing the callsite, or None if not found.
    """

    class CallSiteVisitor(ast.NodeVisitor):
        def __init__(self):
            self.callsite = None

        def visit_Call(self, node):
            if self.is_matching_call(node):
                self.callsite = node
                return
            self.generic_visit(node)

        def is_matching_call(self, call_node):
            if (
                isinstance(call_node.func, ast.Name)
                and call_node.func.id == callee_name
            ):
                return True
            elif (
                isinstance(call_node.func, ast.Attribute)
                and call_node.func.attr == callee_name
            ):
                return True
            elif isinstance(call_node.func, ast.Call):
                return self.is_matching_call(call_node.func)

            return False

    visitor = CallSiteVisitor()
    visitor.visit(caller_ast)
    return visitor.callsite


def get_call_chains_helper(
    func_name: str,
    repo_cg: RepoCallGraph,
    call_chain: list,
    call_chains: list,
    visited: set,
):
    """Helper function for get_call_chains.
    Args:
        func_name (str): name of the function
        repo_cg (RepoCallGraph): call graph of the repository
        call_chain (list): call chain of the function
        call_chains (list): call chains of the function
        visited (set): visited functions
    """
    if func_name in visited:
        return

    visited.add(func_name)
    call_chain.append(func_name)

    if func_name not in repo_cg.inv_call_graph:
        call_chains.append(call_chain.copy())
        call_chain.pop()
        return

    for caller in repo_cg.inv_call_graph[func_name]:
        get_call_chains_helper(caller, repo_cg, call_chain, call_chains, visited)

    call_chain.pop()


def get_call_chains(func_name: str, repo_cg: RepoCallGraph):
    """Given a function name, return its call chains.
    Args:
        func_name (str): name of the function
        repo_cg (RepoCallGraph): call graph of the repository
    Returns:
        list: call chains of the function
    """
    call_chains, call_chain = [], []
    visited = set()
    get_call_chains_helper(func_name, repo_cg, call_chain, call_chains, visited)
    return call_chains
