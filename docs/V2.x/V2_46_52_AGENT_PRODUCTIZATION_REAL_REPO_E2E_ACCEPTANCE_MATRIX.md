# V2.46-V2.52 Real Repo E2E Acceptance Matrix

## 1. 真实项目

| Project | Path | Role |
| --- | --- | --- |
| data_service | `/Users/Zhuanz/Desktop/workspace/data_service` | 自举项目和 MCP 服务宿主 |
| HarnessOS | `/Users/Zhuanz/Desktop/workspace/harnessOS` | 大型 workflow/runtime/agent 项目 |
| Navia | `/Users/Zhuanz/Desktop/workspace/navia` | Chrome extension + FastAPI runtime + rich docs 项目 |
| codexPat | `/Users/Zhuanz/Desktop/workspace/codexPat` | desktop/app/package 项目 |

项目不可用时必须记录 `PROJECT_REPO_UNAVAILABLE`，不得 accepted。

## 2. E2E 场景

### 2.1 MCP Productization

- data_service 能生成 Codex CLI MCP 配置说明。
- Agent playbook 包含 import、snapshot、overview、profile、relationship、context pack。
- 工具清单与 registry 一致。

### 2.2 Profile Onboarding

- 四个项目各有 profile 或 structured unavailable。
- 项目术语只能在 profile artifact 中出现。
- no-hardcode audit 通过。

### 2.3 Human Portal

- data_service 和 HarnessOS 必须生成 HTML。
- Navia 和 codexPat 必须生成 HTML 或 structured blocker。
- HTML 中 Mermaid/SVG 原位渲染，不展示源码。

### 2.4 Task Navigation and Impact

- 对每个可用项目至少运行一个真实开发任务样例。
- 输出 reading order、impact candidate、suggested test。
- 所有建议有 evidence 或 needs_review。

### 2.5 Doc-Code Governance

- 至少 data_service 和 HarnessOS 生成 supported/weak/unsupported 分类样例。
- approve/revoke read-time overlay 行为通过。
- 原始 artifact hash 不变。

### 2.6 Context Playbooks

- maintainer、coding_agent、documentation_agent、architecture_reviewer 四种角色均有 playbook。
- 小 token budget 测试通过。

## 3. False-Green Rejection

以下情况必须拒绝：

- mock-only 代替真实项目。
- 项目路径缺失却标 accepted。
- HTML 图表节点无法追溯 artifact。
- Mermaid 源码直接展示给用户。
- relationship chain 被描述成 full call graph。
- profile 术语写进通用 extractor。
- context pack 建议缺 evidence 或 needs_review。

