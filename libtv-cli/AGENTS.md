# libtv-cli

第三方技能安装指针；本仓库只维护来源与恢复命令。

- 来源：`https://liblibai-web-static.liblib.cloud/cli/1.0.2/libtv-cli-skill.zip`
- 原始路径：`SKILL.md`
- 核对版本：`1.0.2`
- 来源依据：本机官方安装文档与在线官方 manifest，未改动本机 CLI。

安装到 Codex 用户层：

```bash
skill_tmp="$(mktemp -d)"
trap 'rm -rf "$skill_tmp"' EXIT
curl --fail --location https://liblibai-web-static.liblib.cloud/cli/1.0.2/libtv-cli-skill.zip --output "$skill_tmp/skill.zip"
unzip -q "$skill_tmp/skill.zip" -d "$skill_tmp/unpacked"
npx skills add "$skill_tmp/unpacked" --skill libtv-cli -g -a codex -y
```

核对日期：2026-11-16。命令用于恢复安装；本次整理未执行升级或覆盖本机技能。
