"""xtquant (miniQMT) 行情数据源 —— 通过 xtdata 拉取真实 A 股 K 线。

实现镜像了已验证通过的接入方式：``download_history_data`` 先把行情缓存到本地，
``get_market_data_ex`` 再读回，最后映射成 :data:`OHLCV_COLUMNS` 契约（带 DatetimeIndex），
即可经 :class:`~qmtquant.runtime.feed.ReplayFeed` 喂给运行时引擎。数据端不需要任何资金账号/密码。

IMPORTANT: 这里**没有**顶层 ``import xtquant``，以便在没装 miniQMT SDK 的机器上也能正常
``import qmtquant``；``xtdata`` 在 :meth:`get_dataframe` 内部惰性导入。

运行前提（见 README "xtquant / miniQMT integration"）：
- Python 3.10/3.11（终端的 xtquant 无 cp312 构建）；
- 运行中的 miniQMT 终端 + 一次性 ``python scripts/setup_xtquant.py`` 接入。

本终端 build 的两个坑（已在此处理）：
- 日期参数必须是**字符串**（日线 ``'%Y%m%d'``，其余 ``'%Y%m%d%H%M%S'``）；传 datetime 会在
  .pyd 内报错。``''`` 表示"全部"。
- 返回帧的索引也是同样的日期字符串，这里按周期显式解析为 DatetimeIndex。
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from .base import DataSource, OHLCV_COLUMNS


class XtQuantDataSource(DataSource):
    """xtquant / miniQMT 行情数据源（数据端，无需账号）。

    Parameters
    ----------
    period:
        xtquant 周期：``'1d'``（日线）、``'1m'/'5m'/'15m'/'30m'/'1h'``（分钟）等。
    dividend_type:
        复权方式：``'none'``（不复权）、``'front'``/``'back'``（前/后复权）。
        回测通常用 ``'front'``；默认 ``'none'`` 与 xtquant 默认一致。
    download:
        为 ``True``（默认）时先 ``download_history_data`` 刷新本地缓存再读；
        设 ``False`` 则只读已缓存的行情（更快/可离线）。
    """

    def __init__(
        self,
        *,
        period: str = "1d",
        dividend_type: str = "none",
        download: bool = True,
    ) -> None:
        self.period = period
        self.dividend_type = dividend_type
        self.download = download

    def _fmt(self, dt: datetime | None) -> str:
        """把时间格式化成本终端要求的字符串（None -> '' 表示全部）。"""
        if dt is None:
            return ""
        return dt.strftime("%Y%m%d" if self.period == "1d" else "%Y%m%d%H%M%S")

    def get_dataframe(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """拉取 ``symbol`` 在 ``[start, end]`` 的归一化 OHLCV 帧。

        步骤：（可选）下载缓存 -> ``get_market_data_ex`` 读回 -> 解析索引为
        DatetimeIndex -> 仅保留并排序 :data:`OHLCV_COLUMNS` -> 按 ``[start, end]`` 切片。
        下游 :func:`qmtquant.data.sources.base.validate_ohlcv`（经 ReplayFeed）会再做形状校验。

        Raises
        ------
        ValueError
            终端未返回该合约的行情（终端未运行 / 未下载 / 代码或周期不对）时。
        """
        from xtquant import xtdata  # 惰性导入：保持包在无 SDK 环境可导入

        s, e = self._fmt(start), self._fmt(end)
        if self.download:
            xtdata.download_history_data(symbol, self.period, s, e)

        data = xtdata.get_market_data_ex(
            list(OHLCV_COLUMNS),
            [symbol],
            period=self.period,
            start_time=s,
            end_time=e,
            count=-1,
            dividend_type=self.dividend_type,
            fill_data=True,
        )
        df = None if data is None else data.get(symbol)
        if df is None or len(df) == 0:
            raise ValueError(
                f"xtquant 未返回 {symbol!r} 的 {self.period} 行情 "
                f"[{s or '...'}, {e or '...'}]：确认终端在运行、代码/周期正确、已下载数据。"
            )

        df = df.copy()
        idx_fmt = "%Y%m%d" if self.period == "1d" else "%Y%m%d%H%M%S"
        df.index = pd.to_datetime(df.index, format=idx_fmt)
        df = df[list(OHLCV_COLUMNS)].astype(float).sort_index()

        if start is not None or end is not None:
            df = df.loc[start:end]
        return df


__all__ = ["XtQuantDataSource"]
