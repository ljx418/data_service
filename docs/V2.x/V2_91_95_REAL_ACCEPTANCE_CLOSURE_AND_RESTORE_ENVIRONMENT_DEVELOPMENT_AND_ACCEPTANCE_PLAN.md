# V2.91-V2.95 Development and Acceptance Plan

## 1. 总体策略

本阶段先完成文档基线，再进入后续实现。实现前必须完成每个子阶段的 development plan、acceptance plan 和 pre-implementation audit。实现后必须完成 focused tests、真实项目 E2E、PRD/spec review、false-green audit 和 acceptance audit report。

当前仅完成文档开发，不声明任何 V2.91-V2.95 功能已实现。

## 2. 子阶段开发计划

| 阶段 | 开发目标 | 计划产物 | 用户可见效果 |
| --- | --- | --- | --- |
| V2.91 | 恢复本机验收 runtime | `runtime_restore/runtime_diagnosis.json`、`restore_checklist.md`、`focused_regression_result.json` | 维护者能判断本机是否可复跑 pytest，若失败可看到明确恢复步骤 |
| V2.92 | Route A 真实资料验收闭环 | `route_a_closure/material_manifest.json`、`redaction_decision.json`、`manual_acceptance_record.md` | 维护者能上传或绑定代表性资料，并看到脱敏、截图和人工验收状态 |
| V2.93 | 人工质量决策闭环 | `quality_decision/human_decisions.jsonl`、`rule_effect_closure.json`、`quality_closure_report.md` | 维护者能确认或拒绝质量建议，审计者能追踪每条 decision |
| V2.94 | 外部项目路径与 E2E 闭环 | `external_project_closure/path_binding_decision.json`、`e2e_result_matrix.json`、`unavailable_decisions.md` | 维护者能看到每个外部项目的真实路径、E2E 结果或不可用原因 |
| V2.95 | Final Release Gate | `release_finalizer/final_gate_summary.json`、`final_release_report.md`、`false_green_audit.md` | 维护者能看到最终是否可出门，以及所有阻断项 |

## 3. 验收计划

共享验收命令计划：

```text
pytest -q \
  backend/tests/test_v2_91_restoreable_acceptance_runtime.py \
  backend/tests/test_v2_92_route_a_material_closure.py \
  backend/tests/test_v2_93_human_quality_decision_closure.py \
  backend/tests/test_v2_94_external_project_path_e2e_closure.py \
  backend/tests/test_v2_95_final_release_gate_closure.py \
  backend/tests/test_public_surface_guard.py

python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

文档阶段不要求这些测试存在或通过；实现阶段必须新增 focused tests 后复跑。

## 4. Pre-implementation Audit 要求

每个子阶段开始前必须确认：

- PRD 目标体验有明确 artifact 和测试映射。
- public surface 不与 V2.86-V2.90 混淆。
- 缺真实资料或人工确认时只允许 `needs_review`。
- 缺路径或环境不可用时只允许 `structured_unavailable` 或 `structured_blocker`。
- 无需修改 legacy 大文件。

## 5. False-green 防线

- pytest runtime 不可用不能写成 focused tests passed。
- Route A 缺资料不能 accepted。
- 质量建议缺人工 decision 不能 accepted。
- 外部项目缺路径不能 accepted。
- human approval 缺失不能 final release accepted。
- dependency audit 风险必须进入 release gate。

