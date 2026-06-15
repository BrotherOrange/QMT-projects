

import time
from datetime import datetime
from xtquant import xtdata

# 下载财务数据
stock = '000001.SZ'
start_time = datetime(2000,1,1)
end_time = datetime(2038,1,1)

xtdata.download_financial_data([stock], [], start_time.strftime('%Y%m%d'), end_time.strftime('%Y%m%d'), incrementally=False)


# 下载财务数据
stock = '000001.SZ'
start_time = datetime(2000,1,1)
end_time = datetime(2038,1,1)

while 1:
    try:
        xtdata.download_financial_data([stock], [], start_time.strftime('%Y%m%d'), end_time.strftime('%Y%m%d'), incrementally=False)
        break
    except RuntimeError as e:
        print('download error %s will retry', e)
        time.sleep(10)


# 下载财务数据
stock = '000001.SZ'
start_time = datetime(2000,1,1)
end_time = datetime(2038,1,1)

xtdata.download_financial_data2([stock], [], start_time.strftime('%Y%m%d'), end_time.strftime('%Y%m%d'), callback=lambda x: print(x))




# 下载财务数据
stock = '000001.SZ'
start_time = datetime(2000,1,1)
end_time = datetime(2038,1,1)

while 1:
    try:
        xtdata.download_financial_data2([stock], [], start_time.strftime('%Y%m%d'), end_time.strftime('%Y%m%d'), callback=lambda x: print(x))
        break
    except RuntimeError as e:
        print('download error %s will retry', e)
        time.sleep(10)
