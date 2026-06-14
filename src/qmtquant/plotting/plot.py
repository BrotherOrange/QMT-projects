"""Non-blocking plotting helper for backtrader (the verified plot-blocking fix).

KNOWN BUG
---------
``backtrader``'s :meth:`Cerebro.plot` unconditionally calls
``matplotlib.pyplot.show()`` at the end of plotting. In a plain ``.py`` script
this spins up the GUI backend's event loop (e.g. the Tk ``mainloop``) and
**blocks forever** -- even when ``matplotlib.use("Agg")`` has been selected,
because ``show()`` is still invoked on the figures backtrader created.

THE FIX (verified working)
--------------------------
1. Force the headless ``Agg`` backend *before* ``matplotlib.pyplot`` is ever
   imported (done at module import time below).
2. Temporarily replace ``plt.show`` with a no-op around the ``cerebro.plot()``
   call so the embedded ``show()`` returns immediately instead of blocking,
   then restore the original ``plt.show`` in a ``finally`` block.
3. Persist each produced figure with ``fig.savefig`` and return the list of
   saved file paths.

This module is migrated verbatim-in-spirit from the old ``bt_helpers.py`` smoke
script, preserving its multi-figure naming scheme.

JUPYTER CAVEAT
--------------
This fix is **unnecessary in Jupyter / IPython**: there inline plotting works
out of the box (``%matplotlib inline``), ``plt.show()`` does not block, and
``cerebro.plot()`` renders figures directly into the notebook. Use this helper
in plain scripts, CLIs, tests, and other headless contexts.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import matplotlib

# 必须在导入 pyplot 之前切换到无界面后端 Agg。
# Must select the headless backend BEFORE importing pyplot; do not import
# pyplot anywhere else in this package.
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (intentional: after backend select)

import backtrader as bt  # noqa: E402


def save_plot(
    cerebro: bt.Cerebro,
    path: str | os.PathLike[str] = "backtrader_plot.png",
    dpi: int = 100,
    **plot_kwargs: Any,
) -> list[str]:
    """Render ``cerebro``'s figures to disk without blocking, return saved paths.

    Wraps :meth:`backtrader.Cerebro.plot` so that the ``matplotlib.pyplot.show``
    call it makes internally becomes a no-op (it otherwise blocks forever in
    plain scripts -- see the module docstring). After plotting, every produced
    figure is written via :meth:`matplotlib.figure.Figure.savefig`.

    Parameters
    ----------
    cerebro:
        A ``Cerebro`` instance that has already ``run()``.
    path:
        Destination for the first figure. Defaults to ``"backtrader_plot.png"``.
        Parent directories are created automatically if needed.
    dpi:
        Resolution passed to ``savefig``. Defaults to ``100``.
    **plot_kwargs:
        Forwarded to ``cerebro.plot``. ``iplot=False`` and
        ``style="candlestick"`` are applied as defaults unless overridden.

    Returns
    -------
    list[str]
        Absolute-or-relative string paths of every image written, in order.
        When backtrader produces multiple figures, the first uses ``path`` and
        the rest get ``"{stem}_{i}_{j}{ext}"`` suffixes derived from it.

    Notes
    -----
    Unnecessary in Jupyter / IPython, where inline plotting already works and
    ``plt.show()`` does not block.
    """
    # backtrader 默认值：非交互式 + K 线样式。
    plot_kwargs.setdefault("iplot", False)
    plot_kwargs.setdefault("style", "candlestick")

    out = Path(path)
    if out.parent and not out.parent.exists():
        out.parent.mkdir(parents=True, exist_ok=True)

    # 临时把 plt.show 替换成空操作，绕过 backtrader 内部的阻塞调用。
    _orig_show = plt.show
    plt.show = lambda *args, **kwargs: None  # type: ignore[assignment]
    try:
        # cerebro.plot 返回一个嵌套列表：list[list[Figure]]。
        figs = cerebro.plot(**plot_kwargs)
    finally:
        plt.show = _orig_show  # type: ignore[assignment]

    stem = out.stem
    suffix = out.suffix or ".png"
    parent = out.parent

    saved: list[str] = []
    first = True
    for i, group in enumerate(figs):
        for j, fig in enumerate(group):
            if first:
                target = out
                first = False
            else:
                target = parent / f"{stem}_{i}_{j}{suffix}"
            fig.savefig(target, dpi=dpi)
            saved.append(str(target))

    return saved


__all__ = ["save_plot"]
