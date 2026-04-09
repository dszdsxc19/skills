#!/bin/bash
# harness-check.sh — 系统设计流程偏离检测器
# 用法：bash .claude/skills/harness-check/scripts/check.sh [project-root]
# 只读，不修改任何文件

PROJECT="${1:-.}"
cd "$PROJECT" || exit 1

echo "=== Harness 偏离检测报告 ==="
echo "项目路径：$(pwd)"
echo ""

# ── 工具函数 ──────────────────────────────────────────
check_file() {
  local path="$1"
  if [ -f "$path" ]; then
    echo "  ✅ $path"
    return 0
  else
    echo "  ⬜ $path"
    return 1
  fi
}

# ── 各阶段产物存在性检查 ───────────────────────────────
echo "【第 1 阶段：产品阶段】"
check_file "docs/PRD.md"
STAGE1_OK=$?

echo ""
echo "【第 2 阶段：系统设计阶段】"
check_file "docs/SYSTEM_DESIGN.md"
S2A=$?
check_file "docs/TECH_SELECTION.md"
S2B=$?
check_file "docs/DATA_MODEL.md"
S2C=$?
STAGE2_OK=$(( (S2A + S2B + S2C) == 0 ? 0 : 1 ))

echo ""
echo "【第 3 阶段：详细设计阶段】"
check_file "docs/API_SPEC.md"
S3A=$?
check_file "docs/DATA_MODEL_PHYSICAL.md"
S3B=$?
check_file "docs/TEST_STRATEGY.md"
S3C=$?
STAGE3_OK=$(( (S3A + S3B + S3C) == 0 ? 0 : 1 ))

echo ""
echo "【第 4 阶段：Harness 构建】"
check_file "ARCHITECTURE.md"
S4A=$?
check_file "AGENTS.md"
S4B=$?
check_file "RULES.md"
S4C=$?
STAGE4_OK=$(( (S4A + S4B + S4C) == 0 ? 0 : 1 ))

echo ""
echo "【第 5 阶段：实现阶段】"
SRC_COUNT=$(find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" -o -name "*.java" -o -name "*.rs" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/.claude/*" \
  -not -path "*/docs/*" \
  2>/dev/null | wc -l | tr -d ' ')
if [ "$SRC_COUNT" -gt 0 ]; then
  echo "  ✅ 发现 $SRC_COUNT 个实现文件"
else
  echo "  ⬜ 尚无实现代码"
fi

# ── 前置条件违规检测 ───────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "【偏离检测（前置条件链）】"
echo ""

VIOLATIONS=0

# 规则 1：有系统设计但无 PRD → 跳了产品阶段
if [ -f "docs/SYSTEM_DESIGN.md" ] && [ ! -f "docs/PRD.md" ]; then
  echo "  🚨 规则1 违反：SYSTEM_DESIGN.md 存在，但 PRD.md 缺失"
  echo "     原因：系统设计必须服务于产品需求，没有 PRD 的设计是无根之木"
  echo "     建议：补写 docs/PRD.md，确认产品目标和功能范围后再推进"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 规则 2：有 API Spec 但无系统设计 → 跳了系统设计阶段
if [ -f "docs/API_SPEC.md" ] && [ ! -f "docs/SYSTEM_DESIGN.md" ]; then
  echo "  🚨 规则2 违反：API_SPEC.md 存在，但 SYSTEM_DESIGN.md 缺失"
  echo "     原因：API 设计依赖模块拆分，而模块拆分来自系统设计"
  echo "     建议：补写 docs/SYSTEM_DESIGN.md（架构图、模块职责、依赖关系）"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 规则 3：有 ARCHITECTURE.md 但无 API_SPEC → 在详细设计前构建了 Harness
if [ -f "ARCHITECTURE.md" ] && [ ! -f "docs/API_SPEC.md" ]; then
  echo "  🚨 规则3 违反：ARCHITECTURE.md 存在，但 API_SPEC.md 缺失"
  echo "     原因：Harness 是设计的「编译结果」，没有 API 契约的约束文档是空架构"
  echo "     建议：先完成 docs/API_SPEC.md（前后端接口契约），再完善 ARCHITECTURE.md"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 规则 4：有 Harness 文件但无系统设计 → Harness 缺乏架构依据
if { [ -f "AGENTS.md" ] || [ -f "RULES.md" ]; } && [ ! -f "docs/SYSTEM_DESIGN.md" ]; then
  echo "  🚨 规则4 违反：AGENTS.md/RULES.md 存在，但 SYSTEM_DESIGN.md 缺失"
  echo "     原因：行为指引和开发规则必须从真实的架构决策中提炼，否则只是凭空发明"
  echo "     建议：补写 docs/SYSTEM_DESIGN.md 后，重新审视 AGENTS.md 和 RULES.md 的内容"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 规则 5：有实现代码但无 API_SPEC → 过早开始实现
SRC_SAMPLE=$(find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" -o -name "*.java" -o -name "*.rs" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/.claude/*" \
  -not -path "*/docs/*" \
  2>/dev/null | head -1)

if [ -n "$SRC_SAMPLE" ] && [ ! -f "docs/API_SPEC.md" ]; then
  echo "  🚨 规则5 违反：发现实现代码（如 $SRC_SAMPLE），但 API_SPEC.md 不存在"
  echo "     原因：没有接口契约就开始实现，前后端会对不上，返工成本极高"
  echo "     建议：暂停实现，先完成 docs/API_SPEC.md，确认前后端接口后再继续"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# ── 汇总 ──────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$VIOLATIONS" -eq 0 ]; then
  echo "✅ 未发现偏离，项目流程正常"
else
  echo "⚠️  共发现 $VIOLATIONS 个偏离项，建议按上述建议修正后继续推进"
fi
echo ""
echo "提示：运行 /harness 查看完整进度，运行 /harness-next 推进阶段"
