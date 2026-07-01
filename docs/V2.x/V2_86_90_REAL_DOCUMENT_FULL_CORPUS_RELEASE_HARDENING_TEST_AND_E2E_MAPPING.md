# V2.86-V2.90 Test and E2E Mapping

## 1. Focused Tests 规划

| 阶段 | 计划测试 | 验收重点 |
| --- | --- | --- |
| V2.86 | `backend/tests/test_v2_86_full_corpus_e2e_hardening.py` | 全量 docs 输入、HTML failure 分类、Source trace |
| V2.87 | `backend/tests/test_v2_87_route_a_representative_acceptance.py` | Route A contract、redaction、manual acceptance status |
| V2.88 | `backend/tests/test_v2_88_quality_governance_human_review.py` | quality review、correction decision、rule effect 不改写上游 |
| V2.89 | `backend/tests/test_v2_89_external_project_e2e_closure.py` | 外部路径 accepted/unavailable 分类 |
| V2.90 | `backend/tests/test_v2_90_release_gate_restore_hygiene.py` | release gate、restore/smoke、dependency hygiene、human approval |
| 公共守卫 | `backend/tests/test_public_surface_guard.py` | MCP/CLI/HTTP public surface 未破坏 |

## 2. 真实 E2E 映射

| 场景 | 输入 | 预期输出 | 不可 accepted 条件 |
| --- | --- | --- | --- |
| 全量 docs 构建 | `docs/V2.x` | full corpus run、parser failure、query/source trace report | HTML extractor 失败无记录 |
| Route A 验收 | 用户代表性真实资料 | sample pack contract、manual acceptance record | 未提供资料或 mock-only |
| 质量审查 | V2.84 quality artifacts | human quality review、decision history | 无人工审查 |
| 外部项目 | data_service/codexPat/HarnessOS/Navia | path manifest、project E2E records | 缺路径却 accepted |
| 发布出门 | M1-M4 artifacts | release gate summary、readiness report | human approval 缺失 |

## 3. 自动化可视化验收

后续实现阶段应优先使用 headless 浏览器或 API evidence 生成 HTML 报告。只有 headless 无法覆盖真实交互时，才使用会抢占焦点的 ChromeCli 或截图工具，并必须提前告知用户。

HTML 报告必须包含：

- 当前架构与目标架构实现状态。
- 真实用户体验路径截图或 headless evidence。
- 每个 accepted row 的 evidence refs。
- 每个 `needs_review`、`structured_unavailable`、`structured_blocker` 的原因和 next action。
- PRD/spec review 和 false-green audit。

## 4. 文档阶段验收

```text
rg -n "full call graph|runtime topology|data/control flow|type inference|完整恢复复杂项目设计意图" docs/V2.x/V2_86_90_REAL_DOCUMENT_FULL_CORPUS_RELEASE_HARDENING_*.md
python - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
ET.parse(Path("docs/V2.x/V2_86_90_REAL_DOCUMENT_FULL_CORPUS_RELEASE_HARDENING_TARGET_STATE.drawio"))
print("drawio xml ok")
PY
git diff --check
```

上述第一条命令如果出现命中，必须人工检查语境，只允许出现在禁止声明或边界说明中。

## 5. 最终验收报告要求

最终报告不得使用虚假验收或不实信息。不能通过的项目必须明确写入：

- status。
- reason。
- evidence_refs。
- next_action。
- 是否阻断 final release accepted。
