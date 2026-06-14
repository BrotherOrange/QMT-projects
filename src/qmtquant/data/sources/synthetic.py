"""Seeded synthetic OHLCV generator.

Migrated from the old ``make_data()`` smoke-test helper. Provides:

* :func:`generate_ohlcv` -- a pure, deterministic function for tests and quick
  experiments.
* :class:`SyntheticDataSource` -- a :class:`~qmtquant.data.sources.base.DataSource`
  wrapper so the engine can consume synthetic bars exactly like any real source.

Determinism comes from :func:`numpy.random.default_rng` seeded with ``seed``.
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from .base import DataSource, OHLCV_COLUMNS


def generate_ohlcv(
    n: int = 300,
    seed: int = 42,
    *,
    start: str = "2022-01-01",
    start_price: float = 100.0,
    freq: str = "B",
) -> pd.DataFrame:
    """Generate a deterministic trend+noise OHLCV frame.

    The close price is a small upward random walk (drift ``0.05`` per step,
    unit Gaussian noise) clipped at a floor of ``1.0``. Open/high/low are
    derived from close with small Gaussian perturbations, and volume is random
    integers. The index is a business-day (by default) :class:`~pandas.DatetimeIndex`.

    Parameters
    ----------
    n:
        Number of bars.
    seed:
        Seed for :func:`numpy.random.default_rng` (controls full determinism).
    start:
        First date of the index (parsed by :func:`pandas.date_range`).
    start_price:
        Base price added to the cumulative random walk.
    freq:
        Pandas offset alias for the index frequency (default ``"B"``).

    Returns
    -------
    pandas.DataFrame
        Frame with columns exactly :data:`OHLCV_COLUMNS` and a
        :class:`~pandas.DatetimeIndex`.
    """
    rng = np.random.default_rng(seed)

    steps = rng.normal(0.05, 1.0, size=n)
    close = start_price + np.cumsum(steps)
    close = np.clip(close, 1.0, None)  # 价格地板，避免出现非正价

    open_ = close + rng.normal(0.0, 0.3, size=n)
    high = np.maximum(open_, close) + np.abs(rng.normal(0.0, 0.5, size=n))
    low = np.minimum(open_, close) - np.abs(rng.normal(0.0, 0.5, size=n))
    volume = rng.integers(1000, 5000, size=n)

    index = pd.date_range(start=start, periods=n, freq=freq)

    df = pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=index,
    )
    # 确保列顺序与契约一致
    return df[list(OHLCV_COLUMNS)]


class SyntheticDataSource(DataSource):
    """A :class:`DataSource` backed by :func:`generate_ohlcv`.

    The generator parameters are fixed at construction time; ``symbol`` and the
    ``start`` / ``end`` arguments of :meth:`get_dataframe` only affect feed
    naming and date slicing, not the underlying random series (so the same
    instance is fully reproducible).
    """

    def __init__(self, n: int = 300, seed: int = 42, *, start: str = "2022-01-01") -> None:
        self.n = n
        self.seed = seed
        self.start = start

    def get_dataframe(
        self,
        symbol: str = "SYNTH",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Return synthetic OHLCV bars, optionally sliced to ``[start, end]``."""
        df = generate_ohlcv(n=self.n, seed=self.seed, start=self.start)
        if start is not None or end is not None:
            df = df.loc[start:end]
        return df


__all__ = ["generate_ohlcv", "SyntheticDataSource"]
