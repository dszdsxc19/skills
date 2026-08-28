# Skill 仓库

这是一个可复用的 AI Agent Skill 仓库，用来沉淀稳定的工作流程、判断规则、脚本和参考资料。

一级目录包含两类内容：

- **本仓库维护**：目录中包含完整 `SKILL.md` 和必要的配套文件。
- **外部安装**：目录中只保留 `AGENTS.md`，记录来源和 `npx skills add` 命令，不复制第三方本体。

本仓库维护的 skill 可能包含：

- `scripts/`：可执行的检查、扫描或迁移脚本
- `references/`：按需读取的详细参考资料
- `templates/`：流程模板
- `agents/`：Agent 展示或运行配置
- `evals/`：触发和输出质量评测

## Obsidian 与知识库

| Skill | 类型 | 用途 |
| --- | --- | --- |
| `obsidian-bases` | 外部安装 | 创建和维护 Obsidian Bases，包括筛选、公式、视图和汇总。 |
| `obsidian-cli` | 外部安装 | 通过 Obsidian CLI 搜索、读取和管理笔记，也支持插件与主题调试。 |
| `obsidian-markdown` | 外部安装 | 创建符合 Obsidian 语法的 Markdown，包括 wikilink、嵌入、callout 和 properties。 |
| `siddhartha-inbox-triage` | 本仓库维护 | 为 Siddhartha 知识库筛选和判断 Inbox 笔记去向，不默认改写原文。 |
| `siddhartha-review` | 本仓库维护 | 为 Siddhartha 知识库生成低负担、先回忆后核对的复习候选。 |
| `siddhartha-wiki-audit` | 本仓库维护 | 审计 Siddhartha wiki 的 metadata、类型边界、连接、索引和重复内容。 |

`siddhartha-*` skills 需要在 Siddhartha vault 根目录运行，并依赖其 `AGENTS.md` 和固定目录结构。

## 写作与内容

| Skill | 类型 | 用途 |
| --- | --- | --- |
| `content-strategy` | 外部安装 | 规划内容支柱、主题集群、优先级和内容路线图。 |
| `data-storytelling` | 外部安装 | 把数据分析组织成面向决策的叙事、图表和行动建议。 |
| `documentation-writer` | 外部安装 | 按 Diátaxis 框架设计教程、操作指南、参考和解释型文档。 |
| `information-writing-strategy` | 本仓库维护 | 在商业写作前明确受众、目标、核心信息、文章类型和详细提纲。 |
| `writing-beats` | 外部安装 | 从原始材料中逐个选择和写作叙事 beat，逐步形成文章。 |
| `writing-editor` | 本仓库维护 | 作为克制的第一读者 review 草稿，优先帮助作者自己修改。 |
| `writing-fragments` | 外部安装 | 通过追问收集异质写作片段，为后续文章积累原材料。 |

## 工程与流程

| Skill | 类型 | 用途 |
| --- | --- | --- |
| `argos-dashboard` | 本仓库维护 | 创建、重构并验证高质量 Argos 看板，支持接口 Method 联动筛选与 SLI 指标整理。 |
| `auto-agentic-postgres-change` | 本仓库维护 | 安全设计、执行和验证 auto-agentic-app 共享 PostgreSQL 的 Schema 与数据变更。 |
| `changeset-helper` | 本仓库维护 | 管理 monorepo 的 Changesets 版本、变更记录和发布流程。 |
| `defuddle` | 外部安装 | 使用 Defuddle CLI 从网页提取干净 Markdown，减少页面噪声。 |
| `harness` | 本仓库维护 | 指引 AI 协作项目所处阶段、当前产物和下一步。 |
| `harness-check` | 本仓库维护 | 用脚本检查项目是否偏离既定系统设计流程。 |
| `harness-next` | 本仓库维护 | 验证阶段产物后推进流程，并创建下一阶段模板。 |
| `migrate-postman-to-bruno` | 本仓库维护 | 将 Postman 桌面工作区迁移为原生 Bruno collections。 |
| `research-internal-services` | 本仓库维护 | 调研内部服务现状与关键链路，形成证据化、复用优先的最小技术方案。 |
| `vscode-worktree-workflow` | 本仓库维护 | 用 VS Code multi-root workspace 和 Git worktree 组织多仓库、多需求并行开发。 |

## Skill 管理

| Skill | 类型 | 用途 |
| --- | --- | --- |
| `find-skills` | 本仓库维护 | 从公开生态中发现适合特定任务的现成 skill。 |
| `skill-creator` | 本仓库维护 | 创建、改进和评测 skill。 |
| `skill-manager` | 本仓库维护 | 为发现、创建、安装、同步和维护 skill 提供统一路由。 |

## Codex 用户级同步清单

以下目录是从本机 Codex 用户层同步来的外部安装指针，只保存来源与安装命令，不复制第三方 skill 本体。内置 system skill 和插件缓存不在此清单中。

| 来源 | Skills |
| --- | --- |
| `@bytedance-dev/bytedcli 内置 skill` | `bytedcli` |
| `addyosmani/agent-skills` | `planning-and-task-breakdown` |
| `anthropics/skills` | `doc-coauthoring`、`frontend-design` |
| `JimLiu/baoyu-skills` | `baoyu-xhs-images` |
| `mastra-ai/skills` | `mastra` |
| `mattpocock/skills` | `ask-matt`、`batch-grill-me`、`claude-handoff`、`code-review`、`codebase-design`、`design-an-interface`、`diagnosing-bugs`、`domain-modeling`<br>`edit-article`、`git-guardrails-claude-code`、`grill-me`、`grill-with-docs`、`grilling`、`handoff`、`implement`、`improve-codebase-architecture`<br>`loop-me`、`migrate-to-shoehorn`、`obsidian-vault`、`prototype`、`qa`、`request-refactor-plan`、`research`、`resolving-merge-conflicts`<br>`scaffold-exercises`、`setup-matt-pocock-skills`、`setup-pre-commit`、`setup-ts-deep-modules`、`tdd`、`teach`、`to-questionnaire`、`to-spec`<br>`to-tickets`、`triage`、`ubiquitous-language`、`wayfinder`、`wizard`、`writing-great-skills`、`writing-shape` |
| `nextlevelbuilder/ui-ux-pro-max-skill` | `ui-ux-pro-max` |
| `op7418/guizang-social-card-skill` | `guizang-social-card-skill` |
| `open.feishu.cn well-known` | `lark-approval`、`lark-apps`、`lark-attendance`、`lark-base`、`lark-calendar`、`lark-contact`、`lark-doc`、`lark-drive`<br>`lark-event`、`lark-im`、`lark-mail`、`lark-markdown`、`lark-minutes`、`lark-note`、`lark-okr`、`lark-openapi-explorer`<br>`lark-shared`、`lark-sheets`、`lark-skill-maker`、`lark-slides`、`lark-task`、`lark-vc`、`lark-vc-agent`、`lark-whiteboard`<br>`lark-wiki`、`lark-workflow-meeting-summary`、`lark-workflow-standup-report` |
| `skills.byted.org/stone/fornax` | `fornax-cli` |
| `vercel-labs/agent-skills` | `vercel-react-best-practices`、`web-design-guidelines` |
| `wshobson/agents` | `openapi-spec-generation` |
| `微信开发者工具 App 内置 skill` | `wechatide-skill` |

其中 10 个 `mattpocock/skills` skill 已从上游主分支删除；对应指针固定到删除前提交，避免安装地址失效。

## 使用方式

本仓库维护的 skill 可以复制、链接或通过仓库地址安装。外部 skill 应进入对应目录查看 `AGENTS.md`，再执行其中的 `npx skills add` 命令。

阅读顺序：

1. 先根据任务匹配 skill 的用途。
2. 如果目录中有 `SKILL.md`，完整读取并按需使用配套文件。
3. 如果目录中只有 `AGENTS.md`，按说明从原始来源安装。

有外部依赖的 skill 会在自己的 `SKILL.md` 中说明前置条件，例如 `defuddle` 需要 Defuddle CLI，`obsidian-cli` 需要运行中的 Obsidian。
