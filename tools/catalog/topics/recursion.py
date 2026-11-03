"""Recursion & Backtracking."""
from itertools import combinations, permutations, product

from lib import Playlist, Problem, ints, join, lines, rand_ints, rand_str

PLAYLISTS = [
    Playlist(
        key="recursion",
        title="07 · Recursion & Backtracking",
        description="Think in smaller subproblems, then explore choices and undo them: subsets, combinations, permutations and puzzles.",
        accent="#F4B6C2",
        titles=[
            "Print 1 to N",
            "Factorial",
            "Sum of Digits",
            "Reverse String Using Recursion",
            "Fibonacci",
            "Power of a Number (mod)",
            "Binary Strings Without Consecutive Ones",
            "Generate Parentheses",
            "Subsets (Power Set)",
            "Subset Sums",
            "Subsets With Duplicates",
            "Combination Sum",
            "Combination Sum II",
            "Combination Sum III",
            "Permutations",
            "Letter Combinations of a Phone Number",
            "Palindrome Partitioning",
            "Word Search",
            "Rat in a Maze",
            "N-Queens",
            "Graph M-Coloring",
            "Sudoku Solver",
        ],
    )
]


# ── Binary strings without consecutive ones ─────────────────────

def _binstr(inp):
    n = int(lines(inp)[0])
    out = []

    def go(s):
        if len(s) == n:
            out.append(s)
            return
        go(s + "0")
        if not s.endswith("1"):
            go(s + "1")

    go("")
    return "\n".join(out)


def _binstr_brute(inp):
    n = int(lines(inp)[0])
    return "\n".join(s for s in ("".join(p) for p in product("01", repeat=n)) if "11" not in s)


# ── Generate parentheses ────────────────────────────────────────

def _parens(inp):
    n = int(lines(inp)[0])
    out = []

    def go(s, o, c):
        if len(s) == 2 * n:
            out.append(s)
            return
        if o < n:
            go(s + "(", o + 1, c)
        if c < o:
            go(s + ")", o, c + 1)

    go("", 0, 0)
    return "\n".join(out)


def _parens_brute(inp):
    n = int(lines(inp)[0])

    def ok(s):
        d = 0
        for ch in s:
            d += 1 if ch == "(" else -1
            if d < 0:
                return False
        return d == 0

    return "\n".join(s for s in ("".join(p) for p in product("()", repeat=2 * n)) if ok(s))


# ── Subsets ─────────────────────────────────────────────────────

def _fmt_sets(sets):
    return "\n".join("[" + " ".join(map(str, s)) + "]" for s in sets)


def _subsets(inp):
    nums = sorted(ints(lines(inp)[0]))
    out = []

    def go(i, cur):
        if i == len(nums):
            out.append(list(cur))
            return
        cur.append(nums[i])
        go(i + 1, cur)
        cur.pop()
        go(i + 1, cur)

    go(0, [])
    return _fmt_sets(sorted(out))


def _subsets_brute(inp):
    nums = sorted(ints(lines(inp)[0]))
    res = []
    for mask in range(1 << len(nums)):
        res.append([nums[i] for i in range(len(nums)) if mask >> i & 1])
    return _fmt_sets(sorted(res))


def _subset_sums(inp):
    nums = ints(lines(inp)[0])
    sums = []

    def go(i, s):
        if i == len(nums):
            sums.append(s)
            return
        go(i + 1, s + nums[i])
        go(i + 1, s)

    go(0, 0)
    return join(sorted(sums))


def _subset_sums_brute(inp):
    nums = ints(lines(inp)[0])
    return join(sorted(sum(c) for k in range(len(nums) + 1) for c in combinations(nums, k)))


def _subsets_dup(inp):
    nums = sorted(ints(lines(inp)[0]))
    out = []

    def go(start, cur):
        out.append(list(cur))
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            cur.append(nums[i])
            go(i + 1, cur)
            cur.pop()

    go(0, [])
    return _fmt_sets(sorted(out))


def _subsets_dup_brute(inp):
    nums = sorted(ints(lines(inp)[0]))
    res = {tuple(c) for k in range(len(nums) + 1) for c in combinations(nums, k)}
    return _fmt_sets(sorted(list(x) for x in res))


# ── Combination sums ────────────────────────────────────────────

def _comb_out(res):
    return _fmt_sets(sorted(res)) if res else "none"


def _comb1(inp):
    ls = lines(inp)
    cands, target = sorted(set(ints(ls[0]))), int(ls[1])
    res = []

    def go(i, rem, cur):
        if rem == 0:
            res.append(list(cur))
            return
        for j in range(i, len(cands)):
            if cands[j] > rem:
                break
            cur.append(cands[j])
            go(j, rem - cands[j], cur)
            cur.pop()

    go(0, target, [])
    return _comb_out(res)


def _comb1_brute(inp):
    ls = lines(inp)
    cands, target = sorted(set(ints(ls[0]))), int(ls[1])
    res = set()

    def go(cur, s):
        if s == target:
            res.add(tuple(sorted(cur)))
            return
        if s > target:
            return
        for c in cands:
            go(cur + [c], s + c)

    go([], 0)
    return _comb_out([list(x) for x in res])


def _comb2(inp):
    ls = lines(inp)
    cands, target = sorted(ints(ls[0])), int(ls[1])
    res = []

    def go(start, rem, cur):
        if rem == 0:
            res.append(list(cur))
            return
        for i in range(start, len(cands)):
            if i > start and cands[i] == cands[i - 1]:
                continue
            if cands[i] > rem:
                break
            cur.append(cands[i])
            go(i + 1, rem - cands[i], cur)
            cur.pop()

    go(0, target, [])
    return _comb_out(res)


def _comb2_brute(inp):
    ls = lines(inp)
    cands, target = sorted(ints(ls[0])), int(ls[1])
    res = {c for k in range(1, len(cands) + 1) for c in combinations(cands, k) if sum(c) == target}
    return _comb_out([list(x) for x in res])


def _comb3(inp):
    k, n = map(int, lines(inp)[0].split())
    res = []

    def go(start, rem, cur):
        if len(cur) == k:
            if rem == 0:
                res.append(list(cur))
            return
        for d in range(start, 10):
            if d > rem:
                break
            cur.append(d)
            go(d + 1, rem - d, cur)
            cur.pop()

    go(1, n, [])
    return _comb_out(res)


def _comb3_brute(inp):
    k, n = map(int, lines(inp)[0].split())
    return _comb_out([list(c) for c in combinations(range(1, 10), k) if sum(c) == n])


# ── Permutations ────────────────────────────────────────────────

def _perms(inp):
    nums = sorted(ints(lines(inp)[0]))
    out, used = [], [False] * len(nums)

    def go(cur):
        if len(cur) == len(nums):
            out.append(list(cur))
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            cur.append(nums[i])
            go(cur)
            cur.pop()
            used[i] = False

    go([])
    return "\n".join(join(p) for p in out)


def _perms_brute(inp):
    nums = sorted(ints(lines(inp)[0]))
    return "\n".join(join(p) for p in sorted(permutations(nums)))


# ── Phone letters ───────────────────────────────────────────────

PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def _phone(inp):
    digits = lines(inp)[0]
    out = []

    def go(i, s):
        if i == len(digits):
            out.append(s)
            return
        for ch in PHONE[digits[i]]:
            go(i + 1, s + ch)

    go(0, "")
    return "\n".join(out)


def _phone_brute(inp):
    digits = lines(inp)[0]
    return "\n".join(sorted("".join(p) for p in product(*(PHONE[d] for d in digits))))


# ── Palindrome partitioning ─────────────────────────────────────

def _pal_part(inp):
    s = lines(inp)[0]
    out = []

    def go(i, cur):
        if i == len(s):
            out.append(" ".join(cur))
            return
        for j in range(i + 1, len(s) + 1):
            piece = s[i:j]
            if piece == piece[::-1]:
                cur.append(piece)
                go(j, cur)
                cur.pop()

    go(0, [])
    return "\n".join(sorted(out))


def _pal_part_brute(inp):
    s = lines(inp)[0]
    n = len(s)
    res = []
    for mask in range(1 << (n - 1)):
        parts, start = [], 0
        for i in range(n - 1):
            if mask >> i & 1:
                parts.append(s[start:i + 1])
                start = i + 1
        parts.append(s[start:])
        if all(p == p[::-1] for p in parts):
            res.append(" ".join(parts))
    return "\n".join(sorted(res))


# ── Word search ─────────────────────────────────────────────────

def _parse_grid(ls):
    r, c = map(int, ls[0].split())
    return [list(ls[1 + i]) for i in range(r)], ls[1 + r]


def _word_search(inp):
    grid, word = _parse_grid(lines(inp))
    R, C = len(grid), len(grid[0])

    def dfs(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] != word[k]:
            return False
        ch, grid[r][c] = grid[r][c], "#"
        found = any(dfs(r + dr, c + dc, k + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        grid[r][c] = ch
        return found

    return "true" if any(dfs(r, c, 0) for r in range(R) for c in range(C)) else "false"


def _word_search_brute(inp):
    grid, word = _parse_grid(lines(inp))
    R, C = len(grid), len(grid[0])

    def paths(path):
        if len(path) == len(word):
            return True
        r, c = path[-1]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in path and grid[nr][nc] == word[len(path)]:
                if paths(path + [(nr, nc)]):
                    return True
        return False

    for r in range(R):
        for c in range(C):
            if grid[r][c] == word[0] and paths([(r, c)]):
                return "true"
    return "false"


def _word_tests(r):
    out = ["1 1\na\na", "1 1\na\nb", "2 2\nab\ncd\nabdc", "2 2\nab\ncd\nabcd", "3 3\naaa\naaa\naaa\naaaaaaaaa", "3 3\naaa\naaa\naaa\naaaaaaaaaa"]
    for _ in range(4):
        R, C = r.randint(2, 5), r.randint(2, 5)
        g = [rand_str(r, C, "abc") for _ in range(R)]
        if r.random() < 0.5:
            # a word that exists: random walk
            rr, cc = r.randrange(R), r.randrange(C)
            seen, w = {(rr, cc)}, g[rr][cc]
            for _ in range(r.randint(1, 6)):
                nxt = [(rr + a, cc + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= rr + a < R and 0 <= cc + b < C and (rr + a, cc + b) not in seen]
                if not nxt:
                    break
                rr, cc = r.choice(nxt)
                seen.add((rr, cc))
                w += g[rr][cc]
        else:
            w = rand_str(r, r.randint(3, 7), "abc")
        out.append(f"{R} {C}\n" + "\n".join(g) + "\n" + w)
    return out


# ── Rat in a maze ───────────────────────────────────────────────

MOVES = (("D", 1, 0), ("L", 0, -1), ("R", 0, 1), ("U", -1, 0))


def _rat(inp):
    ls = lines(inp)
    n = int(ls[0])
    g = [ints(ls[1 + i]) for i in range(n)]
    out = []
    seen = [[False] * n for _ in range(n)]

    def go(r, c, path):
        if r == n - 1 and c == n - 1:
            out.append(path)
            return
        for d, dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and g[nr][nc] == 1 and not seen[nr][nc]:
                seen[nr][nc] = True
                go(nr, nc, path + d)
                seen[nr][nc] = False

    if g[0][0] == 1:
        seen[0][0] = True
        go(0, 0, "")
    return "\n".join(sorted(out)) if out else "-1"


def _rat_tests(r):
    out = ["2\n0 1\n1 1", "2\n1 1\n1 0", "2\n1 1\n0 1", "2\n1 0\n0 1", "3\n1 1 1\n1 1 1\n1 1 1", "4\n1 0 0 0\n1 1 0 1\n1 1 0 0\n0 1 1 1"]
    for n in (3, 4, 4, 5):
        g = [[1 if r.random() < 0.75 else 0 for _ in range(n)] for _ in range(n)]
        g[0][0] = g[n - 1][n - 1] = 1
        out.append(f"{n}\n" + "\n".join(join(row) for row in g))
    return out


# ── N-Queens ────────────────────────────────────────────────────

def _queens(inp):
    n = int(lines(inp)[0])
    sols = []
    cols, d1, d2, place = set(), set(), set(), []

    def go(r):
        if r == n:
            sols.append(list(place))
            return
        for c in range(n):
            if c in cols or r - c in d1 or r + c in d2:
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c); place.append(c)
            go(r + 1)
            cols.discard(c); d1.discard(r - c); d2.discard(r + c); place.pop()

    go(0)
    if not sols:
        return "0"
    first = sols[0]
    board = ["".join("Q" if first[r] == c else "." for c in range(n)) for r in range(n)]
    return "\n".join([str(len(sols))] + board)


def _queens_brute(inp):
    n = int(lines(inp)[0])
    sols = [p for p in permutations(range(n)) if all(abs(p[i] - p[j]) != j - i for i in range(n) for j in range(i + 1, n))]
    if not sols:
        return "0"
    first = sols[0]
    return "\n".join([str(len(sols))] + ["".join("Q" if first[r] == c else "." for c in range(n)) for r in range(n)])


# ── M-coloring ──────────────────────────────────────────────────

def _parse_graph(ls):
    n, m, k = map(int, ls[0].split())
    edges = [tuple(map(int, ls[1 + i].split())) for i in range(m)]
    return n, edges, k


def _mcolor(inp):
    n, edges, k = _parse_graph(lines(inp))
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [0] * n

    def go(v):
        if v == n:
            return True
        for c in range(1, k + 1):
            if all(color[u] != c for u in adj[v]):
                color[v] = c
                if go(v + 1):
                    return True
                color[v] = 0
        return False

    return "true" if go(0) else "false"


def _mcolor_brute(inp):
    n, edges, k = _parse_graph(lines(inp))
    for cols in product(range(k), repeat=n):
        if all(cols[u] != cols[v] for u, v in edges):
            return "true"
    return "false"


def _mcolor_tests(r):
    out = ["1 0 1", "2 1 1\n0 1", "2 1 2\n0 1", "3 3 2\n0 1\n1 2\n0 2", "4 6 3\n0 1\n0 2\n0 3\n1 2\n1 3\n2 3", "4 6 4\n0 1\n0 2\n0 3\n1 2\n1 3\n2 3"]
    for _ in range(5):
        n = r.randint(3, 7)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        es = r.sample(pairs, r.randint(1, len(pairs)))
        k = r.randint(2, 4)
        out.append(f"{n} {len(es)} {k}\n" + "\n".join(f"{u} {v}" for u, v in es))
    return out


# ── Sudoku ──────────────────────────────────────────────────────

def _sudoku(inp):
    g = [list(map(int, row)) for row in lines(inp)[:9]]
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty = []
    for r in range(9):
        for c in range(9):
            v = g[r][c]
            if v:
                rows[r].add(v); cols[c].add(v); boxes[r // 3 * 3 + c // 3].add(v)
            else:
                empty.append((r, c))

    def go(i):
        if i == len(empty):
            return True
        r, c = empty[i]
        b = r // 3 * 3 + c // 3
        for v in range(1, 10):
            if v in rows[r] or v in cols[c] or v in boxes[b]:
                continue
            g[r][c] = v
            rows[r].add(v); cols[c].add(v); boxes[b].add(v)
            if go(i + 1):
                return True
            rows[r].discard(v); cols[c].discard(v); boxes[b].discard(v)
        g[r][c] = 0
        return False

    go(0)
    return "\n".join("".join(map(str, row)) for row in g)


_SOLVED = [
    "534678912", "672195348", "198342567", "859761423", "426853791",
    "713924856", "961537284", "287419635", "345286179",
]


def _sudoku_tests(r):
    from random import Random

    def puzzle(seed, holes):
        rr = Random(seed)
        # Relabel digits and shuffle rows within bands to vary the base grid.
        perm = list(range(1, 10))
        rr.shuffle(perm)
        g = [[perm[int(ch) - 1] for ch in row] for row in _SOLVED]
        bands = []
        for b in range(3):
            rows = g[b * 3:(b + 1) * 3]
            rr.shuffle(rows)
            bands.append(rows)
        g = [row for band in bands for row in band]
        cells = [(i, j) for i in range(9) for j in range(9)]
        rr.shuffle(cells)
        for i, j in cells[:holes]:
            g[i][j] = 0
        return "\n".join("".join(map(str, row)) for row in g)

    out = []
    for k, holes in enumerate((1, 10, 20, 30, 35, 40, 45)):
        p = puzzle(r.randint(0, 10**9) + k, holes)
        if _unique_sudoku(p):
            out.append(p)
    return out


def _unique_sudoku(p):
    g = [list(map(int, row)) for row in p.split("\n")]
    count = 0

    def ok(r, c, v):
        if v in g[r] or any(g[i][c] == v for i in range(9)):
            return False
        br, bc = r // 3 * 3, c // 3 * 3
        return all(g[br + i][bc + j] != v for i in range(3) for j in range(3))

    def go():
        nonlocal count
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    for v in range(1, 10):
                        if ok(r, c, v):
                            g[r][c] = v
                            go()
                            g[r][c] = 0
                            if count > 1:
                                return
                    return
        count += 1

    go()
    return count == 1


_SAMPLE_SUDOKU = "530070000\n600195000\n098000060\n800060003\n400803001\n700020006\n060000280\n000419005\n000080079"


PROBLEMS = [
    Problem(
        title="Binary Strings Without Consecutive Ones",
        difficulty="EASY",
        topics=["Recursion", "Backtracking", "String"],
        description="""Print every binary string of length `n` that never has two `1`s next to each other.

Build the string one character at a time: you can always append `0`, but you may append `1` only when the last character isn't `1`.

**Input:** one integer `n`.

**Output:** the valid strings, one per line, in lexicographic (dictionary) order.""",
        constraints=["1 <= n <= 12"],
        solve=_binstr,
        brute=_binstr_brute,
        examples=[("3", "Of the 8 strings of length 3, five avoid \"11\"."), ("1", "Both single characters are fine.")],
        tests=lambda r: ["2", "4", "5", "7", "8", "10", "12"],
    ),
    Problem(
        title="Generate Parentheses",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "String"],
        description="""Print every string of `n` pairs of parentheses that is correctly balanced.

Add `(` while you still have opening brackets left, and add `)` only when it closes an open one — that way every string you build stays valid.

**Input:** one integer `n`.

**Output:** all balanced strings, one per line, in lexicographic order (`(` comes before `)`).""",
        constraints=["1 <= n <= 7"],
        solve=_parens,
        brute=_parens_brute,
        examples=[("3", "There are 5 balanced strings with 3 pairs."), ("1", "Only one.")],
        tests=lambda r: ["2", "4", "5", "6", "7"],
    ),
    Problem(
        title="Subsets (Power Set)",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "Bit Manipulation"],
        description="""Given an array of **distinct** integers, print every subset (the power set).

For each element you have two choices — take it or leave it — so there are `2^n` subsets.

**Input:** one line of space-separated distinct integers.

**Output:** one subset per line as `[a b c]` with its elements in increasing order (the empty subset is `[]`). Order the lines by comparing subsets element by element, where a shorter prefix comes first — e.g. `[]`, `[1]`, `[1 2]`, `[1 2 3]`, `[1 3]`, `[2]`, …""",
        constraints=["1 <= n <= 10", "-100 <= nums[i] <= 100"],
        solve=_subsets,
        brute=_subsets_brute,
        examples=[("1 2 3", "2³ = 8 subsets."), ("5", "The empty set and [5].")],
        tests=lambda r: ["0", "-1 1", "3 1 2", "10 -10 0 5", "1 2 3 4 5 6 7 8 9 10"]
        + [join(r.sample(range(-50, 50), r.randint(2, 7))) for _ in range(3)],
    ),
    Problem(
        title="Subset Sums",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking"],
        description="""For an array of `n` integers, compute the sum of every one of its `2^n` subsets (including the empty subset, whose sum is 0).

**Input:** one line of space-separated integers.

**Output:** all `2^n` sums, space-separated, in non-decreasing order. Equal sums from different subsets are all printed.""",
        constraints=["1 <= n <= 10", "0 <= nums[i] <= 1000"],
        solve=_subset_sums,
        brute=_subset_sums_brute,
        examples=[("2 3", "Subsets {}, {2}, {3}, {2,3} give 0, 2, 3, 5."), ("5 2 1", "Eight sums.")],
        tests=lambda r: ["0", "7", "1 1", "1 1 1", "1000 1000 1000 1000"]
        + [join(rand_ints(r, r.randint(3, 10), 0, 1000)) for _ in range(4)],
    ),
    Problem(
        title="Subsets With Duplicates",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking"],
        description="""The array may contain repeated values. Print every **distinct** subset — two subsets count as the same if they contain the same values the same number of times.

Sort first, then while choosing the next element at a given depth, skip a value equal to the one you just tried.

**Input:** one line of space-separated integers.

**Output:** one subset per line as `[a b c]` with elements in increasing order (`[]` for empty), lines ordered as in *Subsets (Power Set)*: compare element by element, shorter prefix first.""",
        constraints=["1 <= n <= 10", "-10 <= nums[i] <= 10"],
        solve=_subsets_dup,
        brute=_subsets_dup_brute,
        examples=[("1 2 2", "[2] and [1 2] appear once each even though there are two 2s."), ("0", "Two subsets.")],
        tests=lambda r: ["4 4 4 4", "1 2 3", "2 1 2 1", "-1 -1 0 0 1 1", "5 5 5 5 5 5 5 5 5 5"]
        + [join(rand_ints(r, r.randint(4, 10), -3, 3)) for _ in range(4)],
    ),
    Problem(
        title="Combination Sum",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "Array"],
        description="""Given a list of distinct positive candidate numbers and a `target`, print every combination of candidates that adds up to `target`. **Each candidate may be used any number of times.**

**Input:** line 1 — the candidates; line 2 — `target`.

**Output:** one combination per line as `[a b c]` with values in non-decreasing order, lines sorted by comparing element by element (shorter prefix first). Print `none` if there is no combination.""",
        constraints=["1 <= candidates.length <= 15", "2 <= candidates[i] <= 40", "1 <= target <= 40"],
        solve=_comb1,
        brute=None,
        examples=[("2 3 6 7\n7", "2+2+3 and 7."), ("2\n1", "1 can't be built from 2s.")],
        tests=lambda r: ["2 3 5\n8", "7 3 2\n18", "2\n40", "5 10\n3", "3 4 5 6 7 8 9\n20", "2 4 6 8\n9"]
        + [join(r.sample(range(2, 15), r.randint(2, 5))) + f"\n{r.randint(5, 25)}" for _ in range(3)],
    ),
    Problem(
        title="Combination Sum II",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "Array"],
        description="""Given candidate numbers (possibly with repeats) and a `target`, print every combination that sums to `target` where **each array element is used at most once**. Don't print the same combination twice.

**Input:** line 1 — the candidates; line 2 — `target`.

**Output:** one combination per line as `[a b c]` in non-decreasing order, lines sorted by comparing element by element (shorter prefix first). Print `none` if there is no combination.""",
        constraints=["1 <= candidates.length <= 20", "1 <= candidates[i] <= 50", "1 <= target <= 30"],
        solve=_comb2,
        brute=_comb2_brute,
        examples=[("10 1 2 7 6 1 5\n8", "The two 1s can be used together in [1 1 6]."), ("2 5 2 1 2\n5", "[1 2 2] and [5].")],
        tests=lambda r: ["1 1 1 1 1\n3", "3\n2", "1 2 3 4 5 6 7 8 9 10\n15", "4 4 4 4\n8", "50\n30"]
        + [join(rand_ints(r, r.randint(5, 12), 1, 10)) + f"\n{r.randint(5, 20)}" for _ in range(4)],
    ),
    Problem(
        title="Combination Sum III",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking"],
        description="""Find every set of exactly `k` **different** digits from 1 to 9 whose sum is `n`.

**Input:** one line with `k` and `n`.

**Output:** one combination per line as `[a b c]` in increasing order, lines sorted lexicographically by their numbers. Print `none` if no combination exists.""",
        constraints=["1 <= k <= 9", "1 <= n <= 60"],
        solve=_comb3,
        brute=_comb3_brute,
        examples=[("3 7", "Only 1 + 2 + 4."), ("4 1", "Four different digits sum to at least 10.")],
        tests=lambda r: ["1 5", "1 10", "2 10", "3 9", "9 45", "9 44", "4 20", "5 25", "3 15"],
    ),
    Problem(
        title="Permutations",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "Array"],
        description="""Print every ordering (permutation) of an array of **distinct** integers.

**Input:** one line of space-separated distinct integers.

**Output:** one permutation per line, values space-separated, lines in lexicographic order of the numbers.""",
        constraints=["1 <= n <= 6", "-10 <= nums[i] <= 10"],
        solve=_perms,
        brute=_perms_brute,
        examples=[("1 2 3", "3! = 6 orderings."), ("0 1", "Two orderings.")],
        tests=lambda r: ["5", "2 1", "-1 0 1", "4 3 2 1", "6 5 4 3 2 1"]
        + [join(r.sample(range(-10, 11), r.randint(3, 5))) for _ in range(3)],
    ),
    Problem(
        title="Letter Combinations of a Phone Number",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "String"],
        description="""On a phone keypad, 2 → `abc`, 3 → `def`, 4 → `ghi`, 5 → `jkl`, 6 → `mno`, 7 → `pqrs`, 8 → `tuv`, 9 → `wxyz`. Given a string of digits from 2 to 9, print every letter string it could spell.

**Input:** one line of digits (2–9).

**Output:** all possible strings, one per line, in lexicographic order.""",
        constraints=["1 <= digits.length <= 5"],
        solve=_phone,
        brute=_phone_brute,
        examples=[("23", "3 × 3 = 9 strings."), ("7", "p, q, r, s.")],
        tests=lambda r: ["2", "9", "79", "234", "2345", "99999"] + ["".join(r.choice("23456789") for _ in range(r.randint(2, 4))) for _ in range(3)],
    ),
    Problem(
        title="Palindrome Partitioning",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "String"],
        description="""Split a string into pieces so that **every piece is a palindrome**. Print all such splits.

**Input:** one lowercase string `s`.

**Output:** one split per line with its pieces separated by single spaces (pieces in their original order). Sort the lines as plain strings.""",
        constraints=["1 <= s.length <= 10"],
        solve=_pal_part,
        brute=_pal_part_brute,
        examples=[("aab", "\"a a b\" and \"aa b\"."), ("x", "A single character is a palindrome.")],
        tests=lambda r: ["aa", "abc", "aaaa", "racecar", "abacaba", "aaaaaaaaaa"] + [rand_str(r, r.randint(4, 10), "ab") for _ in range(4)],
    ),
    Problem(
        title="Word Search",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "Matrix"],
        description="""Given a grid of letters and a word, decide whether the word can be traced through the grid by moving between horizontally or vertically adjacent cells. A cell may be used at most once in the word.

**Input:** line 1 — rows `R` and columns `C`; next `R` lines — the grid rows (no spaces); last line — the word.

**Output:** `true` or `false`.""",
        constraints=["1 <= R, C <= 6", "1 <= word.length <= 12"],
        solve=_word_search,
        brute=_word_search_brute,
        examples=[("3 4\nabce\nsfcs\nadee\nabcced", "a→b→c→c→e→d along the grid."), ("3 4\nabce\nsfcs\nadee\nabcb", "The second b would reuse a cell.")],
        tests=_word_tests,
    ),
    Problem(
        title="Rat in a Maze",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking", "Matrix"],
        description="""A rat starts at the top-left cell of an `n × n` maze and wants to reach the bottom-right cell. Cells with `1` are open, `0` are blocked. It can move **D**own, **L**eft, **R**ight or **U**p and can't visit a cell twice in one path.

**Input:** line 1 — `n`; next `n` lines — the maze rows as space-separated 0/1 values.

**Output:** every path as a string of moves, one per line, sorted lexicographically. Print `-1` if no path exists (including when the start or end is blocked).""",
        constraints=["2 <= n <= 5"],
        solve=_rat,
        examples=[("4\n1 0 0 0\n1 1 0 1\n1 1 0 0\n0 1 1 1", "Two routes reach the corner."), ("2\n1 0\n0 1", "The rat is boxed in.")],
        tests=_rat_tests,
    ),
    Problem(
        title="N-Queens",
        difficulty="HARD",
        topics=["Recursion", "Backtracking"],
        description="""Place `n` queens on an `n × n` chessboard so that no two attack each other (no shared row, column or diagonal).

**Input:** one integer `n`.

**Output:** line 1 — the number of valid placements. If there is at least one, then print the board of the **first** placement in this order: compare placements row by row by the column of that row's queen, smallest first. Print the board as `n` lines using `Q` for a queen and `.` for an empty square.""",
        constraints=["1 <= n <= 9"],
        solve=_queens,
        brute=_queens_brute,
        examples=[("4", "Two placements; the first has queens in columns 1, 3, 0, 2."), ("3", "No placement works.")],
        tests=lambda r: ["1", "2", "5", "6", "7", "8", "9"],
    ),
    Problem(
        title="Graph M-Coloring",
        difficulty="MEDIUM",
        topics=["Recursion", "Backtracking"],
        description="""Can the vertices of an undirected graph be colored with at most `k` colors so that no edge connects two vertices of the same color?

**Input:** line 1 — `n` (vertices numbered 0…n−1), `m` (edges) and `k`; next `m` lines — edges `u v`.

**Output:** `true` if such a coloring exists, otherwise `false`.""",
        constraints=["1 <= n <= 8", "0 <= m <= n(n−1)/2", "1 <= k <= 4"],
        solve=_mcolor,
        brute=_mcolor_brute,
        examples=[("4 5 3\n0 1\n1 2\n2 3\n3 0\n0 2", "Color 0 and 2 differently from everything around them."), ("3 3 2\n0 1\n1 2\n0 2", "A triangle needs 3 colors.")],
        tests=_mcolor_tests,
    ),
    Problem(
        title="Sudoku Solver",
        difficulty="HARD",
        topics=["Recursion", "Backtracking", "Matrix"],
        description="""Solve a 9 × 9 Sudoku: fill the empty cells so that every row, every column and every 3 × 3 box contains each digit 1–9 exactly once. Every puzzle given has exactly one solution.

**Input:** 9 lines of 9 characters each; `0` marks an empty cell.

**Output:** the solved grid as 9 lines of 9 digits.""",
        constraints=["The puzzle has exactly one solution."],
        solve=_sudoku,
        examples=[(_SAMPLE_SUDOKU, "Try digits in empty cells, backing up when a row, column or box conflicts.")],
        tests=_sudoku_tests,
    ),
]
