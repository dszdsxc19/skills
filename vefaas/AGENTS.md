# vefaas

这是外部 skill 的安装指针，不在本仓库维护第三方本体。

- 来源：`https://vefaas-cli.tos-cn-beijing.volces.com/skills/`
- 原始路径：`artifacts/vefaas-skill-05c53fd.tgz`，归档内入口为 `SKILL.md`
- 更新索引：`.well-known/agent-skills/index.json` 中的 `vefaas` 条目

安装到 Codex 用户层：

```bash
npx skills add https://vefaas-cli.tos-cn-beijing.volces.com/skills/ --skill vefaas -g -a codex -y
```
