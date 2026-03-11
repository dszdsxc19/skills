---
name: harness-next
description: >
  推进系统设计流程到下一阶段。当用户说"进入下一阶段"、"当前阶段完成了"、
  "推进到系统设计"、"harness next"、"进入详细设计"时触发。
  该 skill 会用脚本客观验证当前阶段的所有产物文件都真实存在，
  验证通过后更新 PROGRESS.md 并创建下一阶段的文档模板。
  如果用户说"推进"、"下一步"在项目上下文中，也应该触发。
---

你负责在用户确认当前阶段完成后，将项目推进到下一阶段。推进前必须用脚本客观验证产物存在，不能依赖用户口头声明。

## 执行流程

### Step 1：读取当前状态

```bash
cat PROGRESS.md
```

从中提取：
- 当前阶段编号（`current_stage` 字段）
- 当前阶段声明的**已完成产物**路径列表（表格中 `✅` 或 `🟡` 行的产物列）

### Step 2：用脚本验证产物真实存在

对当前阶段列出的每个产物路径，运行：

```bash
MISSING=0
for f in [产物路径列表，空格分隔]; do
  [ -f "$f" ] && echo "✅ $f" || { echo "❌ $f 不存在"; MISSING=$((MISSING+1)); }
done
echo "MISSING_COUNT=$MISSING"
```

**如果有缺失产物**：停止，不推进。告诉用户具体哪些文件不存在，提示先完成再运行 `/harness-next`。

**如果全部存在**：继续。

### Step 3：告知用户并确认

展示确认信息：

```
当前阶段 [N - 阶段名] 产物全部验证 ✅

准备推进到：[N+1 - 下一阶段名]
下一阶段需要产出：
  - [产物1路径]
  - [产物2路径]

确认推进？（回复"确认"或"是"继续）
```

等用户确认。

### Step 4：更新 PROGRESS.md

读取当前 PROGRESS.md，做以下修改：
1. 将 `current_stage` 从 N 改为 N+1
2. 将当前阶段行的状态从 `🟡 进行中` 改为 `✅ 完成`
3. 将下一阶段行的状态从 `⏳ 未开始` 改为 `🟡 进行中`

用 Edit 工具精确修改，不要整体重写文件。

### Step 5：创建下一阶段的文档模板

根据推进到的阶段，从 `.claude/skills/harness-next/templates/` 复制对应模板：

| 推进到 | 需要创建的文件 | 模板来源 |
|--------|-------------|---------|
| 阶段 1（产品阶段） | `docs/PRD.md` | `templates/PRD.md` |
| 阶段 2（系统设计） | `docs/SYSTEM_DESIGN.md`, `docs/TECH_SELECTION.md`, `docs/DATA_MODEL.md` | `templates/SYSTEM_DESIGN.md` 等 |
| 阶段 3（详细设计） | `docs/API_SPEC.md`, `docs/DATA_MODEL_PHYSICAL.md`, `docs/TEST_STRATEGY.md` | 对应模板 |
| 阶段 4（Harness 构建） | `ARCHITECTURE.md`, `AGENTS.md`, `RULES.md` | 对应模板 |
| 阶段 5（实现） | `src/` 目录（如不存在则创建） | `mkdir -p src` |
| 阶段 6（部署运维） | `docs/DEPLOY_OPS.md` | `templates/DEPLOY_OPS.md` |

只创建**不存在**的文件，不覆盖用户已有内容。

执行复制：
```bash
cp .claude/skills/harness-next/templates/[模板文件] [目标路径]
```

### Step 6：完成报告

```
✅ 已推进到：阶段 [N+1] - [阶段名称]

创建的文档模板：
  - [文件路径1]（新建）
  - [文件路径2]（已存在，跳过）

下一步：
  1. 打开上述文档，按模板内容填写
  2. 完成后运行 /harness-next 继续推进
  3. 随时运行 /harness 查看进度，/harness-check 检查偏离
```
