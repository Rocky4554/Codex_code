"""Binary Search Trees — search, update, order statistics and repair."""
import sys

from lib import Playlist, Problem, TreeNode, boolstr, ints, join, lines, parse_tree, random_tree, serialize_tree
from topics.trees import all_nodes, chain, inorder_vals, lca_by_paths, paths_from_root

sys.setrecursionlimit(10000)

PLAYLISTS = [
    Playlist(
        key="bst",
        title="14 · Binary Search Trees",
        description="Use the left < node < right ordering to search, insert, delete and repair in O(height).",
        accent="#A6D8E8",
        titles=[
            "Search in a BST",
            "Insert into a BST",
            "Floor and Ceil in a BST",
            "Kth Smallest in a BST",
            "Kth Largest in a BST",
            "Validate BST",
            "LCA in a BST",
            "Minimum Difference in a BST",
            "Inorder Successor in a BST",
            "Delete Node in a BST",
            "Two Sum in a BST",
            "Construct BST from Preorder",
            "Recover a BST",
            "Largest BST Subtree",
        ],
    )
]

BST_INPUT = "a binary search tree as space-separated level-order values, with `null` for a missing child (an empty tree is just `null`). All values are distinct; every node's left subtree holds smaller values and its right subtree larger ones"
TREE_OUT = "the tree as space-separated level-order values with `null` for missing children (trailing `null`s omitted), or `null` if it is empty"


# ── test helpers ─────────────────────────────────────────────────

def bst(r, n, lo=1, hi=999):
    return random_tree(r, n, lo, hi, bst=True)


def bst_line(r, n, lo=1, hi=999):
    return serialize_tree(bst(r, n, lo, hi))


def bst_shapes(r, empty=True, big=True):
    """BST input lines: empty, single, both skews, balanced, random sizes."""
    out = ["null"] if empty else []
    out.append(str(r.randint(1, 999)))
    out.append(serialize_tree(chain(sorted(r.sample(range(1, 999), 6), reverse=True), "left")))
    out.append(serialize_tree(chain(sorted(r.sample(range(1, 999), 7)), "right")))
    out.append("8 4 12 2 6 10 14 1 3 5 7 9 11 13 15")
    for n in (5, 10, 20, 40):
        out.append(bst_line(r, n))
    if big:
        out.append(bst_line(r, 400))
    return out


def vals_of(line):
    return [int(t) for t in line.split() if t != "null"]


def _sorted_vals(inp):
    return sorted(vals_of(lines(inp)[0]))


def _insert(root, v):
    if root is None:
        return TreeNode(v)
    cur = root
    while True:
        if v < cur.val:
            if cur.left is None:
                cur.left = TreeNode(v)
                return root
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = TreeNode(v)
                return root
            cur = cur.right


def _insert_rec(root, v):
    if root is None:
        return TreeNode(v)
    if v < root.val:
        root.left = _insert_rec(root.left, v)
    else:
        root.right = _insert_rec(root.right, v)
    return root


# ── solutions ────────────────────────────────────────────────────

def _search(inp):
    ls = lines(inp)
    cur, x = parse_tree(ls[0]), int(ls[1])
    while cur and cur.val != x:
        cur = cur.left if x < cur.val else cur.right
    return serialize_tree(cur)


def _search_brute(inp):
    ls = lines(inp)
    x = int(ls[1])
    hit = [n for n in all_nodes(parse_tree(ls[0])) if n.val == x]
    return serialize_tree(hit[0] if hit else None)


def _insert_solve(inp):
    ls = lines(inp)
    return serialize_tree(_insert(parse_tree(ls[0]), int(ls[1])))


def _insert_brute(inp):
    ls = lines(inp)
    return serialize_tree(_insert_rec(parse_tree(ls[0]), int(ls[1])))


def _floor_ceil(inp):
    ls = lines(inp)
    cur, x = parse_tree(ls[0]), int(ls[1])
    fl = ce = -1
    while cur:
        if cur.val == x:
            fl = ce = x
            break
        if cur.val < x:
            fl = cur.val
            cur = cur.right
        else:
            ce = cur.val
            cur = cur.left
    return f"{fl} {ce}"


def _floor_ceil_brute(inp):
    ls = lines(inp)
    vs, x = vals_of(ls[0]), int(ls[1])
    fl = max((v for v in vs if v <= x), default=-1)
    ce = min((v for v in vs if v >= x), default=-1)
    return f"{fl} {ce}"


def _kth_smallest(inp):
    ls = lines(inp)
    root, k = parse_tree(ls[0]), int(ls[1])
    st, cur = [], root
    while True:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        k -= 1
        if k == 0:
            return str(cur.val)
        cur = cur.right


def _kth_smallest_brute(inp):
    ls = lines(inp)
    return str(_sorted_vals(inp)[int(ls[1]) - 1])


def _kth_largest(inp):
    ls = lines(inp)
    root, k = parse_tree(ls[0]), int(ls[1])
    st, cur = [], root
    while True:  # reverse inorder: right, node, left
        while cur:
            st.append(cur)
            cur = cur.right
        cur = st.pop()
        k -= 1
        if k == 0:
            return str(cur.val)
        cur = cur.left


def _kth_largest_brute(inp):
    ls = lines(inp)
    return str(_sorted_vals(inp)[-int(ls[1])])


def _validate(inp):
    def ok(n, lo, hi):
        if n is None:
            return True
        if (lo is not None and n.val <= lo) or (hi is not None and n.val >= hi):
            return False
        return ok(n.left, lo, n.val) and ok(n.right, n.val, hi)

    return boolstr(ok(parse_tree(lines(inp)[0]), None, None))


def _validate_brute(inp):
    v = inorder_vals(parse_tree(lines(inp)[0]))
    return boolstr(all(a < b for a, b in zip(v, v[1:])))


def _lca_bst(inp):
    ls = lines(inp)
    cur = parse_tree(ls[0])
    a, b = ints(ls[1])
    while True:
        if a < cur.val and b < cur.val:
            cur = cur.left
        elif a > cur.val and b > cur.val:
            cur = cur.right
        else:
            return str(cur.val)


def _lca_bst_brute(inp):
    ls = lines(inp)
    a, b = ints(ls[1])
    return str(lca_by_paths(paths_from_root(parse_tree(ls[0])), a, b)[0])


def _min_diff(inp):
    v = inorder_vals(parse_tree(lines(inp)[0]))
    return str(min(b - a for a, b in zip(v, v[1:])))


def _min_diff_brute(inp):
    vs = vals_of(lines(inp)[0])
    return str(min(abs(a - b) for i, a in enumerate(vs) for b in vs[i + 1 :]))


def _successor(inp):
    ls = lines(inp)
    cur, x = parse_tree(ls[0]), int(ls[1])
    best = -1
    while cur:
        if cur.val > x:
            best = cur.val
            cur = cur.left
        else:
            cur = cur.right
    return str(best)


def _successor_brute(inp):
    ls = lines(inp)
    x = int(ls[1])
    return str(min((v for v in vals_of(ls[0]) if v > x), default=-1))


def _delete(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = _delete(root.left, key)
    elif key > root.val:
        root.right = _delete(root.right, key)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        s = root.right
        while s.left:
            s = s.left
        root.val = s.val
        root.right = _delete(root.right, s.val)
    return root


def _delete_solve(inp):
    ls = lines(inp)
    return serialize_tree(_delete(parse_tree(ls[0]), int(ls[1])))


def _two_sum(inp):
    ls = lines(inp)
    v, t = inorder_vals(parse_tree(ls[0])), int(ls[1])
    i, j = 0, len(v) - 1
    while i < j:
        s = v[i] + v[j]
        if s == t:
            return "true"
        if s < t:
            i += 1
        else:
            j -= 1
    return "false"


def _two_sum_brute(inp):
    ls = lines(inp)
    vs, t = vals_of(ls[0]), int(ls[1])
    return boolstr(any(vs[i] + vs[j] == t for i in range(len(vs)) for j in range(i + 1, len(vs))))


def _from_preorder(inp):
    pre = ints(lines(inp)[0])
    i = 0

    def build(hi):
        nonlocal i
        if i == len(pre) or (hi is not None and pre[i] > hi):
            return None
        node = TreeNode(pre[i])
        i += 1
        node.left = build(node.val)
        node.right = build(hi)
        return node

    return serialize_tree(build(None))


def _from_preorder_brute(inp):
    root = None
    for v in ints(lines(inp)[0]):
        root = _insert_rec(root, v)
    return serialize_tree(root)


def _recover(inp):
    root = parse_tree(lines(inp)[0])
    first = second = prev = None
    st, cur = [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        if prev and prev.val > cur.val:
            if first is None:
                first = prev
            second = cur
        prev = cur
        cur = cur.right
    first.val, second.val = second.val, first.val
    return serialize_tree(root)


def _recover_brute(inp):
    root = parse_tree(lines(inp)[0])
    order = []

    def go(n):
        if n:
            go(n.left)
            order.append(n)
            go(n.right)

    go(root)
    for node, v in zip(order, sorted(n.val for n in order)):
        node.val = v
    return serialize_tree(root)


def _largest_bst(inp):
    best = 0

    def go(n):
        """-> (is_bst, size, min, max)"""
        nonlocal best
        if n is None:
            return True, 0, None, None
        lb, ls_, lmin, lmax = go(n.left)
        rb, rs, rmin, rmax = go(n.right)
        if lb and rb and (lmax is None or lmax < n.val) and (rmin is None or n.val < rmin):
            size = ls_ + rs + 1
            best = max(best, size)
            return True, size, lmin if lmin is not None else n.val, rmax if rmax is not None else n.val
        return False, 0, None, None

    go(parse_tree(lines(inp)[0]))
    return str(best)


def _largest_bst_brute(inp):
    root = parse_tree(lines(inp)[0])
    best = 0
    for n in all_nodes(root):
        v = inorder_vals(n)
        if all(a < b for a, b in zip(v, v[1:])):
            best = max(best, len(v))
    return str(best)


# ── tests ────────────────────────────────────────────────────────

def _t_search(r):
    out = ["null\n5", "7\n7", "7\n3"]
    for line in bst_shapes(r, empty=False):
        vs = vals_of(line)
        out.append(f"{line}\n{r.choice(vs)}")
    out.append(f"{line}\n1000")
    return out


def _t_insert(r):
    out = ["null\n5", "7\n3", "7\n9"]
    for line in bst_shapes(r, empty=False):
        vs = set(vals_of(line))
        out.append(f"{line}\n{r.choice([v for v in range(1, 1000) if v not in vs])}")
    return out


def _t_present_value(r, empty=False):
    out = []
    for line in bst_shapes(r, empty=False):
        out.append(f"{line}\n{r.choice(vals_of(line))}")
    return out


def _t_floor_ceil(r):
    out = ["8 4 12 2 6 10 14\n0", "8 4 12 2 6 10 14\n15", "8 4 12 2 6 10 14\n9", "8 4 12 2 6 10 14\n8", "null\n3"]
    for line in bst_shapes(r, empty=False):
        out.append(f"{line}\n{r.randint(0, 1000)}")
    return out


def _t_kth(r):
    out = ["5\n1"]
    for line in bst_shapes(r, empty=False):
        n = len(vals_of(line))
        out.append(f"{line}\n{r.randint(1, n)}")
    line = bst_line(r, 30)
    out += [f"{line}\n1", f"{line}\n30"]
    return out


def _t_validate(r):
    out = ["null", "1", "2 1 3", "5 1 7 null null 4 8", "5 1 7 null null 6 8", "2 2 2", "10 5 15 null null 6 20", "3 1 5 0 4"]
    for n in (5, 12, 30, 200):
        root = bst(r, n)
        out.append(serialize_tree(root))
        nodes = all_nodes(root)
        a, b = r.sample(nodes, 2)
        a.val, b.val = b.val, a.val
        out.append(serialize_tree(root))
    for n in (4, 9, 20):
        out.append(serialize_tree(random_tree(r, n, 1, 99)))
    return out


def _t_lca(r):
    out = ["6 2 8 0 4 7 9 null null 3 5\n2 8", "6 2 8 0 4 7 9 null null 3 5\n3 5"]
    for line in bst_shapes(r, empty=False)[2:]:
        a, b = r.sample(vals_of(line), 2)
        out.append(f"{line}\n{a} {b}")
    line = bst_line(r, 50)
    paths = paths_from_root(parse_tree(line))
    deep = max(paths, key=lambda v: len(paths[v]))
    out.append(f"{line}\n{paths[deep][1]} {deep}")
    return out


def _t_min_diff(r):
    out = ["1 null 3", "4 2 6 1 3"]
    for line in bst_shapes(r, empty=False)[2:]:
        out.append(line)
    out.append(bst_line(r, 60, 1, 10_000))
    return out


def _t_successor(r):
    out = []
    for line in bst_shapes(r, empty=False):
        vs = vals_of(line)
        out.append(f"{line}\n{r.choice(vs)}")
        out.append(f"{line}\n{max(vs)}")
    return out[:16]


def _t_delete(r):
    out = ["null\n5", "5\n5", "5\n3", "5 3 6 2 4 null 7\n3", "5 3 6 2 4 null 7\n5", "5 3 6 2 4 null 7\n7", "5 3 6 2 4 null 7\n6", "5 3 6 2 4 null 7\n0"]
    for line in bst_shapes(r, empty=False, big=False)[2:]:
        out.append(f"{line}\n{r.choice(vals_of(line))}")
    line = bst_line(r, 300)
    out.append(f"{line}\n{vals_of(line)[0]}")
    return out


def _t_two_sum(r):
    out = ["5\n10", "2 1 3\n4", "2 1 3\n6", "5 3 6 2 4 null 7\n9", "5 3 6 2 4 null 7\n28"]
    for line in bst_shapes(r, empty=False)[2:]:
        a, b = r.sample(vals_of(line), 2)
        out.append(f"{line}\n{a + b}")
        out.append(f"{line}\n{r.randint(2, 2000)}")
    return out[:18]


def _preorder_line(root):
    return join(n.val for n in all_nodes(root))


def _t_from_preorder(r):
    out = ["5", "3 1 2", "1 2 3 4 5", "5 4 3 2 1", "8 5 1 7 10 12"]
    for n in (6, 12, 25, 60, 300):
        out.append(_preorder_line(bst(r, n)))
    return out


def _t_recover(r):
    out = ["1 3 null null 2", "3 1 4 null null 2", "2 3 1", "5 3 8 2 4 7 9 10 null null null null null null 1"]
    for n in (3, 6, 15, 40, 300):
        root = bst(r, n)
        a, b = r.sample(all_nodes(root), 2)
        a.val, b.val = b.val, a.val
        out.append(serialize_tree(root))
    root = bst(r, 20)  # swap two neighbours in sorted order
    nodes = sorted(all_nodes(root), key=lambda x: x.val)
    k = r.randrange(len(nodes) - 1)
    nodes[k].val, nodes[k + 1].val = nodes[k + 1].val, nodes[k].val
    out.append(serialize_tree(root))
    return out


def _with_bst_subtree(r, n, sub):
    """Random binary tree whose values are scrambled, except one subtree reshaped into a valid BST."""
    root = random_tree(r, n, 1, 999)
    candidates = [x for x in all_nodes(root) if len(inorder_vals(x)) >= sub]
    target = min(candidates, key=lambda x: len(inorder_vals(x))) if candidates else root
    order = []

    def go(x):
        if x:
            go(x.left)
            order.append(x)
            go(x.right)

    go(target)
    for node, v in zip(order, sorted(x.val for x in order)):
        node.val = v
    return serialize_tree(root)


def _t_largest_bst(r):
    out = ["null", "4", "10 5 15 1 8 null 7", "5 2 4 1 3", "2 1 3", "3 2 4 1 null null 5"]
    for n, sub in ((8, 3), (15, 6), (30, 10), (60, 25), (300, 80)):
        out.append(_with_bst_subtree(r, n, sub))
    out.append(serialize_tree(random_tree(r, 12, 1, 50)))
    return out


PROBLEMS = [
    Problem(
        title="Search in a BST",
        difficulty="EASY",
        topics=["Tree", "BST"],
        description=f"""Find the node with value `x` in a binary search tree and print the subtree rooted at it. At each node, go left if `x` is smaller and right if it's larger, so you only walk one path from the root.

**Input:** line 1 is {BST_INPUT}. Line 2 is `x`.

**Output:** the subtree rooted at `x` as space-separated level-order values with `null` for missing children (trailing `null`s omitted), or `null` if `x` isn't in the tree.""",
        constraints=["0 <= number of nodes <= 1000", "1 <= node value, x <= 1000"],
        solve=_search,
        brute=_search_brute,
        examples=[("4 2 7 1 3\n2", "2 is the left child of 4; its subtree is 2 with children 1 and 3."), ("4 2 7 1 3\n5", "5 would be left of 7, but that spot is empty.")],
        tests=_t_search,
    ),
    Problem(
        title="Insert into a BST",
        difficulty="EASY",
        topics=["Tree", "BST"],
        description=f"""Insert the value `v` into a binary search tree as a new **leaf**: start at the root, go left if `v` is smaller than the current node and right if it's larger, and attach `v` at the first empty spot. `v` is not already in the tree.

**Input:** line 1 is {BST_INPUT}. Line 2 is `v`.

**Output:** {TREE_OUT}.""",
        constraints=["0 <= number of nodes <= 1000", "1 <= node value, v <= 1000"],
        solve=_insert_solve,
        brute=_insert_brute,
        examples=[("4 2 7 1 3\n5", "5 > 4 → go right to 7; 5 < 7 → becomes 7's left child."), ("null\n8", "Inserting into an empty tree makes 8 the root.")],
        tests=_t_insert,
    ),
    Problem(
        title="Floor and Ceil in a BST",
        difficulty="MEDIUM",
        topics=["Tree", "BST"],
        description=f"""For a value `x`, the **floor** is the largest value in the tree that is ≤ `x`, and the **ceil** is the smallest value that is ≥ `x`. Print both, using `-1` when one doesn't exist. Use the BST ordering to find them in one walk from the root.

**Input:** line 1 is {BST_INPUT}. Line 2 is `x`.

**Output:** `floor ceil` on one line.""",
        constraints=["0 <= number of nodes <= 1000", "1 <= node value <= 1000", "0 <= x <= 1000"],
        solve=_floor_ceil,
        brute=_floor_ceil_brute,
        examples=[("8 4 12 2 6 10 14\n11", "10 is the largest value ≤ 11, 12 the smallest ≥ 11."), ("8 4 12 2 6 10 14\n1", "Nothing is ≤ 1; the ceil is 2.")],
        tests=_t_floor_ceil,
    ),
    Problem(
        title="Kth Smallest in a BST",
        difficulty="MEDIUM",
        topics=["Tree", "BST", "DFS", "Stack"],
        description=f"""Print the `k`-th smallest value in a binary search tree (1-indexed). An inorder traversal visits a BST's values in increasing order, so you can stop after `k` visits.

**Input:** line 1 is {BST_INPUT}. Line 2 is `k`.

**Output:** the `k`-th smallest value.""",
        constraints=["1 <= k <= number of nodes <= 1000"],
        solve=_kth_smallest,
        brute=_kth_smallest_brute,
        examples=[("3 1 4 null 2\n1", "Sorted values are 1 2 3 4; the first is 1."), ("5 3 6 2 4 null null 1\n3", "Sorted: 1 2 3 4 5 6; the third is 3.")],
        tests=_t_kth,
    ),
    Problem(
        title="Kth Largest in a BST",
        difficulty="MEDIUM",
        topics=["Tree", "BST", "DFS", "Stack"],
        description=f"""Print the `k`-th largest value in a binary search tree (1-indexed). A **reverse** inorder traversal (right subtree, node, left subtree) visits values from largest to smallest.

**Input:** line 1 is {BST_INPUT}. Line 2 is `k`.

**Output:** the `k`-th largest value.""",
        constraints=["1 <= k <= number of nodes <= 1000"],
        solve=_kth_largest,
        brute=_kth_largest_brute,
        examples=[("5 3 6 2 4 null null 1\n2", "From the top: 6, then 5."), ("8\n1", "The only value is the largest.")],
        tests=_t_kth,
    ),
    Problem(
        title="Validate BST",
        difficulty="MEDIUM",
        topics=["Tree", "BST", "DFS"],
        description="""Decide whether a binary tree is a valid binary search tree: for **every** node, all values in its left subtree are strictly smaller and all values in its right subtree strictly larger. Equal values are not allowed. An empty tree is valid.

Checking only each node against its direct children isn't enough: a value deep in a right subtree must still be larger than every ancestor it sits to the right of. Pass down the allowed (low, high) range instead.

**Input:** a binary tree as space-separated level-order values, with `null` for a missing child (an empty tree is just `null`).

**Output:** `true` or `false`.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_validate,
        brute=_validate_brute,
        examples=[("2 1 3", "1 < 2 < 3."), ("5 1 7 null null 4 8", "4 is in 5's right subtree but smaller than 5.")],
        tests=_t_validate,
    ),
    Problem(
        title="LCA in a BST",
        difficulty="EASY",
        topics=["Tree", "BST"],
        description=f"""Find the lowest common ancestor of the nodes with values `a` and `b`: the deepest node that has both in its subtree (a node is in its own subtree). Both values are in the tree.

In a BST you don't need to search both sides: while both values are smaller than the current node go left, while both are larger go right; the first node where they split (or that equals one of them) is the answer.

**Input:** line 1 is {BST_INPUT}. Line 2 has `a` and `b`.

**Output:** the value of their lowest common ancestor.""",
        constraints=["2 <= number of nodes <= 1000", "a != b"],
        solve=_lca_bst,
        brute=_lca_bst_brute,
        examples=[("6 2 8 0 4 7 9 null null 3 5\n2 8", "2 is left of 6 and 8 right of it."), ("6 2 8 0 4 7 9 null null 3 5\n2 4", "4 is inside 2's subtree.")],
        tests=_t_lca,
    ),
    Problem(
        title="Minimum Difference in a BST",
        difficulty="EASY",
        topics=["Tree", "BST", "DFS"],
        description=f"""Print the smallest difference between the values of any two different nodes. The closest pair of values is always adjacent in sorted order, so compare neighbours in an inorder traversal.

**Input:** {BST_INPUT}. The tree has at least two nodes.

**Output:** the minimum difference.""",
        constraints=["2 <= number of nodes <= 1000"],
        solve=_min_diff,
        brute=_min_diff_brute,
        examples=[("4 2 6 1 3", "Sorted 1 2 3 4 6: neighbours differ by 1."), ("1 null 48 12 49", "48 and 49 differ by 1.")],
        tests=_t_min_diff,
    ),
    Problem(
        title="Inorder Successor in a BST",
        difficulty="MEDIUM",
        topics=["Tree", "BST"],
        description=f"""The **inorder successor** of `x` is the next larger value in the tree. Print it, or `-1` if `x` is the largest. Walk down from the root: whenever the current node is larger than `x`, it's a candidate and you go left; otherwise go right.

**Input:** line 1 is {BST_INPUT}. Line 2 is `x`, a value in the tree.

**Output:** the successor's value, or `-1`.""",
        constraints=["1 <= number of nodes <= 1000"],
        solve=_successor,
        brute=_successor_brute,
        examples=[("20 8 22 4 12 null null null null 10 14\n8", "The next value after 8 is 10."), ("20 8 22 4 12 null null null null 10 14\n22", "22 is the largest value.")],
        tests=_t_successor,
    ),
    Problem(
        title="Delete Node in a BST",
        difficulty="MEDIUM",
        topics=["Tree", "BST", "Recursion"],
        description=f"""Delete the node with value `key` from a binary search tree and print the resulting tree. Use exactly these rules so the result is unique:

- If `key` isn't in the tree, the tree doesn't change.
- If the node has **no children**, remove it.
- If it has **one child**, that child takes the node's place.
- If it has **two children**, copy the smallest value of its right subtree (its inorder successor) into the node, then delete that successor from the right subtree using these same rules.

**Input:** line 1 is {BST_INPUT}. Line 2 is `key`.

**Output:** {TREE_OUT}.""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_delete_solve,
        examples=[("5 3 6 2 4 null 7\n3", "3 has two children; its successor 4 replaces it."), ("5 3 6 2 4 null 7\n6", "6 has one child, so 7 moves up.")],
        tests=_t_delete,
    ),
    Problem(
        title="Two Sum in a BST",
        difficulty="MEDIUM",
        topics=["Tree", "BST", "Two Pointers"],
        description=f"""Are there two **different** nodes whose values add up to `target`? Print `true` or `false`.

The inorder traversal is sorted, so two pointers from both ends find the pair in O(n).

**Input:** line 1 is {BST_INPUT}. Line 2 is `target`.

**Output:** `true` or `false`.""",
        constraints=["1 <= number of nodes <= 1000", "2 <= target <= 2000"],
        solve=_two_sum,
        brute=_two_sum_brute,
        examples=[("5 3 6 2 4 null 7\n9", "2 + 7 = 9 (also 3 + 6, 4 + 5)."), ("5 3 6 2 4 null 7\n28", "The two largest, 6 + 7, only reach 13.")],
        tests=_t_two_sum,
    ),
    Problem(
        title="Construct BST from Preorder",
        difficulty="MEDIUM",
        topics=["Tree", "BST", "Recursion"],
        description="""Rebuild a binary search tree from its preorder traversal (node, left subtree, right subtree). Values are distinct, so the tree is unique.

Inserting values one by one works in O(n²) for skewed trees. For O(n), build recursively with an upper bound: a value belongs to the current subtree only while it is below the bound.

**Input:** one line with the preorder values, space-separated.

**Output:** the tree as space-separated level-order values with `null` for missing children (trailing `null`s omitted).""",
        constraints=["1 <= number of nodes <= 1000", "values are distinct"],
        solve=_from_preorder,
        brute=_from_preorder_brute,
        examples=[("8 5 1 7 10 12", "8 is the root; 5 1 7 form its left subtree, 10 12 its right."), ("1 2 3", "Each value is larger than the last: a right chain.")],
        tests=_t_from_preorder,
    ),
    Problem(
        title="Recover a BST",
        difficulty="HARD",
        topics=["Tree", "BST", "DFS"],
        description="""A binary search tree had the values of exactly **two** nodes swapped by mistake. Fix it without changing the tree's shape, and print the repaired tree.

In an inorder traversal of the broken tree, the sorted order is violated in one or two places; the swapped nodes are the first node of the first violation and the second node of the last one.

**Input:** the broken tree as space-separated level-order values, with `null` for a missing child. Values are distinct.

**Output:** the repaired tree in the same level-order format (trailing `null`s omitted).""",
        constraints=["2 <= number of nodes <= 1000"],
        solve=_recover,
        brute=_recover_brute,
        examples=[("1 3 null null 2", "1 and 3 were swapped: the root should be 3 with 1 below it."), ("3 1 4 null null 2", "2 and 3 were swapped.")],
        tests=_t_recover,
    ),
    Problem(
        title="Largest BST Subtree",
        difficulty="HARD",
        topics=["Tree", "BST", "DFS", "Recursion"],
        description="""Given a binary tree (not necessarily a BST), find the largest **subtree** that is a valid binary search tree and print its number of nodes. A subtree is a node together with **all** of its descendants. Valid means every node's left subtree holds strictly smaller values and its right subtree strictly larger ones.

Solve it in one post-order pass: each node reports whether its subtree is a BST, along with its size and its minimum and maximum values.

**Input:** a binary tree as space-separated level-order values, with `null` for a missing child (an empty tree is just `null`).

**Output:** the size of the largest BST subtree (0 for an empty tree).""",
        constraints=["0 <= number of nodes <= 1000"],
        solve=_largest_bst,
        brute=_largest_bst_brute,
        examples=[("10 5 15 1 8 null 7", "The subtree at 5 (5, 1, 8) is a BST; 15 → 7 isn't."), ("2 1 3", "The whole tree is a BST.")],
        tests=_t_largest_bst,
    ),
]
