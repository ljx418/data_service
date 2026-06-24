# V2.63-V2.66 Test and E2E Mapping

## 1. 测试目标

本阶段测试必须证明四件事：

- 外部项目 E2E 不把不可用结果写成 accepted。
- Portal V3+ 只展示 persisted evidence，不制造 artifact 外事实。
- Delivery cleanup 只生成可审查计划，不删除用户文件。
- Contract regression 能识别 public surface breaking change。

## 2. Focused test mapping

| Phase | Test file | Primary assertions |
| --- | --- | --- |
| V2.63 | `backend/tests/test_v2_63_external_project_full_e2e.py` | project matrix、run records、artifact readiness、failure diagnosis |
| V2.64 | `backend/tests/test_v2_64_portal_v3_experience.py` | Portal sections、evidence refs、unresolved visibility、HTML redaction |
| V2.65 | `backend/tests/test_v2_65_delivery_cleanup_versioning.py` | file classification、safe_to_delete false、manual review flags |
| V2.66 | `backend/tests/test_v2_66_public_surface_contract_regression.py` | baseline/diff/compatibility/diagnosis |

## 3. Shared regression tests

```text
pytest -q backend/tests/test_public_surface_guard.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
```

Protected file diff check:

```text
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 4. Real project E2E expectations

| Project | Expected handling |
| --- | --- |
| data_service | Must be accepted for stage closure |
| codexPat | accepted or structured_unavailable/structured_blocker with reason |
| HarnessOS | accepted or structured_unavailable/structured_blocker with reason |
| Navia | accepted or structured_unavailable/structured_blocker with reason |

不可用项目不能进入 accepted count。每个不可用项目必须记录 `failure_category`、`reason`、`next_action`。

## 5. PRD/spec review checklist

- 是否仍遵守不声称完整设计意图恢复。
- 是否避免 full call graph、runtime topology、data/control flow、type inference。
- 是否所有 accepted 都有 artifact/test/E2E evidence。
- 是否所有 Portal 状态项都有 evidence_ref 或 unresolved reason。
- 是否 cleanup plan 没有执行删除。
- 是否 contract breaking change 没有静默通过。

## 6. False-green audit checklist

- mock-only evidence 不能 accepted。
- structured_unavailable 不能 accepted。
- needs_review 不能 accepted。
- structured_blocker 不能 accepted。
- HTML 不能隐藏 warning/unresolved。
- 文档 claim 不能当 code fact。
