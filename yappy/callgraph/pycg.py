"""
This file is a wrapper of the pycg, a practical python call graph generator. Please refer to:
1. https://github.com/vitsalis/PyCG
2. https://pypi.org/project/pycg/

Vitalis Salis, Thodoris Sotiropoulos, Panos Louridas, Diomidis Spinellis and Dimitris Mitropoulos. PyCG: Practical
Call Graph Generation in Python. In 43rd International Conference on Software Engineering, ICSE '21, 25–28 May 2021.
"""

import packaging
import pkg_resources
import pycg
from packaging import version
from pycg import formats
from pycg.pycg import CallGraphGenerator as CallGraphGeneratorPyCG

pycg_version = pkg_resources.get_distribution("pycg").version
if packaging.version.Version(pycg_version) > packaging.version.Version("0.0.3"):

    class CallGraphGenerator(CallGraphGeneratorPyCG):
        def __init__(self, entry_points, package, max_iter=-1, operation="call-graph"):
            super().__init__(entry_points, package, max_iter, operation)

    pycg.pycg.CallGraphGeneratorPyCG = CallGraphGenerator


def inverse_cg(cg: dict):
    """Given a call graph, return its inverse.
    the inverse call graph is a mapping from functions to their
    references (call sites).

    Args:
        cg (dict): call graph

    Returns:
        dict: inverse call graph
    """
    inverse_cg = {}
    for caller, callees in cg.items():
        for callee in callees:
            if callee not in inverse_cg:
                inverse_cg[callee] = []
            inverse_cg[callee].append(caller)
    return inverse_cg
