---
name: xtquant-api-get-buysellvol
description: 本技能用于使用xtquant库查询股票的内外盘数据（主动买卖量）。通过download_history_data2下载内外盘数据(period='buysellvol')，然后使用get_market_data_ex查询主动买入量(buyVol)、主动卖出量(sellVol)、委买委卖量等数据。
---

# 查询内外盘数据（主动买卖量）

## 接口说明

查询股票内外盘数据需要两个步骤：
1. 先使用 `download_history_data2` 下载内外盘数据（period='buysellvol'）
2. 再使用 `get_market_data_ex` 查询主动买入量、主动卖出量等数据

## 返回数据结构

`get_market_data_ex` 返回的数据格式为：
```python
{
    '股票代码': DataFrame,  # 包含该股票所有历史内外盘数据
    ...
}
```

每个 DataFrame 包含以下字段：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `time` | 时间戳（毫秒） | 1504627200000 |
| `buyVol` | 主动买入量（外盘） | 1250000 |
| `sellVol` | 主动卖出量（内盘） | 980000 |
| `bidVolTotal` | 委买总量 | 5000000 |
| `bidPriceAvg` | 委买均价 | 12.35 |
| `askVolTotal` | 委卖总量 | 4500000 |
| `askPriceAvg` | 委卖均价 | 12.38 |
| `sbv` | 小单买入量 | 320000 |
| `sav` | 小单卖出量 | 280000 |
| `transNum` | 成交笔数 | 15234 |

## 数据字段详解

### 内外盘数据

| 字段 | 说明 | 分析用途 |
|------|------|----------|
| `buyVol` | 主动买入量（外盘）| 反映买方积极性 |
| `sellVol` | 主动卖出量（内盘）| 反映卖方积极性 |

**内外盘比例分析：**
- 外盘 > 内盘：买方力量强，看多情绪浓厚
- 外盘 < 内盘：卖方力量强，看空情绪浓厚
- 外盘 ≈ 内盘：买卖双方力量均衡

### 委买委卖数据

| 字段 | 说明 | 分析用途 |
|------|------|----------|
| `bidVolTotal` | 委买总量（买盘挂单总量）| 反映买方承接意愿 |
| `askVolTotal` | 委卖总量（卖盘挂单总量）| 反映卖方抛压大小 |
| `bidPriceAvg` | 委买均价 | 买方愿意接受的平均价格 |
| `askPriceAvg` | 委卖均价 | 卖方愿意接受的平均价格 |

**委比分析：**
```
委比 = (委买总量 - 委卖总量) / (委买总量 + 委卖总量) × 100%
```
- 委比 > 0：买盘强于卖盘
- 委比 < 0：卖盘强于买盘

### 小单数据

| 字段 | 说明 |
|------|------|
| `sbv` | 小单买入量（Small Buy Volume）|
| `sav` | 小单卖出量（Small Ask Volume）|

小单通常代表散户交易行为，可用于分析散户情绪。

## 使用示例

### 单股查询内外盘数据

```python
from xtquant import xtdata

# 1. 下载内外盘数据
stock_code = '000001.SZ'
xtdata.download_history_data(stock_code, period='buysellvol', start_time='', end_time='')

# 2. 查询内外盘数据
data = xtdata.get_market_data_ex(
    field_list=[],
    stock_list=[stock_code],
    period='buysellvol',
    count=-1
)

# 3. 解析结果
df = data[stock_code]
latest = df.iloc[-1]  # 取最新一天数据

buy_vol = latest['buyVol']      # 主动买入量（外盘）
sell_vol = latest['sellVol']    # 主动卖出量（内盘）
total_vol = buy_vol + sell_vol  # 总成交量

# 计算内外盘比例
buy_ratio = buy_vol / total_vol * 100 if total_vol > 0 else 0
sell_ratio = sell_vol / total_vol * 100 if total_vol > 0 else 0

print(f"主动买入量: {buy_vol:,.0f} ({buy_ratio:.2f}%)")
print(f"主动卖出量: {sell_vol:,.0f} ({sell_ratio:.2f}%)")
print(f"市场情绪: {'看多' if buy_ratio > 55 else ('看空' if sell_ratio > 55 else '中性')}")
```

### 批量查询多股内外盘数据

```python
from xtquant import xtdata

# 股票列表
stock_list = ['000001.SZ', '600000.SH', '000002.SZ']

# 1. 批量下载内外盘数据
xtdata.download_history_data2(
    stock_list=stock_list,
    period='buysellvol',
    start_time='',
    end_time='',
    callback=lambda x: print(f"下载进度: {x}")
)

# 2. 批量查询内外盘数据
data = xtdata.get_market_data_ex(
    field_list=[],
    stock_list=stock_list,
    period='buysellvol',
    count=-1
)

# 3. 解析结果
for stock in stock_list:
    df = data[stock]
    latest = df.iloc[-1]
    
    buy_vol = latest['buyVol']
    sell_vol = latest['sellVol']
    total_vol = buy_vol + sell_vol
    
    if total_vol > 0:
        buy_ratio = buy_vol / total_vol * 100
        sentiment = "看多" if buy_ratio > 55 else ("看空" if buy_ratio < 45 else "中性")
    else:
        sentiment = "无数据"
    
    print(f"{stock} - 外盘: {buy_vol:,.0f}, 内盘: {sell_vol:,.0f}, 情绪: {sentiment}")
```

### 完整分析示例

```python
import pandas as pd
from xtquant import xtdata

def analyze_buysellvol(stock_code):
    """
    分析股票内外盘数据
    
    Args:
        stock_code: 股票代码，如 '000001.SZ'
    
    Returns:
        dict: 分析结果
    """
    # 下载数据
    xtdata.download_history_data(stock_code, period='buysellvol', start_time='', end_time='')
    
    # 查询数据
    data = xtdata.get_market_data_ex(
        field_list=[],
        stock_list=[stock_code],
        period='buysellvol',
        count=-1
    )
    
    df = data[stock_code]
    latest = df.iloc[-1]
    
    # 内外盘分析
    buy_vol = latest['buyVol']
    sell_vol = latest['sellVol']
    total_vol = buy_vol + sell_vol
    
    buy_ratio = buy_vol / total_vol * 100 if total_vol > 0 else 0
    sell_ratio = sell_vol / total_vol * 100 if total_vol > 0 else 0
    
    # 委买委卖分析
    bid_vol = latest['bidVolTotal']
    ask_vol = latest['askVolTotal']
    total_bid_ask = bid_vol + ask_vol
    
    wei_bi = (bid_vol - ask_vol) / total_bid_ask * 100 if total_bid_ask > 0 else 0
    
    result = {
        'stock_code': stock_code,
        'date': latest.name,
        
        # 内外盘数据
        'buyVol': buy_vol,              # 主动买入量（外盘）
        'sellVol': sell_vol,            # 主动卖出量（内盘）
        'totalVol': total_vol,          # 总成交量
        'buyRatio': buy_ratio,          # 买入占比(%)
        'sellRatio': sell_ratio,        # 卖出占比(%)
        
        # 委买委卖数据
        'bidVolTotal': bid_vol,         # 委买总量
        'askVolTotal': ask_vol,         # 委卖总量
        'bidPriceAvg': latest['bidPriceAvg'],  # 委买均价
        'askPriceAvg': latest['askPriceAvg'],  # 委卖均价
        'weiBi': wei_bi,                # 委比(%)
        
        # 小单数据
        'sbv': latest['sbv'],           # 小单买入量
        'sav': latest['sav'],           # 小单卖出量
        
        # 其他
        'transNum': latest['transNum'], # 成交笔数
        
        # 情绪判断
        'sentiment': '看多' if buy_ratio > 55 else ('看空' if sell_ratio > 55 else '中性'),
        'weiBiSentiment': '买盘强' if wei_bi > 0 else '卖盘强'
    }
    
    return result


# 使用示例
result = analyze_buysellvol('000001.SZ')
print(f"股票: {result['stock_code']}")
print(f"日期: {result['date']}")
print(f"外盘/内盘: {result['buyVol']:,.0f} / {result['sellVol']:,.0f}")
print(f"外盘占比: {result['buyRatio']:.2f}%")
print(f"市场情绪: {result['sentiment']}")
print(f"委比: {result['weiBi']:.2f}% ({result['weiBiSentiment']})")
```

## 注意事项

1. **必须先下载后查询**：`buysellvol` 是特殊周期，需要先下载才能查询到数据
2. **数据频率**：内外盘数据通常是日级的，每个交易日一条记录
3. **实时性**：数据会随市场变化而更新，建议在使用前重新下载
4. **数据起始时间**：不同股票的数据起始时间可能不同，最早可追溯到2017年左右
5. **field_list 传空列表**：获取内外盘数据时，`field_list` 参数需要传空列表 `[]`

## 分析技巧

### 1. 内外盘比例判断趋势

```python
def judge_trend_by_buysellvol(buy_ratio):
    """根据外盘比例判断趋势"""
    if buy_ratio > 60:
        return "强势看多"
    elif buy_ratio > 55:
        return "看多"
    elif buy_ratio > 45:
        return "中性"
    elif buy_ratio > 40:
        return "看空"
    else:
        return "强势看空"
```

### 2. 委比判断即时买卖意愿

```python
def judge_weibi(bid_vol, ask_vol):
    """根据委买委卖量判断买卖意愿"""
    total = bid_vol + ask_vol
    if total == 0:
        return "无数据", 0
    
    wei_bi = (bid_vol - ask_vol) / total * 100
    
    if wei_bi > 20:
        return "买盘很强", wei_bi
    elif wei_bi > 10:
        return "买盘较强", wei_bi
    elif wei_bi > -10:
        return "买卖均衡", wei_bi
    elif wei_bi > -20:
        return "卖盘较强", wei_bi
    else:
        return "卖盘很强", wei_bi
```

### 3. 结合小单分析散户情绪

```python
def analyze_retail_sentiment(sbv, sav):
    """分析散户情绪（小单买卖量）"""
    total = sbv + sav
    if total == 0:
        return "无数据", 0
    
    retail_buy_ratio = sbv / total * 100
    
    if retail_buy_ratio > 60:
        return "散户积极买入", retail_buy_ratio
    elif retail_buy_ratio > 55:
        return "散户买入较多", retail_buy_ratio
    elif retail_buy_ratio > 45:
        return "散户情绪中性", retail_buy_ratio
    elif retail_buy_ratio > 40:
        return "散户卖出较多", retail_buy_ratio
    else:
        return "散户积极卖出", retail_buy_ratio
```
