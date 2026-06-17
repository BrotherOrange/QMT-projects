"""``qmtquant`` 命令行入口：用合成数据跑一次统一运行时演示。

仅作端到端冒烟演示，证明 数据→引擎→PaperBroker 链路可用。内置的
:class:`_DemoStrategy` 是**演示用买入持有**，不是你的策略——请按
:class:`qmtquant.runtime.Strategy` 自己实现。Tests 不依赖本模块。

Registered in pyproject.toml as::

    [project.scripts]
    qmtquant = "qmtquant.cli:main"
"""
from __future__ import annotations

import argparse

from .data.sources.synthetic import SyntheticDataSource
from .live.paper_broker import PaperBroker
from .runtime.engine import run
from .runtime.feed import ReplayFeed
from .runtime.strategy import Strategy, Context


class _DemoStrategy(Strategy):
    """演示用：第一次有机会就买入 ``size`` 股并持有到底（非交易建议）。"""

    def __init__(self, size: int = 100) -> None:
        self.size = size
        self._done = False

    def on_bar(self, ctx: Context) -> None:
        if not self._done and ctx.position() is None:
            ctx.buy(self.size)   # 市价买入，下一根开盘成交
            self._done = True


def main(argv: list[str] | None = None) -> int:
    """用合成数据跑一次运行时演示，打印结果摘要。返回进程退出码。"""
    parser = argparse.ArgumentParser(prog="qmtquant", description="统一运行时演示（合成数据）")
    parser.add_argument("--seed", type=int, default=42, help="合成数据随机种子（默认 42）")
    parser.add_argument("--bars", type=int, default=300, help="合成 K 线根数（默认 300）")
    parser.add_argument("--cash", type=float, default=100_000.0, help="初始资金（默认 100000）")
    args = parser.parse_args(argv)

    df = SyntheticDataSource(n=args.bars, seed=args.seed).get_dataframe("SYNTH")
    feed = ReplayFeed(df, "SYNTH")
    broker = PaperBroker(cash=args.cash)
    result = run(_DemoStrategy(), feed, broker)

    m = result.metrics
    pos = [(p.symbol, p.size, round(p.avg_price, 2)) for p in result.final_positions]
    print("=" * 60)
    print("qmtquant 运行时演示（合成数据 / 演示策略=买入持有）")
    print("=" * 60)
    print(f"bars={args.bars} seed={args.seed} 初始资金={args.cash:.2f}")
    print(f"期末现金   : {result.final_cash:.2f}")
    print(f"期末持仓   : {pos}")
    print(f"成交笔数   : {m.num_trades}")
    print(f"总收益率   : {m.total_return:.4%}")
    print(f"夏普       : {m.sharpe:.2f}")
    print(f"最大回撤   : {m.max_drawdown:.4%}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
