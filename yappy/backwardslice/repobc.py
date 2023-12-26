"""perform interprocedural backwards slicing using pybc"""

import astunparse
import gast as ast

from python_graphs.program_utils import program_to_ast

from yappy.ast.astutils import add_parent_info
from yappy.pdg.pypdg import construct_pdg, ProgramDependenceGraph
from yappy.callgraph.pycg import RepoEntity, RepoCallGraph, construct_cg
from yappy.backwardslice.pybc import compute_backward_slice
from yappy.backwardslice.utils import (
    print_code_with_highlights,
    get_func_code,
    find_callsite,
    get_call_chains,
)


def get_callsite_bc(caller_func: RepoEntity, called_func: RepoEntity):
    """Given a caller function and a called function, return the backward slice of the callsite.
    Args:
        caller_func (RepoEntity): the caller function
        called_func (RepoEntity): the called function
    Returns:
        set: the set of pdg nodes in the backward slice of the callsite
    """

    caller_code = get_func_code(caller_func)
    caller_ast = add_parent_info(program_to_ast(caller_code))
    caller_pdg = construct_pdg(caller_ast)

    callsite_node = find_callsite(caller_ast, called_func.name)
    if callsite_node is None:
        raise ValueError(f"Func '{called_func}' not called in '{caller_func}'.")

    callsite_node = caller_pdg.get_node_by_source(astunparse.unparse(callsite_node))

    backward_slice = compute_backward_slice(caller_pdg, callsite_node)
    backward_slice = {node.ast_node for node in backward_slice}
    print_code_with_highlights(caller_code, backward_slice)


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

    for idx, call_chain in enumerate(call_chains):
        print(f"=============== Chain {idx} ===============")
        caller, callee = None, None

        for caller in call_chain:
            if caller == target_func:
                print("[In] destination: ", caller)
                print("[Find] target: ", target_ast_node)
            else:
                print("[In] caller: ", caller)
                print("[Find] callee: ", callee)
                bc = get_callsite_bc(caller, callee)
                # interprocedural_slice.update(bc)
                # print(bc)

            callee = caller

        print(f"=============== End of chain ===============\n\n")

    return interprocedural_slice


if __name__ == "__main__":
    repo_path = "../data/yt-fts"
    cg, _, _ = construct_cg(repo_path)
    repo_cg = RepoCallGraph(repo_path=repo_path, pycg_dict=cg)

    target_func = RepoEntity(id="yt_fts.download.get_vid_title", repo_path=repo_path)
    interprocedural_slice = get_interproc_slice(
        repo_cg, target_func, target_ast_node=None
    )
