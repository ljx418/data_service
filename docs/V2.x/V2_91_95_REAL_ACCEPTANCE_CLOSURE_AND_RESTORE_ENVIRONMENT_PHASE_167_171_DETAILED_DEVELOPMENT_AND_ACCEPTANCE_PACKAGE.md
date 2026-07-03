# V2.91-V2.95 Phase 167-171 Detailed Development and Acceptance Package

## Phase 167 / V2.91：Restoreable Acceptance Runtime

Development plan：

- 新增或扩展 runtime restore service。
- 检查当前 Python、venv、pytest、dependency baseline。
- 尝试复跑 V2.81-V2.90 focused regression，不能运行时生成 structured blocker。

Acceptance plan：

- `runtime_diagnosis.json` 说明 runtime 是否可复跑。
- `focused_regression_result.json` 包含真实 command、exit code、status。
- 不允许将 service health 作为 pytest passed。

Focused test：

```text
pytest -q backend/tests/test_v2_91_restoreable_acceptance_runtime.py
```

## Phase 168 / V2.92：Route A Representative Material Closure

Development plan：

- 实现 Route A material intake。
- 记录资料来源类型、脱敏策略、截图/headless evidence、manual reviewer decision。
- 无资料时输出 `needs_review`。

Acceptance plan：

- 真实资料、脱敏审查、截图或 headless evidence、人工验收记录全部存在时才可 accepted。
- mock-only、sample-only、path-only 拒绝 accepted。

Focused test：

```text
pytest -q backend/tests/test_v2_92_route_a_material_closure.py
```

## Phase 169 / V2.93：Human Quality Decision Closure

Development plan：

- 读取 V2.84/V2.88 quality artifacts。
- 写入 human decision history。
- 生成 rule effect closure，确认 upstream hashes unchanged。

Acceptance plan：

- 每条 quality recommendation 有 human decision 或明确 needs_review。
- 自动建议不得 accepted。

Focused test：

```text
pytest -q backend/tests/test_v2_93_human_quality_decision_closure.py
```

## Phase 170 / V2.94：External Project E2E Path Closure

Development plan：

- 绑定 data_service、codexPat、HarnessOS、Navia 路径。
- 可读项目执行 scoped E2E 或 smoke。
- 缺路径项目写 structured_unavailable。

Acceptance plan：

- 每个项目都有 accepted、structured_unavailable 或 structured_blocker。
- 缺路径项目不得 accepted。

Focused test：

```text
pytest -q backend/tests/test_v2_94_external_project_path_e2e_closure.py
```

## Phase 171 / V2.95：Final Release Gate Closure

Development plan：

- 聚合 V2.91-V2.94 artifacts 与 V2.86-V2.90 accepted evidence。
- 接入 dependency hygiene、restore smoke、human approval state。
- 生成 final release report 和 false-green audit。

Acceptance plan：

- 所有高风险项 accepted 后 final release 才可 accepted。
- 任一 `needs_review`、`structured_unavailable`、`structured_blocker` 必须保留在 final report。

Focused test：

```text
pytest -q backend/tests/test_v2_95_final_release_gate_closure.py
```

## Final Stage Command Plan

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

## Required Final Audit

Final acceptance audit must include:

- Focused test results.
- Real data E2E results.
- PRD/spec review.
- False-green audit.
- Protected legacy diff check.
- Public surface guard.
- Explicit non-accepted states.

