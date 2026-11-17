# ub-mode

第三方技能安装指针；本仓库维护来源、核对版本与恢复命令。

- 来源：`unclebob/ub-mode`
- 上游入口：https://github.com/unclebob/ub-mode
- 原始路径：`SKILL.md`
- 核对提交：`3da62bf3fcfd2034de41f30d920d2739e566171f`
- 用途：通过 TDD、领域建模、根因修复、行为测试与小步提交组织开发，并调用配套工具检查代码质量。

## 安装到 Codex 用户层

使用 Python 3 与 Codex 自带的 `skill-installer` 恢复已核对版本：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo unclebob/ub-mode \
  --ref 3da62bf3fcfd2034de41f30d920d2739e566171f \
  --path . \
  --name ub-mode
```

安装后通过 `$ub-mode` 调用。已有安装时，先核对版本和本机定制再决定如何更新。

## 配套工具

| 工具 | 来源 | 版本 | 核对提交 |
| --- | --- | --- | --- |
| Crapper | https://github.com/unclebob/crapper | `0.1.0` | `c757ec79a6c15dc815238bbd9c2f4601eb54d3cc` |
| Dryer | https://github.com/unclebob/dryer | `0.1.0` | `66ff6d21a42c04afcad89c78a80066176d1294b0` |
| Mutator | https://github.com/unclebob/mutator | `0.1.0` | `830ec7e9c39664d753f8699015bc796df67727b9` |

需要 `uv` 和 Python 3.12。以下命令将三者安装到同一独立环境，使 Mutator 可以导入 Crapper：

```bash
uv tool install --python 3.12 \
  --with 'dryer @ git+https://github.com/unclebob/dryer.git@66ff6d21a42c04afcad89c78a80066176d1294b0' \
  --with 'mutator @ git+https://github.com/unclebob/mutator.git@830ec7e9c39664d753f8699015bc796df67727b9' \
  --with-executables-from dryer \
  --with-executables-from mutator \
  'crapper @ git+https://github.com/unclebob/crapper.git@c757ec79a6c15dc815238bbd9c2f4601eb54d3cc'
```

`uv tool list` 中的管理项为 `crapper`，包含 `crapper`、`dryer`、`mutator` 三个命令。安装后检查：

```bash
uv tool list
crapper --help
dryer --help
mutator --help
```

核对日期：2026-11-17。技能文件已与固定提交逐文件核对；配套工具已在临时样例中验证 Python、TypeScript 复杂度分析、重复代码检测，以及 4 个变异全部被测试捕获。
