# Skill 仓库

这是一个可复用的 AI Agent Skill 仓库，用来沉淀稳定的工作流程、判断规则、脚本和参考资料。

每个一级目录代表一个独立 skill，入口通常是 `SKILL.md`。部分 skill 还包含：

- `scripts/`：可执行的检查、扫描或迁移脚本
- `references/`：按需读取的详细参考资料
- `templates/`：流程模板
- `agents/`：Agent 展示或运行配置
- `evals/`：触发和输出质量评测

## Obsidian 与知识库

| Skill | 用途 |
| --- | --- |
| `obsidian-bases` | 创建和维护 Obsidian Bases，包括筛选、公式、视图和汇总。 |
| `obsidian-cli` | 通过 Obsidian CLI 搜索、读取和管理笔记，也支持插件与主题调试。 |
| `obsidian-markdown` | 创建符合 Obsidian 语法的 Markdown，包括 wikilink、嵌入、callout 和 properties。 |
| `siddhartha-inbox-triage` | 为 Siddhartha 知识库筛选和判断 Inbox 笔记去向，不默认改写原文。 |
| `siddhartha-review` | 为 Siddhartha 知识库生成低负担、先回忆后核对的复习候选。 |
| `siddhartha-wiki-audit` | 审计 Siddhartha wiki 的 metadata、类型边界、连接、索引和重复内容。 |

`siddhartha-*` skills 需要在 Siddhartha vault 根目录运行，并依赖其 `AGENTS.md` 和固定目录结构。

## 写作与内容

| Skill | 用途 |
| --- | --- |
| `content-strategy` | 规划内容支柱、主题集群、优先级和内容路线图。 |
| `data-storytelling` | 把数据分析组织成面向决策的叙事、图表和行动建议。 |
| `documentation-writer` | 按 Diátaxis 框架设计教程、操作指南、参考和解释型文档。 |
| `information-writing-strategy` | 在商业写作前明确受众、目标、核心信息、文章类型和详细提纲。 |
| `writing-beats` | 从原始材料中逐个选择和写作叙事 beat，逐步形成文章。 |
| `writing-editor` | 作为克制的第一读者 review 草稿，优先帮助作者自己修改。 |
| `writing-fragments` | 通过追问收集异质写作片段，为后续文章积累原材料。 |

## 工程与流程

| Skill | 用途 |
| --- | --- |
| `changeset-helper` | 管理 monorepo 的 Changesets 版本、变更记录和发布流程。 |
| `defuddle` | 使用 Defuddle CLI 从网页提取干净 Markdown，减少页面噪声。 |
| `harness` | 指引 AI 协作项目所处阶段、当前产物和下一步。 |
| `harness-check` | 用脚本检查项目是否偏离既定系统设计流程。 |
| `harness-next` | 验证阶段产物后推进流程，并创建下一阶段模板。 |
| `migrate-postman-to-bruno` | 将 Postman 桌面工作区迁移为原生 Bruno collections。 |

## Skill 管理

| Skill | 用途 |
| --- | --- |
| `find-skills` | 从公开生态中发现适合特定任务的现成 skill。 |
| `skill-creator` | 创建、改进和评测 skill。 |
| `skill-manager` | 为发现、创建、安装、同步和维护 skill 提供统一路由。 |

## 使用方式

将需要的 skill 目录复制或链接到 Agent 支持的 skills 目录。不同工具的加载位置可能不同，使用前应确认目标工具的约定。

阅读顺序：

1. 先根据任务匹配 skill 的用途。
2. 完整读取该目录下的 `SKILL.md`。
3. 按 `SKILL.md` 指引，仅在需要时读取 `references/`、运行 `scripts/` 或使用模板。

有外部依赖的 skill 会在自己的 `SKILL.md` 中说明前置条件，例如 `defuddle` 需要 Defuddle CLI，`obsidian-cli` 需要运行中的 Obsidian。
