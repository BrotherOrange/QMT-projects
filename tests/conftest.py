"""Shared pytest fixtures for the qmtquant test-suite."""

from __future__ import annotations

import pandas as pd
import pytest

from qmtquant.data.sources.synthetic import SyntheticDataSource, generate_ohlcv


@pytest.fixture
def synth_df() -> pd.DataFrame:
    """A deterministic synthetic OHLCV frame (default seed/size)."""
    return generate_ohlcv()


@pytest.fixture
def synth_source() -> SyntheticDataSource:
    """A deterministic synthetic data source (default seed/size)."""
    return SyntheticDataSource()
