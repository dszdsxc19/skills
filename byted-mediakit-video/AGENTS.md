# byted-mediakit-video

第三方技能安装指针；本仓库只维护来源与恢复命令。

- 来源：`@volcengine/mediakit-cli`
- 原始路径：`skills/byted-mediakit-video/SKILL.md`
- 核对版本：`0.2.2`
- 来源依据：本机安装锁与 npm 包 package.json 已核对；原仓库 volcengine/mediakit-cli。

安装到 Codex 用户层：

```bash
npm install -g @volcengine/mediakit-cli@0.2.2
skill_package_dir="$(npm root -g)/@volcengine/mediakit-cli/skills/byted-mediakit-video"
npx skills add "$skill_package_dir" --skill byted-mediakit-video -g -a codex -y
```

核对日期：2026-11-16。命令用于恢复安装；本次整理未执行升级或覆盖本机技能。
