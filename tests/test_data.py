"""Smoke check #2 + determinism for the data layer.

Covers:
    * ``generate_ohlcv`` produces N bars with the exact OHLCV columns and a
      DatetimeIndex,
    * the generator is seeded (same seed -> identical frame),
    * ``SyntheticDataSource.to_feed`` builds a ``bt.feeds.PandasData``, and
    * ``validate_ohlcv`` rejects a malformed frame.
"""

from __future__ import annotations

import backtrader as bt
import pandas as pd
import pytest

from qmtquant.data.feeds import validate_ohlcv
from qmtquant.data.sources.base import OHLCV_COLUMNS
from qmtquant.data.sources.synthetic import SyntheticDataSource, generate_ohlcv


def test_generate_ohlcv_shape_and_columns(synth_df: pd.DataFrame) -> None:
    """Default frame has 300 rows, OHLCV columns and a DatetimeIndex."""
    assert isinstance(synth_df, pd.DataFrame)
    assert len(synth_df) == 300
    # Columns are exactly the OHLCV set (order-independent membership check).
    assert set(synth_df.columns) == set(OHLCV_COLUMNS)
    assert isinstance(synth_df.index, pd.DatetimeIndex)


def test_generate_ohlcv_is_seeded() -> None:
    """Two calls with the same seed yield identical frames."""
    a = generate_ohlcv(n=120, seed=7)
    b = generate_ohlcv(n=120, seed=7)
    pd.testing.assert_frame_equal(a, b)

    # ...and a different seed yields a different frame.
    c = generate_ohlcv(n=120, seed=8)
    assert not a.equals(c)


def test_synthetic_source_to_feed(synth_source: SyntheticDataSource) -> None:
    """The source adapts its frame into a backtrader PandasData feed."""
    feed = synth_source.to_feed("SYNTH")
    assert isinstance(feed, bt.feeds.PandasData)


def test_validate_ohlcv_rejects_bad_frame() -> None:
    """A frame missing OHLCV columns / DatetimeIndex is rejected."""
    bad = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
    with pytest.raises(ValueError):
        validate_ohlcv(bad)
