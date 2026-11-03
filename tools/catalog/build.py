#!/usr/bin/env python3
"""Build the DSA sheet catalog from topics/*.py.

    python3 tools/catalog/build.py                 # validate everything and write the JSON files
    python3 tools/catalog/build.py --check         # validate only (no writes)
    python3 tools/catalog/build.py --only arrays   # validate one topic module (implies --check)

Writes:
    src/main/resources/catalog/dsa-sheet-problems.json   problems + examples + test cases
    src/main/resources/catalog/playlists.json            featured playlists (DSA path + kept ones)
"""
from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG = ROOT / "src/main/resources/catalog"
sys.path.insert(0, str(HERE))

from lib import Playlist, Problem, rng_for  # noqa: E402

MAX_INPUT = 30_000          # bytes per test input
MAX_TOTAL = 150_000         # bytes of input per problem
MAX_TESTS = 20
MIN_HIDDEN = 5
BRUTE_LIMIT = 400           # cross-check brute on inputs up to this many chars
SLOW_SECONDS = 2.0
# Featured playlists that aren't part of the DSA path and are kept as-is.
KEEP_PLAYLISTS = {"Top Coding Interview Questions", "SQL Interview Questions", "SQL Joins & Self Joins", "SQL Aggregation & Window Functions"}
# Order of topic modules in the DSA path.
PATH_ORDER = ["basics", "sorting", "arrays", "hashing", "binarysearch", "strings", "recursion", "linkedlist",
              "bits", "greedy", "slidingwindow", "stackqueue", "trees", "bst", "heaps", "graphs", "dp", "tries"]


def norm(out: str) -> str:
    """Match the judge: strip trailing whitespace per line and trailing blank lines."""
    return "\n".join(l.rstrip() for l in str(out).replace("\r", "").split("\n")).strip("\n").strip()


def load_modules(only: str | None):
    names = sorted(m.name for m in pkgutil.iter_modules([str(HERE / "topics")]))
    if only:
        names = [n for n in names if n == only]
        if not names:
            sys.exit(f"no topics/{only}.py")
    return {n: importlib.import_module(f"topics.{n}") for n in names}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()
    write = not (args.check or args.only)

    existing = json.loads((HERE / "existing_problems.json").read_text())
    existing_titles = {p["title"].lower(): p["title"] for p in existing}
    errors: list[str] = []
    warn: list[str] = []
    modules = load_modules(args.only)

    problems: list[tuple[str, Problem]] = []
    playlists: list[tuple[str, Playlist]] = []
    for name, mod in modules.items():
        for p in getattr(mod, "PROBLEMS", []):
            problems.append((name, p))
        for pl in getattr(mod, "PLAYLISTS", []):
            playlists.append((name, pl))

    seen: dict[str, str] = {}
    out_problems = []
    for mod, p in problems:
        where = f"{mod}: {p.title!r}"
        key = p.title.lower()
        if key in existing_titles:
            errors.append(f"{where} already exists in the live catalog — reuse it in a playlist instead of redefining it")
        if key in seen:
            errors.append(f"{where} duplicates a title from {seen[key]}")
        seen[key] = mod
        if p.difficulty not in ("EASY", "MEDIUM", "HARD"):
            errors.append(f"{where} bad difficulty {p.difficulty}")
        if "**Input:**" not in p.description or "**Output:**" not in p.description:
            errors.append(f"{where} description needs **Input:** and **Output:** sections")
        if not p.examples:
            errors.append(f"{where} needs at least one example")

        r = rng_for(p.title)
        try:
            hidden = [t for t in p.tests(r)]
        except Exception as e:  # noqa: BLE001
            errors.append(f"{where} tests() raised {e!r}")
            continue
        sample_inputs = [norm(i) for i, _ in p.examples]
        hidden_inputs = []
        for t in hidden:
            t = norm(t)
            if t and t not in sample_inputs and t not in hidden_inputs:
                hidden_inputs.append(t)
        if len(hidden_inputs) < MIN_HIDDEN:
            errors.append(f"{where} has {len(hidden_inputs)} distinct hidden tests (need ≥ {MIN_HIDDEN})")
        all_inputs = sample_inputs + hidden_inputs
        if len(all_inputs) > MAX_TESTS:
            warn.append(f"{where} {len(all_inputs)} tests, keeping first {MAX_TESTS}")
            all_inputs = all_inputs[:MAX_TESTS]
        total = sum(len(i) for i in all_inputs)
        big = [len(i) for i in all_inputs if len(i) > MAX_INPUT]
        if big:
            errors.append(f"{where} test input too large ({max(big)} bytes > {MAX_INPUT})")
        if total > MAX_TOTAL:
            errors.append(f"{where} total test input {total} bytes > {MAX_TOTAL}")

        outputs = []
        for i, inp in enumerate(all_inputs):
            t0 = time.perf_counter()
            try:
                got = norm(p.solve(inp))
            except Exception as e:  # noqa: BLE001
                errors.append(f"{where} solve() raised on test {i}: {e!r}\n      input: {inp[:120]!r}")
                got = None
            dt = time.perf_counter() - t0
            if dt > SLOW_SECONDS:
                warn.append(f"{where} solve() took {dt:.1f}s on test {i}")
            if got == "":
                warn.append(f"{where} empty output on test {i}")
            if got is not None and p.brute and len(inp) <= BRUTE_LIMIT:
                try:
                    b = norm(p.brute(inp))
                except Exception as e:  # noqa: BLE001
                    errors.append(f"{where} brute() raised on test {i}: {e!r}")
                    b = got
                if b != got:
                    errors.append(f"{where} solve/brute disagree on test {i}\n      input: {inp[:160]!r}\n      solve: {got[:120]!r}\n      brute: {b[:120]!r}")
            outputs.append(got)

        if any(o is None for o in outputs):
            continue
        n_samples = len(sample_inputs)
        out_problems.append({
            "title": p.title,
            "difficulty": p.difficulty,
            "description": p.description.strip(),
            "topics": p.topics,
            "constraints": p.constraints,
            "examples": [
                {"input": sample_inputs[k], "output": outputs[k], "explanation": p.examples[k][1]}
                for k in range(n_samples)
            ],
            "testCases": [
                {"input": all_inputs[k], "expectedOutput": outputs[k], "sample": k < n_samples}
                for k in range(len(all_inputs))
            ],
            "_module": mod,
        })

    known = set(existing_titles) | set(seen)
    placed = set()
    for mod, pl in playlists:
        for t in pl.titles:
            if t.lower() not in known:
                errors.append(f"{mod}: playlist {pl.title!r} references unknown problem {t!r}")
            placed.add(t.lower())
        if len(set(t.lower() for t in pl.titles)) != len(pl.titles):
            errors.append(f"{mod}: playlist {pl.title!r} lists a problem twice")
    for mod, p in problems:
        if p.title.lower() not in placed:
            errors.append(f"{mod}: {p.title!r} isn't in any playlist")

    by_mod: dict[str, int] = {}
    for p in out_problems:
        by_mod[p["_module"]] = by_mod.get(p["_module"], 0) + 1
    for name in modules:
        pls = [pl for m, pl in playlists if m == name]
        print(f"  {name:<14} {by_mod.get(name, 0):>3} new problems · " + ", ".join(f"{pl.title} ({len(pl.titles)})" for pl in pls))
    for w in warn:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(out_problems)} problems built, {len(errors)} error(s), {len(warn)} warning(s).")
    if errors:
        sys.exit(1)

    if write:
        for p in out_problems:
            p.pop("_module")
        (CATALOG / "dsa-sheet-problems.json").write_text(json.dumps(out_problems, indent=1, ensure_ascii=False) + "\n")
        order = {k: i for i, k in enumerate(PATH_ORDER)}
        path = sorted((pl for _, pl in playlists), key=lambda pl: order.get(pl.key, 99))
        current = json.loads((CATALOG / "playlists.json").read_text())
        kept = [p for p in current if p["title"] in KEEP_PLAYLISTS]
        top = [p for p in kept if not p["title"].startswith("SQL")]
        sql = [p for p in kept if p["title"].startswith("SQL")]
        generated = [
            {"title": pl.title, "accentColor": pl.accent, "description": pl.description, "titles": pl.titles}
            for pl in path
        ]
        (CATALOG / "playlists.json").write_text(json.dumps(top + generated + sql, indent=1, ensure_ascii=False) + "\n")
        print(f"Wrote {len(out_problems)} problems and {len(top) + len(generated) + len(sql)} playlists.")


if __name__ == "__main__":
    main()
