"""perform interprocedural backwards slicing using pybc"""

import gast as ast
from yappy.ast.astutils import build_ast, find_all_def_nodes
from yappy.pdg.pypdg import construct_pdg, ProgramDependenceGraph
from yappy.backwardslice.pybc import compute_backward_slice
from yappy.backwardslice.utils import print_code_with_highlights
from yappy.callgraph.pycg import RepoEntity, RepoCallGraph, CalleeType, construct_cg


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


def get_func_code(func: RepoEntity) -> str:
    raise NotImplementedError


def get_backward_slice_of_callsite(caller_func: RepoEntity, called_func: RepoEntity):
    """Given a caller function and a called function, return the backward slice of the callsite.
    Args:
        caller_func (RepoEntity): the caller function
        called_func (RepoEntity): the called function
    Returns:
        set: the set of pdg nodes in the backward slice of the callsite
    """
    raise NotImplementedError

    # caller_ast = None  # TODO: get the caller's AST

    # # TODO: can we pass AST or does it need to be gast
    # caller_pdg = construct_pdg(caller_ast)

    # callsite_ast_node = None  # TODO: get the callsite AST node
    # callsite_node = caller_pdg.get_node_by_ast_node(callsite_ast_node)

    # backward_slice = compute_backward_slice(caller_pdg, callsite_node)
    # backward_slice = {node.ast_node for node in backward_slice}

    # return backward_slice


def get_interproc_slice(
    repo_cg: RepoCallGraph, target_func: RepoEntity, target_ast_node: ast.stmt
):
    """Given a target function and line number, return the interprocedural slice.

    Args:
        repo_cg (RepoCallGraph): call graph of the repository
        target_func (RepoEntity): the target function
        target_node (ast.stmt): the target statement in the target function

    Returns:
        set: the set of pdg nodes in the interprocedural slice of the target node
    """
    call_chains = get_call_chains(target_func, repo_cg)
    interprocedural_slice = set()

    for call_chain in call_chains:
        caller, callee = None, None

        for func in call_chain:
            caller = func

            if func == target_func:
                callee = target_func
            else:
                bc = get_backward_slice_of_callsite(caller, callee)
                caller = callee
                interprocedural_slice.update(bc)
                print(bc)

    return interprocedural_slice


if __name__ == "__main__":
    repo_path = "../data/yt-fts"
    cg, _, _ = construct_cg(repo_path)
    repo_cg = RepoCallGraph(repo_path=repo_path, pycg_dict=cg)

    target_func = RepoEntity(id="yt_fts.download.vtt_to_db", repo_path=repo_path)
    target_ast_node = None
    interprocedural_slice = get_interproc_slice(repo_cg, target_func, target_ast_node)
