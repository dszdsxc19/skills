---
name: changeset-helper
description: 用于管理 monorepo 的 changeset 版本发布流程。当用户需要发布包、更新版本号、或创建变更记录时使用此技能。支持 add、version、publish 三个步骤，支持 patch/minor/major 和 alpha/beta/rc 版本类型。自动从 package.json 读取可用包列表，默认选择 @ai-buddy/sdk。
---

# Changeset Helper

帮助用户使用 Changeset 进行版本管理和发布。此技能引导用户完成完整的发布流程：创建变更记录、更新版本号、构建和发布。

## 重要说明

- **changeset add 是交互式命令**，在非交互环境中会失败。需要手动创建 changeset 文件。
- **每步完成后必须询问用户是否继续**
- **最终必须保存完整的执行记录到输出文件**

## 工作流程

按顺序执行以下步骤：

### 1. 读取可用包列表

首先读取根目录的 `package.json`，获取 `workspaces` 中定义的所有包。默认选择 `@ai-buddy/sdk`。

```bash
# 读取 package.json
cat /Users/admin/Desktop/ai/ymm-llms-chat/package.json
```

可用的包通常包括：
- `@ai-buddy/sdk`
- `@ai-buddy/ui`
- `@ai-buddy/web`

### 2. 向用户确认参数

使用 AskUserQuestion 工具向用户确认：

**包选择**（默认 @ai-buddy/sdk）

**变更类型**：
- `patch` - 修复 bug（1.0.0 → 1.0.1）
- `minor` - 新功能（1.0.0 → 1.1.0）
- `major` - 破坏性变更（1.0.0 → 2.0.0）
- `alpha` - 内部测试版（0.1.0-alpha.0）
- `beta` - 公开测试版（0.1.0-beta.0）
- `rc` - 发布候选版（0.1.0-rc.0）

**变更描述**：简要描述本次变更的内容

### 3. 执行 changeset add

**重要**: `yarn changeset add` 是交互式命令，在非交互环境中会失败。

**方法 1: 交互式命令（仅在 TTY 环境中）**
```bash
yarn changeset add
```

**方法 2: 直接创建文件（推荐）**
```bash
# 创建 changeset 文件
cat > .changeset/CHANGE_NAME.md << 'EOF'
---
"@ai-buddy/sdk": patch
---

变更描述内容
EOF
```

替换 `CHANGE_NAME` 为描述性名称，如 `fix-widget-bug`、`add-feature-x` 等。

完成后询问用户：**"changeset 文件已创建，是否继续执行 version？"**

### 4. 执行 changeset version

根据 changeset 文件更新版本号。

**正式版本**:
```bash
yarn changeset version --since @ai-buddy/sdk
```

**预发布版本** (alpha/beta/rc):
```bash
yarn changeset version --snapshot alpha --since @ai-buddy/sdk
```

**效果**:
- 读取 `.changeset/*.md` 文件
- 更新 `packages/sdk/package.json` 中的版本号
- 更新 `CHANGELOG.md`
- 消耗已应用的 changeset 文件

**注意**：
- 预发布版本会生成时间戳格式（如 `0.0.0-alpha-20260311092323`）
- 如需标准格式（如 `0.2.0-alpha-0`），需手动修改 `package.json`

完成后询问用户：**"版本号已更新，是否继续构建和发布？"**

### 5. 构建并发布

**构建命令**:
```bash
yarn build:sdk
```

**发布命令**:
```bash
yarn workspace @ai-buddy/sdk publish --registry https://npm.amh-group.com/
```

**快捷命令**（如果 package.json 中已配置）:
```bash
# Alpha 版本一键发布
yarn publish:sdk:alpha

# Beta 版本
yarn publish:sdk:beta

# RC 版本
yarn publish:sdk:rc

# 正式版本
yarn publish:sdk
```

### 6. 显示发布结果

发布成功后，必须显示 npm 包地址：

```
发布成功！

包名: @ai-buddy/sdk
版本: 0.2.0-alpha-0
地址: https://npm.amh-group.com/-/web/detail/@ai-buddy/sdk
```

### 7. 保存执行记录

**必须将完整的执行记录保存到输出文件**。

使用 Write 工具保存 transcript，包含：
- 任务概述
- 每个步骤的命令和结果
- 版本变化详情
- 构建和发布命令
- 常见问题排查
- 参考文档链接

输出文件路径：`<workspace>/iteration-<N>/eval-<ID>-with_skill/outputs/transcript.txt`

## 常用命令参考

| 命令 | 用途 |
|------|------|
| `yarn changeset add` | 创建变更记录（交互式） |
| `yarn changeset version --since <pkg>` | 更新正式版本 |
| `yarn changeset version --snapshot alpha --since <pkg>` | 更新 alpha 版本 |
| `yarn build:sdk` | 构建 SDK |
| `yarn workspace <pkg> publish --registry <url>` | 发布包 |

## 版本号规则

| 类型 | 说明 | 示例 |
|------|------|------|
| patch | 修复 bug，向后兼容 | 1.0.0 → 1.0.1 |
| minor | 新功能，向后兼容 | 1.0.0 → 1.1.0 |
| major | 破坏性变更 | 1.0.0 → 2.0.0 |
| alpha | 内部测试 | 0.1.0-alpha.0 |
| beta | 公开测试 | 0.1.0-beta.0 |
| rc | 发布候选 | 0.1.0-rc.0 |

## 注意事项

1. `add` 和 `version` 是独立步骤，不要在一次操作中完成
2. 每步完成后**必须**询问用户是否继续
3. 交互式命令失败时使用手动创建文件的方式
4. 预发布版本可能需要手动调整版本号格式
5. **必须保存完整的执行记录到输出文件**

## 测试环境特殊说明

在测试环境中，由于无法执行交互式命令和实际的发布操作：
- 手动创建 changeset 文件代替 `yarn changeset add`
- 可以执行 `yarn changeset version`（非交互式）
- **仅展示**构建和发布命令，**不实际执行**
- **必须保存**完整的执行记录
