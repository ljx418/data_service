# V2.81-V2.85 Test and E2E Mapping

## 1. 文档阶段检查

| 检查项 | 命令或方法 | 通过标准 |
| --- | --- | --- |
| JSON 证据可解析 | `python3 -m json.tool docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_HUMAN_AUDIT_EVIDENCE_INDEX.json` | exit 0 |
| 真实 E2E 快照可解析 | `python3 -m json.tool docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_REAL_E2E_EVIDENCE.json` | exit 0 |
| 视觉 manifest 可解析 | `python3 -m json.tool docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_VISUAL_EVIDENCE_MANIFEST.json` | exit 0 |
| drawio 可解析 | 统计 `<diagram` 页数 | 不超过 8 页 |
| 空白检查 | `git diff --check` | passed |

## 2. 后续 focused tests 计划

后续进入实现时建议新增：

```text
backend/tests/test_v2_81_real_document_sample_contract.py
backend/tests/test_v2_82_real_document_import_wiki.py
backend/tests/test_v2_83_retrieval_graphrag_source_trace.py
backend/tests/test_v2_84_quality_governance_real_document.py
backend/tests/test_v2_85_release_closure_rerun.py
```

## 3. 真实资料 E2E 场景

| 场景 | 用户动作 | 必须记录 |
| --- | --- | --- |
| 真实资料导入 | 创建 workspace，导入真实文档 | 资料类型、导入结果、source refs、截图 |
| Wiki artifact | 触发 build，查看 Wiki artifact | page refs、distill refs、截图 |
| 检索 | 输入真实问题并查询 | query、result、source refs、截图 |
| GraphRAG | 查看社区/邻居/图查询 | graph result、边界说明、截图 |
| Source trace | 从结果回到 source/unit/evidence | trace refs、失败原因 |
| 质量治理 | 查看 low signal / feedback / correction | quality refs、review 状态 |
| Release closure | 汇总真实资料、外部项目、human approval | final status、false-green audit |

## 4. False-green 审计

必须确认：

- mock-only 资料没有写成真实资料 accepted；
- Source trace 缺失没有写成 accepted；
- GraphRAG 没有声称 full call graph 或 runtime topology；
- human approval 缺失时 release readiness 不能 accepted；
- 外部项目 unavailable 不计入 accepted；
- 截图不能替代 artifact refs 或真实执行结果。
