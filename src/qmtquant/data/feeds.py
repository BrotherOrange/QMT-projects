"""The single OHLCV -> backtrader adapter and validation point.

Every data source funnels through here before cerebro sees it:
:func:`validate_ohlcv` fails loudly on a bad shape (missing columns or a
non-:class:`~pandas.DatetimeIndex`) so problems surface with a clear message
instead of as a cryptic backtrader error, and :func:`make_pandas_feed` wraps a
validated frame in :class:`backtrader.feeds.PandasData`.

:data:`OHLCV_COLUMNS` is OWNED by :mod:`qmtquant.data.sources.base`; this module
imports it from there (single source of truth).
"""

from __future__ import annotations

from typing import Any

import backtrader as bt
import pandas as pd

from .sources.base import OHLCV_COLUMNS


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Return ``df`` unchanged if it is a well-formed OHLCV frame, else raise.

    A well-formed frame has a :class:`~pandas.DatetimeIndex` and contains all of
    :data:`OHLCV_COLUMNS`.

    Parameters
    ----------
    df:
        Candidate OHLCV frame.

    Returns
    -------
    pandas.DataFrame
        The same ``df`` instance, unmodified.

    Raises
    ------
    ValueError
        If ``df`` is not a :class:`~pandas.DataFrame`, lacks a
        :class:`~pandas.DatetimeIndex`, or is missing any required column.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"expected a pandas DataFrame, got {type(df).__name__!r}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            "OHLCV frame must have a DatetimeIndex, got "
            f"{type(df.index).__name__!r}"
        )
    missing = [col for col in OHLCV_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"OHLCV frame is missing required columns: {missing} "
            f"(expected all of {list(OHLCV_COLUMNS)}, got {list(df.columns)})"
        )
    return df


def make_pandas_feed(
    df: pd.DataFrame,
    *,
    name: str | None = None,
    **kwargs: Any,
) -> bt.feeds.PandasData:
    """Validate ``df`` then wrap it in a backtrader pandas feed.

    Parameters
    ----------
    df:
        OHLCV frame; validated via :func:`validate_ohlcv`.
    name:
        Optional human-readable feed name (passed to backtrader as ``name``).
    **kwargs:
        Extra keyword arguments forwarded to
        :class:`backtrader.feeds.PandasData`.

    Returns
    -------
    backtrader.feeds.PandasData
        A feed backed by the validated frame.
    """
    validate_ohlcv(df)
    if name is not None:
        kwargs.setdefault("name", name)
    return bt.feeds.PandasData(dataname=df, **kwargs)


__all__ = ["validate_ohlcv", "make_pandas_feed"]
