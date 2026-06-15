---
name: 下载财务数据
description: 下载A股财务数据，在获取财务数据前需要先下载财务数据，支持的财务数据如下：
    'Balance'          #资产负债表
    'Income'           #利润表
    'CashFlow'         #现金流量表
    'Capital'          #股本表
    'Holdernum'        #股东数
    'Top10holder'      #十大股东
    'Top10flowholder'  #十大流通股东
    'Pershareindex'    #每股指标
---

> # tips:
> - 下载财务数据后，才能通过get_financial_data获取到财务数据，
> - 通常可以单独写一个下载财务数据脚本，定时执行，这样在获取财务数据时不用再提前下载