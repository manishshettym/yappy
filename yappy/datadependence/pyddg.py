import ast


class DataDependencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = {}
        self.current_blocks = []

    def visit_FunctionDef(self, node):
        for arg in node.args.args:
            self.dependencies[arg.arg] = []
        self.current_blocks.append((node.name, node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()

    def visit_Assign(self, node):
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        values = [v.id for v in ast.walk(node.value) if isinstance(v, ast.Name)]
        for target in targets:
            if target not in self.dependencies:
                self.dependencies[target] = []
            for value in values:
                self.dependencies[target].append((value, node.lineno))
            for block in self.current_blocks:
                self.dependencies[target].append(block)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        target = node.target.id if isinstance(node.target, ast.Name) else None
        values = [v.id for v in ast.walk(node.value) if isinstance(v, ast.Name)]
        if target:
            if target not in self.dependencies:
                self.dependencies[target] = []
            for value in values:
                self.dependencies[target].append((value, node.lineno))
            for block in self.current_blocks:
                self.dependencies[target].append(block)
        self.generic_visit(node)

    #### Dependency in blocks of code ####

    def visit_For(self, node):
        # loop variables are dependent on the loop condition
        # and the loop body is dependent on the loop variables

        # loop variables
        if isinstance(node.target, ast.Tuple):
            targets = [t.id for t in node.target.elts if isinstance(t, ast.Name)]
        else:
            targets = [node.target.id]

        values = [v.id for v in ast.walk(node.iter) if isinstance(v, ast.Name)]
        for target in targets:
            if target not in self.dependencies:
                self.dependencies[target] = []
            for value in values:
                self.dependencies[target].append((value, node.lineno))
            for block in self.current_blocks:
                self.dependencies[target].append(block)

        # loop body (visit the body)
        self.current_blocks.append(("For", node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()

    def visit_If(self, node):
        self.current_blocks.append(("If", node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()

    def visit_IfExp(self, node):
        self.current_blocks.append(("IfExp", node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()

    def visit_While(self, node):
        self.current_blocks.append(("While", node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()

    def visit_With(self, node):
        self.current_blocks.append(("With", node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()

    def visit_Try(self, node):
        self.current_blocks.append(("Try", node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()

    def visit_ExceptHandler(self, node):
        self.current_blocks.append(("Except", node.lineno))
        self.generic_visit(node)
        self.current_blocks.pop()


def get_data_dependencies(code):
    tree = ast.parse(code)
    visitor = DataDependencyVisitor()
    visitor.visit(tree)
    return visitor.dependencies
