"""PaperBroker A 股规则单测 + 引擎端到端冒烟（全部离线、确定性）。"""

from __future__ import annotations

import pandas as pd
import pytest

from qmtquant.data.sources.synthetic import SyntheticDataSource
from qmtquant.live.broker import Order, OrderSide, OrderType
from qmtquant.live.paper_broker import AShareRules, PaperBroker
from qmtquant.runtime.engine import run
from qmtquant.runtime.feed import Bar, ReplayFeed
from qmtquant.runtime.strategy import Context, Strategy

TS = pd.Timestamp("2026-01-02")


def bar(open_, *, high=None, low=None, close=None, up=None, down=None, sym="X", ts=TS) -> Bar:
    return Bar(
        ts=ts, symbol=sym, open=open_,
        high=high if high is not None else open_,
        low=low if low is not None else open_,
        close=close if close is not None else open_,
        volume=1000, up_limit=up, down_limit=down,
    )


def buy(b: PaperBroker, size, price=None, sym="X"):
    t = OrderType.LIMIT if price is not None else OrderType.MARKET
    return b.place_order(Order(symbol=sym, side=OrderSide.BUY, size=size, price=price, type=t))


def sell(b: PaperBroker, size, price=None, sym="X"):
    t = OrderType.LIMIT if price is not None else OrderType.MARKET
    return b.place_order(Order(symbol=sym, side=OrderSide.SELL, size=size, price=price, type=t))


def test_buy_lot_rounding_and_next_bar_fill():
    b = PaperBroker(cash=100_000.0)
    buy(b, 150)                       # 150 → 整手取整为 100
    b.update_market(bar(10.0))
    b.process_pending()
    pos = b.get_positions()
    assert len(pos) == 1 and pos[0].size == 100 and pos[0].avg_price == pytest.approx(10.0)
    # cash = 100000 - (1000 + max(1000*0.0003,5)=5 + 1000*1e-5=0.01)
    assert b.get_cash() == pytest.approx(100_000 - 1005.01)


def test_t1_blocks_same_day_sell_until_roll_day():
    b = PaperBroker(cash=100_000.0)
    buy(b, 100); b.update_market(bar(10.0)); b.process_pending()
    assert b.get_positions()[0].size == 100

    sell(b, 100)
    b.update_market(bar(11.0)); b.process_pending()      # 当日：T+1 不可卖
    assert b.get_positions()[0].size == 100              # 仍持有

    b.roll_day()                                         # 次日：解锁
    b.update_market(bar(11.0)); b.process_pending()
    assert b.get_positions() == []                       # 卖出成交


def test_price_limit_blocks_buy_at_up_limit():
    b = PaperBroker(cash=100_000.0)
    buy(b, 100)
    b.update_market(bar(10.5, up=10.5))                  # 开盘=涨停价
    b.process_pending()
    assert b.get_positions() == []                       # 涨停买不进
    assert b.get_cash() == 100_000.0


def test_price_limit_blocks_sell_at_down_limit():
    b = PaperBroker(cash=100_000.0)
    buy(b, 100); b.update_market(bar(10.0)); b.process_pending()
    b.roll_day()                                         # 解锁可卖
    sell(b, 100)
    b.update_market(bar(9.0, down=9.0))                  # 开盘=跌停价
    b.process_pending()
    assert b.get_positions()[0].size == 100              # 跌停卖不出


def test_insufficient_cash_rejects_buy():
    b = PaperBroker(cash=500.0)
    buy(b, 100)                                          # 需 ~1005 > 500
    b.update_market(bar(10.0)); b.process_pending()
    assert b.get_positions() == []
    assert b.get_cash() == 500.0
    assert b._pending == []                              # 现金不足 → 拒单移出队列


def test_fees_and_cash_round_trip():
    b = PaperBroker(cash=100_000.0)
    buy(b, 100); b.update_market(bar(10.0)); b.process_pending()
    assert b.get_cash() == pytest.approx(100_000 - 1005.01)
    b.roll_day()
    sell(b, 100); b.update_market(bar(11.0)); b.process_pending()
    # 卖出 proceeds = 1100 - 5(佣金) - 0.55(印花税) - 0.011(过户费)
    assert b.get_cash() == pytest.approx(100_000 - 1005.01 + (1100 - 5 - 0.55 - 0.011))
    assert b.get_positions() == []
    assert len(b.trades) == 2


def test_limit_order_fills_when_price_crosses():
    b = PaperBroker(cash=100_000.0)
    buy(b, 100, price=9.5)                               # 限价 9.5 买
    b.update_market(bar(10.0, high=10.2, low=9.4))       # 盘中触及 9.5（low=9.4）
    b.process_pending()
    pos = b.get_positions()
    assert len(pos) == 1 and pos[0].size == 100
    assert pos[0].avg_price == pytest.approx(9.5)        # 成交于 min(open,limit)=9.5


class _BuyOnceStrategy(Strategy):
    """冒烟用：第一次有机会买 100 股并持有（非交易建议）。"""

    def __init__(self):
        self._done = False

    def on_bar(self, ctx: Context) -> None:
        if not self._done and ctx.position() is None:
            ctx.buy(100)
            self._done = True


def test_engine_end_to_end_smoke():
    df = SyntheticDataSource(n=50, seed=1).get_dataframe("X")
    feed = ReplayFeed(df, "X")
    broker = PaperBroker(cash=100_000.0)
    result = run(_BuyOnceStrategy(), feed, broker)

    assert len(result.equity_curve) == 50
    assert result.metrics.num_trades == 1
    assert any(p.symbol == "X" and p.size == 100 for p in result.final_positions)
    # 指标可计算（不校验具体数值，只确保类型/范围合理）
    assert 0.0 <= result.metrics.max_drawdown <= 1.0
    assert isinstance(result.metrics.total_return, float)
