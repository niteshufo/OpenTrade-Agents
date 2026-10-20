import pandas as pd

from app.agents.momentum import generate_signals


def run_backtest(
    candles: pd.DataFrame,
    initial_balance: float = 10_000.0,
    fee_rate: float = 0.001,
    fast_window: int = 10,
    slow_window: int = 30,
) -> dict:
    """Run a long-only moving-average crossover backtest.

    Signals formed at candle close are executed at the next candle close.
    One position at a time; no leverage or short selling.
    Open positions are marked to market at the final candle.
    """
    if initial_balance <= 0:
        raise ValueError("initial_balance must be positive.")
    if not 0 <= fee_rate < 1:
        raise ValueError("fee_rate must be between 0 and 1.")
    if "close" not in candles.columns or candles.empty:
        raise ValueError("Candles must be non-empty and contain 'close'.")

    data = generate_signals(candles, fast_window, slow_window).copy()
    close = pd.to_numeric(data["close"], errors="raise")

    if close.isna().any() or (close <= 0).any():
        raise ValueError("Close prices must be positive and non-null.")

    cash = float(initial_balance)
    quantity = 0.0
    entry_price = None
    entry_fee = 0.0
    realized_pnl = 0.0
    trades = []
    equity_values = []

    for i in range(len(data)):
        price = float(close.iloc[i])

        # Execute the previous candle's signal at this candle's close.
        if i > 0:
            signal = data["signal"].iloc[i - 1]

            if signal == "BUY" and quantity == 0:
                quantity = cash / (price * (1 + fee_rate))
                cost = quantity * price
                entry_fee = cost * fee_rate
                cash -= cost + entry_fee
                entry_price = price

                trades.append({
                    "side": "BUY",
                    "price": price,
                    "quantity": quantity,
                    "fee": entry_fee,
                })

            elif signal == "SELL" and quantity > 0:
                proceeds = quantity * price
                exit_fee = proceeds * fee_rate
                trade_pnl = (
                    (price - entry_price) * quantity
                    - entry_fee
                    - exit_fee
                )
                cash += proceeds - exit_fee
                realized_pnl += trade_pnl

                trades.append({
                    "side": "SELL",
                    "price": price,
                    "quantity": quantity,
                    "fee": exit_fee,
                    "entry_price": entry_price,
                    "net_pnl": trade_pnl,
                })

                quantity = 0.0
                entry_price = None
                entry_fee = 0.0

        equity_values.append(cash + quantity * price)

    equity = pd.Series(equity_values, dtype=float)
    final_price = float(close.iloc[-1])
    final_equity = float(equity.iloc[-1])
    unrealized_pnl = 0.0

    if quantity > 0:
        unrealized_pnl = (
            (final_price - entry_price) * quantity - entry_fee
        )

    peak = equity.cummax()
    drawdown = equity / peak - 1.0
    completed = [trade for trade in trades if trade["side"] == "SELL"]
    wins = sum(1 for trade in completed if trade["net_pnl"] > 0)

    return {
        "initial_balance": float(initial_balance),
        "final_equity": final_equity,
        "net_return_pct": (final_equity / initial_balance - 1) * 100,
        "max_drawdown_pct": float(drawdown.min() * 100),
        "realized_pnl": float(realized_pnl),
        "unrealized_pnl": float(unrealized_pnl),
        "completed_trades": len(completed),
        "winning_trades": wins,
        "win_rate_pct": wins / len(completed) * 100 if completed else 0.0,
        "open_position": quantity > 0,
        "open_quantity": float(quantity),
        "trades": trades,
        "equity_curve": equity.tolist(),
    }
