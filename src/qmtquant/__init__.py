"""qmtquant —— 自建统一量化运行时（回测 / 模拟 / 实盘）。

写一套策略，换"数据源 + broker"即可在回测/模拟/实盘之间无感切换::

    from qmtquant import Strategy, ReplayFeed, run, PaperBroker, XtQuantDataSource

    class MyStrategy(Strategy):
        def on_bar(self, ctx):
            ...   # 你的逻辑

    feed = ReplayFeed(XtQuantDataSource(period="1d").get_dataframe("000001.SZ"), "000001.SZ")
    result = run(MyStrategy(), feed, PaperBroker(cash=100_000))
    print(result.metrics)

依赖方向：``data``(OHLCV 数据源) → ``runtime``(策略/引擎) → 结果；``live``(broker 抽象 +
PaperBroker + 未来 XtQuantBroker) 被引擎使用。
"""

from __future__ import annotations

__version__: str = "0.1.0"

# 数据
from .data.sources.base import DataSource, OHLCV_COLUMNS, validate_ohlcv
from .data.sources.synthetic import generate_ohlcv, SyntheticDataSource
from .data.sources.csv import CsvDataSource
from .data.sources.xtquant_source import XtQuantDataSource

# 运行时（策略 / 行情 / 引擎 / 结果）
from .runtime.strategy import Strategy, Context
from .runtime.feed import Bar, Feed, ReplayFeed
from .runtime.engine import run
from .runtime.result import Result, Metrics

# 交易 broker（抽象 + 本地模拟；实盘 XtQuantBroker 见 live 子包）
from .live.broker import Broker, Order, OrderSide, OrderType, Position
from .live.paper_broker import PaperBroker, AShareRules

# 配置
from .config import BrokerConfig, BacktestConfig

__all__ = [
    "__version__",
    # data
    "DataSource",
    "OHLCV_COLUMNS",
    "validate_ohlcv",
    "generate_ohlcv",
    "SyntheticDataSource",
    "CsvDataSource",
    "XtQuantDataSource",
    # runtime
    "Strategy",
    "Context",
    "Bar",
    "Feed",
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
    # config
    "BrokerConfig",
    "BacktestConfig",
]
