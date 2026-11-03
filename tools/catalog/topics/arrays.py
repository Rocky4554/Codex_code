"""Arrays — traversal, two pointers, prefix sums and matrices."""
from collections import Counter
from itertools import combinations

from lib import Playlist, Problem, ints, join, lines, rand_ints

PLAYLISTS = [
    Playlist(
        key="arrays",
        title="03 · Arrays",
        description="From single scans to prefix sums, two pointers and matrix walks — the core of most interviews.",
        accent="#A8E6CF",
        titles=[
            "Find Largest / Smallest Element",
            "Find Second Largest Number",
            "Left Rotate by One",
            "Remove Duplicates from Sorted Array",
            "Move All Zeros to End",
            "Rotate Array by K Positions",
            "Union of Two Sorted Arrays",
            "Find Missing Number in Array",
            "Max Consecutive Ones",
            "Find Duplicates in Array",
            "Merge Two Sorted Arrays",
            "Leaders in an Array",
            "Best Time to Buy and Sell Stock",
            "Rearrange by Sign",
            "Majority Element",
            "Maximum Subarray",
            "Product of Array Except Self",
            "Longest Consecutive Sequence",
            "Pascal's Triangle",
            "Spiral Matrix",
            "Rotate Matrix 90 Degrees",
            "Set Matrix Zeroes",
            "Next Permutation",
            "Subarray Sum Equals K",
            "Majority Element II",
            "3Sum",
            "4Sum",
            "Merge Intervals",
            "Maximum Product Subarray",
            "Count Inversions",
            "Trapping Rain Water",
        ],
    )
]


def _arr(inp):
    return ints(lines(inp)[0])


def _matrix(inp):
    ls = lines(inp)
    r, c = map(int, ls[0].split())
    return [ints(ls[1 + i]) for i in range(r)], r, c


def _matrix_text(m):
    return "\n".join(join(row) for row in m)


def _rand_matrix(r, rows, cols, lo, hi):
    return f"{rows} {cols}\n" + "\n".join(join(rand_ints(r, cols, lo, hi)) for _ in range(rows))


# ── solutions ────────────────────────────────────────────────────

def _left_rotate(inp):
    a = _arr(inp)
    return join(a[1:] + a[:1])


def _union(inp):
    ls = lines(inp)
    a, b = ints(ls[0]), ints(ls[1])
    i = j = 0
    out = []
    while i < len(a) or j < len(b):
        if j >= len(b) or (i < len(a) and a[i] <= b[j]):
            v = a[i]; i += 1
        else:
            v = b[j]; j += 1
        if not out or out[-1] != v:
            out.append(v)
    return join(out)


def _union_brute(inp):
    ls = lines(inp)
    return join(sorted(set(ints(ls[0])) | set(ints(ls[1]))))


def _max_ones(inp):
    best = cur = 0
    for x in _arr(inp):
        cur = cur + 1 if x == 1 else 0
        best = max(best, cur)
    return str(best)


def _leaders(inp):
    a = _arr(inp)
    out, mx = [], None
    for x in reversed(a):
        if mx is None or x > mx:
            out.append(x)
            mx = x
    return join(reversed(out))


def _leaders_brute(inp):
    a = _arr(inp)
    return join(a[i] for i in range(len(a)) if all(a[i] > a[j] for j in range(i + 1, len(a))))


def _longest_consec(inp):
    s = set(_arr(inp))
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return str(best)


def _longest_consec_brute(inp):
    v = sorted(set(_arr(inp)))
    best = cur = 1
    for i in range(1, len(v)):
        cur = cur + 1 if v[i] == v[i - 1] + 1 else 1
        best = max(best, cur)
    return str(best)


def _rearrange(inp):
    a = _arr(inp)
    pos = [x for x in a if x > 0]
    neg = [x for x in a if x < 0]
    out = []
    for p, n in zip(pos, neg):
        out += [p, n]
    return join(out)


def _next_perm(inp):
    a = _arr(inp)
    i = len(a) - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i >= 0:
        j = len(a) - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
    a[i + 1 :] = reversed(a[i + 1 :])
    return join(a)


def _next_perm_brute(inp):
    from itertools import permutations
    a = tuple(_arr(inp))
    perms = sorted(set(permutations(a)))
    k = perms.index(a)
    return join(perms[(k + 1) % len(perms)])


def _spiral(inp):
    m, r, c = _matrix(inp)
    top, bot, left, right = 0, r - 1, 0, c - 1
    out = []
    while top <= bot and left <= right:
        out += [m[top][j] for j in range(left, right + 1)]
        out += [m[i][right] for i in range(top + 1, bot + 1)]
        if top < bot:
            out += [m[bot][j] for j in range(right - 1, left - 1, -1)]
        if left < right:
            out += [m[i][left] for i in range(bot - 1, top, -1)]
        top, bot, left, right = top + 1, bot - 1, left + 1, right - 1
    return join(out)


def _spiral_brute(inp):
    m, r, c = _matrix(inp)
    seen = [[False] * c for _ in range(r)]
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    i = j = d = 0
    out = []
    for _ in range(r * c):
        out.append(m[i][j]); seen[i][j] = True
        ni, nj = i + dirs[d][0], j + dirs[d][1]
        if not (0 <= ni < r and 0 <= nj < c) or seen[ni][nj]:
            d = (d + 1) % 4
            ni, nj = i + dirs[d][0], j + dirs[d][1]
        i, j = ni, nj
    return join(out)


def _rotate(inp):
    m, n, _ = _matrix(inp)
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j], m[j][i] = m[j][i], m[i][j]
    for row in m:
        row.reverse()
    return _matrix_text(m)


def _rotate_brute(inp):
    m, n, _ = _matrix(inp)
    return _matrix_text([[m[n - 1 - j][i] for j in range(n)] for i in range(n)])


def _zeroes(inp):
    m, r, c = _matrix(inp)
    rows = {i for i in range(r) for j in range(c) if m[i][j] == 0}
    cols = {j for i in range(r) for j in range(c) if m[i][j] == 0}
    return _matrix_text([[0 if i in rows or j in cols else m[i][j] for j in range(c)] for i in range(r)])


def _pascal(inp):
    n = int(lines(inp)[0])
    rows, row = [], [1]
    for _ in range(n):
        rows.append(row)
        row = [1] + [row[k] + row[k + 1] for k in range(len(row) - 1)] + [1]
    return "\n".join(join(x) for x in rows)


def _pascal_brute(inp):
    from math import comb
    n = int(lines(inp)[0])
    return "\n".join(join(comb(i, k) for k in range(i + 1)) for i in range(n))


def _subarray_k(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    seen = Counter({0: 1})
    s = count = 0
    for x in a:
        s += x
        count += seen[s - k]
        seen[s] += 1
    return str(count)


def _subarray_k_brute(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    return str(sum(1 for i in range(len(a)) for j in range(i, len(a)) if sum(a[i : j + 1]) == k))


def _majority2(inp):
    a = _arr(inp)
    c1 = c2 = None
    n1 = n2 = 0
    for x in a:
        if x == c1:
            n1 += 1
        elif x == c2:
            n2 += 1
        elif n1 == 0:
            c1, n1 = x, 1
        elif n2 == 0:
            c2, n2 = x, 1
        else:
            n1 -= 1
            n2 -= 1
    res = sorted({c for c in (c1, c2) if c is not None and a.count(c) > len(a) // 3})
    return join(res) or "none"


def _majority2_brute(inp):
    a = _arr(inp)
    c = Counter(a)
    return join(sorted(v for v in c if c[v] > len(a) // 3)) or "none"


def _four_sum(inp):
    ls = lines(inp)
    a, target = sorted(ints(ls[0])), int(ls[1])
    n, out = len(a), []
    for i in range(n):
        if i and a[i] == a[i - 1]:
            continue
        for j in range(i + 1, n):
            if j > i + 1 and a[j] == a[j - 1]:
                continue
            lo, hi = j + 1, n - 1
            while lo < hi:
                s = a[i] + a[j] + a[lo] + a[hi]
                if s < target:
                    lo += 1
                elif s > target:
                    hi -= 1
                else:
                    out.append((a[i], a[j], a[lo], a[hi]))
                    lo += 1
                    while lo < hi and a[lo] == a[lo - 1]:
                        lo += 1
                    hi -= 1
    return "\n".join(join(q) for q in out) or "none"


def _four_sum_brute(inp):
    ls = lines(inp)
    a, target = ints(ls[0]), int(ls[1])
    qs = sorted({tuple(sorted(c)) for c in combinations(a, 4) if sum(c) == target})
    return "\n".join(join(q) for q in qs) or "none"


def _inversions(inp):
    a = _arr(inp)

    def sort(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        inv = sort(lo, mid) + sort(mid, hi)
        merged, i, j = [], lo, mid
        while i < mid and j < hi:
            if a[i] <= a[j]:
                merged.append(a[i]); i += 1
            else:
                merged.append(a[j]); j += 1
                inv += mid - i
        merged += a[i:mid] + a[j:hi]
        a[lo:hi] = merged
        return inv

    return str(sort(0, len(a)))


def _inversions_brute(inp):
    a = _arr(inp)
    return str(sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j]))


def _max_product(inp):
    a = _arr(inp)
    best = hi = lo = a[0]
    for x in a[1:]:
        cand = (x, hi * x, lo * x)
        hi, lo = max(cand), min(cand)
        best = max(best, hi)
    return str(best)


def _max_product_brute(inp):
    a = _arr(inp)
    best = a[0]
    for i in range(len(a)):
        p = 1
        for j in range(i, len(a)):
            p *= a[j]
            best = max(best, p)
    return str(best)


# ── test generators ─────────────────────────────────────────────

def _rand_sorted(r, n, lo, hi):
    return join(sorted(rand_ints(r, n, lo, hi)))


def _rearrange_case(r, half):
    pos = [r.randint(1, 10**6) for _ in range(half)]
    neg = [-r.randint(1, 10**6) for _ in range(half)]
    tagged = [(p, 0) for p in pos] + [(q, 1) for q in neg]
    r.shuffle(tagged)
    return join(x for x, _ in tagged)


def _four_sum_case(r, n, lo, hi):
    a = rand_ints(r, n, lo, hi)
    t = sum(r.sample(a, 4)) if n >= 4 else 0
    return f"{join(a)}\n{t}"


PROBLEMS = [
    Problem(
        title="Left Rotate by One",
        difficulty="EASY",
        topics=["Array"],
        description="""Shift every element of the array one position to the left. The first element moves to the end.

**Input:** one line of space-separated integers.

**Output:** the rotated array, space-separated.""",
        constraints=["1 <= n <= 10^5"],
        solve=_left_rotate,
        examples=[("1 2 3 4 5", "1 moves from the front to the back."), ("9", "A single element stays put.")],
        tests=lambda r: ["1 2", "7 7 7", "-1 0 1", "5 4 3 2 1"] + [join(rand_ints(r, n, -100, 100)) for n in (6, 20, 100)] + [join(rand_ints(r, 3000, -10**5, 10**5))],
    ),
    Problem(
        title="Union of Two Sorted Arrays",
        difficulty="EASY",
        topics=["Array", "Two Pointers"],
        description="""Given two arrays that are each sorted in non-decreasing order, print every **distinct** value that appears in either one, in increasing order.

Merge them with two pointers and skip a value if it equals the last one you printed — no set needed.

**Input:** two lines, each a sorted list of space-separated integers.

**Output:** the union, space-separated, in increasing order.""",
        constraints=["1 <= n, m <= 10^5"],
        solve=_union,
        brute=_union_brute,
        examples=[("1 2 3 4 5\n2 3 4 4 5 6", "Every value from 1 to 6 appears somewhere."), ("1 1 1\n2 2", "Duplicates collapse.")],
        tests=lambda r: ["5\n5", "1\n2", "-3 -1\n-2 0", "1 2 3\n4 5 6", "4 5 6\n1 2 3", "1 1 2 2\n1 1 2 2"]
        + [f"{_rand_sorted(r, n, -20, 20)}\n{_rand_sorted(r, m, -20, 20)}" for n, m in ((8, 5), (30, 40))]
        + [f"{_rand_sorted(r, 1500, -10**5, 10**5)}\n{_rand_sorted(r, 1500, -10**5, 10**5)}"],
    ),
    Problem(
        title="Max Consecutive Ones",
        difficulty="EASY",
        topics=["Array"],
        description="""The array contains only 0s and 1s. Print the length of the longest run of consecutive 1s.

**Input:** one line of space-separated 0s and 1s.

**Output:** the length of the longest run of 1s (0 if there are none).""",
        constraints=["1 <= n <= 10^5"],
        solve=_max_ones,
        examples=[("1 1 0 1 1 1", "The last three 1s form the longest run."), ("0 0", "No 1s at all.")],
        tests=lambda r: ["1", "0", "1 1 1 1", "1 0 1 0 1", "0 1 1 0 1 1 1 1"] + [join(rand_ints(r, n, 0, 1)) for n in (15, 60, 300)] + [join(r.choices([0, 1], weights=[1, 6], k=8000))],
    ),
    Problem(
        title="Leaders in an Array",
        difficulty="EASY",
        topics=["Array"],
        description="""An element is a **leader** if it is strictly greater than every element to its right. The last element is always a leader.

Scan from the right while tracking the maximum seen so far.

**Input:** one line of space-separated integers.

**Output:** the leaders in their original left-to-right order, space-separated.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_leaders,
        brute=_leaders_brute,
        examples=[("16 17 4 3 5 2", "17 beats everything after it, so do 5 and 2."), ("5 5 5", "Equal is not strictly greater, so only the last 5 leads.")],
        tests=lambda r: ["8", "1 2 3 4", "4 3 2 1", "-1 -2 -3", "2 2 1 1", "10 -5 10"] + [join(rand_ints(r, n, -50, 50)) for n in (10, 40, 150)] + [join(rand_ints(r, 2500, -10**9, 10**9))],
    ),
    Problem(
        title="Longest Consecutive Sequence",
        difficulty="MEDIUM",
        topics=["Array", "Hash Set"],
        description="""The array is unsorted. Find the length of the longest set of values that form a run of consecutive integers (like 4, 5, 6, 7). The values may appear anywhere in the array; duplicates count once.

Sorting takes `O(n log n)`. With a hash set you can do `O(n)`: only start counting from a value `x` whose `x − 1` is missing.

**Input:** one line of space-separated integers.

**Output:** the length of the longest consecutive run.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_longest_consec,
        brute=_longest_consec_brute,
        examples=[("100 4 200 1 3 2", "1, 2, 3, 4 is a run of length 4."), ("0 3 7 2 5 8 4 6 0 1", "0 through 8 — length 9.")],
        tests=lambda r: ["5", "1 1 1", "10 30 20", "-2 -1 0 1", "1 3 5 2 4", "1000000000 -1000000000"]
        + [join(rand_ints(r, n, -30, 30)) for n in (10, 40, 200)]
        + [join(r.sample(range(-5000, 5000), 3000))],
    ),
    Problem(
        title="Rearrange by Sign",
        difficulty="MEDIUM",
        topics=["Array", "Two Pointers"],
        description="""The array has an equal number of positive and negative numbers (and no zeros). Rearrange it so signs alternate, **starting with a positive number**, while keeping the original relative order of the positives among themselves and of the negatives among themselves.

**Input:** one line of space-separated non-zero integers, half positive and half negative.

**Output:** the rearranged array, space-separated.""",
        constraints=["2 <= n <= 10^5", "n is even"],
        solve=_rearrange,
        examples=[("3 1 -2 -5 2 -4", "Positives 3, 1, 2 interleave with negatives -2, -5, -4."), ("-1 1", "Positive first: 1 -1.")],
        tests=lambda r: ["1 -1", "-5 -6 7 8", "1 2 3 -1 -2 -3", "-3 -2 -1 3 2 1"] + [_rearrange_case(r, h) for h in (4, 10, 50, 1000)],
    ),
    Problem(
        title="Pascal's Triangle",
        difficulty="EASY",
        topics=["Array", "Math"],
        description="""Print the first `n` rows of Pascal's triangle. Each row starts and ends with 1, and every inner value is the sum of the two values above it.

**Input:** one integer `n`.

**Output:** `n` lines; line `i` (starting at 1) has the `i` values of that row, space-separated.""",
        constraints=["1 <= n <= 30"],
        solve=_pascal,
        brute=_pascal_brute,
        examples=[("5", "Row 5 is 1 4 6 4 1."), ("1", "Just the top 1.")],
        tests=lambda r: ["2", "3", "6", "10", "15", "20", "30"],
    ),
    Problem(
        title="Spiral Matrix",
        difficulty="MEDIUM",
        topics=["Matrix", "Array"],
        description="""Print all elements of an `r × c` matrix in spiral order: go right along the top row, down the right column, left along the bottom row, up the left column, then repeat on the inner layer.

**Input:** the first line has `r` and `c`, followed by `r` lines of `c` integers.

**Output:** all `r·c` values in spiral order, space-separated.""",
        constraints=["1 <= r, c <= 50"],
        solve=_spiral,
        brute=_spiral_brute,
        examples=[("3 3\n1 2 3\n4 5 6\n7 8 9", "Right 1 2 3, down 6 9, left 8 7, up 4, then the centre 5."), ("2 4\n1 2 3 4\n5 6 7 8", "One full lap covers everything.")],
        tests=lambda r: ["1 1\n7", "1 4\n1 2 3 4", "4 1\n1\n2\n3\n4", "2 2\n1 2\n3 4", "3 4\n1 2 3 4\n5 6 7 8\n9 10 11 12"]
        + [_rand_matrix(r, a, b, -99, 99) for a, b in ((5, 3), (4, 7), (6, 6), (40, 35))],
    ),
    Problem(
        title="Rotate Matrix 90 Degrees",
        difficulty="MEDIUM",
        topics=["Matrix", "Array"],
        description="""Rotate an `n × n` matrix 90 degrees **clockwise**.

You can do it in place: transpose the matrix (swap `m[i][j]` with `m[j][i]`), then reverse every row.

**Input:** the first line is `n n`, followed by `n` lines of `n` integers.

**Output:** the rotated matrix, one row per line, values space-separated.""",
        constraints=["1 <= n <= 60"],
        solve=_rotate,
        brute=_rotate_brute,
        examples=[("3 3\n1 2 3\n4 5 6\n7 8 9", "The left column 1 4 7 becomes the top row read bottom-up: 7 4 1."), ("1 1\n5", "Nothing to rotate.")],
        tests=lambda r: ["2 2\n1 2\n3 4", "2 2\n0 0\n0 1"] + [_rand_matrix(r, n, n, -99, 99) for n in (3, 4, 5, 8, 20, 50)],
    ),
    Problem(
        title="Set Matrix Zeroes",
        difficulty="MEDIUM",
        topics=["Matrix", "Array"],
        description="""Wherever the matrix has a 0, set that cell's **entire row and column** to 0. Decide using the original zeros only — zeros you write don't spread further.

**Input:** the first line has `r` and `c`, followed by `r` lines of `c` integers.

**Output:** the resulting matrix, one row per line, values space-separated.""",
        constraints=["1 <= r, c <= 60"],
        solve=_zeroes,
        examples=[("3 3\n1 1 1\n1 0 1\n1 1 1", "The centre zero clears the middle row and column."), ("2 3\n0 1 2\n3 4 5", "Row 0 and column 0 become zero.")],
        tests=lambda r: ["1 1\n0", "1 1\n5", "2 2\n1 2\n3 4", "2 2\n0 0\n1 1", "3 4\n1 2 3 0\n4 5 6 7\n8 0 9 1"]
        + [_rand_matrix(r, a, b, 0, 9) for a, b in ((4, 5), (6, 3))]
        + [_rand_matrix(r, 7, 7, 1, 20).replace(" 5 ", " 0 ", 1), _rand_matrix(r, 40, 40, 1, 400)],
    ),
    Problem(
        title="Next Permutation",
        difficulty="MEDIUM",
        topics=["Array", "Two Pointers"],
        description="""Rearrange the numbers into the **next lexicographically greater permutation**. If the array is already the largest permutation (non-increasing), wrap around to the smallest one (sorted ascending).

From the right, find the first index `i` with `a[i] < a[i+1]`, swap `a[i]` with the smallest larger value to its right, then reverse the suffix after `i`.

**Input:** one line of space-separated integers (duplicates allowed).

**Output:** the next permutation, space-separated.""",
        constraints=["1 <= n <= 10^5", "0 <= a[i] <= 100"],
        solve=_next_perm,
        brute=_next_perm_brute,
        examples=[("1 2 3", "The permutation after 1 2 3 is 1 3 2."), ("3 2 1", "The largest wraps around to 1 2 3.")],
        tests=lambda r: ["1", "1 1", "1 1 5", "1 5 1", "5 1 1", "2 3 1", "1 3 2", "1 2 3 6 5 4"]
        + [join(rand_ints(r, 7, 0, 4)), join(rand_ints(r, 6, 0, 9)), join(rand_ints(r, 3000, 0, 100))],
    ),
    Problem(
        title="Subarray Sum Equals K",
        difficulty="MEDIUM",
        topics=["Array", "Hash Map", "Prefix Sum"],
        description="""Count the contiguous, non-empty subarrays whose elements add up to exactly `k`. Elements can be negative.

Keep a running prefix sum and a hash map of how many times each prefix sum has appeared: a subarray ending here sums to `k` once for every earlier prefix equal to `sum − k`.

**Input:** the first line is the array; the second line is `k`.

**Output:** the number of subarrays with sum `k`.""",
        constraints=["1 <= n <= 2·10^4", "-1000 <= a[i] <= 1000", "-10^7 <= k <= 10^7"],
        solve=_subarray_k,
        brute=_subarray_k_brute,
        examples=[("1 1 1\n2", "[1, 1] at positions 0–1 and 1–2."), ("1 2 3\n3", "[1, 2] and [3].")],
        tests=lambda r: ["5\n5", "5\n3", "0 0 0\n0", "1 -1 1 -1\n0", "-1 -1 1\n0", "3 4 7 2 -3 1 4 2\n7"]
        + [f"{join(rand_ints(r, n, -5, 5))}\n{r.randint(-5, 5)}" for n in (15, 40, 80)]
        + [f"{join(rand_ints(r, 4000, -10, 10))}\n{r.randint(-20, 20)}"],
    ),
    Problem(
        title="Majority Element II",
        difficulty="MEDIUM",
        topics=["Array", "Hash Map"],
        description="""Find every value that appears **more than ⌊n/3⌋ times**. There can be at most two such values.

A counter map works; the extended Boyer–Moore vote finds the two candidates in `O(1)` extra space, followed by a second pass to verify them.

**Input:** one line of space-separated integers.

**Output:** the qualifying values in increasing order, space-separated, or `none` if there are none.""",
        constraints=["1 <= n <= 5·10^4", "-10^9 <= a[i] <= 10^9"],
        solve=_majority2,
        brute=_majority2_brute,
        examples=[("3 2 3", "3 appears twice, more than ⌊3/3⌋ = 1."), ("1 2 3 4", "Nothing appears more than once.")],
        tests=lambda r: ["1", "1 2", "2 2", "1 1 2 2 3", "1 2 3 1 2 3", "4 4 4 1 2 3", "-1 -1 -1 5 5 5 0"]
        + [join(rand_ints(r, n, 0, 3)) for n in (10, 30, 200)]
        + [join(r.choices([7, -7, 1, 2, 3, 4], weights=[5, 4, 1, 1, 1, 1], k=3000))],
    ),
    Problem(
        title="4Sum",
        difficulty="MEDIUM",
        topics=["Array", "Two Pointers", "Sorting"],
        description="""Find all **unique** quadruplets of values `[a, b, c, d]` from four different positions whose sum equals `target`.

Sort the array, fix the first two values with nested loops (skipping repeats), and find the last two with two pointers — `O(n³)`.

**Input:** the first line is the array; the second line is `target`.

**Output:** one quadruplet per line, values in non-decreasing order, lines sorted lexicographically (compare first values, then second, …). Print `none` if there are no quadruplets.""",
        constraints=["1 <= n <= 200", "-10^9 <= a[i], target <= 10^9"],
        solve=_four_sum,
        brute=_four_sum_brute,
        examples=[("1 0 -1 0 -2 2\n0", "Three different quadruplets reach 0."), ("2 2 2 2 2\n8", "Only one unique quadruplet: 2 2 2 2.")],
        tests=lambda r: ["1 2 3\n6", "0 0 0 0\n0", "1 1 1 1\n5", "-3 -2 -1 0 0 1 2 3\n0", "1000000000 1000000000 1000000000 1000000000\n-294967296"]
        + [_four_sum_case(r, n, -10, 10) for n in (8, 12, 20)]
        + [_four_sum_case(r, 150, -50, 50)],
    ),
    Problem(
        title="Maximum Product Subarray",
        difficulty="MEDIUM",
        topics=["Array"],
        description="""Find the contiguous, non-empty subarray with the largest product and print that product.

A negative number flips the biggest product into the smallest and vice versa, so track both the maximum and the minimum product of subarrays ending at each position.

**Input:** one line of space-separated integers.

**Output:** the maximum product.""",
        constraints=["1 <= n <= 2·10^4", "-10 <= a[i] <= 10"],
        solve=_max_product,
        brute=_max_product_brute,
        examples=[("2 3 -2 4", "[2, 3] gives 6."), ("-2 0 -1", "The best you can do is 0.")],
        tests=lambda r: ["-5", "0", "-2 -3", "-2 3 -4", "0 0 0", "2 -5 -2 -4 3", "-1 -1 -1"]
        + [join(rand_ints(r, n, -4, 4)) for n in (10, 30, 120)]
        + [join(r.choices([-2, -1, 1, 2, 0], weights=[3, 3, 3, 3, 1], k=60))],
    ),
    Problem(
        title="Count Inversions",
        difficulty="HARD",
        topics=["Array", "Sorting"],
        description="""An **inversion** is a pair of positions `i < j` with `a[i] > a[j]`. Count the inversions in the array.

Checking every pair is `O(n²)`. During merge sort, whenever an element from the right half is placed before the remaining elements of the left half, it forms an inversion with each of them — that gives `O(n log n)`.

**Input:** one line of space-separated integers.

**Output:** the number of inversions.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_inversions,
        brute=_inversions_brute,
        examples=[("2 4 1 3 5", "(2, 1), (4, 1), (4, 3)."), ("1 2 3", "Sorted arrays have none.")],
        tests=lambda r: ["5", "2 1", "5 4 3 2 1", "1 1 1", "3 1 2 3 1"] + [join(rand_ints(r, n, -20, 20)) for n in (10, 40, 90)]
        + [join(rand_ints(r, 2500, -10**9, 10**9)), join(range(2000, 0, -1))],
    ),
]
