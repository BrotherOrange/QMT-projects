"""Smoke check #13: plotting writes a real PNG without hanging.

This guards the verified plot-blocking fix in ``qmtquant.plotting.plot``:
backtrader's ``cerebro.plot()`` unconditionally calls ``plt.show()`` which
blocks forever in plain scripts. ``save_plot`` temporarily no-ops ``plt.show``
and then ``fig.savefig``s. If the fix regresses, this test would hang (and the
suite would time out) rather than silently pass.

Uses ``tmp_path`` so no artifacts land in the repo.
"""

from __future__ import annotations

import os

from qmtquant.backtest.engine import BacktestResult
from qmtquant.plotting.plot import save_plot


def test_save_plot_writes_png(result: BacktestResult, tmp_path) -> None:
    """save_plot returns a non-empty list of real, non-empty PNG paths."""
    target = tmp_path / "smoke_plot.png"

    saved = save_plot(result.cerebro, target)

    assert isinstance(saved, list)
    assert saved, "save_plot returned an empty list"
    for path in saved:
        assert os.path.exists(path), f"plot file missing: {path}"
        assert os.path.getsize(path) > 0, f"plot file empty: {path}"
