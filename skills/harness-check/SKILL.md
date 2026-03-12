---
name: harness-check
description: >
  检查 AI 协作项目是否偏离了系统设计流程。当用户说"检查有没有偏离"、
  "harness check"、"帮我审计项目状态"、"是不是走错了"、"流程对不对"时触发。
  通过 bash 脚本客观检测文件系统状态（不靠 AI 猜测），返回结构化的偏离报告。
  任何需要确认项目流程合规性的场景都应触发这个 skill。
---

你负责客观检测项目是否偏离了系统设计流程。**核心原则：文件存不存在不靠 AI 判断，靠脚本检测。**

## 执行步骤

### Step 1：运行检测脚本

优先运行独立脚本：

```bash
bash .claude/skills/harness-check/scripts/check.sh
```

如果脚本执行失败（路径不对或权限问题），使用以下内嵌逻辑：

```bash
echo "=== Harness 偏离检测报告 ==="
echo ""

# ── 产物存在性检查 ──────────────────────────
check_file() { [ -f "$1" ] && echo "  ✅ $1" || echo "  ⬜ $1"; }

echo "【第 1 阶段：产品阶段】"
check_file "docs/PRD.md"
check_file "docs/WIREFRAME.md"

echo "【第 2 阶段：验证阶段】"
check_file "docs/ROI.md"

echo "【第 3 阶段：系统设计阶段】"
check_file "docs/SYSTEM_DESIGN.md"
check_file "docs/TECH_SELECTION.md"
check_file "docs/MODULE_DESIGN.md"
check_file "docs/DATA_MODEL.md"

echo "【第 4 阶段：详细设计阶段】"
check_file "docs/API_SPEC.md"
check_file "docs/DATA_MODEL_PHYSICAL.md"
check_file "docs/TEST_STRATEGY.md"

echo "【第 5 阶段：Harness 构建】"
check_file "ARCHITECTURE.md"
check_file "AGENTS.md"
check_file "RULES.md"

# ── 前置条件违规检查 ─────────────────────────
echo ""
echo "【偏离检测】"
V=0

[ -f "docs/SYSTEM_DESIGN.md" ] && [ ! -f "docs/PRD.md" ] && \
  echo "  🚨 SYSTEM_DESIGN 存在但 PRD 缺失（跳过了产品阶段）" && V=$((V+1))

[ -f "docs/SYSTEM_DESIGN.md" ] && [ ! -f "docs/ROI.md" ] && \
  echo "  🚨 SYSTEM_DESIGN 存在但 ROI.md 缺失（跳过了验证阶段，未做价值评估就进入系统设计）" && V=$((V+1))

[ -f "docs/API_SPEC.md" ] && [ ! -f "docs/SYSTEM_DESIGN.md" ] && \
  echo "  🚨 API_SPEC 存在但 SYSTEM_DESIGN 缺失（跳过了系统设计阶段）" && V=$((V+1))

[ -f "ARCHITECTURE.md" ] && [ ! -f "docs/API_SPEC.md" ] && \
  echo "  🚨 ARCHITECTURE.md 存在但 API_SPEC 缺失（在详细设计前构建了 Harness）" && V=$((V+1))

[ -f "AGENTS.md" ] && [ ! -f "docs/SYSTEM_DESIGN.md" ] && \
  echo "  🚨 AGENTS.md 存在但 SYSTEM_DESIGN 缺失（Harness 缺乏设计依据）" && V=$((V+1))

SRC=$(find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" -o -name "*.java" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/.claude/*" \
  2>/dev/null | head -1)
[ -n "$SRC" ] && [ ! -f "docs/API_SPEC.md" ] && \
  echo "  🚨 发现实现代码（$SRC 等）但 API_SPEC.md 不存在（过早开始实现）" && V=$((V+1))

echo ""
[ "$V" -eq 0 ] && echo "  ✅ 未发现偏离，流程正常" || echo "  共发现 $V 个偏离项"
```

### Step 2：整理并展示报告

将脚本原始输出整理成如下格式输出给用户：

```
📋 Harness 偏离检测报告
━━━━━━━━━━━━━━━━━━━━━━

阶段产物状态：
  第1阶段（产品阶段）
    ✅ docs/PRD.md
  第2阶段（系统设计）
    ✅ docs/SYSTEM_DESIGN.md
    ⬜ docs/TECH_SELECTION.md  ← 缺失
    ...

偏离检测：
  🚨 [偏离描述]  ← 如有
  ✅ 未发现偏离  ← 如无

建议：
  [具体操作建议]
```

### Step 3：解读偏离并给出建议

对每个检测到的偏离，说明：
1. **违反了什么规则**（见下方规则表）
2. **为什么这条规则存在**（一句话原因）
3. **怎么修复**（具体下一步）

如果没有偏离，提示下一步可以：
- 运行 `/harness` 查看完整进度
- 运行 `/harness-next` 推进到下一阶段

## 偏离规则说明

| 检测规则 | 严重程度 | 原因 |
|---------|---------|------|
| 有后置文档但缺前置文档 | 🚨 严重 | 每个阶段的产物是下一阶段的输入，没有 PRD 的系统设计是无根之木 |
| SYSTEM_DESIGN 存在但 ROI.md 缺失 | 🚨 严重 | 验证阶段的价值评估是进入系统设计的决策门，没做 ROI 评估就投入系统设计，风险极高 |
| ARCHITECTURE.md 存在但 API_SPEC 缺失 | 🚨 严重 | Harness 是设计的"编译结果"，没有完整的详细设计，约束文档无法写准确 |
| 有实现代码但无 API_SPEC | 🚨 严重 | 没有接口契约就开始实现，前后端必然对不上，返工成本极高 |
| 有 Harness 文件但缺系统设计 | 🚨 严重 | AGENTS.md 里的指引必须来自真实的架构决策，否则只是空话 |
