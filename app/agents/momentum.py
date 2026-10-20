from typing import Literal

import pandas as pd


Signal = Literal["BUY", "SELL", "HOLD"]


def generate_signals(
    candles: pd.DataFrame,
    fast_window: int = 10,
    slow_window: int = 30,
) -> pd.DataFrame:
    """Generate moving-average crossover signals from OHLCV candles.

    Required column: close.
    BUY when fast SMA crosses above slow SMA.
    SELL when fast SMA crosses below slow SMA.
    Otherwise HOLD.
    """
    if fast_window < 1 or slow_window < 1:
        raise ValueError("Moving-average windows must be positive integers.")

    if fast_window >= slow_window:
        raise ValueError("fast_window must be smaller than slow_window.")

    if "close" not in candles.columns:
        raise ValueError("Candles must contain a 'close' column.")

    if candles.empty:
        raise ValueError("Candles cannot be empty.")

    close = pd.to_numeric(candles["close"], errors="raise")

    if close.isna().any() or not close.map(lambda value: value == value).all():
        raise ValueError("Close prices must not contain missing values.")

    if (close <= 0).any():
        raise ValueError("Close prices must be positive.")

    result = candles.copy()
    result["fast_sma"] = close.rolling(
        window=fast_window,
        min_periods=fast_window,
    ).mean()
    result["slow_sma"] = close.rolling(
        window=slow_window,
        min_periods=slow_window,
    ).mean()

    previous_fast = result["fast_sma"].shift(1)
    previous_slow = result["slow_sma"].shift(1)

    crossed_up = (
        (result["fast_sma"] > result["slow_sma"])
        & (previous_fast <= previous_slow)
    )
    crossed_down = (
        (result["fast_sma"] < result["slow_sma"])
        & (previous_fast >= previous_slow)
    )

    result["signal"] = "HOLD"
    result.loc[crossed_up, "signal"] = "BUY"
    result.loc[crossed_down, "signal"] = "SELL"

    # Ignore signals until both moving averages are available.
    unavailable = result["slow_sma"].isna()
    result.loc[unavailable, "signal"] = "HOLD"

    return result
