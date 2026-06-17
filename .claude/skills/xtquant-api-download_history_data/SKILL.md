---
name: xtquant-api-download-kline
description: 本技能用于使用xtquant库(原生python接口)的xtdata模块下载历史K线，支持多种时间周期，周期包括日线(1d)、1分钟(1m)和5分钟(5m)和tick。

---
For better usage,see [REFERENCE.md]. For examples, see [EXAMPLES.md].

> ⚠️ 本机终端兼容性（万联证券版，2026-06-18 实测）：
> - 本终端 xtquant build **不支持 `incrementally` 参数**（下文签名里的 `incrementally` 仅更新版 xtquant 有）。调用 `download_history_data` / `download_history_data2` 时**不要传 `incrementally`**，否则报 `TypeError`。脚本与示例已据此修正。
> - `download_history_data2` **必须带 `callback`**，否则会永久阻塞。
> - `start_time` / `end_time` 必须是**字符串**（`'%Y%m%d'` 或 `'%Y%m%d%H%M%S'`），**不接受 `datetime` 对象**（否则报 `supply_history_data incompatible arguments`）。脚本已用 `strftime` 转换。
> - 运行环境须为 Python 3.10/3.11（本终端 xtquant 无 cp312，详见项目 README 的 xtquant 接入说明）。

关键字： 下载k线， 下载分笔数据，下载历史行情，下载行情

Run the helper script:

python scripts/download_history_data.py,scripts/download_history_data2.py

下载接口有两个接口 分别是
1、download_history_data(stock_code, period, start_time='', end_time='', incrementally = None)
2、download_history_data2(stock_list, period, start_time='', end_time='', callback=None,incrementally = None)

> # 1、函数说明 download_history_data(stock_code, period, start_time='', end_time='', incrementally = None)
> - 释义
>     + 补充历史行情数据
> - 参数
>     + stock_code - string 合约代码
>     + period - string 周期
>     + start_time - string|datetime 起始时间
>     + end_time - string|datetime 结束时间
>     + incrementally - 是否增量下载
>         - bool - 是否增量下载
>         - None - 使用start_time控制，start_time为空则增量下载，增量下载时会从本地最后一条数据往后下载
> 
> 同步接口，补充数据完成后返回


> # 2、函数说明 download_history_data2(stock_list, period, start_time='', end_time='', callback=None, incrementally=None)
> 
> - 释义
>     + 补充历史行情数据，批量版本
> - 参数
> 
>     + stock_list - list 合约列表
>     + period - string 周期
>     + start_time - string|datetime 起始时间
> 
>     + end_time - string|datetime 结束时间
> 
>     + callback - func 回调函数
> 
>     + 参数为进度信息dict
> 
>         + total - 总下载个数
>         + finished - 已完成个数
>         + stockcode - 本地下载完成的合约代码
>         + message - 本次信息
> - 同步接口，补充数据完成后返回
# 下载历史K线数据技巧

> - incrementally=True为增量下载，注意这个增量机制不会下载本地中间日期缺失的数据，只会从本地最新一天开始下载，比如本地已经下载的数据日期为：
> 2026-01-01、2026-01-03、2026-01-09， 今天日期是2026-01-13，当选择增量下载时，会从2026-01-10开始下载（即中间2026-01-02、2026-01-04-2026-01-08的数> 据不会下载），想要下载蹭缺失的日期，需要incrementally=False 且start_time和end_time覆盖缺失的日期
> - period为tick时（即下载分笔时）建议按天下载，即for循环遍历要下载的区间，start_time和end_time传同一天，
> 下载后的数据会以私有协议保存成本地文件，需要用xtdata.get_market_data_ex接口查询
> 
> 
> - download_history_data - 下载指定合约代码指定周期对应时间范围的行情数据提示
> 
>     - QMT提供的行情数据中，基础周期包含 tick 1m 5m 1d，这些是实际用于存储的周期 其他周期为合成周期，以基础周期合成得到
> 
>     - 合成周期
> 
>         - 3m， 由1m线合成
>         - 10m, 15m, 30m, 60m, 2h, 3h, 4h 由5分钟线合成
>         - 2d(2日线), 3d(3日线), 5d(5日线), 1w（周线）, 1mon（月线）, 1q(季线), 1hy(半年线), 1y（年线） 由日线数据合成
>         - 获取合成周期时
> 
> - 如果取历史，需要下载历史的基础周期（如取15m需要下载5m）
> - 如果取实时，可以直接订阅原始周期（如直接订阅15m）
> - 如果同时用到基础周期和合成周期，只需要下载基础周期,例如同时使用5m和15m，因为15m也是由5m合成，所以只需要下载一次5m的数据即可