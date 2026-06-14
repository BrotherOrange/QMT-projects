"""Console-script entry point for qmtquant.

This is a *thin* wrapper: it parses a few arguments, runs the default synthetic
backtest end-to-end through the package's public APIs, prints a human-readable
summary, and saves a plot under ``artifacts/``. It is the runnable replacement
for the original root smoke-test script's ``main`` behavior.

Tests never depend on this module -- they exercise the package APIs directly.

Registered in pyproject.toml as::

    [project.scripts]
    qmtquant = "qmtquant.cli:main"
"""
from __future__ import annotations

import argparse

from .backtest.engine import run_backtest
from .data.sources.synthetic import SyntheticDataSource
from .plotting.plot import save_plot


def _build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the ``qmtquant`` console script."""
    parser = argparse.ArgumentParser(
        prog="qmtquant",
        description="Run the default synthetic backtrader backtest and save a plot.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for the synthetic OHLCV data (default: 42).",
    )
    parser.add_argument(
        "--bars",
        type=int,
        default=300,
        help="Number of bars (rows) to generate (default: 300).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="artifacts/backtrader_plot.png",
        help="Output path for the saved plot (default: artifacts/backtrader_plot.png).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the default synthetic backtest end-to-end.

    Args:
        argv: Optional argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code (0 on success).
    """
    args = _build_parser().parse_args(argv)

    source = SyntheticDataSource(n=args.bars, seed=args.seed)
    result = run_backtest(source)

    metrics = result.metrics
    print("=" * 60)
    print("qmtquant backtest")
    print("=" * 60)
    print(f"bars            : {args.bars}  (seed={args.seed})")
    print(f"start value     : {result.start_value:.2f}")
    print(f"end value       : {result.end_value:.2f}")
    print(f"sharpe          : {metrics.sharpe}")
    print(f"max drawdown %  : {metrics.max_drawdown}")
    print(f"total return    : {metrics.total_return}")
    print(f"total trades    : {metrics.total_trades}")

    saved = save_plot(result.cerebro, args.out)
    print(f"saved plot      : {', '.join(saved)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
