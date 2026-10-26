# Abstraction Thinking / First-Principles Modeling

一个可复用的 Agent Skill：识别不同场景中的不变量，将复杂问题压缩为简洁的函数、状态机或关系模型，并由此推导可复用的产品/架构结论及适用边界。

## 何时使用

- 多个具体业务或技术形态，想寻找统一抽象。
- 设计 Capability、Adapter、Execution、Batch 等通用机制。
- 讨论系统的“本质是什么”，希望用一个模型解释。
- 需要从概念模型推导架构边界、产品形态或演进路径。
- 希望将某领域发现的规律迁移到另一个领域。

## 何时不使用

简单问答、单纯计算、翻译润色、确定性的操作/修复任务，或形式化不能带来新洞察的情况。

## 安装

解压后会得到 `abstraction-thinking/` 文件夹，其中 `SKILL.md` 是必需入口文件。

- **Codex（当前仓库）**：将文件夹放到 `<项目根目录>/.agents/skills/abstraction-thinking/`。
- **Codex（用户级）**：放到 `~/.agents/skills/abstraction-thinking/`。
- **Claude Code（当前项目）**：放到 `<项目根目录>/.claude/skills/abstraction-thinking/`。
- **Claude Code（用户级）**：放到 `~/.claude/skills/abstraction-thinking/`。

重启相应工具或重新加载会话（如未自动识别）。Skill 是否自动触发由宿主的技能发现与匹配机制决定，不能保证每次必定触发。

## 如何触发

**自动触发**：在有复杂抽象需求的对话中，宿主可依据 `SKILL.md` 的 `description` 选择此 Skill。

**显式触发**：

- Codex：在对话中提及 `$abstraction-thinking`。
- Claude Code：在支持的界面使用 `/abstraction-thinking`，或明确要求使用该 Skill。

示例请求：

> 这些 API、Agent 和画布工作流，是否存在相同的执行契约？请用最小的模型解释，并推导接口设计。

> 我们刚讨论了几个产品，能不能提炼它们真正相同的底层结构？指出一个反例。

## 文件说明

- `SKILL.md`：主要指令、触发条件和五步建模流程。
- `references/modeling-playbook.md`：选择模型、严谨性检查及工程化边界。
- `references/examples.md`：对话实例和反例。
- `references/trigger-cases.md`：应触发、不应触发的测试样例。

此 Skill 仅包含提示指令和参考资料，无可执行脚本、第三方依赖或外部服务调用。

标准格式参考：Agent Skills Specification（https://agentskills.io/specification）、OpenAI Build Skills（https://learn.chatgpt.com/docs/build-skills）。
