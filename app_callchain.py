"""
Application: Call chain analysis
Description: This script finds all the call chains that lead to a function under test.

Yappy Modules used:
1. call graph

TODO: update this to directly use the callgraph module
"""

import json
from rich.console import Console


def load_call_graph(file_path):
    with open(file_path, "r") as f:
        call_graph = json.load(f)

    return call_graph


def load_inverse_call_graph(file_path):
    with open(file_path, "r") as f:
        inverse_call_graph = json.load(f)

    return inverse_call_graph


function_under_test = "yt_fts.download.vtt_to_db"

cg = load_call_graph("./results/cg.json")
icg = load_inverse_call_graph("./results/icg.json")


# find chains of calls that lead to the function under test
# by traversing the inverse call graph backwards
def find_call_chains(target_func):
    chains = []
    stack = [(target_func, [])]

    while stack:
        func, chain = stack.pop()
        if func not in chain:
            chain = chain + [func]
            if func in icg:
                for caller in icg[func]:
                    stack.append((caller, chain))
            else:
                chains.append(chain)

    return chains


# pretty print the call chains
def print_call_chains(chains):
    for chain in chains:
        pretty_chain = " \u2192 ".join(chain)
        print(pretty_chain)


chains = find_call_chains(function_under_test)
print_call_chains(chains)
