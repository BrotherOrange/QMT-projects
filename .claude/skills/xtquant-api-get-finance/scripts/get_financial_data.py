

import time
from datetime import datetime
from xtquant import xtdata




# 下载财务数据
stock = '000001.SZ'
start_time = datetime(2000,1,1)
end_time = datetime(2038,1,1)
data = xtdata.get_financial_data([stock], [], start_time.strftime('%Y%m%d'), end_time.strftime('%Y%m%d'), report_type='report_time')

print(data)

