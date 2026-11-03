"""Sorting — classic algorithms and sorting-based tricks."""
from collections import Counter

from lib import Playlist, Problem, boolstr, ints, join, lines, rand_ints

PLAYLISTS = [
    Playlist(
        key="sorting",
        title="02 · Sorting",
        description="Implement the classic sorts yourself, then use ordering to solve problems.",
        accent="#B5D8FF",
        titles=[
            "Check if Array Is Sorted",
            "Selection Sort",
            "Bubble Sort",
            "Insertion Sort",
            "Merge Sort",
            "Quick Sort",
            "Counting Sort",
            "Sort Array by Parity",
            "Sort 0s 1s and 2s",
            "Sort by Frequency",
        ],
    )
]


def _arr(inp):
    return ints(lines(inp)[0])


def _sorted(inp):
    return join(sorted(_arr(inp)))


def _insertion(inp):
    a = _arr(inp)
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return join(a)


def _counting(inp):
    a = _arr(inp)
    cnt = [0] * 1001
    for x in a:
        cnt[x] += 1
    return join(v for v in range(1001) for _ in range(cnt[v]))


def _is_sorted(inp):
    a = _arr(inp)
    return boolstr(all(a[i] <= a[i + 1] for i in range(len(a) - 1)))


def _dutch(inp):
    a = _arr(inp)
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]
            lo += 1
            mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]
            hi -= 1
    return join(a)


def _by_freq(inp):
    a = _arr(inp)
    c = Counter(a)
    return join(sorted(a, key=lambda x: (-c[x], x)))


def _by_freq_brute(inp):
    a = _arr(inp)
    out = []
    for v in sorted(set(a), key=lambda v: (-a.count(v), v)):
        out += [v] * a.count(v)
    return join(out)


def _parity(inp):
    a = _arr(inp)
    return join([x for x in a if x % 2 == 0] + [x for x in a if x % 2])


def _rand_lines(r, sizes, lo, hi):
    return [join(rand_ints(r, n, lo, hi)) for n in sizes]


def _sort_tests(r):
    return ["5", "2 1", "1 2 3 4 5", "5 4 3 2 1", "3 3 3 3", "-5 0 -5 7 -100000 100000", "0 -1"] + _rand_lines(r, [10, 50], -1000, 1000) + [
        join(rand_ints(r, 2000, -10**5, 10**5))
    ]


SORT_DESC = """Sort the array in non-decreasing order **by implementing {name} yourself** (don't call a built-in sort — the point is the algorithm).

{how}

**Input:** one line of space-separated integers.

**Output:** the sorted integers, space-separated."""


PROBLEMS = [
    Problem(
        title="Check if Array Is Sorted",
        difficulty="EASY",
        topics=["Array", "Sorting"],
        description="""Print `true` if the array is sorted in non-decreasing order (each element is at most the next one), otherwise `false`. Equal neighbours are allowed.

**Input:** one line of space-separated integers.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_is_sorted,
        examples=[("1 2 2 5 9", "Every element is ≤ the next."), ("3 4 1 6", "4 > 1 breaks the order.")],
        tests=lambda r: ["7", "1 1 1", "2 1", "1 2", "-3 -2 -2 0", "5 4 3 2 1", "1 2 3 4 3"]
        + [join(sorted(rand_ints(r, 300, -10**9, 10**9))), join(rand_ints(r, 30, 0, 5))],
    ),
    Problem(
        title="Insertion Sort",
        difficulty="EASY",
        topics=["Sorting", "Array"],
        description=SORT_DESC.format(
            name="insertion sort",
            how="Insertion sort grows a sorted prefix one element at a time: take the next element and shift larger elements of the prefix one step right until its slot opens up. It's `O(n²)` in general but very fast on nearly-sorted input.",
        ),
        constraints=["1 <= n <= 2000", "-10^5 <= a[i] <= 10^5"],
        solve=_insertion,
        brute=_sorted,
        examples=[("12 11 13 5 6", "Insert 11 before 12, keep 13, then slide 5 and 6 into place."), ("1 2 3", "Already sorted — nothing moves.")],
        tests=_sort_tests,
    ),
    Problem(
        title="Counting Sort",
        difficulty="EASY",
        topics=["Sorting", "Array"],
        description="""All values are small (between 0 and 1000), so you can sort without comparing elements: count how many times each value appears, then write each value out that many times. This runs in `O(n + k)` where `k` is the value range.

**Input:** one line of space-separated integers, each between 0 and 1000.

**Output:** the sorted integers, space-separated.""",
        constraints=["1 <= n <= 10^5", "0 <= a[i] <= 1000"],
        solve=_counting,
        brute=_sorted,
        examples=[("4 2 2 8 3 3 1", "Counts: 1×1, 2×2, 3×2, 4×1, 8×1."), ("0 1000 0", "Zeros first, then 1000.")],
        tests=lambda r: ["5", "0", "1000 999 998", "7 7 7 7", "1 2 3"] + _rand_lines(r, [20, 100], 0, 1000) + [join(rand_ints(r, 5000, 0, 1000)), join(rand_ints(r, 40, 0, 3))],
    ),
    Problem(
        title="Sort Array by Parity",
        difficulty="EASY",
        topics=["Array", "Two Pointers"],
        description="""Rearrange the array so that every even number comes before every odd number. Keep the **original relative order** within the evens and within the odds (a stable partition).

**Input:** one line of space-separated integers.

**Output:** the rearranged integers, space-separated.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_parity,
        examples=[("3 1 2 4", "Evens 2, 4 keep their order, then odds 3, 1."), ("-3 -2 0 5", "-2 and 0 are even; -3 and 5 odd.")],
        tests=lambda r: ["1", "2", "1 3 5", "2 4 6", "0 0 1 1", "7 8 9 10 11 12"] + _rand_lines(r, [15, 200], -100, 100) + [join(rand_ints(r, 2000, -10**9, 10**9))],
    ),
    Problem(
        title="Sort 0s 1s and 2s",
        difficulty="MEDIUM",
        topics=["Array", "Sorting", "Two Pointers"],
        description="""The array contains only 0s, 1s and 2s. Sort it in a **single pass** with constant extra space.

Keep three regions with pointers `low`, `mid` and `high`: everything before `low` is 0, between `low` and `mid` is 1, after `high` is 2. Look at `a[mid]` and swap it into the right region (the Dutch national flag algorithm).

**Input:** one line of space-separated values, each 0, 1 or 2.

**Output:** the sorted values, space-separated.""",
        constraints=["1 <= n <= 10^5"],
        solve=_dutch,
        brute=_sorted,
        examples=[("2 0 2 1 1 0", "Two 0s, two 1s, two 2s."), ("1 0", "Just swap.")],
        tests=lambda r: ["0", "2", "2 2 2", "0 0 0 1", "2 1 0", "1 1 1 1"] + _rand_lines(r, [10, 60, 300], 0, 2) + [join(rand_ints(r, 8000, 0, 2))],
    ),
    Problem(
        title="Sort by Frequency",
        difficulty="MEDIUM",
        topics=["Sorting", "Hash Map"],
        description="""Sort the array so that values that appear **more often come first**. If two values appear the same number of times, the **smaller value comes first**. Equal values stay grouped together.

**Input:** one line of space-separated integers.

**Output:** the reordered integers, space-separated.""",
        constraints=["1 <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_by_freq,
        brute=_by_freq_brute,
        examples=[("4 6 2 6 4 4", "4 appears 3 times, 6 twice, 2 once."), ("3 1 2", "All appear once, so order by value.")],
        tests=lambda r: ["5", "1 1 2 2", "2 2 1 1", "-1 -1 3 3 3 -2", "9 8 7 6"] + _rand_lines(r, [20, 80], -5, 5) + [join(rand_ints(r, 3000, -50, 50)), join(rand_ints(r, 40, -10**9, 10**9))],
    ),
]
