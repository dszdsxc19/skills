# batch-grill-me

这是外部 skill 的安装指针，不在本仓库维护第三方本体。

- 来源：`mattpocock/skills`
- 原始路径：`skills/in-progress/batch-grill-me/SKILL.md`
- 状态：上游主分支已删除该 skill；固定到删除前提交 `2ab958093e83e0ec752e6c1c5932da465bf23e0c`。

安装到 Codex 用户层：

```bash
skill_tmp=$(mktemp -d)
trap 'rm -rf "$skill_tmp"' EXIT
git -C "$skill_tmp" init --quiet
git -C "$skill_tmp" remote add origin https://github.com/mattpocock/skills.git
git -C "$skill_tmp" fetch --quiet --depth 1 origin 2ab958093e83e0ec752e6c1c5932da465bf23e0c
git -C "$skill_tmp" checkout --quiet FETCH_HEAD
npx skills add "$skill_tmp" --skill batch-grill-me -g -a codex -y
```
