# V2.116-V2.120 Development and Acceptance Plan

## 1. 总体流程

每个子阶段必须先完成 development plan、acceptance plan、pre-implementation audit，再进入实现。子阶段结束后必须产出 focused tests、真实 `/mnt/c/workspace` E2E、PRD/spec review、false-green audit 和 acceptance note。

## 2. 子阶段计划

| 阶段 | 开发动作 | 验收动作 | 出门状态 |
| --- | --- | --- | --- |
| V2.116 | 读取 V2.111 OCR candidates；生成 anchor registry；运行 provider 或记录 blocker | 验证 hash、source ref、anchor、provider output；拒绝 direct text extraction 冒充 OCR | OCR rows accepted 或 needs_review/structured_unavailable |
| V2.117 | 对 in-scope 文档执行 import/query/source trace batch | 验证每条 accepted row 有完整 source chain | Source rows accepted 或 structured_unavailable |
| V2.118 | 使用 headless 捕获 `/knowledge` 或 report 截图 | 验证 screenshot manifest、页面状态、路径脱敏；浏览器不可用时 blocker | UI evidence accepted 或 structured_blocker |
| V2.119 | 建立 safe build allowlist、approval state 和 managed sandbox contract；sandbox 未通过前只生成 proposal | 验证未批准命令不执行；无 sandbox 时真实命令不执行；日志截断脱敏；timeout/cache/retry 记录 | Build rows accepted、needs_review、structured_unavailable 或 structured_blocker |
| V2.120 | 聚合 V2.116-V2.119 artifacts，复跑 final gate | 验证 high-risk 全部 accepted 或 approved out_of_scope；执行 false-green audit | Final accepted 或可信 non-accepted |

## 3. 用户体验验收路径

1. 维护者打开 report，看到 OCR 候选文件、hash、anchor 状态和补证动作。
2. 审计者点击文档行，看到 import artifact、query result、source trace refs。
3. 维护者打开 UI evidence 区，看到真实截图或浏览器依赖 blocker。
4. Agent 查看 safe build allowlist；只有 approved decision 和 managed sandbox 都有效时才执行命令，否则展示 proposal 和 blocker。
5. 维护者复跑 final gate，看到为什么可以或不能出门。

## 4. 共享验收命令

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_116_ocr_anchor_provider_closure.py \
  backend/tests/test_v2_117_source_trace_batch_closure.py \
  backend/tests/test_v2_118_headless_ui_visual_acceptance.py \
  backend/tests/test_v2_119_safe_build_allowlist_governance.py \
  backend/tests/test_v2_120_final_portfolio_acceptance_rerun.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests
npm --prefix frontend run build
git diff --check
git diff --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
git diff --cached --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 5. 真实 E2E 命令计划

```text
PYTHONPATH=backend python3 -m data_service portfolio-real-evidence build \
  --workspace-id v2_116_120_real \
  --root /mnt/c/workspace \
  --max-code-projects 3 \
  --timeout-seconds 120 \
  --headless
```

有界执行只允许验证 runtime governance，不得作为全量项目 accepted。未执行项目必须保留 queue row 和 `deferred_by_limit` 或等价结构化原因。
