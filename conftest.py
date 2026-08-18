"""项目根 conftest：显式把仓库根目录加入 sys.path。

不同 pytest 导入模式（prepend / append / importlib）下行为不一致，
显式插入根目录保证能稳定 import dcc_checker。
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
