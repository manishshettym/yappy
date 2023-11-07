import collections


class Analysis(object):
    """Base class for a data flow analysis.

    Attributes:
      label: The name of the analysis.
      forward: (bool) True for forward analyses, False for backward analyses.
      in_label: The name of the analysis, suffixed with _in.
      out_label: The name of the analysis, suffixed with _out.
      before_label: Either the in_label or out_label depending on the direction of
        the analysis. Marks the before_value on a node during an analysis.
      after_label: Either the in_label or out_label depending on the direction of
        the analysis. Marks the after_value on a node during an analysis.
    """

    def __init__(self, label, forward):
        self.label = label
        self.forward = forward

        self.in_label = label + "_in"
        self.out_label = label + "_out"

        self.before_label = self.in_label if forward else self.out_label
        self.after_label = self.out_label if forward else self.in_label

    def aggregate_previous_after_values(self, previous_after_values):
        """Computes the before value for a node from the previous after values.

        This is the 'meet' or 'join' function of the analysis.
        TODO(manishs): Update terminology to match standard textbook notation.

        Args:
          previous_after_values: The after values of all before nodes.
        Returns:
          The before value for the current node.
        """
        raise NotImplementedError

    def compute_after_value(self, node, before_value):
        """Computes the after value for a node from the node and the before value.

        This is the 'transfer' function of the analysis.
        TODO(manishs): Update terminology to match standard textbook notation.

        Args:
          node: The node or block for which to compute the after value.
          before_value: The before value of the node.
        Returns:
          The computed after value for the node.
        """
        raise NotImplementedError

    def visit(self, node):
        """Visit the nodes of the control flow graph, performing the analysis.

        Terminology:
          in_value: The value of the analysis at the start of a node.
          out_value: The value of the analysis at the end of a node.
          before_value: in_value in a forward analysis; out_value in a backward
            analysis.
          after_value: out_value in a forward analysis; in_value in a backward
            analysis.

        Args:
          node: A graph element that supports the .next / .prev API, such as a
            ControlFlowNode from a ControlFlowGraph or a BasicBlock from a
            ControlFlowGraph.
        """
        to_visit = collections.deque([node])
        while to_visit:
            node = to_visit.popleft()

            before_nodes = node.prev if self.forward else node.next
            after_nodes = node.next if self.forward else node.prev
            previous_after_values = [
                before_node.get_label(self.after_label)
                for before_node in before_nodes
                if before_node.has_label(self.after_label)
            ]

            if node.has_label(self.after_label):
                initial_after_value_hash = hash(node.get_label(self.after_label))
            else:
                initial_after_value_hash = None
            before_value = self.aggregate_previous_after_values(previous_after_values)
            node.set_label(self.before_label, before_value)
            after_value = self.compute_after_value(node, before_value)
            node.set_label(self.after_label, after_value)
            if hash(after_value) != initial_after_value_hash:
                for after_node in after_nodes:
                    to_visit.append(after_node)
