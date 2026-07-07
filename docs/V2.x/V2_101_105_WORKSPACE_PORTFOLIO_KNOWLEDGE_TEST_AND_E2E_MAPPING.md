# V2.101-V2.105 Test and E2E Mapping

## 1. Focused Tests

计划 focused tests：

```text
backend/tests/test_v2_101_workspace_portfolio_discovery.py
backend/tests/test_v2_102_project_knowledge_builder.py
backend/tests/test_v2_103_document_media_intake.py
backend/tests/test_v2_104_knowledge_console_portfolio.py
backend/tests/test_v2_105_portfolio_release_gate.py
backend/tests/test_public_surface_guard.py
```

## 2. Real E2E Inputs

| 输入 | 用途 | 不可用处理 |
| --- | --- | --- |
| `/mnt/c/workspace` | 真实项目组合扫描 | structured_blocker |
| `/mnt/c/workspace/data_service` | 强制代码项目样本 | failed 或 structured_blocker |
| `/mnt/c/workspace/codexPat` | 外部代码项目样本 | structured_unavailable |
| `/mnt/c/workspace/harnessOS` | 外部代码项目样本 | structured_unavailable |
| `/mnt/c/workspace/navia` | 外部代码项目样本 | structured_unavailable |
| `/mnt/c/workspace/技术分享` | 纯资料/PPT/PDF/DOCX 样本 | needs_review 或 structured_unavailable |
| `/mnt/c/workspace/1-AI教案` | docs/images 样本 | needs_review 或 structured_unavailable |
| `/mnt/c/workspace/我在城市的深海里漂流` | 文档/图片资料样本 | needs_review 或 structured_unavailable |

## 3. Acceptance Commands

文档阶段只规划命令，不执行实现验收。实现阶段最终命令应包含：

```text
PYTHONPATH=backend python3 -m pytest -q \
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

真实 E2E 命令计划：

```text
PYTHONPATH=backend python3 -m data_service portfolio scan \
  --workspace-id v2_101_105_real \
  --root /mnt/c/workspace \
  --limit 40

PYTHONPATH=backend python3 -m data_service portfolio build \
  --workspace-id v2_101_105_real \
  --root /mnt/c/workspace \
  --limit 40 \
  --max-code-projects 1

PYTHONPATH=backend python3 -m data_service portfolio report \
  --workspace-id v2_101_105_real
```

E2E 有界执行规则：

- `--limit` 和 `--max-code-projects` 是可复跑验收边界，不是 silent skip。超过边界的项目必须出现在 build run、release gate 或 acceptance audit 的 `needs_review`/next action 中。
- 若实现选择全量构建，必须提供超时、缓存、失败分类和 structured blocker 策略。
- `data_service` 作为强制代码样本；其他代码项目可在有界验收中记录为待构建，但不得计入 accepted。
- docs/media readiness 可覆盖真实资料目录；只有实际 ingest/query/source trace 完成的行才能标记 ingest accepted。

## 4. Headless UI 验收

优先使用 headless browser：

- 打开 `/knowledge`。
- 进入 portfolio panel。
- 截取维护者首页，必须包含 Portfolio Status Header、Project Registry Summary、Build Run Summary、Media Readiness Summary 和 Next Actions List。
- 截取单项目详情。
- 截取媒体 readiness 或 OCR 缺口。
- 截取 release gate 状态。

截图不能替代 build evidence，只能证明 UI 真实展示 persisted artifacts。

截图与 artifact 对照规则：

- 首页统计值必须能在 `project_registry.json` 或 `release_gate.json` 中找到来源。
- 项目详情必须能在 `project_build_runs.json` 或 `portfolio_index.json` 中找到来源。
- media readiness 必须能在 `media_readiness.json` 或 `source_candidate_matrix.json` 中找到来源。
- release gate 必须能在 `release_gate.json` 和 `false_green_audit.md` 中找到来源。
- release gate 截图和 API 结果必须同时展示 `implementation_status` 与 `portfolio_final_status`；OCR/provider 缺失时不得把 `portfolio_final_status` 显示为 accepted。

## 5. PRD / Spec Review

每个阶段验收报告必须说明：

- PRD 目标体验是否被真实 artifact 支撑。
- 是否存在 docs claim 被误当 code fact。
- 是否保留 OCR、路径、权限、人工确认的 non-accepted 状态。
- 是否有 mock-only、sample-only、UI-only evidence 被误用。
- 是否明确区分本阶段功能实现状态与项目组合资料全绿状态。

## 6. False-green Audit

重点拒绝：

- scan 成功即项目理解 accepted。
- UI 截图即建库 accepted。
- OCR 不可用的图片/扫描件被 accepted。
- docs claim 被写成 code fact。
- silent skip 不可读目录。
