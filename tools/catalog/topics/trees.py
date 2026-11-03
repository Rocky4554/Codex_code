"""Binary Trees — traversals, views, paths and construction."""
import sys
from collections import deque

from lib import Playlist, Problem, TreeNode, boolstr, ints, join, lines, parse_tree, random_tree, serialize_tree

sys.setrecursionlimit(10000)

PLAYLISTS = [
    Playlist(
        key="trees",
        title="13 · Binary Trees",
        description="Traversals, views, root-to-leaf paths and tree construction: recursion on trees until it feels natural.",
        accent="#B5E8A6",
        titles=[
            "Inorder Traversal",
            "Preorder Traversal",
            "Postorder Traversal",
            "Level Order Traversal",
            "Count Nodes",
            "Height of Tree",
            "Same Tree",
            "Symmetric Tree",
            "Path Sum",
            "All Root-to-Leaf Paths",
            "Check Balanced Tree",
            "Diameter of Binary Tree",
            "Right Side View",
            "Zigzag Level Order Traversal",
            "Top View of a Tree",
            "Bottom View of a Tree",
            "Boundary Traversal",
            "Vertical Order Traversal",
            "Lowest Common Ancestor",
            "Maximum Width of Binary Tree",
            "Nodes at Distance K",
            "Minimum Time to Burn the Tree",
            "Construct Tree from Preorder and Inorder",
            "Flatten Tree to Linked List",
            "Maximum Path Sum",
        ],
    )
]

TREE_INPUT = "a binary tree as space-separated level-order values, with `null` for a missing child (an empty tree is just `null`)"


# ── shared helpers (bst.py imports these) ───────────────────────

def all_nodes(root):
    out, st = [], [root] if root else []
    while st:
        n = st.pop()
        out.append(n)
        if n.right:
            st.append(n.right)
        if n.left:
            st.append(n.left)
    return out


def inorder_vals(root):
    out, st, cur = [], [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        out.append(cur.val)
        cur = cur.right
    return out


def chain(vals, side):
    root = cur = None
    for v in vals:
        node = TreeNode(v)
        if root is None:
            root = cur = node
        else:
            setattr(cur, side, node)
            cur = node
    return root


def zigzag_chain(r, vals):
    root = cur = None
    for v in vals:
        node = TreeNode(v)
        if root is None:
            root = cur = node
        else:
            setattr(cur, r.choice(("left", "right")), node)
            cur = node
    return root


def rtree(r, n, lo=1, hi=99, distinct=True):
    return serialize_tree(random_tree(r, n, lo, hi, distinct=distinct))


def shape_tests(r, lo=1, hi=99, empty=True, big=True, distinct=True):
    """A spread of tree shapes as input lines."""
    pool = lambda k: r.sample(range(lo, hi + 1), k) if distinct else [r.randint(lo, hi) for _ in range(k)]
    out = ["null"] if empty else []
    out.append(str(pool(1)[0]))
    out.append(serialize_tree(chain(pool(6), "left")))
    out.append(serialize_tree(chain(pool(7), "right")))
    out.append(serialize_tree(zigzag_chain(r, pool(8))))
    out.append(join(pool(15)))  # complete tree of 4 levels
    for n in (5, 9, 14, 25):
        out.append(rtree(r, n, lo, hi, distinct))
    if big:
        out.append(serialize_tree(random_tree(r, 400, -999 if lo < 0 else 1, 999, distinct=distinct)))
    return out


def paths_from_root(root):
    """value -> list of values on the path from the root (values assumed distinct)."""
    out = {}
    st = [(root, [root.val])] if root else []
    while st:
        n, p = st.pop()
        out[n.val] = p
        for c in (n.left, n.right):
            if c:
                st.append((c, p + [c.val]))
    return out


def lca_by_paths(paths, a, b):
    pa, pb = paths[a], paths[b]
    k = 0
    while k < len(pa) and k < len(pb) and pa[k] == pb[k]:
        k += 1
    return pa[k - 1], k


def dist_by_paths(paths, a, b):
    _, common = lca_by_paths(paths, a, b)
    return len(paths[a]) + len(paths[b]) - 2 * common


def levels(root):
    out, q = [], deque([root] if root else [])
    while q:
        lvl = []
        for _ in range(len(q)):
            n = q.popleft()
            lvl.append(n)
            if n.left:
                q.append(n.left)
            if n.right:
                q.append(n.right)
        out.append(lvl)
    return out


def _tree(inp, k=0):
    return parse_tree(lines(inp)[k])


def _pick_vals(r, line, k):
    vals = [int(t) for t in line.split() if t != "null"]
    return r.sample(vals, min(k, len(vals)))


# ── solutions ────────────────────────────────────────────────────

def _postorder(inp):
    out = []

    def go(n):
        if n:
            go(n.left)
            go(n.right)
            out.append(n.val)

    go(_tree(inp))
    return join(out) if out else "empty"


def _postorder_brute(inp):
    root = _tree(inp)
    if not root:
        return "empty"
    s1, s2 = [root], []
    while s1:
        n = s1.pop()
        s2.append(n.val)
        if n.left:
            s1.append(n.left)
        if n.right:
            s1.append(n.right)
    return join(s2[::-1])


def _count(inp):
    def go(n):
        return 0 if n is None else 1 + go(n.left) + go(n.right)

    return str(go(_tree(inp)))


def _count_brute(inp):
    return str(sum(1 for t in lines(inp)[0].split() if t != "null"))


def _same(inp):
    def eq(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and eq(a.left, b.left) and eq(a.right, b.right)

    return boolstr(eq(_tree(inp, 0), _tree(inp, 1)))


def _same_brute(inp):
    return boolstr(serialize_tree(_tree(inp, 0)) == serialize_tree(_tree(inp, 1)))


def _mirror(n):
    return None if n is None else TreeNode(n.val, _mirror(n.right), _mirror(n.left))


def _symmetric(inp):
    def mirror(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    root = _tree(inp)
    return boolstr(root is None or mirror(root.left, root.right))


def _symmetric_brute(inp):
    root = _tree(inp)
    return boolstr(serialize_tree(root) == serialize_tree(_mirror(root)))


def _diameter(inp):
    best = 0

    def h(n):
        nonlocal best
        if not n:
            return 0
        a, b = h(n.left), h(n.right)
        best = max(best, a + b)
        return 1 + max(a, b)

    h(_tree(inp))
    return str(best)


def _undirected(root):
    adj = {}
    for n in all_nodes(root):
        adj.setdefault(id(n), [])
        for c in (n.left, n.right):
            if c:
                adj[id(n)].append(id(c))
                adj.setdefault(id(c), []).append(id(n))
    return adj


def _bfs_far(adj, s):
    dist = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return max(dist.values())


def _diameter_brute(inp):
    root = _tree(inp)
    if not root:
        return "0"
    adj = _undirected(root)
    return str(max(_bfs_far(adj, s) for s in adj))


def _path_sum(inp):
    ls = lines(inp)
    root, target = parse_tree(ls[0]), int(ls[1])

    def go(n, rem):
        if not n:
            return False
        rem -= n.val
        if not n.left and not n.right:
            return rem == 0
        return go(n.left, rem) or go(n.right, rem)

    return boolstr(go(root, target))


def _leaf_sums(root):
    sums, st = [], [(root, root.val)] if root else []
    while st:
        n, s = st.pop()
        if not n.left and not n.right:
            sums.append(s)
        for c in (n.left, n.right):
            if c:
                st.append((c, s + c.val))
    return sums


def _path_sum_brute(inp):
    ls = lines(inp)
    return boolstr(int(ls[1]) in _leaf_sums(parse_tree(ls[0])))


def _root_leaf_paths(inp):
    out = []

    def go(n, path):
        path.append(str(n.val))
        if not n.left and not n.right:
            out.append("->".join(path))
        if n.left:
            go(n.left, path)
        if n.right:
            go(n.right, path)
        path.pop()

    root = _tree(inp)
    if root:
        go(root, [])
    return "\n".join(out) if out else "empty"


def _right_view(inp):
    lv = levels(_tree(inp))
    return join(l[-1].val for l in lv) if lv else "empty"


def _right_view_brute(inp):
    seen = {}

    def go(n, d):
        if n:
            seen.setdefault(d, n.val)
            go(n.right, d + 1)
            go(n.left, d + 1)

    go(_tree(inp), 0)
    return join(seen[d] for d in sorted(seen)) if seen else "empty"


def _zigzag(inp):
    lv = levels(_tree(inp))
    if not lv:
        return "empty"
    return "\n".join(join(n.val for n in (l if i % 2 == 0 else l[::-1])) for i, l in enumerate(lv))


def _bfs_cols(root):
    """[(node, col, depth, bfs_index)] in level order."""
    out, q, i = [], deque([(root, 0, 0)] if root else []), 0
    while q:
        n, c, d = q.popleft()
        out.append((n, c, d, i))
        i += 1
        if n.left:
            q.append((n.left, c - 1, d + 1))
        if n.right:
            q.append((n.right, c + 1, d + 1))
    return out


def _top_view(inp):
    first = {}
    for n, c, _, _ in _bfs_cols(_tree(inp)):
        first.setdefault(c, n.val)
    return join(first[c] for c in sorted(first)) if first else "empty"


def _top_view_brute(inp):
    best = {}
    for n, c, d, i in _bfs_cols(_tree(inp)):
        if c not in best or (d, i) < best[c][0]:
            best[c] = ((d, i), n.val)
    return join(best[c][1] for c in sorted(best)) if best else "empty"


def _bottom_view(inp):
    last = {}
    for n, c, _, _ in _bfs_cols(_tree(inp)):
        last[c] = n.val
    return join(last[c] for c in sorted(last)) if last else "empty"


def _bottom_view_brute(inp):
    best = {}
    for n, c, d, i in _bfs_cols(_tree(inp)):
        if c not in best or (d, i) > best[c][0]:
            best[c] = ((d, i), n.val)
    return join(best[c][1] for c in sorted(best)) if best else "empty"


def _vertical(inp):
    cells = sorted((c, d, n.val) for n, c, d, _ in _bfs_cols(_tree(inp)))
    if not cells:
        return "empty"
    out, cur, col = [], [], cells[0][0]
    for c, _, v in cells:
        if c != col:
            out.append(join(cur))
            cur, col = [], c
        cur.append(v)
    out.append(join(cur))
    return "\n".join(out)


def _vertical_brute(inp):
    cols = {}

    def go(n, c, d):
        if n:
            cols.setdefault(c, []).append((d, n.val))
            go(n.left, c - 1, d + 1)
            go(n.right, c + 1, d + 1)

    go(_tree(inp), 0, 0)
    return "\n".join(join(v for _, v in sorted(cols[c])) for c in sorted(cols)) or "empty"


def _is_leaf(n):
    return n is not None and n.left is None and n.right is None


def _boundary(inp):
    root = _tree(inp)
    if not root:
        return "empty"
    if _is_leaf(root):
        return str(root.val)
    res = [root.val]
    cur = root.left
    while cur:
        if not _is_leaf(cur):
            res.append(cur.val)
        cur = cur.left if cur.left else cur.right
    st = [root]
    while st:  # leaves, left to right
        n = st.pop()
        if _is_leaf(n):
            res.append(n.val)
        if n.right:
            st.append(n.right)
        if n.left:
            st.append(n.left)
    right, cur = [], root.right
    while cur:
        if not _is_leaf(cur):
            right.append(cur.val)
        cur = cur.right if cur.right else cur.left
    return join(res + right[::-1])


def _lca(inp):
    ls = lines(inp)
    root = parse_tree(ls[0])
    a, b = ints(ls[1])

    def go(n):
        if n is None or n.val in (a, b):
            return n
        l, r = go(n.left), go(n.right)
        return n if l and r else l or r

    return str(go(root).val)


def _lca_brute(inp):
    ls = lines(inp)
    a, b = ints(ls[1])
    return str(lca_by_paths(paths_from_root(parse_tree(ls[0])), a, b)[0])


def _max_width(inp):
    root = _tree(inp)
    if not root:
        return "0"
    best, q = 0, [(root, 0)]
    while q:
        base = q[0][1]
        best = max(best, q[-1][1] - q[0][1] + 1)
        nxt = []
        for n, p in q:
            p -= base
            if n.left:
                nxt.append((n.left, 2 * p))
            if n.right:
                nxt.append((n.right, 2 * p + 1))
        q = nxt
    return str(best)


def _max_width_brute(inp):
    span = {}

    def go(n, d, p):
        if n:
            lo, hi = span.get(d, (p, p))
            span[d] = (min(lo, p), max(hi, p))
            go(n.left, d + 1, 2 * p)
            go(n.right, d + 1, 2 * p + 1)

    go(_tree(inp), 0, 0)
    return str(max((hi - lo + 1 for lo, hi in span.values()), default=0))


def _dist_k(inp):
    ls = lines(inp)
    root = parse_tree(ls[0])
    target, k = ints(ls[1])
    parent, start = {}, None
    for n in all_nodes(root):
        if n.val == target:
            start = n
        for c in (n.left, n.right):
            if c:
                parent[id(c)] = n
    seen, frontier = {id(start)}, [start]
    for _ in range(k):
        nxt = []
        for n in frontier:
            for m in (n.left, n.right, parent.get(id(n))):
                if m and id(m) not in seen:
                    seen.add(id(m))
                    nxt.append(m)
        frontier = nxt
    vals = sorted(n.val for n in frontier)
    return join(vals) if vals else "none"


def _dist_k_brute(inp):
    ls = lines(inp)
    target, k = ints(ls[1])
    paths = paths_from_root(parse_tree(ls[0]))
    vals = sorted(v for v in paths if dist_by_paths(paths, target, v) == k)
    return join(vals) if vals else "none"


def _burn(inp):
    ls = lines(inp)
    root = parse_tree(ls[0])
    start = int(ls[1])
    adj = {}
    node_of = {}
    for n in all_nodes(root):
        node_of[n.val] = n
        adj.setdefault(n.val, [])
        for c in (n.left, n.right):
            if c:
                adj[n.val].append(c.val)
                adj.setdefault(c.val, []).append(n.val)
    dist = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return str(max(dist.values()))


def _burn_brute(inp):
    ls = lines(inp)
    start = int(ls[1])
    paths = paths_from_root(parse_tree(ls[0]))
    return str(max(dist_by_paths(paths, start, v) for v in paths))


def _build_pre_in(inp):
    ls = lines(inp)
    pre, ino = ints(ls[0]), ints(ls[1])
    where = {v: i for i, v in enumerate(ino)}
    it = iter(pre)

    def build(lo, hi):
        if lo > hi:
            return None
        v = next(it)
        node = TreeNode(v)
        node.left = build(lo, where[v] - 1)
        node.right = build(where[v] + 1, hi)
        return node

    return serialize_tree(build(0, len(ino) - 1))


def _build_pre_in_brute(inp):
    ls = lines(inp)

    def build(pre, ino):
        if not pre:
            return None
        k = ino.index(pre[0])
        return TreeNode(pre[0], build(pre[1 : k + 1], ino[:k]), build(pre[k + 1 :], ino[k + 1 :]))

    return serialize_tree(build(ints(ls[0]), ints(ls[1])))


def _flatten(inp):
    root = _tree(inp)
    cur = root
    while cur:  # Morris-style: splice the left subtree in between node and its right subtree
        if cur.left:
            tail = cur.left
            while tail.right:
                tail = tail.right
            tail.right = cur.right
            cur.right, cur.left = cur.left, None
        cur = cur.right
    out, cur = [], root
    while cur:
        out.append(cur.val)
        cur = cur.right
    return join(out) if out else "empty"


def _preorder(inp):
    out = [n.val for n in all_nodes(_tree(inp))]
    return join(out) if out else "empty"


def _max_path(inp):
    best = None

    def gain(n):
        nonlocal best
        if not n:
            return 0
        l, r = max(gain(n.left), 0), max(gain(n.right), 0)
        here = n.val + l + r
        best = here if best is None else max(best, here)
        return n.val + max(l, r)

    gain(_tree(inp))
    return str(best)


def _max_path_brute(inp):
    root = _tree(inp)
    nodes = all_nodes(root)
    parent, depth = {id(root): None}, {id(root): 0}
    for n in nodes:
        for c in (n.left, n.right):
            if c:
                parent[id(c)] = n
                depth[id(c)] = depth[id(n)] + 1
    best = None
    for a in nodes:
        for b in nodes:
            x, y, s = a, b, 0
            while x is not y:
                if depth[id(x)] >= depth[id(y)]:
                    s += x.val
                    x = parent[id(x)]
                else:
                    s += y.val
                    y = parent[id(y)]
            s += x.val
            best = s if best is None else max(best, s)
    return str(best)


# ── tests ────────────────────────────────────────────────────────

def _t_shapes(r):
    return shape_tests(r)


def _t_same(r):
    out = ["null\nnull", "1\nnull", "null\n5"]
    for n in (1, 4, 9, 20, 60):
        a = rtree(r, n)
        out.append(f"{a}\n{a}")
        root = parse_tree(a)
        nodes = all_nodes(root)
        x = r.choice(nodes)
        x.val = x.val + 100
        out.append(f"{a}\n{serialize_tree(root)}")
    out.append("1 2 3\n1 3 2")
    out.append("1 2\n1 null 2")
    return out


def _sym_line(r, n):
    half = random_tree(r, n, 1, 9, distinct=False)
    return serialize_tree(TreeNode(r.randint(1, 9), half, _mirror(half)))


def _t_symmetric(r):
    out = ["null", "7", "1 2 2", "1 2 3", "1 2 2 null 3 null 3", "1 2 2 3 4 4 3"]
    for n in (2, 5, 12, 40):
        line = _sym_line(r, n)
        out.append(line)
        root = parse_tree(line)
        leaf = [x for x in all_nodes(root) if _is_leaf(x)]
        r.choice(leaf).val += 1
        out.append(serialize_tree(root))
    out.append(rtree(r, 9))
    return out


def _t_path_sum(r):
    out = ["null\n0", "5\n5", "5\n6", "1 2\n1", "1 2\n3"]
    for n in (6, 10, 20, 40, 300):
        line = rtree(r, n, -20, 20, distinct=False)
        sums = _leaf_sums(parse_tree(line))
        out.append(f"{line}\n{r.choice(sums)}")
        out.append(f"{line}\n{r.randint(-100, 100)}")
    return out


def _t_with_pair(r):
    out = ["1 2\n1 2", "1 null 2 null 3\n3 2"]
    for n in (3, 6, 12, 25, 60, 400):
        line = rtree(r, n, 1, 999)
        a, b = _pick_vals(r, line, 2)
        out.append(f"{line}\n{a} {b}")
    line = rtree(r, 30, 1, 999)
    a = _pick_vals(r, line, 1)[0]
    paths = paths_from_root(parse_tree(line))
    deep = max(paths, key=lambda v: len(paths[v]))
    out.append(f"{line}\n{paths[deep][0]} {deep}")  # one is the root
    out.append(f"{line}\n{deep} {paths[deep][-2] if len(paths[deep]) > 1 else a}")  # one is an ancestor of the other
    return out


def _t_dist_k(r):
    out = ["1\n1 0", "1\n1 3", "3 5 1 6 2 0 8 null null 7 4\n5 2"]
    for n in (5, 10, 25, 60, 300):
        line = rtree(r, n, 1, 999)
        v = _pick_vals(r, line, 1)[0]
        out.append(f"{line}\n{v} {r.randint(0, 5)}")
    out.append(f"{line}\n{v} 50")
    return out


def _t_burn(r):
    out = ["4\n4", "1 2 3\n2", serialize_tree(chain(list(range(1, 11)), "left")) + "\n10"]
    for n in (5, 12, 30, 80, 400):
        line = rtree(r, n, 1, 999)
        out.append(f"{line}\n{_pick_vals(r, line, 1)[0]}")
    return out


def _preorder_of(root):
    return [n.val for n in all_nodes(root)]


def _t_pre_in(r):
    out = []
    for root in (
        TreeNode(1),
        chain([1, 2, 3, 4], "left"),
        chain([4, 3, 2, 1], "right"),
        zigzag_chain(r, r.sample(range(1, 50), 7)),
        *(random_tree(r, n, 1, 999) for n in (5, 9, 20, 50, 300)),
    ):
        out.append(f"{join(_preorder_of(root))}\n{join(inorder_vals(root))}")
    return out


PROBLEMS = [
    Problem(
        title="Postorder Traversal",
        difficulty="EASY",
        topics=["Tree", "Binary Tree", "DFS", "Recursion"],
        description=f"""Print the values of a binary tree in **postorder**: left subtree, then right subtree, then the node itself.

**Input:** {TREE_INPUT}.

**Output:** the postorder values space-separated, or `empty` if the tree has no nodes.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_postorder,
        brute=_postorder_brute,
        examples=[("1 2 3 4 5", "Children 4 and 5 come before 2, both subtrees before the root 1."), ("1 null 2 3", "3 is the left child of 2, so the order is 3, 2, 1.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Count Nodes",
        difficulty="EASY",
        topics=["Tree", "Binary Tree", "DFS", "Recursion"],
        description=f"""Count how many nodes a binary tree has. A tree's size is 1 (the root) plus the sizes of its two subtrees.

**Input:** {TREE_INPUT}.

**Output:** the number of nodes.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_count,
        brute=_count_brute,
        examples=[("1 2 3 4 5 6", "Six values, six nodes."), ("null", "An empty tree has 0 nodes.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Same Tree",
        difficulty="EASY",
        topics=["Tree", "Binary Tree", "DFS"],
        description=f"""Two binary trees are the same when they have exactly the same shape and every pair of matching nodes holds the same value. Print `true` if the two given trees are the same, otherwise `false`.

**Input:** two lines, each {TREE_INPUT}.

**Output:** `true` or `false`.""",
        constraints=["0 <= number of nodes in each tree <= 1000"],
        solve=_same,
        brute=_same_brute,
        examples=[("1 2 3\n1 2 3", "Identical shape and values."), ("1 2\n1 null 2", "Same values, but 2 hangs on different sides.")],
        tests=_t_same,
    ),
    Problem(
        title="Symmetric Tree",
        difficulty="EASY",
        topics=["Tree", "Binary Tree", "DFS", "BFS"],
        description=f"""A tree is **symmetric** if its left subtree is a mirror image of its right subtree: same values, with left and right swapped at every level. Print `true` if the tree is symmetric, otherwise `false`. An empty tree counts as symmetric.

**Input:** {TREE_INPUT}.

**Output:** `true` or `false`.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_symmetric,
        brute=_symmetric_brute,
        examples=[("1 2 2 3 4 4 3", "The left side 2 → (3, 4) mirrors the right side 2 → (4, 3)."), ("1 2 2 null 3 null 3", "Both 3s hang to the right, so it isn't a mirror.")],
        tests=_t_symmetric,
    ),
    Problem(
        title="Path Sum",
        difficulty="EASY",
        topics=["Tree", "Binary Tree", "DFS"],
        description=f"""Is there a path from the root down to a **leaf** (a node with no children) whose values add up to `target`? Print `true` or `false`. An empty tree has no paths.

**Input:** line 1 is {TREE_INPUT}. Line 2 is the integer `target`.

**Output:** `true` or `false`.""",
        constraints=["0 <= number of nodes <= 1000", "-1000 <= node value <= 1000", "-10^6 <= target <= 10^6"],
        solve=_path_sum,
        brute=_path_sum_brute,
        examples=[("5 4 8 11 null 13 4 7 2\n22", "5 → 4 → 11 → 2 adds up to 22."), ("1 2 3\n5", "The leaf paths sum to 3 and 4.")],
        tests=_t_path_sum,
    ),
    Problem(
        title="All Root-to-Leaf Paths",
        difficulty="EASY",
        topics=["Tree", "Binary Tree", "DFS", "Recursion"],
        description=f"""Print every path from the root to a leaf. Write a path as its values joined by `->`, for example `1->2->5`.

Print one path per line, in the order a depth-first search visits the leaves when it always explores the left child before the right one.

**Input:** {TREE_INPUT}.

**Output:** the paths, one per line, or `empty` if the tree has no nodes.""",
        constraints=["0 <= number of nodes <= 500"],
        solve=_root_leaf_paths,
        examples=[("1 2 3 null 5", "Leaves 5 and 3 give two paths."), ("7", "A lone root is its own leaf.")],
        tests=lambda r: shape_tests(r, big=False) + [rtree(r, 150, 1, 999)],
    ),
    Problem(
        title="Diameter of Binary Tree",
        difficulty="EASY",
        topics=["Tree", "Binary Tree", "DFS"],
        description=f"""The **diameter** of a tree is the number of edges on the longest path between any two nodes. The path doesn't have to pass through the root.

Hint: at each node, the longest path that bends there is (height of left subtree) + (height of right subtree).

**Input:** {TREE_INPUT}.

**Output:** the diameter (0 for an empty or single-node tree).""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_diameter,
        brute=_diameter_brute,
        examples=[("1 2 3 4 5", "4 → 2 → 1 → 3 has 3 edges."), ("1 2 null 3 4 5 null null 6", "The longest path 5 → 3 → 2 → 4 → 6 never touches the root.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Right Side View",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "BFS", "DFS"],
        description=f"""Imagine standing to the right of a binary tree. Print the value you'd see on each level: the rightmost node of every level, from the top level down.

**Input:** {TREE_INPUT}.

**Output:** the visible values space-separated, top to bottom, or `empty` for an empty tree.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_right_view,
        brute=_right_view_brute,
        examples=[("1 2 3 null 5 null 4", "Levels are [1], [2, 3], [5, 4]; the last of each is seen."), ("1 2 3 4", "4 sticks out on the bottom level even though it's on the left.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Zigzag Level Order Traversal",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "BFS"],
        description=f"""Print the tree level by level, alternating direction: the first level (the root) left to right, the next right to left, then left to right again, and so on.

**Input:** {TREE_INPUT}.

**Output:** one line per level with its values space-separated, or `empty` for an empty tree.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_zigzag,
        examples=[("3 9 20 null null 15 7", "Level 2 is printed backwards: 20 9."), ("1 2 3 4 5 6 7", "Levels: 1 | 3 2 | 4 5 6 7.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Top View of a Tree",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "BFS"],
        description=f"""Give the root column 0. A left child is one column to the left of its parent (column − 1), a right child one column to the right (column + 1).

The **top view** shows, for every column, the node nearest the top (smallest depth). If two nodes in a column have the same depth, the one that comes first in level order (further left) is seen.

Print the top view from the leftmost column to the rightmost.

**Input:** {TREE_INPUT}.

**Output:** the visible values space-separated, or `empty` for an empty tree.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_top_view,
        brute=_top_view_brute,
        examples=[("1 2 3 4 5 6 7", "Columns −2…2 show 4, 2, 1, 3, 7; 5 and 6 are hidden under 1."), ("1 2 3 null 4 null null null 5 null 6", "The chain 4 → 5 → 6 drifts right: 4 and 5 hide behind 1 and 3, but 6 sticks out at column 2.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Bottom View of a Tree",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "BFS"],
        description=f"""Use columns as in the top view: the root is column 0, a left child is column − 1, a right child column + 1.

The **bottom view** shows, for every column, the deepest node. If two nodes in a column share the greatest depth, the one that comes **later** in level order (further right) is seen.

Print the bottom view from the leftmost column to the rightmost.

**Input:** {TREE_INPUT}.

**Output:** the visible values space-separated, or `empty` for an empty tree.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_bottom_view,
        brute=_bottom_view_brute,
        examples=[("20 8 22 5 3 null 25 null null 10 14", "Column 0 holds 20 and 3 (deeper), column 1 holds 22 and 14 (deeper)."), ("1 2 3 4 5 6 7", "5 and 6 tie at column 0 depth 2; 6 comes later in level order.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Boundary Traversal",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "DFS"],
        description=f"""Print the boundary of a binary tree going anticlockwise, starting from the root. The boundary is made of four parts, with no node printed twice:

1. **The root.**
2. **The left boundary**, top-down: start at the root's left child, and at each step move to the left child if there is one, otherwise the right child. Leaves are left out (they come in part 3). If the root has no left child, this part is empty.
3. **All leaves** from left to right (excluding the root).
4. **The right boundary**, bottom-up: start at the root's right child and move to the right child if there is one, otherwise the left child, leaving out leaves; print these nodes in reverse (bottom to top). If the root has no right child, this part is empty.

A tree that is just a root prints only the root.

**Input:** {TREE_INPUT}.

**Output:** the boundary values space-separated, or `empty` for an empty tree.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_boundary,
        examples=[("1 2 3 4 5 6 7 null null 8 9", "Root 1, left edge 2, leaves 4 8 9 6 7, right edge 3."), ("1 null 2 3 4", "No left subtree: root, then leaves 3 4, then the right edge 2.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Vertical Order Traversal",
        difficulty="HARD",
        topics=["Tree", "Binary Tree", "BFS", "DFS"],
        description=f"""Give the root column 0 and depth 0. A left child has column − 1 and depth + 1; a right child has column + 1 and depth + 1.

Print the tree column by column from the leftmost column to the rightmost. Within a column, list nodes from the top (smallest depth) down; nodes that share both column and depth are listed in increasing order of value.

**Input:** {TREE_INPUT}.

**Output:** one line per column with its values space-separated, or `empty` for an empty tree.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_vertical,
        brute=_vertical_brute,
        examples=[("3 9 20 null null 15 7", "Columns: [9], [3, 15], [20], [7]."), ("1 2 3 4 6 5 7", "6 and 5 share column 0 and depth 2, so they're sorted: 5 6.")],
        tests=lambda r: shape_tests(r, distinct=False) + [rtree(r, 30, 1, 5, distinct=False)],
    ),
    Problem(
        title="Lowest Common Ancestor",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "DFS", "Recursion"],
        description=f"""The **lowest common ancestor** of two nodes `a` and `b` is the deepest node that has both of them in its subtree. A node counts as being in its own subtree, so if `a` is an ancestor of `b`, the answer is `a`.

All values in the tree are distinct, and both `a` and `b` are in the tree.

**Input:** line 1 is {TREE_INPUT}. Line 2 has the two values `a` and `b`.

**Output:** the value of their lowest common ancestor.""",
        constraints=["2 <= number of nodes <= 1000", "values are distinct", "a != b"],
        solve=_lca,
        brute=_lca_brute,
        examples=[("3 5 1 6 2 0 8 null null 7 4\n5 1", "5 and 1 meet at the root."), ("3 5 1 6 2 0 8 null null 7 4\n5 4", "4 is inside 5's subtree, so 5 is the answer.")],
        tests=_t_with_pair,
    ),
    Problem(
        title="Maximum Width of Binary Tree",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "BFS"],
        description=f"""Number the positions in each level as if the tree were complete: the root is position 0, and a node at position `p` has its left child at `2p` and its right child at `2p + 1`.

The **width** of a level is (position of its rightmost node) − (position of its leftmost node) + 1, so missing nodes between them count. Print the largest width over all levels.

**Input:** {TREE_INPUT}.

**Output:** the maximum width (0 for an empty tree).""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_max_width,
        brute=_max_width_brute,
        examples=[("1 3 2 5 3 null 9", "The bottom level spans positions 0 to 3: width 4."), ("1 3 2 5 null null 9 6 null 7", "The last level has 6 at position 0 and 7 at position 6: width 7.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Nodes at Distance K",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "BFS", "DFS"],
        description=f"""Find every node that is exactly `k` edges away from the node with value `target`. Paths may go up through parents as well as down through children.

All values are distinct and `target` is in the tree.

**Input:** line 1 is {TREE_INPUT}. Line 2 has `target` and `k`.

**Output:** the matching values in increasing order, space-separated, or `none` if there are none.""",
        constraints=["1 <= number of nodes <= 1000", "values are distinct", "0 <= k <= 1000"],
        solve=_dist_k,
        brute=_dist_k_brute,
        examples=[("3 5 1 6 2 0 8 null null 7 4\n5 2", "Two steps from 5: down to 7 and 4, or up through 3 to 1."), ("1 2 3\n2 3", "Nothing is 3 edges from 2.")],
        tests=_t_dist_k,
    ),
    Problem(
        title="Minimum Time to Burn the Tree",
        difficulty="HARD",
        topics=["Tree", "Binary Tree", "BFS"],
        description=f"""A fire starts at the node with value `start`. Every second it spreads from each burning node to its parent and its children. Print how many seconds it takes until every node is burning.

All values are distinct and `start` is in the tree.

**Input:** line 1 is {TREE_INPUT}. Line 2 is `start`.

**Output:** the number of seconds.""",
        constraints=["1 <= number of nodes <= 1000", "values are distinct"],
        solve=_burn,
        brute=_burn_brute,
        examples=[("1 2 3 4 5 null 6 null null 7 8\n8", "The fire reaches 6, the farthest node, after 5 seconds."), ("4\n4", "A single node is already burning: 0 seconds.")],
        tests=_t_burn,
    ),
    Problem(
        title="Construct Tree from Preorder and Inorder",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "Recursion", "DFS"],
        description="""Rebuild a binary tree from its preorder and inorder traversals. All values are distinct, so the tree is unique.

The first preorder value is the root; its position in the inorder list splits the remaining values into the left and right subtrees.

**Input:** line 1 is the preorder traversal, line 2 the inorder traversal (space-separated values).

**Output:** the rebuilt tree as space-separated level-order values with `null` for missing children (trailing `null`s omitted).""",
        constraints=["1 <= number of nodes <= 1000", "values are distinct"],
        solve=_build_pre_in,
        brute=_build_pre_in_brute,
        examples=[("3 9 20 15 7\n9 3 15 20 7", "Root 3; 9 is left of it in inorder, 15 20 7 are right."), ("1 2 3\n3 2 1", "Each value is to the left of the previous one: a left chain.")],
        tests=_t_pre_in,
    ),
    Problem(
        title="Flatten Tree to Linked List",
        difficulty="MEDIUM",
        topics=["Tree", "Binary Tree", "DFS", "Stack"],
        description=f"""Flatten a binary tree into a "linked list" in place: every node's left child becomes empty and its right child points to the next node in **preorder** (node, left subtree, right subtree).

Try to do it with O(1) extra space: for each node with a left subtree, attach its right subtree to the rightmost node of the left subtree, then move the left subtree over to the right.

Print the values by following right pointers from the root.

**Input:** {TREE_INPUT}.

**Output:** the values of the flattened list space-separated, or `empty` for an empty tree.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_flatten,
        brute=_preorder,
        examples=[("1 2 5 3 4 null 6", "Preorder: 1 2 3 4 5 6."), ("0", "One node is already flat.")],
        tests=_t_shapes,
    ),
    Problem(
        title="Maximum Path Sum",
        difficulty="HARD",
        topics=["Tree", "Binary Tree", "DFS", "Recursion"],
        description=f"""A **path** is any sequence of nodes where each adjacent pair is connected by an edge; no node repeats, and the path doesn't have to pass through the root. It contains at least one node.

Print the largest possible sum of values along a path. Values can be negative.

Hint: at each node, compute the best "downward" sum starting there, and update the answer with the path that bends at this node.

**Input:** {TREE_INPUT} (the tree is not empty).

**Output:** the maximum path sum.""",
        constraints=["1 <= number of nodes <= 1000", "-1000 <= node value <= 1000"],
        solve=_max_path,
        brute=_max_path_brute,
        examples=[("-10 9 20 null null 15 7", "15 → 20 → 7 gives 42."), ("-3 -2 -1", "All negative: the best path is the single node -1.")],
        tests=lambda r: shape_tests(r, lo=-30, hi=30, empty=False) + [rtree(r, 12, -9, -1, distinct=False)],
    ),
]
