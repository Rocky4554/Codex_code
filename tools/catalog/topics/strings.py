"""Strings — scanning, counting and building strings."""
from collections import Counter

from lib import Playlist, Problem, boolstr, lines, rand_str

PLAYLISTS = [
    Playlist(
        key="strings",
        title="06 · Strings",
        description="Character-level scans, counting and careful parsing, from reversing words to palindromic substrings.",
        accent="#C9C3F5",
        titles=[
            "Reverse String",
            "Count Vowels",
            "Check Palindrome",
            "Largest Odd Number in String",
            "Remove Outermost Parentheses",
            "Reverse Words in a String",
            "Remove Duplicate Characters",
            "Check Anagram",
            "Rotate String Check",
            "First Non-Repeating Character",
            "Longest Common Prefix",
            "String Compression",
            "Maximum Nesting Depth of Parentheses",
            "Roman to Integer",
            "Integer to Roman",
            "Sort Characters by Frequency",
            "String to Integer",
            "Count Palindromic Substrings",
            "Longest Palindromic Substring",
            "Sum of Beauty of All Substrings",
        ],
    )
]


def _first(inp):
    return lines(inp)[0]


def _outermost(inp):
    s = _first(inp)
    out, depth = [], 0
    for ch in s:
        if ch == "(":
            if depth:
                out.append(ch)
            depth += 1
        else:
            depth -= 1
            if depth:
                out.append(ch)
    return "".join(out) or "none"


def _outermost_brute(inp):
    s = _first(inp)
    parts, start, depth = [], 0, 0
    for i, ch in enumerate(s):
        depth += 1 if ch == "(" else -1
        if depth == 0:
            parts.append(s[start + 1:i])
            start = i + 1
    return "".join(parts) or "none"


def _reverse_words(inp):
    return " ".join(reversed(_first(inp).split()))


def _largest_odd(inp):
    s = _first(inp)
    for i in range(len(s) - 1, -1, -1):
        if int(s[i]) % 2:
            return s[: i + 1]
    return "none"


def _largest_odd_brute(inp):
    s = _first(inp)
    best = None
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            t = s[i:j]
            if int(t[-1]) % 2 and (best is None or int(t) > int(best)):
                best = t
    return best if best is not None else "none"


def _rotate(inp):
    s, goal = lines(inp)[:2]
    return boolstr(len(s) == len(goal) and goal in s + s)


def _rotate_brute(inp):
    s, goal = lines(inp)[:2]
    return boolstr(any(s[i:] + s[:i] == goal for i in range(len(s))))


def _sort_freq(inp):
    c = Counter(_first(inp))
    return "".join(ch * k for ch, k in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def _nesting(inp):
    depth = best = 0
    for ch in _first(inp):
        if ch == "(":
            depth += 1
            best = max(best, depth)
        elif ch == ")":
            depth -= 1
    return str(best)


ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
         (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
VALUE = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _to_roman(n):
    out = []
    for v, sym in ROMAN:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)


def _roman_to_int(inp):
    s = _first(inp)
    total = 0
    for i, ch in enumerate(s):
        v = VALUE[ch]
        if i + 1 < len(s) and VALUE[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return str(total)


def _roman_to_int_brute(inp):
    s = _first(inp)
    return str(next(n for n in range(1, 4000) if _to_roman(n) == s))


def _int_to_roman(inp):
    return _to_roman(int(_first(inp)))


def _atoi(inp):
    s = inp.split("\n")[0]
    i, n = 0, len(s)
    while i < n and s[i] == " ":
        i += 1
    sign = 1
    if i < n and s[i] in "+-":
        sign = -1 if s[i] == "-" else 1
        i += 1
    val = 0
    while i < n and s[i].isdigit():
        val = val * 10 + int(s[i])
        i += 1
    val *= sign
    return str(max(-2**31, min(2**31 - 1, val)))


def _count_pal(inp):
    s = _first(inp)
    total = 0
    for c in range(2 * len(s) - 1):
        lo, hi = c // 2, c // 2 + c % 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            total += 1
            lo -= 1
            hi += 1
    return str(total)


def _count_pal_brute(inp):
    s = _first(inp)
    return str(sum(s[i:j] == s[i:j][::-1] for i in range(len(s)) for j in range(i + 1, len(s) + 1)))


def _beauty(inp):
    s = _first(inp)
    total = 0
    for i in range(len(s)):
        freq = [0] * 26
        for j in range(i, len(s)):
            freq[ord(s[j]) - 97] += 1
            present = [f for f in freq if f]
            total += max(present) - min(present)
    return str(total)


def _beauty_brute(inp):
    s = _first(inp)
    total = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            c = Counter(s[i:j]).values()
            total += max(c) - min(c)
    return str(total)


# ── generators ───────────────────────────────────────────────────

def _primitive(r, pairs):
    """A random balanced parentheses string with `pairs` pairs."""
    out, opened, closed = [], 0, 0
    while closed < pairs:
        if opened < pairs and (opened == closed or r.random() < 0.5):
            out.append("(")
            opened += 1
        else:
            out.append(")")
            closed += 1
    return "".join(out)


def _balanced_seq(r, groups, size):
    return "".join("(" + _primitive(r, r.randint(0, size)) + ")" for _ in range(groups))


def _expr(r, n):
    """Random valid expression with digits, operators and parentheses."""
    def build(depth):
        if depth > 6 or r.random() < 0.3:
            return str(r.randint(0, 9))
        a, b = build(depth + 1), build(depth + 1)
        e = f"{a}{r.choice('+-*/')}{b}"
        return f"({e})" if r.random() < 0.6 else e
    out = build(0)
    while len(out) < n:
        out = f"({out}){r.choice('+-*/')}{build(0)}"
    return out


def _words_line(r, k):
    words = [rand_str(r, r.randint(1, 7)) for _ in range(k)]
    return "".join(w + " " * r.randint(1, 3) for w in words).rstrip()


PROBLEMS = [
    Problem(
        title="Largest Odd Number in String",
        difficulty="EASY",
        topics=["String", "Math"],
        description="""The string `num` holds the digits of a large non-negative integer. Find the largest-valued **odd** integer that is a non-empty contiguous substring of `num`, and print it exactly as it appears. If there is no odd substring, print `none`.

Hint: a number is odd when its last digit is odd, and keeping more of the prefix only makes it bigger.

**Input:** one line with `num` (digits only, no leading zeros unless it is `0`).

**Output:** the largest odd substring, or `none`.""",
        constraints=["1 <= |num| <= 10^5"],
        solve=_largest_odd,
        brute=_largest_odd_brute,
        examples=[("35427", "The whole number ends in 7, which is odd."), ("4206", "Every digit is even.")],
        tests=lambda r: ["0", "1", "2", "8", "10", "2468642", "1234567890", "9000"]
        + [rand_str(r, n, "123456789")[:1] + rand_str(r, n - 1, "0123456789") for n in (8, 15, 25)]
        + ["1" + "8" * 5000 + "3" + "2" * 3000],
    ),
    Problem(
        title="Remove Outermost Parentheses",
        difficulty="EASY",
        topics=["String", "Stack"],
        description="""A balanced parentheses string can be split into **primitive** parts: non-empty balanced pieces that can't be split any further. For example `(()())(())` splits into `(()())` and `(())`.

Remove the outermost pair of parentheses from every primitive part and print what's left. If nothing is left, print `none`.

Track the current depth: copy a character only when it isn't the opening or closing bracket at depth zero.

**Input:** one line with a balanced string of `(` and `)`.

**Output:** the string after removing each part's outer parentheses, or `none`.""",
        constraints=["2 <= |s| <= 10^5", "s is balanced"],
        solve=_outermost,
        brute=_outermost_brute,
        examples=[("(()())(())", "Parts (()()) and (()) become ()() and ()."), ("()()", "Each part is just (), which leaves nothing.")],
        tests=lambda r: ["()", "(())", "((()))", "()(())((()))", "(()(()))"]
        + [_balanced_seq(r, g, s) for g, s in ((3, 3), (5, 2), (8, 4))]
        + [_balanced_seq(r, 400, 8)],
    ),
    Problem(
        title="Reverse Words in a String",
        difficulty="MEDIUM",
        topics=["String", "Two Pointers"],
        description="""Reverse the order of the words in a line. A word is a run of non-space characters. Words may be separated by more than one space; print them separated by exactly **one** space.

**Input:** one line of words.

**Output:** the words in reverse order, separated by single spaces.""",
        constraints=["1 <= |s| <= 10^4", "s contains at least one word"],
        solve=_reverse_words,
        examples=[("the sky is blue", "Read the words from the end."), ("practice   makes  perfect", "Extra spaces between words collapse to one.")],
        tests=lambda r: ["hello", "a b", "one    two", "SprintCode is fun", "x y z 1 2 3"]
        + [_words_line(r, k) for k in (4, 9, 20)]
        + [_words_line(r, 1500)],
    ),
    Problem(
        title="Rotate String Check",
        difficulty="EASY",
        topics=["String"],
        description="""A **rotation** moves some characters from the front of a string to its back, so `abcde` can become `cdeab`. Rotating by zero is allowed. Print `true` if `goal` is a rotation of `s`, otherwise `false`.

Neat trick: every rotation of `s` appears inside `s + s`.

**Input:** `s` on the first line, `goal` on the second.

**Output:** `true` or `false`.""",
        constraints=["1 <= |s|, |goal| <= 10^4", "Lowercase letters only"],
        solve=_rotate,
        brute=_rotate_brute,
        examples=[("abcde\ncdeab", "Move \"ab\" to the end."), ("abcde\nabced", "No rotation swaps the last two letters.")],
        tests=lambda r: ["a\na", "a\nb", "ab\nba", "abc\nabcabc", "aaaa\naaaa", "abab\nbaba", "abc\nacb"]
        + [(lambda s, k: f"{s}\n{s[k:] + s[:k]}")(rand_str(r, n, "abc"), r.randrange(n)) for n in (10, 30)]
        + [f"{rand_str(r, 20, 'ab')}\n{rand_str(r, 20, 'ab')}"]
        + [(lambda s: f"{s}\n{s[2000:] + s[:2000]}")(rand_str(r, 4000))],
    ),
    Problem(
        title="Maximum Nesting Depth of Parentheses",
        difficulty="EASY",
        topics=["String", "Stack"],
        description="""You're given a valid expression made of digits, the operators `+ - * /` and parentheses. Its **nesting depth** is the largest number of parentheses that are open at the same time. Print the nesting depth (0 if there are no parentheses).

**Input:** one line with the expression.

**Output:** the maximum nesting depth.""",
        constraints=["1 <= |s| <= 10^4", "The parentheses are balanced"],
        solve=_nesting,
        examples=[("(1+(2*3)+((8)/4))+1", "The 8 sits inside three open parentheses."), ("1+2*3", "No parentheses at all.")],
        tests=lambda r: ["7", "(1)", "((((9))))", "(1)+(2)+(3)", "1+(2*(3-(4/5)))"]
        + [_expr(r, n) for n in (10, 30, 60)]
        + [_expr(r, 3000)],
    ),
    Problem(
        title="Roman to Integer",
        difficulty="EASY",
        topics=["String", "Hash Map", "Math"],
        description="""Convert a Roman numeral to an integer. The symbols are `I = 1`, `V = 5`, `X = 10`, `L = 50`, `C = 100`, `D = 500` and `M = 1000`. Symbols are normally written largest to smallest and added up, but a smaller symbol placed **before** a larger one is subtracted: `IV = 4`, `IX = 9`, `XL = 40`, `XC = 90`, `CD = 400`, `CM = 900`.

**Input:** one line with a valid Roman numeral.

**Output:** its value.""",
        constraints=["1 <= value <= 3999"],
        solve=_roman_to_int,
        brute=_roman_to_int_brute,
        examples=[("LVIII", "L + V + III = 50 + 5 + 3."), ("MCMXCIV", "M + CM + XC + IV = 1000 + 900 + 90 + 4 = 1994.")],
        tests=lambda r: ["I", "IV", "IX", "XL", "XC", "CD", "CM", "MMMCMXCIX", "MMXXVI"]
        + [_to_roman(r.randint(1, 3999)) for _ in range(4)],
    ),
    Problem(
        title="Integer to Roman",
        difficulty="MEDIUM",
        topics=["String", "Math"],
        description="""Convert an integer to its standard Roman numeral, using the symbols `I V X L C D M` and the subtractive pairs `IV IX XL XC CD CM`. Always use the shortest standard form (so 4 is `IV`, never `IIII`).

Go through the values from largest to smallest (including the six subtractive pairs) and take each one as many times as it fits.

**Input:** one integer `n`.

**Output:** `n` as a Roman numeral.""",
        constraints=["1 <= n <= 3999"],
        solve=_int_to_roman,
        examples=[("58", "50 + 5 + 3 → L + V + III."), ("1994", "1000 + 900 + 90 + 4 → M + CM + XC + IV.")],
        tests=lambda r: ["1", "3", "4", "9", "14", "40", "444", "999", "3999", "2026"] + [str(r.randint(1, 3999)) for _ in range(3)],
    ),
    Problem(
        title="Sort Characters by Frequency",
        difficulty="MEDIUM",
        topics=["String", "Hash Map", "Sorting"],
        description="""Rearrange the characters of a string so that more frequent characters come first, with all copies of the same character kept together. When two characters appear equally often, the one with the smaller character code (`ASCII` order) comes first.

**Input:** one line with the string (letters and digits, no spaces).

**Output:** the rearranged string.""",
        constraints=["1 <= |s| <= 5 * 10^4"],
        solve=_sort_freq,
        examples=[("tree", "e appears twice; r and t once each, r first."), ("Aabb", "b twice, then A before a (uppercase sorts first).")],
        tests=lambda r: ["a", "zzzz", "abc", "cccaaa", "112233", "Mississippi"]
        + [rand_str(r, n, alpha) for n, alpha in ((15, "abc"), (40, "aAbB01"), (80, "abcdefghij"))]
        + [rand_str(r, 6000, "abcdefghijklmnopqrstuvwxyzABC0123")],
    ),
    Problem(
        title="String to Integer",
        difficulty="MEDIUM",
        topics=["String"],
        description="""Parse an integer out of a line of text, following these rules exactly:

1. Skip any leading spaces.
2. An optional `+` or `-` sign may come next.
3. Read digits until the first non-digit character or the end of the line. Everything after that is ignored.
4. If no digits were read, the result is `0`.
5. Clamp the result to the 32-bit signed range `[-2147483648, 2147483647]`.

**Input:** one line of text.

**Output:** the parsed integer.""",
        constraints=["1 <= |s| <= 200", "s contains letters, digits, spaces, '+', '-' and '.'"],
        solve=_atoi,
        examples=[("-42", "A sign followed by digits."), ("4193 with words", "Reading stops at the space after 4193.")],
        tests=lambda r: ["0", "+1", "-0", "words and 987", "3.14159", "-91283472332", "91283472332", "2147483647", "-2147483648",
                         "2147483648", "+-12", "00000123abc", "-", "-5-"]
        + [rand_str(r, 12, "0123456789") + rand_str(r, 4, "ab .")],
    ),
    Problem(
        title="Count Palindromic Substrings",
        difficulty="MEDIUM",
        topics=["String", "Two Pointers"],
        description="""Count the substrings of `s` that read the same forwards and backwards. Substrings at different positions count separately, even if they're equal.

Every palindrome has a center: a single character (odd length) or the gap between two characters (even length). Expand outward from all `2n - 1` centers for `O(n²)` without extra memory.

**Input:** one line with a lowercase string.

**Output:** the number of palindromic substrings.""",
        constraints=["1 <= |s| <= 1000"],
        solve=_count_pal,
        brute=_count_pal_brute,
        examples=[("abc", "Only the three single letters."), ("aaa", "a, a, a, aa, aa and aaa.")],
        tests=lambda r: ["a", "ab", "aa", "aba", "abba", "racecar", "abcdcba"]
        + [rand_str(r, n, "ab") for n in (12, 25, 40)]
        + [rand_str(r, 1000, "abc")],
    ),
    Problem(
        title="Sum of Beauty of All Substrings",
        difficulty="MEDIUM",
        topics=["String", "Hash Map"],
        description="""The **beauty** of a string is the frequency of its most common character minus the frequency of its least common character (counting only characters that appear). For example, `aabcb` has beauty `2 - 1 = 1`.

Print the sum of the beauty of every substring of `s`.

Fix each start position and extend the end one character at a time, updating a 26-slot frequency table as you go.

**Input:** one line with a lowercase string.

**Output:** the total beauty.""",
        constraints=["1 <= |s| <= 500"],
        solve=_beauty,
        brute=_beauty_brute,
        examples=[("aabcb", "Substrings with non-zero beauty: aab, aabc, aabcb, abcb, bcb, each with beauty 1."), ("aaa", "One distinct letter means beauty 0 everywhere.")],
        tests=lambda r: ["a", "ab", "aab", "abcabc", "zzzaz"]
        + [rand_str(r, n, "abc") for n in (10, 20, 30)]
        + [rand_str(r, 300, "abcde")],
    ),
]
