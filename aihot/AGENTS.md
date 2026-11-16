# aihot

第三方技能安装指针；本仓库只维护来源与恢复命令。

- 来源：`https://aihot.news/aihot-skill/`
- 原始路径：`SKILL.md`
- 来源依据：官方站点入口已回读。

安装到 Codex 用户层：

```bash
skill_tmp="$(mktemp -d)"
trap 'rm -rf "$skill_tmp"' EXIT
curl --fail --location https://aihot.news/aihot-skill/ --output "$skill_tmp/SKILL.md"
npx skills add "$skill_tmp" --skill aihot -g -a codex -y
```

核对日期：2026-11-16。命令用于恢复安装；本次整理未执行升级或覆盖本机技能。
