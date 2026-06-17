# -*- coding: utf-8 -*-
"""让当前 conda 环境能直接 `from xtquant import xtdata`（引用迅投 miniQMT 终端自带的 xtquant）。

做法：在当前解释器的 site-packages 里建一个**目录联接(junction)** `xtquant`，指向终端
`bin.x64/Lib/site-packages/xtquant` 文件夹。这样：
  - `import xtquant` 正常解析（它就在 site-packages 里），其 .pyd 从联接目标目录加载所需
    DLL（实测连 xttrader.connect() 都无需额外 add_dll_directory）。
  - **只暴露 xtquant 一个包**，不会把终端那套庞大的 Python 3.6 旧库（IPython/Pillow6/
    pyreadline 等）带进本环境——避免冲突（早期用整目录 append 会导致 pytest 因旧 pyreadline 崩溃）。

用法（须用目标环境的 python 运行，例如 qmt-projects-py310）：
    python scripts/setup_xtquant.py
    python scripts/setup_xtquant.py --bin "D:/QMT/bin.x64"     # 自定义终端路径
    QMTQUANT_QMT_BIN_PATH=... python scripts/setup_xtquant.py  # 或用环境变量

注意：xtquant 的 .pyd 仅提供到 cp311，必须在 Python 3.10/3.11 下运行（3.12 无法 import）。
junction 在 NTFS 上免管理员权限即可创建；若失败（如非 NTFS），脚本自动回退为复制。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import sysconfig

# 本机已安装的迅投 miniQMT 终端默认路径（按需用 --bin / 环境变量覆盖）
DEFAULT_QMT_BIN = r"F:\finance\迅投QMT极速交易系统交易终端 万联证券版\bin.x64"


def find_site_packages() -> str:
    purelib = sysconfig.get_paths().get("purelib")
    if purelib and os.path.isdir(purelib):
        return purelib
    import site
    for p in site.getsitepackages():
        if os.path.isdir(p):
            return p
    raise RuntimeError("找不到可写的 site-packages 目录")


def remove_existing(link: str) -> None:
    """删除已存在的 link：junction 用 rmdir 仅删联接（不动目标）；真实目录则整树删除。"""
    if not os.path.exists(link) and not os.path.islink(link):
        return
    # 先尝试当作 junction/链接删除
    subprocess.run(["cmd", "/c", "rmdir", link], capture_output=True)
    if os.path.exists(link):
        # 仍存在说明是真实目录（如旧的复制），整树删除
        shutil.rmtree(link, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="为当前 conda 环境接入 miniQMT 的 xtquant")
    parser.add_argument(
        "--bin",
        dest="qmt_bin",
        default=os.environ.get("QMTQUANT_QMT_BIN_PATH", DEFAULT_QMT_BIN),
        help="迅投 QMT 终端的 bin.x64 目录（默认取环境变量 QMTQUANT_QMT_BIN_PATH 或内置默认值）",
    )
    args = parser.parse_args()

    qmt_bin = os.path.abspath(args.qmt_bin)
    target = os.path.join(qmt_bin, "Lib", "site-packages", "xtquant")

    print(f"Python: {sys.version.split()[0]}  ({sys.executable})")
    if sys.version_info[:2] not in {(3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11)}:
        print("⚠️  警告：xtquant 的 .pyd 仅到 cp311，请在 Python 3.10/3.11 下运行；当前版本可能无法 import。")

    if not os.path.isdir(target) or not os.path.isfile(os.path.join(target, "__init__.py")):
        print(f"❌ 未在该路径找到 xtquant 包：{target}")
        print("   请用 --bin 指定正确的 QMT 终端 bin.x64 目录。")
        return 2

    sp = find_site_packages()
    link = os.path.join(sp, "xtquant")
    remove_existing(link)

    # 优先 junction（不占额外磁盘、随终端更新自动同步）
    subprocess.run(["cmd", "/c", "mklink", "/J", link, target], capture_output=True)
    made = "junction"
    if not os.path.isfile(os.path.join(link, "__init__.py")):
        # 回退：直接复制
        print("（junction 创建失败，回退为复制 xtquant ...）")
        shutil.copytree(target, link)
        made = "copy"

    if os.path.isfile(os.path.join(link, "__init__.py")):
        print(f"✅ 已在 site-packages 接入 xtquant（{made}）：{link} -> {target}")
    else:
        print(f"❌ 接入失败：{link}")
        return 1

    # 自检：全新子进程裸 import（不加任何 path/DLL hack，验证联接自给自足）
    r = subprocess.run(
        [sys.executable, "-c", "from xtquant import xtdata; print(xtdata.get_instrument_detail('000001.SZ')['InstrumentName'])"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.returncode == 0:
        print(f"✅ 自检通过：子进程可直接 `from xtquant import xtdata`（取到 {r.stdout.strip()}）。")
        print("   现在本环境的任何脚本/REPL/skill 都能直接 import xtquant。")
        return 0
    print(f"⚠️  接入成功但自检 import 失败：\n{r.stderr.strip()}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
