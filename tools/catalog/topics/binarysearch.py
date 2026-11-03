"""Binary Search — on sorted arrays, and on the answer."""
from bisect import bisect_left, bisect_right
from math import ceil, isqrt

from lib import Playlist, Problem, boolstr, ints, join, lines, rand_ints

PLAYLISTS = [
    Playlist(
        key="binarysearch",
        title="05 · Binary Search",
        description="Halve the search space every step, first on sorted arrays and then on the answer itself.",
        accent="#B5D8FF",
        titles=[
            "Binary Search",
            "Lower and Upper Bound",
            "Floor and Ceil in Sorted Array",
            "First and Last Occurrence",
            "Count Occurrences in Sorted Array",
            "Search in Rotated Sorted Array",
            "Find Minimum in Rotated Sorted Array",
            "Single Element in a Sorted Array",
            "Peak of a Mountain Array",
            "Integer Square Root",
            "Nth Root of a Number",
            "Koko Eating Bananas",
            "Minimum Days to Make Bouquets",
            "Smallest Divisor Within Threshold",
            "Ship Packages Within D Days",
            "Kth Missing Positive Number",
            "Aggressive Cows",
            "Allocate Books",
            "Search a 2D Matrix",
            "Median of Two Sorted Arrays",
        ],
    )
]


def _arr_x(inp):
    ls = lines(inp)
    return ints(ls[0]), int(ls[1])


# ── sorted-array lookups ─────────────────────────────────────────

def _bounds(inp):
    a, x = _arr_x(inp)
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] >= x:
            hi = mid
        else:
            lo = mid + 1
    lb = lo
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > x:
            hi = mid
        else:
            lo = mid + 1
    return f"{lb} {lo}"


def _bounds_brute(inp):
    a, x = _arr_x(inp)
    lb = next((i for i, v in enumerate(a) if v >= x), len(a))
    ub = next((i for i, v in enumerate(a) if v > x), len(a))
    return f"{lb} {ub}"


def _floor_ceil(inp):
    a, x = _arr_x(inp)
    i = bisect_right(a, x)
    j = bisect_left(a, x)
    fl = a[i - 1] if i > 0 else -1
    ce = a[j] if j < len(a) else -1
    return f"{fl} {ce}"


def _floor_ceil_brute(inp):
    a, x = _arr_x(inp)
    fl = max((v for v in a if v <= x), default=-1)
    ce = min((v for v in a if v >= x), default=-1)
    return f"{fl} {ce}"


def _first_last(inp):
    a, x = _arr_x(inp)
    i, j = bisect_left(a, x), bisect_right(a, x)
    return "-1 -1" if i == j else f"{i} {j - 1}"


def _first_last_brute(inp):
    a, x = _arr_x(inp)
    idx = [i for i, v in enumerate(a) if v == x]
    return f"{idx[0]} {idx[-1]}" if idx else "-1 -1"


def _count_sorted(inp):
    a, x = _arr_x(inp)
    return str(bisect_right(a, x) - bisect_left(a, x))


def _count_sorted_brute(inp):
    a, x = _arr_x(inp)
    return str(a.count(x))


def _rot_min(inp):
    a = ints(lines(inp)[0])
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        else:
            hi = mid
    return str(a[lo])


def _rot_min_brute(inp):
    return str(min(ints(lines(inp)[0])))


def _single(inp):
    a = ints(lines(inp)[0])
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid % 2:
            mid -= 1
        if a[mid] == a[mid + 1]:
            lo = mid + 2
        else:
            hi = mid
    return str(a[lo])


def _single_brute(inp):
    a = ints(lines(inp)[0])
    return str(next(v for v in a if a.count(v) == 1))


def _mountain(inp):
    a = ints(lines(inp)[0])
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < a[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return str(lo)


def _mountain_brute(inp):
    a = ints(lines(inp)[0])
    return str(a.index(max(a)))


# ── search on the answer ─────────────────────────────────────────

def _isqrt(inp):
    n = int(lines(inp)[0])
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid - 1
    return str(lo)


def _isqrt_brute(inp):
    return str(isqrt(int(lines(inp)[0])))


def _nth_root(inp):
    n, m = map(int, lines(inp)[0].split())
    lo, hi = 1, m
    while lo <= hi:
        mid = (lo + hi) // 2
        p = mid ** n
        if p == m:
            return str(mid)
        if p < m:
            lo = mid + 1
        else:
            hi = mid - 1
    return "-1"


def _nth_root_brute(inp):
    n, m = map(int, lines(inp)[0].split())
    r = 1
    while r ** n < m:
        r += 1
    return str(r) if r ** n == m else "-1"


def _min_true(lo, hi, ok):
    """Smallest value in [lo, hi] with ok(value) True (ok is monotone)."""
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def _koko(inp):
    piles, h = _arr_x(inp)
    return str(_min_true(1, max(piles), lambda k: sum(ceil(p / k) for p in piles) <= h))


def _koko_brute(inp):
    piles, h = _arr_x(inp)
    k = 1
    while sum(ceil(p / k) for p in piles) > h:
        k += 1
    return str(k)


def _bouquet_ok(bloom, m, k, day):
    made = run = 0
    for b in bloom:
        if b <= day:
            run += 1
            if run == k:
                made += 1
                run = 0
        else:
            run = 0
    return made >= m


def _bouquets(inp):
    ls = lines(inp)
    bloom = ints(ls[0])
    m, k = map(int, ls[1].split())
    if m * k > len(bloom):
        return "-1"
    return str(_min_true(min(bloom), max(bloom), lambda d: _bouquet_ok(bloom, m, k, d)))


def _bouquets_brute(inp):
    ls = lines(inp)
    bloom = ints(ls[0])
    m, k = map(int, ls[1].split())
    for d in sorted(set(bloom)):
        if _bouquet_ok(bloom, m, k, d):
            return str(d)
    return "-1"


def _divisor(inp):
    a, t = _arr_x(inp)
    return str(_min_true(1, max(a), lambda d: sum(ceil(x / d) for x in a) <= t))


def _divisor_brute(inp):
    a, t = _arr_x(inp)
    d = 1
    while sum(ceil(x / d) for x in a) > t:
        d += 1
    return str(d)


def _days_needed(w, cap):
    days, load = 1, 0
    for x in w:
        if load + x > cap:
            days += 1
            load = 0
        load += x
    return days


def _ship(inp):
    w, d = _arr_x(inp)
    return str(_min_true(max(w), sum(w), lambda c: _days_needed(w, c) <= d))


def _ship_brute(inp):
    w, d = _arr_x(inp)
    c = max(w)
    while _days_needed(w, c) > d:
        c += 1
    return str(c)


def _kth_missing(inp):
    a, k = _arr_x(inp)
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] - (mid + 1) < k:
            lo = mid + 1
        else:
            hi = mid
    return str(lo + k)


def _kth_missing_brute(inp):
    a, k = _arr_x(inp)
    s = set(a)
    x = 0
    while k:
        x += 1
        if x not in s:
            k -= 1
    return str(x)


def _cows_ok(stalls, k, gap):
    placed, last = 1, stalls[0]
    for s in stalls[1:]:
        if s - last >= gap:
            placed += 1
            last = s
    return placed >= k


def _cows(inp):
    stalls, k = _arr_x(inp)
    stalls.sort()
    lo, hi = 1, stalls[-1] - stalls[0]
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _cows_ok(stalls, k, mid):
            lo = mid
        else:
            hi = mid - 1
    return str(lo)


def _cows_brute(inp):
    stalls, k = _arr_x(inp)
    stalls.sort()
    best = 1
    for g in range(1, stalls[-1] - stalls[0] + 1):
        if _cows_ok(stalls, k, g):
            best = g
    return str(best)


def _students_needed(pages, cap):
    students, load = 1, 0
    for p in pages:
        if load + p > cap:
            students += 1
            load = 0
        load += p
    return students


def _books(inp):
    pages, m = _arr_x(inp)
    if m > len(pages):
        return "-1"
    return str(_min_true(max(pages), sum(pages), lambda c: _students_needed(pages, c) <= m))


def _books_brute(inp):
    pages, m = _arr_x(inp)
    n = len(pages)
    if m > n:
        return "-1"
    from functools import lru_cache

    pre = [0]
    for p in pages:
        pre.append(pre[-1] + p)

    @lru_cache(None)
    def best(i, s):  # min possible max for pages[i:] split among s students
        if s == 1:
            return pre[n] - pre[i]
        res = float("inf")
        for j in range(i + 1, n - s + 2):
            res = min(res, max(pre[j] - pre[i], best(j, s - 1)))
        return res

    return str(best(0, m))


def _matrix(inp):
    ls = lines(inp)
    r, c = map(int, ls[0].split())
    flat = [v for row in ls[1:1 + r] for v in ints(row)]
    x = int(ls[1 + r])
    lo, hi = 0, r * c - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if flat[mid] == x:
            return "true"
        if flat[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return "false"


def _matrix_brute(inp):
    ls = lines(inp)
    r, _ = map(int, ls[0].split())
    flat = [v for row in ls[1:1 + r] for v in ints(row)]
    return boolstr(int(ls[1 + r]) in flat)


def _fmt_median(num2: int) -> str:
    """num2 = 2 × median (an integer). Print with one decimal."""
    sign = "-" if num2 < 0 else ""
    q, rem = divmod(abs(num2), 2)
    return f"{sign}{q}.{5 if rem else 0}"


def _median(inp):
    ls = lines(inp)
    a, b = ints(ls[0]), ints(ls[1])
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    INF = float("inf")
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        aL = a[i - 1] if i > 0 else -INF
        aR = a[i] if i < m else INF
        bL = b[j - 1] if j > 0 else -INF
        bR = b[j] if j < n else INF
        if aL <= bR and bL <= aR:
            if (m + n) % 2:
                return _fmt_median(2 * max(aL, bL))
            return _fmt_median(max(aL, bL) + min(aR, bR))
        if aL > bR:
            hi = i - 1
        else:
            lo = i + 1
    raise AssertionError("unreachable")


def _median_brute(inp):
    ls = lines(inp)
    c = sorted(ints(ls[0]) + ints(ls[1]))
    t = len(c)
    return _fmt_median(2 * c[t // 2] if t % 2 else c[t // 2 - 1] + c[t // 2])


# ── test generators ──────────────────────────────────────────────

def _sorted_arr(r, n, lo, hi):
    return sorted(rand_ints(r, n, lo, hi))


def _arr_x_tests(r, cases):
    out = []
    for n, lo, hi in cases:
        a = _sorted_arr(r, n, lo, hi)
        x = r.choice(a) if r.random() < 0.6 else r.randint(lo - 2, hi + 2)
        out.append(f"{join(a)}\n{x}")
    return out


def _rotated(r, n, lo, hi):
    a = sorted(r.sample(range(lo, hi + 1), n))
    k = r.randrange(n)
    return a[k:] + a[:k]


def _single_case(r, pairs):
    vals = sorted(r.sample(range(-1000, 1000), pairs + 1))
    lone = r.choice(vals)
    out = []
    for v in vals:
        out += [v] if v == lone else [v, v]
    return join(out)


def _mountain_case(r, n):
    peak = r.randrange(1, n - 1)
    vals = sorted(r.sample(range(1, 10 * n), n))
    top = vals[-1]
    rest = vals[:-1]
    r.shuffle(rest)
    left = sorted(rest[:peak])
    right = sorted(rest[peak:], reverse=True)
    return join(left + [top] + right)


def _matrix_case(r, rows, cols, present):
    flat = sorted(r.sample(range(-500, 500), rows * cols))
    x = r.choice(flat) if present else r.choice([v for v in range(-502, 502) if v not in flat])
    body = "\n".join(join(flat[i * cols:(i + 1) * cols]) for i in range(rows))
    return f"{rows} {cols}\n{body}\n{x}"


PROBLEMS = [
    Problem(
        title="Lower and Upper Bound",
        difficulty="EASY",
        topics=["Binary Search", "Array"],
        description="""Given a sorted array (it may contain duplicates) and a value `x`, find:

- the **lower bound**: the first index whose value is `>= x`, and
- the **upper bound**: the first index whose value is `> x`.

If no such index exists, use `n`, the length of the array.

**Input:** the sorted array on the first line, `x` on the second.

**Output:** the lower bound and the upper bound, separated by a space.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i], x <= 10^9"],
        solve=_bounds,
        brute=_bounds_brute,
        examples=[("1 2 2 2 5 8\n2", "The first 2 is at index 1; the first value above 2 (5) is at index 4."), ("3 5 9\n10", "Every value is smaller than 10, so both are n = 3.")],
        tests=lambda r: ["5\n5", "5\n1", "5\n9", "1 1 1 1\n1", "2 4 6 8\n5", "2 4 6 8\n-3"]
        + _arr_x_tests(r, [(20, 0, 10), (40, -20, 20), (60, 0, 5)])
        + [f"{join(_sorted_arr(r, 3000, -10**6, 10**6))}\n0"],
    ),
    Problem(
        title="Floor and Ceil in Sorted Array",
        difficulty="EASY",
        topics=["Binary Search", "Array"],
        description="""Given a sorted array and a value `x`, print:

- the **floor**: the largest value in the array that is `<= x`, and
- the **ceil**: the smallest value in the array that is `>= x`.

Print `-1` for whichever one doesn't exist.

**Input:** the sorted array on the first line, `x` on the second. All values are non-negative.

**Output:** the floor and the ceil, separated by a space.""",
        constraints=["1 <= n <= 10^5", "0 <= a[i], x <= 10^9"],
        solve=_floor_ceil,
        brute=_floor_ceil_brute,
        examples=[("3 4 4 7 8 10\n5", "4 is the largest value ≤ 5 and 7 the smallest ≥ 5."), ("3 4 4 7 8 10\n8", "8 itself is both.")],
        tests=lambda r: ["5\n5", "5\n2", "5\n7", "1 3 5\n0", "1 3 5\n6", "2 2 2\n2"]
        + [(lambda a: f"{join(a)}\n{r.randint(0, 60)}")(_sorted_arr(r, n, 0, 50)) for n in (15, 30, 45)]
        + [f"{join(_sorted_arr(r, 3000, 0, 10**6))}\n500000"],
    ),
    Problem(
        title="First and Last Occurrence",
        difficulty="EASY",
        topics=["Binary Search", "Array"],
        description="""Given a sorted array and a target `x`, print the index of the **first** and **last** occurrence of `x`. If `x` isn't in the array, print `-1 -1`.

Aim for `O(log n)`: run two binary searches, one that keeps moving left after a match and one that keeps moving right.

**Input:** the sorted array on the first line, `x` on the second.

**Output:** the first and last index of `x`, separated by a space.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i], x <= 10^9"],
        solve=_first_last,
        brute=_first_last_brute,
        examples=[("5 7 7 8 8 8 10\n8", "8 occupies indices 3 to 5."), ("5 7 7 8 8 10\n6", "6 isn't present.")],
        tests=lambda r: ["4\n4", "4\n3", "2 2 2 2 2\n2", "1 2 3\n1", "1 2 3\n3", "1 2 3\n4"]
        + _arr_x_tests(r, [(20, 0, 6), (40, -5, 5), (60, 0, 30)])
        + [f"{join(_sorted_arr(r, 3000, 0, 300))}\n150"],
    ),
    Problem(
        title="Count Occurrences in Sorted Array",
        difficulty="EASY",
        topics=["Binary Search", "Array"],
        description="""Given a **sorted** array and a value `x`, count how many times `x` appears.

A linear scan works, but the array is sorted: find the first and last position of `x` with binary search and subtract, for `O(log n)`.

**Input:** the sorted array on the first line, `x` on the second.

**Output:** how many times `x` appears (possibly 0).""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i], x <= 10^9"],
        solve=_count_sorted,
        brute=_count_sorted_brute,
        examples=[("2 2 3 3 3 3 4\n3", "3 appears four times."), ("1 1 2 2 2 2 3\n5", "5 never appears.")],
        tests=lambda r: ["9\n9", "9\n1", "7 7 7 7 7 7\n7", "1 2 3 4\n2"]
        + _arr_x_tests(r, [(25, 0, 5), (50, -3, 3), (80, 0, 20)])
        + [f"{join(_sorted_arr(r, 3000, 0, 40))}\n17"],
    ),
    Problem(
        title="Find Minimum in Rotated Sorted Array",
        difficulty="MEDIUM",
        topics=["Binary Search", "Array"],
        description="""An array of **distinct** integers was sorted in increasing order and then rotated at some unknown pivot, so `[1, 2, 3, 4, 5]` might become `[4, 5, 1, 2, 3]`. It may also not be rotated at all. Find the smallest element in `O(log n)`.

Compare the middle element with the last one: if it's bigger, the minimum lies to the right of the middle.

**Input:** one line with the rotated array.

**Output:** the minimum value.""",
        constraints=["1 <= n <= 10^5", "All values are distinct"],
        solve=_rot_min,
        brute=_rot_min_brute,
        examples=[("4 5 6 7 0 1 2", "The array was rotated after 7; the minimum is 0."), ("11 13 15 17", "Not rotated, so the first element is the minimum.")],
        tests=lambda r: ["5", "2 1", "1 2", "3 1 2", "2 3 1"]
        + [join(_rotated(r, n, -100, 100)) for n in (10, 25, 50, 80)]
        + [join(_rotated(r, 3000, -10**6, 10**6))],
    ),
    Problem(
        title="Single Element in a Sorted Array",
        difficulty="MEDIUM",
        topics=["Binary Search", "Array"],
        description="""In a sorted array, every value appears exactly **twice** except one value that appears once. Find that value in `O(log n)`.

Before the single element, each pair starts at an even index; after it, pairs start at odd indices. Binary search on which side of the break the middle falls.

**Input:** one line with the sorted array (its length is odd).

**Output:** the value that appears once.""",
        constraints=["1 <= n <= 10^5", "n is odd"],
        solve=_single,
        brute=_single_brute,
        examples=[("1 1 2 3 3 4 4 8 8", "Every value is paired except 2."), ("3 3 7 7 10 11 11", "10 is alone.")],
        tests=lambda r: ["42", "1 2 2", "1 1 2", "-5 -5 0 3 3"]
        + [_single_case(r, p) for p in (3, 8, 15, 30)]
        + [_single_case(r, 999)],
    ),
    Problem(
        title="Peak of a Mountain Array",
        difficulty="MEDIUM",
        topics=["Binary Search", "Array"],
        description="""A **mountain array** strictly increases up to a single peak and then strictly decreases. The peak is never the first or last element. Find the index of the peak in `O(log n)`.

If `a[mid] < a[mid + 1]` you're still climbing, so the peak is to the right; otherwise it's at `mid` or to its left.

**Input:** one line with the mountain array.

**Output:** the index of the peak (0-based).""",
        constraints=["3 <= n <= 10^5", "The array is a valid mountain"],
        solve=_mountain,
        brute=_mountain_brute,
        examples=[("0 2 5 9 4 1", "9 at index 3 is the highest point."), ("1 3 2", "The peak 3 is at index 1.")],
        tests=lambda r: ["1 2 1", "1 9 8 7 6 5", "1 2 3 4 5 0", "-3 -1 -2"]
        + [_mountain_case(r, n) for n in (5, 12, 30, 70)]
        + [_mountain_case(r, 3000)],
    ),
    Problem(
        title="Integer Square Root",
        difficulty="EASY",
        topics=["Binary Search", "Math"],
        description="""Given a non-negative integer `n`, print `⌊√n⌋`, the largest integer whose square is at most `n`. Don't use a built-in square root.

Binary search over `0 … n` for the last value `m` with `m × m <= n`.

**Input:** one integer `n`.

**Output:** the integer square root of `n`.""",
        constraints=["0 <= n <= 10^18"],
        solve=_isqrt,
        brute=_isqrt_brute,
        examples=[("28", "5² = 25 ≤ 28 < 36 = 6²."), ("49", "A perfect square: 7.")],
        tests=lambda r: ["0", "1", "2", "3", "4", "99", "100", "1000000000000000000", "999999999999999999"]
        + [str(r.randint(0, 10**18)) for _ in range(3)],
    ),
    Problem(
        title="Nth Root of a Number",
        difficulty="MEDIUM",
        topics=["Binary Search", "Math"],
        description="""Given `n` and `m`, find the integer `x` with `x^n = m`. If no such integer exists, print `-1`.

Binary search `x` in `1 … m`. Compute `x^n` with integer arithmetic so precision isn't an issue.

**Input:** one line with `n` and `m`.

**Output:** the integer `n`-th root of `m`, or `-1`.""",
        constraints=["1 <= n <= 30", "1 <= m <= 10^9"],
        solve=_nth_root,
        brute=_nth_root_brute,
        examples=[("3 27", "3³ = 27."), ("4 69", "2⁴ = 16 and 3⁴ = 81, so 69 has no integer 4th root.")],
        tests=lambda r: ["1 1", "1 999999937", "2 1", "30 1", "30 1073741824", "2 999950884", "3 1000000000", "5 32", "9 1000000000"]
        + [(lambda n, x: f"{n} {x ** n}")(*((lambda n: (n, r.randint(1, int(10 ** (9 / n)))))(r.randint(2, 6)))) for _ in range(2)]
        + [f"{r.randint(2, 6)} {r.randint(1, 10**9)}"],
    ),
    Problem(
        title="Koko Eating Bananas",
        difficulty="MEDIUM",
        topics=["Binary Search", "Array"],
        description="""There are piles of bananas, and the guard returns in `h` hours. Each hour you pick one pile and eat up to `k` bananas from it. If the pile has fewer than `k`, you finish it and wait out the rest of that hour.

Find the **smallest** eating speed `k` that lets you finish every pile within `h` hours.

The hours needed only go down as `k` grows, so binary search on `k` between 1 and the largest pile.

**Input:** the pile sizes on the first line, `h` on the second.

**Output:** the minimum integer speed `k`.""",
        constraints=["1 <= n <= 10^4", "n <= h <= 10^9", "1 <= pile <= 10^9"],
        solve=_koko,
        brute=_koko_brute,
        examples=[("3 6 7 11\n8", "At speed 4: 1 + 2 + 2 + 3 = 8 hours."), ("30 11 23 4 20\n5", "With one hour per pile, k must be the largest pile, 30.")],
        tests=lambda r: ["1\n1", "5\n5", "5\n1", "1 1 1 1\n4", "10 10 10\n100"]
        + [(lambda p: f"{join(p)}\n{r.randint(len(p), 3 * len(p))}")(rand_ints(r, n, 1, 60)) for n in (5, 10, 20)]
        + [(lambda p: f"{join(p)}\n{r.randint(len(p), 2 * len(p))}")(rand_ints(r, 30, 1, 200))],
    ),
    Problem(
        title="Minimum Days to Make Bouquets",
        difficulty="MEDIUM",
        topics=["Binary Search", "Array"],
        description="""A garden row has flowers where flower `i` blooms on day `bloom[i]`. A bouquet needs `k` **adjacent** bloomed flowers, and each flower can be used in only one bouquet. Find the minimum day by which you can make `m` bouquets, or print `-1` if it's impossible.

**Input:** the bloom days on the first line, then `m` and `k` on the second line.

**Output:** the minimum number of days, or `-1`.""",
        constraints=["1 <= n <= 10^5", "1 <= bloom[i] <= 10^9", "1 <= m, k <= 10^6"],
        solve=_bouquets,
        brute=_bouquets_brute,
        examples=[("7 7 7 7 13 11 12 7\n2 3", "By day 12, flowers 0–2 and 5–7 have all bloomed."), ("1 10 3 10 2\n3 2", "Six flowers are needed but there are only five.")],
        tests=lambda r: ["5\n1 1", "5\n1 2", "1 2 3 4\n2 2", "4 3 2 1\n1 4", "9 1 9 1 9\n2 1"]
        + [f"{join(rand_ints(r, n, 1, 30))}\n{r.randint(1, 4)} {r.randint(1, 3)}" for n in (8, 15, 25)]
        + [f"{join(rand_ints(r, 40, 1, 100))}\n3 4"],
    ),
    Problem(
        title="Smallest Divisor Within Threshold",
        difficulty="MEDIUM",
        topics=["Binary Search", "Array"],
        description="""Pick a positive integer divisor `d`, divide every array element by it and round each result **up**. Find the smallest `d` for which the sum of these rounded results is at most `threshold`.

Bigger divisors only shrink the sum, so binary search `d` between 1 and the largest element.

**Input:** the array on the first line, `threshold` on the second.

**Output:** the smallest valid divisor.""",
        constraints=["1 <= n <= 5 * 10^4", "1 <= a[i] <= 10^6", "n <= threshold <= 10^6"],
        solve=_divisor,
        brute=_divisor_brute,
        examples=[("1 2 5 9\n6", "With d = 5: 1 + 1 + 1 + 2 = 5 ≤ 6; d = 4 gives 7."), ("44 22 33 11 1\n5", "Only d = 44 brings every term down to 1.")],
        tests=lambda r: ["1\n1", "10\n1", "10\n10", "3 3 3\n9", "100 1\n2"]
        + [(lambda a: f"{join(a)}\n{r.randint(len(a), 4 * len(a))}")(rand_ints(r, n, 1, 80)) for n in (6, 12, 25)]
        + [(lambda a: f"{join(a)}\n{r.randint(len(a), 2 * len(a))}")(rand_ints(r, 40, 1, 300))],
    ),
    Problem(
        title="Ship Packages Within D Days",
        difficulty="MEDIUM",
        topics=["Binary Search", "Array"],
        description="""Packages must ship **in the given order**. Each day you load packages onto the ship until adding the next one would exceed its capacity. Find the minimum capacity that ships everything within `d` days.

The capacity is at least the heaviest package and at most the total weight. Binary search between those, simulating the days for each guess.

**Input:** the package weights on the first line, `d` on the second.

**Output:** the minimum ship capacity.""",
        constraints=["1 <= d <= n <= 5 * 10^4", "1 <= weight <= 500"],
        solve=_ship,
        brute=_ship_brute,
        examples=[("1 2 3 4 5 6 7 8 9 10\n5", "Capacity 15: [1–5], [6, 7], [8], [9], [10]."), ("3 2 2 4 1 4\n3", "Capacity 6: [3, 2], [2, 4], [1, 4].")],
        tests=lambda r: ["7\n1", "1 1 1 1\n4", "1 1 1 1\n1", "10 1 1 1\n2", "5 5 5 5 5\n3"]
        + [(lambda w: f"{join(w)}\n{r.randint(1, len(w))}")(rand_ints(r, n, 1, 30)) for n in (8, 15, 25)]
        + [f"{join(rand_ints(r, 40, 1, 100))}\n7"],
    ),
    Problem(
        title="Kth Missing Positive Number",
        difficulty="EASY",
        topics=["Binary Search", "Array"],
        description="""Given a strictly increasing array of positive integers and a number `k`, find the `k`-th positive integer that is **missing** from the array.

At index `i`, exactly `a[i] - (i + 1)` numbers are missing before `a[i]`. Binary search for where that count reaches `k`.

**Input:** the array on the first line, `k` on the second.

**Output:** the `k`-th missing positive integer.""",
        constraints=["1 <= n <= 10^5", "1 <= a[i] <= 10^9", "1 <= k <= 10^9"],
        solve=_kth_missing,
        brute=_kth_missing_brute,
        examples=[("2 3 4 7 11\n5", "Missing: 1, 5, 6, 8, 9, 10… the 5th is 9."), ("1 2 3 4\n2", "Nothing is missing up to 4; the missing numbers are 5, 6, 7… so the 2nd is 6.")],
        tests=lambda r: ["1\n1", "5\n1", "5\n4", "5\n5", "1 2 3\n100"]
        + [(lambda a: f"{join(a)}\n{r.randint(1, 40)}")(sorted(r.sample(range(1, 80), n))) for n in (5, 15, 30)]
        + [f"{join(sorted(r.sample(range(1, 4000), 1500)))}\n700"],
    ),
    Problem(
        title="Aggressive Cows",
        difficulty="HARD",
        topics=["Binary Search", "Sorting"],
        description="""Stalls stand at the given positions along a line (in no particular order). Place `k` cows in distinct stalls so that the **minimum distance** between any two cows is as large as possible. Print that largest minimum distance.

For a candidate distance `g`, greedily place cows left to right whenever the gap is at least `g`. If `k` cows fit, try a bigger `g`.

**Input:** the stall positions on the first line, `k` on the second.

**Output:** the largest possible minimum distance.""",
        constraints=["2 <= k <= n <= 10^5", "0 <= position <= 10^9", "Positions are distinct"],
        solve=_cows,
        brute=_cows_brute,
        examples=[("0 3 4 7 10 9\n4", "Cows at 0, 3, 7 and 10 are at least 3 apart."), ("4 2 1 3 6\n2", "Put them at the ends, 1 and 6.")],
        tests=lambda r: ["1 2\n2", "0 100\n2", "1 2 3 4 5\n5", "1 2 3 4 5\n3", "10 1 7 4\n3"]
        + [f"{join(r.sample(range(0, 200), n))}\n{r.randint(2, n)}" for n in (6, 12, 25)]
        + [f"{join(r.sample(range(0, 600), 60))}\n9"],
    ),
    Problem(
        title="Allocate Books",
        difficulty="HARD",
        topics=["Binary Search", "Array"],
        description="""Books are arranged in order, with the given page counts. Split them among `m` students so that each student gets a **contiguous** block of at least one book and every book goes to someone. Minimize the largest number of pages any one student reads.

Print that minimum, or `-1` if there are fewer books than students.

**Input:** the page counts on the first line, `m` on the second.

**Output:** the minimum possible maximum pages, or `-1`.""",
        constraints=["1 <= n, m <= 10^5", "1 <= pages <= 10^4"],
        solve=_books,
        brute=_books_brute,
        examples=[("12 34 67 90\n2", "[12, 34, 67] and [90]: the max is 113."), ("15 17 20\n4", "Four students but only three books.")],
        tests=lambda r: ["10\n1", "10\n2", "5 5 5 5\n4", "5 5 5 5\n1", "1 100 1\n2"]
        + [f"{join(rand_ints(r, n, 1, 50))}\n{r.randint(1, n)}" for n in (6, 10, 14)]
        + [f"{join(rand_ints(r, 18, 1, 200))}\n5"],
    ),
    Problem(
        title="Search a 2D Matrix",
        difficulty="MEDIUM",
        topics=["Binary Search", "Matrix"],
        description="""Each row of the matrix is sorted, and the first value of each row is greater than the last value of the row above it. Decide whether `x` is in the matrix in `O(log(r·c))`.

Read row by row, the matrix is one sorted list, so binary search on index `i` and look at cell `(i / c, i % c)`.

**Input:** `r c` on the first line, then `r` rows of `c` integers, then `x` on the last line.

**Output:** `true` if `x` is in the matrix, otherwise `false`.""",
        constraints=["1 <= r, c <= 100", "-10^4 <= values, x <= 10^4"],
        solve=_matrix,
        brute=_matrix_brute,
        examples=[("3 4\n1 3 5 7\n10 11 16 20\n23 30 34 60\n3", "3 is in the first row."), ("3 4\n1 3 5 7\n10 11 16 20\n23 30 34 60\n13", "13 would sit between 11 and 16 but isn't there.")],
        tests=lambda r: ["1 1\n5\n5", "1 1\n5\n4", "1 3\n1 2 3\n3", "3 1\n1\n2\n3\n0"]
        + [_matrix_case(r, rr, cc, p) for rr, cc, p in ((3, 3, True), (4, 5, False), (6, 4, True), (5, 7, False))]
        + [_matrix_case(r, 25, 30, True)],
    ),
    Problem(
        title="Median of Two Sorted Arrays",
        difficulty="HARD",
        topics=["Binary Search", "Array"],
        description="""Given two sorted arrays, find the median of all their elements combined. If the total count is even, the median is the average of the two middle values.

Merging works in `O(n + m)`. The `O(log(min(n, m)))` approach binary searches a cut in the smaller array so that the left halves of both arrays together hold exactly half the elements, and everything on the left is `<=` everything on the right.

**Input:** the first sorted array on line 1, the second on line 2. Both are non-empty.

**Output:** the median with exactly one decimal place (for example `2.0` or `2.5`).""",
        constraints=["1 <= n, m <= 10^5", "-10^6 <= values <= 10^6"],
        solve=_median,
        brute=_median_brute,
        examples=[("1 3\n2", "Combined [1, 2, 3], so the median is 2."), ("1 2\n3 4", "Combined [1, 2, 3, 4]: (2 + 3) / 2 = 2.5.")],
        tests=lambda r: ["5\n5", "1\n2", "-5 -3\n-4", "1 1 1\n1 1 1", "1 2 3 4 5\n6 7 8 9 10", "-7\n-2 -1 0"]
        + [f"{join(_sorted_arr(r, a, -50, 50))}\n{join(_sorted_arr(r, b, -50, 50))}" for a, b in ((3, 7), (10, 1), (12, 13))]
        + [f"{join(_sorted_arr(r, 1500, -10**6, 10**6))}\n{join(_sorted_arr(r, 1201, -10**6, 10**6))}"],
    ),
]
