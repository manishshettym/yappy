import enum
import gast as ast
from python_graphs.program_graph import (
    make_node_for_ast_list,
    make_list_field_name,
    make_node_from_ast_value,
)

from python_graphs import program_graph_dataclasses as pb


def add_ast_edges(program_graph, root):
    for ast_node in ast.walk(root):
        for field_name, value in ast.iter_fields(ast_node):
            if isinstance(value, list):
                pg_node = make_node_for_ast_list()
                program_graph.add_node(pg_node)
                program_graph.add_new_edge(
                    ast_node, pg_node, pb.EdgeType.FIELD, field_name
                )
                for index, item in enumerate(value):
                    list_field_name = make_list_field_name(field_name, index)
                    if isinstance(item, ast.AST):
                        program_graph.add_new_edge(
                            pg_node, item, pb.EdgeType.FIELD, list_field_name
                        )
                    else:
                        item_node = make_node_from_ast_value(item)
                        program_graph.add_node(item_node)
                        program_graph.add_new_edge(
                            pg_node, item_node, pb.EdgeType.FIELD, list_field_name
                        )
            elif isinstance(value, ast.AST):
                program_graph.add_new_edge(
                    ast_node, value, pb.EdgeType.FIELD, field_name
                )
            else:
                pg_node = make_node_from_ast_value(value)
                program_graph.add_node(pg_node)
                program_graph.add_new_edge(
                    ast_node, pg_node, pb.EdgeType.FIELD, field_name
                )

    return program_graph


class PDGEdgeType(enum.Enum):
    CD = 0
    DD = 1


def post_dominator_tree(cfg):
    """Compute the post-dominator tree of a control flow graph.

    A node V is post-dominated by a node U if every path from V to the end of
    the CFG must go through U.

    returns: a dictionary mapping each node to its set of post-dominators.
    """
    nodes = cfg.get_control_flow_nodes()
    exit_nodes = [node for node in nodes if not node.next]

    # Initialization: ∀n ∈ N \ {end}: pdom(n) = N
    pdom = {node: set(nodes) for node in nodes}

    # Initialization: pdom(end) = {end}
    for exit_node in exit_nodes:
        pdom[exit_node] = {exit_node}

    # Iteration: ∀n ∈ N \ {end}: pdom(n) = {n} ∪ (⋂ pdom(s)) ∀s ∈ succ(n)
    while True:
        change = False
        for node in nodes:
            if node in exit_nodes:
                continue
            new_pdom = {node} | set.intersection(*(pdom[succ] for succ in node.next))
            if new_pdom != pdom[node]:
                pdom[node] = new_pdom
                change = True
        if not change:
            break

    # print_pdt(pdom)

    return pdom


def get_pdt_parent(pdt, node):
    """Get the parent of a node in the post-dominator tree.

    parent is one that post dominates the node and is
    dominated by all other post dominators of the node.
    """
    candidates = pdt[node]
    for candidate in candidates:
        if all(candidate not in pdt[other] for other in candidates):
            return candidate
    return None


def print_pdt(pdt):
    print("Post Dominator Tree")
    for node in pdt:
        print(node.instruction.node)
        print("Post Dominators:")
        for post_dominator in pdt[node]:
            print(post_dominator.instruction.node)
        print()
