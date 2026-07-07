# V2.101-V2.105 Phase 177-181 Detailed Development and Acceptance Package

## Phase 177 / V2.101：Workspace Portfolio Discovery

开发目标：

- 新增只读 workspace scanner。
- 新增 project classifier。
- 生成 `project_registry.json` 和 `discovery_report.md`。

验收目标：

- 使用真实 `/mnt/c/workspace` 扫描。
- data_service 至少被识别为 `code_project`。
- 技术分享至少被识别为 `media_corpus` 或 `doc_project`。
- hidden/cache/generated 目录必须有 ignored reason。

Focused test：

```text
backend/tests/test_v2_101_workspace_portfolio_discovery.py
```

## Phase 178 / V2.102：Project Knowledge Builder

开发目标：

- 对 `code_project` 执行有界 code asset import/snapshot/inventory/symbols/project brief；overview/context-pack 作为可用时增强证据，不作为默认全量承诺。
- 对项目 docs 生成 source candidate/readiness；只有真实完成 ingest/query/source trace 时才能写成 ingest accepted。
- 生成 `project_build_runs.json` 和 `portfolio_index.json`。

验收目标：

- 至少一个真实代码项目 accepted，并具备 codebase import、snapshot、inventory/symbols、project brief 或 overview refs。
- 失败项目保留 `structured_unavailable` 或 `structured_blocker`。
- 未构建或超出有界范围的项目保留 `needs_review` 和 next action，不能计入 accepted。
- build run 必须包含 command refs 和 artifact refs。

Focused test：

```text
backend/tests/test_v2_102_project_knowledge_builder.py
```

## Phase 179 / V2.103：Document and Media Intake

开发目标：

- 生成 `source_candidate_matrix.json`。
- 生成 `media_readiness.json`。
- 明确 extractor availability、OCR provider health 和 conversion provider health。

验收目标：

- 覆盖真实 PPTX/PDF/DOCX/YAML/PNG/JPG 样本。
- 无 OCR provider 时图片/扫描件不得 accepted。
- PPTX/PDF/DOCX 只基于可抽取文本 accepted。

Focused test：

```text
backend/tests/test_v2_103_document_media_intake.py
```

## Phase 180 / V2.104：Knowledge Console Portfolio Panel

开发目标：

- `/knowledge` 增加 portfolio panel。
- 新增前端 API client。
- 增加 headless UI 验收截图路径。
- 维护者首页必须包含 `PortfolioStatusHeader`、`ProjectRegistrySummary`、`BuildRunSummary`、`MediaReadinessSummary`、`NextActionsList`。
- 项目组合视图必须包含 `ProjectRegistryTable`、`ProjectDetailDrawer`、`MediaReadinessPanel`、`ReleaseGatePanel`。

验收目标：

- 面板数据来自 HTTP read API。
- 截图包含项目列表、项目详情、media readiness 和 release gate。
- UI 不隐藏 non-accepted 状态。
- 截图内每个状态面板必须能追溯到 artifact ref 或 API response id。
- 若 API 或 artifact 缺失，UI 必须显示结构化不可用或阻断，不能展示静态成功态。

Focused test：

```text
backend/tests/test_v2_104_knowledge_console_portfolio.py
```

## Phase 181 / V2.105：Portfolio Release Gate

开发目标：

- 聚合 V2.101-V2.104 artifacts。
- 生成 `release_gate.json`、`false_green_audit.md`、`portfolio_report.html`。

验收目标：

- accepted 项均有真实证据。
- OCR、UI-only、scan-only、docs claim、silent skip false-green 被拒绝。
- 出门状态使用最差高风险项。
- `portfolio_report.html` 必须列出目标架构实体、当前实现实体、UI 截图证据、focused tests、真实 workspace E2E、PRD/spec review 和 false-green audit；缺任一高风险证据时 final status 不得 accepted。

Focused test：

```text
backend/tests/test_v2_105_portfolio_release_gate.py
```

## Final Acceptance Command Plan

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_101_workspace_portfolio_discovery.py \
  backend/tests/test_v2_102_project_knowledge_builder.py \
  backend/tests/test_v2_103_document_media_intake.py \
  backend/tests/test_v2_104_knowledge_console_portfolio.py \
  backend/tests/test_v2_105_portfolio_release_gate.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```
