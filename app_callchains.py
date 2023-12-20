"""
Application: Call Chains
Description: This script finds the call chains of a function by traversing the static
inverse call graph in a depth-first manner.

Yappy Modules used:
1. call graph
"""

import json
import os

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


repo_path = "./yappy/data/yt-fts"
cg, _, _ = construct_cg(repo_path)
repo_cg = RepoCallGraph(repo_path=repo_path, pycg_dict=cg)


target_func = RepoEntity(id="yt_fts.download.vtt_to_db", repo_path=repo_path)
call_chains = get_call_chains(target_func, repo_cg)

print(f"Call chains for {target_func.id}:")
for call_chain in call_chains:
    for i, func in enumerate(call_chain):
        print(f"[{func}]", end=" -> " if i != len(call_chain) - 1 else "")
    print()
