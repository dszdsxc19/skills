# 物理数据模型

> **阶段定位**：详细设计阶段产出。将概念模型转化为具体的数据库表设计。
> 概念模型见 `docs/DATA_MODEL.md`。

---

## 表结构

### `users`

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, NOT NULL | 主键，使用 UUID v4 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 登录邮箱 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**索引**：
- `idx_users_email` ON `email` — 登录查询

---

### `[table_name]`

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, NOT NULL | |
| user_id | UUID | FK → users.id | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**索引**：
- `idx_[table]_user_id` ON `user_id` — 按用户查询

**外键**：
- `user_id` → `users(id)` ON DELETE CASCADE

---

## 分库分表策略

> 当前数据量 [X]，暂不分表 / 按 [字段] 水平分片

---

## 迁移策略

- 使用 [迁移工具，如 Flyway / Liquibase / Prisma Migrate]
- 迁移文件目录：`db/migrations/`
- 命名规范：`V{version}__{description}.sql`
