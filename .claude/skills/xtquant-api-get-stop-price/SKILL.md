---
name: xtquant-api-get-stop-price
description: 本技能用于使用xtquant库查询股票的涨跌停价格。通过download_history_data2下载停价数据(period='stoppricedata')，然后使用get_market_data_ex查询涨停价(涨停价)和跌停价(跌停价)。注意：返回的字段名为中文。
---

# 查询涨跌停价格

## 接口说明

查询股票涨跌停价格需要两个步骤：
1. 先使用 `download_history_data2` 下载停价数据（period='stoppricedata'）
2. 再使用 `get_market_data_ex` 查询涨停价和跌停价

## 返回数据结构

`get_market_data_ex` 返回的数据格式为：
```python
{
    '股票代码': DataFrame,  # 包含该股票所有历史停价数据
    ...
}
```

每个 DataFrame 包含以下字段：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `time` | 时间戳（毫秒） | 1776355200000 |
| `涨停价` | 涨停价格 | 12.20 |
| `跌停价` | 跌停价格 | 9.98 |
| `ss` | 状态标记 | 0 |

## 使用示例

### 单股查询涨跌停价

```python
from xtquant import xtdata

# 1. 下载停价数据
stock_code = '000001.SZ'
xtdata.download_history_data(stock_code, period='stoppricedata', start_time='', end_time='')

# 2. 查询涨跌停价（字段名为中文）
data = xtdata.get_market_data_ex(
    field_list=[],
    stock_list=[stock_code],
    period='stoppricedata',
    count=-1
)

df = data[stock_code]
up_price = df['涨停价'].iloc[-1]    # 涨停价（取最新一条）
down_price = df['跌停价'].iloc[-1]  # 跌停价（取最新一条）

print(f"涨停价: {up_price}")
print(f"跌停价: {down_price}")
```

### 批量查询多股涨跌停价

```python
from xtquant import xtdata

# 股票列表
stock_list = ['000001.SZ', '600000.SH', '000002.SZ']

# 1. 批量下载停价数据
xtdata.download_history_data2(
    stock_list=stock_list,
    period='stoppricedata',
    start_time='',
    end_time='',
    callback=lambda x: print(f"下载进度: {x}")
)

# 2. 批量查询涨跌停价（字段名为中文）
data = xtdata.get_market_data_ex(
    field_list=[],
    stock_list=stock_list,
    period='stoppricedata',
    count=-1
)

# 解析结果
for stock in stock_list:
    df = data[stock]
    up_price = df['涨停价'].iloc[-1]    # 最新涨停价
    down_price = df['跌停价'].iloc[-1]  # 最新跌停价
    print(f"{stock} - 涨停价: {up_price}, 跌停价: {down_price}")
```

### 带错误重试的完整示例

```python
import time
from xtquant import xtdata

def get_stop_prices(stock_list, max_retry=3):
    """
    获取股票涨跌停价格
    
    Args:
        stock_list: 股票代码列表
        max_retry: 最大重试次数
    
    Returns:
        dict: {stock_code: {'upPrice': float, 'downPrice': float}}
    """
    result = {}
    
    # 下载数据（带重试）
    for i in range(max_retry):
        try:
            xtdata.download_history_data2(
                stock_list=stock_list,
                period='stoppricedata',
                start_time='',
                end_time=''
            )
            break
        except RuntimeError as e:
            print(f"下载失败，重试 {i+1}/{max_retry}: {e}")
            time.sleep(2)
    
    # 查询数据（字段名为中文）
    data = xtdata.get_market_data_ex(
        field_list=[],
        stock_list=stock_list,
        period='stoppricedata',
        count=-1
    )
    
    # 整理结果
    for stock in stock_list:
        try:
            df = data[stock]
            up_price = float(df['涨停价'].iloc[-1])
            down_price = float(df['跌停价'].iloc[-1])
            result[stock] = {
                'upPrice': up_price,
                'downPrice': down_price
            }
        except Exception as e:
            print(f"解析 {stock} 数据失败: {e}")
            result[stock] = {'upPrice': None, 'downPrice': None}
    
    return result

# 使用示例
stocks = ['000001.SZ', '600000.SH']
prices = get_stop_prices(stocks)
for stock, price_info in prices.items():
    print(f"{stock}: 涨停 {price_info['upPrice']}, 跌停 {price_info['downPrice']}")
```

## 注意事项

1. **必须先下载后查询**：`stoppricedata` 是特殊周期，需要先下载才能查询到数据
2. **实时性**：涨跌停价会随市场变化而更新，建议在使用前重新下载
3. **ST股票**：ST股票的涨跌停幅度为 5%，普通股票为 10%，科创板/创业板为 20%
4. **新股**：新股上市首日涨跌停规则可能不同，需注意特殊情况
