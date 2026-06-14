"""CSV-backed data source for real saved bars.

:class:`CsvDataSource` reads ``{root}/{symbol}.csv`` into the normalized OHLCV
frame: it parses the date column into a :class:`~pandas.DatetimeIndex`,
lowercases / renames columns to :data:`OHLCV_COLUMNS`, and slices by date. This
is the second concrete implementation, proving the
:class:`~qmtquant.data.sources.base.DataSource` abstraction generalizes beyond
the synthetic generator.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import DataSource, OHLCV_COLUMNS


class CsvDataSource(DataSource):
    """Read normalized OHLCV bars from per-symbol CSV files.

    Each symbol lives in its own file ``{root}/{symbol}.csv``. The file must
    have a date column (default ``"date"``) plus open/high/low/close/volume
    columns (case-insensitive); extra columns are dropped.
    """

    def __init__(self, root: str | Path, *, date_col: str = "date") -> None:
        self.root = Path(root)
        self.date_col = date_col

    def get_dataframe(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Load ``{root}/{symbol}.csv`` as a normalized OHLCV frame.

        Steps: read the CSV, lowercase column names, parse the date column into
        a :class:`~pandas.DatetimeIndex`, keep / order only
        :data:`OHLCV_COLUMNS`, sort by date, and slice to ``[start, end]``.
        Validation happens later in
        :func:`qmtquant.data.feeds.make_pandas_feed`.

        Raises
        ------
        FileNotFoundError
            If the per-symbol CSV does not exist.
        ValueError
            If the configured date column is absent.
        """
        path = self.root / f"{symbol}.csv"
        if not path.exists():
            raise FileNotFoundError(f"no CSV for symbol {symbol!r}: {path}")

        df = pd.read_csv(path)
        # 统一列名为小写，便于映射到 OHLCV 契约
        df.columns = [str(c).strip().lower() for c in df.columns]

        date_col = self.date_col.lower()
        if date_col not in df.columns:
            raise ValueError(
                f"date column {self.date_col!r} not found in {path} "
                f"(columns: {list(df.columns)})"
            )

        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col).sort_index()
        df.index.name = self.date_col

        # 仅保留契约列并固定顺序；缺列会在下游校验时报错
        keep = [c for c in OHLCV_COLUMNS if c in df.columns]
        df = df[keep]

        if start is not None or end is not None:
            df = df.loc[start:end]
        return df


__all__ = ["CsvDataSource"]
