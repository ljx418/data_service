# V2.111-V2.115 PRD：Workspace Portfolio Final Acceptance Closure

## 1. 阶段定位

V2.106-V2.110 已实现 final evidence closure machinery。真实 `/mnt/c/workspace` 有界验收的 gate 结果是：

```text
implementation_status=accepted
portfolio_final_status=structured_unavailable
high_risk_unresolved_count=164
```

V2.111-V2.115 的目标是闭合 final acceptance 所需的真实执行证据，而不是扩大项目理解承诺。本阶段只处理 OCR/media、source trace、UI evidence、多项目安全 build runtime 和 final release rerun。

本阶段仍不声明：

- 完整恢复复杂项目设计意图。
- full call graph、runtime topology、data/control flow 或 type inference。
- OCR/provider 缺失时媒体资料已被理解。
- 只有 PPT/PDF 直接文本抽取结果时 OCR 已被验收。
- 没有真实可 OCR 文本样本时 V2.111 或 final release 不可以 accepted。
- 有界 build 等价于全量项目 accepted。
- UI 截图、HTML report、drawio 或 docs claim 可替代真实 source/build evidence。
- `needs_review`、`structured_unavailable`、`structured_blocker` 不可计入 accepted。

## 2. 当前事实基线

| 项 | 当前状态 | 本阶段目标 |
| --- | --- | --- |
| Final evidence machinery | `implementation_status=accepted` | 复用 V2.106-V2.110 artifacts 作为输入 |
| OCR/media | provider 与 media matrix 已有，真实 OCR/转换证据缺失；OCR 真实样本资格尚需确认 | 先确认真实可 OCR 文本样本，再执行或结构化阻断每个 OCR/media row |
| Source trace | closure matrix 已有，import/query/source trace 链缺失 | 为 accepted 文档建立完整 source evidence chain |
| UI evidence | `/knowledge` final evidence panel 已接入，截图证据缺失 | 生成 headless screenshot 或结构化浏览器阻断 |
| Multi-project build | 队列和诊断已有，安全 runtime 不完整 | 引入 sandbox、timeout、cache、恢复和日志治理 |
| Final release gate | `portfolio_final_status=structured_unavailable` | 重新聚合并输出 accepted 或可信 non-accepted |

## 3. 阶段目标与用户体验

| 阶段 | 名称 | 用户可体验结果 |
| --- | --- | --- |
| V2.111 | OCR / Media Provider Real Execution Closure | 维护者在报告中看到每个图片、扫描 PDF、PPT 的 OCR/转换执行状态、证据路径、失败原因和补证动作 |
| V2.112 | Document Ingest / Query / Source Trace Full Closure | 审计者可以点击文档行，看到 import artifact、query result、source trace refs 和不通过原因 |
| V2.113 | Headless UI Evidence Capture Closure | 维护者看到 `/knowledge` final evidence panel 的真实截图证据；失败时看到浏览器依赖诊断 |
| V2.114 | Safe Multi-project Build Runtime Governance | Agent 获得完整项目 build queue、缓存命中、超时、失败隔离、retry/resume 和命令 allowlist 结果 |
| V2.115 | Final Portfolio Release Gate Rerun and Packaging | 系统重新判断 portfolio final status，并输出 HTML/JSON/Markdown 交付包 |

## 4. In Scope

- OCR/provider readiness 到真实 execution evidence 的闭环。
- OCR 真实样本资格确认：必须证明存在文本型图片/扫描件、具备来源 ref、样本 hash、预期文本锚点或人工说明；若只发现 PPT/PDF 可直接抽取文本，不得计入 OCR accepted。
- PDF/PPT/image/text extractor evidence matrix。
- Source import、query、source trace 三段证据链。
- Headless UI screenshot，优先无焦点抢占；不可用时结构化阻断。
- 多项目 build runtime：allowlist、timeout、cache、独立 output/cache、日志截断、敏感信息脱敏、retry/resume。
- Final release gate rerun、PRD/spec review、false-green audit、acceptance package。

## 5. Out of Scope

- 自动安装系统依赖、OCR、LibreOffice、Chrome/Chromium。
- 自动修改被扫描项目。
- 自动执行未批准的外部项目任意 shell script。
- 自动删除、移动或重写 workspace 文件。
- 默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。
- 将 docs/present、drawio、HTML report 当作代码或 source trace evidence。

## 6. 完成定义

文档阶段完成：

1. PRD、目标架构、开发验收计划、coverage matrix、测试映射、里程碑、gap analysis、pre-implementation audit、drawio 全部落盘。
2. drawio 不超过 8 页，中文书写，展示目标体验、当前到目标架构、代码实体分层、数据/证据流、开发验收计划、出门条件、No-Go。
3. 每个阶段都有 artifact contract、public surface、focused test、真实 E2E 输入、PRD/spec review 和 false-green audit。
4. 明确 `portfolio_final_status` 不能在高风险项未闭合时 accepted。
5. V2.111 明确区分 OCR 样本资格、OCR/provider 执行、PPT/PDF 直接文本抽取；缺真实 OCR 样本时必须保留 `structured_unavailable` 或 `needs_review`。

实现阶段完成：

1. V2.111-V2.115 focused tests 全部通过。
2. 真实 `/mnt/c/workspace` E2E 完成，或每个不可用项有 structured blocker/unavailable reason。
3. `/knowledge` 或 HTML report 能展示 final evidence 状态和截图/阻断证据。
4. public surface guard、compileall、frontend build、git diff checks 全部通过。
5. protected legacy files 未修改，除非用户明确批准。

## 7. 文档基线

本阶段文档入口：

- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_PRD.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_IMPLEMENTATION_BLUEPRINT_AND_ACCEPTANCE_SPEC.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_PHASE_READINESS_AND_SCHEMA_CONTRACTS.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_FULL_COVERAGE_MATRIX.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TEST_AND_E2E_MAPPING.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_MILESTONES_AND_EXIT_GATES.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_GAP_ANALYSIS.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_PRE_IMPLEMENTATION_AUDIT_REPORT.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_DOCUMENT_AUDIT_REPORT.md`
- `docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TARGET_STATE.drawio`

文档阶段状态：

```text
documentation_status=pass_for_implementation_guidance
implementation_acceptance=not_pass
final_release_acceptance=not_pass
```
