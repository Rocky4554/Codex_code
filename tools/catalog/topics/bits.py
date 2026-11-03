"""Bit Manipulation."""
from functools import reduce

from lib import Playlist, Problem, boolstr, ints, join, lines, rand_ints

PLAYLISTS = [
    Playlist(
        key="bits",
        title="09 · Bit Manipulation",
        description="Work directly with the binary form of numbers: test, set and count bits, and let XOR cancel things out.",
        accent="#A7D8F0",
        titles=[
            "Check the i-th Bit",
            "Set and Clear the i-th Bit",
            "Check Power of Two",
            "Count Set Bits",
            "Minimum Bit Flips",
            "Single Number",
            "XOR from 1 to N",
            "XOR of a Range",
            "Counting Bits up to N",
            "Two Numbers Appearing Once",
            "Divide Without Multiplying",
        ],
    )
]


def _check_bit(inp):
    n, i = map(int, lines(inp)[0].split())
    return boolstr(n >> i & 1 == 1)


def _set_clear(inp):
    n, i = map(int, lines(inp)[0].split())
    return f"{n | (1 << i)} {n & ~(1 << i)}"


def _set_clear_brute(inp):
    n, i = map(int, lines(inp)[0].split())
    b = list(bin(n)[2:].zfill(max(i + 1, n.bit_length())))
    b[-1 - i] = "1"
    s = int("".join(b), 2)
    b[-1 - i] = "0"
    return f"{s} {int(''.join(b), 2)}"


def _pow2(inp):
    n = int(lines(inp)[0])
    return boolstr(n > 0 and n & (n - 1) == 0)


def _pow2_brute(inp):
    n = int(lines(inp)[0])
    return boolstr(n > 0 and bin(n).count("1") == 1)


def _popcount(inp):
    n = int(lines(inp)[0])
    c = 0
    while n:
        n &= n - 1
        c += 1
    return str(c)


def _popcount_brute(inp):
    return str(bin(int(lines(inp)[0])).count("1"))


def _flips(inp):
    a, b = map(int, lines(inp)[0].split())
    return str(bin(a ^ b).count("1"))


def _flips_brute(inp):
    a, b = map(int, lines(inp)[0].split())
    w = max(a.bit_length(), b.bit_length(), 1)
    return str(sum(x != y for x, y in zip(bin(a)[2:].zfill(w), bin(b)[2:].zfill(w))))


def _xor_upto(n):
    return [n, 1, n + 1, 0][n % 4]


def _xor1n(inp):
    return str(_xor_upto(int(lines(inp)[0])))


def _xor1n_brute(inp):
    n = int(lines(inp)[0])
    if n > 10**6:
        return _xor1n(inp)
    return str(reduce(lambda a, b: a ^ b, range(1, n + 1), 0))


def _xor_range(inp):
    l, r = map(int, lines(inp)[0].split())
    return str(_xor_upto(r) ^ _xor_upto(l - 1))


def _xor_range_brute(inp):
    l, r = map(int, lines(inp)[0].split())
    if r - l > 10**6:  # too big to loop; only small ranges are cross-checked
        return _xor_range(inp)
    return str(reduce(lambda a, b: a ^ b, range(l, r + 1), 0))


def _counting(inp):
    n = int(lines(inp)[0])
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return join(dp)


def _counting_brute(inp):
    return join(bin(i).count("1") for i in range(int(lines(inp)[0]) + 1))


def _two_once(inp):
    nums = ints(lines(inp)[0])
    x = 0
    for v in nums:
        x ^= v
    low = x & -x
    a = b = 0
    for v in nums:
        if v & low:
            a ^= v
        else:
            b ^= v
    return join(sorted((a, b)))


def _two_once_brute(inp):
    nums = ints(lines(inp)[0])
    return join(sorted(v for v in set(nums) if nums.count(v) == 1))


def _two_once_tests(r):
    out = ["1 2", "-1 0", "5 5 7 9", "0 3 3 -8 4 4"]
    for n in (5, 50, 2000):
        pool = r.sample(range(-10**6, 10**6), n + 2)
        singles, pairs = pool[:2], pool[2:]
        arr = singles + pairs + pairs
        r.shuffle(arr)
        out.append(join(arr))
    for _ in range(2):
        pool = r.sample(range(0, 100), 8)
        arr = pool[:2] + pool[2:] * 2
        r.shuffle(arr)
        out.append(join(arr))
    return out


def _divide(inp):
    a, b = map(int, lines(inp)[0].split())
    neg = (a < 0) != (b < 0)
    x, y = abs(a), abs(b)
    q = 0
    for shift in range(32, -1, -1):
        if (y << shift) <= x:
            x -= y << shift
            q |= 1 << shift
    q = -q if neg else q
    return str(max(-(2**31), min(2**31 - 1, q)))


def _divide_brute(inp):
    a, b = map(int, lines(inp)[0].split())
    q = abs(a) // abs(b)
    q = -q if (a < 0) != (b < 0) else q
    return str(max(-(2**31), min(2**31 - 1, q)))


PROBLEMS = [
    Problem(
        title="Check the i-th Bit",
        difficulty="EASY",
        topics=["Bit Manipulation"],
        description="""Is bit `i` of `n` set? Bits are numbered from the right starting at 0, so bit 0 is the ones place.

Shift `n` right by `i` and look at the lowest bit, or AND `n` with `1 << i`.

**Input:** one line with `n` and `i`.

**Output:** `true` if bit `i` is 1, otherwise `false`.""",
        constraints=["0 <= n <= 10^18", "0 <= i <= 62"],
        solve=_check_bit,
        examples=[("13 2", "13 is 1101 in binary; bit 2 is 1."), ("13 1", "Bit 1 of 1101 is 0.")],
        tests=lambda r: ["0 0", "1 0", "1 1", "1024 10", "1023 10", "1000000000000000000 59", "4611686018427387904 62"]
        + [f"{r.randint(0, 10**18)} {r.randint(0, 62)}" for _ in range(3)],
    ),
    Problem(
        title="Set and Clear the i-th Bit",
        difficulty="EASY",
        topics=["Bit Manipulation"],
        description="""Given `n` and a bit position `i` (0 = rightmost), print two numbers: `n` with bit `i` forced to 1, and `n` with bit `i` forced to 0.

Use OR with `1 << i` to set, and AND with the complement `~(1 << i)` to clear.

**Input:** one line with `n` and `i`.

**Output:** `set cleared` on one line.""",
        constraints=["0 <= n <= 10^18", "0 <= i <= 62"],
        solve=_set_clear,
        brute=_set_clear_brute,
        examples=[("9 1", "1001 → set bit 1: 1011 = 11; clear bit 1: 1001 = 9."), ("15 3", "1111 → 1111 = 15 and 0111 = 7.")],
        tests=lambda r: ["0 0", "0 5", "1 0", "255 7", "256 8", "1000000000000000000 0", "0 62"]
        + [f"{r.randint(0, 10**18)} {r.randint(0, 62)}" for _ in range(3)],
    ),
    Problem(
        title="Check Power of Two",
        difficulty="EASY",
        topics=["Bit Manipulation", "Math"],
        description="""Print `true` if `n` is a power of two (1, 2, 4, 8, …), otherwise `false`.

A power of two has exactly one set bit, so `n & (n − 1)` is 0 for it — and only for it (when `n > 0`).

**Input:** one integer `n`.

**Output:** `true` or `false`.""",
        constraints=["-10^18 <= n <= 10^18"],
        solve=_pow2,
        brute=_pow2_brute,
        examples=[("16", "16 = 10000 in binary."), ("12", "12 = 1100 has two set bits.")],
        tests=lambda r: ["0", "1", "2", "3", "-4", "-1", "1073741824", "1152921504606846976", "1152921504606846977", "999999999999999999"]
        + [str(r.randint(1, 10**18)) for _ in range(2)],
    ),
    Problem(
        title="Count Set Bits",
        difficulty="EASY",
        topics=["Bit Manipulation"],
        description="""Count how many 1s appear in the binary form of `n`.

A neat trick: `n & (n − 1)` removes the lowest set bit, so repeat it until `n` is 0 and count the steps.

**Input:** one non-negative integer `n`.

**Output:** the number of set bits.""",
        constraints=["0 <= n <= 10^18"],
        solve=_popcount,
        brute=_popcount_brute,
        examples=[("11", "11 = 1011 has three 1s."), ("128", "128 = 10000000.")],
        tests=lambda r: ["0", "1", "255", "256", "1000000000000000000", "576460752303423487"] + [str(r.randint(0, 10**18)) for _ in range(4)],
    ),
    Problem(
        title="Minimum Bit Flips",
        difficulty="EASY",
        topics=["Bit Manipulation"],
        description="""How many single-bit flips does it take to turn `a` into `b`? Each flip changes one bit from 0 to 1 or 1 to 0.

The bits that differ are exactly the set bits of `a XOR b`.

**Input:** one line with `a` and `b`.

**Output:** the minimum number of flips.""",
        constraints=["0 <= a, b <= 10^18"],
        solve=_flips,
        brute=_flips_brute,
        examples=[("10 7", "1010 vs 0111 differ in 3 places."), ("5 5", "Already equal.")],
        tests=lambda r: ["0 0", "0 1", "1 0", "0 1000000000000000000", "255 0", "123456789 987654321"]
        + [f"{r.randint(0, 10**18)} {r.randint(0, 10**18)}" for _ in range(4)],
    ),
    Problem(
        title="XOR from 1 to N",
        difficulty="EASY",
        topics=["Bit Manipulation", "Math"],
        description="""Compute `1 XOR 2 XOR … XOR n` (0 when `n` is 0).

Looping works for small `n`, but `n` here can be huge. Write out the first few prefix XORs and you'll spot a pattern that repeats every 4 numbers.

**Input:** one integer `n`.

**Output:** the XOR of all integers from 1 to `n`.""",
        constraints=["0 <= n <= 10^18"],
        solve=_xor1n,
        examples=[("5", "1^2^3^4^5 = 1."), ("4", "1^2^3^4 = 4.")],
        tests=lambda r: ["0", "1", "2", "3", "6", "7", "100", "1000000000000000000", "999999999999999999"] + [str(r.randint(0, 10**18)) for _ in range(2)],
        brute=_xor1n_brute,
    ),
    Problem(
        title="XOR of a Range",
        difficulty="MEDIUM",
        topics=["Bit Manipulation", "Math"],
        description="""Compute `L XOR (L+1) XOR … XOR R`.

XOR cancels itself out: the XOR from L to R equals (XOR from 1 to R) XOR (XOR from 1 to L−1).

**Input:** one line with `L` and `R`.

**Output:** the XOR of every integer in `[L, R]`.""",
        constraints=["1 <= L <= R <= 10^18"],
        solve=_xor_range,
        brute=_xor_range_brute,
        examples=[("4 8", "4^5^6^7^8 = 8."), ("3 3", "A single number.")],
        tests=lambda r: ["1 1", "1 2", "1 10", "5 9", "100 199", "37 1000"]
        + [(lambda a: f"{a} {a + r.randint(0, 300)}")(r.randint(1, 10**4)) for _ in range(2)]
        + ["1 1000000000000000000", "123456789012 987654321098765"],
    ),
    Problem(
        title="Counting Bits up to N",
        difficulty="EASY",
        topics=["Bit Manipulation", "DP"],
        description="""For every integer `i` from 0 to `n`, count the set bits of `i`.

Reuse earlier answers: `i` has the same bits as `i >> 1` plus its own lowest bit.

**Input:** one integer `n`.

**Output:** `n + 1` space-separated counts, for `i = 0, 1, …, n`.""",
        constraints=["0 <= n <= 5000"],
        solve=_counting,
        brute=_counting_brute,
        examples=[("5", "0, 1, 10, 11, 100, 101 → 0 1 1 2 1 2."), ("0", "Just 0.")],
        tests=lambda r: ["1", "2", "15", "16", "64", "1000", "5000"] + [str(r.randint(3, 200)) for _ in range(2)],
    ),
    Problem(
        title="Two Numbers Appearing Once",
        difficulty="MEDIUM",
        topics=["Bit Manipulation", "Array"],
        description="""Every number in the array appears exactly twice, except two numbers that appear exactly once. Find those two.

XOR of the whole array is `a XOR b`. Any set bit in it is a bit where `a` and `b` differ — use it to split the array into two groups and XOR each group.

**Input:** one line of space-separated integers.

**Output:** the two numbers that appear once, smaller first.""",
        constraints=["2 <= n <= 3 × 10^4", "-10^6 <= nums[i] <= 10^6"],
        solve=_two_once,
        brute=_two_once_brute,
        examples=[("1 2 1 3 2 5", "3 and 5 have no partner."), ("-1 0", "Both appear once.")],
        tests=_two_once_tests,
    ),
    Problem(
        title="Divide Without Multiplying",
        difficulty="MEDIUM",
        topics=["Bit Manipulation", "Math"],
        description="""Divide `a` by `b` **without** using multiplication, division or modulo, truncating toward zero (`7 / -2 = -3`). The result must fit in a signed 32-bit integer; if it's larger than `2147483647`, print `2147483647`.

Subtract the largest `b × 2^k` that still fits, again and again, using shifts.

**Input:** one line with `a` and `b`.

**Output:** the truncated quotient.""",
        constraints=["-2^31 <= a, b <= 2^31 − 1", "b != 0"],
        solve=_divide,
        brute=_divide_brute,
        examples=[("10 3", "10 / 3 = 3.33…, truncated to 3."), ("7 -2", "−3.5 truncates toward zero: −3.")],
        tests=lambda r: ["0 1", "1 1", "-2147483648 -1", "-2147483648 1", "2147483647 1", "2147483647 2", "-7 2", "-7 -2", "5 10"]
        + [f"{r.randint(-2**31, 2**31 - 1)} {r.choice([-1, 1]) * r.randint(1, 10**5)}" for _ in range(3)],
    ),
]
