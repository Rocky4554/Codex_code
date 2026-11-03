"""Tries."""
from collections import Counter

from lib import Playlist, Problem, ints, join, lines, rand_ints, rand_str

PLAYLISTS = [
    Playlist(
        key="tries",
        title="18 · Tries",
        description="Prefix trees for fast word and prefix lookups, plus the bitwise trie trick for maximum XOR.",
        accent="#C3B8F5",
        titles=[
            "Implement a Trie",
            "Trie With Counts and Erase",
            "Longest Word With All Prefixes",
            "Count Distinct Substrings",
            "Maximum XOR of Two Numbers",
            "Maximum XOR With a Limit",
        ],
    )
]


def _ops(inp):
    ls = lines(inp)
    q = int(ls[0])
    return [ls[1 + i].split() for i in range(q)]


# ── Implement a trie ────────────────────────────────────────────

def _trie(inp):
    root = {}
    out = []
    for op, w in _ops(inp):
        node = root
        if op == "insert":
            for ch in w:
                node = node.setdefault(ch, {})
            node["$"] = True
            continue
        found = True
        for ch in w:
            if ch not in node:
                found = False
                break
            node = node[ch]
        out.append("true" if found and (op == "startsWith" or "$" in node) else "false")
    return "\n".join(out)


def _trie_brute(inp):
    words, out = set(), []
    for op, w in _ops(inp):
        if op == "insert":
            words.add(w)
        elif op == "search":
            out.append("true" if w in words else "false")
        else:
            out.append("true" if any(x.startswith(w) for x in words) else "false")
    return "\n".join(out)


def _trie_tests(r):
    out = ["1\nsearch a", "2\ninsert a\nsearch a", "3\ninsert abc\nsearch ab\nstartsWith ab", "4\ninsert ab\ninsert abc\nsearch ab\nsearch abcd"]
    for q in (10, 30, 2000):
        ops = []
        alpha = "ab" if q < 100 else "abc"
        has_query = False
        for _ in range(q):
            op = r.choice(["insert", "search", "startsWith"])
            w = rand_str(r, r.randint(1, 5 if q < 100 else 8), alpha)
            ops.append(f"{op} {w}")
            has_query |= op != "insert"
        if not has_query:
            ops[-1] = "search a"
        out.append(f"{q}\n" + "\n".join(ops))
    return out


# ── Counts and erase ────────────────────────────────────────────

class _Node:
    __slots__ = ("kids", "end", "pre")

    def __init__(self):
        self.kids, self.end, self.pre = {}, 0, 0


def _count_trie(inp):
    root = _Node()
    out = []
    for op, w in _ops(inp):
        if op == "insert":
            node = root
            for ch in w:
                node = node.kids.setdefault(ch, _Node())
                node.pre += 1
            node.end += 1
        elif op == "erase":
            node, path = root, []
            for ch in w:
                node = node.kids.get(ch)
                if node is None:
                    break
                path.append(node)
            if node is None or node.end == 0:
                continue
            for n in path:
                n.pre -= 1
            node.end -= 1
        else:
            node = root
            for ch in w:
                node = node.kids.get(ch)
                if node is None:
                    break
            if node is None:
                out.append("0")
            else:
                out.append(str(node.end if op == "countEqual" else node.pre))
    return "\n".join(out)


def _count_trie_brute(inp):
    bag, out = Counter(), []
    for op, w in _ops(inp):
        if op == "insert":
            bag[w] += 1
        elif op == "erase":
            if bag[w]:
                bag[w] -= 1
        elif op == "countEqual":
            out.append(str(bag[w]))
        else:
            out.append(str(sum(c for x, c in bag.items() if x.startswith(w))))
    return "\n".join(out)


def _count_trie_tests(r):
    out = ["1\ncountEqual a", "2\nerase a\ncountPrefix a", "4\ninsert a\ninsert a\nerase a\ncountEqual a", "4\ninsert ab\ninsert abc\ncountPrefix ab\ncountPrefix abcd"]
    for q in (12, 40, 2000):
        ops = []
        alpha = "ab" if q < 100 else "abc"
        for k in range(q):
            op = r.choice(["insert", "insert", "erase", "countEqual", "countPrefix"])
            w = rand_str(r, r.randint(1, 4 if q < 100 else 7), alpha)
            ops.append(f"{op} {w}")
        ops[-1] = "countPrefix a"
        out.append(f"{q}\n" + "\n".join(ops))
    return out


# ── Longest word with all prefixes ──────────────────────────────

def _complete(inp):
    words = lines(inp)[0].split()
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = True
    best = ""
    for w in words:
        node, ok = root, True
        for ch in w:
            node = node[ch]
            if "$" not in node:
                ok = False
                break
        if ok and (len(w) > len(best) or (len(w) == len(best) and w < best)):
            best = w
    return best or "None"


def _complete_brute(inp):
    words = set(lines(inp)[0].split())
    good = [w for w in words if all(w[:k] in words for k in range(1, len(w) + 1))]
    if not good:
        return "None"
    return min(good, key=lambda w: (-len(w), w))


def _complete_tests(r):
    out = ["a", "b ba bac", "ab abc", "a b c", "k ki kir kira kiran", "n ni nin ninj ninja ninga"]
    for n in (8, 20, 2500):
        ws = []
        for _ in range(n):
            ws.append(rand_str(r, r.randint(1, 4 if n < 100 else 6), "ab"))
        out.append(join(ws))
    return out


# ── Distinct substrings ─────────────────────────────────────────

def _distinct(inp):
    s = lines(inp)[0] if lines(inp) and lines(inp)[0] else ""
    root, count = {}, 0
    for i in range(len(s)):
        node = root
        for ch in s[i:]:
            if ch not in node:
                node[ch] = {}
                count += 1
            node = node[ch]
    return str(count)


def _distinct_brute(inp):
    s = lines(inp)[0]
    return str(len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)}))


# ── Maximum XOR ─────────────────────────────────────────────────

BITS = 30


def _insert_bits(root, x):
    node = root
    for b in range(BITS, -1, -1):
        node = node.setdefault(x >> b & 1, {})


def _best_xor(root, x):
    node, res = root, 0
    for b in range(BITS, -1, -1):
        want = 1 - (x >> b & 1)
        if want in node:
            res |= 1 << b
            node = node[want]
        else:
            node = node[1 - want]
    return res


def _maxxor(inp):
    nums = ints(lines(inp)[0])
    root = {}
    best = 0
    for x in nums:
        _insert_bits(root, x)
        best = max(best, _best_xor(root, x))
    return str(best)


def _maxxor_brute(inp):
    nums = ints(lines(inp)[0])
    return str(max(a ^ b for a in nums for b in nums))


def _limit_parse(inp):
    ls = lines(inp)
    nums = ints(ls[0])
    q = int(ls[1])
    return nums, [tuple(map(int, ls[2 + i].split())) for i in range(q)]


def _maxxor_limit(inp):
    nums, queries = _limit_parse(inp)
    nums = sorted(nums)
    order = sorted(range(len(queries)), key=lambda i: queries[i][1])
    ans = [-1] * len(queries)
    root, j = {}, 0
    for qi in order:
        x, m = queries[qi]
        while j < len(nums) and nums[j] <= m:
            _insert_bits(root, nums[j])
            j += 1
        if j:
            ans[qi] = _best_xor(root, x)
    return "\n".join(map(str, ans))


def _maxxor_limit_brute(inp):
    nums, queries = _limit_parse(inp)
    out = []
    for x, m in queries:
        cands = [x ^ a for a in nums if a <= m]
        out.append(str(max(cands)) if cands else "-1")
    return "\n".join(out)


def _limit_tests(r):
    out = ["5\n1\n3 4", "5\n1\n3 5", "0 1 2 3 4\n3\n3 1\n1 3\n5 6"]
    for n, q, hi in ((6, 5, 20), (10, 8, 100), (12, 10, 10**9)):
        nums = rand_ints(r, n, 0, hi)
        qs = [f"{r.randint(0, hi)} {r.randint(0, hi)}" for _ in range(q)]
        out.append(f"{join(nums)}\n{q}\n" + "\n".join(qs))
    nums = rand_ints(r, 1000, 0, 10**9)
    qs = [f"{r.randint(0, 10**9)} {r.randint(0, 10**9)}" for _ in range(800)]
    out.append(f"{join(nums)}\n800\n" + "\n".join(qs))
    return out


PROBLEMS = [
    Problem(
        title="Implement a Trie",
        difficulty="MEDIUM",
        topics=["Trie", "Design", "String"],
        description="""Build a prefix tree (trie) that supports three commands:

- `insert w` — add the word `w`.
- `search w` — is `w` one of the inserted words?
- `startsWith p` — does any inserted word begin with `p`?

Each trie node has one child per next letter and a flag marking the end of a word.

**Input:** line 1 — the number of commands `q`; next `q` lines — one command each.

**Output:** for every `search` and `startsWith` command, print `true` or `false` on its own line.""",
        constraints=["1 <= q <= 3 × 10^4", "1 <= word length <= 20, lowercase letters"],
        solve=_trie,
        brute=_trie_brute,
        examples=[("6\ninsert apple\nsearch apple\nsearch app\nstartsWith app\ninsert app\nsearch app", "\"app\" is only a prefix until it's inserted itself."), ("2\ninsert code\nstartsWith cod", "\"cod\" begins \"code\".")],
        tests=_trie_tests,
    ),
    Problem(
        title="Trie With Counts and Erase",
        difficulty="MEDIUM",
        topics=["Trie", "Design", "String"],
        description="""Build a trie that stores words **with multiplicity** and supports:

- `insert w` — add one copy of `w`.
- `countEqual w` — how many copies of exactly `w` are stored?
- `countPrefix p` — how many stored words (counting copies) start with `p`?
- `erase w` — remove one copy of `w`; if `w` isn't stored, do nothing.

Keep two counters per node: how many words pass through it and how many end at it.

**Input:** line 1 — `q`; next `q` lines — one command each.

**Output:** one line per `countEqual` / `countPrefix` command with the count.""",
        constraints=["1 <= q <= 3 × 10^4", "1 <= word length <= 20, lowercase letters"],
        solve=_count_trie,
        brute=_count_trie_brute,
        examples=[("7\ninsert apple\ninsert apple\ninsert apps\ncountEqual apple\ncountPrefix app\nerase apple\ncountPrefix app", "Two apples and one apps, then one apple is erased."), ("2\nerase cat\ncountEqual cat", "Erasing a missing word does nothing.")],
        tests=_count_trie_tests,
    ),
    Problem(
        title="Longest Word With All Prefixes",
        difficulty="MEDIUM",
        topics=["Trie", "String"],
        description="""From a list of words, find the longest word such that **every** prefix of it (`w[0..0]`, `w[0..1]`, …, the word itself) is also in the list. If several words tie in length, pick the lexicographically smallest. If no word qualifies, print `None`.

**Input:** one line of space-separated lowercase words.

**Output:** the word, or `None`.""",
        constraints=["1 <= n <= 10^4", "1 <= word length <= 30"],
        solve=_complete,
        brute=_complete_brute,
        examples=[("n ni nin ninj ninja ninga", "\"ninga\" is missing \"ning\", but every prefix of \"ninja\" is there."), ("ab abc", "Neither word has \"a\" in the list.")],
        tests=_complete_tests,
    ),
    Problem(
        title="Count Distinct Substrings",
        difficulty="MEDIUM",
        topics=["Trie", "String"],
        description="""Count how many **different** non-empty substrings a string has.

Insert every suffix into a trie: each new node created is a substring you haven't seen before.

**Input:** one lowercase string `s`.

**Output:** the number of distinct non-empty substrings.""",
        constraints=["1 <= s.length <= 400"],
        solve=_distinct,
        brute=_distinct_brute,
        examples=[("abab", "a, b, ab, ba, aba, bab, abab — 7."), ("aaa", "a, aa, aaa.")],
        tests=lambda r: ["a", "ab", "aaaaaaaa", "abcdefghijklmnopqrstuvwxyz", "banana", "mississippi"]
        + [rand_str(r, r.randint(10, 40), "ab") for _ in range(3)]
        + [rand_str(r, 400, "abc"), "a" * 400],
    ),
    Problem(
        title="Maximum XOR of Two Numbers",
        difficulty="MEDIUM",
        topics=["Trie", "Bit Manipulation", "Array"],
        description="""Find the largest value of `nums[i] XOR nums[j]` over all pairs (`i` and `j` may be equal, so a single-element array gives 0).

Put every number's 31-bit binary form into a trie. For each number, walk the trie preferring the opposite bit at every level — that greedily maximizes the XOR from the top bit down.

**Input:** one line of non-negative integers.

**Output:** the maximum XOR.""",
        constraints=["1 <= n <= 2 × 10^4", "0 <= nums[i] < 2^31"],
        solve=_maxxor,
        brute=_maxxor_brute,
        examples=[("3 10 5 25 2 8", "5 XOR 25 = 28."), ("7", "Only one number: 7 XOR 7 = 0.")],
        tests=lambda r: ["0", "0 0", "1 2", "0 2147483647", "8 10 2"]
        + [join(rand_ints(r, r.randint(4, 15), 0, 100)) for _ in range(3)]
        + [join(rand_ints(r, 2500, 0, 2**31 - 1))],
    ),
    Problem(
        title="Maximum XOR With a Limit",
        difficulty="HARD",
        topics=["Trie", "Bit Manipulation", "Sorting"],
        description="""You get an array `nums` and queries `(x, m)`. For each query, find the maximum of `x XOR a` over all `a` in `nums` with `a <= m`. If no element is `<= m`, the answer is `-1`.

Answer queries offline: sort them by `m`, sort `nums`, and add elements to a bitwise trie only once they're allowed.

**Input:** line 1 — `nums`; line 2 — `q`; next `q` lines — `x m`.

**Output:** one answer per query, in the original query order.""",
        constraints=["1 <= n, q <= 10^4", "0 <= nums[i], x, m <= 10^9"],
        solve=_maxxor_limit,
        brute=_maxxor_limit_brute,
        examples=[("0 1 2 3 4\n3\n3 1\n1 3\n5 6", "Query 1 may use 0 or 1: 3 XOR 0 = 3."), ("5 2 4 6 6 3\n2\n12 4\n8 1", "Nothing is ≤ 1 in the second query.")],
        tests=_limit_tests,
    ),
]
