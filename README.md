# qmtquant

一个**自建的统一 Python 量化运行时**：写**一套**策略，换"数据源 + broker"即可在
**回测 / 模拟 / 实盘**之间无感切换。A 股行情/交易经 迅投 xtquant / miniQMT 接入。

```
data (OHLCV 数据源)  ->  runtime (Strategy / 引擎 / 结果)
live/ : Broker 抽象  ->  PaperBroker(本地模拟, A股规则)  |  XtQuantBroker(实盘, v2)
```

- **回测/模拟**：`ReplayFeed`(历史K线) + `PaperBroker`（内存撮合，完整 A 股规则）
- **实盘 (v2)**：`RealtimeFeed`(xtdata 实时) + `XtQuantBroker`(xttrader)
- 策略只依赖 `Strategy` / `Context` 与 `Broker` 抽象 → 切换只换 feed + broker，**策略代码不改**。

> 设计与决策见 `docs/superpowers/specs/2026-06-18-quant-runtime-design.md`
> （为什么不用 backtrader、为什么不用 QMT 原生回测）。

---

## 安装（src-layout，必须先 editable 安装）

### conda（推荐：`qmt-projects-py310` 环境）

```bash
conda env create -f environment.yml
conda activate qmt-projects-py310
pip install -e ".[dev]"          # pyproject 变动后重跑
```

> 用 **Python 3.10**：实盘路径依赖 miniQMT 自带的 `xtquant`，其编译扩展(.pyd)只到 cp311
> （**无 cp312**），故 3.12 无法 import xtquant。纯回测/模拟（合成或已下载的历史数据）不强求。
> 接入 xtquant 见下文"xtquant / miniQMT 接入"。

### venv / pip

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev]"          # 仅 numpy<2 + pandas + pytest，无 backtrader
```

---

## 快速上手：写一套策略，回测/模拟/实盘通用

```python
from qmtquant import Strategy, Context, ReplayFeed, PaperBroker, run, SyntheticDataSource

class MyStrategy(Strategy):
    def on_bar(self, ctx: Context) -> None:
        ma5 = sum(ctx.history(5)) / 5 if len(ctx.history(5)) == 5 else None
        # ... 你的逻辑；下单：ctx.buy(100) / ctx.sell(100) / ctx.broker.place_order(...)

# 回测/模拟：合成数据（无需终端）
df = SyntheticDataSource(n=300, seed=42).get_dataframe("SYNTH")
result = run(MyStrategy(), ReplayFeed(df, "SYNTH"), PaperBroker(cash=100_000))
print(result.metrics)          # total_return / sharpe / max_drawdown / num_trades
print(result.final_cash, result.final_positions)
```

用**真实 A 股数据**回测/模拟（需先按下文接好 xtquant + 终端在运行）：

```python
from qmtquant import XtQuantDataSource, ReplayFeed, PaperBroker, run

df = XtQuantDataSource(period="1d").get_dataframe("000001.SZ")
result = run(MyStrategy(), ReplayFeed(df, "000001.SZ"), PaperBroker(cash=100_000))
```

**将来切实盘 (v2)**：把 `ReplayFeed` 换成 `RealtimeFeed`、`PaperBroker` 换成
`XtQuantBroker(account_id=...)`，`MyStrategy` 一行不改。

### 成交模型 & A 股规则（PaperBroker）

- **成交时点**：第 t 根收盘决策、第 t+1 根开盘成交（无未来函数）。市价单成交于开盘价，
  限价单按当根 `[low, high]` 盘中撮合。
- **A 股规则**（`AShareRules`，可配）：T+1（当日买入当日不可卖）、涨跌停不可成交、整手 100、
  佣金万三·最低 5 元 + 卖出印花税 0.05% + 双向过户费 0.001%。

### CLI 演示

```bash
qmtquant --bars 300 --seed 42        # 合成数据 + 演示买入持有，打印结果摘要
```

---

## 测试

```bash
pytest
```

覆盖：包导入/版本、合成数据生成与校验、`ReplayFeed`、`PaperBroker` 各条 A 股规则
（T+1 / 涨跌停 / 整手 / 费用 / 现金不足拒单 / 限价撮合）、引擎端到端冒烟。
全部**离线、不依赖终端**；可选实盘数据测试用 `QMT_LIVE_TESTS=1` 开启。

---

## 依赖

`pyproject.toml` 仅 `numpy>=1.26,<2` + `pandas>=2.2,<3`（dev 加 `pytest`）。
`numpy` held `<2` 是因为 miniQMT 自带 xtquant 的 .pyd 针对 numpy 1.x C-API 编译。
**不再依赖 backtrader / matplotlib**。

---

## xtquant / miniQMT 接入（2026-06-18 实测可用）

迅投 miniQMT 终端已安装；`xtquant` 的数据端(`xtdata`)与交易通道(`xttrader.connect()`)
均已对真实终端验证可用。

**环境要求 — 仅 Python 3.10/3.11。** 终端自带 `xtquant` 的 `.pyd` 只到 cp311（无 cp312）。

**让 `from xtquant import xtdata` 在本环境可用**（`xtquant` 不是 pip 包，在终端安装目录内）：

```bash
conda activate qmt-projects-py310
python scripts/setup_xtquant.py          # 或： --bin "<你的QMT路径>\bin.x64"
```

该脚本在 env 的 site-packages 建一个**目录联接(junction)** `xtquant` 指向终端自带的
`xtquant`——只暴露 xtquant 一个包（不污染本环境；实测连 `xttrader.connect()` 都无需额外
`add_dll_directory`）。终端移动/重装后重跑即可（NTFS 上无需管理员；失败自动回退为复制）。

**已验证可用**：股票列表/板块、`get_instrument_detail`、`download_history_data` +
`get_market_data_ex`(1m/5m/1d/tick)、`download_history_data2`(带 callback)、财务数据。

**本终端 build 的坑**（相关 skill 脚本/文档已据此修正）：

- 无 `incrementally` 参数（`download_history_data`/`download_history_data2`/`download_financial_data`），勿传。
- 无 `get_instrument_detail_list`，请循环调用 `get_instrument_detail`。
- `download_history_data2` 不传 `callback` 会永久阻塞。
- `download_*` / `get_market_data_ex` 的日期参数必须是**字符串**（`%Y%m%d` 或 `%Y%m%d%H%M%S`），不接受 datetime。
- `stoppricedata`(涨跌停)、`buysellvol`(内外盘) 周期本 build **不支持**；涨跌停改用
  `get_instrument_detail` 的 `UpStopPrice`/`DownStopPrice`。

配置见 `.env.example`（`QMTQUANT_XT_ACCOUNT_ID` / `QMTQUANT_MINI_QMT_PATH` /
`QMTQUANT_QMT_BIN_PATH`）。`.env` 已被 git 忽略；**密码绝不入库**（只在 QMT 客户端手输）。

---

## 路线图（v2）

- `RealtimeFeed`(xtdata 实时订阅) + `XtQuantBroker`(xttrader 实盘下单)，同一 `Strategy` 跑实盘；
  券商模拟账户(假钱真 API)亦走 `XtQuantBroker`。
- 多标的/选股域、更精细的限价撮合、结果绘图、参数扫描。
- `live/xtquant_broker.py` 当前为 stub（`NotImplementedError`），实盘接入时实现
  `xtquant.xttrader`（登录、`order_stock`、`cancel_order_stock`、`query_stock_positions`、`query_stock_asset`）。
