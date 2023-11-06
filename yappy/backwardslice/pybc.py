from yappy.datadependence.pyddg import get_data_dependencies


def print_with_highlight(code, highlight_lines):
    # TODO: FIXME: this is hacky because we need to handle this at the
    # statement level and not line level.
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if i + 1 in highlight_lines:
            print("\033[92m{}\033[0m".format(line))
        else:
            print(line)

    print()


def get_backward_slice(dependencies, line):
    slice = set()
    slice.add(line)

    def visit(var):
        if var in dependencies:
            for dep, dep_line in dependencies[var]:
                if dep_line < line and dep_line not in slice:
                    slice.add(dep_line)
                    visit(dep)

    # visiting a variable whose dependency is at line
    # i.e., LHS of the assignment at line
    # note: only visits LHS and not variables after line (because backward slice)
    for var in dependencies:
        for dep, dep_line in dependencies[var]:
            if dep_line == line:
                visit(var)

    # visiting the variables that the line depends on
    # i.e., RHS of the assignment at line
    for var, deps in dependencies.items():
        for dep, dep_line in deps:
            if dep_line == line:
                visit(dep)

    return sorted(list(slice))


code = """def foo(x, y, z):
    x = x + 1
    y = y + 2
    for i in range(y):
        if i % 2 == 0:
            z = x + 2
        else:
            z = x + 3
        a = y + 1
    k = bar(z)
    return a
"""

ddg = get_data_dependencies(code)
print(ddg)
slice_lines = get_backward_slice(ddg, 10)


print(slice_lines)
print_with_highlight(code, slice_lines)
