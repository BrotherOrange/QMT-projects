# xtdata.get_market_data_ex 函数说明

## 函数功能

获取指定证券在给定周期内的历史行情或逐笔/Level2等扩展数据，并按字段组织为 `pd.DataFrame` 返回。

## 函数签名

```python
def get_market_data_ex(
    field_list=[],
    stock_list=[],
    period='1d',
    start_time='',
    end_time='',
    count=-1,
    dividend_type='none',
    fill_data=True
) -> dict[str, pd.DataFrame]
```

## 使用示例

```python
from xtquant import xtdata

data = xtdata.get_market_data_ex(
    field_list=["close", "volume"],          # 需要的字段
    stock_list=["000001.SZ", "600000.SH"],   # 标的列表
    period="1d",                             # 日线
    start_time="20200101",                   # 起始日期
    end_time="20201231",                     # 结束日期
    dividend_type="front",                   # 前复权
    fill_data=True,                          # 缺失数据前值填充
)

# 访问某个字段的数据，例如收盘价
close_df = data["close"]
print(close_df.head())
```

## 参数详解

### field_list

行情数据字段列表，`[]` 表示全部字段。

**K线可选字段：**

| 字段 | 说明 |
|------|------|
| `time` | 时间戳 |
| `open` | 开盘价 |
| `high` | 最高价 |
| `low` | 最低价 |
| `close` | 收盘价 |
| `volume` | 成交量 |
| `amount` | 成交额 |
| `settle` | 今结算 |
| `openInterest` | 持仓量 |
| `preClose` | 前收 |

**分笔可选字段：**

| 字段 | 说明 |
|------|------|
| `time` | 时间戳 |
| `lastPrice` | 最新价 |
| `open` | 开盘价 |
| `high` | 最高价 |
| `low` | 最低价 |
| `lastClose` | 前收盘价 |
| `amount` | 成交总额 |
| `volume` | 成交总量 |
| `pvolume` | 原始成交总量 |
| `stockStatus` | 证券状态 |
| `openInt` | 持仓量 |
| `lastSettlementPrice` | 前结算 |
| `askPrice1` ~ `askPrice5` | 卖一价 ~ 卖五价 |
| `bidPrice1` ~ `bidPrice5` | 买一价 ~ 买五价 |
| `askVol1` ~ `askVol5` | 卖一量 ~ 卖五量 |
| `bidVol1` ~ `bidVol5` | 买一量 ~ 买五量 |

### stock_list

股票代码列表，例如 `["000001.SZ", "600000.SH"]`。

### period

数据周期，可选值：

| 周期值 | 说明 |
|--------|------|
| `tick` | 分笔数据 |
| `1m` / `5m` / `15m` | 分钟线 |
| `1d` | 日线 |
| `l2quote` | Level2行情快照 |
| `l2quoteaux` | Level2行情快照补充 |
| `l2order` | Level2逐笔委托 |
| `l2transaction` | Level2逐笔成交 |
| `l2transactioncount` | Level2大单统计 |
| `l2orderqueue` | Level2委买委卖队列 |
| `transactioncount1m` | Level1逐笔成交统计一分钟 |
| `transactioncount1d` | Level1逐笔成交统计日线 |
| `warehousereceipt` | 期货仓单 |
| `futureholderrank` | 期货席位 |
| `interactiveqa` | 互动问答 |

### start_time
string|datetime
起始时间，格式如 `"20200101"` 或 `"20200101093000"`。

### end_time
string|datetime
结束时间，格式如 `"20201231"` 或 `"20201231150000"`。

### count

数量，`-1` 表示全部，`n` 表示从结束时间向前数 n 个。

### dividend_type

除权类型，可选值：

| 类型值 | 说明 |
|--------|------|
| `none` | 不复权 |
| `front` | 前复权 |
| `back` | 后复权 |
| `front_ratio` | 等比前复权 |
| `back_ratio` | 等比后复权 |

### fill_data

对齐时间戳时是否填充数据，仅对K线有效，分笔周期不对齐时间戳。

- `True`：以缺失数据的前一条数据填充
  - `open`、`high`、`low`、`close` 为前一条数据的 `close`
  - `amount`、`volume` 为 0
  - `settle`、`openInterest` 和前一条数据相同
- `False`：缺失数据所有字段填 `NaN`

## 返回值

返回数据集，格式为 `{field1: DataFrame1, field2: DataFrame2, ...}`：

- `field1`, `field2`, ...：数据字段
- `DataFrame1`, `DataFrame2`, ...：`pd.DataFrame` 字段对应的数据，各字段维度相同，index 为 `stock_list`，columns 为 `time_list`
