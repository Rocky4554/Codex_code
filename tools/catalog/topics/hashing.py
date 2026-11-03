"""Hashing — counting, lookups and prefix-sum maps."""
from collections import Counter, defaultdict

from lib import Playlist, Problem, boolstr, ints, join, lines, rand_ints, rand_str

PLAYLISTS = [
    Playlist(
        key="hashing",
        title="04 · Hashing",
        description="Trade a little memory for speed: count, look up and remember what you've seen with hash maps and sets.",
        accent="#A8E6CF",
        titles=[
            "Frequency of Elements",
            "Count Occurrences in Array",
            "Contains Duplicate",
            "Find First Duplicate",
            "Highest and Lowest Frequency Element",
            "Find Intersection of Arrays",
            "Two Sum",
            "Isomorphic Strings",
            "Distinct Elements in Every Window",
            "Group Anagrams",
            "Valid Sudoku",
            "Longest Subarray with Sum K",
            "Subarray Sum Equals K",
            "Count Subarrays with XOR K",
        ],
    )
]


def _hi_lo(inp):
    a = ints(lines(inp)[0])
    c = Counter(a)
    hi = max(c.values())
    lo = min(c.values())
    return f"{min(x for x in c if c[x] == hi)} {min(x for x in c if c[x] == lo)}"


def _isomorphic(inp):
    s, t = lines(inp)[:2]
    if len(s) != len(t):
        return "false"
    f, b = {}, {}
    for x, y in zip(s, t):
        if f.setdefault(x, y) != y or b.setdefault(y, x) != x:
            return "false"
    return "true"


def _isomorphic_brute(inp):
    s, t = lines(inp)[:2]
    if len(s) != len(t):
        return "false"
    pat = lambda w: [w.index(ch) for ch in w]  # noqa: E731
    return boolstr(pat(s) == pat(t))


def _window_distinct(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    c = Counter(a[:k])
    out = [len(c)]
    for i in range(k, len(a)):
        c[a[i]] += 1
        c[a[i - k]] -= 1
        if c[a[i - k]] == 0:
            del c[a[i - k]]
        out.append(len(c))
    return join(out)


def _window_distinct_brute(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    return join(len(set(a[i:i + k])) for i in range(len(a) - k + 1))


def _sudoku(inp):
    g = [row.split() for row in lines(inp)[:9]]
    seen = set()
    for r in range(9):
        for c in range(9):
            v = g[r][c]
            if v == ".":
                continue
            keys = [("r", r, v), ("c", c, v), ("b", r // 3, c // 3, v)]
            if any(k in seen for k in keys):
                return "false"
            seen.update(keys)
    return "true"


def _longest_sum_k(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    first = {0: -1}
    s = best = 0
    for i, x in enumerate(a):
        s += x
        if s - k in first:
            best = max(best, i - first[s - k])
        first.setdefault(s, i)
    return str(best)


def _longest_sum_k_brute(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    best = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s == k:
                best = max(best, j - i + 1)
    return str(best)


def _count_sum_k(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    seen = defaultdict(int)
    seen[0] = 1
    s = cnt = 0
    for x in a:
        s += x
        cnt += seen[s - k]
        seen[s] += 1
    return str(cnt)


def _count_sum_k_brute(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    cnt = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            cnt += s == k
    return str(cnt)


def _count_xor_k(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    seen = defaultdict(int)
    seen[0] = 1
    x = cnt = 0
    for v in a:
        x ^= v
        cnt += seen[x ^ k]
        seen[x] += 1
    return str(cnt)


def _count_xor_k_brute(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    cnt = 0
    for i in range(len(a)):
        x = 0
        for j in range(i, len(a)):
            x ^= a[j]
            cnt += x == k
    return str(cnt)


def _arr_k(r, n, lo, hi, klo, khi):
    return f"{join(rand_ints(r, n, lo, hi))}\n{r.randint(klo, khi)}"


def _sudoku_board(r, valid: bool, holes: int):
    base = [[(3 * (i % 3) + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
    digits = list(range(1, 10))
    r.shuffle(digits)
    g = [[str(digits[v - 1]) for v in row] for row in base]
    cells = [(i, j) for i in range(9) for j in range(9)]
    for i, j in r.sample(cells, holes):
        g[i][j] = "."
    if not valid:
        empties = [(i, j) for i, j in cells if g[i][j] == "."]
        i, j = r.choice(empties)
        # copy a digit already present in the same row
        present = [x for x in g[i] if x != "."]
        g[i][j] = r.choice(present)
    return "\n".join(" ".join(row) for row in g)


def _sudoku_tests(r):
    out = [_sudoku_board(r, True, 81 - 1), _sudoku_board(r, True, 0)]
    for h in (30, 45, 60):
        out.append(_sudoku_board(r, True, h))
        out.append(_sudoku_board(r, False, h))
    # box-only conflict: two same digits in one box, different rows/cols
    g = [["."] * 9 for _ in range(9)]
    g[0][0] = "5"
    g[1][1] = "5"
    out.append("\n".join(" ".join(row) for row in g))
    # column conflict
    g = [["."] * 9 for _ in range(9)]
    g[0][4] = "3"
    g[8][4] = "3"
    out.append("\n".join(" ".join(row) for row in g))
    return out


PROBLEMS = [
    Problem(
        title="Highest and Lowest Frequency Element",
        difficulty="EASY",
        topics=["Hash Map", "Array"],
        description="""Given an array, find the element that appears **most often** and the element that appears **least often** (among the values that appear at all).

If several values share the highest frequency, pick the smallest of them. Do the same for the lowest frequency.

**Input:** one line of space-separated integers.

**Output:** the most frequent value and the least frequent value, separated by a space.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_hi_lo,
        examples=[("10 5 10 15 10 5", "10 appears 3 times; 15 appears once."), ("4 4 2 2", "Both appear twice, so the smallest (2) wins both ties.")],
        tests=lambda r: ["7", "1 2 3", "-5 -5 3 3 3 -1", "9 9 9 9"]
        + [join(rand_ints(r, n, 1, m)) for n, m in ((20, 5), (50, 10), (200, 30))]
        + [join(rand_ints(r, 2000, -10**9, 10**9))],
    ),
    Problem(
        title="Isomorphic Strings",
        difficulty="EASY",
        topics=["Hash Map", "String"],
        description="""Two strings `s` and `t` are **isomorphic** if you can replace every character of `s` to get `t`, where each character always maps to the same character and no two different characters map to the same one. A character may map to itself.

Print `true` if `s` and `t` are isomorphic, otherwise `false`.

**Input:** `s` on the first line, `t` on the second. Both are non-empty lowercase strings.

**Output:** `true` or `false`.""",
        constraints=["1 <= |s|, |t| <= 5 * 10^4"],
        solve=_isomorphic,
        brute=_isomorphic_brute,
        examples=[("egg\nadd", "e→a and g→d."), ("badc\nbaba", "Both d and b would have to map to b.")],
        tests=lambda r: ["a\nb", "ab\naa", "aa\nab", "abc\nabcd", "paper\ntitle", "foo\nbar", "abab\ncdcd", "abcdefghijklmnopqrstuvwxyz\nzyxwvutsrqponmlkjihgfedcba"]
        + [(lambda s: f"{s}\n{s.translate(str.maketrans('abcd', 'dcba'))}")(rand_str(r, 40, "abcd"))]
        + [f"{rand_str(r, 30, 'abc')}\n{rand_str(r, 30, 'xyz')}" for _ in range(2)]
        + [(lambda s: f"{s}\n{s.translate(str.maketrans('abcdefghij', 'jihgfedcba'))}")(rand_str(r, 5000, "abcdefghij"))],
    ),
    Problem(
        title="Distinct Elements in Every Window",
        difficulty="MEDIUM",
        topics=["Hash Map", "Sliding Window", "Array"],
        description="""Given an array and a window size `k`, count how many **distinct** values are in each contiguous window of `k` elements, from left to right.

Recounting every window is `O(n·k)`. Instead, keep a count map and update it as the window slides: add the entering element, remove the leaving one.

**Input:** the array on the first line, `k` on the second.

**Output:** `n - k + 1` space-separated counts, one per window.""",
        constraints=["1 <= k <= n <= 10^5"],
        solve=_window_distinct,
        brute=_window_distinct_brute,
        examples=[("1 2 1 3 4 2 3\n4", "Windows: [1,2,1,3]→3, [2,1,3,4]→4, [1,3,4,2]→4, [3,4,2,3]→3."), ("5 5 5\n2", "Every window holds only 5.")],
        tests=lambda r: ["7\n1", "1 2 3 4\n4", "1 2 3 4\n1", "2 2 2 2 2\n3"]
        + [_arr_k(r, 30, 1, 5, 3, 3), _arr_k(r, 50, 1, 20, 1, 50), _arr_k(r, 60, -3, 3, 10, 10)]
        + [f"{join(rand_ints(r, 4000, 1, 500))}\n250"],
    ),
    Problem(
        title="Valid Sudoku",
        difficulty="MEDIUM",
        topics=["Hash Set", "Matrix"],
        description="""You're given a partially filled 9×9 Sudoku board. Decide whether the filled cells are **consistent**: no digit repeats within a row, within a column, or within any of the nine 3×3 boxes.

Empty cells are written as `.`. You don't need to check whether the board can actually be solved, only whether the digits already placed break a rule.

**Input:** 9 lines, each with 9 space-separated tokens (`1`–`9` or `.`).

**Output:** `true` if the board is consistent, otherwise `false`.""",
        constraints=["The board is always 9×9"],
        solve=_sudoku,
        examples=[(
            "5 3 . . 7 . . . .\n6 . . 1 9 5 . . .\n. 9 8 . . . . 6 .\n8 . . . 6 . . . 3\n4 . . 8 . 3 . . 1\n7 . . . 2 . . . 6\n. 6 . . . . 2 8 .\n. . . 4 1 9 . . 5\n. . . . 8 . . 7 9",
            "No row, column or box repeats a digit.",
        ), (
            "8 3 . . 7 . . . .\n6 . . 1 9 5 . . .\n. 9 8 . . . . 6 .\n8 . . . 6 . . . 3\n4 . . 8 . 3 . . 1\n7 . . . 2 . . . 6\n. 6 . . . . 2 8 .\n. . . 4 1 9 . . 5\n. . . . 8 . . 7 9",
            "The first column has two 8s (and so does the top-left box).",
        )],
        tests=_sudoku_tests,
    ),
    Problem(
        title="Longest Subarray with Sum K",
        difficulty="MEDIUM",
        topics=["Hash Map", "Prefix Sum", "Array"],
        description="""Find the length of the longest contiguous subarray whose elements add up to exactly `k`. The array may contain negative numbers. Print `0` if no subarray has sum `k`.

Keep a running prefix sum and remember the **first** index where each prefix sum appears. If `prefix - k` was seen at index `j`, the subarray after `j` up to here sums to `k`.

**Input:** the array on the first line, `k` on the second.

**Output:** the length of the longest subarray with sum `k`.""",
        constraints=["1 <= n <= 10^5", "-10^4 <= a[i] <= 10^4", "-10^9 <= k <= 10^9"],
        solve=_longest_sum_k,
        brute=_longest_sum_k_brute,
        examples=[("10 5 2 7 1 9\n15", "[5, 2, 7, 1] has sum 15 and length 4."), ("-1 2 3\n6", "No subarray sums to 6.")],
        tests=lambda r: ["5\n5", "5\n3", "0 0 0 0\n0", "1 -1 1 -1 1\n0", "-5 8 -14 2 4 12\n-5", "1 2 3 4 5\n15"]
        + [_arr_k(r, 40, -5, 5, -3, 3), _arr_k(r, 60, -10, 10, -5, 5), _arr_k(r, 80, 0, 4, 5, 12)]
        + [f"{join(rand_ints(r, 4000, -20, 20))}\n7"],
    ),
    Problem(
        title="Count Subarrays with XOR K",
        difficulty="HARD",
        topics=["Hash Map", "Prefix Sum", "Array"],
        description="""Count the contiguous subarrays whose bitwise XOR of all elements equals `k`.

XOR works like a prefix sum: if `P` is the XOR of everything so far, a subarray ending here has XOR `k` exactly when some earlier prefix equals `P ^ k`. Count those prefixes with a hash map.

**Input:** the array of non-negative integers on the first line, `k` on the second.

**Output:** the number of subarrays with XOR equal to `k`.""",
        constraints=["1 <= n <= 10^5", "0 <= a[i], k <= 10^9"],
        solve=_count_xor_k,
        brute=_count_xor_k_brute,
        examples=[("4 2 2 6 4\n6", "[4,2], [4,2,2,6,4], [2,2,6] and [6]."), ("5 6 7 8 9\n5", "[5] and the whole array (5 ^ 6 ^ 7 ^ 8 ^ 9 = 5).")],
        tests=lambda r: ["0\n0", "1\n0", "0 0 0\n0", "1 2 3\n0", "7 7 7 7\n7"]
        + [_arr_k(r, 40, 0, 7, 0, 7), _arr_k(r, 60, 0, 15, 0, 15), _arr_k(r, 80, 0, 3, 1, 1)]
        + [f"{join(rand_ints(r, 4000, 0, 63))}\n21"],
    ),
]
