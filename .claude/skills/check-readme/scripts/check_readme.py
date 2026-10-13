#!/usr/bin/env python3
"""Lint skill entries in README.md. See ../SKILL.md."""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ENTRY = re.compile(r"^- \*\*\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\*\* - (?P<desc>\S.*)$")
LOOSE = re.compile(r"^- \*\*\[")
MAX_WORDS = 10


def added_lines(readme):
    out = subprocess.run(
        ["git", "diff", "-U0", "origin/main", "--", str(readme)],
        capture_output=True, text=True, check=True,
    ).stdout
    lines, current = set(), 0
    for row in out.splitlines():
        hunk = re.match(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", row)
        if hunk:
            start, count = int(hunk.group(1)), int(hunk.group(2) or 1)
            lines.update(range(start, start + count))
    return lines


def main():
    readme = Path(__file__).resolve().parents[4] / "README.md"
    only = added_lines(readme) if "--diff" in sys.argv else None
    text = readme.read_text(encoding="utf-8").splitlines()

    problems, urls = [], defaultdict(list)
    for no, line in enumerate(text, 1):
        if not LOOSE.match(line):
            continue
        m = ENTRY.match(line)
        if not m:
            problems.append((no, "format", line))
            continue
        urls[(m.group("name"), m.group("url"))].append(no)
        if len(m.group("desc").split()) > MAX_WORDS:
            problems.append((no, "long-description", m.group("name")))
    for (name, url), nos in urls.items():
        for no in nos[1:]:
            problems.append((no, "duplicate", f"{name} {url} (first on line {nos[0]})"))

    if only is not None:
        problems = [p for p in problems if p[0] in only]
    for no, kind, detail in sorted(problems):
        print(f"README.md:{no}: {kind}: {detail}")
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
