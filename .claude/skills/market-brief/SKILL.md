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
2. **Verified data (you, before any agent).** Subagents may not get the session's connectors: the scout agent reported no connector tools on its first run with them. So you fetch the hard facts yourself and write `reports/<date>/verified.md` for every agent to read. Use these tools:
   - **LunarCrush `topic`** for each asset: `$spy`, `$qqq`, `$nvda`, `$tsla`, `$aapl`, `$amzn`, `$ibit`, `$etha`, plus `cryptocurrencies` sorted by `market_cap` (limit 3) for BTC and ETH. Record price, 24h/7d/30d change, 1-year high and low, sentiment, and the critical theme. **Rate limit: 4 calls per minute, 100 per day.** Send at most 4 per batch and wait for the minute to reset if you hit the limit. Sanity-check each row: if a price move contradicts its underlying (for example ETHA vs. ETH) or its own market-cap change, mark it UNRELIABLE.
   - **USAFacts → FRED `getSeriesObservations`** (`sort_order: desc`, `limit: 3–5`) for `DGS10`, `DGS2`, `DFF` and `DCOILBRENTEU`. The VIX (`VIXCLS`) is license-restricted, so don't request it.
   - **USAFacts → web_gov `fetch`**:
     - `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` for FOMC dates.
     - `https://www.bls.gov/schedule/news_release/cpi.htm` and `https://www.bls.gov/schedule/news_release/empsit.htm` for CPI and jobs dates.

     Mark each date CONFIRMED, NOT LISTED, or CONTRADICTED.

   Tell Scout, Oracle and Bear to read `verified.md` first, treat it as verified, and not spend searches re-finding it.
3. **Scout (`scout`).** Start it with the watchlist, today's date, the lookback, and `reports/<date>/news.md`. When it returns, check that `news.md` ends with `## Hand-off to Oracle`. If the section is missing, send the agent back to add it.
4. **Oracle (`oracle`).** Start it with the watchlist, today's date, `reports/<date>/projections.md`, and the path to `news.md`. Check that the file has `## Answers to Scout` and `## Hand-off to Bear`.
5. **Bear (`bear`).** Start it with both report paths, `reports/<date>/puts.md`, and the user's constraints.
6. **One follow-up round (only if needed).** If `puts.md` lists open questions, group them by owner and send each owning agent its questions. Use SendMessage to the same agent if it is still available; otherwise start it fresh with the question IDs and its report path. Have it append a `## Follow-up answers` section to its own report. Then send Bear the answers and ask it to revise `puts.md` and mark what changed. Stop after one round; anything still unresolved stays listed as open.
7. **Report back.** Show the user the summary table from `puts.md`, the top bearish news, what the follow-up round changed (if one ran), and the paths to all three files. Keep the disclaimer.
8. **Update the live dashboard.** This is the Agent Factory page at https://claude.ai/artifact/7KVv6sSvCmmZZtrEePmWP7, and the step uses the `ArtifactData` tool with that `url`. Its database is the durable record: the `reports/` folder disappears with the container, so the scorecard lives here.
   - **At the start of the shift** (before step 3), `set` `runs/<date>-r<n>` with `{date, label: "Run <n>", status: "running", nextShift}`. Use `n` = 1 plus the number of runs already listed for that date.
   - **After Bear**, `update` that run document with the full shift:
     - `status: "complete"` (or `"failed"` with a `summary` saying what broke);
     - `riskUsed`, `riskCap`, `emailSent`;
     - `summary`: one sentence;
     - `supply`: `[{source, detail, state: "verified"|"rejected"}]` from `verified.md`;
     - `scout {searches, budget, requests, items:[{id, text, severity}], line}`;
     - `oracle {answered, total, items:[{text, state}], line}`;
     - `bear {ideas, line, candidates:[{asset, score, breakdown:{catalyst,timing,projections,positioning,data}, decision, reason}]}`.

     Each `line` is a two-sentence, in-character report from that agent. Every `text` stays under 45 characters.
   - **Scorecard: new rows.** For every candidate Bear scored, `set` `scorecard/<date>-<ASSET>` with `{date, asset, score, decision, entry, checkDate: date + 14 days, exit: null, source}`. `entry` is the verified price from `verified.md`.
   - **Scorecard: paper trades.** When Bear opens an idea, add `paper: {structure, strikes, expiry, cost, maxLoss, value, pnl}`. Price `value` with `put_math.py`: the `bs` estimate while open, intrinsic value at expiry. `pnl` = value − cost.
   - **Scorecard: grading.** `list` the scorecard and handle every row whose `exit` is null:
     - set `latest` from today's `verified.md` price for that asset;
     - when `checkDate` ≤ today, also set `exit` and `exitDate`.

     Pin every update with `if_version`, and batch the writes (up to 50 per call). Never change an `entry` once it's written.
9. **Email summary (when the user asked for one).** Write `reports/<date>/email.md` and send it.
   - **Recipient:** the address given in the request or in the scheduled run's prompt. Never commit a recipient address to the repo.
   - **Subject:** `Market brief <date> – <N> put ideas` (or `– no trades` when there are none).
   - **Body:** plain text that is readable on a phone, under 300 words, in this order:
     0. A link to the live dashboard: https://claude.ai/artifact/7KVv6sSvCmmZZtrEePmWP7
     1. **Top recommendations**: one line each with rank, underlying, structure, strikes, expiry, est. cost / max loss, breakeven, and score. Mark estimated premiums.
     2. **Top 3 bearish news items**: date, headline, and why it matters, one line each.
     3. **Key dates in the next 2 weeks.**
     4. **Watch-outs**: data gaps, estimates, overlap between ideas.
     5. The disclaimer, verbatim.
   - **Send** with whichever email tool this session has: a send tool from a connected mail connector, such as Resend or Gmail. If the connector can only create drafts, create a draft addressed to the recipient and say so. If no email tool is connected, say that the email wasn't sent and give the file path. Never report an email as sent unless the tool confirmed it.

## Put math helper

`scripts/put_math.py` computes payoffs and Black-Scholes estimates so the strategist does not do arithmetic by hand:

```bash
python3 .claude/skills/market-brief/scripts/put_math.py long-put --spot 182 --strike 175 --premium 4.10
python3 .claude/skills/market-brief/scripts/put_math.py put-spread --spot 182 --long-strike 175 --short-strike 160 --long-premium 4.10 --short-premium 1.05
python3 .claude/skills/market-brief/scripts/put_math.py bs --spot 182 --strike 175 --days 45 --iv 0.38
```

Add `--contracts N` and `--multiplier M` (default 100; use the venue's contract size for crypto, for example 1 for a 1-BTC Deribit option).

## Data connectors

Scout and Oracle use these claude.ai connectors when the session has them:

- **LunarCrush**: live stock, ETF and crypto prices, recent change, and social sentiment. No options data.
- **USAFacts Government Data**:
  - FRED series for rates and oil (`DGS10`, `DGS2`, `DFF`, `T10Y2Y`, `DCOILBRENTEU`);
  - `web_gov` for reading federalreserve.gov, bls.gov and sec.gov pages, which confirms FOMC, CPI and earnings dates even when direct fetches are blocked.

If a connector is missing, the agents fall back to web search. Option chains and implied volatility still come only from search, until an options data source (for example Deribit for crypto) is reachable.

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
