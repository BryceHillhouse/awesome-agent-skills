---
name: check-readme
description: Lint README.md skill entries for format, duplicate links, and over-long descriptions. Use before committing changes to README.md or when asked to check or clean up the skill list.
---

# Check README entries

Run the checker from the repo root:

```bash
python3 .claude/skills/check-readme/scripts/check_readme.py            # all problems
python3 .claude/skills/check-readme/scripts/check_readme.py --diff     # only lines added since origin/main
```

It reports, by line number:

- **format**: a bullet that looks like an entry but does not match
  `- **[author/name](url)** - description`.
- **duplicate**: the same entry (name and URL) listed more than once.
- **long-description**: a description over 10 words (the CONTRIBUTING.md limit).

Many older entries predate the 10-word rule, so use `--diff` to judge a change
and fix only the lines you added. Exit code is 1 when the checked lines have problems.
