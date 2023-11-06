import ast


class DataDependencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = {}

    def visit_FunctionDef(self, node):
        for arg in node.args.args:
            self.dependencies[arg.arg] = []
        self.generic_visit(node)

    def visit_Assign(self, node):
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        values = [v.id for v in ast.walk(node.value) if isinstance(v, ast.Name)]
        for target in targets:
            if target not in self.dependencies:
                self.dependencies[target] = []
            for value in values:
                self.dependencies[target].append((value, node.lineno))
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        target = node.target.id if isinstance(node.target, ast.Name) else None
        values = [v.id for v in ast.walk(node.value) if isinstance(v, ast.Name)]
        if target:
            if target not in self.dependencies:
                self.dependencies[target] = []
            for value in values:
                self.dependencies[target].append((value, node.lineno))
        self.generic_visit(node)

    def visit_Call(self, node):
        func = node.func.id if isinstance(node.func, ast.Name) else None
        args = [arg.id for arg in node.args if isinstance(arg, ast.Name)]
        if func:
            if func not in self.dependencies:
                self.dependencies[func] = []
            for arg in args:
                self.dependencies[func].append((arg, node.lineno))
        self.generic_visit(node)

    def visit_For(self, node):
        target = node.target.id if isinstance(node.target, ast.Name) else None
        iter_values = [v.id for v in ast.walk(node.iter) if isinstance(v, ast.Name)]
        if target:
            if target not in self.dependencies:
                self.dependencies[target] = []
            for value in iter_values:
                self.dependencies[target].append((value, node.lineno))
        self.generic_visit(node)


def get_data_dependencies(code):
    tree = ast.parse(code)
    visitor = DataDependencyVisitor()
    visitor.visit(tree)
    return visitor.dependencies
