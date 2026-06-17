# EXAMPLES

> ⚠️ 兼容性（本机 `万联证券版` 终端实测，2026-06-18）：本终端的 xtquant build **不支持
> `incrementally` 参数**（仅更新版 xtquant 有），下方示例已移除它。另外 `download_history_data2`
> **必须带 `callback`**，否则调用会永久阻塞。Python 须为 3.10/3.11（无 cp312）。

# 单股下载
```python
from datetime import datetime
from xtquant import xtdata
from typing import List, Any


stock = '000001.SZ'
period = '1d'
start_time = datetime(2026,1,1).strftime('%Y%m%d')  # 本机终端要求字符串日期，不接受 datetime
end_time = datetime(2026,3,19).strftime('%Y%m%d')
# 单股下载
down_result = xtdata.download_history_data(stock, period, start_time, end_time)
print(down_result)
```

# 单股下载-报错重试
```python
import time
from datetime import datetime
from xtquant import xtdata
from typing import List, Any

stock = '000001.SZ'
period = '1d'
start_time = datetime(2026,1,1).strftime('%Y%m%d')  # 本机终端要求字符串日期，不接受 datetime
end_time = datetime(2026,3,19).strftime('%Y%m%d')

while 1:
    try:
        # 下载过程可能会有异常，用while True 和try except增加重试机制
        down_result = xtdata.download_history_data(stock, period, start_time, end_time)
        print(down_result)
        break
    except RuntimeError as e:
        print('download error %s will retry', e)
        time.sleep(10)
```



# 多股下载
```python
from datetime import datetime
from xtquant import xtdata
from typing import List, Any


stock = '000001.SZ'
period = '1d'
start_time = datetime(2026,1,1).strftime('%Y%m%d')  # 本机终端要求字符串日期，不接受 datetime
end_time = datetime(2026,3,19).strftime('%Y%m%d')
# 多股下载
down_result = xtdata.download_history_data2([stock], period, start_time, end_time, callback=lambda x: print(x))
print(down_result)
```

# 多股下载-报错重试
```python
import time
from datetime import datetime
from xtquant import xtdata
from typing import List, Any

stock = '000001.SZ'
period = '1d'
start_time = datetime(2026,1,1).strftime('%Y%m%d')  # 本机终端要求字符串日期，不接受 datetime
end_time = datetime(2026,3,19).strftime('%Y%m%d')

while 1:
    try:
        # 下载过程可能会有异常，用while True 和try except增加重试机制
        down_result = xtdata.download_history_data2([stock], period, start_time, end_time, callback=lambda x: print(x))
        print(down_result)
        break
    except RuntimeError as e:
        print('download error %s will retry', e)
        time.sleep(10)
```
