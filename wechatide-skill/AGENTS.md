# wechatide-skill

这是外部 skill 的安装指针，不在本仓库维护第三方本体。

- 来源：`微信开发者工具 App 内置 skill`
- 原始路径：`/Applications/wechatwebdevtools.app/Contents/Resources/app.asar.unpacked/wechatide-skill`

安装到 Codex 用户层：

```bash
mkdir -p "$HOME/.codex/skills"
ditto "/Applications/wechatwebdevtools.app/Contents/Resources/app.asar.unpacked/wechatide-skill" "$HOME/.codex/skills/wechatide-skill"
```
