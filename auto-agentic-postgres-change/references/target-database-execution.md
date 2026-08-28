# Target database execution and verification

仅在准备连接、执行或验证 `apps/auto-agentic-app` 的共享 PostgreSQL 变更时读取本文件。代码设计和本地单测阶段不需要加载它。

## 1. 动态解析执行上下文

先从当前任务和代码中解析以下值，不把历史值写回本 Skill：

- 用户本轮授权的目标部署上下文；
- 当前服务 PSM、部署类型和标准环境；
- 项目实际使用的本地执行身份；
- 读取 `DATABASE_URL` 的应用配置入口；
- 项目内明确的迁移 package script。

需要核对部署泳道时，先确认 `bitscli` 可用并完成登录，再把已解析的值代入平台查询。下面仅表示参数结构，尖括号不是可执行值：

```bash
bitscli env deploy-context \
  --env '<target-deployment-env>' \
  --psm '<service-psm>[<deployment-type>]' \
  --standard-env '<standard-env>'
```

如果本次执行依赖该泳道中的服务，继续执行需要平台证明环境存在、状态正常、目标服务属于该环境、资源正在使用且集群已部署。若数据库通过独立配置域或本地已验证配置链访问，服务未部署在该配置域不等于数据库目标错误；此时必须转而用数据库身份探针和用户确认建立证据。

如果返回多个相近环境，使用用户本轮明确指定的目标；没有明确目标时停止并询问，不能按创建人、更新时间或名字相似度自动选择。

## 2. 构造并固定运行 wrapper

本地执行身份和部署服务 PSM 职责不同，不能互换。先从当前项目脚本或已经成功的同类只读命令解析本地执行身份，再选择以下一种配置链。

### 2.1 本地默认配置链

当用户明确确认本地配置连接目标共享数据库，且只读探针能证明库身份时，优先复用项目已经验证的本地 wrapper。下面只表示结构：

```bash
doas --login-type deviceflow \
  -p '<local-doas-identity>' \
  <read-only-or-migration-command>
```

### 2.2 显式运行上下文

只有当前目标必须模拟特定部署运行上下文、并且代码或平台已经证明所需变量时，才显式注入它们：

```bash
doas --login-type deviceflow \
  -e '<credential-region>' \
  -p '<local-doas-identity>' \
  env \
  SERVICE_ENV='<target-config-env>' \
  TCE_ENV='<target-config-env>' \
  RUNTIME_IDC_NAME='<runtime-idc>' \
  TCE_HOST_ENV='<runtime-host-env>' \
  IS_TCE_DOCKER_ENV='<docker-flag>' \
  NODE_ENV='<node-env>' \
  <read-only-or-migration-command>
```

尖括号都是待解析占位符，禁止原样执行。选定 wrapper 后，配置探针、数据库预检、正式迁移和后验验证必须使用同一个 wrapper。

本机缺少 `/opt/tiger` 时，SDK 可能把日志写到应用 `log/` 并输出目录告警。按退出码、最终业务输出和数据库后验判断成功；同时检查 `git status --short`，确保日志目录被忽略且没有污染工作树。

## 3. 配置身份探针

在数据库连接前，先记录当前配置上下文并只输出连接串哈希。哈希用于同一轮执行中的前后对比，不是凭证，也不是跨时间永久的数据库编号。

```bash
<resolved-runtime-wrapper> \
  pnpm exec tsx --eval '
    import { createHash } from "node:crypto";
    import env from "@byted-service/env";
    import { getAppConfig } from "./api/mastra/config/tcc.ts";

    (async () => {
      const config = await getAppConfig();
      if (!config.DATABASE_URL) throw new Error("DATABASE_URL is required");
      console.log(JSON.stringify({
        runtimeEnv: env.getEnv(),
        isProd: env.isProd(),
        databaseConfigFingerprint: createHash("sha256")
          .update(config.DATABASE_URL)
          .digest("hex")
          .slice(0, 16),
      }, null, 2));
    })().then(() => process.exit(0), error => {
      console.error(error instanceof Error ? error.message : String(error));
      process.exit(1);
    });
  '
```

不要用 `runtimeEnv` 或 `isProd` 单独判定数据库身份：本地 wrapper、配置环境和部署泳道可能共享数据库但显示不同标签。要求配置指纹存在，并在数据库探针中继续核对实际库名、Schema、主从状态和服务端指纹。

如果日志明确显示 TCC 加载失败并 fallback 到 `process.env` 或 `.env`，即使存在 `DATABASE_URL` 也停止。仅出现“检查本地 `.env`”或“未找到 `.env`”日志，不足以判定 TCC 加载失败。

## 4. PostgreSQL 只读身份与风险检查

使用应用的 `getAppConfig()` 和 `PostgresStore({ disableInit: true, max: 1 })` 建立只读探针。探针只输出必要的非敏感事实，不输出连接串或服务端地址原值。

### 数据库身份

```sql
SELECT
  current_database() AS database,
  current_schema() AS schema,
  current_user AS role,
  version() AS version,
  inet_server_addr()::text AS server_addr,
  pg_is_in_recovery() AS is_replica;
```

在 Node 中对 `server_addr` 做 SHA-256 并仅保留短哈希，然后删除原值再输出。`is_replica=true` 时不得继续写入。

### 目标表规模

将 `$1` 绑定为明确的目标表名数组：

```sql
SELECT
  c.relname AS table_name,
  c.reltuples::bigint::text AS estimated_rows,
  pg_total_relation_size(c.oid)::bigint::text AS total_bytes
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = current_schema()
  AND c.relname = ANY($1::text[])
  AND c.relkind IN ('r', 'p')
ORDER BY c.relname;
```

不要对未知大表直接执行 `COUNT(*)`。先看关系大小和估算行数，再决定是否需要精确计数。

### 活跃事务

```sql
SELECT
  COUNT(*)::int AS active_sessions,
  COALESCE(
    EXTRACT(EPOCH FROM MAX(clock_timestamp() - xact_start)),
    0
  )::int AS oldest_xact_seconds
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
  AND state <> 'idle';
```

### 目标关系锁

```sql
SELECT
  COUNT(*) FILTER (WHERE NOT l.granted)::int AS waiting_locks,
  COUNT(*) FILTER (WHERE l.granted)::int AS granted_locks
FROM pg_locks l
JOIN pg_class c ON c.oid = l.relation
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = current_schema()
  AND c.relname = ANY($1::text[]);
```

有等待锁时停止。存在已授予锁或长事务时，结合目标 DDL 所需锁级别判断；不能只看等待锁为零就认定安全。

### 预期结构

从迁移源代码生成本轮 `expectedTables`、`expectedColumns`、`expectedIndexes` 和 `expectedConstraints`，再查询系统目录比较。不要长期手写另一份完整 Schema 当事实源；迁移代码是预期结构的当前来源。

关键检查包括：

```sql
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = current_schema()
  AND table_name = ANY($1::text[]);
```

```sql
SELECT
  c.relname AS index_name,
  i.indisvalid AS is_valid,
  i.indisready AS is_ready,
  pg_get_indexdef(i.indexrelid) AS definition
FROM pg_index i
JOIN pg_class c ON c.oid = i.indexrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = current_schema()
  AND c.relname = ANY($1::text[]);
```

```sql
SELECT
  conrelid::regclass::text AS table_name,
  conname,
  convalidated,
  pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid::regclass::text = ANY($1::text[]);
```

新增唯一键时，为实际键列编写对应的 `GROUP BY ... HAVING COUNT(*) > 1` 检查。新增 CHECK/NOT NULL 时，先写出能返回所有违规行数的反向条件。

## 5. 正式迁移

优先运行仓库内经过测试的 package script。先从当前 `package.json` 回读真实入口，再通过前面固定的 wrapper 执行；不要把某个业务迁移命令永久写死在 Skill 中：

```bash
<resolved-runtime-wrapper> pnpm run <verified-migration-script>
```

禁止原样执行占位符。不同迁移必须使用各自的明确 package script，不能借相邻业务入口执行无关 SQL。

## 6. 后验验证

使用同一 wrapper 和同一组期望对象重新查询，输出：

- `missingTables`
- `missingColumns`
- `missingIndexes`
- `invalidIndexes`
- `invalidConstraints`
- 重复键分组数和约束违规行数
- 迁移前后关键表行数或业务聚合
- 目标关系等待锁

纯 Schema 迁移的理想结果是所有 missing/invalid/violation 数组为空或计数为零，历史业务聚合不变，等待锁为零。

若结果不满足预期，保留现场并停止后续发布。不要执行 DROP、DELETE、TRUNCATE 或覆盖式 UPDATE 来隐藏失败。

## 7. 工具边界

- `bitscli env` 用于查询部署元数据和部署事实，不等于远程 shell，也不会替你执行 PostgreSQL 迁移。
- `database-toolbox` 当前主要覆盖 ByteRDS/MySQL、ByteDoc 和 Redis；本项目这里是 PostgreSQL。可以复用其变更安全思想，但不要把 MySQL 工单命令套到 PostgreSQL。
- HTTP 流量路由头不能改变本地迁移进程读取哪个 `DATABASE_URL`。
