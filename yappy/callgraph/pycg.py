"""
This contains a wrapper, extensions, and abstractions for pycg, a practical python call graph generator. Please refer to:
1. https://github.com/vitsalis/PyCG
2. https://pypi.org/project/pycg/

Vitalis Salis, Thodoris Sotiropoulos, Panos Louridas, Diomidis Spinellis and Dimitris Mitropoulos. PyCG: Practical
Call Graph Generation in Python. In 43rd International Conference on Software Engineering, ICSE '21, 25–28 May 2021.
"""

import os
import packaging
import pkg_resources
from packaging import version
from enum import Enum, auto
from typing import List, Dict, Set, Tuple, Optional


import pycg
from pycg import formats
from pycg.pycg import CallGraphGenerator as CallGraphGeneratorPyCG

from yappy.callgraph.imports import fix_repo_imports
from yappy.ast.astutils import build_ast, find_all_def_nodes, extract_body


############ PyCG Wrapper ############

pycg_version = pkg_resources.get_distribution("pycg").version
if packaging.version.Version(pycg_version) > packaging.version.Version("0.0.3"):

    class CallGraphGenerator(CallGraphGeneratorPyCG):
        def __init__(self, entry_points, package, max_iter=-1, operation="call-graph"):
            super().__init__(entry_points, package, max_iter, operation)

    pycg.pycg.CallGraphGeneratorPyCG = CallGraphGenerator


############ RepoCallGraph Abstractions ############


class CalleeType(Enum):
    """Enum for callee types."""

    BUILTIN = auto()
    API = auto()
    LOCAL = auto()
    EXTERNAL = auto()


class CallerType(Enum):
    """Enum for caller types."""

    FUNCTION = auto()
    METHOD = auto()
    CLASS = auto()
    DEFAULT = auto()


class RepoModule:
    def __init__(self, name: str, repo_path: str):
        self.name = name
        self.repo_path = repo_path

    @property
    def file_path(self) -> str:
        return os.path.join(self.repo_path, *self.name.split(".")) + ".py"

    def exists(self) -> bool:
        return os.path.exists(self.file_path)


class RepoEntity:
    def __init__(self, id: str, repo_path: str):
        self.id = id  # abc.xyz.[...].entity
        self.repo_path = repo_path
        self._module = None  # internal module object
        self.module = self.id  # triggers property setter
        self.type = None

    @property
    def name(self) -> str:
        name = self.id.split(".")[-1]
        if name == "__init__":
            return self.id.split(".")[-2]
        if "lambda" in name:
            return self.id.split(".")[-2]
        return name

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, id: str):
        module_from_function = lambda function: ".".join(function.split(".")[:-1])
        module_from_method = lambda method: ".".join(method.split(".")[:-2])

        func_module = RepoModule(module_from_function(id), self.repo_path)
        meth_module = RepoModule(module_from_method(id), self.repo_path)

        if not func_module.exists():
            if not meth_module.exists():
                # FIXME: defaults to func_module; could be None?
                self._module = func_module
            else:
                self._module = meth_module
        else:
            self._module = func_module

    def exists(self) -> bool:
        if self._module:
            return self._module.exists()
        else:
            return False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.id


class Caller(RepoEntity):
    def __init__(self, id: str, repo_path: str):
        super().__init__(id, repo_path)
        # TODO: more granular types; currently not being used anywhere
        self.type = CallerType.DEFAULT


class Callee(RepoEntity):
    def __init__(self, id: str, repo_path: str):
        super().__init__(id, repo_path)
        self.type = None


class RepoCallGraph:
    def __init__(
        self, repo_path: str, pycg_dict: Optional[Dict[str, List[str]]] = None
    ):
        self.repo_path = repo_path
        self.call_graph: Dict[RepoEntity, List[RepoEntity]] = {}
        self.inv_call_graph: Dict[RepoEntity, List[RepoEntity]] = {}

        if pycg_dict:
            self.load_pycg(pycg_dict)

        if self.call_graph:
            self.build_inverse_call_graph()

    def add_call(self, caller: RepoEntity, callee: RepoEntity):
        if callee.type is None:
            if not callee.exists() and "<builtin>" in callee.id:
                callee.type = CalleeType.BUILTIN

            # NOTE(@manishs): this assumes that if not a builtin,
            # and can't be found in the repo, it's an API.abs
            # this may propagate some (seems rare) FPs in
            # cgraph path analysis; e.g., calls to nested functions.
            elif not callee.exists():
                callee.type = CalleeType.API

            elif caller.module.file_path == callee.module.file_path:
                callee.type = CalleeType.LOCAL

            else:
                callee.type = CalleeType.EXTERNAL

        if caller not in self.call_graph:
            self.call_graph[caller] = []

        self.call_graph[caller].append(callee)

    def load_pycg(self, pycg_dict: Dict[str, List[str]]):
        for caller_id, callee_ids in pycg_dict.items():
            caller = RepoEntity(caller_id, self.repo_path)

            for callee_id in callee_ids:
                callee = RepoEntity(callee_id, self.repo_path)
                self.add_call(caller, callee)

    def load_from_json(self, file_path: str):
        with open(file_path, "r") as file:
            json_dict = json.load(file)
            self.load_pycg(json_dict)

    def write_to_json(self, file_path: str):
        with open(file_path, "w") as file:
            json.dump(self.as_dict(), file, indent=4)

    def as_dict(self):
        return {
            caller.id: [callee.id for callee in callees]
            for caller, callees in self.call_graph.items()
        }

    def build_inverse_call_graph(self):
        for caller, callees in self.call_graph.items():
            for callee in callees:
                if callee not in self.inv_call_graph:
                    self.inv_call_graph[callee] = []
                self.inv_call_graph[callee].append(caller)

    # iterator for self.call_graph
    def __iter__(self):
        return iter(self.call_graph.items())


############ CG constructors and PyCG Extensions ############


def construct_cg(repo_path: str, max_iter: int = -1) -> Tuple[dict, dict, dict]:
    """Generate call graph for a repository.

    Args:
        repo_path (str): path to the repository
        max_iter (int, optional): maximum number of PyCG iterations. Defaults to 1.

    Returns:
        Tuple[dict, dict]: call graph and its inverse
    """
    repo_path = fix_repo_imports(repo_path)

    python_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.abspath(os.path.join(root, file)))

    cg_generator = CallGraphGenerator(python_files, repo_path, max_iter=max_iter)
    cg_generator.analyze()

    formatter = formats.Simple(cg_generator)
    cgraph = formatter.generate()
    inverse_cgraph = inverse_cg(cgraph)
    sanity_checks = sanity_cg(repo_path, cgraph)
    return cgraph, inverse_cgraph, sanity_checks


def inverse_cg(pycg_cgraph: dict) -> dict:
    """Given a call graph, return its inverse.
    the inverse call graph is a mapping from functions to their
    references (call sites).

    Args:
        pycg_cgraph (dict): call graph

    Returns:
        dict: inverse call graph
    """
    inverse_cg = {}
    for caller, callees in pycg_cgraph.items():
        for callee in callees:
            if callee not in inverse_cg:
                inverse_cg[callee] = []
            inverse_cg[callee].append(caller)
    return inverse_cg


def sanity_cg(repo_path: str, pycg_cgraph: dict) -> dict:
    """Return sanity checks and metadata for the callgraph of a repo.

    Args:
        repo_path (str): path to the repo
        pycg_cgraph (dict): callgraph of the repo
    """

    sanity_checks = {}
    cgraph = RepoCallGraph(repo_path, pycg_cgraph)

    for caller, callees in cgraph:
        if callees == []:
            continue

        if caller not in sanity_checks:
            sanity_checks[caller.id] = {
                "file": caller.module.file_path,
                "callcount": 0,
                "uninvokedcalls": 0,
                "unknowncalls": 0,
                "warnings": [],
            }

        # Check 1: if the function file exists
        if not caller.exists():
            sanity_checks[caller.id]["warnings"].append("Caller file does not exist.")
            continue

        with open(caller.module.file_path) as f:
            astree = build_ast(f.read())

        # Check 2: if the caller is defined in the file
        function_defs = find_all_def_nodes(astree, caller.name)
        if len(function_defs) == 0:
            sanity_checks[caller.id]["warnings"].append("Caller not defined in file.")
            continue

        function_bodies = [extract_body(function_def) for function_def in function_defs]

        # Check 3: if the caller call counts are reasonable
        sanity_checks[caller.id]["callcount"] = len(callees)
        if len(callees) > 40:
            sanity_checks[caller.id]["warnings"].append("Caller has > 40 calls.")

        for callee in callees:
            # Check 4: if callee is in the caller's body
            if not any([callee.name in fb for fb in function_bodies]):
                sanity_checks[caller.id]["uninvokedcalls"] += 1
                sanity_checks[caller.id]["warnings"].append(
                    f"Callee {callee.id} not in caller's body."
                )

            # Check 5: if callee file exists
            if not callee.exists():
                sanity_checks[caller.id]["unknowncalls"] += 1
                sanity_checks[caller.id]["warnings"].append(
                    f"Callee {callee.id} file does not exist."
                )

    return sanity_checks
