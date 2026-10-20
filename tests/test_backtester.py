import pandas as pd
import pytest

from app.services.backtester import run_backtest


def test_backtest_returns_metrics():
    candles = pd.DataFrame({
        "close": (
            list(range(150, 99, -1))
            + list(range(100, 151))
            + list(range(150, 99, -1))
        )
    })

    result = run_backtest(
        candles,
        initial_balance=10_000,
        fee_rate=0.001,
        fast_window=3,
        slow_window=5,
    )

    assert result["initial_balance"] == 10_000
    assert isinstance(result["final_equity"], float)
    assert "net_return_pct" in result
    assert "max_drawdown_pct" in result
    assert result["completed_trades"] >= 1

def test_backtest_rejects_invalid_balance():
    candles = pd.DataFrame({"close": [100, 101, 102]})

    with pytest.raises(ValueError):
        run_backtest(candles, initial_balance=0)


def test_backtest_rejects_invalid_fee():
    candles = pd.DataFrame({"close": [100, 101, 102]})

    with pytest.raises(ValueError):
        run_backtest(candles, fee_rate=1)


def test_backtest_rejects_empty_data():
    candles = pd.DataFrame({"close": []})

    with pytest.raises(ValueError):
        run_backtest(candles)

def test_backtest_returns_equity_curve_for_each_candle():
    candles = pd.DataFrame({"close": [100, 101, 102, 103, 104]})

    result = run_backtest(
        candles,
        initial_balance=10_000,
        fast_window=2,
        slow_window=3,
    )

    assert len(result["equity_curve"]) == len(candles)
    assert all(isinstance(value, float) for value in result["equity_curve"])


def test_backtest_reports_open_position_pnl():
    candles = pd.DataFrame({
        "close": (
            list(range(110, 99, -1))
            + list(range(100, 111))
        )
    })

    result = run_backtest(
        candles,
        initial_balance=10_000,
        fee_rate=0.001,
        fast_window=2,
        slow_window=3,
    )

    assert result["open_position"] is True
    assert result["unrealized_pnl"] > 0
    assert result["open_quantity"] > 0


def test_backtest_includes_fees_in_completed_trade_pnl():
    candles = pd.DataFrame({
        "close": (
            list(range(110, 99, -1))
            + list(range(100, 111))
            + list(range(110, 94, -1))
        )
    })

    result = run_backtest(
        candles,
        initial_balance=10_000,
        fee_rate=0.001,
        fast_window=2,
        slow_window=3,
    )

    sell_trades = [
        trade for trade in result["trades"]
        if trade["side"] == "SELL"
    ]

    assert sell_trades
    for trade in sell_trades:
        expected_pnl = (
            (trade["price"] - trade["entry_price"]) * trade["quantity"]
            - trade["fee"]
            - trade["entry_price"] * trade["quantity"] * 0.001
        )
        assert trade["net_pnl"] == pytest.approx(expected_pnl)
