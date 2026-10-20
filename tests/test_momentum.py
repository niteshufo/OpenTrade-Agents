import pandas as pd
import pytest

from app.agents.momentum import generate_signals


def test_strategy_returns_expected_columns():
    candles = pd.DataFrame({"close": list(range(1, 41))})

    result = generate_signals(candles, fast_window=3, slow_window=5)

    assert "fast_sma" in result.columns
    assert "slow_sma" in result.columns
    assert "signal" in result.columns
    assert result.iloc[-1]["signal"] == "HOLD"


def test_strategy_rejects_invalid_windows():
    candles = pd.DataFrame({"close": list(range(1, 11))})

    with pytest.raises(ValueError):
        generate_signals(candles, fast_window=5, slow_window=3)


def test_strategy_rejects_missing_close_column():
    candles = pd.DataFrame({"volume": [100, 200, 300]})

    with pytest.raises(ValueError):
        generate_signals(candles)


def test_strategy_rejects_non_positive_prices():
    candles = pd.DataFrame({"close": [10, 11, 0, 12]})

    with pytest.raises(ValueError):
        generate_signals(candles)
