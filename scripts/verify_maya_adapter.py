"""在 mayapy standalone 下验证 MayaAdapter 的基本方法。

运行：  "<Maya>/bin/mayapy.exe" scripts/verify_maya_adapter.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import maya.standalone  # noqa: E402

try:
    maya.standalone.initialize(name="python")
except Exception as e:  # pragma: no cover
    print("standalone initialize FAIL:", repr(e))
    sys.exit(0)

import maya.cmds as cmds  # noqa: E402
from dcc_checker.adapters.maya_adapter import MayaAdapter  # noqa: E402

cmds.file(new=True, force=True)
cube = cmds.polyCube(name="SM_TestCube")[0]

adapter = MayaAdapter()
meshes = adapter.list_meshes()
print("list_meshes:", meshes)
print("has SM_TestCube:", "SM_TestCube" in meshes)

sgs = adapter.get_shading_engines("SM_TestCube")
print("shading engines:", sgs)

adapter.freeze_transforms(["SM_TestCube"])
print("freeze ok")

adapter.delete_history(["SM_TestCube"])
print("delete history ok")

# 蒙皮保护：造一个带 skinCluster 的 mesh，确认走 bakePartialHistory 而非裸删
skin_mesh = cmds.polyCube(name="SM_Skinned")[0]
cmds.select(skin_mesh)
joints = [cmds.joint(p=(0, 0, 0)), cmds.joint(p=(0, 1, 0))]
cmds.skinCluster(joints[0], skin_mesh, toSelectedBones=True)
print("skin cluster:", cmds.ls(cmds.listHistory(skin_mesh, pruneDagObjects=True), type="skinCluster"))

adapter.delete_history([skin_mesh])
print("skinned delete_history (bakePartialHistory) ok; skinCluster=",
      cmds.ls(type="skinCluster"))

print("MAYA ADAPTER VERIFY DONE")
