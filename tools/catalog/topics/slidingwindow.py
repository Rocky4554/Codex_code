"""Sliding Window & Two Pointers — linear-time scans over subarrays and substrings."""
from collections import Counter, defaultdict

from lib import Playlist, Problem, ints, join, lines, rand_ints, rand_str

PLAYLISTS = [
    Playlist(
        key="slidingwindow",
        title="11 · Sliding Window & Two Pointers",
        description="Grow a window on the right, shrink it on the left: turn nested loops over subarrays into one linear pass.",
        accent="#FFD6A5",
        titles=[
            "Maximum Sum Subarray of Size K",
            "Maximum Points from Cards",
            "Container With Most Water",
            "Longest Substring Without Repeating Characters",
            "Max Consecutive Ones III",
            "Fruit into Baskets",
            "Minimum Size Subarray Sum",
            "Longest Repeating Character Replacement",
            "Subarray Product Less Than K",
            "Binary Subarrays With Sum",
            "Count Number of Nice Subarrays",
            "Number of Substrings Containing All Three Characters",
            "Longest Substring with At Most K Distinct Characters",
            "Subarrays with K Different Integers",
            "Minimum Window Substring",
            "Trapping Rain Water",
        ],
    )
]


def _arr_k(inp):
    ls = lines(inp)
    return ints(ls[0]), int(ls[1])


# ── solutions ────────────────────────────────────────────────────

def _max_sum_k(inp):
    a, k = _arr_k(inp)
    cur = best = sum(a[:k])
    for i in range(k, len(a)):
        cur += a[i] - a[i - k]
        best = max(best, cur)
    return str(best)


def _max_sum_k_brute(inp):
    a, k = _arr_k(inp)
    return str(max(sum(a[i : i + k]) for i in range(len(a) - k + 1)))


def _cards(inp):
    a, k = _arr_k(inp)
    n = len(a)
    cur = best = sum(a[:k])
    for i in range(1, k + 1):  # swap the i-th card from the left end for one from the right end
        cur += a[n - i] - a[k - i]
        best = max(best, cur)
    return str(best)


def _cards_brute(inp):
    a, k = _arr_k(inp)
    n = len(a)
    return str(max(sum(a[:left]) + sum(a[n - (k - left) :]) if k - left else sum(a[:left]) for left in range(k + 1)))


def _ones_iii(inp):
    a, k = _arr_k(inp)
    left = zeros = best = 0
    for right, x in enumerate(a):
        zeros += x == 0
        while zeros > k:
            zeros -= a[left] == 0
            left += 1
        best = max(best, right - left + 1)
    return str(best)


def _ones_iii_brute(inp):
    a, k = _arr_k(inp)
    best = 0
    for i in range(len(a)):
        z = 0
        for j in range(i, len(a)):
            z += a[j] == 0
            if z > k:
                break
            best = max(best, j - i + 1)
    return str(best)


def _min_size(inp):
    a, target = _arr_k(inp)
    left = s = 0
    best = len(a) + 1
    for right, x in enumerate(a):
        s += x
        while s >= target:
            best = min(best, right - left + 1)
            s -= a[left]
            left += 1
    return str(best if best <= len(a) else 0)


def _min_size_brute(inp):
    a, target = _arr_k(inp)
    best = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s >= target:
                if not best or j - i + 1 < best:
                    best = j - i + 1
                break
    return str(best)


def _char_replace(inp):
    ls = lines(inp)
    s, k = ls[0], int(ls[1])
    count = Counter()
    left = top = best = 0
    for right, ch in enumerate(s):
        count[ch] += 1
        top = max(top, count[ch])
        while right - left + 1 - top > k:
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return str(best)


def _char_replace_brute(inp):
    ls = lines(inp)
    s, k = ls[0], int(ls[1])
    best = 0
    for i in range(len(s)):
        c = Counter()
        for j in range(i, len(s)):
            c[s[j]] += 1
            if j - i + 1 - max(c.values()) <= k:
                best = max(best, j - i + 1)
    return str(best)


def _product_less(inp):
    a, k = _arr_k(inp)
    if k <= 1:
        return "0"
    prod, left, count = 1, 0, 0
    for right, x in enumerate(a):
        prod *= x
        while prod >= k:
            prod //= a[left]
            left += 1
        count += right - left + 1
    return str(count)


def _product_less_brute(inp):
    a, k = _arr_k(inp)
    count = 0
    for i in range(len(a)):
        p = 1
        for j in range(i, len(a)):
            p *= a[j]
            if p >= k:
                break
            count += 1
    return str(count)


def _at_most_sum(a, goal):
    if goal < 0:
        return 0
    left = s = count = 0
    for right, x in enumerate(a):
        s += x
        while s > goal:
            s -= a[left]
            left += 1
        count += right - left + 1
    return count


def _binary_sum(inp):
    a, goal = _arr_k(inp)
    return str(_at_most_sum(a, goal) - _at_most_sum(a, goal - 1))


def _binary_sum_brute(inp):
    a, goal = _arr_k(inp)
    return str(sum(1 for i in range(len(a)) for j in range(i, len(a)) if sum(a[i : j + 1]) == goal))


def _at_most_distinct(a, k):
    count = defaultdict(int)
    left = total = 0
    for right, x in enumerate(a):
        count[x] += 1
        while len(count) > k:
            count[a[left]] -= 1
            if count[a[left]] == 0:
                del count[a[left]]
            left += 1
        total += right - left + 1
    return total


def _k_distinct(inp):
    a, k = _arr_k(inp)
    return str(_at_most_distinct(a, k) - _at_most_distinct(a, k - 1))


def _k_distinct_brute(inp):
    a, k = _arr_k(inp)
    return str(sum(1 for i in range(len(a)) for j in range(i, len(a)) if len(set(a[i : j + 1])) == k))


def _min_window(inp):
    ls = lines(inp)
    s, t = ls[0], ls[1]
    need = Counter(t)
    missing = len(t)
    left = 0
    best = (len(s) + 1, 0)
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if right - left + 1 < best[0]:
                best = (right - left + 1, left)
            need[s[left]] += 1
            missing += 1
            left += 1
    size, start = best
    return s[start : start + size] if size <= len(s) else "-1"


def _min_window_brute(inp):
    ls = lines(inp)
    s, t = ls[0], ls[1]
    need = Counter(t)
    for size in range(len(t), len(s) + 1):
        for i in range(len(s) - size + 1):
            if not need - Counter(s[i : i + size]):
                return s[i : i + size]
    return "-1"


# ── test generators ──────────────────────────────────────────────

def _t_arr_k(r, special, lo, hi, k_of_n, sizes=(8, 15, 40, 2500)):
    out = list(special)
    for n in sizes:
        out.append(f"{join(rand_ints(r, n, lo, hi))}\n{k_of_n(r, n)}")
    return out


def _t_char_replace(r):
    out = ["A\n0", "A\n1", "AB\n0", "AAAA\n2", "ABCD\n0", "ABCD\n4"]
    for n, alpha in ((10, "AB"), (20, "ABC"), (40, "ABCDE"), (3000, "ABCD")):
        out.append(f"{rand_str(r, n, alpha)}\n{r.randint(0, n // 3)}")
    return out


def _t_min_window(r):
    out = ["a\na", "a\nb", "a\naa", "aa\naa", "ab\nb", "bba\nab", "aAbB\nAb", "cabwefgewcwaefgcf\ncae"]
    for n, m, alpha in ((12, 3, "abc"), (30, 4, "abcde"), (60, 6, "abcdefg"), (3000, 15, "abcdefghijklmnop")):
        s = rand_str(r, n, alpha)
        t = rand_str(r, m, alpha)
        out.append(f"{s}\n{t}")
    return out


PROBLEMS = [
    Problem(
        title="Maximum Sum Subarray of Size K",
        difficulty="EASY",
        topics=["Sliding Window", "Array"],
        description="""Find the largest sum of any `k` consecutive elements.

Compute the first window's sum, then slide: add the element entering on the right and subtract the one leaving on the left. Each step is `O(1)`.

**Input:** line 1 is the array; line 2 is `k`.

**Output:** the maximum window sum.""",
        constraints=["1 <= k <= n <= 10^5", "-10^4 <= value <= 10^4"],
        solve=_max_sum_k,
        brute=_max_sum_k_brute,
        examples=[("2 1 5 1 3 2\n3", "The window 5 1 3 sums to 9."), ("-1 -2 -3\n1", "With negatives only, pick the largest single value.")],
        tests=lambda r: _t_arr_k(r, ["5\n1", "4 4 4\n3", "1 2 3 4\n4", "-5 -1 -3\n2"], -100, 100, lambda r, n: r.randint(1, n)),
    ),
    Problem(
        title="Maximum Points from Cards",
        difficulty="MEDIUM",
        topics=["Sliding Window", "Array"],
        description="""Cards lie in a row, each worth some points. You must take exactly `k` cards, and each time you may only take a card from the **left end or the right end** of the row. Maximise your total.

Any valid choice takes some cards from the left and the rest from the right. Start with all `k` from the left, then trade them one at a time for cards from the right.

**Input:** line 1 is the card values; line 2 is `k`.

**Output:** the maximum total.""",
        constraints=["1 <= k <= n <= 10^5", "1 <= value <= 10^4"],
        solve=_cards,
        brute=_cards_brute,
        examples=[("1 2 3 4 5 6 1\n3", "Taking all three from the right (5 + 6 + 1 = 12) beats any mix with the left end."), ("9 7 7 9 7 7 9\n7", "k = n takes every card.")],
        tests=lambda r: _t_arr_k(r, ["5\n1", "2 2 2\n2", "100 1 1 1 100\n2", "1 1000 1\n1"], 1, 100, lambda r, n: r.randint(1, n)),
    ),
    Problem(
        title="Max Consecutive Ones III",
        difficulty="MEDIUM",
        topics=["Sliding Window", "Array"],
        description="""The array holds only `0`s and `1`s. You may flip at most `k` zeros into ones. Print the length of the longest run of consecutive ones you can get.

Equivalently: find the longest window that contains at most `k` zeros.

**Input:** line 1 is the array; line 2 is `k`.

**Output:** the longest possible run.""",
        constraints=["1 <= n <= 10^5", "0 <= k <= n"],
        solve=_ones_iii,
        brute=_ones_iii_brute,
        examples=[("1 1 1 0 0 0 1 1 1 1 0\n2", "Flip the two zeros before the run of four ones: length 6."), ("0 0 0\n0", "No flips allowed and no ones.")],
        tests=lambda r: _t_arr_k(r, ["1\n0", "0\n1", "1 1 1\n0", "0 0 0 0\n4"], 0, 1, lambda r, n: r.randint(0, n // 2)),
    ),
    Problem(
        title="Minimum Size Subarray Sum",
        difficulty="MEDIUM",
        topics=["Sliding Window", "Array"],
        description="""All values are positive. Find the length of the shortest contiguous subarray whose sum is **at least** `target`. Print `0` if no such subarray exists.

Because every value is positive, growing the window only increases the sum and shrinking it only decreases it, so two pointers work.

**Input:** line 1 is the array; line 2 is `target`.

**Output:** the minimal length, or `0`.""",
        constraints=["1 <= n <= 10^5", "1 <= value <= 10^4", "1 <= target <= 10^9"],
        solve=_min_size,
        brute=_min_size_brute,
        examples=[("2 3 1 2 4 3\n7", "4 3 reaches 7 with two elements."), ("1 1 1\n5", "The whole array only sums to 3.")],
        tests=lambda r: _t_arr_k(r, ["5\n5", "5\n6", "1 4 4\n4", "1 2 3 4 5\n15"], 1, 20, lambda r, n: r.randint(1, 10 * n)),
    ),
    Problem(
        title="Longest Repeating Character Replacement",
        difficulty="MEDIUM",
        topics=["Sliding Window", "String", "Hash Map"],
        description="""The string contains uppercase letters. You may change at most `k` characters to any other uppercase letter. Print the length of the longest substring that consists of a single repeated letter after the changes.

A window is fixable when `window length − (count of its most frequent letter) <= k`.

**Input:** line 1 is the string; line 2 is `k`.

**Output:** the longest achievable length.""",
        constraints=["1 <= length <= 10^5", "0 <= k <= length"],
        solve=_char_replace,
        brute=_char_replace_brute,
        examples=[("ABAB\n2", "Change both A's (or both B's): length 4."), ("AABABBA\n1", "Change the A in BABB to get BBBB, length 4.")],
        tests=_t_char_replace,
    ),
    Problem(
        title="Subarray Product Less Than K",
        difficulty="MEDIUM",
        topics=["Sliding Window", "Array"],
        description="""All values are positive. Count the contiguous subarrays whose product is **strictly less** than `k`.

When the window `[left, right]` is valid, every subarray ending at `right` and starting at or after `left` is valid too, adding `right − left + 1` to the count.

**Input:** line 1 is the array; line 2 is `k`.

**Output:** the number of such subarrays.""",
        constraints=["1 <= n <= 3 * 10^4", "1 <= value <= 1000", "0 <= k <= 10^6"],
        solve=_product_less,
        brute=_product_less_brute,
        examples=[("10 5 2 6\n100", "Eight subarrays, e.g. [5 2 6] = 60."), ("1 2 3\n0", "No product is below 0.")],
        tests=lambda r: _t_arr_k(r, ["1\n1", "1\n2", "1 1 1\n2", "5 5 5\n26"], 1, 12, lambda r, n: r.randint(0, 2000), (8, 15, 40, 3000)),
    ),
    Problem(
        title="Binary Subarrays With Sum",
        difficulty="MEDIUM",
        topics=["Sliding Window", "Array", "Hash Map"],
        description="""The array holds only `0`s and `1`s. Count the contiguous subarrays whose sum equals exactly `goal`.

"Exactly `goal`" is hard to slide directly, but "at most `goal`" is easy. Use `count(sum <= goal) − count(sum <= goal − 1)`.

**Input:** line 1 is the array; line 2 is `goal`.

**Output:** the number of subarrays.""",
        constraints=["1 <= n <= 3 * 10^4", "0 <= goal <= n"],
        solve=_binary_sum,
        brute=_binary_sum_brute,
        examples=[("1 0 1 0 1\n2", "Four subarrays contain exactly two ones."), ("0 0 0\n0", "All six subarrays sum to 0.")],
        tests=lambda r: _t_arr_k(r, ["1\n1", "1\n0", "0\n1", "1 1 1\n3"], 0, 1, lambda r, n: r.randint(0, n // 2), (8, 15, 40, 3000)),
    ),
    Problem(
        title="Subarrays with K Different Integers",
        difficulty="HARD",
        topics=["Sliding Window", "Array", "Hash Map"],
        description="""Count the contiguous subarrays that contain **exactly** `k` distinct integers.

As with sums, "exactly `k`" equals "at most `k`" minus "at most `k − 1`", and "at most `k` distinct" is a standard sliding window with a frequency map.

**Input:** line 1 is the array; line 2 is `k`.

**Output:** the number of subarrays.""",
        constraints=["1 <= n <= 2 * 10^4", "1 <= k <= n"],
        solve=_k_distinct,
        brute=_k_distinct_brute,
        examples=[("1 2 1 2 3\n2", "Seven subarrays, e.g. [1 2], [2 1 2], [1 2 1 2]."), ("1 2 1 3 4\n3", "[1 2 1 3], [2 1 3], [1 3 4].")],
        tests=lambda r: _t_arr_k(r, ["1\n1", "1 1 1\n1", "1 2 3\n3", "1 2 3\n2"], 1, 5, lambda r, n: r.randint(1, min(5, n)), (8, 15, 40, 3000)),
    ),
    Problem(
        title="Minimum Window Substring",
        difficulty="HARD",
        topics=["Sliding Window", "String", "Hash Map"],
        description="""Find the shortest substring of `s` that contains every character of `t`, counting repeats (if `t` has two `a`s, the window needs at least two `a`s). Characters are case-sensitive.

If several shortest windows exist, print the **leftmost** one. If no window works, print `-1`.

**Input:** line 1 is `s`; line 2 is `t`. Both contain only English letters.

**Output:** the minimum window, or `-1`.""",
        constraints=["1 <= |s|, |t| <= 10^5"],
        solve=_min_window,
        brute=_min_window_brute,
        examples=[("ADOBECODEBANC\nABC", "BANC is the shortest window holding A, B and C."), ("a\naa", "s has only one a.")],
        tests=_t_min_window,
    ),
]
