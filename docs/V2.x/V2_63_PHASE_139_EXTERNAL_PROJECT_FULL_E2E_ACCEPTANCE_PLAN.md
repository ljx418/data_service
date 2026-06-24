# V2.63 / Phase 139 Acceptance Plan：External Project Full E2E

## 1. 验收目标

本阶段验收目标是证明 External Project Full E2E 使用真实项目、真实 artifact、真实 evidence，不把不可用或 mock-only 结果写成 accepted。

本文是 phase-specific acceptance plan，不是验收完成证据。

## 2. Focused test

计划测试命令：

```text
pytest -q backend/tests/test_v2_63_external_project_full_e2e.py
```

共享守护：

```text
pytest -q backend/tests/test_public_surface_guard.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 3. Real E2E acceptance rules

| Project | Required result |
| --- | --- |
| data_service | accepted |
| codexPat | accepted or structured_unavailable/structured_blocker with reason |
| HarnessOS | accepted or structured_unavailable/structured_blocker with reason |
| Navia | accepted or structured_unavailable/structured_blocker with reason |

`structured_unavailable`、`structured_blocker`、`needs_review` 不能计入 accepted。

## 4. Artifact acceptance

必须生成：

```text
external_e2e/full_project_matrix.json
external_e2e/project_run_records.json
external_e2e/artifact_readiness.json
external_e2e/external_e2e_report.md
```

每个 project row 必须包含：

- project_id。
- status。
- path_status。
- dependency_status。
- artifact_status。
- commands。
- evidence_refs 或 unresolved reason。
- failure_category。
- next_action。

## 5. PRD/spec review checklist

- 是否仍遵守“不声明完整恢复复杂项目设计意图”。
- 是否没有声称 full call graph、runtime topology、data/control flow、type inference。
- 是否没有把 documentation claim 当 code fact。
- 是否没有把外部项目不可用写成 accepted。
- failure diagnosis 是否能支撑维护者下一步动作。

## 6. False-green audit checklist

- mock-only evidence 不能 accepted。
- path_unavailable 不能 accepted。
- dependency_drift 不能 accepted，除非真实修复并重新运行。
- sandbox_limit 不能 accepted。
- artifact_missing 不能 accepted。
- needs_review 不能 accepted。

## 7. 出门条件

Phase 139 出门必须具备：

- focused test 通过。
- data_service 真实 E2E accepted。
- codexPat、HarnessOS、Navia 有 accepted 或结构化不可用/阻塞结果。
- PRD/spec review report。
- false-green audit report。
- acceptance audit report。
- protected legacy file diff check 无未授权修改。
