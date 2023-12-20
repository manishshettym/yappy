"""
Application: Repo Call graph
Description: This script generates a call graph for a python repository.

Yappy Modules used:
1. call graph
"""

import json
import os

from yappy.callgraph.pycg import RepoCallGraph, CalleeType, construct_cg

repo_path = "./yappy/data/dias"
cg, icg, cg_sanity = construct_cg(repo_path)

# abstraction over the call graph for analysis
repo_cg = RepoCallGraph(repo_path=repo_path, pycg_dict=cg)

# e.g., finding the external functions (outside file) used by function

for func, uses in repo_cg:
    if func.name == "rewrite_enclosed_sub":
        print("Function: ", func.name)
        print("Module Path:", func.module.file_path)

        for use in uses:
            if use.type == CalleeType.EXTERNAL:
                print("Call: ", use.name, " @ ", use.module.file_path)
