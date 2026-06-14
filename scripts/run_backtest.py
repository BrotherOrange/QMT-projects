"""Copy-pasteable end-to-end demo for the :mod:`qmtquant` package.

This script is the manual "sanity run" that replaces the old root-level
``test_backtrader.py``. It uses ONLY the public :mod:`qmtquant` API:

    1. build a deterministic synthetic data source,
    2. run a backtest through :func:`qmtquant.run_backtest`,
    3. print the headline metrics, and
    4. render the backtrader chart to ``artifacts/`` via
       :func:`qmtquant.save_plot` (the verified non-blocking plot helper).

It is intentionally NOT imported by the package or the test-suite; run it
directly to eyeball that everything wires together:

    python scripts/run_backtest.py
    python scripts/run_backtest.py --seed 7 --bars 500 --out artifacts/demo.png

By default it delegates to :func:`qmtquant.cli.main` so the script and the
``qmtquant`` console-script stay behaviourally identical. Pass ``--inline`` to
exercise the public objects (``SyntheticDataSource`` / ``run_backtest`` /
``save_plot``) explicitly instead.
"""

from __future__ import annotations

import argparse
import os
import sys

from qmtquant import SyntheticDataSource, run_backtest, save_plot


def _run_inline(seed: int, bars: int, out: str) -> int:
    """Drive the public API directly and print a small summary.

    This mirrors what :func:`qmtquant.cli.main` does, but spelled out so the
    script doubles as a worked example of the top-level objects.
    """
    # 1. Build a deterministic synthetic OHLCV source.
    source = SyntheticDataSource(n=bars, seed=seed)

    # 2. Run the backtest end-to-end (feed -> cerebro -> run -> metrics).
    result = run_backtest(source)

    # 3. Print the headline numbers.
    metrics = result.metrics
    print("=" * 48)
    print("qmtquant synthetic backtest")
    print("=" * 48)
    print(f"start value : {result.start_value:,.2f}")
    print(f"end value   : {result.end_value:,.2f}")
    print(f"pnl         : {result.end_value - result.start_value:,.2f}")
    print(f"sharpe      : {metrics.sharpe}")
    print(f"max dd      : {metrics.max_drawdown}")
    print(f"tot return  : {metrics.total_return}")
    print(f"tot trades  : {metrics.total_trades}")

    # 4. Save the chart under artifacts/ without blocking on plt.show().
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    saved = save_plot(result.cerebro, out)
    print(f"saved plot  : {saved}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse args and run the demo, delegating to the CLI by default."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (default: 42)")
    parser.add_argument("--bars", type=int, default=300, help="number of bars (default: 300)")
    parser.add_argument(
        "--out",
        type=str,
        default="artifacts/backtrader_plot.png",
        help="output PNG path (default: artifacts/backtrader_plot.png)",
    )
    parser.add_argument(
        "--inline",
        action="store_true",
        help="drive the public API directly instead of delegating to qmtquant.cli.main",
    )
    args = parser.parse_args(argv)

    if args.inline:
        return _run_inline(args.seed, args.bars, args.out)

    # Delegate to the installed console-script entry point for parity.
    from qmtquant.cli import main as cli_main

    return cli_main(["--seed", str(args.seed), "--bars", str(args.bars), "--out", args.out])


if __name__ == "__main__":
    sys.exit(main())
