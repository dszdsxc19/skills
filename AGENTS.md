# Repository Guidelines

## 仓库定位

本仓库用于保存可复用的 AI Agent Skills，不是单一应用程序。

一级目录分为两类：

1. 本仓库维护的 skill：以 `<skill-name>/SKILL.md` 作为入口。
2. 外部安装指针：只保留 `<skill-name>/AGENTS.md`，记录来源与 `npx skills add` 命令。

本仓库维护的 skill 可包含：

- `scripts/`：可执行脚本
- `references/`：按需读取的参考资料
- `templates/`：可复用模板
- `assets/`：静态资源
- `agents/`：Agent 配置
- `evals/`：评测用例

仓库整体用途和 skill 索引见 `README.md`。

## 新增与迁入 Skill

新增自研 skill 时：

1. 使用小写、连字符命名目录，例如 `writing-editor`。
2. 确保目录中存在非空的 `SKILL.md`。
3. 保留 `SKILL.md` 引用的脚本、参考资料、模板和配置，不要只复制入口文件。
4. 检查 frontmatter 中的 `name` 与目录名一致。
5. 在 `README.md` 的对应分类中补充用途说明。
6. 不要提交缓存、构建产物、临时文件或本机环境配置。

对于通过 `npx skills add` 或其他在线来源安装的第三方 skill：

1. 不复制或提交第三方 `SKILL.md` 本体。
2. 不提交第三方附带的 `scripts/`、`references/`、`assets/`、`evals/` 等内容。
3. 创建同名目录，并只写入 `AGENTS.md`。
4. `AGENTS.md` 必须记录来源仓库、原始 skill 路径和可执行的安装命令。
5. 来源不明确时，先查原项目的 `skills-lock.json`，不要猜测仓库地址。

## 编辑原则

- `SKILL.md` 应使用直接、可执行的操作说明，避免无关叙述。
- description 要清楚说明触发场景，避免与其他 skill 大面积重叠。
- 相对路径必须以当前 skill 目录为基准，并确保目标文件存在。
- 脚本应有明确的运行方式、依赖和错误提示。
- 修改已有 skill 时，不要顺带重构无关目录。
- README 只介绍能力和使用入口，不复制完整 skill 指令。

## 验证

本仓库没有统一构建命令。提交前按变更范围验证：

```bash
git status --short
git diff --check
find . -mindepth 2 -maxdepth 2 -name SKILL.md -print
```

还应完成以下检查：

- 所有自研 skill 都包含 `SKILL.md`。
- 所有外部安装指针都只包含 `AGENTS.md`，且安装命令完整。
- `SKILL.md` 中引用的 `scripts/`、`references/`、`templates/` 和 `assets/` 文件存在。
- 修改脚本后运行对应脚本或至少执行语法检查。
- 修改工作流后按文档示例完成一次端到端验证。
- README 中的目录名与实际一级目录一致。

如果某项验证因环境依赖无法执行，应在交付说明中明确记录。

## Git 规范

- 提交前检查完整 diff，避免混入无关文件。
- 提交信息使用中文，控制在 30 字以内。
- 一次提交应围绕同一批 skill 或同一类维护目标。
- 不改写或撤销其他人尚未提交的变更。
- 未经明确要求，不执行破坏性 Git 操作。
