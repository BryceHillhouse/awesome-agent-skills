---
name: market-brief
description: Run the three-agent market workflow — news-scout and market-projections in parallel, then puts-strategist — for a watchlist of stocks and crypto, and produce a put-recommendations report. Use when asked for a market brief, news-driven put ideas, or to run the stock/crypto agents.
---

# Market brief

Three subagents in `.claude/agents/` produce one dated set of reports:

| Agent | Job | Output |
|---|---|---|
| `news-scout` | Market-moving news, graded by impact | `reports/<date>/news.md` |
| `market-projections` | Analyst targets, implied vol, technicals, crypto positioning | `reports/<date>/projections.md` |
| `puts-strategist` | Ranked put ideas from both reports | `reports/<date>/puts.md` |

## Steps

1. **Get the inputs.** You need a watchlist. If the user gave none, ask for one. Otherwise use what they gave. Also note any constraints they mention: account size, max risk per idea, holdings to hedge, horizon, lookback window (default 72h). Use today's date as `<date>` (YYYY-MM-DD) and create `reports/<date>/`.
2. **Research in parallel.** In a single message, start both `news-scout` and `market-projections` with the Agent tool. Give each the watchlist, today's date, and its output path.
3. **Check the research.** Once both are done, read both files. If either file is missing or mostly gaps, re-run that agent once with the gaps called out.
4. **Strategize.** Start `puts-strategist` with both report paths, the output path, and the user's constraints.
5. **Report back.** Show the user the summary table from `puts.md`, the top bearish news, and the paths to all three files. Keep the disclaimer.

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
