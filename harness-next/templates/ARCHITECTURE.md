# 系统架构约束

> **阶段定位**：Harness 构建阶段产出。这是给 **AI Agent** 读的约束文档。
> 人类版本见 `docs/SYSTEM_DESIGN.md`，接口契约见 `docs/API_SPEC.md`。

---

## 系统层次结构

```
[复制 SYSTEM_DESIGN.md 中的架构图，用 Agent 友好的方式表述]

Layer 1: [名称] — [职责一句话]
Layer 2: [名称] — [职责一句话]
Layer 3: [名称] — [职责一句话]
```

---

## 模块边界规则（Agent 必须遵守）

- `[模块 A]` 不能直接导入 `[模块 B]`，必须通过接口层
- 所有对外接口必须遵循 `docs/API_SPEC.md` 中定义的响应格式
- `[具体约束]`

---

## 技术栈

> 来源：`docs/TECH_SELECTION.md`

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | | |
| 后端框架 | | |
| 数据库 | | |
| 缓存 | | |

---

## 数据模型

参见 `docs/DATA_MODEL_PHYSICAL.md`

---

## 接口规范

参见 `docs/API_SPEC.md`

---

## 测试要求

参见 `docs/TEST_STRATEGY.md`

---

## 代码规范

- 文件命名：
- 目录结构：[参考 RULES.md]
- 注释要求：

---

## 禁止事项（Agent 不能做的）

- 不能跳过测试直接合并代码
- 不能修改 `docs/API_SPEC.md` 中已约定的接口路径和参数格式（需要修改时先报告）
- `[其他约束]`
