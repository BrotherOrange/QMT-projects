import time
from datetime import datetime
from xtquant import xtdata
from typing import List, Any

stock = '000001.SZ'
period = '1d'
start_time = datetime(2026,1,1)
end_time = datetime(2026,3,19)

while 1:
    try:
        # 下载过程可能会有异常，用while True 和try except增加重试机制
        down_result = xtdata.download_history_data2([stock], period, start_time, end_time, callback=lambda x: print(x),incrementally=False)
        print(down_result)
        break
    except RuntimeError as e:
        print('download error %s will retry', e)
        time.sleep(10)