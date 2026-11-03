"""Dynamic Programming — 1-D, grids, knapsack, strings, stocks, LIS and interval DP.

Every problem has a `brute` written as a different formulation (plain
recursion / top-down memo / enumeration) so build.py can cross-check the
bottom-up `solve` on small inputs.
"""
import sys
from functools import lru_cache
from itertools import combinations

from lib import Playlist, Problem, boolstr, ints, join, lines, rand_ints, rand_str

sys.setrecursionlimit(100_000)
MOD = 1_000_000_007
INF = float("inf")

PLAYLISTS = [
    Playlist(
        key="dp",
        title="17 · Dynamic Programming",
        description="Break problems into overlapping subproblems: 1-D, grids, knapsack, strings, stocks, LIS and interval DP.",
        accent="#F6C1E0",
        titles=[
            "Fibonacci",
            "Climbing Stairs",
            "Frog Jump",
            "Frog Jump with K Steps",
            "House Robber",
            "House Robber II",
            "Maximum Subarray",
            "Unique Grid Paths",
            "Unique Paths with Obstacles",
            "Minimum Path Sum",
            "Triangle Minimum Path",
            "Minimum Falling Path Sum",
            "Subset Sum Exists",
            "Partition Equal Subset Sum",
            "Minimum Subset Sum Difference",
            "Count Subsets with Sum K",
            "0/1 Knapsack",
            "Coin Change",
            "Coin Change II",
            "Unbounded Knapsack",
            "Rod Cutting",
            "Longest Common Subsequence",
            "Longest Common Substring",
            "Longest Palindromic Subsequence",
            "Longest Palindromic Substring",
            "Minimum Insertions to Make Palindrome",
            "Edit Distance",
            "Distinct Subsequences",
            "Wildcard Matching",
            "Stock Trading with Unlimited Transactions",
            "Stock Trading with Two Transactions",
            "Stock Trading with K Transactions",
            "Stock Trading with Cooldown",
            "Stock Trading with Transaction Fee",
            "Longest Increasing Subsequence",
            "Number of Longest Increasing Subsequences",
            "Matrix Chain Multiplication",
            "Burst Balloons",
            "Palindrome Partitioning Min Cuts",
            "Maximal Square",
            "Count Square Submatrices",
        ],
    )
]


# ── input helpers (local) ────────────────────────────────────────

def _grid_ints(inp):
    ls = lines(inp)
    r, c = ints(ls[0])
    return [ints(ls[1 + i]) for i in range(r)], r, c


def _bits_grid(inp):
    ls = lines(inp)
    r, c = ints(ls[0])
    return [[int(ch) for ch in ls[1 + i]] for i in range(r)], r, c


def _grid_text(r_, rows):
    return f"{len(rows)} {len(rows[0])}\n" + "\n".join(join(row) for row in rows)


def _bits_text(rows):
    return f"{len(rows)} {len(rows[0])}\n" + "\n".join("".join(map(str, row)) for row in rows)


# ── 1-D ──────────────────────────────────────────────────────────

def _frog(inp):
    h = ints(lines(inp)[0])
    n = len(h)
    dp = [0] * n
    for i in range(1, n):
        dp[i] = dp[i - 1] + abs(h[i] - h[i - 1])
        if i > 1:
            dp[i] = min(dp[i], dp[i - 2] + abs(h[i] - h[i - 2]))
    return str(dp[-1])


def _frog_brute(inp):
    h = ints(lines(inp)[0])

    @lru_cache(None)
    def f(i):
        if i == 0:
            return 0
        best = f(i - 1) + abs(h[i] - h[i - 1])
        if i > 1:
            best = min(best, f(i - 2) + abs(h[i] - h[i - 2]))
        return best

    return str(f(len(h) - 1))


def _frogk(inp):
    ls = lines(inp)
    h, k = ints(ls[0]), int(ls[1])
    n = len(h)
    dp = [0] * n
    for i in range(1, n):
        dp[i] = min(dp[j] + abs(h[i] - h[j]) for j in range(max(0, i - k), i))
    return str(dp[-1])


def _frogk_brute(inp):
    ls = lines(inp)
    h, k = ints(ls[0]), int(ls[1])

    @lru_cache(None)
    def f(i):  # cost from i to the end
        if i == len(h) - 1:
            return 0
        return min(abs(h[j] - h[i]) + f(j) for j in range(i + 1, min(len(h), i + k + 1)))

    return str(f(0))


def _rob_line(a):
    take, skip = 0, 0
    for x in a:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)


def _rob2(inp):
    a = ints(lines(inp)[0])
    if len(a) == 1:
        return str(a[0])
    return str(max(_rob_line(a[1:]), _rob_line(a[:-1])))


def _rob2_brute(inp):
    a = ints(lines(inp)[0])
    n = len(a)

    @lru_cache(None)
    def f(i, first_taken):
        if i >= n:
            return 0
        if i == n - 1 and first_taken and n > 1:
            return 0
        skip = f(i + 1, first_taken)
        take = a[i] + f(i + 2, first_taken or i == 0)
        return max(skip, take)

    return str(f(0, False))


# ── grids ────────────────────────────────────────────────────────

def _paths(inp):
    m, n = ints(lines(inp)[0])
    row = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] = (row[j] + row[j - 1]) % MOD
    return str(row[-1])


def _paths_brute(inp):
    m, n = ints(lines(inp)[0])

    @lru_cache(None)
    def f(i, j):
        if i == m - 1 and j == n - 1:
            return 1
        total = 0
        if i + 1 < m:
            total += f(i + 1, j)
        if j + 1 < n:
            total += f(i, j + 1)
        return total % MOD

    return str(f(0, 0))


def _obst(inp):
    g, r, c = _grid_ints(inp)
    dp = [0] * c
    dp[0] = 1 if g[0][0] == 0 else 0
    for i in range(r):
        for j in range(c):
            if g[i][j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] = (dp[j] + dp[j - 1]) % MOD
    return str(dp[-1])


def _obst_brute(inp):
    g, r, c = _grid_ints(inp)

    @lru_cache(None)
    def f(i, j):
        if i >= r or j >= c or g[i][j] == 1:
            return 0
        if i == r - 1 and j == c - 1:
            return 1
        return (f(i + 1, j) + f(i, j + 1)) % MOD

    return str(f(0, 0))


def _minpath(inp):
    g, r, c = _grid_ints(inp)
    dp = [INF] * c
    dp[0] = 0
    for i in range(r):
        for j in range(c):
            left = dp[j - 1] if j > 0 else INF
            dp[j] = g[i][j] + min(dp[j], left)
    return str(dp[-1])


def _minpath_brute(inp):
    g, r, c = _grid_ints(inp)

    @lru_cache(None)
    def f(i, j):
        if i == r - 1 and j == c - 1:
            return g[i][j]
        opts = []
        if i + 1 < r:
            opts.append(f(i + 1, j))
        if j + 1 < c:
            opts.append(f(i, j + 1))
        return g[i][j] + min(opts)

    return str(f(0, 0))


def _tri_parse(inp):
    ls = lines(inp)
    n = int(ls[0])
    return [ints(ls[1 + i]) for i in range(n)]


def _tri(inp):
    t = _tri_parse(inp)
    dp = t[-1][:]
    for i in range(len(t) - 2, -1, -1):
        dp = [t[i][j] + min(dp[j], dp[j + 1]) for j in range(i + 1)]
    return str(dp[0])


def _tri_brute(inp):
    t = _tri_parse(inp)

    @lru_cache(None)
    def f(i, j):
        if i == len(t) - 1:
            return t[i][j]
        return t[i][j] + min(f(i + 1, j), f(i + 1, j + 1))

    return str(f(0, 0))


def _tri_text(rows):
    return f"{len(rows)}\n" + "\n".join(join(r) for r in rows)


def _fall_parse(inp):
    ls = lines(inp)
    n = int(ls[0])
    return [ints(ls[1 + i]) for i in range(n)]


def _fall(inp):
    g = _fall_parse(inp)
    n = len(g)
    dp = g[0][:]
    for i in range(1, n):
        dp = [g[i][j] + min(dp[max(0, j - 1): j + 2]) for j in range(n)]
    return str(min(dp))


def _fall_brute(inp):
    g = _fall_parse(inp)
    n = len(g)

    @lru_cache(None)
    def f(i, j):
        if j < 0 or j >= n:
            return INF
        if i == n - 1:
            return g[i][j]
        return g[i][j] + min(f(i + 1, j - 1), f(i + 1, j), f(i + 1, j + 1))

    return str(min(f(0, j) for j in range(n)))


def _square_text(rows):
    return f"{len(rows)}\n" + "\n".join(join(r) for r in rows)


# ── subsets / knapsack ───────────────────────────────────────────

def _subset(inp):
    ls = lines(inp)
    a, t = ints(ls[0]), int(ls[1])
    can = 1  # bitset: bit s set ⇔ sum s reachable
    for x in a:
        can |= can << x
    return boolstr(bool(can >> t & 1))


def _subset_brute(inp):
    ls = lines(inp)
    a, t = ints(ls[0]), int(ls[1])

    @lru_cache(None)
    def f(i, rem):
        if rem == 0:
            return True
        if i == len(a) or rem < 0:
            return False
        return f(i + 1, rem - a[i]) or f(i + 1, rem)

    return boolstr(f(0, t))


def _partition(inp):
    a = ints(lines(inp)[0])
    s = sum(a)
    if s % 2:
        return "false"
    reach = {0}
    for x in a:
        reach |= {v + x for v in reach if v + x <= s // 2}
    return boolstr(s // 2 in reach)


def _partition_brute(inp):
    a = ints(lines(inp)[0])
    s = sum(a)
    if s % 2:
        return "false"
    return _subset_brute(f"{join(a)}\n{s // 2}")


def _mindiff(inp):
    a = ints(lines(inp)[0])
    s = sum(a)
    reach = 1
    for x in a:
        reach |= reach << x
    return str(min(abs(s - 2 * v) for v in range(s + 1) if reach >> v & 1))


def _mindiff_brute(inp):
    a = ints(lines(inp)[0])
    s = sum(a)

    @lru_cache(None)
    def f(i, cur):
        if i == len(a):
            return abs(s - 2 * cur)
        return min(f(i + 1, cur + a[i]), f(i + 1, cur))

    return str(f(0, 0))


def _countk(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    dp = [0] * (k + 1)
    dp[0] = 1
    for x in a:
        for s in range(k, x - 1, -1):
            dp[s] = (dp[s] + dp[s - x]) % MOD
    return str(dp[k])


def _countk_brute(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])

    @lru_cache(None)
    def f(i, rem):
        if i == len(a):
            return 1 if rem == 0 else 0
        total = f(i + 1, rem)
        if a[i] <= rem:
            total += f(i + 1, rem - a[i])
        return total % MOD

    return str(f(0, k))


def _knap_parse(inp):
    ls = lines(inp)
    return ints(ls[0]), ints(ls[1]), int(ls[2])


def _knap01(inp):
    w, v, cap = _knap_parse(inp)
    dp = [0] * (cap + 1)
    for wi, vi in zip(w, v):
        for c in range(cap, wi - 1, -1):
            dp[c] = max(dp[c], dp[c - wi] + vi)
    return str(dp[cap])


def _knap01_brute(inp):
    w, v, cap = _knap_parse(inp)

    @lru_cache(None)
    def f(i, c):
        if i == len(w):
            return 0
        best = f(i + 1, c)
        if w[i] <= c:
            best = max(best, v[i] + f(i + 1, c - w[i]))
        return best

    return str(f(0, cap))


def _knapu(inp):
    w, v, cap = _knap_parse(inp)
    dp = [0] * (cap + 1)
    for c in range(1, cap + 1):
        for wi, vi in zip(w, v):
            if wi <= c:
                dp[c] = max(dp[c], dp[c - wi] + vi)
    return str(dp[cap])


def _knapu_brute(inp):
    w, v, cap = _knap_parse(inp)

    @lru_cache(None)
    def f(i, c):
        if i == len(w):
            return 0
        best = f(i + 1, c)
        if w[i] <= c:
            best = max(best, v[i] + f(i, c - w[i]))
        return best

    return str(f(0, cap))


def _knap_text(w, v, cap):
    return f"{join(w)}\n{join(v)}\n{cap}"


def _ways(inp):
    ls = lines(inp)
    coins, amt = ints(ls[0]), int(ls[1])
    dp = [0] * (amt + 1)
    dp[0] = 1
    for c in coins:
        for s in range(c, amt + 1):
            dp[s] = (dp[s] + dp[s - c]) % MOD
    return str(dp[amt])


def _ways_brute(inp):
    ls = lines(inp)
    coins, amt = ints(ls[0]), int(ls[1])

    @lru_cache(None)
    def f(i, rem):
        if rem == 0:
            return 1
        if i == len(coins):
            return 0
        total = f(i + 1, rem)
        if coins[i] <= rem:
            total += f(i, rem - coins[i])
        return total % MOD

    return str(f(0, amt))


def _rod(inp):
    p = ints(lines(inp)[0])
    n = len(p)
    dp = [0] * (n + 1)
    for length in range(1, n + 1):
        dp[length] = max(p[cut - 1] + dp[length - cut] for cut in range(1, length + 1))
    return str(dp[n])


def _rod_brute(inp):
    p = ints(lines(inp)[0])

    @lru_cache(None)
    def f(rem):
        if rem == 0:
            return 0
        return max(p[c - 1] + f(rem - c) for c in range(1, rem + 1))

    return str(f(len(p)))


# ── strings ──────────────────────────────────────────────────────

def _two(inp):
    ls = lines(inp)
    return ls[0], ls[1]


def _lcs_len(a, b):
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0]
        for j, d in enumerate(b):
            cur.append(prev[j] + 1 if ch == d else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def _lcs(inp):
    a, b = _two(inp)
    return str(_lcs_len(a, b))


def _lcs_rec(a, b):
    @lru_cache(None)
    def f(i, j):
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + f(i + 1, j + 1)
        return max(f(i + 1, j), f(i, j + 1))

    return f(0, 0)


def _lcs_brute(inp):
    a, b = _two(inp)
    return str(_lcs_rec(a, b))


def _lcsub(inp):
    a, b = _two(inp)
    best = 0
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0] * (len(b) + 1)
        for j, d in enumerate(b):
            if ch == d:
                cur[j + 1] = prev[j] + 1
                best = max(best, cur[j + 1])
        prev = cur
    return str(best)


def _lcsub_brute(inp):
    a, b = _two(inp)
    subs = {a[i:j] for i in range(len(a)) for j in range(i + 1, len(a) + 1)}
    return str(max((len(s) for s in subs if s in b), default=0))


def _lps(inp):
    s = lines(inp)[0]
    return str(_lcs_len(s, s[::-1]))


def _lps_rec(s):
    @lru_cache(None)
    def f(i, j):
        if i > j:
            return 0
        if i == j:
            return 1
        if s[i] == s[j]:
            return 2 + f(i + 1, j - 1)
        return max(f(i + 1, j), f(i, j - 1))

    return f(0, len(s) - 1)


def _lps_brute(inp):
    return str(_lps_rec(lines(inp)[0]))


def _mininsert(inp):
    s = lines(inp)[0]
    return str(len(s) - _lcs_len(s, s[::-1]))


def _mininsert_brute(inp):
    s = lines(inp)[0]

    @lru_cache(None)
    def f(i, j):
        if i >= j:
            return 0
        if s[i] == s[j]:
            return f(i + 1, j - 1)
        return 1 + min(f(i + 1, j), f(i, j - 1))

    return str(f(0, len(s) - 1))


def _edit(inp):
    a, b = _two(inp)
    prev = list(range(len(b) + 1))
    for i, ch in enumerate(a, 1):
        cur = [i]
        for j, d in enumerate(b, 1):
            cur.append(prev[j - 1] if ch == d else 1 + min(prev[j - 1], prev[j], cur[j - 1]))
        prev = cur
    return str(prev[-1])


def _edit_brute(inp):
    a, b = _two(inp)

    @lru_cache(None)
    def f(i, j):
        if i == len(a):
            return len(b) - j
        if j == len(b):
            return len(a) - i
        if a[i] == b[j]:
            return f(i + 1, j + 1)
        return 1 + min(f(i + 1, j + 1), f(i + 1, j), f(i, j + 1))

    return str(f(0, 0))


def _distinct(inp):
    s, t = _two(inp)
    dp = [0] * (len(t) + 1)
    dp[0] = 1
    for ch in s:
        for j in range(len(t), 0, -1):
            if t[j - 1] == ch:
                dp[j] = (dp[j] + dp[j - 1]) % MOD
    return str(dp[-1])


def _distinct_brute(inp):
    s, t = _two(inp)

    @lru_cache(None)
    def f(i, j):
        if j == len(t):
            return 1
        if i == len(s):
            return 0
        total = f(i + 1, j)
        if s[i] == t[j]:
            total += f(i + 1, j + 1)
        return total % MOD

    return str(f(0, 0))


def _wild(inp):
    s, p = _two(inp)
    prev = [False] * (len(p) + 1)
    prev[0] = True
    for j in range(1, len(p) + 1):
        prev[j] = prev[j - 1] and p[j - 1] == "*"
    for ch in s:
        cur = [False] * (len(p) + 1)
        for j in range(1, len(p) + 1):
            pc = p[j - 1]
            if pc == "*":
                cur[j] = cur[j - 1] or prev[j]
            elif pc == "?" or pc == ch:
                cur[j] = prev[j - 1]
        prev = cur
    return boolstr(prev[-1])


def _wild_brute(inp):
    s, p = _two(inp)

    @lru_cache(None)
    def f(i, j):
        if j == len(p):
            return i == len(s)
        if p[j] == "*":
            return f(i, j + 1) or (i < len(s) and f(i + 1, j))
        return i < len(s) and (p[j] == "?" or p[j] == s[i]) and f(i + 1, j + 1)

    return boolstr(f(0, 0))


def _rand_pattern(r, s):
    """Pattern that sometimes matches s: mutate s with ? and * and the odd typo."""
    out = []
    i = 0
    while i < len(s):
        roll = r.random()
        if roll < 0.15:
            out.append("?")
            i += 1
        elif roll < 0.28:
            out.append("*")
            i += r.randint(0, 3)
        elif roll < 0.33:
            out.append(r.choice("abc"))
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out) or "*"


# ── stocks ───────────────────────────────────────────────────────

def _prices(inp):
    return ints(lines(inp)[0])


def _stock2(inp):
    p = _prices(inp)
    return str(sum(max(0, p[i] - p[i - 1]) for i in range(1, len(p))))


def _stock_k_dp(p, k):
    if k == 0 or len(p) < 2:
        return 0
    buy = [-INF] * (k + 1)
    sell = [0] * (k + 1)
    for x in p:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - x)
            sell[t] = max(sell[t], buy[t] + x)
    return sell[k]


def _stock_k_brute(p, k):
    @lru_cache(None)
    def f(i, holding, left):
        if i == len(p) or (left == 0 and not holding):
            return 0
        best = f(i + 1, holding, left)
        if holding:
            best = max(best, p[i] + f(i + 1, False, left - 1))
        else:
            best = max(best, -p[i] + f(i + 1, True, left))
        return best

    return f(0, False, k)


def _stock2_brute(inp):
    p = _prices(inp)
    return str(_stock_k_brute(p, len(p)))


def _stock3(inp):
    return str(_stock_k_dp(_prices(inp), 2))


def _stock3_brute(inp):
    return str(_stock_k_brute(_prices(inp), 2))


def _stock4(inp):
    ls = lines(inp)
    return str(_stock_k_dp(ints(ls[0]), int(ls[1])))


def _stock4_brute(inp):
    ls = lines(inp)
    return str(_stock_k_brute(ints(ls[0]), int(ls[1])))


def _cool(inp):
    p = _prices(inp)
    hold, sold, rest = -INF, 0, 0
    for x in p:
        hold, sold, rest = max(hold, rest - x), hold + x, max(rest, sold)
    return str(max(sold, rest))


def _cool_brute(inp):
    p = _prices(inp)

    @lru_cache(None)
    def f(i, holding):
        if i >= len(p):
            return 0
        best = f(i + 1, holding)
        if holding:
            best = max(best, p[i] + f(i + 2, False))
        else:
            best = max(best, -p[i] + f(i + 1, True))
        return best

    return str(f(0, False))


def _fee(inp):
    ls = lines(inp)
    p, fee = ints(ls[0]), int(ls[1])
    hold, free = -INF, 0
    for x in p:
        hold, free = max(hold, free - x), max(free, hold + x - fee)
    return str(free)


def _fee_brute(inp):
    ls = lines(inp)
    p, fee = ints(ls[0]), int(ls[1])

    @lru_cache(None)
    def f(i, holding):
        if i == len(p):
            return 0
        best = f(i + 1, holding)
        if holding:
            best = max(best, p[i] - fee + f(i + 1, False))
        else:
            best = max(best, -p[i] + f(i + 1, True))
        return best

    return str(f(0, False))


# ── LIS family ───────────────────────────────────────────────────

def _nlis(inp):
    a = ints(lines(inp)[0])
    n = len(a)
    length = [1] * n
    count = [1] * n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i]:
                if length[j] + 1 > length[i]:
                    length[i], count[i] = length[j] + 1, count[j]
                elif length[j] + 1 == length[i]:
                    count[i] = (count[i] + count[j]) % MOD
    best = max(length)
    return str(sum(c for l, c in zip(length, count) if l == best) % MOD)


def _nlis_brute(inp):
    a = ints(lines(inp)[0])
    n = len(a)

    @lru_cache(None)
    def f(i):  # (length, count) of LIS starting at i
        best, cnt = 1, 1
        for j in range(i + 1, n):
            if a[j] > a[i]:
                l, c = f(j)
                if l + 1 > best:
                    best, cnt = l + 1, c
                elif l + 1 == best:
                    cnt += c
        return best, cnt % MOD

    res = [f(i) for i in range(n)]
    top = max(l for l, _ in res)
    return str(sum(c for l, c in res if l == top) % MOD)


# ── interval / partition ─────────────────────────────────────────

def _mcm(inp):
    d = ints(lines(inp)[0])
    n = len(d) - 1
    dp = [[0] * n for _ in range(n)]
    for span in range(2, n + 1):
        for i in range(n - span + 1):
            j = i + span - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] + d[i] * d[k + 1] * d[j + 1] for k in range(i, j))
    return str(dp[0][n - 1])


def _mcm_brute(inp):
    d = ints(lines(inp)[0])

    @lru_cache(None)
    def f(i, j):  # matrices i..j (1-based on dims)
        if i == j:
            return 0
        return min(f(i, k) + f(k + 1, j) + d[i - 1] * d[k] * d[j] for k in range(i, j))

    return str(f(1, len(d) - 1))


def _burst(inp):
    a = [1] + ints(lines(inp)[0]) + [1]
    n = len(a)
    dp = [[0] * n for _ in range(n)]
    for gap in range(2, n):
        for i in range(n - gap):
            j = i + gap
            dp[i][j] = max(dp[i][k] + dp[k][j] + a[i] * a[k] * a[j] for k in range(i + 1, j))
    return str(dp[0][n - 1])


def _burst_brute(inp):
    a = tuple(ints(lines(inp)[0]))

    @lru_cache(None)
    def f(rest):  # try every balloon to burst next
        if not rest:
            return 0
        best = 0
        for i, x in enumerate(rest):
            left = rest[i - 1] if i > 0 else 1
            right = rest[i + 1] if i + 1 < len(rest) else 1
            best = max(best, left * x * right + f(rest[:i] + rest[i + 1:]))
        return best

    if len(a) > 9:  # permutations blow up — fall back to the interval recursion
        b = (1,) + a + (1,)

        @lru_cache(None)
        def g(i, j):
            return max((g(i, k) + g(k, j) + b[i] * b[k] * b[j] for k in range(i + 1, j)), default=0)

        return str(g(0, len(b) - 1))
    return str(f(a))


def _cuts(inp):
    s = lines(inp)[0]
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
    dp = [0] * n
    for j in range(n):
        if pal[0][j]:
            dp[j] = 0
        else:
            dp[j] = min(dp[i - 1] + 1 for i in range(1, j + 1) if pal[i][j])
    return str(dp[-1])


def _cuts_brute(inp):
    s = lines(inp)[0]

    @lru_cache(None)
    def f(i):  # min pieces for s[i:]
        if i == len(s):
            return 0
        return min(1 + f(j) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])

    return str(f(0) - 1)


def _maxsq(inp):
    g, r, c = _bits_grid(inp)
    best = 0
    prev = [0] * (c + 1)
    for i in range(r):
        cur = [0] * (c + 1)
        for j in range(c):
            if g[i][j]:
                cur[j + 1] = 1 + min(prev[j], prev[j + 1], cur[j])
                best = max(best, cur[j + 1])
        prev = cur
    return str(best * best)


def _maxsq_brute(inp):
    g, r, c = _bits_grid(inp)
    best = 0
    for i in range(r):
        for j in range(c):
            k = 1
            while i + k <= r and j + k <= c and all(g[x][y] for x in range(i, i + k) for y in range(j, j + k)):
                best = max(best, k)
                k += 1
    return str(best * best)


def _cntsq(inp):
    g, r, c = _bits_grid(inp)
    total = 0
    prev = [0] * (c + 1)
    for i in range(r):
        cur = [0] * (c + 1)
        for j in range(c):
            if g[i][j]:
                cur[j + 1] = 1 + min(prev[j], prev[j + 1], cur[j])
                total += cur[j + 1]
        prev = cur
    return str(total)


def _cntsq_brute(inp):
    g, r, c = _bits_grid(inp)
    total = 0
    for i in range(r):
        for j in range(c):
            k = 1
            while i + k <= r and j + k <= c and all(g[x][y] for x in range(i, i + k) for y in range(j, j + k)):
                total += 1
                k += 1
    return str(total)


def _rand_bits(r, rows, cols, p=0.7):
    return [[1 if r.random() < p else 0 for _ in range(cols)] for _ in range(rows)]


def _rand_obst(r, rows, cols, p=0.2):
    g = [[1 if r.random() < p else 0 for _ in range(cols)] for _ in range(rows)]
    return g


# ── problems ─────────────────────────────────────────────────────

PROBLEMS = [
    Problem(
        title="Frog Jump",
        difficulty="EASY",
        topics=["DP", "Array"],
        description="""A frog sits on stone `0` and wants to reach the last stone. Stone `i` has height `h[i]`. From stone `i` it can jump to stone `i + 1` or stone `i + 2`, and a jump from `i` to `j` costs `|h[i] − h[j]|` energy.

Print the minimum total energy needed to reach the last stone.

**Input:** one line with the heights `h[0] … h[n−1]`.

**Output:** the minimum total energy.""",
        constraints=["1 <= n <= 10^5", "0 <= h[i] <= 10^4"],
        solve=_frog,
        brute=_frog_brute,
        examples=[("10 20 30 10", "0 → 1 → 3 costs 10 + 10 = 20."), ("30 10 60 10 60 50", "0 → 2 → 4 → 5 costs 30 + 0 + 10 = 40.")],
        tests=lambda r: ["7", "5 5", "1 100", "10 30 20", "0 0 0 0 0"]
        + [join(rand_ints(r, r.randint(5, 30), 0, 100)) for _ in range(4)]
        + [join(rand_ints(r, 4000, 0, 10000))],
    ),
    Problem(
        title="Frog Jump with K Steps",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Same frog, longer legs. From stone `i` the frog can jump to any of the next `k` stones (`i + 1` up to `i + k`). A jump from `i` to `j` costs `|h[i] − h[j]|`.

Print the minimum total energy to get from stone `0` to the last stone.

**Input:** the heights on the first line, `k` on the second.

**Output:** the minimum total energy.""",
        constraints=["1 <= n <= 10^4", "1 <= k <= 100", "0 <= h[i] <= 10^4"],
        solve=_frogk,
        brute=_frogk_brute,
        examples=[("10 30 40 50 20\n3", "0 → 1 → 4 costs 20 + 10 = 30."), ("10 20 10\n1", "With k = 1 every stone is visited: 10 + 10 = 20.")],
        tests=lambda r: ["5\n3", "1 9\n1", "1 9 1\n2", "4 8 2 9 1 7\n10", "3 3 3 3\n2"]
        + [f"{join(rand_ints(r, r.randint(5, 25), 0, 100))}\n{r.randint(1, 6)}" for _ in range(4)]
        + [f"{join(rand_ints(r, 2000, 0, 10000))}\n{30}"],
    ),
    Problem(
        title="House Robber II",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Houses stand in a **circle**, and house `i` holds `a[i]` coins. You can't take from two adjacent houses — and because it's a circle, the first and last houses are adjacent too.

Print the most coins you can collect.

**Input:** one line with `a[0] … a[n−1]`.

**Output:** the maximum total.""",
        constraints=["1 <= n <= 10^5", "0 <= a[i] <= 10^4"],
        solve=_rob2,
        brute=_rob2_brute,
        examples=[("2 3 2", "Houses 0 and 2 are neighbours in the circle, so the best is 3."), ("1 2 3 1", "Take houses 0 and 2: 1 + 3 = 4.")],
        tests=lambda r: ["5", "4 9", "9 4", "1 2 3", "200 3 140 20 10", "0 0 0 0"]
        + [join(rand_ints(r, r.randint(4, 30), 0, 100)) for _ in range(4)]
        + [join(rand_ints(r, 4000, 0, 10000))],
    ),
    Problem(
        title="Unique Grid Paths",
        difficulty="MEDIUM",
        topics=["DP", "Math", "Matrix"],
        description="""A robot starts in the top-left cell of an `m × n` grid and wants to reach the bottom-right cell. It may only move **right** or **down**.

Print how many different paths it can take, modulo `1000000007`.

**Input:** one line with `m` and `n`.

**Output:** the number of paths modulo `1000000007`.""",
        constraints=["1 <= m, n <= 1000"],
        solve=_paths,
        brute=_paths_brute,
        examples=[("3 7", "28 ways to arrange 2 downs and 6 rights."), ("3 2", "Right-down-down, down-right-down, down-down-right.")],
        tests=lambda r: ["1 1", "1 10", "10 1", "2 2", "10 10", "18 18", "100 100", "1000 1000", "1 1000"]
        + [f"{r.randint(1, 60)} {r.randint(1, 60)}" for _ in range(2)],
    ),
    Problem(
        title="Unique Paths with Obstacles",
        difficulty="MEDIUM",
        topics=["DP", "Matrix"],
        description="""A robot moves only **right** or **down** from the top-left to the bottom-right cell of a grid. Cells marked `1` are blocked; `0` cells are free. If the start or the finish is blocked there are no paths.

Print the number of paths that avoid every blocked cell, modulo `1000000007`.

**Input:** `r c` on the first line, then `r` lines of `c` space-separated values (`0` or `1`).

**Output:** the number of paths modulo `1000000007`.""",
        constraints=["1 <= r, c <= 100"],
        solve=_obst,
        brute=_obst_brute,
        examples=[("3 3\n0 0 0\n0 1 0\n0 0 0", "Go around the centre rock: over the top or along the bottom."), ("2 2\n0 1\n0 0", "Only down, then right.")],
        tests=lambda r: ["1 1\n0", "1 1\n1", "2 2\n1 0\n0 0", "2 2\n0 0\n0 1", "1 5\n0 0 1 0 0", "3 4\n0 0 0 0\n0 0 0 0\n0 0 0 0"]
        + [_grid_text(r, _rand_obst(r, r.randint(2, 8), r.randint(2, 8)) ) for _ in range(4)]
        + [_grid_text(r, [[0] * 100 for _ in range(100)]), _grid_text(r, _rand_obst(r, 80, 80, 0.1))],
    ),
    Problem(
        title="Minimum Path Sum",
        difficulty="MEDIUM",
        topics=["DP", "Matrix"],
        description="""Each cell of a grid holds a non-negative cost. Walk from the top-left to the bottom-right cell, moving only **right** or **down**, and add up the costs of every cell you step on (including the first and last).

Print the smallest possible total.

**Input:** `r c` on the first line, then `r` lines of `c` space-separated costs.

**Output:** the minimum path sum.""",
        constraints=["1 <= r, c <= 200", "0 <= cost <= 100"],
        solve=_minpath,
        brute=_minpath_brute,
        examples=[("3 3\n1 3 1\n1 5 1\n4 2 1", "1 → 3 → 1 → 1 → 1 = 7."), ("2 3\n1 2 3\n4 5 6", "1 → 2 → 3 → 6 = 12.")],
        tests=lambda r: ["1 1\n5", "1 4\n1 2 3 4", "4 1\n4\n3\n2\n1", "2 2\n0 0\n0 0"]
        + [_grid_text(r, [rand_ints(r, cc, 0, 9) for _ in range(rr)]) for rr, cc in [(3, 5), (5, 3), (6, 6), (8, 4)]]
        + [_grid_text(r, [rand_ints(r, 120, 0, 100) for _ in range(80)])],
    ),
    Problem(
        title="Triangle Minimum Path",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""A triangle of numbers has `i + 1` values on row `i`. Start at the top and move down one row at a time; from position `j` you can step to position `j` or `j + 1` on the next row.

Print the minimum sum of a path from the top to the bottom row.

**Input:** `n` (the number of rows) on the first line, then row `i` with `i + 1` space-separated integers.

**Output:** the minimum path sum.""",
        constraints=["1 <= n <= 200", "-10^4 <= value <= 10^4"],
        solve=_tri,
        brute=_tri_brute,
        examples=[("4\n2\n3 4\n6 5 7\n4 1 8 3", "2 → 3 → 5 → 1 = 11."), ("1\n-10", "A single value.")],
        tests=lambda r: ["2\n1\n2 3", "3\n-1\n2 3\n1 -1 -3", "3\n0\n0 0\n0 0 0"]
        + [_tri_text([rand_ints(r, i + 1, -20, 20) for i in range(n)]) for n in (4, 5, 6, 8, 10)]
        + [_tri_text([rand_ints(r, i + 1, -100, 100) for i in range(115)])],
    ),
    Problem(
        title="Minimum Falling Path Sum",
        difficulty="MEDIUM",
        topics=["DP", "Matrix"],
        description="""In an `n × n` matrix, a falling path picks one cell in every row, starting anywhere in the first row. From column `j` the next row's cell must be in column `j − 1`, `j` or `j + 1`.

Print the smallest possible sum of a falling path.

**Input:** `n` on the first line, then `n` lines of `n` space-separated integers.

**Output:** the minimum falling path sum.""",
        constraints=["1 <= n <= 100", "-100 <= value <= 100"],
        solve=_fall,
        brute=_fall_brute,
        examples=[("3\n2 1 3\n6 5 4\n7 8 9", "1 → 4 → 8 = 13 (or 1 → 5 → 7)."), ("2\n-19 57\n-40 -5", "-19 → -40 = -59.")],
        tests=lambda r: ["1\n7", "1\n-7", "2\n1 2\n3 4", "3\n0 0 0\n0 0 0\n0 0 0"]
        + [_square_text([rand_ints(r, n, -50, 50) for _ in range(n)]) for n in (3, 4, 5, 6, 8)]
        + [_square_text([rand_ints(r, 80, -100, 100) for _ in range(80)])],
    ),
    Problem(
        title="Subset Sum Exists",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Given an array of positive integers and a `target`, decide whether some subset of the array (any selection of elements, each used at most once) adds up to exactly `target`. The empty subset adds up to `0`.

**Input:** the array on the first line, `target` on the second.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 200", "1 <= a[i] <= 1000", "0 <= target <= 10^5"],
        solve=_subset,
        brute=_subset_brute,
        examples=[("3 34 4 12 5 2\n9", "4 + 5 = 9."), ("3 34 4 12 5 2\n30", "No combination reaches 30.")],
        tests=lambda r: ["5\n0", "5\n5", "5\n4", "1 1 1 1\n4", "2 4 6\n7", "7 3 2 5 8\n14"]
        + [f"{join(rand_ints(r, r.randint(4, 15), 1, 30))}\n{r.randint(0, 120)}" for _ in range(4)]
        + [f"{join(rand_ints(r, 200, 1, 1000))}\n{r.randint(1000, 90000)}"],
    ),
    Problem(
        title="Partition Equal Subset Sum",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Can the array be split into two groups with exactly the same sum? Every element must go into one of the two groups.

**Input:** one line of positive integers.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 200", "1 <= a[i] <= 100"],
        solve=_partition,
        brute=_partition_brute,
        examples=[("1 5 11 5", "{1, 5, 5} and {11} both sum to 11."), ("1 2 3 5", "The total 11 is odd.")],
        tests=lambda r: ["1", "2 2", "1 2", "3 3 3 3", "100 1 1 98", "2 2 3 5"]
        + [join(rand_ints(r, r.randint(4, 16), 1, 20)) for _ in range(4)]
        + [join(rand_ints(r, 200, 1, 100))],
    ),
    Problem(
        title="Minimum Subset Sum Difference",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Split the array into two groups (either may be empty) so that the absolute difference between their sums is as small as possible. Every element goes into exactly one group.

**Input:** one line of non-negative integers.

**Output:** the minimum possible difference.""",
        constraints=["1 <= n <= 200", "0 <= a[i] <= 500"],
        solve=_mindiff,
        brute=_mindiff_brute,
        examples=[("1 6 11 5", "{1, 5, 6} = 12 and {11} = 11, difference 1."), ("3 9 7 3", "{3, 7} and {9, 3}: 10 vs 12 → 2.")],
        tests=lambda r: ["7", "0", "4 4", "1 100", "0 0 0", "1 2 3 4 5"]
        + [join(rand_ints(r, r.randint(4, 15), 0, 40)) for _ in range(4)]
        + [join(rand_ints(r, 200, 0, 500))],
    ),
    Problem(
        title="Count Subsets with Sum K",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Count the subsets of the array whose elements add up to exactly `k`. Subsets are chosen by **position**, so equal values at different positions count as different subsets (and a `0` can be included or not). When `k = 0` the empty subset counts.

Print the count modulo `1000000007`.

**Input:** the array on the first line, `k` on the second.

**Output:** the number of subsets modulo `1000000007`.""",
        constraints=["1 <= n <= 200", "0 <= a[i] <= 1000", "0 <= k <= 10^4"],
        solve=_countk,
        brute=_countk_brute,
        examples=[("1 2 2 3\n3", "{1, 2}, {1, 2'} and {3}."), ("0 1\n1", "{1} and {0, 1}.")],
        tests=lambda r: ["5\n0", "5\n5", "0 0 0\n0", "1 1 1 1\n2", "2 4 6\n5", "3 3 3\n6"]
        + [f"{join(rand_ints(r, r.randint(4, 14), 0, 10))}\n{r.randint(0, 30)}" for _ in range(4)]
        + [f"{join(rand_ints(r, 200, 0, 60))}\n{5000}"],
    ),
    Problem(
        title="0/1 Knapsack",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""You have `n` items; item `i` weighs `w[i]` and is worth `v[i]`. Your bag holds at most `W` weight. Each item can be taken **at most once**.

Print the largest total value you can carry.

**Input:** weights on the first line, values on the second, capacity `W` on the third.

**Output:** the maximum total value.""",
        constraints=["1 <= n <= 200", "1 <= w[i] <= 1000", "0 <= v[i] <= 10^4", "0 <= W <= 10^4"],
        solve=_knap01,
        brute=_knap01_brute,
        examples=[("1 3 4 5\n1 4 5 7\n7", "Items of weight 3 and 4 give 4 + 5 = 9."), ("4 5 1\n1 2 3\n4", "Only one item fits at a time; the weight-1 item is worth the most: 3.")],
        tests=lambda r: [_knap_text([5], [10], 4), _knap_text([5], [10], 5), _knap_text([1, 2, 3], [6, 10, 12], 0), _knap_text([1, 1, 1], [3, 2, 1], 2)]
        + [_knap_text(rand_ints(r, n, 1, 15), rand_ints(r, n, 0, 40), r.randint(0, 40)) for n in (4, 6, 8, 10, 12)]
        + [_knap_text(rand_ints(r, 150, 1, 1000), rand_ints(r, 150, 0, 10000), 5000)],
    ),
    Problem(
        title="Coin Change II",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Given coin denominations (unlimited supply of each) and an `amount`, count the number of **combinations** of coins that add up to the amount. Order doesn't matter: `1 + 2` and `2 + 1` are the same combination. An amount of `0` has exactly one combination (use no coins).

Print the count modulo `1000000007`.

**Input:** the distinct coin values on the first line, `amount` on the second.

**Output:** the number of combinations modulo `1000000007`.""",
        constraints=["1 <= coins <= 100", "1 <= coin <= 5000", "0 <= amount <= 10^4"],
        solve=_ways,
        brute=_ways_brute,
        examples=[("1 2 5\n5", "5, 2+2+1, 2+1+1+1, 1+1+1+1+1."), ("2\n3", "3 can't be made from 2s.")],
        tests=lambda r: ["7\n0", "3\n9", "2 3\n1", "1\n10", "10\n10", "3 5 7 8 9 10 11\n500"]
        + [f"{join(sorted(r.sample(range(1, 20), r.randint(1, 5))))}\n{r.randint(0, 60)}" for _ in range(4)]
        + [f"{join(sorted(r.sample(range(1, 300), 40)))}\n10000"],
    ),
    Problem(
        title="Unbounded Knapsack",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Like the 0/1 knapsack, but you have an **unlimited** supply of every item. Item `i` weighs `w[i]` and is worth `v[i]`; the bag holds at most `W`.

Print the largest total value you can carry.

**Input:** weights on the first line, values on the second, capacity `W` on the third.

**Output:** the maximum total value.""",
        constraints=["1 <= n <= 100", "1 <= w[i] <= 1000", "0 <= v[i] <= 10^4", "0 <= W <= 10^4"],
        solve=_knapu,
        brute=_knapu_brute,
        examples=[("2 4 6\n5 11 13\n10", "Two of weight 4 plus one of weight 2: 11 + 11 + 5 = 27."), ("5\n10\n4", "Nothing fits.")],
        tests=lambda r: [_knap_text([1], [1], 0), _knap_text([1], [7], 9), _knap_text([3, 4], [5, 7], 7), _knap_text([2, 3], [1, 100], 5)]
        + [_knap_text(rand_ints(r, n, 1, 12), rand_ints(r, n, 0, 30), r.randint(0, 40)) for n in (3, 5, 6, 8, 10)]
        + [_knap_text(rand_ints(r, 60, 1, 1000), rand_ints(r, 60, 0, 10000), 8000)],
    ),
    Problem(
        title="Rod Cutting",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""A rod of length `n` can be cut into pieces of whole lengths. A piece of length `i` sells for `price[i]` (the first value is the price of length 1, the second of length 2, and so on). You may also sell the rod uncut.

Print the maximum money you can make from a rod of length `n`, where `n` is the number of prices given.

**Input:** one line with `price[1] … price[n]`.

**Output:** the maximum revenue.""",
        constraints=["1 <= n <= 1000", "0 <= price <= 10^5"],
        solve=_rod,
        brute=_rod_brute,
        examples=[("1 5 8 9 10 17 17 20", "Cut into 2 + 6: 5 + 17 = 22."), ("3 5 8 9 10 17 17 20", "Eight pieces of length 1: 8 × 3 = 24.")],
        tests=lambda r: ["7", "1 1", "1 10", "0 0 0", "2 5 7 8"]
        + [join(rand_ints(r, r.randint(3, 15), 0, 50)) for _ in range(4)]
        + [join(sorted(rand_ints(r, 800, 0, 100000)))],
    ),
    Problem(
        title="Longest Common Subsequence",
        difficulty="MEDIUM",
        topics=["DP", "String"],
        description="""A **subsequence** keeps some characters of a string in their original order (not necessarily adjacent). Print the length of the longest subsequence that the two strings share.

**Input:** two lowercase strings, one per line.

**Output:** the length of their longest common subsequence.""",
        constraints=["1 <= |a|, |b| <= 1000"],
        solve=_lcs,
        brute=_lcs_brute,
        examples=[("abcde\nace", "\"ace\" appears in both, in order."), ("abc\ndef", "No shared characters.")],
        tests=lambda r: ["a\na", "a\nb", "aaaa\naa", "abcdef\nfedcba", "xyz\nxyzxyz"]
        + [f"{rand_str(r, r.randint(3, 20), 'abcd')}\n{rand_str(r, r.randint(3, 20), 'abcd')}" for _ in range(4)]
        + [f"{rand_str(r, 600, 'abcdefg')}\n{rand_str(r, 600, 'abcdefg')}"],
    ),
    Problem(
        title="Longest Common Substring",
        difficulty="MEDIUM",
        topics=["DP", "String"],
        description="""A **substring** is a run of consecutive characters. Print the length of the longest substring that appears in both strings (0 if they share no character).

**Input:** two lowercase strings, one per line.

**Output:** the length of their longest common substring.""",
        constraints=["1 <= |a|, |b| <= 1000"],
        solve=_lcsub,
        brute=_lcsub_brute,
        examples=[("abcdxyz\nxyzabcd", "\"abcd\" (or \"xyz\" is shorter)."), ("zxabcdezy\nyzabcdezx", "\"abcdez\" has length 6.")],
        tests=lambda r: ["a\na", "a\nb", "aaaa\naaa", "abc\ncab", "banana\nanana"]
        + [f"{rand_str(r, r.randint(3, 20), 'abc')}\n{rand_str(r, r.randint(3, 20), 'abc')}" for _ in range(4)]
        + [f"{rand_str(r, 600, 'ab')}\n{rand_str(r, 600, 'ab')}"],
    ),
    Problem(
        title="Longest Palindromic Subsequence",
        difficulty="MEDIUM",
        topics=["DP", "String"],
        description="""Print the length of the longest subsequence of `s` that reads the same forwards and backwards. A subsequence keeps characters in order but may skip some.

**Input:** one lowercase string `s`.

**Output:** the length of its longest palindromic subsequence.""",
        constraints=["1 <= |s| <= 1000"],
        solve=_lps,
        brute=_lps_brute,
        examples=[("bbbab", "\"bbbb\"."), ("cbbd", "\"bb\".")],
        tests=lambda r: ["a", "ab", "aa", "racecar", "abcdef", "agbdba"]
        + [rand_str(r, r.randint(4, 25), "abc") for _ in range(4)]
        + [rand_str(r, 700, "abcde")],
    ),
    Problem(
        title="Minimum Insertions to Make Palindrome",
        difficulty="HARD",
        topics=["DP", "String"],
        description="""You may insert characters anywhere in `s`. Print the fewest insertions needed to turn `s` into a palindrome.

Hint: the characters you don't need to touch form the longest palindromic subsequence.

**Input:** one lowercase string `s`.

**Output:** the minimum number of insertions.""",
        constraints=["1 <= |s| <= 1000"],
        solve=_mininsert,
        brute=_mininsert_brute,
        examples=[("mbadm", "Insert to get \"mbdadbm\": 2 insertions."), ("zzazz", "Already a palindrome.")],
        tests=lambda r: ["a", "ab", "abc", "aaaa", "leetcode", "abcba"]
        + [rand_str(r, r.randint(4, 25), "abc") for _ in range(4)]
        + [rand_str(r, 700, "abcd")],
    ),
    Problem(
        title="Edit Distance",
        difficulty="HARD",
        topics=["DP", "String"],
        description="""Turn string `a` into string `b` using three operations, each costing 1: **insert** a character, **delete** a character, or **replace** a character.

Print the minimum number of operations.

**Input:** two lowercase strings, one per line.

**Output:** the minimum number of edits.""",
        constraints=["1 <= |a|, |b| <= 1000"],
        solve=_edit,
        brute=_edit_brute,
        examples=[("horse\nros", "horse → rorse → rose → ros."), ("intention\nexecution", "5 edits.")],
        tests=lambda r: ["a\na", "a\nb", "a\nabc", "abc\na", "kitten\nsitting", "flaw\nlawn"]
        + [f"{rand_str(r, r.randint(2, 15), 'abc')}\n{rand_str(r, r.randint(2, 15), 'abc')}" for _ in range(4)]
        + [f"{rand_str(r, 500, 'abcdef')}\n{rand_str(r, 500, 'abcdef')}"],
    ),
    Problem(
        title="Distinct Subsequences",
        difficulty="HARD",
        topics=["DP", "String"],
        description="""Count how many ways `t` appears as a subsequence of `s`: each way is a different set of positions in `s` that spells `t` in order.

Print the count modulo `1000000007`.

**Input:** `s` on the first line, `t` on the second (both lowercase).

**Output:** the number of ways modulo `1000000007`.""",
        constraints=["1 <= |s|, |t| <= 1000"],
        solve=_distinct,
        brute=_distinct_brute,
        examples=[("rabbbit\nrabbit", "Choose which two of the three b's to use: 3 ways."), ("babgbag\nbag", "5 ways.")],
        tests=lambda r: ["a\na", "a\nb", "a\naa", "aaaa\naa", "abcabc\nabc", "xyz\nxyz"]
        + [f"{rand_str(r, r.randint(5, 25), 'ab')}\n{rand_str(r, r.randint(1, 4), 'ab')}" for _ in range(4)]
        + [f"{rand_str(r, 900, 'ab')}\n{rand_str(r, 40, 'ab')}"],
    ),
    Problem(
        title="Wildcard Matching",
        difficulty="HARD",
        topics=["DP", "String"],
        description="""Check whether a pattern matches a whole string. In the pattern, `?` matches exactly one character and `*` matches any sequence of characters (including none). Every other character matches only itself.

**Input:** the string on the first line (lowercase letters), the pattern on the second (lowercase letters, `?`, `*`).

**Output:** `true` if the pattern matches the entire string, otherwise `false`.""",
        constraints=["1 <= |s|, |p| <= 1000"],
        solve=_wild,
        brute=_wild_brute,
        examples=[("adceb\n*a*b", "`*` takes nothing, `a`, `*` takes \"dce\", `b`."), ("acdcb\na*c?b", "No way to line up the final `?b`.")],
        tests=lambda r: ["a\n*", "a\n?", "a\nb", "aa\na", "aa\n*a", "abc\n***", "abc\n?b?", "abc\na*d"]
        + [(lambda s: f"{s}\n{_rand_pattern(r, s)}")(rand_str(r, r.randint(3, 15), "abc")) for _ in range(5)]
        + [(lambda s: f"{s}\n{_rand_pattern(r, s)}")(rand_str(r, 500, "abc"))],
    ),
    Problem(
        title="Stock Trading with Unlimited Transactions",
        difficulty="MEDIUM",
        topics=["DP", "Greedy", "Array"],
        description="""`p[i]` is a stock's price on day `i`. You may buy and sell as many times as you like, but you can hold at most one share at a time (sell before you buy again). Buying and selling on the same day is allowed but pointless.

Print the maximum profit.

**Input:** one line of daily prices.

**Output:** the maximum profit (0 if no trade helps).""",
        constraints=["1 <= n <= 10^5", "0 <= p[i] <= 10^4"],
        solve=_stock2,
        brute=_stock2_brute,
        examples=[("7 1 5 3 6 4", "Buy 1 → sell 5, buy 3 → sell 6: 4 + 3 = 7."), ("7 6 4 3 1", "Prices only fall.")],
        tests=lambda r: ["5", "1 2", "2 1", "1 2 3 4 5", "3 3 3"]
        + [join(rand_ints(r, r.randint(5, 30), 0, 50)) for _ in range(4)]
        + [join(rand_ints(r, 4000, 0, 10000))],
    ),
    Problem(
        title="Stock Trading with Two Transactions",
        difficulty="HARD",
        topics=["DP", "Array"],
        description="""Daily prices are given. You may complete **at most two** transactions (a transaction is one buy followed later by one sell), holding at most one share at a time.

Print the maximum profit.

**Input:** one line of daily prices.

**Output:** the maximum profit.""",
        constraints=["1 <= n <= 10^5", "0 <= p[i] <= 10^5"],
        solve=_stock3,
        brute=_stock3_brute,
        examples=[("3 3 5 0 0 3 1 4", "Buy 0 → sell 3, buy 1 → sell 4: 3 + 3 = 6."), ("1 2 3 4 5", "One long trade: 4.")],
        tests=lambda r: ["5", "2 1", "1 2", "7 6 4 3 1", "1 2 4 2 5 7 2 4 9 0"]
        + [join(rand_ints(r, r.randint(5, 25), 0, 50)) for _ in range(4)]
        + [join(rand_ints(r, 4000, 0, 100000))],
    ),
    Problem(
        title="Stock Trading with K Transactions",
        difficulty="HARD",
        topics=["DP", "Array"],
        description="""Daily prices are given along with `k`. You may complete **at most `k`** transactions (buy then sell), holding at most one share at a time.

Print the maximum profit.

**Input:** daily prices on the first line, `k` on the second.

**Output:** the maximum profit.""",
        constraints=["1 <= n <= 1000", "0 <= k <= 100", "0 <= p[i] <= 1000"],
        solve=_stock4,
        brute=_stock4_brute,
        examples=[("2 4 1\n2", "Buy 2 → sell 4."), ("3 2 6 5 0 3\n2", "Buy 2 → sell 6, buy 0 → sell 3: 7.")],
        tests=lambda r: ["5\n3", "1 5\n0", "1 5\n1", "1 3 1 3 1 3\n2", "1 3 1 3 1 3\n5"]
        + [f"{join(rand_ints(r, r.randint(5, 20), 0, 30))}\n{r.randint(0, 5)}" for _ in range(4)]
        + [f"{join(rand_ints(r, 1000, 0, 1000))}\n{50}"],
    ),
    Problem(
        title="Stock Trading with Cooldown",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Daily prices are given. Trade as many times as you like, holding at most one share, but after you **sell** you must wait one full day before buying again (a one-day cooldown).

Print the maximum profit.

**Input:** one line of daily prices.

**Output:** the maximum profit.""",
        constraints=["1 <= n <= 10^5", "0 <= p[i] <= 1000"],
        solve=_cool,
        brute=_cool_brute,
        examples=[("1 2 3 0 2", "Buy, sell, cool down, buy, sell: 3."), ("1", "One day, no trade.")],
        tests=lambda r: ["2 1", "1 2", "1 2 4", "6 1 6 4 3 0 2", "1 4 2 7"]
        + [join(rand_ints(r, r.randint(5, 25), 0, 30)) for _ in range(4)]
        + [join(rand_ints(r, 4000, 0, 1000))],
    ),
    Problem(
        title="Stock Trading with Transaction Fee",
        difficulty="MEDIUM",
        topics=["DP", "Greedy", "Array"],
        description="""Daily prices are given along with a `fee` charged once for each completed transaction (buy then sell). Trade as often as you like, holding at most one share at a time.

Print the maximum profit after fees.

**Input:** daily prices on the first line, `fee` on the second.

**Output:** the maximum profit.""",
        constraints=["1 <= n <= 10^5", "0 <= p[i], fee <= 10^4"],
        solve=_fee,
        brute=_fee_brute,
        examples=[("1 3 2 8 4 9\n2", "Buy 1 → sell 8, buy 4 → sell 9: (7 − 2) + (5 − 2) = 8."), ("1 3 7 5 10 3\n3", "One trade 1 → 10 beats two: 6.")],
        tests=lambda r: ["5\n1", "1 5\n4", "1 5\n5", "1 2 3 4\n0", "9 8 7\n0"]
        + [f"{join(rand_ints(r, r.randint(5, 25), 0, 30))}\n{r.randint(0, 6)}" for _ in range(4)]
        + [f"{join(rand_ints(r, 4000, 0, 10000))}\n{r.randint(0, 500)}"],
    ),
    Problem(
        title="Number of Longest Increasing Subsequences",
        difficulty="MEDIUM",
        topics=["DP", "Array"],
        description="""Count how many **strictly increasing** subsequences have the maximum possible length. Subsequences are chosen by position, so equal values at different positions give different subsequences.

Print the count modulo `1000000007`.

**Input:** one line of integers.

**Output:** the number of longest increasing subsequences modulo `1000000007`.""",
        constraints=["1 <= n <= 2000", "-10^6 <= a[i] <= 10^6"],
        solve=_nlis,
        brute=_nlis_brute,
        examples=[("1 3 5 4 7", "[1, 3, 4, 7] and [1, 3, 5, 7]."), ("2 2 2 2 2", "Each single element is a longest one: 5.")],
        tests=lambda r: ["9", "1 2", "2 1", "1 2 3 4", "4 3 2 1", "1 1 2 2"]
        + [join(rand_ints(r, r.randint(5, 25), 0, 10)) for _ in range(4)]
        + [join(rand_ints(r, 1200, -1000, 1000))],
    ),
    Problem(
        title="Matrix Chain Multiplication",
        difficulty="HARD",
        topics=["DP"],
        description="""Matrix `i` has size `d[i−1] × d[i]`, so `n` matrices are described by `n + 1` dimensions. Multiplying an `x × y` matrix by a `y × z` matrix costs `x · y · z` scalar multiplications. The product's value doesn't depend on how you parenthesise, but the cost does.

Print the minimum total cost to multiply the whole chain (0 if there is only one matrix).

**Input:** one line with the dimensions `d[0] … d[n]`.

**Output:** the minimum number of scalar multiplications.""",
        constraints=["2 <= n + 1 <= 200", "1 <= d[i] <= 100"],
        solve=_mcm,
        brute=_mcm_brute,
        examples=[("10 20 30 40 30", "((A·B)·C)·D costs 6000 + 12000 + 12000 = 30000."), ("10 20 30", "A single product: 10·20·30 = 6000.")],
        tests=lambda r: ["5 7", "1 1 1", "40 20 30 10 30", "1 2 3 4 3", "100 1 100 1 100"]
        + [join(rand_ints(r, r.randint(3, 10), 1, 30)) for _ in range(4)]
        + [join(rand_ints(r, 150, 1, 100))],
    ),
    Problem(
        title="Burst Balloons",
        difficulty="HARD",
        topics=["DP", "Array"],
        description="""Balloons in a row carry numbers. Bursting balloon `i` earns `left · a[i] · right`, where `left` and `right` are the numbers on its current neighbours (a missing neighbour counts as `1`). After a burst, the neighbours become adjacent.

Burst every balloon in the best order and print the maximum total coins.

Hint: think about which balloon you burst **last** inside a range.

**Input:** one line with the balloon numbers.

**Output:** the maximum coins.""",
        constraints=["1 <= n <= 200", "0 <= a[i] <= 100"],
        solve=_burst,
        brute=_burst_brute,
        examples=[("3 1 5 8", "Burst 1, 5, 3, 8 for 15 + 120 + 24 + 8 = 167."), ("1 5", "Burst 1 then 5: 5 + 5 = 10.")],
        tests=lambda r: ["7", "0", "1 1", "0 9 0", "9 76 64 21"]
        + [join(rand_ints(r, r.randint(3, 8), 0, 20)) for _ in range(4)]
        + [join(rand_ints(r, 120, 0, 100))],
    ),
    Problem(
        title="Palindrome Partitioning Min Cuts",
        difficulty="HARD",
        topics=["DP", "String"],
        description="""Cut the string into pieces so that **every piece is a palindrome**. Print the minimum number of cuts needed (0 if the whole string is already a palindrome).

**Input:** one lowercase string `s`.

**Output:** the minimum number of cuts.""",
        constraints=["1 <= |s| <= 1000"],
        solve=_cuts,
        brute=_cuts_brute,
        examples=[("aab", "\"aa\" | \"b\": 1 cut."), ("abc", "\"a\" | \"b\" | \"c\": 2 cuts.")],
        tests=lambda r: ["a", "ab", "aa", "racecar", "abacaba", "banana"]
        + [rand_str(r, r.randint(4, 25), "ab") for _ in range(4)]
        + [rand_str(r, 600, "abc")],
    ),
    Problem(
        title="Maximal Square",
        difficulty="MEDIUM",
        topics=["DP", "Matrix"],
        description="""A grid holds `0`s and `1`s. Find the largest square made entirely of `1`s and print its **area**.

**Input:** `r c` on the first line, then `r` lines of `c` characters, each `0` or `1` (no spaces).

**Output:** the area of the largest all-ones square (0 if there are no ones).""",
        constraints=["1 <= r, c <= 300"],
        solve=_maxsq,
        brute=_maxsq_brute,
        examples=[("4 5\n10100\n10111\n11111\n10010", "A 2 × 2 block of ones: area 4."), ("1 1\n0", "No ones.")],
        tests=lambda r: ["1 1\n1", "2 2\n11\n11", "2 3\n111\n111", "3 1\n1\n1\n0", "3 3\n010\n111\n010"]
        + [_bits_text(_rand_bits(r, r.randint(2, 8), r.randint(2, 8))) for _ in range(4)]
        + [_bits_text(_rand_bits(r, 120, 120, 0.85))],
    ),
    Problem(
        title="Count Square Submatrices",
        difficulty="MEDIUM",
        topics=["DP", "Matrix"],
        description="""A grid holds `0`s and `1`s. Count every square submatrix (of any size) whose cells are all `1`.

**Input:** `r c` on the first line, then `r` lines of `c` characters, each `0` or `1` (no spaces).

**Output:** the number of all-ones squares.""",
        constraints=["1 <= r, c <= 300"],
        solve=_cntsq,
        brute=_cntsq_brute,
        examples=[("3 4\n0111\n1111\n0111", "10 of size 1, 4 of size 2, 1 of size 3: 15."), ("3 3\n101\n110\n110", "6 ones + 1 square of size 2 = 7.")],
        tests=lambda r: ["1 1\n0", "1 1\n1", "2 2\n11\n11", "3 3\n111\n111\n111", "1 5\n11011"]
        + [_bits_text(_rand_bits(r, r.randint(2, 8), r.randint(2, 8))) for _ in range(4)]
        + [_bits_text(_rand_bits(r, 120, 120, 0.85))],
    ),
]
