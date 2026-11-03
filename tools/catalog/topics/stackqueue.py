"""Stacks & Queues — LIFO/FIFO structures and monotonic stacks."""
from collections import OrderedDict, deque

from lib import Playlist, Problem, ints, join, lines, rand_ints, rand_str

PLAYLISTS = [
    Playlist(
        key="stackqueue",
        title="12 · Stacks & Queues",
        description="LIFO and FIFO structures, then the monotonic stack: one pass that answers 'nearest bigger or smaller' for every element.",
        accent="#F5A9A9",
        titles=[
            "Implement Stack Using Array",
            "Implement Queue Using Array",
            "Valid Parentheses",
            "Queue Using Two Stacks",
            "Min Stack",
            "Evaluate Reverse Polish Notation",
            "Infix to Postfix",
            "Next Greater Element",
            "Next Smaller Element",
            "Next Greater Element II",
            "Daily Temperatures",
            "Stock Span",
            "Asteroid Collision",
            "Remove K Digits",
            "Sum of Subarray Minimums",
            "LRU Cache",
            "Sliding Window Maximum",
            "Largest Rectangle in Histogram",
            "Maximal Rectangle",
        ],
    )
]

MOD = 1_000_000_007


# ── monotonic stack family ───────────────────────────────────────

def _nse(inp):
    a = ints(lines(inp)[0])
    ans, st = [-1] * len(a), []
    for i in range(len(a) - 1, -1, -1):
        while st and st[-1] >= a[i]:
            st.pop()
        ans[i] = st[-1] if st else -1
        st.append(a[i])
    return join(ans)


def _nse_brute(inp):
    a = ints(lines(inp)[0])
    return join(next((a[j] for j in range(i + 1, len(a)) if a[j] < a[i]), -1) for i in range(len(a)))


def _nge2(inp):
    a = ints(lines(inp)[0])
    n = len(a)
    ans, st = [-1] * n, []
    for i in range(2 * n - 1, -1, -1):
        x = a[i % n]
        while st and st[-1] <= x:
            st.pop()
        if i < n:
            ans[i] = st[-1] if st else -1
        st.append(x)
    return join(ans)


def _nge2_brute(inp):
    a = ints(lines(inp)[0])
    n = len(a)
    return join(next((a[(i + d) % n] for d in range(1, n) if a[(i + d) % n] > a[i]), -1) for i in range(n))


def _daily(inp):
    t = ints(lines(inp)[0])
    ans, st = [0] * len(t), []
    for i, x in enumerate(t):
        while st and t[st[-1]] < x:
            j = st.pop()
            ans[j] = i - j
        st.append(i)
    return join(ans)


def _daily_brute(inp):
    t = ints(lines(inp)[0])
    return join(next((j - i for j in range(i + 1, len(t)) if t[j] > t[i]), 0) for i in range(len(t)))


def _span(inp):
    p = ints(lines(inp)[0])
    ans, st = [], []
    for i, x in enumerate(p):
        while st and p[st[-1]] <= x:
            st.pop()
        ans.append(i - st[-1] if st else i + 1)
        st.append(i)
    return join(ans)


def _span_brute(inp):
    p = ints(lines(inp)[0])
    out = []
    for i in range(len(p)):
        k = 0
        while i - k >= 0 and p[i - k] <= p[i]:
            k += 1
        out.append(k)
    return join(out)


def _asteroids(inp):
    st = []
    for a in ints(lines(inp)[0]):
        alive = True
        while alive and a < 0 and st and st[-1] > 0:
            if st[-1] < -a:
                st.pop()
            elif st[-1] == -a:
                st.pop()
                alive = False
            else:
                alive = False
        if alive:
            st.append(a)
    return join(st) if st else "empty"


def _asteroids_brute(inp):
    a = ints(lines(inp)[0])
    changed = True
    while changed:
        changed = False
        for i in range(len(a) - 1):
            if a[i] > 0 and a[i + 1] < 0:
                x, y = a[i], -a[i + 1]
                a = a[:i] + ([a[i]] if x > y else [a[i + 1]] if y > x else []) + a[i + 2 :]
                changed = True
                break
    return join(a) if a else "empty"


def _remove_k(inp):
    ls = lines(inp)
    num, k = ls[0], int(ls[1])
    st = []
    for d in num:
        while k and st and st[-1] > d:
            st.pop()
            k -= 1
        st.append(d)
    if k:
        st = st[:-k]
    return "".join(st).lstrip("0") or "0"


def _remove_k_brute(inp):
    from itertools import combinations
    ls = lines(inp)
    num, k = ls[0], int(ls[1])
    keep = len(num) - k
    best = None
    for idx in combinations(range(len(num)), keep):
        s = "".join(num[i] for i in idx).lstrip("0") or "0"
        if best is None or (len(s), s) < (len(best), best):
            best = s
    return best if best is not None else "0"


def _sum_mins(inp):
    a = ints(lines(inp)[0])
    n = len(a)
    left, right = [0] * n, [0] * n
    st = []
    for i in range(n):  # previous strictly smaller
        while st and a[st[-1]] >= a[i]:
            st.pop()
        left[i] = i - st[-1] if st else i + 1
        st.append(i)
    st = []
    for i in range(n - 1, -1, -1):  # next smaller or equal
        while st and a[st[-1]] > a[i]:
            st.pop()
        right[i] = st[-1] - i if st else n - i
        st.append(i)
    return str(sum(a[i] * left[i] * right[i] for i in range(n)) % MOD)


def _sum_mins_brute(inp):
    a = ints(lines(inp)[0])
    total = 0
    for i in range(len(a)):
        m = a[i]
        for j in range(i, len(a)):
            m = min(m, a[j])
            total += m
    return str(total % MOD)


def _window_max(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    dq, out = deque(), []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(a[dq[0]])
    return join(out)


def _window_max_brute(inp):
    ls = lines(inp)
    a, k = ints(ls[0]), int(ls[1])
    return join(max(a[i : i + k]) for i in range(len(a) - k + 1))


def _histogram_heights(h):
    best, st = 0, []
    for i, x in enumerate(h + [0]):
        start = i
        while st and st[-1][1] >= x:
            j, height = st.pop()
            best = max(best, height * (i - j))
            start = j
        st.append((start, x))
    return best


def _histogram(inp):
    return str(_histogram_heights(ints(lines(inp)[0])))


def _histogram_brute(inp):
    h = ints(lines(inp)[0])
    best = 0
    for i in range(len(h)):
        m = h[i]
        for j in range(i, len(h)):
            m = min(m, h[j])
            best = max(best, m * (j - i + 1))
    return str(best)


def _maximal_rect(inp):
    ls = lines(inp)
    r, c = map(int, ls[0].split())
    heights, best = [0] * c, 0
    for row in ls[1 : 1 + r]:
        for j, ch in enumerate(row):
            heights[j] = heights[j] + 1 if ch == "1" else 0
        best = max(best, _histogram_heights(heights))
    return str(best)


def _maximal_rect_brute(inp):
    ls = lines(inp)
    r, c = map(int, ls[0].split())
    g = ls[1 : 1 + r]
    best = 0
    for top in range(r):
        for left in range(c):
            for bottom in range(top, r):
                for right in range(left, c):
                    if all(g[i][j] == "1" for i in range(top, bottom + 1) for j in range(left, right + 1)):
                        best = max(best, (bottom - top + 1) * (right - left + 1))
    return str(best)


# ── expression problems ──────────────────────────────────────────

def _rpn(inp):
    st = []
    for tok in lines(inp)[0].split():
        if tok in "+-*/" and len(tok) == 1:
            b, a = st.pop(), st.pop()
            if tok == "+":
                st.append(a + b)
            elif tok == "-":
                st.append(a - b)
            elif tok == "*":
                st.append(a * b)
            else:
                q = abs(a) // abs(b)
                st.append(q if (a >= 0) == (b > 0) else -q)
        else:
            st.append(int(tok))
    return str(st[0])


def _rpn_brute(inp):
    # Rebuild a fully parenthesised infix string and evaluate it with truncating division.
    st = []
    for tok in lines(inp)[0].split():
        if tok in "+-*/" and len(tok) == 1:
            b, a = st.pop(), st.pop()
            st.append((tok, a, b))
        else:
            st.append(int(tok))

    def ev(node):
        if isinstance(node, int):
            return node
        op, a, b = node
        x, y = ev(a), ev(b)
        if op == "/":
            return int(x / y) if abs(x) < 2**52 and abs(y) < 2**52 else (abs(x) // abs(y)) * (1 if (x >= 0) == (y > 0) else -1)
        return {"+": x + y, "-": x - y, "*": x * y}[op]

    return str(ev(st[0]))


PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}


def _to_postfix(inp):
    out, st = [], []
    for ch in lines(inp)[0].replace(" ", ""):
        if ch.isalpha():
            out.append(ch)
        elif ch == "(":
            st.append(ch)
        elif ch == ")":
            while st[-1] != "(":
                out.append(st.pop())
            st.pop()
        else:
            while st and st[-1] != "(" and (PREC[st[-1]] > PREC[ch] or (PREC[st[-1]] == PREC[ch] and ch != "^")):
                out.append(st.pop())
            st.append(ch)
    while st:
        out.append(st.pop())
    return "".join(out)


def _to_postfix_brute(inp):
    # Recursive-descent parser producing postfix directly.
    s = lines(inp)[0].replace(" ", "")
    pos = 0

    def peek():
        return s[pos] if pos < len(s) else ""

    def eat():
        nonlocal pos
        pos += 1
        return s[pos - 1]

    def atom():
        if peek() == "(":
            eat()
            v = expr()
            eat()
            return v
        return eat()

    def power():
        base = atom()
        if peek() == "^":
            eat()
            return base + power() + "^"
        return base

    def term():
        v = power()
        while peek() in ("*", "/") and peek():
            op = eat()
            v = v + power() + op
        return v

    def expr():
        v = term()
        while peek() in ("+", "-") and peek():
            op = eat()
            v = v + term() + op
        return v

    return expr()


# ── design problems ──────────────────────────────────────────────

def _two_stack_queue(inp):
    ls = lines(inp)
    q = int(ls[0])
    inbox, outbox, out = [], [], []

    def shift():
        if not outbox:
            while inbox:
                outbox.append(inbox.pop())

    for cmd in ls[1 : 1 + q]:
        parts = cmd.split()
        if parts[0] == "push":
            inbox.append(int(parts[1]))
        elif parts[0] == "pop":
            shift()
            out.append(str(outbox.pop()) if outbox else "-1")
        elif parts[0] == "peek":
            shift()
            out.append(str(outbox[-1]) if outbox else "-1")
        else:
            out.append("true" if not inbox and not outbox else "false")
    return "\n".join(out)


def _two_stack_queue_brute(inp):
    ls = lines(inp)
    q, out = deque(), []
    for cmd in ls[1 : 1 + int(ls[0])]:
        parts = cmd.split()
        if parts[0] == "push":
            q.append(int(parts[1]))
        elif parts[0] == "pop":
            out.append(str(q.popleft()) if q else "-1")
        elif parts[0] == "peek":
            out.append(str(q[0]) if q else "-1")
        else:
            out.append("true" if not q else "false")
    return "\n".join(out)


def _lru(inp):
    ls = lines(inp)
    cap, q = map(int, ls[0].split())
    cache, out = OrderedDict(), []
    for cmd in ls[1 : 1 + q]:
        parts = cmd.split()
        if parts[0] == "get":
            k = int(parts[1])
            if k in cache:
                cache.move_to_end(k)
                out.append(str(cache[k]))
            else:
                out.append("-1")
        else:
            k, v = int(parts[1]), int(parts[2])
            if k in cache:
                cache.move_to_end(k)
            cache[k] = v
            if len(cache) > cap:
                cache.popitem(last=False)
    return "\n".join(out) if out else "none"


def _lru_brute(inp):
    ls = lines(inp)
    cap, q = map(int, ls[0].split())
    order, vals, out = [], {}, []  # order: least recent first
    for cmd in ls[1 : 1 + q]:
        parts = cmd.split()
        k = int(parts[1])
        if parts[0] == "get":
            if k in vals:
                order.remove(k)
                order.append(k)
                out.append(str(vals[k]))
            else:
                out.append("-1")
        else:
            if k in vals:
                order.remove(k)
            order.append(k)
            vals[k] = int(parts[2])
            if len(order) > cap:
                del vals[order.pop(0)]
    return "\n".join(out) if out else "none"


# ── test generators ──────────────────────────────────────────────

def _arr_tests(r, special, lo=-50, hi=50, sizes=(7, 12, 40, 2000)):
    return list(special) + [join(rand_ints(r, n, lo, hi)) for n in sizes]


def _t_asteroids(r):
    out = ["5", "-5", "5 -5", "-2 -1 1 2", "1 -2 3 -4", "10 2 -5", "8 -8 8"]
    for n in (8, 15, 1500):
        out.append(join(r.choice([-1, 1]) * r.randint(1, 30) for _ in range(n)))
    return out


def _t_remove_k(r):
    out = ["9\n1", "10\n1", "10200\n1", "112\n1", "1111\n2", "123456\n3", "54321\n2", "100200\n2"]
    for n in (10, 12):
        s = str(r.randint(1, 9)) + rand_str(r, n - 1, "0123456789")
        out.append(f"{s}\n{r.randint(0, n)}")
    s = str(r.randint(1, 9)) + rand_str(r, 2999, "0123456789")
    out.append(f"{s}\n{r.randint(1, 2999)}")
    return out


def _t_window(r):
    out = ["5\n1", "1 3 -1 -3 5 3 6 7\n3", "4 4 4 4\n2", "9 8 7 6\n4", "1 2 3 4 5\n5"]
    for n in (10, 30, 2000):
        out.append(f"{join(rand_ints(r, n, -99, 99))}\n{r.randint(1, n)}")
    return out


def _t_grid(r):
    out = ["1 1\n0", "1 1\n1", "2 2\n11\n11", "3 4\n1010\n1011\n1111", "2 3\n000\n000"]
    for rows, cols, p in ((4, 5, 0.6), (6, 6, 0.7), (5, 7, 0.8)):
        g = ["".join("1" if r.random() < p else "0" for _ in range(cols)) for _ in range(rows)]
        out.append(f"{rows} {cols}\n" + "\n".join(g))
    g = ["".join("1" if r.random() < 0.75 else "0" for _ in range(60)) for _ in range(60)]
    out.append("60 60\n" + "\n".join(g))
    return out


def _rand_infix(r, depth):
    if depth == 0 or r.random() < 0.25:
        return r.choice("abcdefghij")
    a, b = _rand_infix(r, depth - 1), _rand_infix(r, depth - 1)
    op = r.choice("+-*/^")
    e = f"{a}{op}{b}"
    return f"({e})" if r.random() < 0.5 else e


def _t_infix(r):
    out = ["a", "a+b", "a+b*c", "(a+b)*c", "a-b-c", "a^b^c", "a*(b+c)/d", "((a))", "a+b*(c^d-e)^(f+g*h)-i"]
    out += [_rand_infix(r, d) for d in (3, 4, 5)]
    return out


def _rand_rpn(r, depth):
    if depth == 0 or r.random() < 0.2:
        return [str(r.randint(-20, 20))]
    left, right = _rand_rpn(r, depth - 1), _rand_rpn(r, depth - 1)
    op = r.choice("+-*/")
    if op == "/":
        # keep the divisor non-zero
        right = [str(r.choice([-7, -3, -2, 2, 3, 5, 9]))]
    return left + right + [op]


def _t_rpn(r):
    out = ["5", "2 1 + 3 *", "4 13 5 / +", "7 -3 /", "-7 2 /", "0 3 /", "3 4 - 5 -"]
    out += [" ".join(_rand_rpn(r, d)) for d in (3, 5, 6, 8)]
    return out


def _t_two_stack(r):
    out = ["1\nempty", "2\npop\npeek", "4\npush 1\npush 2\npop\npeek"]
    for q in (10, 25, 400):
        cmds = []
        for _ in range(q):
            c = r.choices(["push", "pop", "peek", "empty"], [4, 2, 2, 1])[0]
            cmds.append(f"push {r.randint(-100, 100)}" if c == "push" else c)
        out.append(f"{q}\n" + "\n".join(cmds))
    return out


def _t_lru(r):
    out = ["1 3\nput 1 1\nput 2 2\nget 1", "2 1\nget 5", "1 4\nput 1 1\nput 1 2\nget 1\nget 1",
           "2 6\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nget 3"]
    for cap, q, keys in ((2, 15, 4), (3, 40, 6), (50, 1500, 120)):
        cmds = []
        for _ in range(q):
            k = r.randint(1, keys)
            cmds.append(f"put {k} {r.randint(0, 999)}" if r.random() < 0.5 else f"get {k}")
        out.append(f"{cap} {q}\n" + "\n".join(cmds))
    return out


PROBLEMS = [
    Problem(
        title="Queue Using Two Stacks",
        difficulty="EASY",
        topics=["Stack", "Queue", "Design"],
        description="""Build a first-in, first-out queue using only two stacks. Push onto an *inbox* stack; when you need the front, pour the inbox into an *outbox* stack, which reverses the order. Each element moves at most twice, so every operation is `O(1)` amortised.

Commands:
- `push x`: add `x` to the back.
- `pop`: remove and print the front element, or `-1` if the queue is empty.
- `peek`: print the front element without removing it, or `-1` if empty.
- `empty`: print `true` if the queue is empty, otherwise `false`.

**Input:** line 1 is `q`; each of the next `q` lines is one command.

**Output:** one line for every `pop`, `peek` and `empty` command, in order.""",
        constraints=["1 <= q <= 10^4"],
        solve=_two_stack_queue,
        brute=_two_stack_queue_brute,
        examples=[("5\npush 1\npush 2\npeek\npop\nempty", "1 is at the front; after popping it, 2 remains.")],
        tests=_t_two_stack,
    ),
    Problem(
        title="Evaluate Reverse Polish Notation",
        difficulty="MEDIUM",
        topics=["Stack", "Math"],
        description="""Evaluate an expression written in reverse Polish (postfix) notation, where each operator follows its two operands. For example `2 1 + 3 *` means `(2 + 1) × 3`.

Operators are `+`, `-`, `*` and `/`. Division between integers **truncates toward zero** (`7 / -3 = -2`). The expression is always valid and never divides by zero.

**Input:** one line of space-separated tokens.

**Output:** the value of the expression.""",
        constraints=["1 <= tokens <= 10^4"],
        solve=_rpn,
        brute=_rpn_brute,
        examples=[("2 1 + 3 *", "(2 + 1) × 3 = 9."), ("4 13 5 / +", "13 / 5 = 2 (truncated), then 4 + 2 = 6.")],
        tests=_t_rpn,
    ),
    Problem(
        title="Infix to Postfix",
        difficulty="MEDIUM",
        topics=["Stack", "String"],
        description="""Convert an infix expression to postfix (reverse Polish) notation.

Operands are single lowercase letters. Operators, from lowest to highest precedence: `+ -`, then `* /`, then `^`. `+ - * /` are left-associative; `^` is **right-associative** (`a^b^c` means `a^(b^c)`). Parentheses group as usual and do not appear in the output.

**Input:** one line, the expression (no spaces).

**Output:** the postfix expression, with no spaces.""",
        constraints=["1 <= length <= 10^4"],
        solve=_to_postfix,
        brute=_to_postfix_brute,
        examples=[("a+b*c", "* binds tighter, so b c * comes first: abc*+."), ("(a+b)*c^d^e", "Parentheses first; ^ groups from the right.")],
        tests=_t_infix,
    ),
    Problem(
        title="Next Smaller Element",
        difficulty="MEDIUM",
        topics=["Stack", "Monotonic Stack", "Array"],
        description="""For every element, find the first element to its **right** that is strictly smaller. Print `-1` if there is none.

Scan from right to left with a stack that stays increasing from bottom to top: pop everything that is not smaller than the current element, and whatever is left on top is the answer.

**Input:** one line of space-separated integers.

**Output:** the answers, space-separated, in the original order.""",
        constraints=["1 <= n <= 10^5"],
        solve=_nse,
        brute=_nse_brute,
        examples=[("4 8 5 2 25", "4 → 2, 8 → 5, 5 → 2, nothing smaller after 2 or 25."), ("3 3 1", "Equal values don't count as smaller.")],
        tests=lambda r: _arr_tests(r, ["7", "1 2 3 4", "4 3 2 1", "5 5 5"]),
    ),
    Problem(
        title="Next Greater Element II",
        difficulty="MEDIUM",
        topics=["Stack", "Monotonic Stack", "Array"],
        description="""The array is **circular**: after the last element comes the first one again. For every element, find the first strictly greater element you meet when walking forward (wrapping around). Print `-1` if there is none.

Iterate over the array twice (indices `2n − 1` down to 0) with a decreasing stack, so the wrap-around is handled without copying.

**Input:** one line of space-separated integers.

**Output:** the answers, space-separated, in the original order.""",
        constraints=["1 <= n <= 10^5"],
        solve=_nge2,
        brute=_nge2_brute,
        examples=[("1 2 1", "The last 1 wraps around to find 2; 2 has nothing greater."), ("5 4 3 2 1", "Every smaller element wraps to 5.")],
        tests=lambda r: _arr_tests(r, ["7", "2 2 2", "1 2 3 4", "3 1 2"]),
    ),
    Problem(
        title="Daily Temperatures",
        difficulty="MEDIUM",
        topics=["Stack", "Monotonic Stack", "Array"],
        description="""Given daily temperatures, print for each day how many days you have to wait for a strictly warmer day. If no warmer day comes, print `0` for that day.

**Input:** one line of space-separated temperatures.

**Output:** the waits, space-separated.""",
        constraints=["1 <= n <= 10^5", "30 <= temperature <= 100"],
        solve=_daily,
        brute=_daily_brute,
        examples=[("73 74 75 71 69 72 76 73", "Day 0 waits 1 day for 74; day 2 waits 4 days for 76."), ("30 40 50", "Each day is warmed by the next.")],
        tests=lambda r: _arr_tests(r, ["50", "90 80 70", "60 60 60", "30 100"], 30, 100),
    ),
    Problem(
        title="Stock Span",
        difficulty="MEDIUM",
        topics=["Stack", "Monotonic Stack", "Array"],
        description="""The **span** of a stock's price on a day is the number of consecutive days, ending with that day and counting backwards, on which the price was less than or equal to that day's price. Print the span for every day.

**Input:** one line of space-separated prices.

**Output:** the spans, space-separated.""",
        constraints=["1 <= n <= 10^5", "1 <= price <= 10^5"],
        solve=_span,
        brute=_span_brute,
        examples=[("100 80 60 70 60 75 85", "On the 75 day the run 60 70 60 75 gives span 4."), ("10 10 10", "Equal prices extend the span.")],
        tests=lambda r: _arr_tests(r, ["5", "1 2 3 4", "4 3 2 1"], 1, 100),
    ),
    Problem(
        title="Asteroid Collision",
        difficulty="MEDIUM",
        topics=["Stack", "Array"],
        description="""Asteroids move along a line. The absolute value is the size; a positive sign means it moves right, negative means it moves left. All move at the same speed.

When a right-mover meets a left-mover, the smaller one explodes; if they are the same size, both explode. Two asteroids moving the same way never meet. Print the asteroids that remain after all collisions, left to right, or `empty` if none remain.

**Input:** one line of space-separated non-zero integers.

**Output:** the surviving asteroids, space-separated, or `empty`.""",
        constraints=["1 <= n <= 10^4", "1 <= |value| <= 1000"],
        solve=_asteroids,
        brute=_asteroids_brute,
        examples=[("5 10 -5", "-5 hits 10 and explodes."), ("8 -8", "Equal sizes destroy each other.")],
        tests=_t_asteroids,
    ),
    Problem(
        title="Remove K Digits",
        difficulty="MEDIUM",
        topics=["Stack", "Monotonic Stack", "String"],
        description="""Given a non-negative integer as a string, remove exactly `k` digits so the number that remains is as small as possible. Print it without leading zeros; if nothing (or only zeros) is left, print `0`.

Greedy idea: walking left to right, whenever the previous kept digit is larger than the current one, removing it makes the number smaller.

**Input:** line 1 is the number (no leading zeros unless it is `0`); line 2 is `k`.

**Output:** the smallest possible result.""",
        constraints=["1 <= length <= 10^4", "0 <= k <= length"],
        solve=_remove_k,
        brute=lambda inp: _remove_k_brute(inp) if len(lines(inp)[0]) <= 12 else _remove_k(inp),
        examples=[("1432219\n3", "Remove 4, 3 and 2 to get 1219."), ("10200\n1", "Remove the 1; leading zeros vanish, leaving 200.")],
        tests=_t_remove_k,
    ),
    Problem(
        title="Sum of Subarray Minimums",
        difficulty="MEDIUM",
        topics=["Stack", "Monotonic Stack", "Array"],
        description="""For every contiguous subarray, take its minimum. Print the sum of all those minimums modulo `1000000007`.

Instead of listing subarrays, count for each element how many subarrays it is the minimum of: (distance to the previous smaller element) × (distance to the next smaller-or-equal element). Breaking ties on one side only stops subarrays from being counted twice.

**Input:** one line of space-separated positive integers.

**Output:** the sum modulo 1000000007.""",
        constraints=["1 <= n <= 3 * 10^4", "1 <= value <= 3 * 10^4"],
        solve=_sum_mins,
        brute=_sum_mins_brute,
        examples=[("3 1 2 4", "Minimums 3,1,2,4,1,1,2,1,1,1 sum to 17."), ("2 2", "2 + 2 + 2 = 6.")],
        tests=lambda r: _arr_tests(r, ["5", "1 1 1 1", "1 2 3 4", "4 3 2 1"], 1, 30000, (8, 20, 60, 3000)),
    ),
    Problem(
        title="LRU Cache",
        difficulty="MEDIUM",
        topics=["Design", "Hash Map"],
        description="""Simulate a **least recently used** cache with a fixed capacity.

- `get k`: print the value stored for key `k`, or `-1` if it isn't cached. A successful get makes `k` the most recently used key.
- `put k v`: store `v` under `k` (updating it if present) and make `k` the most recently used key. If this pushes the size over the capacity, evict the least recently used key.

Both operations should be `O(1)`: pair a hash map with a doubly linked list ordered by recency.

**Input:** line 1 has `capacity` and `q`; each of the next `q` lines is a command.

**Output:** one line per `get` command. If there are no `get` commands, print `none`.""",
        constraints=["1 <= capacity <= 1000", "1 <= q <= 10^4"],
        solve=_lru,
        brute=_lru_brute,
        examples=[("2 6\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nget 3", "get 1 refreshes key 1, so putting 3 evicts key 2.")],
        tests=_t_lru,
    ),
    Problem(
        title="Sliding Window Maximum",
        difficulty="HARD",
        topics=["Queue", "Sliding Window", "Monotonic Stack", "Array"],
        description="""A window of size `k` slides from the left end of the array to the right end, one step at a time. Print the maximum of every window position.

Keep a deque of indices whose values are decreasing: the front is always the current maximum, and an index leaves from the front once it slides out of the window. That's `O(n)` overall.

**Input:** line 1 is the array; line 2 is `k`.

**Output:** the `n − k + 1` window maximums, space-separated.""",
        constraints=["1 <= k <= n <= 10^5"],
        solve=_window_max,
        brute=_window_max_brute,
        examples=[("1 3 -1 -3 5 3 6 7\n3", "Windows [1 3 -1], [3 -1 -3], … give 3 3 5 5 6 7."), ("9 4\n1", "Window size 1 just repeats the array.")],
        tests=_t_window,
    ),
    Problem(
        title="Largest Rectangle in Histogram",
        difficulty="HARD",
        topics=["Stack", "Monotonic Stack", "Array"],
        description="""Bars of width 1 stand side by side with the given heights. Find the area of the largest rectangle that fits entirely inside the histogram.

For each bar, the widest rectangle using its full height stretches until a shorter bar on each side. A stack of increasing heights finds those boundaries in one pass.

**Input:** one line of space-separated non-negative heights.

**Output:** the largest area.""",
        constraints=["1 <= n <= 10^5", "0 <= height <= 10^4"],
        solve=_histogram,
        brute=_histogram_brute,
        examples=[("2 1 5 6 2 3", "Heights 5 and 6 form a 5 × 2 = 10 rectangle."), ("2 4", "The single bar of height 4 gives 4.")],
        tests=lambda r: _arr_tests(r, ["0", "7", "3 3 3 3", "1 2 3 4 5", "5 4 3 2 1"], 0, 50),
    ),
    Problem(
        title="Maximal Rectangle",
        difficulty="HARD",
        topics=["Stack", "Monotonic Stack", "Array"],
        description="""Given a grid of `0`s and `1`s, find the area of the largest rectangle containing only `1`s.

Treat each row as the floor of a histogram: the height in a column is the number of consecutive `1`s ending at that row. Run the largest-rectangle-in-histogram algorithm on every row.

**Input:** line 1 has `r` and `c`; each of the next `r` lines is a string of `c` characters, each `0` or `1`.

**Output:** the largest all-ones rectangle area.""",
        constraints=["1 <= r, c <= 200"],
        solve=_maximal_rect,
        brute=lambda inp: _maximal_rect_brute(inp) if len(inp) <= 80 else _maximal_rect(inp),
        examples=[("4 5\n10100\n10111\n11111\n10010", "The 2 × 3 block of ones in rows 2–3 gives 6."), ("1 1\n0", "No ones at all.")],
        tests=_t_grid,
    ),
]
