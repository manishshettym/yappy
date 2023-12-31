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
