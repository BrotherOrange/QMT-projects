# qmtquant

A small, well-structured quant backtesting toolkit built on
[backtrader](https://www.backtrader.com/), with a future-facing
xtquant / miniQMT live-trading path baked in as an empty shell.

The package follows a strict one-way dependency direction:

```
data  ->  strategies  ->  backtest  ->  plotting
live/ is an independent, future-facing sibling (no backtest coupling)
```

The engine depends only on the `DataSource` abstraction and a `bt.Strategy`
subclass, so a CSV source, the seeded synthetic source, or (later) an xtquant
market-data source can all be swapped in without touching the engine.

---

## Install (editable install is REQUIRED first)

This project uses a **src-layout** (`src/qmtquant/...`). The package is not on
`sys.path` until you install it. Always install it editable before importing or
running anything -- otherwise `import qmtquant` will fail.

### Option A -- conda (recommended; the `qmt-projects-py310` env)

```bash
conda env create -f environment.yml
conda activate qmt-projects-py310
# the editable dev install already ran via the environment.yml pip section;
# re-run it any time pyproject.toml changes:
pip install -e ".[dev]"
```

> Python 3.10 is used so a single env serves both the backtrader backtest stack
> and the xtquant live path. The installed miniQMT terminal ships `xtquant`
> .pyd builds for cp36..cp311 only (NO cp312), so xtquant cannot be imported on
> Python 3.12. See "xtquant / miniQMT integration" below.

### Option B -- plain venv / pip

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# editable install with dev extras (pulls pinned backtrader/numpy/pandas/matplotlib + pytest)
pip install -e ".[dev]"
```

---

## Run the example / CLI

After the editable install, a console script named `qmtquant` is on your PATH:

```bash
# default synthetic backtest, prints a summary and saves a plot to artifacts/
qmtquant

# tune the run
qmtquant --seed 7 --bars 500 --out artifacts/run7.png
```

Equivalent runnable demo script (not imported by the package or tests):

```bash
python scripts/run_backtest.py
```

Or from Python:

```python
from qmtquant import run_backtest, save_plot, SyntheticDataSource

result = run_backtest(SyntheticDataSource(n=300, seed=42))
print(result.start_value, "->", result.end_value)
print(result.metrics)
save_plot(result.cerebro, "artifacts/backtrader_plot.png")
```

---

## Run the tests

```bash
pytest
```

`pytest` configuration lives in `pyproject.toml` (`testpaths=["tests"]`,
`addopts="-q"`). The suite migrates the original 13 smoke checks (imports/
versions, feed build, indicators, orders, trades, broker cash with commission,
the four analyzers, and `save_plot` writing a PNG) into proper tests against the
package API. The backtest runs **once** via a session-scoped fixture and many
assertions check that single result.

---

## NOTE: the `cerebro.plot()` blocking bug (and the fix)

backtrader's `cerebro.plot()` **unconditionally** calls
`matplotlib.pyplot.show()` at the end. In a plain `.py` script (no GUI event
loop) this **blocks forever** in the Tk mainloop -- and it does so *even when you
have already called `matplotlib.use("Agg")`*. `Agg` stops a window from opening,
but `show()` still hands control to the GUI loop and never returns.

The verified fix lives in `src/qmtquant/plotting/plot.py` as `save_plot(...)`:

1. `matplotlib.use("Agg")` is set **at import time**, before `pyplot` is imported
   (and `pyplot` is imported nowhere else in the package).
2. Around the `cerebro.plot()` call, `plt.show` is temporarily replaced with a
   no-op, then restored in a `finally` block (so interactive sessions are not
   polluted).
3. The returned figures are written to disk with `fig.savefig(...)`.

```python
from qmtquant import save_plot
saved_paths = save_plot(result.cerebro, "artifacts/backtrader_plot.png")
```

**Not needed in Jupyter.** Inside a Jupyter notebook, inline plotting works and
`cerebro.plot()` returns normally -- `save_plot` is only required for headless
`.py` script / CLI runs.

---

## Why the dependency pins (numpy<2, matplotlib<3.8)

These are pinned in `pyproject.toml` because they are known-good *together* with
backtrader `1.9.78.123`:

- **numpy `>=1.26,<2`** -- backtrader references numpy aliases that were removed
  in numpy 2.x (e.g. `np.bool`, `np.float`). Under numpy 2.x backtrader raises
  `AttributeError` on import/use, so numpy is held in the 1.26.x line.
- **matplotlib `>=3.5,<3.8`** -- backtrader's plotting code calls matplotlib
  internals removed in 3.8 (axis label / locator / date handling), which breaks
  `cerebro.plot()`. Held below 3.8 to keep plotting working.

`pandas` is intentionally unpinned (its API surface used here is stable across
versions compatible with numpy 1.26.x).

---

## Live trading roadmap (xtquant, after qualification)

Market **data** via xtquant is now **implemented** (`XtQuantDataSource`, verified
end-to-end: real daily bars -> backtrader backtest). The live **broker** (order
placement) is still a stub raising `NotImplementedError`, pending the trading wiring.

- `qmtquant/live/broker.py` -- the `Broker` ABC plus the
  `Order` / `Position` / `OrderSide` / `OrderType` domain types.
- `qmtquant/live/xtquant_broker.py` -- `XtQuantBroker` stub; after QMT
  qualification, implement it via `xtquant.xttrader`
  (`XtQuantTrader` / `StockAccount`: login, `order_stock`, `cancel_order_stock`,
  `query_stock_positions`, `query_stock_asset`).
- `qmtquant/data/sources/xtquant_source.py` -- `XtQuantDataSource` **implemented**
  via `xtquant.xtdata` (`download_history_data` + `get_market_data_ex`); pulls real
  A-share OHLCV bars (daily/minute) into the `DataSource` contract. Usage:
  `run_backtest(XtQuantDataSource(period="1d"), symbol="000001.SZ")` (needs the env
  set up via `scripts/setup_xtquant.py` + a running terminal).

Configuration for the live path is documented in `.env.example`
(`QMTQUANT_XT_ACCOUNT_ID`, `QMTQUANT_MINI_QMT_PATH`). The backtest path needs
none of these.

To keep CI green before qualification, **no** `import xtquant` appears at module
top-level anywhere; xtquant is imported lazily inside the methods that need it.

---

## xtquant / miniQMT integration (verified working 2026-06-18)

The 迅投 miniQMT terminal is installed and its `xtquant` API has been verified
against the running terminal (both the data side `xtdata` and the trade-channel
`xttrader.connect()` succeed).

**Environment requirement -- Python 3.10/3.11 only.** The terminal-bundled
`xtquant` ships compiled `.pyd` extensions for cp36..cp311; there is **no
cp312** build. So xtquant works in `qmt-projects-py310` but **cannot** be
imported under Python 3.12.

**Making `from xtquant import xtdata` work in the env.** `xtquant` is not a
pip package here -- it lives inside the terminal install. Run once per env:

```bash
conda activate qmt-projects-py310
python scripts/setup_xtquant.py          # or: --bin "<path>\bin.x64"
```

This creates a **directory junction** `xtquant` inside the env's site-packages
pointing at the terminal's `bin.x64/Lib/site-packages/xtquant`. So `import
xtquant` resolves normally and its `.pyd` loads its DLLs from the junction
target (verified: even `xttrader.connect()` needs no extra `add_dll_directory`).
Crucially this exposes **only `xtquant`** -- NOT the terminal's large Python-3.6
package tree (IPython / Pillow 6 / pyreadline / ...), which would otherwise
shadow or break the env (an early "append the whole site-packages" attempt made
`pytest` crash on the terminal's ancient `pyreadline`). After setup, any
script / REPL / xtquant skill in the env can `import xtquant` directly. The
default terminal path is baked into `scripts/setup_xtquant.py` -- override with
`--bin` or the `QMTQUANT_QMT_BIN_PATH` env var if you move/reinstall QMT.
(Junctions need no admin rights on NTFS; the script falls back to copying if the
junction can't be created.)

**Verified-working API surface** (6/8 of the `xtquant-api-*` skills): stock list
& sectors, `get_instrument_detail`, `download_history_data` + `get_market_data_ex`
(1m/5m/1d/tick), `download_history_data2` (with callback), and financial data.

**This terminal build's quirks** (the skills were written for a newer xtquant;
their scripts/docs have been corrected accordingly):

- No `incrementally` kwarg on `download_history_data` / `download_history_data2`
  / `download_financial_data` -- do not pass it (raises `TypeError`).
- No `get_instrument_detail_list` -- loop over `get_instrument_detail` instead.
- `download_history_data2` **blocks forever without a `callback`** -- always pass one.
- The `stoppricedata` (涨跌停价) and `buysellvol` (内外盘) periods are **not
  supported** by this build (`get_market_data_ex` errors with "周期错误"). The
  two skills that relied on them were removed. Workarounds: read 涨跌停价 from
  `get_instrument_detail` (`UpStopPrice` / `DownStopPrice`), or compute it from
  `preClose` x board ratio; reconstruct 内外盘 from tick data if needed.
