"""Smoke check #1: imports and third-party sanity.

Confirms the package imports cleanly (no backtrader / xtquant required) and the
curated top-level runtime API is exposed.
"""

from __future__ import annotations


def test_third_party_versions() -> None:
    """numpy / pandas import and report sane versions (numpy held <2 for xtquant)."""
    import numpy as np
    import pandas as pd

    numpy_major = int(np.__version__.split(".")[0])
    assert numpy_major < 2, f"numpy must be <2 (xtquant .pyd compat), got {np.__version__}"
    assert getattr(pd, "__version__", None), "pandas.__version__ missing"


def test_package_imports() -> None:
    """The top-level package imports and exposes the curated runtime API."""
    import qmtquant

    assert isinstance(qmtquant.__version__, str) and qmtquant.__version__

    for name in (
        # runtime
        "Strategy",
        "Context",
        "Bar",
        "ReplayFeed",
        "run",
        "Result",
        "Metrics",
        # broker
        "Broker",
        "Order",
        "OrderSide",
        "OrderType",
        "Position",
        "PaperBroker",
        "AShareRules",
        # data
        "DataSource",
        "OHLCV_COLUMNS",
        "validate_ohlcv",
        "generate_ohlcv",
        "SyntheticDataSource",
        "CsvDataSource",
        "XtQuantDataSource",
    ):
        assert hasattr(qmtquant, name), f"qmtquant.{name} not exported"


def test_package_does_not_import_backtrader() -> None:
    """Importing qmtquant must not pull in backtrader (the dep was removed)."""
    import sys

    import qmtquant  # noqa: F401

    assert "backtrader" not in sys.modules, "qmtquant must not import backtrader"
