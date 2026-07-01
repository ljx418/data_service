# V2.81-V2.85 Development and Acceptance Plan

## 1. 开发计划

### 1.1 真实资料路线

本阶段后续实现和验收按以下路线执行：

| 路线 | 用途 | 验收含义 |
| --- | --- | --- |
| Route A 用户提供真实资料 | 最终代表性人工验收 | 可以作为 real-document UX accepted 候选 |
| Route B 仓库内真实项目文档 | 自动化 dry run、工程烟测、报告结构验证 | 可以证明自动化路径，不替代用户代表性人工接受 |
| Route C structured unavailable | 无资料、无权限、无路径时 | 不能 accepted，必须保留 next action |
| Route D mock/synthetic fixture | 单元测试或开发辅助 | 不能作为真实资料 accepted evidence |

### V2.81 Real Document Sample and Scenario Contract

目标效果：

- 维护者能看到真实资料样本、脱敏规则、导入方式、目标路径和截图要求。

文档开发：

- 定义真实资料样本 contract。
- 定义人工体验路径和截图标准。
- 定义 mock-only、sample-only、真实资料的状态区分。

验收：

- 未提供真实资料时必须是 `needs_review`。
- 真实资料样本必须说明来源类型、脱敏规则和验收用途。

### V2.82 Real Document Import and Wiki Acceptance

目标效果：

- 维护者能用真实资料完成导入、解析和 Wiki artifact 验收。

文档开发：

- 定义 source import / workspace / build / Wiki artifact 验收步骤。
- 定义导入失败、格式不支持、低信号资料的状态分类。

验收：

- accepted 必须有真实资料、执行步骤、artifact refs 和截图证据。
- 解析失败不能隐藏，必须进入 `needs_review` 或 `structured_blocker`。

### V2.83 Retrieval, GraphRAG and Source Trace Acceptance

目标效果：

- 维护者能对真实资料执行检索、GraphRAG 和 Source trace，并理解结果来源。

文档开发：

- 定义查询用例、预期结果、source trace 检查点。
- 定义 GraphRAG 结果边界，禁止过度解释。

验收：

- 检索结果必须能回到 source / unit / evidence。
- Source trace 缺失不能 accepted。
- GraphRAG 不能被写成完整调用图或运行拓扑。

### V2.84 Quality Governance and Correction Acceptance

目标效果：

- 维护者能看到真实资料质量问题、反馈、纠错计划和人工 review 状态。

文档开发：

- 定义 low-signal audit、quality feedback、correction plan、rule review 验收路径。
- 定义质量治理截图和 evidence refs。

验收：

- 质量问题不能被 UI 或报告隐藏。
- 缺人工 review 的纠错建议必须是 `needs_review`。

### V2.85 Release Closure Rerun and Human Sign-off

目标效果：

- 维护者能把真实资料验收、外部项目状态、warning gate、restore/smoke 和 human approval 汇总成出门结论。

文档开发：

- 定义 release rerun checklist。
- 定义 final manual acceptance report。
- 定义 final release accepted 的必要条件。

验收：

- 外部项目路径缺失时仍保持 `structured_unavailable`。
- human approval 缺失时 release readiness 不能 accepted。
- 真实资料人工验收缺失时 final release 不能 accepted。

## 2. 总体验收命令计划

文档阶段验收：

```text
python3 -m json.tool docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_HUMAN_AUDIT_EVIDENCE_INDEX.json
python3 -m json.tool docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_REAL_E2E_EVIDENCE.json
python3 -m json.tool docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_VISUAL_EVIDENCE_MANIFEST.json
git diff --check
```

后续实现或补验阶段计划：

```text
pytest -q backend/tests/test_public_surface_guard.py
python -m compileall backend/data_service backend/app/api backend/tests
```

真实资料补验必须另行记录：

- 资料来源类型；
- 执行步骤；
- 截图证据；
- artifact refs；
- false-green audit；
- failed / needs_review / structured_unavailable / structured_blocker 原因。

## 3. 审计意见

当前文档阶段目标是 pass for implementation guidance，不能写成 pass for implementation acceptance。真实资料未补验前，人工真实资料体验保持 `needs_review`。
