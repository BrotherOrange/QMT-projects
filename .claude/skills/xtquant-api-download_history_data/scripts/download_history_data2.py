import time
from datetime import datetime
from xtquant import xtdata
from typing import List, Any

stock = '000001.SZ'
period = '1d'
# 注意：本机终端只接受字符串日期(YYYYMMDD)，不接受 datetime 对象，故用 strftime 转字符串。
start_time = datetime(2026,1,1).strftime('%Y%m%d')
end_time = datetime(2026,3,19).strftime('%Y%m%d')

while 1:
    try:
        # 下载过程可能会有异常，用while True 和try except增加重试机制
        # 注意：本机终端 build 不支持 incrementally；download_history_data2 必须带 callback，否则会永久阻塞。
        down_result = xtdata.download_history_data2([stock], period, start_time, end_time, callback=lambda x: print(x))
        print(down_result)
        break
    except RuntimeError as e:
        print('download error %s will retry', e)
        time.sleep(10)