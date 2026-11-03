"""Heaps & priority queues — top-k, streaming and greedy merging."""
import heapq
from collections import Counter

from lib import Playlist, Problem, boolstr, ints, join, lines, rand_ints

PLAYLISTS = [
    Playlist(
        key="heaps",
        title="15 · Heaps & Priority Queues",
        description="Use a heap whenever you repeatedly need the smallest or largest item — top-k, streams and greedy merges.",
        accent="#FFC8DD",
        titles=[
            "Kth Largest Element in an Array",
            "Kth Smallest Element",
            "Last Stone Weight",
            "Minimum Cost to Connect Ropes",
            "Kth Largest in a Stream",
            "Sort a Nearly Sorted Array",
            "Merge K Sorted Arrays",
            "Top K Frequent Elements",
            "K Closest Points to Origin",
            "Hand of Straights",
            "Task Scheduler",
            "Find Median from Data Stream",
        ],
    )
]


def _arr_k(inp):
    ls = lines(inp)
    return ints(ls[0]), int(ls[1])


def _kth_smallest(inp):
    a, k = _arr_k(inp)
    heap = []  # max-heap of the k smallest, stored negated
    for x in a:
        heapq.heappush(heap, -x)
        if len(heap) > k:
            heapq.heappop(heap)
    return str(-heap[0])


def _kth_smallest_brute(inp):
    a, k = _arr_k(inp)
    return str(sorted(a)[k - 1])


def _merge_k(inp):
    ls = lines(inp)
    k = int(ls[0])
    arrays = [ints(ls[1 + i]) for i in range(k)]
    heap = [(a[0], i, 0) for i, a in enumerate(arrays) if a]
    heapq.heapify(heap)
    out = []
    while heap:
        v, i, j = heapq.heappop(heap)
        out.append(v)
        if j + 1 < len(arrays[i]):
            heapq.heappush(heap, (arrays[i][j + 1], i, j + 1))
    return join(out)


def _merge_k_brute(inp):
    ls = lines(inp)
    k = int(ls[0])
    return join(sorted(x for i in range(k) for x in ints(ls[1 + i])))


def _top_k(inp):
    a, k = _arr_k(inp)
    c = Counter(a)
    best = heapq.nsmallest(k, c.items(), key=lambda kv: (-kv[1], kv[0]))
    return join(v for v, _ in best)


def _top_k_brute(inp):
    a, k = _arr_k(inp)
    vals = sorted(set(a), key=lambda v: (-a.count(v), v))
    return join(vals[:k])


def _points(inp):
    ls = lines(inp)
    n, k = map(int, ls[0].split())
    pts = [tuple(ints(ls[1 + i])) for i in range(n)]
    best = heapq.nsmallest(k, pts, key=lambda p: (p[0] * p[0] + p[1] * p[1], p[0], p[1]))
    return "\n".join(join(p) for p in best)


def _points_brute(inp):
    ls = lines(inp)
    n, k = map(int, ls[0].split())
    pts = sorted((tuple(ints(ls[1 + i])) for i in range(n)), key=lambda p: (p[0] ** 2 + p[1] ** 2, p))
    return "\n".join(join(p) for p in pts[:k])


def _last_stone(inp):
    heap = [-x for x in ints(lines(inp)[0])]
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = -heapq.heappop(heap), -heapq.heappop(heap)
        if a != b:
            heapq.heappush(heap, -(a - b))
    return str(-heap[0] if heap else 0)


def _last_stone_brute(inp):
    s = ints(lines(inp)[0])
    while len(s) > 1:
        s.sort()
        a, b = s.pop(), s.pop()
        if a != b:
            s.append(a - b)
    return str(s[0] if s else 0)


def _ropes(inp):
    heap = ints(lines(inp)[0])
    heapq.heapify(heap)
    cost = 0
    while len(heap) > 1:
        s = heapq.heappop(heap) + heapq.heappop(heap)
        cost += s
        heapq.heappush(heap, s)
    return str(cost)


def _ropes_brute(inp):
    s = ints(lines(inp)[0])
    cost = 0
    while len(s) > 1:
        s.sort()
        x = s.pop(0) + s.pop(0)
        cost += x
        s.append(x)
    return str(cost)


def _stream_ops(inp):
    ls = lines(inp)
    k, q = int(ls[0]), int(ls[1])
    return k, [int(ls[2 + i].split()[1]) for i in range(q)]


def _kth_stream(inp):
    k, adds = _stream_ops(inp)
    heap, out = [], []
    for x in adds:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
        out.append(heap[0] if len(heap) == k else -1)
    return "\n".join(map(str, out))


def _kth_stream_brute(inp):
    k, adds = _stream_ops(inp)
    seen, out = [], []
    for x in adds:
        seen.append(x)
        out.append(sorted(seen, reverse=True)[k - 1] if len(seen) >= k else -1)
    return "\n".join(map(str, out))


def _fmt_median(twice):
    # twice = 2 × median, an integer; print with exactly one decimal place
    sign = "-" if twice < 0 else ""
    t = abs(twice)
    return f"{sign}{t // 2}.{5 if t % 2 else 0}"


def _median(inp):
    ls = lines(inp)
    q = int(ls[0])
    lo, hi, out = [], [], []  # lo: max-heap (negated), hi: min-heap
    for i in range(q):
        op = ls[1 + i].split()
        if op[0] == "add":
            x = int(op[1])
            heapq.heappush(lo, -x)
            heapq.heappush(hi, -heapq.heappop(lo))
            if len(hi) > len(lo):
                heapq.heappush(lo, -heapq.heappop(hi))
        else:
            twice = -lo[0] * 2 if len(lo) > len(hi) else -lo[0] + hi[0]
            out.append(_fmt_median(twice))
    return "\n".join(out)


def _median_brute(inp):
    ls = lines(inp)
    q = int(ls[0])
    vals, out = [], []
    for i in range(q):
        op = ls[1 + i].split()
        if op[0] == "add":
            vals.append(int(op[1]))
        else:
            s = sorted(vals)
            n = len(s)
            twice = s[n // 2] * 2 if n % 2 else s[n // 2 - 1] + s[n // 2]
            out.append(_fmt_median(twice))
    return "\n".join(out)


def _task(inp):
    ls = lines(inp)
    tasks, n = ls[0].split(), int(ls[1])
    counts = Counter(tasks).values()
    top = max(counts)
    ties = sum(1 for c in counts if c == top)
    return str(max(len(tasks), (top - 1) * (n + 1) + ties))


def _task_brute(inp):
    ls = lines(inp)
    tasks, n = ls[0].split(), int(ls[1])
    left = Counter(tasks)
    ready = {t: 0 for t in left}  # earliest time each task type can run
    time = 0
    while left:
        cands = [t for t in left if ready[t] <= time]
        if cands:
            t = max(cands, key=lambda x: (left[x], x))
            left[t] -= 1
            if not left[t]:
                del left[t]
            ready[t] = time + n + 1
        time += 1
    return str(time)


def _hand(inp):
    ls = lines(inp)
    a, g = ints(ls[0]), int(ls[1])
    if len(a) % g:
        return "false"
    c = Counter(a)
    heap = list(c)
    heapq.heapify(heap)
    while heap:
        first = heap[0]
        for v in range(first, first + g):
            if c[v] == 0:
                return "false"
            c[v] -= 1
            if c[v] == 0:
                if v != heap[0]:
                    return "false"
                heapq.heappop(heap)
    return "true"


def _hand_brute(inp):
    ls = lines(inp)
    a, g = sorted(ints(ls[0])), int(ls[1])
    while a:
        first = a[0]
        for v in range(first, first + g):
            if v not in a:
                return "false"
            a.remove(v)
    return "true"


def _nearly(inp):
    a, k = _arr_k(inp)
    heap, out = [], []
    for x in a:
        heapq.heappush(heap, x)
        if len(heap) > k:
            out.append(heapq.heappop(heap))
    while heap:
        out.append(heapq.heappop(heap))
    return join(out)


def _nearly_brute(inp):
    a, _ = _arr_k(inp)
    return join(sorted(a))


# ── test generators ─────────────────────────────────────────────

def _arr_k_case(r, n, lo, hi, kmax=None):
    a = rand_ints(r, n, lo, hi)
    return f"{join(a)}\n{r.randint(1, kmax or n)}"


def _merge_case(r, k, maxlen, lo, hi):
    rows = [join(sorted(rand_ints(r, r.randint(1, maxlen), lo, hi))) for _ in range(k)]
    return f"{k}\n" + "\n".join(rows)


def _top_k_case(r, n, lo, hi):
    a = rand_ints(r, n, lo, hi)
    return f"{join(a)}\n{r.randint(1, len(set(a)))}"


def _points_case(r, n, lo, hi):
    pts = [f"{r.randint(lo, hi)} {r.randint(lo, hi)}" for _ in range(n)]
    return f"{n} {r.randint(1, n)}\n" + "\n".join(pts)


def _stream_case(r, q, lo, hi):
    k = r.randint(1, max(1, q // 2))
    return f"{k}\n{q}\n" + "\n".join(f"add {r.randint(lo, hi)}" for _ in range(q))


def _median_case(r, q, lo, hi):
    ops = ["add " + str(r.randint(lo, hi))]
    for _ in range(q - 1):
        ops.append("median" if r.random() < 0.4 else "add " + str(r.randint(lo, hi)))
    ops.append("median")
    return f"{len(ops)}\n" + "\n".join(ops)


def _task_case(r, n_tasks, letters, cooldown):
    return join(r.choice(letters) for _ in range(n_tasks)) + f"\n{cooldown}"


def _hand_case(r, groups, g, make_valid):
    a = []
    for _ in range(groups):
        start = r.randint(0, 30)
        a += list(range(start, start + g))
    if not make_valid:
        a[r.randrange(len(a))] += r.choice((-1, 1, 2))
    r.shuffle(a)
    return f"{join(a)}\n{g}"


def _nearly_case(r, n, k):
    a = sorted(rand_ints(r, n, -1000, 1000))
    # shuffle within windows of size k + 1 so each element stays within k of its spot
    for start in range(0, n, k + 1):
        chunk = a[start : start + k + 1]
        r.shuffle(chunk)
        a[start : start + k + 1] = chunk
    return f"{join(a)}\n{k}"


PROBLEMS = [
    Problem(
        title="Kth Smallest Element",
        difficulty="EASY",
        topics=["Heap", "Array", "Sorting"],
        description="""Print the `k`-th smallest value in the array (counting duplicates, so `k = 1` is the minimum).

Sorting works in `O(n log n)`. A max-heap holding only the `k` smallest values seen so far does it in `O(n log k)`: push each value and pop the largest whenever the heap grows past `k`.

**Input:** the first line is the array; the second line is `k`.

**Output:** the `k`-th smallest value.""",
        constraints=["1 <= k <= n <= 10^5", "-10^9 <= a[i] <= 10^9"],
        solve=_kth_smallest,
        brute=_kth_smallest_brute,
        examples=[("7 10 4 3 20 15\n3", "Sorted: 3 4 7 10 15 20 — the third is 7."), ("5 5 1\n2", "Duplicates count: 1 5 5, so the second is 5.")],
        tests=lambda r: ["9\n1", "3 1 2\n3", "2 2 2 2\n4", "-5 -1 -3\n1"] + [_arr_k_case(r, n, -50, 50) for n in (8, 25, 100)] + [_arr_k_case(r, 2500, -10**9, 10**9)],
    ),
    Problem(
        title="Last Stone Weight",
        difficulty="EASY",
        topics=["Heap"],
        description="""You have a pile of stones with positive weights. Each turn, take the two heaviest stones `x ≥ y` and smash them: if they're equal both are destroyed, otherwise a stone of weight `x − y` goes back on the pile. Stop when at most one stone is left.

A max-heap gives you the two heaviest stones in `O(log n)` per turn.

**Input:** one line of space-separated stone weights.

**Output:** the weight of the last stone, or `0` if none remain.""",
        constraints=["1 <= n <= 10^4", "1 <= weight <= 1000"],
        solve=_last_stone,
        brute=_last_stone_brute,
        examples=[("2 7 4 1 8 1", "8 and 7 → 1, 4 and 2 → 2, 2 and 1 → 1, 1 and 1 → gone, leaving 1."), ("3 3", "Equal stones destroy each other.")],
        tests=lambda r: ["5", "1 1", "10 4", "1 2 3", "9 3 3 3"] + [join(rand_ints(r, n, 1, 30)) for n in (6, 15, 60)] + [join(rand_ints(r, 2000, 1, 1000))],
    ),
    Problem(
        title="Minimum Cost to Connect Ropes",
        difficulty="MEDIUM",
        topics=["Heap", "Greedy"],
        description="""You have ropes of the given lengths. Joining two ropes of lengths `a` and `b` costs `a + b` and produces one rope of that length. Join all ropes into one with the **minimum total cost**.

Greedy works: always join the two shortest ropes, using a min-heap.

**Input:** one line of space-separated rope lengths.

**Output:** the minimum total cost (`0` if there is only one rope).""",
        constraints=["1 <= n <= 10^5", "1 <= length <= 10^4"],
        solve=_ropes,
        brute=_ropes_brute,
        examples=[("4 3 2 6", "Join 2+3=5, then 4+5=9, then 6+9=15: total 5+9+15 = 29."), ("7", "Nothing to join.")],
        tests=lambda r: ["1 1", "5 5 5", "1 2 3 4 5", "10000 1"] + [join(rand_ints(r, n, 1, 50)) for n in (6, 20, 70)] + [join(rand_ints(r, 4000, 1, 10**4))],
    ),
    Problem(
        title="Kth Largest in a Stream",
        difficulty="MEDIUM",
        topics=["Heap", "Design"],
        description="""Numbers arrive one at a time. After each new number, report the `k`-th largest number seen so far (duplicates count). If fewer than `k` numbers have arrived, report `-1`.

Keep a min-heap of the `k` largest values: its top is the answer.

**Input:** the first line is `k`, the second is `q`, then `q` lines of the form `add x`.

**Output:** one line per `add`: the current `k`-th largest, or `-1`.""",
        constraints=["1 <= k <= 10^4", "1 <= q <= 10^4", "-10^4 <= x <= 10^4"],
        solve=_kth_stream,
        brute=_kth_stream_brute,
        examples=[("3\n5\nadd 4\nadd 5\nadd 8\nadd 2\nadd 10", "Fewer than 3 numbers at first, then 4, 4, 5."), ("1\n3\nadd -1\nadd 3\nadd 2", "With k = 1 it's the running maximum.")],
        tests=lambda r: ["1\n1\nadd 5", "2\n1\nadd 5", "2\n4\nadd 1\nadd 1\nadd 1\nadd 1"] + [_stream_case(r, q, -20, 20) for q in (6, 12, 30, 60)] + [_stream_case(r, 2000, -10**4, 10**4)],
    ),
    Problem(
        title="Sort a Nearly Sorted Array",
        difficulty="MEDIUM",
        topics=["Heap", "Sorting"],
        description="""Every element is at most `k` positions away from where it belongs in sorted order. Sort the array.

A min-heap of size `k + 1` always contains the next smallest element, which gives `O(n log k)` — faster than a full sort when `k` is small.

**Input:** the first line is the array; the second line is `k`.

**Output:** the sorted array, space-separated.""",
        constraints=["1 <= n <= 10^5", "0 <= k < n"],
        solve=_nearly,
        brute=_nearly_brute,
        examples=[("6 5 3 2 8 10 9\n3", "Each value is within 3 places of its sorted spot."), ("1 2 3\n0", "k = 0 means it's already sorted.")],
        tests=lambda r: ["4\n0", "2 1\n1", "3 2 1\n2", "1 1 1 1\n2"] + [_nearly_case(r, n, k) for n, k in ((10, 2), (30, 4), (80, 1), (200, 7))] + [_nearly_case(r, 2500, 10)],
    ),
    Problem(
        title="Merge K Sorted Arrays",
        difficulty="MEDIUM",
        topics=["Heap", "Array"],
        description="""You're given `k` arrays, each sorted in non-decreasing order. Merge them into one sorted array.

Put the first element of each array into a min-heap along with which array it came from. Repeatedly pop the smallest and push the next element from the same array: `O(N log k)` for `N` total elements.

**Input:** the first line is `k`, followed by `k` lines, each a sorted, non-empty list of integers.

**Output:** all values in sorted order, space-separated.""",
        constraints=["1 <= k <= 500", "total elements <= 10^5"],
        solve=_merge_k,
        brute=_merge_k_brute,
        examples=[("3\n1 4 7\n2 5 8\n3 6 9", "Taking the smallest front each time gives 1 through 9."), ("2\n1 1\n1", "Duplicates are all kept.")],
        tests=lambda r: ["1\n5", "1\n1 2 3", "2\n4 5 6\n1 2 3", "3\n-1\n-2\n-3"] + [_merge_case(r, k, m, -50, 50) for k, m in ((3, 5), (6, 8), (12, 3))] + [_merge_case(r, 40, 100, -10**5, 10**5)],
    ),
    Problem(
        title="Top K Frequent Elements",
        difficulty="MEDIUM",
        topics=["Heap", "Hash Map"],
        description="""Print the `k` values that appear most often. Order them from most to least frequent; when two values appear equally often, the **smaller value comes first** (and wins a spot if they tie at the cut-off).

Count with a hash map, then take the top `k` with a heap (or bucket sort by frequency).

**Input:** the first line is the array; the second line is `k` (at most the number of distinct values).

**Output:** the `k` values, space-separated, in the order described.""",
        constraints=["1 <= n <= 10^5", "1 <= k <= number of distinct values"],
        solve=_top_k,
        brute=_top_k_brute,
        examples=[("1 1 1 2 2 3\n2", "1 appears 3 times, 2 twice."), ("4 4 5 5 6\n1", "4 and 5 tie at two each; the smaller, 4, wins.")],
        tests=lambda r: ["7\n1", "1 2 3\n3", "3 2 1\n2", "-1 -1 2 2 2\n2"] + [_top_k_case(r, n, -6, 6) for n in (10, 30, 120)] + [_top_k_case(r, 3000, -200, 200)],
    ),
    Problem(
        title="K Closest Points to Origin",
        difficulty="MEDIUM",
        topics=["Heap", "Sorting", "Math"],
        description="""Given points on a plane, print the `k` points closest to the origin `(0, 0)` by Euclidean distance.

Order the output by distance (closest first). Break ties by smaller `x`, then smaller `y`. Compare squared distances `x² + y²` to stay in integers.

**Input:** the first line has `n` and `k`, followed by `n` lines with a point `x y`.

**Output:** `k` lines, each a point `x y`, in the order described.""",
        constraints=["1 <= k <= n <= 10^4", "-10^4 <= x, y <= 10^4"],
        solve=_points,
        brute=_points_brute,
        examples=[("3 2\n3 3\n5 -1\n-2 4", "Squared distances 18, 26, 20: the closest two are (3, 3) then (-2, 4)."), ("2 1\n1 0\n0 1", "Both at distance 1 — the smaller x, 0, comes first.")],
        tests=lambda r: ["1 1\n0 0", "3 3\n1 1\n-1 -1\n1 -1", "4 2\n2 0\n0 2\n-2 0\n0 -2"] + [_points_case(r, n, -5, 5) for n in (6, 15, 40)] + [_points_case(r, 1500, -10**4, 10**4)],
    ),
    Problem(
        title="Hand of Straights",
        difficulty="MEDIUM",
        topics=["Heap", "Hash Map", "Greedy"],
        description="""Can the cards be split into groups of exactly `g` cards each, where every group is `g` **consecutive** values (like 3, 4, 5)? Every card must be used.

Greedy: the smallest remaining card must start a group, so repeatedly take the smallest value and consume one card of each value up to `smallest + g − 1`.

**Input:** the first line is the card values; the second line is `g`.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 10^4", "1 <= g <= n", "0 <= value <= 10^9"],
        solve=_hand,
        brute=_hand_brute,
        examples=[("1 2 3 6 2 3 4 7 8\n3", "Groups 1 2 3, 2 3 4 and 6 7 8."), ("1 2 3 4 5\n4", "5 cards can't form groups of 4.")],
        tests=lambda r: ["5\n1", "1 1 2 2 3 3\n3", "1 2 4\n3", "8 10 12\n3", "1 2 3 3 4 5\n3"] + [_hand_case(r, gr, g, ok) for gr, g, ok in ((3, 2, True), (4, 3, False), (5, 4, True), (6, 3, False))] + [_hand_case(r, 300, 5, True)],
    ),
    Problem(
        title="Task Scheduler",
        difficulty="MEDIUM",
        topics=["Heap", "Greedy", "Hash Map"],
        description="""A CPU runs tasks labelled by capital letters, one per time unit. Two runs of the **same** task must be separated by at least `n` units, during which the CPU can run other tasks or sit idle. Tasks can run in any order. Print the minimum number of time units to finish everything.

The most frequent task decides the shape: with maximum count `m` and `t` tasks sharing that count, the answer is `max(total, (m − 1)·(n + 1) + t)`. You can also simulate it with a max-heap.

**Input:** the first line is the task letters, space-separated; the second line is `n`.

**Output:** the minimum number of time units.""",
        constraints=["1 <= tasks <= 10^4", "0 <= n <= 100"],
        solve=_task,
        brute=_task_brute,
        examples=[("A A A B B B\n2", "A B idle A B idle A B — 8 units."), ("A A A B B B\n0", "No cooldown: 6 units.")],
        tests=lambda r: ["A\n5", "A B C D\n3", "A A A A\n1", "A A A B C D E F G\n2", "A A B B C C\n2"] + [_task_case(r, t, letters, c) for t, letters, c in ((10, "AB", 3), (20, "ABCDE", 2), (30, "ABC", 4))] + [_task_case(r, 400, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 10), _task_case(r, 60, "AAAAB", 7)],
    ),
    Problem(
        title="Find Median from Data Stream",
        difficulty="HARD",
        topics=["Heap", "Design"],
        description="""Process a stream of operations: `add x` adds a number, and `median` asks for the median of all numbers added so far. With an even count, the median is the average of the two middle values.

Keep two heaps: a max-heap for the smaller half and a min-heap for the larger half, rebalanced so their sizes differ by at most one. Each operation is `O(log n)`.

**Input:** the first line is `q`, followed by `q` operations. The first operation is always `add`.

**Output:** one line per `median`, printed with exactly one decimal place (e.g. `2.0`, `2.5`, `-1.5`).""",
        constraints=["1 <= q <= 2·10^4", "-10^5 <= x <= 10^5"],
        solve=_median,
        brute=_median_brute,
        examples=[("5\nadd 1\nadd 2\nmedian\nadd 3\nmedian", "Median of [1, 2] is 1.5, of [1, 2, 3] is 2."), ("3\nadd -4\nadd 1\nmedian", "(-4 + 1) / 2 = -1.5.")],
        tests=lambda r: ["2\nadd 5\nmedian", "4\nadd 2\nadd 2\nadd 2\nmedian", "5\nadd -1\nmedian\nadd -2\nmedian\nmedian"] + [_median_case(r, q, -10, 10) for q in (8, 20, 50)] + [_median_case(r, 2500, -10**5, 10**5)],
    ),
]
