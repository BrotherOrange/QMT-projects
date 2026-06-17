"""Data layer: synthetic generator determinism, OHLCV validation, and ReplayFeed."""

from __future__ import annotations

import pandas as pd
import pytest

from qmtquant.data.sources.base import OHLCV_COLUMNS, validate_ohlcv
from qmtquant.data.sources.synthetic import SyntheticDataSource, generate_ohlcv
from qmtquant.runtime.feed import Bar, ReplayFeed


def test_generate_ohlcv_shape_and_columns(synth_df: pd.DataFrame) -> None:
    """Default frame has 300 rows, OHLCV columns and a DatetimeIndex."""
    assert isinstance(synth_df, pd.DataFrame)
    assert len(synth_df) == 300
    assert set(synth_df.columns) == set(OHLCV_COLUMNS)
    assert isinstance(synth_df.index, pd.DatetimeIndex)


def test_generate_ohlcv_is_seeded() -> None:
    """Two calls with the same seed yield identical frames; different seed differs."""
    a = generate_ohlcv(n=120, seed=7)
    b = generate_ohlcv(n=120, seed=7)
    pd.testing.assert_frame_equal(a, b)
    c = generate_ohlcv(n=120, seed=8)
    assert not a.equals(c)


def test_validate_ohlcv_rejects_bad_frame() -> None:
    """A frame missing OHLCV columns / DatetimeIndex is rejected."""
    bad = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
    with pytest.raises(ValueError):
        validate_ohlcv(bad)


def test_replayfeed_yields_bars_with_limits(synth_source: SyntheticDataSource) -> None:
    """ReplayFeed yields one Bar per row; first bar has no price limits, later ones do."""
    df = synth_source.get_dataframe("SYNTH")
    bars = list(ReplayFeed(df, "SYNTH", limit_pct=0.10))

    assert len(bars) == len(df)
    assert all(isinstance(b, Bar) and b.symbol == "SYNTH" for b in bars)

    # 首根无前收 → 无涨跌停；其后按前收 ±10% 估算
    assert bars[0].up_limit is None and bars[0].down_limit is None
    prev_close = bars[0].close
    assert bars[1].up_limit == round(prev_close * 1.10, 2)
    assert bars[1].down_limit == round(prev_close * 0.90, 2)
