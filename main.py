"""BTC Race Entry: Washout Recovery Bot (btc-race-24h-20261115).

Strategy Overview:
- Ultra-selective washout-recovery mean-reversion bot for CBBTC/USD 1-min bars on Orca Whirlpool.
- Lookback = 90 bars; enters when trailing return is between -300 bps and -120 bps (confirmed washout/capitulation dip).
- Exits on +110 bps take-profit, 120-batch max hold, or a 20 bps trailing stop from the position's peak PnL.
- Includes a reset threshold (-10 bps) and an end guard (no entries in the last 120 bars of the 1,440-bar window).
- Fully deterministic, stdlib only, zero network, zero wall clock.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

LOOKBACK = 90
DIP_LO_BPS = -300
DIP_HI_BPS = -120
WARMUP_BARS = 120
SIZE_BPS = 10000
TAKE_PROFIT_BPS = 110
MAX_HOLD_BATCHES = 120
TRAIL_BPS = 20
COOLDOWN_BATCHES = 20
RESET_BPS = -10
END_GUARD_BARS = 120
MAX_SLIPPAGE_BPS = 100


class WashoutBot:
    def __init__(self, symbol):
        self.symbol = symbol
        self.closes = []
        self.entry_seq = None
        self.cooldown = 0
        self.locked = False
        self.peak = 0.0

    def on_batch(self, state, batch):
        try:
            bar = None
            for b in batch["bars"]:
                if b["symbol"] == self.symbol:
                    bar = b
                    break
            if bar is None:
                return []
            c = int(bar["c"])
            # Guard against invalid/non-positive close prices
            if c <= 0:
                return []
            self.closes.append(c)
            if self.cooldown > 0:
                self.cooldown -= 1
            if len(self.closes) <= LOOKBACK:
                return []

            trailing = (self.closes[-1] / self.closes[-1 - LOOKBACK] - 1) * 10000
            if trailing > RESET_BPS:
                self.locked = False

            holding = state.positions.get(self.symbol)
            if holding and holding.qty > 0:
                val = state.value(self.symbol, holding.qty)
                pnl_ratio = (val / holding.cost - 1) if holding.cost > 0 else 0.0
                pnl_bps = pnl_ratio * 10000
                self.peak = max(self.peak, pnl_ratio)
                held_batches = state.seq - self.entry_seq if self.entry_seq is not None else 0

                if (
                    pnl_bps >= TAKE_PROFIT_BPS
                    or held_batches >= MAX_HOLD_BATCHES
                    or (self.peak > 0 and (self.peak - pnl_ratio) * 10000 >= TRAIL_BPS)
                ):
                    self.cooldown = COOLDOWN_BATCHES
                    self.entry_seq = None
                    self.peak = 0.0
                    return [{
                        "side": "sell",
                        "symbol": self.symbol,
                        "qty": holding.qty,
                        "max_slippage_bps": MAX_SLIPPAGE_BPS,
                    }]
                return []

            if self.cooldown > 0 or self.locked:
                return []
            if len(self.closes) <= WARMUP_BARS:
                return []
            if state.seq > 1440 - END_GUARD_BARS:
                return []
            if not (DIP_LO_BPS <= trailing <= DIP_HI_BPS):
                return []

            notional = state.cash * SIZE_BPS // 10000
            min_notional = int(state.hello["fees"]["min_notional_quote_units"])
            if notional < min_notional:
                return []

            self.locked = True
            self.entry_seq = state.seq
            self.peak = 0.0
            return [{
                "side": "buy",
                "symbol": self.symbol,
                "notional_quote_units": notional,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]
        except Exception:
            return []


def main():
    bot = WashoutBot("CBBTC")
    makefun_bars.run(bot.on_batch)


if __name__ == "__main__":
    main()
