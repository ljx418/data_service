# V2.59-V2.62 Milestones and Exit Gates

## M0 Stage Readiness

出门条件：

- V2.54-V2.58 final acceptance audit accepted。
- V2.59-V2.62 PRD、目标架构、开发验收计划、coverage matrix、gap drawio 已落盘。
- 当前 changed files 已纳入 pre-implementation audit。
- no open fatal / major planning finding。

## M1 V2.59 Public Surface Stabilization

用户可体验结果：

- 维护者能看到 MCP / CLI / HTTP surface 是否一致。
- Agent 能读取 contract snapshot 和 migration note。
- 审计者能查看 drift report。

出门条件：

- `public_surface_snapshot.json` 生成。
- `public_surface_parity_matrix.json` 生成。
- `public_surface_drift_report.json` 生成。
- `migration_notes.md` 生成。
- Focused tests、public surface guard、real data_service E2E 通过。
- Snapshot 不能只来自 hardcoded expected list。

## M2 V2.60 Real Project E2E Expansion

用户可体验结果：

- 维护者能看到四项目 E2E 状态和失败分类。
- 不可用项目有明确复查动作。

出门条件：

- data_service real E2E accepted。
- codexPat、HarnessOS、Navia 有 accepted、structured_unavailable 或 structured_blocker。
- 不可用项目未计入 accepted。
- Failure categories 完整。
- Mock-only evidence 被拒绝。

## M3 V2.61 Acceptance Artifact Cleanup and Packaging

用户可体验结果：

- 维护者能判断哪些文件应提交、哪些是临时产物、哪些需要人工确认。
- 新接手者能按 handoff checklist 恢复验收。

出门条件：

- `package_manifest.json` 生成。
- `cleanup_plan.md` 生成。
- `handoff_checklist.md` 生成。
- `package_audit_report.md` 生成。
- 不自动删除未确认归属文件。
- Public payload redaction 通过。

## M4 V2.62 Human Portal UX Integration

用户可体验结果：

- Portal 展示阶段状态、contract stability、E2E coverage、restore readiness、delivery checklist。
- Portal 中的 warnings、unresolved、needs_review、structured_unavailable 清晰可见。

出门条件：

- `portal_state_summary.json` 生成。
- `portal_sections.json` 生成。
- `portal_acceptance_panel.json` 生成。
- `project_portal_v3.html` 生成。
- HTML 不展示 raw Mermaid source。
- Portal 不把 unavailable/needs_review 渲染为 accepted。

## M5 Stage Closure

出门条件：

- V2.59-V2.62 coverage matrix 所有 in-scope row 均有 accepted、structured_unavailable、structured_blocker 或 needs_review 状态。
- No unsupported accepted row。
- Focused tests 通过。
- V2.46-V2.58 baseline regression 通过。
- Real E2E 或 structured rationale 完整。
- PRD/spec review 通过。
- False-green audit 通过。
- Protected legacy file diff 为空。
- no open fatal / major finding。

## Global Rejection Rules

- Mock-only evidence 不能作为 real E2E。
- `structured_unavailable` 不能写成 accepted。
- 文档 claim 不能写成 code fact。
- Portal 不能隐藏 needs_review / unresolved。
- Cleanup 不能删除未经确认的用户文件。
- 不得声称 full call graph、runtime topology、data/control flow、type inference。
