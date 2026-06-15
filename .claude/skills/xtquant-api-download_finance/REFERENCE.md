# 下载财务数据

## download_financial_data

```python
 download_financial_data(stock_list, table_list=[], start_time='', end_time='', incrementally = None)
```

**功能**：下载财务数据

### 参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_list | list | 合约代码列表 |
| table_list | list | 财务数据表名列表 传[]为下载全部表|
| start_time | string | 起始时间 |
| end_time | string | 结束时间，以m_anntime披露日期字段，按[start_time, end_time]范围筛选 |
| incrementally | bool | 是否增量下载，建议调用时传入True或False,|

### 返回

无

### 备注

同步执行，补充数据完成后返回

---

## download_financial_data2

```python
download_financial_data2(
    stock_list,
    table_list=[],
    start_time='',
    end_time='',
    callback=None
)
```

**功能**：下载财务数据

### 参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_list | list | 合约代码列表 |
| table_list | list | 财务数据表名列表 |
| start_time | string | 起始时间 |
| end_time | string | 结束时间，以m_anntime披露日期字段，按[start_time, end_time]范围筛选 |
| callback | func | 回调函数，参数为进度信息dict |

#### callback 进度信息

| 字段 | 说明 |
|------|------|
| total | 总下载个数 |
| finished | 已完成个数 |
| stockcode | 本地下载完成的合约代码 |
| message | 本次信息 |