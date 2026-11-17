#!/usr/bin/env bash
# 把本 skill 软链到当前用户的 DSH skills 目录（实体保留在 skill 仓库，单一事实源，幂等）。
# 用法: bash scripts/install.sh
set -euo pipefail

NAME="wx-mp-clip"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DST="${DSH_SKILLS_DIR:-$HOME/.dsh/skills}/$NAME"

echo "实体目录 : $SRC"
echo "软链到   : $DST"

command -v node >/dev/null || { echo "缺少 node（需 Node>=18）"; exit 1; }
[ -f "$SRC/SKILL.md" ] || { echo "缺少 SKILL.md"; exit 1; }
node --check "$SRC/scripts/wx_clip.mjs"

# 已指向同一目录则跳过；否则备份旧实体/旧链后重建软链
if [ -L "$DST" ] && [ "$(readlink "$DST")" = "$SRC" ]; then
  echo "已存在相同软链，跳过"
else
  if [ -e "$DST" ] || [ -L "$DST" ]; then
    bak="$DST.bak.$(date +%Y%m%d%H%M%S)"
    mv "$DST" "$bak"
    echo "已备份旧版本 -> $bak"
  fi
  mkdir -p "$(dirname "$DST")"
  ln -s "$SRC" "$DST"
fi

[ -f "$DST/SKILL.md" ] && [ -f "$DST/scripts/wx_clip.mjs" ] || { echo "软链安装不完整"; exit 1; }
node --check "$DST/scripts/wx_clip.mjs"
echo "✅ 安装完成（软链）: $DST -> $SRC"
echo "   直接运行：node \"$DST/scripts/wx_clip.mjs\" \"<mp.weixin.qq.com 文章URL>\" ./out --ocr"
