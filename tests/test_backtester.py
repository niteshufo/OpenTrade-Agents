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
