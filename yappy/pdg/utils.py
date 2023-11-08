import enum
import gast as ast


class PDGEdgeType(enum.Enum):
    CD = 0
    DD = 1


def post_dominators(cfg):
    """Compute the post-dominators of each node in a control flow graph.

    A node V is post-dominated by a node U if every path from V to the end of
    the CFG must go through U.

    returns: a dictionary mapping a node to its set of post-dominators.
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

    return pdom


def immediate_post_dominator(pdom):
    """Compute the immediate post-dominator of each node in a control flow graph.

    Args:
        pdom: a dictionary mapping a node to its set of post-dominators.

    A node m is an immediate post-dominator of a node n if:
    1. m is a post-dominator of n
    2. m != n
    3. all other post-dominators of n post-dominate m
    """

    ipdom = {}

    for n, postdoms in pdom.items():
        # postdoms other than n itself
        postdoms = postdoms - {n}

        # m ∈ pdom(n) \ {n}
        for m in postdoms:
            # ∀d ∈ pdom(n) \ {m}: d ∈ pdom(m)
            if all(d in pdom[m] for d in postdoms if d != m):
                ipdom[n] = m
                break

    # print_ipdom(ipdom)

    return ipdom


def print_pdom(pdom):
    print("=== Post Dominators === ")
    for node in pdom:
        print(f"Post Dominators for {cfgnode2code(node)}:")
        for post_dominator in pdom[node]:
            print(cfgnode2code(post_dominator))
        print()


def print_ipdom(ipdom):
    print("=== Immediate Post Dominators === ")
    for node in ipdom:
        print(f"Immediate Post Dominator for {cfgnode2code(node)}:")
        print(cfgnode2code(ipdom[node]))
        print()


def cfgnode2code(cfgnode):
    return ast.unparse(cfgnode.instruction.node)
