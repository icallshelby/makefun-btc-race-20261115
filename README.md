# Washout-Recovery BTC Bot — btc-race-24h-20261115-0828

[![make.fun](https://img.shields.io/badge/make.fun-btc--race--24h--20261115--0828-blue)](https://make.fun/bounty/btc-race-24h-20261115-0828)
[![Strategy](https://img.shields.io/badge/strategy-washout--recovery-green)](./main.py)
[![Dev PnL](https://img.shields.io/badge/dev%20PnL-%2B%241.50-brightgreen)](./SHIP-READY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Ultra-selective washout-recovery trading bot for the make.fun competition
**"Race a BTC trading bot live for 24 hours"** (`btc-race-24h-20261115-0828`,
$250 top 10). Trades Coinbase Wrapped BTC (cbBTC/USD) on 1-minute bars from
the Orca Whirlpool on Solana. Simulation only — no real money is traded.

## Strategy

Capitulation / washout mean-reversion, in the family of the previous race
instance's top finishers, with its own thresholds and confirmation:

- **Lookback:** 90 bars trailing return
- **Entry:** trailing return between **-300 bps and -120 bps** (confirmed washout dip)
- **Take profit:** +110 bps · **Max hold:** 120 bars · **Trailing stop:** 20 bps from peak PnL
- **Cooldown:** 20 bars · **Reset:** -10 bps · **End guard:** no entries in the final 120 bars
- **Size:** 100% of cash per entry, 2–4 trades per 24 h expected

## Verified backtests (fees 4 bps + slippage 2 bps included)

| Window | Net PnL | Trades | Max drawdown |
|---|---|---|---|
| NEW dev window (20261115-0828, graded) | **+$1.504604** | 6 | -2.34% |
| OLD dev window (20261113-2314, hold-out) | **+$5.941248** | 6 | -0.53% |

Both windows positive, max drawdown well under the 25% race limit.
End-to-end driver run (real bot subprocess) reproduces both PnLs to the cent.

## Entry point

`main.py` (Python 3.13, stdlib only) with the vendored SDK in
`vendor/makefun_bars.py`. Deterministic: no network, no wall clock, no files
outside the repository; two runs on the same data produce identical orders.

## License

MIT — see [LICENSE](./LICENSE).
