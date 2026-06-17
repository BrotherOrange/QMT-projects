# PaperBroker 模拟交易沙盒 — 设计文档

日期：2026-06-18
状态：已与用户确认设计，待写实现计划

## 目标

提供一个**本地模拟交易沙盒** `PaperBroker`，让用户自己的策略代码可以把买卖/撤单/查询
操作"打"到模拟环境里验证，而**不动用真实资金账户**；并且——这是核心诉求——

> **无感切换**：用户的策略只依赖 `qmtquant.live.broker.Broker` 抽象接口。
> 从模拟切到实盘，只需把 `PaperBroker` 实例换成 `XtQuantBroker` 实例，**策略代码一行不改**。

```python
# 模拟：                                 # 实盘（将来）：
broker = PaperBroker(quote_source=...)    broker = XtQuantBroker(account_id=...)
# ↓ 以下用户策略代码完全相同 ↓
oid = broker.place_order(Order("000001.SZ", OrderSide.BUY, 100))
broker.get_positions(); broker.get_cash()
```

## 非目标（明确不做）

- **不替用户写任何策略/信号逻辑。** 沙盒只提供 broker 接口与一个"喂行情+调用户回调"的薄回放器；
  策略由用户自己写在回调里。仓库内只有最简单的测试假回调（买一次），不是策略。
- **不进行任何真实交易。** `PaperBroker` 绝不调用 `xtquant.xttrader`，绝不连接资金账户，
  绝不发出真实委托。买卖在 Python 内存里撮合记账。
- **v1 不做实时行情订阅循环**（交易时段调度、收盘结算等）。留作 v2。

## 它与 QMT 的关系

| 层面 | 是否用 QMT | 说明 |
|---|---|---|
| 行情(报价) | 只读使用 | 撮合价可取 QMT 实时行情(`XtQuoteSource`) 或已下载的历史K线离线回放(`ReplayQuoteSource`)。只读、零风险。 |
| 下单/账户 | **完全不用** | 本地内存撮合，不碰 `xttrader`、不碰资金账户。 |

将来的三个部署目标（策略代码全相同）：`PaperBroker`(本地模拟) / `XtQuantBroker`+券商模拟账户(假钱) /
`XtQuantBroker`+真实账户。本 spec 只覆盖 `PaperBroker`。

## 架构与组件

依赖方向：`live/` 仍是独立 sibling；`PaperBroker` 实现 `live/broker.py` 的 `Broker` 抽象。
无顶层 `import xtquant`（`XtQuoteSource` 内惰性导入），保持无 SDK 环境可导入。

### 1. `qmtquant/live/quotes.py` — 行情源

- `Quote`（dataclass）：`symbol, last, up_limit, down_limit, high, low`（live 时 high=low=last）。
- `QuoteSource`（Protocol/ABC）：`get_quote(symbol) -> Quote`。
- `XtQuoteSource(QuoteSource)`：实时。`last` 取 `xtdata.get_full_tick`；`up_limit/down_limit`
  取 `xtdata.get_instrument_detail` 的 `UpStopPrice/DownStopPrice`（已验证可用）。惰性 import xtquant。
- `ReplayQuoteSource(QuoteSource)`：吃一个 OHLCV `DataFrame`（来自 `XtQuantDataSource` 等，DatetimeIndex）；
  内部游标，`advance()` 前进一根；`current_bar()` 返回当前根 (ts, open/high/low/close)；
  `get_quote` 返回当前根（`last=open`，附 high/low 供限价单盘中撮合）。涨跌停按
  `round(prev_close × (1 ± limit_pct), 2)` 估算（`limit_pct` 可配，默认 0.10；注明是近似，
  ST/创业板/科创板需用户按需调整）。

### 2. `qmtquant/live/paper_broker.py` — 模拟撮合内核

- `AShareRules`（frozen dataclass）：
  - `commission_rate=0.0003`（万三）、`min_commission=5.0`
  - `stamp_tax_rate=0.0005`（印花税，**仅卖出**）
  - `transfer_fee_rate=0.00001`（过户费，双向）
  - `lot_size=100`（整手）、`enforce_t1=True`、`enforce_price_limit=True`
- `PaperBroker(Broker)`：
  - `__init__(self, *, cash=100_000.0, quote_source=None, rules=AShareRules())`
  - 内部状态：`_cash`、`_positions: dict[str,_Pos]`（`_Pos`: size, avg_price, sellable, locked_today）、
    `_pending: list[Order]`、`_trades: list[Fill]`、`_oid` 自增计数。
  - 实现 `Broker` 抽象：
    - `connect()/disconnect()`：置/清 `_connected` 标志（无网络动作）。
    - `place_order(order) -> str`：分配订单号；市价/限价单先校验**整手取整**（买入向下取整到 100；
      卖出允许清仓零股），再**入队 `_pending`**（成交时点见下），返回订单号。
    - `cancel_order(order_id)`：从 `_pending` 移除。
    - `get_positions() -> list[Position]`、`get_cash() -> float`。
  - 撮合相关（回放器调用）：
    - `process_pending()`：取 `self.quote_source` 的当前报价，对每个挂单尝试成交——
      校验顺序：**涨跌停不可成交**（买：last≥up_limit 拒；卖：last≤down_limit 拒）→ **T+1 可卖量**
      （卖出 size≤sellable）→ **现金充足**（买入 成本+费用≤cash）。市价单成交价=`quote.last`；
      限价单当 `[low,high]` 跨越限价时成交（买 fill=min(open,limit)，卖 fill=max(open,limit)），
      否则保持挂起。成交即更新现金/持仓/均价、扣费用、记 `_trades`。
    - `roll_day()`：`locked_today → sellable`（T+1 解锁），回放器在日期切换时调用。
  - 只读内省（供用户查看模拟结果，**不属于** Broker 抽象、不影响无感切换）：
    `trades` 成交流水、`equity()` 总资产（现金 + 按 `self.quote_source` 现价的市值）。
  - 费用计算：佣金 `max(amount×rate, min_commission)`（双向）；印花税 `amount×rate`（仅卖出）；
    过户费 `amount×rate`（双向）。买入总成本=金额+佣金+过户费；卖出净收入=金额−佣金−印花税−过户费。

### 3. `qmtquant/live/replay.py` — 薄回放器（不含任何策略）

- `replay(broker, on_bar) -> ReplayResult`（要求 `broker.quote_source` 为 `ReplayQuoteSource`）：
  逐根循环：①与上一根比较日期，日切则 `broker.roll_day()` ②`broker.quote_source.advance()` 前进、
  `broker.process_pending()` 撮合上一步挂单 ③调用**用户回调** `on_bar(broker, bar)`
  （用户在此写自己的下单逻辑）④记录该根权益。返回 `ReplayResult`（权益曲线、成交、末值）。
- `ReplayResult`（dataclass）：`equity_curve: list[(ts, equity)]`、`trades`、`final_cash`、`final_positions`。

## 成交时点（无未来函数）

用户在 `on_bar(t)`（看到第 t 根**收盘**+历史）下的单，进入挂单队列，在**第 t+1 根**由
`process_pending` 撮合：市价单成交于 t+1 **开盘价**；限价单按 t+1 的 `[low,high]` 盘中撮合。
即"收盘决策、下一根开盘成交"，无未来函数（与 backtrader 默认一致）。

## 数据流

```
DataSource(真实/合成) → DataFrame → ReplayQuoteSource
                                        │ advance() 逐根
   replay() ── 日切→roll_day(T+1解锁) ──┤
              ── process_pending(quote) ── PaperBroker 撮合(A股规则+记账)
              ── on_bar(broker,bar) ────── 用户策略下单 → place_order(入队)
                                        └→ 记录权益曲线 → ReplayResult
```
paper→real：把 `replay`+`ReplayQuoteSource` 换成实时循环、`PaperBroker` 换成 `XtQuantBroker`，
`on_bar` 里的策略代码不变。

## 测试（全部离线、不依赖终端、CI 友好）

- `PaperBroker` 单元测试（用合成/手动 `Quote`，无需策略）：
  - T+1：当日买入的数量当日不可卖；`roll_day()` 后可卖。
  - 涨跌停：last≥涨停 买入被拒；last≤跌停 卖出被拒。
  - 整手：买入 150 股按 100 成交；清仓允许零股卖出。
  - 费用：佣金最低 5 元、卖出含印花税、双向过户费，现金扣减正确。
  - 现金不足：买入超过可用现金被拒。
  - 成交后持仓 size/avg_price 与现金正确。
- 端到端 `replay` 冒烟测试：合成数据 + 一个**平凡假回调**（如"第10根买100、第20根卖"），
  断言权益曲线长度、成交笔数、末值合理。
- 可选实盘数据测试：`QMT_LIVE_TESTS=1` 时用 `XtQuantDataSource` 真实日线跑一遍。

## 未来（v2，本 spec 不做）

- 实时行情订阅驱动（交易时段、收盘结算）。
- `XtQuantBroker` 实盘实现（同一 `Broker` 抽象）；若万联提供券商模拟账户，登录它即得"假钱真API"模拟。
- 如策略需要更多查询能力（查单个持仓/查委托/账户总资产），届时在 `Broker` 抽象上**同时**
  为 `PaperBroker` 与 `XtQuantBroker` 增加，保持无感切换。
