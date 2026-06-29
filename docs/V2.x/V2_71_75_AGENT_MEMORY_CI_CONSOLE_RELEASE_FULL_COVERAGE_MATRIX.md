# V2.71-V2.75 Full Coverage Matrix

| PRD 能力 | 阶段 | 计划 artifact | 验收证据 | 当前状态 |
| --- | --- | --- | --- | --- |
| Detailed PRD P0/P1 and user acceptance | V2.71-V2.75 | `V2_71_75_AGENT_MEMORY_CI_CONSOLE_RELEASE_DETAILED_PRD.md` | PRD/spec review、document audit、false-green audit | planned |
| 外部项目路径闭环 | V2.71 | `external_project_closure/project_binding_closure.json` | focused test、真实路径检查、E2E result | planned |
| 外部 E2E closure report | V2.71 | `external_project_closure/e2e_closure_report.md` | data_service accepted，外部项目 accepted 或 structured unavailable/blocker | planned |
| CI matrix | V2.72 | `ci_warning_governance/ci_matrix.json` | 分组测试命令和结果 | planned |
| Warning budget | V2.72 | `ci_warning_governance/warning_budget.json` | warning count、budget、next action | planned |
| Failure diagnosis | V2.72 | `ci_warning_governance/failure_diagnosis.json` | dependency drift、sandbox limit、artifact missing、public surface drift、real regression、needs_review | planned |
| Agent memory index | V2.73 | `agent_memory/memory_index.json` | artifact refs、evidence refs、retention policy | planned |
| Evidence index | V2.73 | `agent_memory/evidence_index.json` | 每条 evidence 可回溯到 persisted artifact | planned |
| Acceptance state | V2.73 | `agent_memory/acceptance_state.json` | accepted/non-accepted 状态不混淆 | planned |
| Task briefing | V2.73 | `agent_memory/task_briefing.json` | recommendation 有 evidence 或 needs_review | planned |
| Console model | V2.74 | `interactive_console/console_model.json` | 面板 status、artifact_ref、evidence_ref、unresolved | planned |
| Console HTML | V2.74 | `interactive_console/maintainer_console.html` | 不硬编码 artifact 外事实，不隐藏 non-accepted | planned |
| Release manifest | V2.75 | `release_restore/release_manifest.json` | 文件分类、版本、surface、redaction | planned |
| MCP config template | V2.75 | `release_restore/mcp_config_template.json` | 可本地配置，不含 secret | planned |
| Smoke commands | V2.75 | `release_restore/smoke_commands.md` | MCP/CLI/HTTP/focused tests 命令 | planned |
| Restore runbook | V2.75 | `release_restore/restore_runbook.md` | 干净本地环境可执行步骤 | planned |

## 状态规则

- `planned`：文档规划，不能作为实现证据。
- `accepted`：必须有真实 artifact、命令、结果、PRD/spec review 和 false-green audit。
- `structured_unavailable`：外部条件不可用，不是 accepted。
- `structured_blocker`：阻断，需要人工或环境变化。
- `needs_review`：证据弱、缺失或需要人工判断。
- `out_of_scope`：明确不属于本阶段。
