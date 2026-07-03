# V2.96-V2.100 Phase 172-176 Detailed Development and Acceptance Package

## Phase 172 / V2.96：Default CLI Gap Closure

开发动作：

- 审计当前 `python -m data_service` 默认入口和 code parser 入口。
- 规划默认 shell CLI 到 code parser 的连接方式。
- 生成 CLI surface result 和 CLI report。

验收：

- `python -m data_service code real-acceptance-closure --help` 或新命令有真实可复跑结果。
- 若保留 legacy parser 行为，必须给出替代 accepted 命令和 documented deprecation。
- MCP、HTTP、CLI inventory 不冲突。

## Phase 173 / V2.97：Route A Evidence Automation

开发动作：

- 规划 Route A 真实资料目录扫描。
- 定义 material manifest、redaction audit、evidence capture manifest。
- 规划 headless screenshot 或 structured unavailable 记录。
- 生成人工最小确认队列。

验收：

- 真实资料存在时生成证据链。
- 资料缺失时保持 `needs_review`。
- mock-only、sample-only、path-only 不得 accepted。

## Phase 174 / V2.98：Quality Decision Minimization

开发动作：

- 读取 V2.84/V2.88/V2.93 质量相关 artifacts。
- 生成风险分级和 decision recommendations。
- 将高风险项写入 human decision backlog。

验收：

- 每条 accepted 质量决策有 reviewer 或自动低风险规则证据。
- 高风险项缺人类 decision 时保持 `needs_review`。
- rule effect 不改写上游 artifact。

## Phase 175 / V2.99：External Project E2E Governance

开发动作：

- 规划外部项目路径 registry。
- 绑定 `data_service`、`codexPat`、`HarnessOS`、`Navia`。
- 对可读项目执行 scoped smoke/E2E。
- 对不可用项目生成 unavailable resolution。

验收：

- 每个项目都有路径状态、E2E 状态和 evidence refs。
- 缺路径项目不计入 accepted。
- sandbox 或依赖限制必须结构化记录。

## Phase 176 / V2.100：Automated Release Evidence Gate

开发动作：

- 聚合 V2.96-V2.99 artifacts 和 V2.86-V2.95 artifacts。
- 接入 dependency hygiene、restore smoke、human approval。
- 生成 evidence summary、final release gate、false-green recheck。

验收：

- final release status 采用最差高风险状态。
- 任一高风险项 non-accepted 时 final release 不得 accepted。
- 报告必须列出补证路径和复跑命令。
