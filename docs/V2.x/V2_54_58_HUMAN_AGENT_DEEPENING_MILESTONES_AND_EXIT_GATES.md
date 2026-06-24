# V2.54-V2.58 Milestones and Exit Gates

## M0 Pre-implementation Gate

出门条件：

- V2.53 acceptance audit accepted。
- 当前 worktree clean，或 changed files 已列入 pre-implementation audit。
- data_service、HarnessOS、Navia、codexPat 路径确认或 structured_unavailable。
- 本阶段 PRD、目标架构、开发验收计划、gap analysis、drawio、coverage matrix 已落盘。
- V2.54 development plan、acceptance plan、pre-implementation audit 已落盘。
- no open fatal / major finding。

## M1 V2.54 Human Portal Deepening

出门条件：

- portal deepening artifacts 生成。
- project story、risk priority、reading path、acceptance state 可读。
- 图表原位渲染，不展示 raw Mermaid source。
- 每个新增 section 有 evidence_refs 或 unresolved reason。
- direct UI route parity 或 UI-only exception 完成。

## M2 V2.55 Agent Task Workflow Hardening

出门条件：

- task workflow bundle 可读。
- reading order、impact candidates、suggested tests、constraints、stop conditions 完整。
- 不声称 full call graph 或 runtime call。
- token budget / omitted_items 可见。

## M3 V2.56 Doc-Code Governance Evidence Loop

出门条件：

- evidence loop、decision history、rule effect 可读。
- approve/revoke 行为通过。
- read-time overlay 不改写原始 docs 或上游 code facts。
- contradicted / unsupported 不被隐藏。

## M4 V2.57 Multi-project Regression Expansion

出门条件：

- 四项目 regression matrix 完成。
- artifact diff / trend / failure diagnosis 可读。
- unavailable 和 needs_review 不计入 accepted。
- parity / redaction / no-hardcode guard 通过。

## M5 V2.58 Developer Onboarding / Restore UX

出门条件：

- restore checklist 和 troubleshooting 可读。
- test dependency baseline 可复现。
- canonical runner 文档完整。
- 沙箱 TestClient 限制有明确说明。

## M6 Closure

出门条件：

- V2.54-V2.58 full coverage matrix 无 unsupported accepted row。
- focused tests 通过。
- 真实项目 E2E 或 structured_unavailable 完整记录。
- PRD/spec review 通过。
- false-green audit 通过。
- no open fatal / major finding。

## Global Claim Boundary

- `planned`、`ready`、`baseline ready` 不代表功能实现。
- accepted implementation claim 必须有 artifact path、test command、real repo result 或 structured rationale。
- documentation claim 不等于 code fact。
