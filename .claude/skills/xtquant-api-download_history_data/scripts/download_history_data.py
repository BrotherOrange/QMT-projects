

import time
from datetime import datetime
from xtquant import xtdata
from typing import List, Any

stock = '000001.SZ'
period = '1d'
# 注意：本机终端的 download_history_data 只接受字符串日期(YYYYMMDD)，不接受 datetime 对象，
# 故用 strftime 转字符串（datetime 对象会报 supply_history_data incompatible arguments）。
start_time = datetime(2026,1,1).strftime('%Y%m%d')
end_time = datetime(2026,3,19).strftime('%Y%m%d')

while 1:
    try:
        # 下载过程可能会有异常，用while True 和try except增加重试机制
        # 注意：本机 万联证券版 终端的 xtquant build 不支持 incrementally 参数（更新版才有），不要传。
        down_result = xtdata.download_history_data(stock, period, start_time, end_time)
        print(down_result)
        break
    except RuntimeError as e:
        print('download error %s will retry', e)
        time.sleep(10)