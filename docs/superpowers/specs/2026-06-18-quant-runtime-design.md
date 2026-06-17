# 统一量化运行时（回测/模拟/实盘）— 设计文档

日期：2026-06-18
状态：架构已与用户确认，待写实现计划
取代：`2026-06-18-paper-broker-design.md`（旧的 backtrader-伴随版，已废弃）

## 背景与决策

实测确认：QMT 原生回测（`qmttools`/`ContextInfo`）是**客户端 GUI 锁定**的——外部
`qmttools.ContextInfo` 是精简 shim（无 `set_universe`/`get_history_data`），回测账户/结果
在外部 Python 取不回。而 `xtdata`（数据）与 `xttrader`（交易）外部均可用。

因此采用 **(X) 自建统一 Python 运行时**：用户写**一套**策略，换"数据源 + broker"即在
回测/模拟/实盘间切换。**删除 backtrader**（其回测与实盘割裂、且已停维护）。

## 目标

- **写一次、无感切换**：策略只依赖 `Strategy`/`Context` 接口与 `Broker` 抽象。
  - 回测/模拟：`ReplayFeed`(历史K线) + `PaperBroker`(内存撮合、A股规则)
  - 实盘(v2)：`RealtimeFeed`(xtdata 实时) + `XtQuantBroker`(xttrader)
  - 切换 = 换 feed + broker，策略代码不改。
- headless、纯 Python、可版本控制 / CI / 参数扫描；不锁 QMT GUI。

## 非目标

- **不替用户写策略**：只提供 `Strategy`/`Context` 接口；仓库内仅有平凡测试假策略。
- v1 不做实时 feed 与 `XtQuantBroker` 实盘（接口预留，留 v2）。
- v1 单标的（`ReplayFeed` 喂单只股票的 DataFrame）；多标的/选股域留 v2（接口不预先排除）。

## 架构

```
        ┌──────────── 同一套策略（用户写，我不碰）────────────┐
        │  class MyStrategy(Strategy): def on_bar(self, ctx): ...│
        └──────────────────────────┬─────────────────────────────┘
 回测/模拟 ◄─ ReplayFeed(历史K线) ──┤ Engine.run ├─ PaperBroker(A股规则,内存撮合)
 实盘(v2) ◄─ RealtimeFeed(xtdata) ──┘            └─ XtQuantBroker(xttrader)  (v2)
```

## 组件（新增 `qmtquant/runtime/`；大量复用现有 data/、config、live/broker）

### runtime/strategy.py — 策略接口（不含策略逻辑）
- `Strategy`(ABC)：`on_init(ctx)`(可选)、`on_bar(ctx)`(必需)、`on_stop(ctx)`(可选)。
- `Context`：传给策略的运行上下文，暴露：
  - `ctx.broker`（`Broker`，下单/查询）、`ctx.now`(当前bar时间)、`ctx.symbol`、`ctx.bar`(当前OHLCV)
  - `ctx.history(n, field="close")`：截至当前 bar（含）的最近 n 根序列
  - `ctx.cash`/`ctx.position(symbol)`：便捷只读访问（转发 broker）

### runtime/feed.py — 行情驱动
- `Bar`(dataclass)：`ts, open, high, low, close, volume, up_limit, down_limit`。
- `Feed`(ABC)：按时间顺序产出 `Bar` + 维护历史窗口。
- `ReplayFeed(Feed)`：吃一个 OHLCV `DataFrame`(来自 `XtQuantDataSource`/`SyntheticDataSource`，DatetimeIndex)
  + `symbol`；逐根产出。涨跌停按 `round(prev_close × (1±limit_pct), 2)` 估算（`limit_pct` 默认 0.10，
  可配；注明近似，ST/创业板/科创板需自调）。
- `RealtimeFeed`：v2，xtdata 订阅驱动（接口同 `Feed`）。

### runtime/engine.py — 引擎
- `run(strategy, feed, broker) -> Result`，每根 bar t：
  1. 与上一根比较日期，日切则 `broker.roll_day()`（T+1 解锁）
  2. `broker.update_market(bar)`：设当前可成交行情=本根
  3. `broker.process_pending()`：撮合**上一根**挂的单（市价成交于本根 open；限价按本根 `[low,high]` 盘中撮合）
  4. `strategy.on_bar(ctx)`：用户看到本根**收盘**+历史，下单 → 入挂单队列
  5. 记录本根权益 `broker.equity()`
- **成交时点**：收盘决策、下一根开盘成交（无未来函数）。
- 说明：`update_market`/`process_pending` 是**回放引擎 + PaperBroker 的内部撮合机制**，
  不属于策略可见面。实盘(v2)将由独立的实时引擎驱动、成交由 `XtQuantBroker` 经 xttrader
  回调异步返回——但**策略侧（`on_bar` + `Broker` 下单/查询接口）完全一致**，这才是"无感切换"的本质。

### runtime/result.py — 结果
- `Result`(dataclass)：`equity_curve: list[(ts, equity)]`、`trades`、`metrics`、`final_cash`、`final_positions`。
- `metrics`：精简自算——`total_return`、`sharpe`(按权益日收益)、`max_drawdown`、`num_trades`。
- （v1.1 可选）`equity_curve` 绘图 helper；v1 仅保存数据，用户自绘。

### live/paper_broker.py — 模拟撮合（实现 Broker 抽象）
- `AShareRules`(frozen dataclass)：佣金 `0.0003`·最低 `5.0`；印花税 `0.0005`(仅卖出)；
  过户费 `0.00001`(双向)；整手 `100`；`enforce_t1=True`；`enforce_price_limit=True`。
- `PaperBroker(Broker)`：`__init__(*, cash=100_000.0, rules=AShareRules())`。
  - 实现 `Broker` 抽象：`connect/disconnect/place_order/cancel_order/get_positions/get_cash`。
  - 引擎接口：`update_market(bar)`、`process_pending()`、`roll_day()`、`equity()`。
  - 撮合校验顺序：整手取整(买向下取整到100；清仓允许零股) → 涨跌停不可成交 → T+1 可卖量 → 现金充足(含费用)。
  - 费用：佣金 `max(额×率, 5)`(双向)；印花税 额×率(卖出)；过户费 额×率(双向)。
  - 状态：现金、持仓(含 T+1 sellable/locked_today)、挂单、成交流水。
  - 只读内省：`trades`、`equity()`(现金+按当前 bar.close 市值)。**策略可用面=Broker 抽象**(保证无感切换)。

### 复用 / 不变
- `live/broker.py`：`Broker` 抽象 + `Order/OrderSide/OrderType/Position`（**复用**）。
- `data/sources/{base,synthetic,csv,xtquant_source}.py`：OHLCV 生产者（**复用**）。
  `DataSource` 去掉 backtrader 相关的 `to_feed`，保留 `get_dataframe` + `OHLCV_COLUMNS` + 形状校验。
- `config.py`：现金等配置（复用；费率以 `AShareRules` 为准）。
- `live/xtquant_broker.py`：实盘 stub，留 v2。

## 删除 backtrader（本次一并清理）

- 删目录/文件：`src/qmtquant/backtest/`（engine/analyzers）、`src/qmtquant/strategies/`（backtrader SmaCross）、
  `src/qmtquant/plotting/`、`src/qmtquant/data/feeds.py`（backtrader PandasData 适配）。
- 删测试：`tests/test_strategy_engine.py`、`tests/test_plot.py`，并改写 `tests/test_data.py`/`test_imports.py`
  去掉 backtrader 部分（保留 OHLCV 生成/校验测试）。
- `src/qmtquant/__init__.py`：移除 `run_backtest/build_cerebro/BacktestResult/Metrics/save_plot/SmaCross`
  导出，改为导出 runtime(`Strategy/Context/ReplayFeed/run/Result`) 与 `PaperBroker`。
- `pyproject.toml`：移除 `backtrader` 依赖；移除仅为 backtrader 而设的 `matplotlib<3.8` 约束
  （matplotlib 若 v1.1 绘图再按需加）。`numpy` 暂保守保留 `<2`（xtquant 的 .pyd 兼容性，实现时验证后再决定是否放开）。
  `pandas` 保留。
- README：更新为统一运行时说明，移除 backtrader/cerebro.plot 段落。

## 变更后的项目结构（src/qmtquant/）

```
__init__.py            # 更新导出
config.py              # 复用
data/sources/{base,synthetic,csv,xtquant_source}.py   # 复用(base 去 to_feed)
live/broker.py         # 复用：Broker 抽象 + 域类型
live/paper_broker.py   # 新：PaperBroker + AShareRules
live/xtquant_broker.py # stub，留 v2
runtime/strategy.py    # 新：Strategy + Context
runtime/feed.py        # 新：Bar + Feed + ReplayFeed (RealtimeFeed v2)
runtime/engine.py      # 新：run()
runtime/result.py      # 新：Result + metrics
```

## 数据流

```
XtQuantDataSource/SyntheticDataSource → DataFrame → ReplayFeed
   Engine.run(strategy, feed, broker) 逐根：
      日切→roll_day(T+1) → update_market(bar) → process_pending(撮合上根挂单)
      → strategy.on_bar(ctx)（用户下单→挂单）→ 记权益 → Result
切换实盘(v2)：ReplayFeed→RealtimeFeed、PaperBroker→XtQuantBroker，策略不变。
```

## 测试（离线、不依赖终端、CI 友好）

- `PaperBroker` 单测（合成 Bar/手动喂行情）：T+1 当日不可卖且 `roll_day` 后可卖；涨停不可买/跌停不可卖；
  整手取整与清仓零股；佣金最低5/卖出印花税/双向过户费 与现金扣减正确；现金不足拒单；持仓 size/avg_price 正确。
- `engine` 端到端冒烟：`SyntheticDataSource` 合成数据 + **平凡假策略**（如第10根买、第20根卖），
  断言权益曲线长度、成交笔数、末值与指标合理（确定性）。
- 可选实盘数据：`QMT_LIVE_TESTS=1` 用 `XtQuantDataSource` 真实日线跑一遍。

## v2（本 spec 不做，接口预留）

- `RealtimeFeed`(xtdata 订阅) + `XtQuantBroker`(xttrader 实盘)，同一 `Strategy` 跑实盘；
  券商模拟账户(假钱真API)亦走 `XtQuantBroker`。
- 多标的/选股域、限价挂单更精细的撮合、结果绘图、参数扫描器。
