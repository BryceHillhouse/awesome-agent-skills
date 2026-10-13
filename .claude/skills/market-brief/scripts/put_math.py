#!/usr/bin/env python3
"""Payoff and Black-Scholes helpers for put ideas. See ../SKILL.md."""
import argparse
import json
import math


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bs_put(spot, strike, days, iv, rate):
    t = days / 365
    if t <= 0 or iv <= 0:
        return {"premium": max(strike - spot, 0.0), "delta": -1.0 if spot < strike else 0.0}
    d1 = (math.log(spot / strike) + (rate + iv * iv / 2) * t) / (iv * math.sqrt(t))
    d2 = d1 - iv * math.sqrt(t)
    premium = strike * math.exp(-rate * t) * norm_cdf(-d2) - spot * norm_cdf(-d1)
    return {"premium": premium, "delta": norm_cdf(d1) - 1}


def long_put(a):
    scale = a.contracts * a.multiplier
    breakeven = a.strike - a.premium
    return {
        "structure": "long put",
        "cost": a.premium * scale,
        "max_loss": a.premium * scale,
        "max_gain": breakeven * scale,
        "breakeven": breakeven,
        "move_to_breakeven_pct": (breakeven / a.spot - 1) * 100,
    }


def put_spread(a):
    if a.short_strike >= a.long_strike:
        raise SystemExit("short strike must be below long strike for a put debit spread")
    scale = a.contracts * a.multiplier
    debit = a.long_premium - a.short_premium
    width = a.long_strike - a.short_strike
    breakeven = a.long_strike - debit
    return {
        "structure": "put debit spread",
        "cost": debit * scale,
        "max_loss": debit * scale,
        "max_gain": (width - debit) * scale,
        "reward_to_risk": (width - debit) / debit if debit > 0 else None,
        "breakeven": breakeven,
        "move_to_breakeven_pct": (breakeven / a.spot - 1) * 100,
    }


def bs(a):
    out = bs_put(a.spot, a.strike, a.days, a.iv, a.rate)
    scale = a.contracts * a.multiplier
    return {
        "structure": "black-scholes put estimate",
        "premium_per_unit": out["premium"],
        "cost": out["premium"] * scale,
        "delta": out["delta"],
        "note": "ESTIMATE - check the live chain",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--spot", type=float, required=True)
        sp.add_argument("--contracts", type=int, default=1)
        sp.add_argument("--multiplier", type=float, default=100)

    lp = sub.add_parser("long-put")
    common(lp)
    lp.add_argument("--strike", type=float, required=True)
    lp.add_argument("--premium", type=float, required=True)
    lp.set_defaults(fn=long_put)

    ps = sub.add_parser("put-spread")
    common(ps)
    ps.add_argument("--long-strike", type=float, required=True)
    ps.add_argument("--short-strike", type=float, required=True)
    ps.add_argument("--long-premium", type=float, required=True)
    ps.add_argument("--short-premium", type=float, required=True)
    ps.set_defaults(fn=put_spread)

    b = sub.add_parser("bs")
    common(b)
    b.add_argument("--strike", type=float, required=True)
    b.add_argument("--days", type=float, required=True)
    b.add_argument("--iv", type=float, required=True, help="annualized, e.g. 0.38 for 38%%")
    b.add_argument("--rate", type=float, default=0.04)
    b.set_defaults(fn=bs)

    a = p.parse_args()
    out = {k: round(v, 4) if isinstance(v, float) else v for k, v in a.fn(a).items()}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
