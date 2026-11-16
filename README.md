# Skill 仓库

个人可公开复用的 AI Agent 技能与第三方安装指针。公司内部技能和用户级规则保存在公司仓库。

一级目录按维护归属保存：

- 自维护技能：完整保存 `SKILL.md` 及其引用的脚本、参考资料、模板和资源。
- 第三方技能：目录只保留 `AGENTS.md`，记录来源、原始路径、核对版本与恢复命令。

## 自维护技能

| Skill | 用途 |
| --- | --- |
| [abstraction-thinking](abstraction-thinking/SKILL.md) | 从产品、架构和流程问题中提取不变量，建立简洁模型，推导可复用的设计结论与适用边界。 |
| [anti-ai-doc-writing](anti-ai-doc-writing/SKILL.md) | 写作、改稿和评审时合并重复自证与防御性解释，将密集否定改写为清晰规则，保留事实与关键条件。 |
| [changeset-helper](changeset-helper/SKILL.md) | 管理 monorepo 的 Changesets 版本、变更记录和发布流程。 |
| [harness](harness/SKILL.md) | 指引 AI 协作项目所处阶段、当前产物和下一步。 |
| [harness-check](harness-check/SKILL.md) | 用脚本检查项目是否偏离既定系统设计流程。 |
| [harness-next](harness-next/SKILL.md) | 验证阶段产物后推进流程，并创建下一阶段模板。 |
| [immich-media-ingest](immich-media-ingest/SKILL.md) | 下载或导入媒体到 Immich，校验原件、复用重复素材、保存来源并回读核验入库结果。 |
| [incident-retrospective](incident-retrospective/SKILL.md) | 编写与更新故障复盘，明确发生、引入与恢复时间、影响范围、根因证据、修复对比和验收边界，支持图文 HTML 交付。 |
| [information-writing-strategy](information-writing-strategy/SKILL.md) | 在商业写作前明确受众、目标、核心信息、文章类型和详细提纲。 |
| [layered-architecture-diagram](layered-architecture-diagram/SKILL.md) | 生成横向泳道式分层技术架构图，并按飞书、Markdown、Draw.io、演示文稿等最终载体选择原生可编辑格式。 |
| [local-project-notes](local-project-notes/SKILL.md) | 将开发方案与交接文档保存在项目 `.local-notes/`，通过 Git 本地 exclude 排除提交，支持跨会话查找与续作。 |
| [migrate-postman-to-bruno](migrate-postman-to-bruno/SKILL.md) | 将 Postman 桌面工作区迁移为原生 Bruno collections。 |
| [miniature-explainer-video](miniature-explainer-video/SKILL.md) | 用 Blender 和 Python 制作微缩三维科普动画，包含分镜、人物与道具动作、图文、旁白、配乐和拟音，交付 MP4 与可编辑工程。 |
| [promptfoo-mastra-workflow-api](promptfoo-mastra-workflow-api/SKILL.md) | Create or update promptfoo evaluations and red-team tests that call Mastra workflow APIs over native HTTP/HTTPS. Use when Codex needs to test a Mastra workflow through `/custom/workflows/:workflowId`, add promptfoo YAML test cases, assert workflow response dat |
| [raycast-cleanup](raycast-cleanup/SKILL.md) | Audit and trim Raycast command clutter, identify low-value enabled commands and extensions, and provide safe UI paths for disabling commands. Use when the user asks to clean up Raycast, reduce enabled commands, disable AI Chat or Calculator, sync/export Raycas |
| [reader-first-tech-docs](reader-first-tech-docs/SKILL.md) | 围绕目标读者的问题设计技术文档主阅读路径，并通过附录保留可追溯的关键事实。 |
| [siddhartha-inbox-triage](siddhartha-inbox-triage/SKILL.md) | 为 Siddhartha 知识库筛选和判断 Inbox 笔记去向，不默认改写原文。 |
| [siddhartha-review](siddhartha-review/SKILL.md) | 为 Siddhartha 知识库生成低负担、先回忆后核对的复习候选。 |
| [siddhartha-wiki-audit](siddhartha-wiki-audit/SKILL.md) | 审计 Siddhartha wiki 的 metadata、类型边界、连接、索引和重复内容。 |
| [skill-manager](skill-manager/SKILL.md) | 为发现、创建、安装、同步和维护 skill 提供统一路由。 |
| [vscode-worktree-workflow](vscode-worktree-workflow/SKILL.md) | 用 VS Code multi-root workspace 和 Git worktree 组织多仓库、多需求并行开发。 |
| [writing-editor](writing-editor/SKILL.md) | 作为克制的第一读者 review 草稿，优先帮助作者自己修改。 |

`siddhartha-*` 依赖相应 Obsidian vault 的结构；其他环境依赖以技能入口为准。

## 第三方安装来源

每个技能进入对应 `AGENTS.md` 查看安装命令。固定提交用于恢复已核对的版本；更新时先确认来源和本机定制。历史安装记录缺失的部分条目使用经过内容核对的恢复来源，指针中注明依据。

本次索引包含 259 个第三方技能，按来源折叠展示：

<details>
<summary>@google/stitch（1 个）</summary>

- [stitch](stitch/AGENTS.md)

</details>

<details>
<summary>@volcengine/mediakit-cli（5 个）</summary>

- [byted-mediakit-audio](byted-mediakit-audio/AGENTS.md)
- [byted-mediakit-editing](byted-mediakit-editing/AGENTS.md)
- [byted-mediakit-image](byted-mediakit-image/AGENTS.md)
- [byted-mediakit-shared](byted-mediakit-shared/AGENTS.md)
- [byted-mediakit-video](byted-mediakit-video/AGENTS.md)

</details>

<details>
<summary>addyosmani/agent-skills（1 个）</summary>

- [planning-and-task-breakdown](planning-and-task-breakdown/AGENTS.md)

</details>

<details>
<summary>affaan-m/everything-claude-code（29 个）</summary>

- [agent-architecture-audit](agent-architecture-audit/AGENTS.md)
- [agent-introspection-debugging](agent-introspection-debugging/AGENTS.md)
- [ai-regression-testing](ai-regression-testing/AGENTS.md)
- [api-design](api-design/AGENTS.md)
- [backend-patterns](backend-patterns/AGENTS.md)
- [brand-discovery](brand-discovery/AGENTS.md)
- [brand-voice](brand-voice/AGENTS.md)
- [connections-optimizer](connections-optimizer/AGENTS.md)
- [content-engine](content-engine/AGENTS.md)
- [continuous-learning-v2](continuous-learning-v2/AGENTS.md)
- [crosspost](crosspost/AGENTS.md)
- [customer-billing-ops](customer-billing-ops/AGENTS.md)
- [e2e-testing](e2e-testing/AGENTS.md)
- [google-workspace-ops](google-workspace-ops/AGENTS.md)
- [lead-intelligence](lead-intelligence/AGENTS.md)
- [market-research](market-research/AGENTS.md)
- [marketing-campaign](marketing-campaign/AGENTS.md)
- [prompt-optimizer](prompt-optimizer/AGENTS.md)
- [remotion-video-creation](remotion-video-creation/AGENTS.md)
- [security-review](security-review/AGENTS.md)
- [security-scan](security-scan/AGENTS.md)
- [seo](seo/AGENTS.md)
- [skill-stocktake](skill-stocktake/AGENTS.md)
- [social-graph-ranker](social-graph-ranker/AGENTS.md)
- [social-publisher](social-publisher/AGENTS.md)
- [taste-application](taste-application/AGENTS.md)
- [taste-distillation](taste-distillation/AGENTS.md)
- [tdd-workflow](tdd-workflow/AGENTS.md)
- [video-editing](video-editing/AGENTS.md)

</details>

<details>
<summary>anthropics/knowledge-work-plugins（1 个）</summary>

- [data-visualization](data-visualization/AGENTS.md)

</details>

<details>
<summary>anthropics/skills（3 个）</summary>

- [doc-coauthoring](doc-coauthoring/AGENTS.md)
- [frontend-design](frontend-design/AGENTS.md)
- [skill-creator](skill-creator/AGENTS.md)

</details>

<details>
<summary>browser-use/video-use（1 个）</summary>

- [video-use](video-use/AGENTS.md)

</details>

<details>
<summary>cloudflare/vibesdk（1 个）</summary>

- [frontend-design-saas](frontend-design-saas/AGENTS.md)

</details>

<details>
<summary>ConardLi/garden-skills（6 个）</summary>

- [beautiful-article](beautiful-article/AGENTS.md)
- [gpt-image-2](gpt-image-2/AGENTS.md)
- [kb-retriever](kb-retriever/AGENTS.md)
- [motion-showreel](motion-showreel/AGENTS.md)
- [web-design-engineer](web-design-engineer/AGENTS.md)
- [web-video-presentation](web-video-presentation/AGENTS.md)

</details>

<details>
<summary>coreyhaines31/marketingskills（1 个）</summary>

- [content-strategy](content-strategy/AGENTS.md)

</details>

<details>
<summary>Dammyjay93/interface-design（1 个）</summary>

- [interface-design](interface-design/AGENTS.md)

</details>

<details>
<summary>drolosoft/immich-photo-manager（2 个）</summary>

- [album-manager](album-manager/AGENTS.md)
- [photo-search](photo-search/AGENTS.md)

</details>

<details>
<summary>dszdsxc19/hell-mode（1 个）</summary>

- [hell-challenge](hell-challenge/AGENTS.md)

</details>

<details>
<summary>elementalsouls/Claude-BugHunter（83 个）</summary>

- [apk-redteam-pipeline](apk-redteam-pipeline/AGENTS.md)
- [bb-local-toolkit](bb-local-toolkit/AGENTS.md)
- [bb-methodology](bb-methodology/AGENTS.md)
- [bug-bounty](bug-bounty/AGENTS.md)
- [bugcrowd-reporting](bugcrowd-reporting/AGENTS.md)
- [cloud-iam-deep](cloud-iam-deep/AGENTS.md)
- [enterprise-vpn-attack](enterprise-vpn-attack/AGENTS.md)
- [evidence-hygiene](evidence-hygiene/AGENTS.md)
- [hunt-api-misconfig](hunt-api-misconfig/AGENTS.md)
- [hunt-aspnet](hunt-aspnet/AGENTS.md)
- [hunt-ato](hunt-ato/AGENTS.md)
- [hunt-auth-bypass](hunt-auth-bypass/AGENTS.md)
- [hunt-brute-force](hunt-brute-force/AGENTS.md)
- [hunt-business-logic](hunt-business-logic/AGENTS.md)
- [hunt-cache-poison](hunt-cache-poison/AGENTS.md)
- [hunt-captcha-bypass](hunt-captcha-bypass/AGENTS.md)
- [hunt-cicd](hunt-cicd/AGENTS.md)
- [hunt-clickjacking](hunt-clickjacking/AGENTS.md)
- [hunt-cloud-misconfig](hunt-cloud-misconfig/AGENTS.md)
- [hunt-cors](hunt-cors/AGENTS.md)
- [hunt-csrf](hunt-csrf/AGENTS.md)
- [hunt-deserialization](hunt-deserialization/AGENTS.md)
- [hunt-dispatch](hunt-dispatch/AGENTS.md)
- [hunt-dom](hunt-dom/AGENTS.md)
- [hunt-exceptional-conditions](hunt-exceptional-conditions/AGENTS.md)
- [hunt-file-upload](hunt-file-upload/AGENTS.md)
- [hunt-fintech-graphql](hunt-fintech-graphql/AGENTS.md)
- [hunt-forgot-password](hunt-forgot-password/AGENTS.md)
- [hunt-graphql](hunt-graphql/AGENTS.md)
- [hunt-grpc](hunt-grpc/AGENTS.md)
- [hunt-host-header](hunt-host-header/AGENTS.md)
- [hunt-html-injection](hunt-html-injection/AGENTS.md)
- [hunt-http-smuggling](hunt-http-smuggling/AGENTS.md)
- [hunt-idor](hunt-idor/AGENTS.md)
- [hunt-jwt-crypto](hunt-jwt-crypto/AGENTS.md)
- [hunt-k8s](hunt-k8s/AGENTS.md)
- [hunt-laravel](hunt-laravel/AGENTS.md)
- [hunt-ldap](hunt-ldap/AGENTS.md)
- [hunt-lfi](hunt-lfi/AGENTS.md)
- [hunt-llm-ai](hunt-llm-ai/AGENTS.md)
- [hunt-mfa-bypass](hunt-mfa-bypass/AGENTS.md)
- [hunt-misc](hunt-misc/AGENTS.md)
- [hunt-nextjs](hunt-nextjs/AGENTS.md)
- [hunt-nodejs](hunt-nodejs/AGENTS.md)
- [hunt-nosqli](hunt-nosqli/AGENTS.md)
- [hunt-ntlm-info](hunt-ntlm-info/AGENTS.md)
- [hunt-oauth](hunt-oauth/AGENTS.md)
- [hunt-open-redirect](hunt-open-redirect/AGENTS.md)
- [hunt-race-condition](hunt-race-condition/AGENTS.md)
- [hunt-rag-vector](hunt-rag-vector/AGENTS.md)
- [hunt-rce](hunt-rce/AGENTS.md)
- [hunt-saml](hunt-saml/AGENTS.md)
- [hunt-session](hunt-session/AGENTS.md)
- [hunt-shadow-api](hunt-shadow-api/AGENTS.md)
- [hunt-sharepoint](hunt-sharepoint/AGENTS.md)
- [hunt-source-leak](hunt-source-leak/AGENTS.md)
- [hunt-spa-api](hunt-spa-api/AGENTS.md)
- [hunt-springboot](hunt-springboot/AGENTS.md)
- [hunt-sqli](hunt-sqli/AGENTS.md)
- [hunt-ssrf](hunt-ssrf/AGENTS.md)
- [hunt-ssti](hunt-ssti/AGENTS.md)
- [hunt-subdomain](hunt-subdomain/AGENTS.md)
- [hunt-tls-network](hunt-tls-network/AGENTS.md)
- [hunt-websocket](hunt-websocket/AGENTS.md)
- [hunt-xss](hunt-xss/AGENTS.md)
- [hunt-xxe](hunt-xxe/AGENTS.md)
- [ios-redteam-pipeline](ios-redteam-pipeline/AGENTS.md)
- [m365-entra-attack](m365-entra-attack/AGENTS.md)
- [meme-coin-audit](meme-coin-audit/AGENTS.md)
- [mid-engagement-ir-detection](mid-engagement-ir-detection/AGENTS.md)
- [offensive-osint](offensive-osint/AGENTS.md)
- [okta-attack](okta-attack/AGENTS.md)
- [osint-methodology](osint-methodology/AGENTS.md)
- [recon-scope-triage](recon-scope-triage/AGENTS.md)
- [redteam-mindset](redteam-mindset/AGENTS.md)
- [redteam-report-template](redteam-report-template/AGENTS.md)
- [report-writing](report-writing/AGENTS.md)
- [security-arsenal](security-arsenal/AGENTS.md)
- [supply-chain-attack-recon](supply-chain-attack-recon/AGENTS.md)
- [triage-validation](triage-validation/AGENTS.md)
- [vmware-vcenter-attack](vmware-vcenter-attack/AGENTS.md)
- [web2-recon](web2-recon/AGENTS.md)
- [web3-audit](web3-audit/AGENTS.md)

</details>

<details>
<summary>github/awesome-copilot（3 个）</summary>

- [documentation-writer](documentation-writer/AGENTS.md)
- [draw-io-diagram-generator](draw-io-diagram-generator/AGENTS.md)
- [excalidraw-diagram-generator](excalidraw-diagram-generator/AGENTS.md)

</details>

<details>
<summary>https://aihot.news/aihot-skill/（1 个）</summary>

- [aihot](aihot/AGENTS.md)

</details>

<details>
<summary>https://liblibai-web-static.liblib.cloud/cli/1.0.2/libtv-cli-skill.zip（1 个）</summary>

- [libtv-cli](libtv-cli/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-approval/SKILL.md（1 个）</summary>

- [lark-approval](lark-approval/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-apps/SKILL.md（1 个）</summary>

- [lark-apps](lark-apps/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-attendance/SKILL.md（1 个）</summary>

- [lark-attendance](lark-attendance/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-base/SKILL.md（1 个）</summary>

- [lark-base](lark-base/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-calendar/SKILL.md（1 个）</summary>

- [lark-calendar](lark-calendar/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-contact/SKILL.md（1 个）</summary>

- [lark-contact](lark-contact/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-doc/SKILL.md（1 个）</summary>

- [lark-doc](lark-doc/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-drive/SKILL.md（1 个）</summary>

- [lark-drive](lark-drive/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-event/SKILL.md（1 个）</summary>

- [lark-event](lark-event/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-im/SKILL.md（1 个）</summary>

- [lark-im](lark-im/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-mail/SKILL.md（1 个）</summary>

- [lark-mail](lark-mail/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-markdown/SKILL.md（1 个）</summary>

- [lark-markdown](lark-markdown/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-minutes/SKILL.md（1 个）</summary>

- [lark-minutes](lark-minutes/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-note/SKILL.md（1 个）</summary>

- [lark-note](lark-note/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-okr/SKILL.md（1 个）</summary>

- [lark-okr](lark-okr/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-openapi-explorer/SKILL.md（1 个）</summary>

- [lark-openapi-explorer](lark-openapi-explorer/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-shared/SKILL.md（1 个）</summary>

- [lark-shared](lark-shared/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-sheets/SKILL.md（1 个）</summary>

- [lark-sheets](lark-sheets/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-skill-maker/SKILL.md（1 个）</summary>

- [lark-skill-maker](lark-skill-maker/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-slides/SKILL.md（1 个）</summary>

- [lark-slides](lark-slides/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-task/SKILL.md（1 个）</summary>

- [lark-task](lark-task/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-vc-agent/SKILL.md（1 个）</summary>

- [lark-vc-agent](lark-vc-agent/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-vc/SKILL.md（1 个）</summary>

- [lark-vc](lark-vc/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-whiteboard/SKILL.md（1 个）</summary>

- [lark-whiteboard](lark-whiteboard/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-wiki/SKILL.md（1 个）</summary>

- [lark-wiki](lark-wiki/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-workflow-meeting-summary/SKILL.md（1 个）</summary>

- [lark-workflow-meeting-summary](lark-workflow-meeting-summary/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/.well-known/skills/lark-workflow-standup-report/SKILL.md（1 个）</summary>

- [lark-workflow-standup-report](lark-workflow-standup-report/AGENTS.md)

</details>

<details>
<summary>https://open.feishu.cn/lark-cli/skills/regular（1 个）</summary>

- [lark-meeting](lark-meeting/AGENTS.md)

</details>

<details>
<summary>https://vefaas-cli.tos-cn-beijing.volces.com/skills/（1 个）</summary>

- [vefaas](vefaas/AGENTS.md)

</details>

<details>
<summary>hypit-ai/hypit（1 个）</summary>

- [hypit](hypit/AGENTS.md)

</details>

<details>
<summary>JimLiu/baoyu-skills（3 个）</summary>

- [baoyu-diagram](baoyu-diagram/AGENTS.md)
- [baoyu-infographic](baoyu-infographic/AGENTS.md)
- [baoyu-xhs-images](baoyu-xhs-images/AGENTS.md)

</details>

<details>
<summary>kepano/obsidian-skills（4 个）</summary>

- [defuddle](defuddle/AGENTS.md)
- [obsidian-bases](obsidian-bases/AGENTS.md)
- [obsidian-cli](obsidian-cli/AGENTS.md)
- [obsidian-markdown](obsidian-markdown/AGENTS.md)

</details>

<details>
<summary>libtv-labs/libtv-skills（1 个）</summary>

- [libtv-skill](libtv-skill/AGENTS.md)

</details>

<details>
<summary>MapleShaw/yt-dlp-downloader-skill（1 个）</summary>

- [yt-dlp-downloader](yt-dlp-downloader/AGENTS.md)

</details>

<details>
<summary>mastra-ai/skills（1 个）</summary>

- [mastra](mastra/AGENTS.md)

</details>

<details>
<summary>mattpocock/skills（42 个）</summary>

- [ask-matt](ask-matt/AGENTS.md)
- [batch-grill-me](batch-grill-me/AGENTS.md)
- [claude-handoff](claude-handoff/AGENTS.md)
- [code-review](code-review/AGENTS.md)
- [codebase-design](codebase-design/AGENTS.md)
- [design-an-interface](design-an-interface/AGENTS.md)
- [diagnosing-bugs](diagnosing-bugs/AGENTS.md)
- [domain-modeling](domain-modeling/AGENTS.md)
- [edit-article](edit-article/AGENTS.md)
- [git-guardrails-claude-code](git-guardrails-claude-code/AGENTS.md)
- [grill-me](grill-me/AGENTS.md)
- [grill-with-docs](grill-with-docs/AGENTS.md)
- [grilling](grilling/AGENTS.md)
- [handoff](handoff/AGENTS.md)
- [implement](implement/AGENTS.md)
- [improve-codebase-architecture](improve-codebase-architecture/AGENTS.md)
- [loop-me](loop-me/AGENTS.md)
- [migrate-to-shoehorn](migrate-to-shoehorn/AGENTS.md)
- [obsidian-vault](obsidian-vault/AGENTS.md)
- [prototype](prototype/AGENTS.md)
- [qa](qa/AGENTS.md)
- [request-refactor-plan](request-refactor-plan/AGENTS.md)
- [research](research/AGENTS.md)
- [resolving-merge-conflicts](resolving-merge-conflicts/AGENTS.md)
- [scaffold-exercises](scaffold-exercises/AGENTS.md)
- [setup-matt-pocock-skills](setup-matt-pocock-skills/AGENTS.md)
- [setup-pre-commit](setup-pre-commit/AGENTS.md)
- [setup-ts-deep-modules](setup-ts-deep-modules/AGENTS.md)
- [tdd](tdd/AGENTS.md)
- [teach](teach/AGENTS.md)
- [to-questionnaire](to-questionnaire/AGENTS.md)
- [to-spec](to-spec/AGENTS.md)
- [to-tickets](to-tickets/AGENTS.md)
- [triage](triage/AGENTS.md)
- [ubiquitous-language](ubiquitous-language/AGENTS.md)
- [wayfinder](wayfinder/AGENTS.md)
- [wizard](wizard/AGENTS.md)
- [writing-beats](writing-beats/AGENTS.md)
- [writing-for-agents](writing-for-agents/AGENTS.md)
- [writing-fragments](writing-fragments/AGENTS.md)
- [writing-great-skills](writing-great-skills/AGENTS.md)
- [writing-shape](writing-shape/AGENTS.md)

</details>

<details>
<summary>nextlevelbuilder/ui-ux-pro-max-skill（1 个）</summary>

- [ui-ux-pro-max](ui-ux-pro-max/AGENTS.md)

</details>

<details>
<summary>op7418/guizang-ppt-skill（1 个）</summary>

- [guizang-ppt-skill](guizang-ppt-skill/AGENTS.md)

</details>

<details>
<summary>op7418/guizang-social-card-skill（1 个）</summary>

- [guizang-social-card-skill](guizang-social-card-skill/AGENTS.md)

</details>

<details>
<summary>phuryn/pm-skills（1 个）</summary>

- [brainstorm-okrs](brainstorm-okrs/AGENTS.md)

</details>

<details>
<summary>remotion-dev/skills（1 个）</summary>

- [remotion-best-practices](remotion-best-practices/AGENTS.md)

</details>

<details>
<summary>Ruphiller/whistle-config（1 个）</summary>

- [whistle-config](whistle-config/AGENTS.md)

</details>

<details>
<summary>slidevjs/slidev（1 个）</summary>

- [slidev](slidev/AGENTS.md)

</details>

<details>
<summary>vercel-labs/agent-skills（2 个）</summary>

- [vercel-react-best-practices](vercel-react-best-practices/AGENTS.md)
- [web-design-guidelines](web-design-guidelines/AGENTS.md)

</details>

<details>
<summary>vercel-labs/json-render（1 个）</summary>

- [remotion](remotion/AGENTS.md)

</details>

<details>
<summary>vercel-labs/skills（1 个）</summary>

- [find-skills](find-skills/AGENTS.md)

</details>

<details>
<summary>volcengine/ark-cli（4 个）</summary>

- [arkcli-agent](arkcli-agent/AGENTS.md)
- [arkcli-auth](arkcli-auth/AGENTS.md)
- [arkcli-billing](arkcli-billing/AGENTS.md)
- [arkcli-pricing](arkcli-pricing/AGENTS.md)

</details>

<details>
<summary>volcengine/volcengine-skills（15 个）</summary>

- [volcengine-api](volcengine-api/AGENTS.md)
- [volcengine-cli](volcengine-cli/AGENTS.md)
- [volcengine-compliance](volcengine-compliance/AGENTS.md)
- [volcengine-db-supabase](volcengine-db-supabase/AGENTS.md)
- [volcengine-deploy](volcengine-deploy/AGENTS.md)
- [volcengine-find-skills](volcengine-find-skills/AGENTS.md)
- [volcengine-iac](volcengine-iac/AGENTS.md)
- [volcengine-knowledge-search](volcengine-knowledge-search/AGENTS.md)
- [volcengine-landing-zone](volcengine-landing-zone/AGENTS.md)
- [volcengine-prepare](volcengine-prepare/AGENTS.md)
- [volcengine-sale](volcengine-sale/AGENTS.md)
- [volcengine-sdk-generator](volcengine-sdk-generator/AGENTS.md)
- [volcengine-tosutil](volcengine-tosutil/AGENTS.md)
- [volcengine-troubleshooting](volcengine-troubleshooting/AGENTS.md)
- [volcengine-vefaas](volcengine-vefaas/AGENTS.md)

</details>

<details>
<summary>wheresryan22/anatomy（1 个）</summary>

- [anatomy](anatomy/AGENTS.md)

</details>

<details>
<summary>wshobson/agents（2 个）</summary>

- [data-storytelling](data-storytelling/AGENTS.md)
- [openapi-spec-generation](openapi-spec-generation/AGENTS.md)

</details>

<details>
<summary>zarazhangrui/frontend-slides（1 个）</summary>

- [frontend-slides](frontend-slides/AGENTS.md)

</details>

<details>
<summary>ZzzLc0405/photo-abstract-editorial（1 个）</summary>

- [photo-abstract-editorial](photo-abstract-editorial/AGENTS.md)

</details>

<details>
<summary>微信开发者工具 App 内置 skill（1 个）</summary>

- [wechatide-skill](wechatide-skill/AGENTS.md)

</details>

## 插件

通过插件分发的技能由各自管理器维护，恢复方式见[插件安装指针](PLUGINS.md)。插件缓存与 system 技能不复制到本仓库。

## 使用与维护

按任务选择技能：自维护目录读取 `SKILL.md`，第三方目录读取 `AGENTS.md`。安装、升级与仓库同步分别执行；同步来源记录会保留本机正在使用的版本和定制。

提交前核对实际目录与索引、相对引用、安装命令语法和敏感信息；脚本变更按影响范围验证。
