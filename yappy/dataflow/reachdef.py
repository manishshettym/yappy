import gast as ast

from python_graphs import instruction as instruction_module

from yappy.dataflow.base import Analysis

READ = instruction_module.READ
WRITE = instruction_module.WRITE


class ReachingDefinitionAnalysis(Analysis):
    """Computes for each variable its reaching definitions."""

    def __init__(self):
        super(ReachingDefinitionAnalysis, self).__init__(
            label="reaching_def", forward=True
        )

    def aggregate_previous_after_values(self, previous_after_values):
        result = set()
        for previous_after_value in previous_after_values:
            result |= previous_after_value
        return frozenset(result)

    def compute_after_value(self, node, before_value):
        result = set(before_value)
        for access in node.instruction.accesses:
            if isinstance(access, ast.Name):
                parent = access.ctx
                if isinstance(parent, ast.Store):
                    kind = WRITE
                else:
                    kind = READ
                name = access.id
            else:
                kind, name_node, _ = access
                name = name_node.id if isinstance(name_node, ast.Name) else name_node

            if kind == WRITE:
                # Remove all other definitions of the same variable
                result = {defn for defn in result if defn[0] != name}
                # Add the new definition
                result.add((name, node))
        return frozenset(result)  # Convert the result back to a FrozenSet
