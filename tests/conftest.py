"""Shared pytest fixtures for the qmtquant test-suite.

The old smoke test followed a "run the backtest once, then assert many things"
pattern. We preserve that here with a *session-scoped* ``result`` fixture so the
relatively expensive cerebro run happens a single time for the whole suite,
while cheaper data fixtures (``synth_df`` / ``synth_source``) are recreated per
test for isolation.
"""

from __future__ import annotations

import pandas as pd
import pytest

from qmtquant.backtest.engine import BacktestResult, run_backtest
from qmtquant.data.sources.synthetic import SyntheticDataSource, generate_ohlcv


@pytest.fixture
def synth_df() -> pd.DataFrame:
    """A deterministic synthetic OHLCV frame (default seed/size)."""
    return generate_ohlcv()


@pytest.fixture
def synth_source() -> SyntheticDataSource:
    """A deterministic synthetic data source (default seed/size)."""
    return SyntheticDataSource()


@pytest.fixture(scope="session")
def result() -> BacktestResult:
    """Run the synthetic backtest exactly ONCE for the whole session.

    Mirrors the old "run once, assert many" smoke test: every downstream test
    inspects this single :class:`~qmtquant.backtest.engine.BacktestResult`.
    """
    return run_backtest(SyntheticDataSource())
