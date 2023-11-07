import collections
import gast as ast

from python_graphs import instruction as instruction_module

from yappy.dataflow.base import Analysis

READ = instruction_module.READ
WRITE = instruction_module.WRITE


class FrozenDict(dict):
    def __hash__(self):
        return hash(
            frozenset((key, frozenset(value.items())) for key, value in self.items())
        )


class DefUseAnalysis(Analysis):
    """Computes for each variable its possible definitions (defs) and all uses."""

    def __init__(self):
        super(DefUseAnalysis, self).__init__(label="def_use", forward=True)

    def aggregate_previous_after_values(self, previous_after_values):
        result = collections.defaultdict(
            lambda: {"defs": frozenset(), "uses": frozenset()}
        )
        for previous_after_value in previous_after_values:
            for key, value in previous_after_value.items():
                result[key]["defs"] |= value["defs"]
                result[key]["uses"] |= value["uses"]
        return FrozenDict(result)

    def compute_after_value(self, node, before_value):
        result = dict(before_value)
        for access in node.instruction.accesses:
            if isinstance(access, ast.Name):
                # If access is a Name object, infer whether it's a read or write
                # based on the context in which the variable is used
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
                result[name] = result.get(
                    name, {"defs": frozenset(), "uses": frozenset()}
                )
                result[name]["defs"] |= frozenset([node])
            elif kind == READ:
                result[name] = result.get(
                    name, {"defs": frozenset(), "uses": frozenset()}
                )
                result[name]["uses"] |= frozenset([node])

        return FrozenDict(result)  # Convert the result back to a FrozenDict
