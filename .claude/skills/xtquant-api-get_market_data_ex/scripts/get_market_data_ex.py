from datetime import datetime
from xtquant import xtdata
import pandas as pd

# 取1分钟K线
stock = '000001.SZ'
period = '1m'
start_time = datetime(2026,3,19,10)
end_time = datetime(2026,3,19,15)

kline = xtdata.get_market_data_ex(['open', 'close', 'high', 'low', 'volume', 'amount','preClose'], [stock], period=period,
                start_time = start_time, end_time = end_time, count = -1
                , dividend_type = 'none', fill_data = True)
                
for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.tail())


# 取5分钟K线
stock = '000001.SZ'
period = '5m'
start_time = datetime(2026,3,19,10)
end_time = datetime(2026,3,19,15)

kline = xtdata.get_market_data_ex(['open', 'close', 'high', 'low', 'volume', 'amount','preClose'], [stock], period=period,
                start_time = start_time, end_time = end_time, count = -1
                , dividend_type = 'none', fill_data = True)
                
for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.tail())


# 取日K
stock = '000001.SZ'
period = '5m'
start_time = datetime(2026,3,1)
end_time = datetime(2026,3,19)

kline = xtdata.get_market_data_ex(['open', 'close', 'high', 'low', 'volume', 'amount','preClose'], [stock], period=period,
                start_time = start_time, end_time = end_time, count = -1
                , dividend_type = 'none', fill_data = True)
                
for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.tail())


# 取tick
stock = '000001.SZ'
period = 'tick'
start_time = datetime(2026,3,19,9,15)
end_time = datetime(2026,3,19,15,0)

kline = xtdata.get_market_data_ex([], [stock], period=period,
                start_time = start_time, end_time = end_time, count = -1
                , dividend_type = 'none', fill_data = True)
                
for s, df in kline.items():
    df['code'] = s
    df['date'] = pd.to_datetime(df.index)
    print(df.head())
    print(df.tail())