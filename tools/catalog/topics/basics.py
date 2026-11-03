"""Basics & Math — the warm-up playlist."""
from math import gcd, isqrt

from lib import Playlist, Problem, boolstr, lines

PLAYLISTS = [
    Playlist(
        key="basics",
        title="01 · Basics & Math",
        description="Warm-up problems on digits, divisors and primes. Get comfortable reading input and printing output.",
        accent="#9BE7C4",
        titles=[
            "Hello World",
            "Print 1 to N",
            "Count Digits",
            "Reverse the Digits",
            "Palindrome Number",
            "Sum of Digits",
            "Armstrong Number",
            "Print All Divisors",
            "Check Prime",
            "GCD and LCM",
            "Factorial",
            "Fibonacci",
            "FizzBuzz",
            "Primes up to N",
            "Power of a Number (mod)",
        ],
    )
]


def _count_digits(inp):
    n = abs(int(lines(inp)[0]))
    return str(len(str(n)))


def _reverse_digits(inp):
    n = int(lines(inp)[0])
    sign = -1 if n < 0 else 1
    return str(sign * int(str(abs(n))[::-1]))


def _armstrong(inp):
    n = int(lines(inp)[0])
    s = str(n)
    return boolstr(sum(int(d) ** len(s) for d in s) == n)


def _divisors(inp):
    n = int(lines(inp)[0])
    small, large = [], []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            small.append(d)
            if d != n // d:
                large.append(n // d)
    return " ".join(map(str, small + large[::-1]))


def _divisors_brute(inp):
    n = int(lines(inp)[0])
    return " ".join(str(d) for d in range(1, n + 1) if n % d == 0)


def _is_prime(inp):
    n = int(lines(inp)[0])
    if n < 2:
        return "false"
    return boolstr(all(n % d for d in range(2, isqrt(n) + 1)))


def _gcd_lcm(inp):
    a, b = map(int, lines(inp)[0].split())
    g = gcd(a, b)
    return f"{g} {a // g * b}"


def _sieve(inp):
    n = int(lines(inp)[0])
    if n < 2:
        return "none"
    mark = [True] * (n + 1)
    mark[0] = mark[1] = False
    for i in range(2, isqrt(n) + 1):
        if mark[i]:
            mark[i * i :: i] = [False] * len(mark[i * i :: i])
    return " ".join(str(i) for i, p in enumerate(mark) if p)


def _sieve_brute(inp):
    n = int(lines(inp)[0])
    ps = [i for i in range(2, n + 1) if all(i % d for d in range(2, i))]
    return " ".join(map(str, ps)) or "none"


MOD = 1_000_000_007


def _power(inp):
    x, n = map(int, lines(inp)[0].split())
    result, base = 1, x % MOD
    while n:
        if n & 1:
            result = result * base % MOD
        base = base * base % MOD
        n >>= 1
    return str(result)


PROBLEMS = [
    Problem(
        title="Count Digits",
        difficulty="EASY",
        topics=["Math", "Basics"],
        description="""Given an integer `n`, print how many digits it has. The sign does not count as a digit.

**Input:** one integer `n`.

**Output:** the number of digits in `n`.""",
        constraints=["-10^18 <= n <= 10^18"],
        solve=_count_digits,
        examples=[("12345", "1, 2, 3, 4, 5 — five digits."), ("-708", "The minus sign is ignored, leaving 7, 0, 8.")],
        tests=lambda r: ["0", "7", "-1", "10", "1000000000000000000", "-999999999999999999"]
        + [str(r.randint(-10**18, 10**18)) for _ in range(4)],
    ),
    Problem(
        title="Reverse the Digits",
        difficulty="EASY",
        topics=["Math", "Basics"],
        description="""Reverse the digits of an integer `n` and print the result. Leading zeros disappear after reversing (`120` becomes `21`), and a negative number stays negative.

**Input:** one integer `n`.

**Output:** `n` with its digits reversed.""",
        constraints=["-10^12 <= n <= 10^12"],
        solve=_reverse_digits,
        examples=[("1234", "Read the digits backwards."), ("-560", "Reverse 560 to 065 = 65, keep the sign.")],
        tests=lambda r: ["0", "5", "-9", "100", "1000000000000", "-1200"] + [str(r.randint(-10**12, 10**12)) for _ in range(4)],
    ),
    Problem(
        title="Armstrong Number",
        difficulty="EASY",
        topics=["Math", "Basics"],
        description="""A number with `k` digits is an **Armstrong number** if the sum of each digit raised to the power `k` equals the number itself. For example `153 = 1³ + 5³ + 3³`.

Print `true` if `n` is an Armstrong number, otherwise `false`.

**Input:** one non-negative integer `n`.

**Output:** `true` or `false`.""",
        constraints=["0 <= n <= 10^9"],
        solve=_armstrong,
        examples=[("153", "1³ + 5³ + 3³ = 1 + 125 + 27 = 153."), ("123", "1³ + 2³ + 3³ = 36, not 123.")],
        tests=lambda r: ["0", "9", "10", "370", "371", "407", "1634", "9474", "9475", "548834", "1000000000"]
        + [str(r.randint(0, 10**9)) for _ in range(2)],
    ),
    Problem(
        title="Print All Divisors",
        difficulty="EASY",
        topics=["Math", "Basics"],
        description="""Print every positive divisor of `n` in increasing order.

Checking every number up to `n` works, but you only need to check up to `√n`: divisors come in pairs `d` and `n / d`.

**Input:** one positive integer `n`.

**Output:** the divisors of `n`, space-separated, in increasing order.""",
        constraints=["1 <= n <= 10^9"],
        solve=_divisors,
        brute=_divisors_brute,
        examples=[("36", "Pairs (1, 36), (2, 18), (3, 12), (4, 9) and 6 on its own."), ("13", "13 is prime.")],
        tests=lambda r: ["1", "2", "97", "100", "720720", "999999937", "1000000000", "735134400"]
        + [str(r.randint(1, 10**6)) for _ in range(3)],
    ),
    Problem(
        title="Check Prime",
        difficulty="EASY",
        topics=["Math", "Basics"],
        description="""Print `true` if `n` is a prime number, otherwise `false`. A prime has exactly two divisors: 1 and itself. 0 and 1 are not prime.

**Input:** one integer `n`.

**Output:** `true` or `false`.""",
        constraints=["0 <= n <= 10^12"],
        solve=_is_prime,
        examples=[("29", "Only 1 and 29 divide it."), ("21", "21 = 3 × 7.")],
        tests=lambda r: ["0", "1", "2", "3", "4", "97", "1000000007", "999999999989", "999999999999", "1000000000000"]
        + [str(r.randint(2, 10**9)) for _ in range(3)],
    ),
    Problem(
        title="GCD and LCM",
        difficulty="EASY",
        topics=["Math", "Basics"],
        description="""Given two positive integers `a` and `b`, print their greatest common divisor and least common multiple.

Use the Euclidean algorithm: `gcd(a, b) = gcd(b, a mod b)`, and `lcm(a, b) = a / gcd(a, b) × b`.

**Input:** one line with `a` and `b`.

**Output:** `gcd lcm` on one line.""",
        constraints=["1 <= a, b <= 10^9"],
        solve=_gcd_lcm,
        examples=[("12 18", "gcd = 6, lcm = 36."), ("7 13", "Coprime: gcd 1, lcm 91.")],
        tests=lambda r: ["1 1", "1 1000000000", "1000000000 1000000000", "999999937 999999929", "48 180", "17 51"]
        + [f"{r.randint(1, 10**9)} {r.randint(1, 10**9)}" for _ in range(4)],
    ),
    Problem(
        title="Primes up to N",
        difficulty="MEDIUM",
        topics=["Math", "Sieve"],
        description="""Print every prime number less than or equal to `n`, in increasing order. If there are none, print `none`.

Testing each number separately is slow for large `n`. The **Sieve of Eratosthenes** crosses out multiples of each prime instead, in `O(n log log n)`.

**Input:** one integer `n`.

**Output:** the primes up to `n`, space-separated, or `none`.""",
        constraints=["0 <= n <= 10^5"],
        solve=_sieve,
        brute=_sieve_brute,
        examples=[("20", "2, 3, 5, 7, 11, 13, 17, 19."), ("1", "There are no primes below 2.")],
        tests=lambda r: ["0", "2", "3", "10", "97", "100", "1000", "30000"] + [str(r.randint(50, 400)) for _ in range(2)],
    ),
    Problem(
        title="Power of a Number (mod)",
        difficulty="MEDIUM",
        topics=["Math", "Recursion", "Bit Manipulation"],
        description="""Compute `x` raised to the power `n`, modulo `1000000007`.

`n` can be as large as 10^18, so multiplying `n` times is too slow. Use **fast exponentiation**: square the base and halve the exponent, multiplying into the result whenever the current bit of `n` is 1. That's `O(log n)`.

**Input:** one line with `x` and `n`.

**Output:** `x^n mod 1000000007`.""",
        constraints=["0 <= x <= 10^9", "0 <= n <= 10^18"],
        solve=_power,
        examples=[("2 10", "2^10 = 1024."), ("3 0", "Anything to the power 0 is 1.")],
        tests=lambda r: ["0 0", "0 5", "1 1000000000000000000", "2 1000000000000000000", "1000000007 3", "999999999 999999999", "10 9"]
        + [f"{r.randint(0, 10**9)} {r.randint(0, 10**18)}" for _ in range(3)],
    ),
]
