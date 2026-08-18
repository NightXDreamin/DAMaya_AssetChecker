# DAMaya Asset Checker — 工具清单与四阶段开发计划

> 生成日期：2026-08-18
> 依据：《DAMaya_AssetChecker_可补充工具清单.md》与当前代码基线（4 个工具）
> 本文档是规划文档：列出全部目标工具与分阶段推进顺序，交付按阶段单独审批执行。

---

## 0. 现状基线

当前已实现 4 个工具：

| 工具 | id | 类别 | 类型 | 说明 |
|---|---|---|---|---|
| 命名前缀检查 | `naming.prefix` | Naming | 检测 | 网格需带 `SM_`/`SK_` 前缀 |
| 默认材质检查 | `material.default` | Material | 检测 | 禁用 `lambert1`/`initialShadingGroup` |
| 删除构建历史 | `cleanup.delete_history` | Cleanup | 动作 | 删历史（已带 `bakePartialHistory` 蒙皮保护） |
| 冻结变换 | `transform.freeze` | Transform | 动作 | Freeze Transforms |

`examples/probe_tool.py` 为示例探针，不参与扫描。

---

## 1. 完整目标工具清单（约 60+ 条）

> 严重级：`ERROR`（挡门禁）/ `WARNING`（提示）/ `INFO`（记录）
> Fix：`[Auto-Fix]` 可自动修复 / `[Manual]` 仅人工

### 1.1 Naming / 命名（8 条）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `NAME_001` | 前缀 `SM_`/`SK_` | ERROR | [Auto-Fix] | [DONE] 已有检测，待补 Fix |
| `NAME_002` | 非法字符（空格/中文/`#$%`/`\|`） | ERROR | [Auto-Fix] | [TODO] 待做 |
| `NAME_003` | Maya 默认名（`pCube1`/`polySurface3`） | WARNING | [Manual] | [TODO] 待做 |
| `NAME_004` | 场景内短名重复 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `NAME_005` | Shape 名 = Transform 名 + "Shape" | WARNING | [Auto-Fix] | [TODO] 待做 |
| `NAME_006` | 清理复制产生的数字后缀 | WARNING | [Auto-Fix] | [TODO] 待做 |
| `NAME_007` | 残留 namespace | ERROR | [Auto-Fix] | [TODO] 待做 |
| `NAME_008` | 材质命名规范（`M_`/`MI_`） | WARNING | [Auto-Fix] | [TODO] 待做 |

### 1.2 Transform / 变换（7 条）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `XFORM_001` | 变换归零检测（T=0,R=0,S=1） | ERROR | [Auto-Fix] | [PARTIAL] 有动作无检测，待补 |
| `XFORM_002` | 禁负缩放 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `XFORM_003` | Pivot 位置合规（底部中心/bbox 中心） | WARNING | [Auto-Fix] | [TODO] 待做 |
| `XFORM_004` | 残留构建历史检测 | WARNING | [Auto-Fix] | [PARTIAL] 有动作无检测，待补 |
| `XFORM_005` | 资产在世界原点 | WARNING | [Auto-Fix] | [TODO] 待做 |
| `XFORM_006` | 缩放值接近 1:1:1（极端值告警） | WARNING | [Manual] | [TODO] 待做 |
| `XFORM_007` | 朝向正确（面向 front/-Z） | INFO | [Manual] | [TODO] 待做 |

### 1.3 Topology / 拓扑（14 条）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `TOPO_001` | N-Gon（>4 边面） | ERROR | [Manual] | [TODO] 待做 |
| `TOPO_002` | 非流形几何（边/顶点） | ERROR | [Auto-Fix] | [TODO] 待做 |
| `TOPO_003` | 零面积面 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `TOPO_004` | 零长度边 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `TOPO_005` | Lamina 面（重叠共顶点面） | ERROR | [Auto-Fix] | [TODO] 待做 |
| `TOPO_006` | 三角面预算（按 profile） | WARNING | [Manual] | [TODO] 待做 |
| `TOPO_007` | 开放边界 / 未闭合边 | WARNING | [Manual] | [TODO] 待做 |
| `TOPO_008` | 反转/不一致法线 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `TOPO_009` | 极点（≥6 边顶点） | INFO | [Manual] | [TODO] 待做 |
| `TOPO_010` | 非平面面 | INFO | [Manual] | [TODO] 待做 |
| `TOPO_011` | 孤立顶点/游离边 | WARNING | [Auto-Fix] | [TODO] 待做 |
| `TOPO_012` | 重合顶点（阈值 0.0001） | WARNING | [Auto-Fix] | [TODO] 待做 |
| `TOPO_013` | 硬边规范/平滑法线 | WARNING | [Auto-Fix] | [TODO] 待做 |
| `TOPO_014` | 内部不可见面 | INFO | [Manual] | [TODO] 待做 |

### 1.4 UV（8 条）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `UV_001` | 必须存在 UV0（`map1`） | ERROR | [Manual] | [TODO] 待做 |
| `UV_002` | UV 超出 0-1 象限 | WARNING | [Manual] | [TODO] 待做 |
| `UV_003` | UV 自重叠/翻转 | WARNING | [Manual] | [TODO] 待做 |
| `UV_004` | Lightmap 需 UV1 且不重叠 | WARNING | [Manual] | [TODO] 待做 |
| `UV_005` | 跨 UV 象限连续壳 | WARNING | [Manual] | [TODO] 待做 |
| `UV_006` | UV 点紧贴象限边界 | INFO | [Manual] | [TODO] 待做 |
| `UV_007` | Texel Density 一致性 | WARNING | [Manual] | [TODO] 待做 |
| `UV_008` | UV 岛间距 padding ≥ N 像素 | INFO | [Manual] | [TODO] 待做 |

### 1.5 Hierarchy / 场景组织（9 条）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `HIER_001` | 空组 | WARNING | [Auto-Fix] | [TODO] 待做 |
| `HIER_002` | 嵌套深度 ≤ N | WARNING | [Manual] | [TODO] 待做 |
| `HIER_003` | 孤立/中间节点（`*Orig`） | INFO | [Auto-Fix] | [TODO] 待做 |
| `HIER_004` | 残留显示层 | WARNING | [Auto-Fix] | [TODO] 待做 |
| `HIER_005` | 父级是几何体 | WARNING | [Manual] | [TODO] 待做 |
| `HIER_006` | 残留 selection sets | INFO | [Auto-Fix] | [TODO] 待做 |
| `HIER_007` | 未使用节点 | INFO | [Auto-Fix] | [TODO] 待做 |
| `HIER_008` | unknown/插件缺失节点 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `HIER_009` | 隐藏废案几何（old/backup/test） | INFO | [Manual] | [TODO] 待做 |

### 1.6 Material & Texture（9 条）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `MAT_001` | 禁 lambert1 | ERROR | [Manual] | [DONE] 已实现 |
| `MAT_002` | 单网格材质数 ≤ N | WARNING | [Manual] | [TODO] 待做 |
| `MAT_003` | 重复材质 | INFO | [Auto-Fix] | [TODO] 待做 |
| `MAT_004` | 面级材质分配 | WARNING | [Manual] | [TODO] 待做 |
| `TEX_001` | 贴图路径在项目内 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `TEX_002` | 分辨率 2 的幂且 ≤ 上限 | WARNING | [Manual] | [TODO] 待做 |
| `TEX_003` | 通道打包命名（`_BC`/`_N`/`_ORM`） | WARNING | [Manual] | [TODO] 待做 |
| `TEX_004` | 贴图缺失/路径断裂 | ERROR | [Manual] | [TODO] 待做 |
| `TEX_005` | 色彩空间正确（Normal/Roughness RAW） | WARNING | [Auto-Fix] | [TODO] 待做 |

### 1.7 Skin & Rig / 蒙皮绑定（9 条，差异化维度）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `SKIN_001` | 每顶点影响骨骼数 ≤ 4 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `SKIN_002` | 骨骼总数 ≤ N（50/75） | WARNING | [Manual] | [TODO] 待做 |
| `SKIN_003` | 唯一根骨骼命名为 `Root` | ERROR | [Auto-Fix] | [TODO] 待做 |
| `SKIN_004` | 无零权重/未归一化权重顶点 | ERROR | [Auto-Fix] | [TODO] 待做 |
| `SKIN_005` | 骨骼命名（左右后缀 `_l`/`_r`） | WARNING | [Manual] | [TODO] 待做 |
| `SKIN_006` | Joint Orient 归零/旋转轴一致 | WARNING | [Manual] | [TODO] 待做 |
| `SKIN_007` | 绑定姿态对称 | WARNING | [Manual] | [TODO] 待做 |
| `SKIN_008` | 无残留无用 deformer | INFO | [Auto-Fix] | [TODO] 待做 |
| `SKIN_009` | 骨骼无缩放 | ERROR | [Auto-Fix] | [TODO] 待做 |

### 1.8 Scene & Export / 场景与导出（8 条，拦源头）

| ID | 规则 | 级别 | Fix | 状态 |
|---|---|---|---|---|
| `SCENE_001` | 场景单位 = cm/m | ERROR | [Auto-Fix] | [TODO] 待做 |
| `SCENE_002` | Up Axis 设置正确 | ERROR | [Manual] | [TODO] 待做 |
| `SCENE_003` | 资产尺度 sanity check | WARNING | [Manual] | [TODO] 待做 |
| `SCENE_004` | 默认相机已隐藏 | INFO | [Auto-Fix] | [TODO] 待做 |
| `SCENE_005` | 平滑预览关闭 | WARNING | [Auto-Fix] | [TODO] 待做 |
| `SCENE_006` | Render stats 全部 active | INFO | [Auto-Fix] | [TODO] 待做 |
| `SCENE_007` | 无未保存修改 | WARNING | [Manual] | [TODO] 待做 |
| `SCENE_008` | FBX 导出设置预检 | ERROR | [Auto-Fix] | [TODO] 待做 |

**合计目标**：8 类，约 72 条（当前已实现 2 检测 + 2 动作）。

---

## 2. 四阶段推进计划

> 每阶段都以「可独立演示」为边界，按依赖从地基到差异化层层推进。

### 阶段 1 — 地基改造 + Transform/Naming 首批规则（规则 4 → 13）

- 先决依赖：T-02 `Issue`/`Severity` 结构化、T-03 `config/rules.json` + `RuleSource` 抽象 + profile、T-05 扩充 `BaseAdapter` 的 Transform/Naming 方法
- 新增工具：`XFORM_001~004`（归零/负缩放/pivot/残留历史）、`NAME_002~004`（非法字符/默认名/重名）
- T-06 Auto-Fix 框架落地：`NAME_001` 补前缀、`XFORM_001` 归零、`XFORM_002` 负缩放修复、`XFORM_004` 删历史
- **验收**：规则 2→13，全部带 Severity 分级与可勾选修复；Action 类工具仍白名单制

### 阶段 2 — 规则密度补齐（规则 → ~44）

- 先决：T-04 `SceneSnapshot` + OpenMaya 性能路径、T-05 扩充 Topology/UV/Texture/Hierarchy 方法
- 新增：Topology 14 条、UV 8 条、Hierarchy 9 条、Naming 补齐 4 条、Material/Texture 补齐 7 条
- **验收**：规则数破 40，覆盖 6 大维度，拓扑检查走 `MFnMesh`/`MItMeshPolygon` 不卡大场景

### 阶段 3 — 差异化能力（规则 → ~72 + 门禁 + CLI）

- 新增：Skin/Rig 9 条、Scene/Export 8 条
- T-07 Git 提交门禁（只拦 `ERROR`）、T-09 `cli.py` + JSON/HTML 报告 + 非零退出码
- T-08 UI 补齐：严重级筛选、`[Fix Selected]`/`[Fix All Safe]`、Scan Selected 双模式、组件级定位、QSettings 持久化
- **验收**：规则全量约 72 条；Git 门禁与 CLI 可被 CI 调用；Skin/Scene 维度成为差异化亮点

### 阶段 4 — 工程化收尾

- T-10~T-22：`pyproject.toml`/`requirements.txt`、`logging`、`pytest-cov`、版本/README 架构图、脏场景样例、registry 递归扫描、Roadmap 纳入版本管理、死代码二次清理、录屏
- **验收**：覆盖率 ≥60%、打包可安装、录屏完整呈现「脏场景 → 全红 → 一键修 → 全绿 → commit 成功」

---

## 3. 依赖关系小结

```
T-02 Issue/Severity ─┬─> T-06 Auto-Fix ─┐
T-03 rules.json      ─┤                    ├─> 阶段1 规则
T-05 adapter(Transform)─┘                  │
T-04 Snapshot+OpenMaya ─> 阶段2 拓扑/UV/层级/材质
阶段1+2 规则 ─> T-06 Fix ─> T-08 UI ─> T-07 门禁 ─> 阶段3
阶段3 ─> T-09 CLI/JSON ─> 阶段4 工程化收尾
```

关键前置：
- **T-02 是第一块骨牌**：解锁 Severity 分级、UI 筛选、Git 门禁、组件级定位、JSON 报告
- **T-04 是性能红线**：拓扑/UV 规则必须走 OpenMaya，否则大场景卡死 Maya

---

## 4. 状态图例

- `[DONE]` 已实现
- `[PARTIAL]` 部分实现（有动作无检测，或需补 Fix）
- `[TODO]` 待做
