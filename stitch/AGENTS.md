# stitch

第三方技能安装指针；本仓库只维护来源与恢复命令。

- 来源：`@google/stitch`
- 原始路径：`skills/design/stitch/SKILL.md`
- 核对版本：`0.12.1`
- 来源依据：全局 npm 包中的入口与本机逐字节一致；原仓库 google-labs-code/stitch-sdk。

安装到 Codex 用户层：

```bash
npm install -g @google/stitch@0.12.1
skill_package_dir="$(npm root -g)/@google/stitch/skills/design/stitch"
npx skills add "$skill_package_dir" --skill stitch -g -a codex -y
```

核对日期：2026-11-16。命令用于恢复安装；本次整理未执行升级或覆盖本机技能。
