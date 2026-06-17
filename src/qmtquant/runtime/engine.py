"""统一运行引擎：把 策略 + 行情(feed) + broker 串起来跑，产出 :class:`Result`。

回测/模拟用 :class:`~qmtquant.runtime.feed.ReplayFeed` + :class:`~qmtquant.live.paper_broker.PaperBroker`。
实盘(v2) 将由独立的实时引擎驱动、成交经 ``XtQuantBroker`` 异步回调返回——但策略侧
（``on_bar`` + :class:`~qmtquant.live.broker.Broker` 接口）完全一致。

每根 bar 的处理顺序（实现"收盘决策、下一根开盘成交"）：
  日切→roll_day(T+1) → update_market(bar) → process_pending(撮合上一根挂单)
  → strategy.on_bar(ctx) → 记录权益。
"""

from __future__ import annotations

from .feed import Feed
from .result import Result, compute_metrics
from .strategy import Context, Strategy


def run(strategy: Strategy, feed: Feed, broker) -> Result:
    """运行一次回测/模拟并返回 :class:`Result`。

    Parameters
    ----------
    strategy:
        用户的 :class:`Strategy` 实例。
    feed:
        行情源（如 :class:`~qmtquant.runtime.feed.ReplayFeed`）。
    broker:
        支持引擎接口（``update_market`` / ``process_pending`` / ``roll_day`` / ``equity``）
        的 broker，如 :class:`~qmtquant.live.paper_broker.PaperBroker`。
    """
    broker.connect()
    history = []
    equity_curve: list[tuple[object, float]] = []
    symbol = getattr(feed, "symbol", "")
    prev_date = None

    strategy.on_init(Context(broker, symbol, None, history))

    last_ctx: Context | None = None
    for bar in feed:
        if prev_date is not None and bar.date != prev_date:
            broker.roll_day()
        broker.update_market(bar)
        broker.process_pending()

        history.append(bar)
        ctx = Context(broker, bar.symbol, bar, history)
        strategy.on_bar(ctx)

        equity_curve.append((bar.ts, broker.equity()))
        prev_date = bar.date
        last_ctx = ctx

    if last_ctx is not None:
        strategy.on_stop(last_ctx)
    broker.disconnect()

    trades = broker.trades
    return Result(
        equity_curve=equity_curve,
        trades=trades,
        metrics=compute_metrics(equity_curve, num_trades=len(trades)),
        final_cash=broker.get_cash(),
        final_positions=broker.get_positions(),
    )


__all__ = ["run"]
