# xtquant get_instrument_detail 技能

## 简介

本技能用于指导如何使用 xtquant 的 `get_instrument_detail` 函数获取股票/期货合约详细信息如当日涨跌价、当日流通股本、总股本、股票名称等。

## 函数说明

### get_instrument_detail(stock_code, iscomplete=False)

获取单个合约的详细信息。

**参数：**
- `stock_code` (str): 股票代码，例如 `"600000.SH"`
- `iscomplete` (bool): 是否返回完整信息，默认为 `False`
  - `False`: 返回部分常用字段
  - `True`: 返回完整字段信息，包含扩展信息

**返回值：**
返回一个字典，包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| ExchangeID | str | 合约市场代码 |
| InstrumentID | str | 合约代码 |
| InstrumentName | str | 合约名称 |
| ProductID | str | 合约的品种ID(期货) |
| ProductName | str | 合约的品种名称(期货) |
| ProductType | str | 合约的类型 |
| ExchangeCode | str | 交易所代码 |
| UniCode | str | 统一规则代码 |
| CreateDate | str | 上市日期(期货) |
| OpenDate | str | IPO日期(股票) |
| ExpireDate | str | 退市日或者到期日 |
| PreClose | double | 前收盘价格 |
| SettlementPrice | double | 前结算价格 |
| UpStopPrice | double | 当日涨停价 |
| DownStopPrice | double | 当日跌停价 |
| FloatVolume | double | 流通股本 |
| TotalVolume | double | 总股本 |
| LongMarginRatio | double | 多头保证金率 |
| ShortMarginRatio | double | 空头保证金率 |
| PriceTick | double | 最小变价单位 |
| VolumeMultiple | int | 合约乘数(对期货以外的品种，默认是1) |
| MainContract | int | 主力合约标记 |
| LastVolume | int | 昨日持仓量 |
| InstrumentStatus | int | 合约停牌状态 |
| IsTrading | bool | 合约是否可交易 |
| IsRecent | bool | 是否是近月合约 |

当 `iscomplete=True` 时，还会包含以下扩展字段：
- ProductTradeQuota
- ContractTradeQuota
- ProductOpenInterestQuota
- ContractOpenInterestQuota

**返回值：** 如果查询失败，返回 `None`

---

### get_instrument_detail_list(stock_list, iscomplete=False)

批量获取多个合约的详细信息。

**参数：**
- `stock_list` (list): 股票代码列表，例如 `["000001.SZ", "600000.SH"]`
- `iscomplete` (bool): 是否返回完整信息，默认为 `False`

**返回值：**
返回一个字典，键为股票代码，值为对应的合约信息字典：
```python
{
    "000001.SZ": { ... },
    "600000.SH": { ... }
}
```

## 使用示例

### 示例1：获取单只股票信息

```python
from xtquant import xtdata

# 获取单只股票信息
stock_code = "600000.SH"
info = xtdata.get_instrument_detail(stock_code)

if info:
    print(f"股票名称: {info['InstrumentName']}")
    print(f"交易所代码: {info['ExchangeID']}")
    print(f"总股本: {info['TotalVolume']}")
    print(f"流通股本: {info['FloatVolume']}")
    print(f"涨停价: {info['UpStopPrice']}")
    print(f"跌停价: {info['DownStopPrice']}")
else:
    print(f"未找到股票 {stock_code} 的信息")
```

### 示例2：获取完整信息

```python
from xtquant import xtdata

# 获取完整信息（包含扩展字段）
stock_code = "000001.SZ"
info = xtdata.get_instrument_detail(stock_code, iscomplete=True)

if info:
    # 打印所有字段
    for key, value in info.items():
        print(f"{key}: {value}")
```

### 示例3：批量获取多只股票信息

```python
from xtquant import xtdata

# 批量获取
stock_list = ["000001.SZ", "600000.SH", "000002.SZ"]
info_dict = xtdata.get_instrument_detail_list(stock_list)

for stock_code, info in info_dict.items():
    if info:
        print(f"\n股票代码: {stock_code}")
        print(f"  名称: {info['InstrumentName']}")
        print(f"  总股本: {info['TotalVolume']}")
        print(f"  流通股本: {info['FloatVolume']}")
```

### 示例4：筛选可交易的股票

```python
from xtquant import xtdata

# 获取股票列表并筛选可交易的
stock_list = xtdata.get_stock_list_in_sector("沪深A股")
trading_stocks = []

for stock_code in stock_list[:100]:  # 取前100只测试
    info = xtdata.get_instrument_detail(stock_code)
    if info and info.get('IsTrading', False):
        trading_stocks.append(stock_code)

print(f"可交易股票数量: {len(trading_stocks)}")
```

### 示例5：获取股票IPO日期

```python
from xtquant import xtdata

# 获取IPO日期
stock_code = "600000.SH"
info = xtdata.get_instrument_detail(stock_code)

if info:
    ipo_date = info.get('OpenDate')
    if ipo_date:
        print(f"{stock_code} 的IPO日期: {ipo_date}")
    else:
        print(f"{stock_code} 没有IPO日期信息")
```

## 注意事项

1. **股票代码格式**：股票代码需要包含交易所后缀，如 `"600000.SH"`（上海）、`"000001.SZ"`（深圳）
2. **数据时效性**：合约信息是实时数据，反映当前市场状态
3. **返回值检查**：函数可能返回 `None`，使用前需要进行判空处理
4. **性能考虑**：批量查询建议使用 `get_instrument_detail_list` 而非循环调用 `get_instrument_detail`

## 相关API

- `xtdata.get_stock_list_in_sector()` - 获取板块股票列表
- `xtdata.get_full_tick()` - 获取全推行情数据
