"""mayapy smoke 脚本：验证目标 Maya 版本能 import maya.cmds 与 PySide2。

运行：  "<Maya>/bin/mayapy.exe" scripts/smoke_maya.py
"""
import sys

print("=== mayapy smoke ===")
print("python:", sys.version.split()[0])

results = []
try:
    import maya.cmds as cmds  # noqa: F401
    results.append(("maya.cmds", "OK"))
except Exception as e:  # pragma: no cover
    results.append(("maya.cmds", "FAIL: %r" % e))

try:
    import PySide2  # noqa: F401
    from PySide2 import QtCore, QtWidgets  # noqa: F401
    results.append(("PySide2", "OK %s" % PySide2.__version__))
except Exception as e:  # pragma: no cover
    results.append(("PySide2", "FAIL: %r" % e))

for name, status in results:
    print("[%s] %s" % (name, status))
print("SMOKE DONE")
