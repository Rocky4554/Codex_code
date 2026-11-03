"""Helpers for authoring catalog problems.

A topic module (topics/*.py) defines:

    PLAYLISTS = [Playlist(...), ...]   # one or more ordered playlists
    PROBLEMS  = [Problem(...), ...]    # new problems introduced by this module

Every expected output is produced by running the problem's reference
`solve` on the test input, so outputs are correct by construction.
Optional `brute` is cross-checked against `solve` on every test whose
input is small (see build.py).
"""
from __future__ import annotations

import random
import zlib
from dataclasses import dataclass, field
from typing import Callable, Iterable


@dataclass
class Problem:
    title: str
    difficulty: str                      # EASY | MEDIUM | HARD
    topics: list[str]
    description: str                     # markdown; must contain **Input:** and **Output:**
    solve: Callable[[str], str]          # stdin text -> stdout text
    examples: list[tuple[str, str]]      # (input, explanation) — shown on the page AND used as sample tests
    tests: Callable[[random.Random], Iterable[str]]  # hidden test inputs (edge cases + random)
    constraints: list[str] = field(default_factory=list)
    brute: Callable[[str], str] | None = None


@dataclass
class Playlist:
    key: str                             # stable id, e.g. "arrays"
    title: str
    description: str
    accent: str                          # hex color
    titles: list[str]                    # ordered: existing + new problem titles


def rng_for(title: str) -> random.Random:
    """Deterministic RNG per problem so regenerated tests are stable."""
    return random.Random(zlib.crc32(title.encode()))


# ── input helpers ────────────────────────────────────────────────

def lines(inp: str) -> list[str]:
    return [l.strip() for l in inp.strip("\n").split("\n")]


def ints(line: str) -> list[int]:
    return [int(x) for x in line.split()]


def join(xs) -> str:
    return " ".join(str(x) for x in xs)


def rand_ints(r: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return [r.randint(lo, hi) for _ in range(n)]


def rand_str(r: random.Random, n: int, alphabet: str = "abcdefghijklmnopqrstuvwxyz") -> str:
    return "".join(r.choice(alphabet) for _ in range(n))


def tree_line(values) -> str:
    """Level-order list with None → 'null', trailing nulls trimmed."""
    vals = list(values)
    while vals and vals[-1] is None:
        vals.pop()
    return " ".join("null" if v is None else str(v) for v in vals) or "null"


def parse_tree(line: str):
    """Level-order 'a b null c' → root TreeNode (or None)."""
    toks = line.split()
    if not toks or toks[0] == "null":
        return None
    root = TreeNode(int(toks[0]))
    q, i = [root], 1
    while q and i < len(toks):
        cur = q.pop(0)
        if i < len(toks) and toks[i] != "null":
            cur.left = TreeNode(int(toks[i])); q.append(cur.left)
        i += 1
        if i < len(toks) and toks[i] != "null":
            cur.right = TreeNode(int(toks[i])); q.append(cur.right)
        i += 1
    return root


def serialize_tree(root) -> str:
    out, q = [], [root]
    while q:
        n = q.pop(0)
        if n is None:
            out.append(None)
            continue
        out.append(n.val)
        q.append(n.left)
        q.append(n.right)
    return tree_line(out)


def random_tree(r: random.Random, n: int, lo: int = 1, hi: int = 99, bst: bool = False, distinct: bool = True):
    """Random binary tree with n nodes (BST when bst=True). Returns root."""
    if n == 0:
        return None
    vals = r.sample(range(lo, hi + 1), n) if distinct else [r.randint(lo, hi) for _ in range(n)]
    if bst:
        root = None
        for v in vals:
            root = _bst_insert(root, v)
        return root
    nodes = [TreeNode(v) for v in vals]
    for i in range(1, n):
        while True:
            p = nodes[r.randrange(i)]
            side = r.choice(("left", "right"))
            if getattr(p, side) is None:
                setattr(p, side, nodes[i])
                break
    return nodes[0]


def _bst_insert(root, v):
    if root is None:
        return TreeNode(v)
    if v < root.val:
        root.left = _bst_insert(root.left, v)
    else:
        root.right = _bst_insert(root.right, v)
    return root


class TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def boolstr(b: bool) -> str:
    return "true" if b else "false"
