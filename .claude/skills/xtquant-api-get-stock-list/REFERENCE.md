# get_stock_list_in_sector 

```python
res = xtdata.get_stock_list_in_sector(sectorname)

```
## 释义

获取板块成份股，支持客户端左侧板块列表中任意的板块，包括自定义板块

## 参数

|字段名	|数据类型	|解释|
|-|- |-|
|sectorname	|string	板块名，如 '沪深A股','沪深京A股','沪深300'，'中证500'，'上证50'，'我的自选'等 可以通过xtdata.get_sector_list()查询支持的板块名|
## 返回值

list：内含成份股代码，代码形式为 'stockcode.market'，如 '000002.SZ'