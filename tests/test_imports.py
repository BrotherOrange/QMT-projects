"""Smoke check #1: imports and pinned-version sanity.

Confirms the package imports cleanly and the third-party stack is the
known-good pinned combination (backtrader importable, numpy major < 2,
pandas present, ``qmtquant.__version__`` exposed).
"""

from __future__ import annotations


def test_third_party_versions() -> None:
    """backtrader / numpy / pandas import and report sane versions."""
    import backtrader as bt
    import numpy as np
    import pandas as pd

    # numpy must stay on the 1.x line (backtrader 1.9.78.123 is not numpy-2 safe).
    numpy_major = int(np.__version__.split(".")[0])
    assert numpy_major < 2, f"numpy must be <2, got {np.__version__}"

    # backtrader and pandas simply need to expose a version string.
    assert getattr(bt, "__version__", None), "backtrader.__version__ missing"
    assert getattr(pd, "__version__", None), "pandas.__version__ missing"


def test_package_imports() -> None:
    """The top-level package imports and exposes a version."""
    import qmtquant

    assert isinstance(qmtquant.__version__, str)
    assert qmtquant.__version__  # non-empty

    # Curated top-level re-exports should be present.
    for name in (
        "run_backtest",
        "build_cerebro",
        "BacktestResult",
        "Metrics",
        "save_plot",
        "SmaCross",
        "generate_ohlcv",
        "SyntheticDataSource",
        "DataSource",
        "OHLCV_COLUMNS",
        "BrokerConfig",
        "BacktestConfig",
    ):
        assert hasattr(qmtquant, name), f"qmtquant.{name} not exported"
