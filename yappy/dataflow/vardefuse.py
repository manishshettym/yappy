import collections
import gast as ast

from python_graphs import instruction as instruction_module

from yappy.dataflow.base import Analysis

READ = instruction_module.READ
WRITE = instruction_module.WRITE


class FrozenDict(dict):
    def __hash__(self):
        return hash(frozenset((key, frozenset(value)) for key, value in self.items()))


class VariableDefUseAnalysis(Analysis):
    def __init__(self):
        super(VariableDefUseAnalysis, self).__init__(label="var_def_use", forward=True)

    def aggregate_previous_after_values(self, previous_after_values):
        result = {"defs": frozenset(), "uses": frozenset()}
        for previous_after_value in previous_after_values:
            result["defs"] |= previous_after_value["defs"]
            result["uses"] |= previous_after_value["uses"]
        return FrozenDict(result)

    def compute_after_value(self, node, before_value):
        # note before_value is ignored, because we only care about
        # the defs and uses of the current node
        result = {"defs": frozenset(), "uses": frozenset()}
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
                result["defs"] |= frozenset([name])
            elif kind == READ:
                result["uses"] |= frozenset([name])
        return FrozenDict(result)
