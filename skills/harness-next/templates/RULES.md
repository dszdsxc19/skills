# 开发规则

> **阶段定位**：Harness 构建阶段产出。告诉 Agent（和人类）具体的编码约束。

---

## 代码规范

### 语言 / 框架版本

- 语言：[语言名] [版本]
- 框架：[框架名] [版本]
- 包管理器：

### 命名规范

- 变量/函数：camelCase
- 类/组件：PascalCase
- 常量：UPPER_SNAKE_CASE
- 文件：kebab-case

### 目录结构

```
src/
├── [模块 A]/
│   ├── [模块A].controller.ts
│   ├── [模块A].service.ts
│   └── [模块A].test.ts
└── shared/
    ├── types/
    └── utils/
```

---

## 架构约束

- **禁止**：跨层直接调用（如 Controller 直接操作数据库）
- **禁止**：在 Service 层引入 HTTP 相关逻辑
- **要求**：所有对外接口必须使用 `docs/API_SPEC.md` 定义的响应格式

---

## 测试要求

- 新功能必须有单元测试
- 覆盖率不低于 **[X]%**
- 测试文件命名：`[filename].test.ts`
- 运行测试：`[测试命令]`

---

## 提交规范

遵循 Conventional Commits：

| 类型 | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): add JWT refresh token` |
| `fix` | 修复 bug | `fix(api): handle empty input edge case` |
| `docs` | 文档更新 | `docs: update API_SPEC for user endpoint` |
| `refactor` | 重构（不改功能） | `refactor(service): extract validation logic` |
| `test` | 测试相关 | `test(user): add unit tests for register flow` |
| `chore` | 构建/工具 | `chore: update dependencies` |

---

## PR / 代码审查

- PR 标题遵循提交规范
- 描述中说明：做了什么 / 为什么这样做 / 如何测试
- 合并前必须通过 CI（lint + tests）
