---
name: market-brief
description: Run the three-agent market relay — scout hands off to oracle, which hands off to bear — for a watchlist of stocks and crypto, and produce a put-recommendations report. Use when asked for a market brief, news-driven put ideas, or to run the stock/crypto agents.
---

# Market brief

Three named subagents (Scout, Oracle, Bear) in `.claude/agents/` run as a relay. Each one reads the previous agent's report, starting with its hand-off section, and leaves a hand-off for the next. The dated files in `reports/<date>/` are the shared record of what each agent told the next.

```
Scout ──"Hand-off to Oracle"──▶ Oracle ──"Hand-off to Bear"──▶ Bear
  ▲                               ▲                             │
  └──────── "Open questions" (one follow-up round) ─────────────┘
```

| Agent | Reads | Writes | Hands off |
|---|---|---|---|
| `scout` | the watchlist | `news.md` (news items `S1…`, catalyst calendar) | priority assets, data requests `N1…`, unconfirmed items |
| `oracle` | `news.md` | `projections.md` | answers to `N1…`, bearish candidates table, conflicts, unknowns |
| `bear` | both reports | `puts.md` | ranked put ideas, open questions `Q1…` |

**Who owns what:** Scout owns news and every date. Oracle owns the numbers. Bear owns scoring (a fixed 0–10 rubric; only scores of 6 or more become ideas) and the trades. Scout and Oracle run on a faster model with per-asset search budgets, and skip any host that fails once. Bear runs on the session's model.

The agents can't message or start each other. Only you (the main session) start them, so you carry each hand-off forward by passing file paths.

## Steps

1. **Get the inputs.** You need a watchlist. If the user gave none, ask for one. Otherwise use what they gave. Also note any constraints they mention: account size, max risk per idea, holdings to hedge, horizon, lookback window (default 72h). Use today's date as `<date>` (YYYY-MM-DD) and create `reports/<date>/`.
2. **Scout (`scout`).** Start it with the watchlist, today's date, the lookback, and `reports/<date>/news.md`. When it returns, check that `news.md` ends with `## Hand-off to Oracle`. If the section is missing, send the agent back to add it.
3. **Oracle (`oracle`).** Start it with the watchlist, today's date, `reports/<date>/projections.md`, and the path to `news.md`. Check that the file has `## Answers to Scout` and `## Hand-off to Bear`.
4. **Bear (`bear`).** Start it with both report paths, `reports/<date>/puts.md`, and the user's constraints.
5. **One follow-up round (only if needed).** If `puts.md` lists open questions, group them by owner and send each owning agent its questions. Use SendMessage to the same agent if it is still available; otherwise start it fresh with the question IDs and its report path. Have it append a `## Follow-up answers` section to its own report. Then send Bear the answers and ask it to revise `puts.md` and mark what changed. Stop after one round; anything still unresolved stays listed as open.
6. **Report back.** Show the user the summary table from `puts.md`, the top bearish news, what the follow-up round changed (if one ran), and the paths to all three files. Keep the disclaimer.

## Put math helper

`scripts/put_math.py` computes payoffs and Black-Scholes estimates so the strategist does not do arithmetic by hand:

```bash
python3 .claude/skills/market-brief/scripts/put_math.py long-put --spot 182 --strike 175 --premium 4.10
python3 .claude/skills/market-brief/scripts/put_math.py put-spread --spot 182 --long-strike 175 --short-strike 160 --long-premium 4.10 --short-premium 1.05
python3 .claude/skills/market-brief/scripts/put_math.py bs --spot 182 --strike 175 --days 45 --iv 0.38
```

Add `--contracts N` and `--multiplier M` (default 100; use the venue's contract size for crypto, for example 1 for a 1-BTC Deribit option).

## Network access (cloud sessions)

In a Claude Code cloud environment, the agents can only open pages on hosts that the environment's **Network access** setting allows. Otherwise WebFetch fails with DNS errors, and the agents fall back to search-result summaries. Add these under **Allowed domains** (environment menu in the session title bar → Edit), and leave **Allow package managers** ticked:

```
finance.yahoo.com
cnbc.com
sec.gov
federalreserve.gov
deribit.com
```

Some sites serve from `www.` or other subdomains (`www.cnbc.com`, `www.sec.gov`, `www.federalreserve.gov`, `www.deribit.com`). If those still fail after the change, add the `www.` form too.
