---
name: add-skill-entry
description: Add a new skill link to README.md following CONTRIBUTING.md. Use when asked to add, list, or submit an agent skill or skill repository to this awesome list.
---

# Add a skill entry

This repo curates links only. Each skill lives in its own repository; never copy skill content into this repo.

## Steps

1. **Collect the details**: GitHub URL, author or org, skill name, and what it does.
2. **Check it is not already listed**: `grep -in "<owner>/<repo>" README.md`. If it is, stop and say where.
3. **Check it meets the bar in CONTRIBUTING.md**:
   - Public repository with a working skill and a README or SKILL.md.
   - Real community usage. Decline brand-new or unused repos and say why.
4. **Write the entry** in this exact format:

   ```markdown
   - **[author/skill-name](https://github.com/author/repo/path)** - Short description of what it does
   ```

   - The name must carry the author or org prefix.
   - The description must be 10 words or fewer, with no trailing period.
5. **Pick the section**:
   - If the author's team has its own "Skills by ..." section, append to the end of it.
   - Otherwise append to the end of the best-fitting subsection under "Community Skills"
     (Marketing, Productivity and Collaboration, Development and Testing,
     Context Engineering, Specialized Domains, n8n Automation, and so on).
   - Keep the blank line before each `</details>`.
6. **Validate**: run `python3 .claude/skills/check-readme/scripts/check_readme.py` and fix anything it reports for your new lines.
7. **Commit** with the title `Add skill: author/skill-name`.
