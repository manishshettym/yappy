import collections
import gast as ast
import textwrap

from python_graphs import instruction as instruction_module
from python_graphs.program_utils import program_to_ast
from python_graphs.program_graph import (
    ProgramGraph,
    make_node_from_ast_node,
)

from python_graphs.control_flow_graphviz import render as render_cfg
from python_graphs.program_graph_graphviz import render as render_pg
import python_graphs.program_graph_dataclasses as pb

from yappy.pdg.utils import (
    PDGEdgeType,
    post_dominators,
    immediate_post_dominator,
    cfgnode2code,
)

import yappy.pdg.cfg as control_flow
from yappy.dataflow.reachdef import ReachingDefinitionAnalysis
from yappy.dataflow.vardefuse import VariableDefUseAnalysis

READ = instruction_module.READ
WRITE = instruction_module.WRITE


############ Utils ############


def print_var_def_use_of_cfg_node(cfg_node):
    var_def_use = cfg_node.get_label("var_def_use_out")
    print(f"defs: {var_def_use['defs']}", f"uses: {var_def_use['uses']}")


def print_def_use_of_cfg_node(cfg_node):
    def_use = cfg_node.get_label("def_use_out")
    for var, info in def_use.items():
        defs = [cgfnode2code(defn) for defn in info["defs"]]
        uses = [cgfnode2code(use) for use in info["uses"]]
        print(f"var={var} has defs: {defs}", f"and uses: {uses}")


def print_reaching_def_of_cfg_node(cfg_node):
    reaching_defs = cfg_node.get_label("reaching_def_in")
    for rd in reaching_defs:
        print(f"var={rd[0]} has reaching definition: {cgfnode2code(rd[1])}")


############ Program Dependence Graph ############


class ProgramDependenceGraph(ProgramGraph):
    def __init__(self, cfg, var_def_use_analysis, reaching_def_analysis):
        super(ProgramDependenceGraph, self).__init__()
        self.cfg = cfg
        self.pdom = post_dominators(cfg)
        self.ipdom = immediate_post_dominator(self.pdom)

        self.var_def_use_analysis = var_def_use_analysis
        self.reaching_def_analysis = reaching_def_analysis

        for control_flow_node in cfg.get_control_flow_nodes():
            self.add_node_from_instruction(control_flow_node.instruction)

        for node in self.nodes.values():
            self.add_data_dependence_edges(node)
            self.add_control_dependence_edges(node)

    def add_data_dependence_edges(self, nodeB):
        """Add data dependence edges for a node B.

        node B is data dependent on another node A
        if there is a variable v in Def(A) and Use(B) such that
        A is a reaching definition of v at B."""

        cfg_nodeB = self.cfg.get_control_flow_node_by_ast_node(nodeB.ast_node)
        var_def_useB = cfg_nodeB.get_label(self.var_def_use_analysis.label + "_out")
        reaching_defB = cfg_nodeB.get_label(self.reaching_def_analysis.label + "_in")

        for var in var_def_useB["uses"]:
            for defn in reaching_defB:
                if defn[0] == var:
                    nodeA = self.get_node_by_ast_node(defn[1].instruction.node)
                    # print(f"DD: {cfgnode2code(defn[1])} --> {cfgnode2code(cfg_nodeB)}")
                    self.add_new_edge(nodeB.id, nodeA.id, edge_type=PDGEdgeType.DD)

    def add_control_dependence_edges(self, nodeA):
        """Add control dependence edges from nodes to node A.

        node C is control dependent on node A
        if there is a path from A to C in the CFG such that
        it does not contain the immediate post-dominator of A.
        """

        cfg_nodeA = self.cfg.get_control_flow_node_by_ast_node(nodeA.ast_node)

        # for every B that A has an edge to
        for cfg_nodeB in cfg_nodeA.next:
            # s.t. node A is not post dominated by node B
            if cfg_nodeB in self.pdom[cfg_nodeA]:
                continue

            # @manish: a node could have no post dominators
            # e.g., ... if <c>: return ...
            # in this case, we skip the node
            if cfg_nodeA not in self.ipdom:
                continue

            # move up from B in the post-dominator tree until A's ipdom

            ipdom_nodeA = self.ipdom[cfg_nodeA]
            current = cfg_nodeB

            while current != ipdom_nodeA:
                # every node on this path is control dependent on A
                nodeC = self.get_node_by_ast_node(current.instruction.node)

                # add the control dependence edge if not to itself
                if nodeC.id != nodeA.id:
                    # print(f"CD: {cfgnode2code(cfg_nodeA)} --> {cfgnode2code(current)}")
                    self.add_new_edge(nodeC.id, nodeA.id, edge_type=PDGEdgeType.CD)

                # move up the post-dominator tree
                current = self.ipdom[current]


def construct_pdg(code, program_node):
    """Construct the Program Dependence Graph from an AST."""

    # Construct the control flow graph
    cfg = control_flow.get_control_flow_graph(program_node)
    try:
        render_cfg(cfg, path="cfg.png")
    except:
        pass

    # Perform the analyses
    def_use_analysis = VariableDefUseAnalysis()  # NOTE: Works perfectly!
    reaching_def_analysis = ReachingDefinitionAnalysis()  # NOTE: Works perfectly!

    for block in cfg.get_enter_control_flow_nodes():
        def_use_analysis.visit(block)

    for block in cfg.get_enter_control_flow_nodes():
        reaching_def_analysis.visit(block)

    # Construct the data dependence graph
    pdg = ProgramDependenceGraph(cfg, def_use_analysis, reaching_def_analysis)
    try:
        render_pg(pdg, path="pdg.png")
    except:
        pass

    return pdg


############ Test ############

if __name__ == "__main__":
    code = """def foo(x, y, z):
        x = x + 1
        y = y + 2
        a = 0
        for i in range(y):
            if i % 2 == 0:
                z = x + 2
            else:
                z = x + 3
            a = y + 1
        k = bar(z)
        return a
    """

    program_node = program_to_ast(code)
    pdg = construct_pdg(code, program_node)
