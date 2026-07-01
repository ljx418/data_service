# V2.86-V2.90 Development and Acceptance Plan

## 1. 开发计划

### 1.1 真实资料路线

| 路线 | 用途 | 验收含义 |
| --- | --- | --- |
| Route A 用户代表性真实资料 | 最终代表性人工验收 | 可作为 final real-document UX accepted 候选 |
| Route B 仓库内真实项目文档 | 自动化 dry run、工程烟测、报告结构验证 | 可证明自动化路径，不替代 Route A |
| Route C structured unavailable | 无资料、无权限、无路径时 | 不能 accepted，必须保留 next action |
| Route D mock/synthetic fixture | 单元测试或开发辅助 | 不能作为真实资料 accepted evidence |

### V2.86 Full Corpus E2E Hardening

目标体验：

- 维护者能对 `docs/V2.x` 全量真实文档执行导入、解析、构建、查询和 Source trace 验收。
- 维护者能看到 HTML extractor 失败、低信号资料和 unsupported format 的分类。

开发内容：

- 定义全量文档输入范围、忽略规则和 failure category。
- 规划 HTML extractor `Section` 错误的复现、修复和验收。
- 生成全量构建报告、parser failure 报告和截图证据索引。

验收：

- 全量 `docs/V2.x` 构建成功或给出 `structured_blocker`。
- HTML extractor 错误不能隐藏。
- accepted 必须有 artifact refs、命令/API 结果和截图或等价 headless evidence。

### V2.87 Route A Representative Material Acceptance

目标体验：

- 维护者能提交或绑定用户代表性真实资料包，确认脱敏规则和验收路径。
- 审计者能确认 Route A 不由 Route B 或 mock-only 替代。

开发内容：

- 定义 sample pack contract、redaction review、manual acceptance record。
- 定义人类截图标准、最小体验步骤和审批记录格式。
- 定义资料缺失时的 `needs_review` 状态和 next action。

验收：

- 未提供用户代表性资料时保持 `needs_review`。
- 提供资料后，每个 accepted row 必须有来源说明、脱敏说明、执行证据和人工确认。

### V2.88 Quality Governance Human Review Closure

目标体验：

- 维护者能审查质量建议、纠错建议和规则影响。
- 审计者能看到人工 review 对每条建议的接受、拒绝或继续 review 结论。

开发内容：

- 定义 human quality review artifact。
- 定义 correction decision history 和 rule effect review。
- 定义上游 artifact hash 只读校验。

验收：

- 无人工 review 的建议保持 `needs_review`。
- rule effect 不得改写上游原始 artifact。
- 所有 correction recommendation 必须有 evidence_refs 或 unresolved reason。

### V2.89 External Project E2E Closure

目标体验：

- 维护者能看到 `data_service`、`codexPat`、`HarnessOS`、`Navia` 的真实路径绑定状态。
- 可用项目能执行真实 E2E，不可用项目明确显示原因和下一步。

开发内容：

- 定义 external project path manifest。
- 定义 real E2E run record 和 unavailable diagnosis。
- 定义外部项目不可用不计 accepted 的 coverage rule。

验收：

- `data_service` 必须有真实本仓 E2E 结果。
- `codexPat`、`HarnessOS`、`Navia` 无真实路径时只能 `structured_unavailable`。
- mock-only 或 path-only 不能 accepted。

### V2.90 Release Gate and Restore Hygiene

目标体验：

- 维护者能看到最终出门状态：真实资料、全量文档、质量审查、外部项目、restore/smoke、dependency hygiene、human approval。
- 审计者能快速判断 release 是否可以 accepted。

开发内容：

- 定义 release gate summary 和 release readiness report。
- 定义 dependency hygiene 记录，包括 npm audit 已知风险。
- 定义工作树清理审计规则，不自动删除未确认文件。

验收：

- Route A 缺失、human approval 缺失、外部项目不可用、全量构建失败任一存在时 final release 不能 accepted。
- `needs_review`、`structured_unavailable`、`structured_blocker` 必须保留。

## 2. 总体验收命令计划

文档阶段验收：

```text
python - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET

docs = Path("docs/V2.x")
for path in docs.glob("V2_86_90_REAL_DOCUMENT_FULL_CORPUS_RELEASE_HARDENING_*.md"):
    text = path.read_text(encoding="utf-8")
    assert "accepted" in text or "needs_review" in text
ET.parse(docs / "V2_86_90_REAL_DOCUMENT_FULL_CORPUS_RELEASE_HARDENING_TARGET_STATE.drawio")
print("document parse ok")
PY
```

后续实现阶段计划命令：

```text
pytest -q backend/tests/test_v2_86_full_corpus_e2e_hardening.py \
  backend/tests/test_v2_87_route_a_representative_acceptance.py \
  backend/tests/test_v2_88_quality_governance_human_review.py \
  backend/tests/test_v2_89_external_project_e2e_closure.py \
  backend/tests/test_v2_90_release_gate_restore_hygiene.py \
  backend/tests/test_public_surface_guard.py

python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 3. 审计意见

当前文档阶段目标是 `pass for implementation guidance`，不能写成 `pass for implementation acceptance`。

进入代码实现前必须确认：

- drawio 已通过人工方向审查。
- 本阶段文档无 fatal/major 规格偏差。
- HTML extractor 全量构建失败有明确验收标准。
- Route A、外部项目、human approval 的不可用状态不会被误写 accepted。
