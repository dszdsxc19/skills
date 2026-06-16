---
name: promptfoo-mastra-workflow-api
description: Create or update promptfoo evaluations that call Mastra workflow APIs over native HTTP/HTTPS. Use when Codex needs to test a Mastra workflow through `/custom/workflows/:workflowId`, add promptfoo YAML test cases, assert workflow response data, wire package scripts, or document promptfoo + Mastra workflow API eval commands. Prefer promptfoo's built-in HTTP/HTTPS provider; do not create a custom provider unless the user explicitly asks for one.
---

# Promptfoo Mastra Workflow API

## Core Pattern

Use promptfoo's native `http` or `https` provider to call the workflow API directly:

```yaml
providers:
  - id: https
    label: <workflow-id>-workflow
    config:
      url: '{{apiBaseUrl}}/custom/workflows/<workflow-id>'
      method: POST
      headers:
        cookie: '{{env.PROMPTFOO_USER_COOKIE}}'
      body: '{{input | dump}}'
      transformResponse: JSON.stringify(json.data ?? null)
      maxRetries: 0
```

Use `id: http` only when the target URL is plain HTTP. Keep `apiBaseUrl` configurable:

```yaml
defaultTest:
  vars:
    apiBaseUrl: https://web.amh-group.com:4111
```

Allow overrides with:

```bash
yarn eval:<workflow-name> --var apiBaseUrl=http://localhost:4111
```

## File Layout

Put promptfoo artifacts under `tests/promptfoo/`:

```text
tests/promptfoo/
  <workflow-id>.promptfooconfig.yaml
  <workflow-id>.cases.yaml
  README.md
```

Do not add workflow eval helpers inside `src/mastra/workflows/`; that directory is for runtime workflow code.

## Test Case Shape

Store workflow inputs and expected final data in YAML:

```yaml
- description: 客户表达价格贵，命中价格敏感
  vars:
    caseId: price-too-high
    expected:
      scriptType: 价格敏感
      userFeedback: 太贵了
    input:
      conversation:
        messages:
          - role: employee
            text: 现在续费有优惠。
          - role: customer
            text: 还是太贵了。
      standardScripts:
        - type: 价格敏感
          scripts:
            - userFeedback: 太贵了
```

Point the config at the cases file:

```yaml
tests: file://./<workflow-id>.cases.yaml
```

## Assertions

Assert the transformed `data` object, not the full YMM envelope. Include a JSON shape assertion plus a business equality assertion:

```yaml
defaultTest:
  assert:
    - type: is-json
      value:
        type: object
        required: [scriptType, userFeedback]
        properties:
          scriptType: { type: string }
          userFeedback: { type: string }
        additionalProperties: false
    - type: javascript
      value: |
        const data = typeof output === 'string' ? JSON.parse(output) : output;
        const expected = context.vars.expected;
        const pass =
          data.scriptType === expected.scriptType &&
          data.userFeedback === expected.userFeedback;

        return {
          pass,
          score: pass ? 1 : 0,
          reason: pass
            ? 'matched expected workflow output'
            : `expected ${JSON.stringify(expected)}, got ${JSON.stringify(data)}`,
        };
```

Adjust required fields for each workflow's output schema.

## Env And Scripts

Read cookies from ignored env files, never from tracked YAML:

```text
PROMPTFOO_USER_COOKIE=dev_passport=...
```

Add package scripts like:

```json
{
  "scripts": {
    "eval:<workflow-name>": "promptfoo eval -c tests/promptfoo/<workflow-id>.promptfooconfig.yaml --env-file .env --no-cache --no-share"
  }
}
```

If the repo uses a different ignored env file, point `--env-file` there.

## Verification

Run a smoke eval against a known local or dev API:

```bash
yarn run dev
yarn eval:<workflow-name> --filter-first-n 1
```

If the server is not running, `maxRetries: 0` should fail quickly with `ECONNREFUSED`.

For TypeScript-only changes in the repo, run:

```bash
yarn tsc --noEmit
```

If TypeScript fails on unrelated existing errors, report that clearly and do not mask it as a promptfoo problem.
