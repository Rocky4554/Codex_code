"""Greedy algorithms."""
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from itertools import combinations, permutations, product

from lib import Playlist, Problem, boolstr, ints, join, lines, rand_ints

PLAYLISTS = [
    Playlist(
        key="greedy",
        title="10 · Greedy",
        description="Make the locally best choice at every step, and learn to argue why it leads to the best overall answer.",
        accent="#FFE29A",
        titles=[
            "Assign Cookies",
            "Lemonade Change",
            "Shortest Job First",
            "Can You Reach the End",
            "Minimum Jumps to the End",
            "Maximum Meetings in One Room",
            "Minimum Platforms",
            "Fractional Knapsack",
            "Job Sequencing",
            "Insert an Interval",
            "Non-overlapping Intervals",
            "Gas Station Circuit",
            "Wildcard Parentheses",
            "Candy Distribution",
        ],
    )
]


# ── Assign cookies ──────────────────────────────────────────────

def _cookies(inp):
    ls = lines(inp)
    g, s = sorted(ints(ls[0])), sorted(ints(ls[1]))
    i = 0
    for size in s:
        if i < len(g) and size >= g[i]:
            i += 1
    return str(i)


def _cookies_brute(inp):
    ls = lines(inp)
    g, s = ints(ls[0]), ints(ls[1])
    match = [-1] * len(s)

    def augment(child, seen):
        for j, size in enumerate(s):
            if size >= g[child] and not seen[j]:
                seen[j] = True
                if match[j] == -1 or augment(match[j], seen):
                    match[j] = child
                    return True
        return False

    return str(sum(augment(c, [False] * len(s)) for c in range(len(g))))


# ── Lemonade change ─────────────────────────────────────────────

def _lemonade(inp):
    fives = tens = 0
    for b in ints(lines(inp)[0]):
        if b == 5:
            fives += 1
        elif b == 10:
            if not fives:
                return "false"
            fives -= 1
            tens += 1
        else:
            if tens and fives:
                tens -= 1
                fives -= 1
            elif fives >= 3:
                fives -= 3
            else:
                return "false"
    return "true"


def _lemonade_brute(inp):
    bills = ints(lines(inp)[0])

    def go(i, f, t):
        if i == len(bills):
            return True
        b = bills[i]
        if b == 5:
            return go(i + 1, f + 1, t)
        if b == 10:
            return f > 0 and go(i + 1, f - 1, t + 1)
        return (f > 0 and t > 0 and go(i + 1, f - 1, t - 1)) or (f >= 3 and go(i + 1, f - 3, t))

    return boolstr(go(0, 0, 0))


def _lemonade_tests(r):
    out = ["5", "10", "20", "5 10", "5 20", "5 5 5 20", "5 5 10 10 20", "5 5 10 20 5 5 5 5 5 5 5 5 5 10 5 5 20 5 20 5"]
    for _ in range(4):
        out.append(join(r.choices([5, 5, 5, 10, 10, 20], k=r.randint(5, 30))))
    out.append(join([5] * 500 + r.choices([5, 10, 20], k=2500)))
    return out


# ── SJF ─────────────────────────────────────────────────────────

def _sjf(inp):
    bursts = sorted(ints(lines(inp)[0]))
    t = total = 0
    for b in bursts:
        total += t
        t += b
    return str(total // len(bursts))


def _sjf_brute(inp):
    bursts = ints(lines(inp)[0])
    best = None
    for order in permutations(bursts):
        t = total = 0
        for b in order:
            total += t
            t += b
        best = total if best is None else min(best, total)
    return str(best // len(bursts))


# ── Jump game ───────────────────────────────────────────────────

def _jump(inp):
    nums = ints(lines(inp)[0])
    reach = 0
    for i, v in enumerate(nums):
        if i > reach:
            return "false"
        reach = max(reach, i + v)
    return "true"


def _jump_brute(inp):
    nums = ints(lines(inp)[0])
    ok = [False] * len(nums)
    ok[-1] = True
    for i in range(len(nums) - 2, -1, -1):
        ok[i] = any(ok[j] for j in range(i + 1, min(len(nums), i + nums[i] + 1)))
    return boolstr(ok[0])


def _jump2(inp):
    nums = ints(lines(inp)[0])
    jumps = end = far = 0
    for i in range(len(nums) - 1):
        far = max(far, i + nums[i])
        if i == end:
            jumps += 1
            end = far
    return str(jumps)


def _jump2_brute(inp):
    nums = ints(lines(inp)[0])
    INF = float("inf")
    dp = [INF] * len(nums)
    dp[0] = 0
    for i in range(len(nums)):
        for j in range(i + 1, min(len(nums), i + nums[i] + 1)):
            dp[j] = min(dp[j], dp[i] + 1)
    return str(dp[-1])


def _jump2_tests(r):
    out = ["0", "1 0", "5 0 0 0 0 0", "1 1 1 1 1", "2 3 0 1 4", "1 2 1 1 1"]
    for n in (8, 15, 40, 3000):
        while True:
            arr = rand_ints(r, n, 0, 5 if n < 100 else 8)
            if _jump(join(arr)) == "true":
                break
        out.append(join(arr))
    return out


# ── Meetings ────────────────────────────────────────────────────

def _meetings(inp):
    ls = lines(inp)
    st, en = ints(ls[0]), ints(ls[1])
    last, count = -1, 0
    for s, e in sorted(zip(st, en), key=lambda x: (x[1], x[0])):
        if s > last:
            count += 1
            last = e
    return str(count)


def _meetings_brute(inp):
    ls = lines(inp)
    ms = sorted(zip(ints(ls[0]), ints(ls[1])))
    for k in range(len(ms), 0, -1):
        for c in combinations(ms, k):
            if all(c[i + 1][0] > c[i][1] for i in range(k - 1)):
                return str(k)
    return "0"


def _interval_pairs(r, n, hi, maxlen):
    st, en = [], []
    for _ in range(n):
        s = r.randint(0, hi)
        st.append(s)
        en.append(s + r.randint(0, maxlen))
    return st, en


def _meetings_tests(r):
    out = ["5\n10", "1 2\n2 3", "1 3\n2 4", "1 1 1\n5 5 5", "0 2 4 6\n1 3 5 7"]
    for n in (6, 9, 10):
        st, en = _interval_pairs(r, n, 30, 8)
        out.append(f"{join(st)}\n{join(en)}")
    st, en = _interval_pairs(r, 2000, 10**6, 1000)
    out.append(f"{join(st)}\n{join(en)}")
    return out


# ── Platforms ───────────────────────────────────────────────────

def _platforms(inp):
    ls = lines(inp)
    arr, dep = sorted(ints(ls[0])), sorted(ints(ls[1]))
    i = j = cur = best = 0
    while i < len(arr):
        if arr[i] <= dep[j]:
            cur += 1
            best = max(best, cur)
            i += 1
        else:
            cur -= 1
            j += 1
    return str(best)


def _platforms_brute(inp):
    ls = lines(inp)
    trains = list(zip(ints(ls[0]), ints(ls[1])))
    return str(max(sum(1 for a, d in trains if a <= t <= d) for t in {a for a, _ in trains}))


def _hhmm(m):
    return (m // 60) * 100 + m % 60


def _platform_tests(r):
    out = ["900\n910", "900 910\n905 920", "900 905\n905 910", "1000 1000 1000\n1030 1015 1001"]
    for n in (5, 8, 12, 2000):
        a, d = [], []
        for _ in range(n):
            s = r.randint(0, 1380)
            a.append(s)
            d.append(min(1439, s + r.randint(0, 120)))
        out.append(f"{join(_hhmm(x) for x in a)}\n{join(_hhmm(x) for x in d)}")
    return out


# ── Fractional knapsack ─────────────────────────────────────────

def _fmt2(x: Fraction) -> str:
    d = Decimal(x.numerator) / Decimal(x.denominator)
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _knap_parse(inp):
    ls = lines(inp)
    n, cap = map(int, ls[0].split())
    items = [tuple(map(int, ls[1 + i].split())) for i in range(n)]
    return cap, items


def _frac_knap(inp):
    cap, items = _knap_parse(inp)
    total = Fraction(0)
    for v, w in sorted(items, key=lambda x: Fraction(x[0], x[1]), reverse=True):
        if cap == 0:
            break
        take = min(w, cap)
        total += Fraction(v * take, w)
        cap -= take
    return _fmt2(total)


def _knap_tests(r):
    out = ["1 0\n10 5", "1 3\n10 5", "2 100\n10 5\n20 10", "3 1\n5 3\n9 4\n2 1"]
    for n in (4, 7, 12, 500):
        items = [f"{r.randint(1, 1000)} {r.randint(1, 100)}" for _ in range(n)]
        out.append(f"{n} {r.randint(1, 60 * n)}\n" + "\n".join(items))
    return out


# ── Job sequencing ──────────────────────────────────────────────

def _jobs_parse(inp):
    ls = lines(inp)
    n = int(ls[0])
    return [tuple(map(int, ls[1 + i].split())) for i in range(n)]


def _jobs(inp):
    jobs = sorted(_jobs_parse(inp), key=lambda x: -x[1])
    maxd = max(d for d, _ in jobs)
    parent = list(range(maxd + 1))  # DSU: latest free slot ≤ d

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    profit = 0
    for d, p in jobs:
        slot = find(d)
        if slot > 0:
            profit += p
            parent[slot] = slot - 1
    return str(profit)


def _jobs_brute(inp):
    jobs = _jobs_parse(inp)
    best = 0
    for k in range(len(jobs) + 1):
        for c in combinations(jobs, k):
            ds = sorted(d for d, _ in c)
            if all(ds[i] >= i + 1 for i in range(len(ds))):
                best = max(best, sum(p for _, p in c))
    return str(best)


def _jobs_tests(r):
    out = ["1\n1 50", "3\n1 10\n1 20\n1 30", "3\n3 5\n3 5\n3 5", "4\n2 100\n1 19\n2 27\n1 25"]
    for n in (5, 8, 10):
        out.append(f"{n}\n" + "\n".join(f"{r.randint(1, n)} {r.randint(1, 100)}" for _ in range(n)))
    n = 2000
    out.append(f"{n}\n" + "\n".join(f"{r.randint(1, 500)} {r.randint(1, 10**4)}" for _ in range(n)))
    return out


# ── Intervals ───────────────────────────────────────────────────

def _merge_all(iv):
    out = []
    for s, e in sorted(iv):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def _insert_parse(inp):
    ls = lines(inp)
    n = int(ls[0])
    iv = [list(map(int, ls[1 + i].split())) for i in range(n)]
    return iv, list(map(int, ls[1 + n].split()))


def _insert(inp):
    iv, (ns, ne) = _insert_parse(inp)
    out, i = [], 0
    while i < len(iv) and iv[i][1] < ns:
        out.append(iv[i]); i += 1
    while i < len(iv) and iv[i][0] <= ne:
        ns, ne = min(ns, iv[i][0]), max(ne, iv[i][1]); i += 1
    out.append([ns, ne])
    out.extend(iv[i:])
    return "\n".join(f"{s} {e}" for s, e in out)


def _insert_brute(inp):
    iv, new = _insert_parse(inp)
    return "\n".join(f"{s} {e}" for s, e in _merge_all(iv + [new]))


def _sorted_disjoint(r, n, hi):
    pts = sorted(r.sample(range(0, hi), 2 * n))
    return [[pts[2 * k], pts[2 * k + 1]] for k in range(n)]


def _insert_tests(r):
    out = ["0\n4 8", "1\n1 5\n2 3", "1\n1 5\n6 8", "1\n6 8\n1 5", "2\n1 2\n3 4\n2 3", "3\n1 2\n5 6\n9 10\n0 11"]
    for n in (4, 8, 1500):
        iv = _sorted_disjoint(r, n, 10 * n + 10)
        a = r.randint(0, 10 * n)
        out.append(f"{n}\n" + "\n".join(f"{s} {e}" for s, e in iv) + f"\n{a} {a + r.randint(0, 25)}")
    return out


def _nonoverlap_parse(inp):
    ls = lines(inp)
    n = int(ls[0])
    return [tuple(map(int, ls[1 + i].split())) for i in range(n)]


def _nonoverlap(inp):
    iv = sorted(_nonoverlap_parse(inp), key=lambda x: x[1])
    keep, end = 0, None
    for s, e in iv:
        if end is None or s >= end:
            keep += 1
            end = e
    return str(len(iv) - keep)


def _nonoverlap_brute(inp):
    iv = sorted(_nonoverlap_parse(inp))
    for k in range(len(iv), -1, -1):
        for c in combinations(iv, k):
            if all(c[i + 1][0] >= c[i][1] for i in range(k - 1)):
                return str(len(iv) - k)
    return str(len(iv))


def _nonoverlap_tests(r):
    out = ["1\n1 2", "2\n1 2\n2 3", "3\n1 2\n1 2\n1 2", "4\n1 100\n11 22\n1 11\n2 12"]
    for n in (6, 9, 10):
        iv = []
        for _ in range(n):
            s = r.randint(0, 30)
            iv.append(f"{s} {s + r.randint(1, 10)}")
        out.append(f"{n}\n" + "\n".join(iv))
    n = 1800
    iv = []
    for _ in range(n):
        s = r.randint(-10**6, 10**6)
        iv.append(f"{s} {s + r.randint(1, 5000)}")
    out.append(f"{n}\n" + "\n".join(iv))
    return out


# ── Gas station ─────────────────────────────────────────────────

def _gas(inp):
    ls = lines(inp)
    gas, cost = ints(ls[0]), ints(ls[1])
    if sum(gas) < sum(cost):
        return "-1"
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0
    return str(start)


def _gas_brute(inp):
    ls = lines(inp)
    gas, cost = ints(ls[0]), ints(ls[1])
    n = len(gas)
    for s in range(n):
        tank, ok = 0, True
        for k in range(n):
            i = (s + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                ok = False
                break
        if ok:
            return str(s)
    return "-1"


def _gas_tests(r):
    out = ["5\n4", "4\n5", "1 2 3 4 5\n3 4 5 1 2", "2 3 4\n3 4 3", "3 3 3\n3 3 3"]
    for n in (6, 10, 20):
        out.append(f"{join(rand_ints(r, n, 0, 9))}\n{join(rand_ints(r, n, 0, 9))}")
    n = 3000
    g = rand_ints(r, n, 0, 1000)
    c = rand_ints(r, n, 0, 1000)
    c[0] = max(0, c[0] - (sum(c) - sum(g)) - 1) if sum(c) > sum(g) else c[0]
    out.append(f"{join(g)}\n{join(c)}")
    return out


# ── Wildcard parentheses ────────────────────────────────────────

def _wild(inp):
    s = lines(inp)[0]
    lo = hi = 0
    for ch in s:
        if ch == "(":
            lo += 1; hi += 1
        elif ch == ")":
            lo -= 1; hi -= 1
        else:
            lo -= 1; hi += 1
        if hi < 0:
            return "false"
        lo = max(lo, 0)
    return boolstr(lo == 0)


def _wild_brute(inp):
    s = lines(inp)[0]
    stars = [i for i, ch in enumerate(s) if ch == "*"]
    for choice in product("()_", repeat=len(stars)):
        t = list(s)
        for i, c in zip(stars, choice):
            t[i] = c
        d, ok = 0, True
        for ch in t:
            if ch == "(":
                d += 1
            elif ch == ")":
                d -= 1
                if d < 0:
                    ok = False
                    break
        if ok and d == 0:
            return "true"
    return "false"


def _wild_tests(r):
    out = ["*", "(", ")", "(*)", "(*))", ")*(", "((*", "**))", "(((((*)))"]
    for _ in range(4):
        out.append("".join(r.choice("()*") for _ in range(r.randint(4, 9))))
    out.append("".join(r.choice("(()**)") for _ in range(5000)))
    return out


# ── Candy ───────────────────────────────────────────────────────

def _candy(inp):
    ra = ints(lines(inp)[0])
    n = len(ra)
    c = [1] * n
    for i in range(1, n):
        if ra[i] > ra[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ra[i] > ra[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return str(sum(c))


def _candy_brute(inp):
    ra = ints(lines(inp)[0])
    n = len(ra)
    c = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            need = 1
            if i > 0 and ra[i] > ra[i - 1]:
                need = max(need, c[i - 1] + 1)
            if i < n - 1 and ra[i] > ra[i + 1]:
                need = max(need, c[i + 1] + 1)
            if need > c[i]:
                c[i] = need
                changed = True
    return str(sum(c))


PROBLEMS = [
    Problem(
        title="Assign Cookies",
        difficulty="EASY",
        topics=["Greedy", "Sorting", "Array"],
        description="""Each child has a greed value — the smallest cookie size that makes them happy — and each cookie has a size. A child can get at most one cookie and each cookie goes to at most one child. Make as many children happy as possible.

Sort both lists and give the smallest cookie that's big enough to the least greedy child still waiting.

**Input:** line 1 — the children's greed values; line 2 — the cookie sizes.

**Output:** the maximum number of happy children.""",
        constraints=["1 <= children, cookies <= 3 × 10^4", "1 <= values <= 10^9"],
        solve=_cookies,
        brute=_cookies_brute,
        examples=[("1 2 3\n1 1", "Both cookies are size 1, so only the child with greed 1 is happy."), ("1 2\n1 2 3", "Every child gets a cookie.")],
        tests=lambda r: ["5\n4", "4\n5", "1 1 1\n1", "10 9 8 7\n5 6 7 8"]
        + [f"{join(rand_ints(r, r.randint(2, 8), 1, 10))}\n{join(rand_ints(r, r.randint(2, 8), 1, 10))}" for _ in range(4)]
        + [f"{join(rand_ints(r, 1200, 1, 10**9))}\n{join(rand_ints(r, 1200, 1, 10**9))}"],
    ),
    Problem(
        title="Lemonade Change",
        difficulty="EASY",
        topics=["Greedy", "Array"],
        description="""Lemonade costs 5. Customers arrive in order and each pays with a 5, 10 or 20 bill. You start with no money. Can you give every customer correct change?

When you have a choice for a 20, give back a 10 + 5 rather than three 5s — 5s are more useful later.

**Input:** one line — the bills in order.

**Output:** `true` if everyone gets correct change, otherwise `false`.""",
        constraints=["1 <= n <= 10^4", "bills[i] is 5, 10 or 20"],
        solve=_lemonade,
        brute=_lemonade_brute,
        examples=[("5 5 5 10 20", "Keep the 10 from customer 4 and hand it back to customer 5."), ("5 5 10 10 20", "The last customer needs 15 but you only hold two 10s.")],
        tests=_lemonade_tests,
    ),
    Problem(
        title="Shortest Job First",
        difficulty="EASY",
        topics=["Greedy", "Sorting"],
        description="""A CPU runs jobs one at a time; all jobs arrive at time 0 and each has a burst time. A job's waiting time is how long it waits before it starts. Run the jobs in the order that minimizes the total waiting time (shortest first) and print the **average** waiting time, rounded down to an integer.

**Input:** one line of burst times.

**Output:** `floor(total waiting time / number of jobs)`.""",
        constraints=["1 <= n <= 10^4", "1 <= burst <= 10^4"],
        solve=_sjf,
        brute=_sjf_brute,
        examples=[("4 3 7 1 2", "Order 1 2 3 4 7 waits 0+1+3+6+10 = 20, average 4."), ("5", "The only job waits 0.")],
        tests=lambda r: ["1 1", "10 1", "3 3 3", "1 2 3 4 5 6 7"]
        + [join(rand_ints(r, r.randint(3, 7), 1, 20)) for _ in range(4)]
        + [join(rand_ints(r, 5000, 1, 10**4))],
    ),
    Problem(
        title="Can You Reach the End",
        difficulty="MEDIUM",
        topics=["Greedy", "Array"],
        description="""You stand on index 0 of an array. The value at each index is the **maximum** number of steps you can jump forward from there. Can you reach the last index?

Track the farthest index reachable so far; if you ever stand beyond it, you're stuck.

**Input:** one line of non-negative integers.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 10^4", "0 <= nums[i] <= 10^5"],
        solve=_jump,
        brute=_jump_brute,
        examples=[("2 3 1 1 4", "Jump 1 step to index 1, then 3 steps to the end."), ("3 2 1 0 4", "Every route lands on the 0 at index 3.")],
        tests=lambda r: ["0", "1 0", "0 1", "2 0 0", "1 1 0 1"]
        + [join(rand_ints(r, r.randint(5, 15), 0, 3)) for _ in range(5)]
        + [join(rand_ints(r, 4000, 0, 4))],
    ),
    Problem(
        title="Minimum Jumps to the End",
        difficulty="MEDIUM",
        topics=["Greedy", "Array"],
        description="""Same jumping rules as *Can You Reach the End*, but now the last index is always reachable. Print the minimum number of jumps needed to get there.

Think in levels, like BFS: all indices reachable with `k` jumps form a window; the next window extends to the farthest point reachable from it.

**Input:** one line of non-negative integers.

**Output:** the minimum number of jumps (0 if the array has one element).""",
        constraints=["1 <= n <= 10^4", "0 <= nums[i] <= 1000", "The last index is reachable."],
        solve=_jump2,
        brute=_jump2_brute,
        examples=[("2 3 1 1 4", "0 → 1 → 4: two jumps."), ("1 1 1 1", "Three single steps.")],
        tests=_jump2_tests,
    ),
    Problem(
        title="Maximum Meetings in One Room",
        difficulty="EASY",
        topics=["Greedy", "Sorting", "Intervals"],
        description="""There is one meeting room and `n` meetings, each with a start and an end time. Schedule as many meetings as possible. A meeting can only start **strictly after** the previous one ends.

Always pick the meeting that finishes earliest among those that still fit.

**Input:** line 1 — start times; line 2 — end times (same order, `start <= end`).

**Output:** the maximum number of meetings.""",
        constraints=["1 <= n <= 10^4", "0 <= start <= end <= 10^7"],
        solve=_meetings,
        brute=_meetings_brute,
        examples=[("1 3 0 5 8 5\n2 4 6 7 9 9", "Meetings (1,2), (3,4), (5,7), (8,9)."), ("1 2\n2 3", "The second starts exactly when the first ends — not allowed.")],
        tests=_meetings_tests,
    ),
    Problem(
        title="Minimum Platforms",
        difficulty="MEDIUM",
        topics=["Greedy", "Sorting"],
        description="""Trains arrive and depart at a station during one day. Times are written as `HHMM` integers (e.g. `905` is 9:05, `1430` is 14:30), and each train departs at or after it arrives. A train occupies a platform from its arrival through its departure, **inclusive** — if one train departs at the same minute another arrives, they need different platforms. Find the minimum number of platforms.

Sort arrivals and departures separately and sweep through both.

**Input:** line 1 — arrival times; line 2 — departure times (same order).

**Output:** the minimum number of platforms.""",
        constraints=["1 <= n <= 10^4", "0 <= times <= 2359"],
        solve=_platforms,
        brute=_platforms_brute,
        examples=[("900 940 950 1100 1500 1800\n910 1200 1120 1130 1900 2000", "Between 11:00 and 11:20 three trains are at the station."), ("900 905\n905 910", "At 9:05 both trains are present.")],
        tests=_platform_tests,
    ),
    Problem(
        title="Fractional Knapsack",
        difficulty="MEDIUM",
        topics=["Greedy", "Sorting"],
        description="""You have a bag of capacity `W` and `n` items, each with a value and a weight. You may take any **fraction** of an item, getting that fraction of its value. Maximize the total value.

Take items in decreasing order of value per unit weight, taking a piece of the last one if it doesn't fully fit.

**Input:** line 1 — `n` and `W`; next `n` lines — `value weight`.

**Output:** the maximum value, rounded to 2 decimal places (half up), e.g. `240.00`.""",
        constraints=["1 <= n <= 10^4", "0 <= W <= 10^6", "1 <= value <= 10^4", "1 <= weight <= 10^3"],
        solve=_frac_knap,
        examples=[("3 50\n60 10\n100 20\n120 30", "Take the first two whole and 2/3 of the third: 60 + 100 + 80."), ("1 2\n10 3", "Two thirds of one item: 6.666… → 6.67.")],
        tests=_knap_tests,
    ),
    Problem(
        title="Job Sequencing",
        difficulty="MEDIUM",
        topics=["Greedy", "Sorting"],
        description="""Each job takes one unit of time, has a deadline `d` (it must finish by time `d`, i.e. occupy one of the slots 1…d) and a profit. Only one job runs at a time. Choose jobs to maximize the total profit.

Take jobs from most to least profitable and put each in the latest free slot not after its deadline.

**Input:** line 1 — `n`; next `n` lines — `deadline profit`.

**Output:** the maximum total profit.""",
        constraints=["1 <= n <= 10^4", "1 <= deadline <= n", "1 <= profit <= 10^4"],
        solve=_jobs,
        brute=_jobs_brute,
        examples=[("4\n4 20\n1 10\n1 40\n1 30", "Run the 40 job in slot 1 and the 20 job later: 60."), ("3\n2 5\n2 6\n2 7", "Only two slots: 7 + 6.")],
        tests=_jobs_tests,
    ),
    Problem(
        title="Insert an Interval",
        difficulty="MEDIUM",
        topics=["Intervals", "Array", "Greedy"],
        description="""You're given a list of non-overlapping intervals sorted by start, and one new interval. Insert the new interval and merge wherever intervals overlap. Intervals are closed, so `[1, 2]` and `[2, 3]` overlap and merge into `[1, 3]`.

**Input:** line 1 — `n`; next `n` lines — `start end` of the existing intervals (sorted, disjoint); last line — the new interval `start end`.

**Output:** the resulting intervals in order, one `start end` per line.""",
        constraints=["0 <= n <= 10^4", "0 <= start <= end <= 10^6"],
        solve=_insert,
        brute=_insert_brute,
        examples=[("2\n1 3\n6 9\n2 5", "[2,5] overlaps [1,3] → [1,5]."), ("3\n1 2\n3 5\n8 10\n4 8", "[4,8] swallows [3,5] and touches [8,10].")],
        tests=_insert_tests,
    ),
    Problem(
        title="Non-overlapping Intervals",
        difficulty="MEDIUM",
        topics=["Intervals", "Greedy", "Sorting"],
        description="""Remove the fewest intervals so that the remaining ones don't overlap. Intervals that only touch at an endpoint, like `[1, 2]` and `[2, 3]`, do **not** overlap.

Keep the interval that ends earliest; it leaves the most room for the rest.

**Input:** line 1 — `n`; next `n` lines — `start end` with `start < end`.

**Output:** the minimum number of intervals to remove.""",
        constraints=["1 <= n <= 10^4", "-10^6 <= start < end <= 10^6"],
        solve=_nonoverlap,
        brute=_nonoverlap_brute,
        examples=[("4\n1 2\n2 3\n3 4\n1 3", "Remove [1,3]; the rest only touch."), ("3\n1 2\n1 2\n1 2", "Keep one copy.")],
        tests=_nonoverlap_tests,
    ),
    Problem(
        title="Gas Station Circuit",
        difficulty="MEDIUM",
        topics=["Greedy", "Array"],
        description="""Stations sit on a circular road. At station `i` you can fill up `gas[i]` units, and driving from `i` to `i + 1` (wrapping around at the end) costs `cost[i]`. Your tank starts empty and has no limit. From which station can you start and drive the full circle back to it?

If the total gas is less than the total cost, it's impossible. Otherwise, whenever your tank goes negative, no station up to that point can be the start — restart from the next one.

**Input:** line 1 — `gas`; line 2 — `cost`.

**Output:** the **smallest** index you can start from, or `-1` if none works.""",
        constraints=["1 <= n <= 10^4", "0 <= gas[i], cost[i] <= 10^4"],
        solve=_gas,
        brute=_gas_brute,
        examples=[("1 2 3 4 5\n3 4 5 1 2", "Starting at index 3 you never run dry."), ("2 3 4\n3 4 3", "Total gas 9 is less than total cost 10.")],
        tests=_gas_tests,
    ),
    Problem(
        title="Wildcard Parentheses",
        difficulty="MEDIUM",
        topics=["Greedy", "String"],
        description="""A string contains `(`, `)` and `*`. Each `*` can act as `(`, as `)`, or as nothing. Can the string be made into a balanced parentheses string?

Instead of trying every choice, track the lowest and highest possible number of open brackets as you scan.

**Input:** one string.

**Output:** `true` or `false`.""",
        constraints=["1 <= s.length <= 10^4"],
        solve=_wild,
        brute=_wild_brute,
        examples=[("(*))", "Use * as ( to get (()). "), (")*(", "The first ) can never be matched.")],
        tests=_wild_tests,
    ),
    Problem(
        title="Candy Distribution",
        difficulty="HARD",
        topics=["Greedy", "Array"],
        description="""Children stand in a line, each with a rating. Give every child at least one candy, and any child with a higher rating than a neighbour must get more candies than that neighbour. What's the fewest candies you need in total?

Do two passes: left to right handles the left neighbour, right to left handles the right one.

**Input:** one line of ratings.

**Output:** the minimum total number of candies.""",
        constraints=["1 <= n <= 2 × 10^4", "0 <= rating <= 2 × 10^4"],
        solve=_candy,
        brute=_candy_brute,
        examples=[("1 0 2", "Give 2, 1, 2."), ("1 2 2", "Give 1, 2, 1 — equal ratings don't need to differ.")],
        tests=lambda r: ["5", "1 2 3 4 5", "5 4 3 2 1", "2 2 2 2", "1 3 2 2 1", "1 6 10 8 7 3 2"]
        + [join(rand_ints(r, r.randint(5, 20), 0, 5)) for _ in range(3)]
        + [join(rand_ints(r, 4000, 0, 20000))],
    ),
]
