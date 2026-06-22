# V2.46-V2.52 Target Architecture：Agent Productization and Architecture Reading Portal

## 1. 架构目标

V2.46-V2.52 将已有 project intelligence artifacts 产品化为三类稳定出口：

- Human Portal：给人类维护者阅读项目、架构图、风险和差异。
- Agent MCP Gateway：给 Codex/Copilot 类 Agent 获取任务上下文和证据链。
- Governance Loop：给架构审计者记录 doc-code drift、profile rule 和 review finding。

## 2. 目标数据流

```text
Existing V2 artifacts
  -> MCP Productization Layer
  -> Project Profile Onboarding
  -> Human Architecture Portal
  -> Task Navigation and Impact v2
  -> Doc-Code Governance Workflow
  -> Agent Context Playbooks
  -> Multi-project Continuous Acceptance
```

## 3. 组件设计

### 3.1 MCP Productization Layer

职责：

- 生成 Codex CLI 配置指南。
- 提供工具发现、推荐调用序列和错误解释。
- 为 Agent 输出固定操作协议。

边界：

- 不新增无证据能力声明。
- 不把 MCP health 当作业务能力 accepted。

### 3.2 Project Profile Onboarding

职责：

- 为新项目生成 profile draft。
- 记录 taxonomy terms、entrypoint patterns、workflow patterns、authority rules。
- 输出 profile validation 和 no-hardcode audit。

边界：

- 项目专用术语只能进入 profile。
- 通用 extractor 不允许出现 HarnessOS/Navia/codexPat hardcode。

### 3.3 Human Architecture Portal

职责：

- 从 persisted artifacts 渲染项目理解首页。
- 展示项目定位、入口、模块、关系链、文档代码差异、风险和 recommended reading。
- 原位渲染 Mermaid/SVG/HTML 图表。
- 如果提供 direct UI route，该 route 只能读取 persisted portal artifacts 或其等价 read contract。

边界：

- HTML 不引入 artifact 外事实。
- Mermaid label 必须 escape。
- 不展示 raw Mermaid source 作为最终图。
- direct UI route 必须纳入 HTTP/MCP/CLI parity，或记录 UI-only read exception 并指向 MCP/CLI 可读取的底层 artifact。

### 3.4 Task Navigation and Impact v2

职责：

- 消费 relationship chain、module reading pack、doc-code alignment 和 test selection。
- 输出 task-aware reading order、impact candidates、suggested tests。

边界：

- relationship chain 不是 full call graph。
- impact candidate 不是确定运行时调用。

### 3.5 Doc-Code Governance Workflow

职责：

- 把 verification finding 接入 quality governance。
- 支持 feedback、rule、review、plan。
- approved rule 只做 read-time overlay。

边界：

- 不改写原始 docs。
- 不改写上游 code facts。

### 3.6 Agent Context Playbooks

职责：

- 为 maintainer、coding_agent、documentation_agent、architecture_reviewer 输出 playbook。
- 每个 playbook 定义推荐 MCP 调用顺序、输入、输出和失败处理。
- 输出 token budget 和 omitted_items。

边界：

- 小 token budget 下不能保留无 evidence 建议。

## 4. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/agent_productization/
  mcp_usage_guide.json
  profile_onboarding/
  human_portal/
  task_navigation_v2/
  doc_code_governance/
  context_playbooks/
  continuous_acceptance/
```

## 5. Public Contract

每个 read output 必须使用统一 envelope：

```json
{
  "ok": true,
  "schema_version": "v2.46-52",
  "workspace_id": "...",
  "codebase_id": "...",
  "snapshot_id": "...",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

错误输出必须结构化，不能泄露绝对路径、secret、raw traceback。

## 6. 架构门禁

- V2.46-V2.52 只能消费 V2.0-V2.45 artifacts 或生成自己命名空间下的新 artifacts。
- 不静默改写 V2.0-V2.45 artifacts。
- 不把 provider unavailable、structured blocker、low confidence 写成 accepted。
- 不把 doc claim 直接写成 code fact。
- 不把 profile 规则写死进通用代码。
- 不把 planning baseline、tool health、HTML 渲染成功或 structured unavailable 当作 accepted implementation。
