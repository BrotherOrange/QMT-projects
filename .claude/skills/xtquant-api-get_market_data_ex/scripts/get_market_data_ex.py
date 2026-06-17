from datetime import datetime
from xtquant import xtdata
import pandas as pd

# 注意：本机 万联证券版 终端的 xtquant build 要求 start_time/end_time 为【字符串】
# （日线用 '%Y%m%d'，分钟/tick 用 '%Y%m%d%H%M%S'），不接受 datetime 对象，
# 否则报 get_market_data3 incompatible arguments。下面用 fmt() 按周期转字符串。

def fmt(dt, period):
    return dt.strftime('%Y%m%d' if period == '1d' else '%Y%m%d%H%M%S')

# 取1分钟K线
stock = '000001.SZ'
period = '1m'
kline = xtdata.get_market_data_ex(['open', 'close', 'high', 'low', 'volume', 'amount', 'preClose'], [stock], period=period,
                start_time=fmt(datetime(2026, 3, 19, 10), period), end_time=fmt(datetime(2026, 3, 19, 15), period), count=-1
                , dividend_type='none', fill_data=True)

for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.tail())


# 取5分钟K线
stock = '000001.SZ'
period = '5m'
kline = xtdata.get_market_data_ex(['open', 'close', 'high', 'low', 'volume', 'amount', 'preClose'], [stock], period=period,
                start_time=fmt(datetime(2026, 3, 19, 10), period), end_time=fmt(datetime(2026, 3, 19, 15), period), count=-1
                , dividend_type='none', fill_data=True)

for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.tail())


# 取日K（period='1d'）
stock = '000001.SZ'
period = '1d'
kline = xtdata.get_market_data_ex(['open', 'close', 'high', 'low', 'volume', 'amount', 'preClose'], [stock], period=period,
                start_time=fmt(datetime(2026, 3, 1), period), end_time=fmt(datetime(2026, 3, 19), period), count=-1
                , dividend_type='none', fill_data=True)

for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.tail())


# 取tick
stock = '000001.SZ'
period = 'tick'
kline = xtdata.get_market_data_ex([], [stock], period=period,
                start_time=fmt(datetime(2026, 3, 19, 9, 15), period), end_time=fmt(datetime(2026, 3, 19, 15, 0), period), count=-1
                , dividend_type='none', fill_data=True)

for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.head())
    print(df.tail())
