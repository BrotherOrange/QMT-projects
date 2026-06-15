---
name: 获取财务数据
description: 获取A股财务数据，取查询资产负债表、利润表、现金流量表、股本表、股东数、十大股东、十大流通股东、每股指标时调用该函数

---



> # tips:
> - 获取财务数据接口不会直接向行情服务器发起获取请求，需要先下载财务数据
> - **下载财务数据请使用 `xtdata.download_financial_data` 接口，不要使用 `download_history_data`**
> - `download_history_data` 是下载K线数据的，不包括财务数据
> - 下载财务数据示例：
>   ```python
>   xtdata.download_financial_data(
>       stock_list=['920455.BJ'],
>       table_list=['Top10holder', 'Top10flowholder'],
>       start_time='20200101',
>       end_time='20300101'
>   )
>   ```
