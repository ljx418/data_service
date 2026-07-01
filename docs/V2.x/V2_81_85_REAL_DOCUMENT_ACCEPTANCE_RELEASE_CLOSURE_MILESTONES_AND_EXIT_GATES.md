# V2.81-V2.85 Milestones and Exit Gates

## 1. 里程碑

| 里程碑 | 阶段 | 完成物 | 用户可见效果 |
| --- | --- | --- | --- |
| M1 | V2.81 | sample contract、manual scenario plan | 维护者知道要用什么真实资料、如何验收 |
| M2 | V2.82 | import run、Wiki artifact review | 维护者能确认真实资料导入和 Wiki 结果 |
| M3 | V2.83 | query trace review、GraphRAG review | 维护者能检索真实资料并追溯来源 |
| M4 | V2.84 | quality governance review、correction report | 维护者能看到质量问题和纠错状态 |
| M5 | V2.85 | release closure rerun、manual acceptance report | 维护者能判断是否满足最终出门条件 |

## 2. 阶段进入条件

每个子阶段进入实现或补验前必须具备：

- development plan；
- acceptance plan；
- pre-implementation audit；
- PRD/spec review；
- 真实资料或结构化不可用原因；
- protected legacy file strategy；
- false-green risk checklist。

Fatal 或 major 审计意见未关闭时不得进入实现。

## 3. 阶段出门条件

每个子阶段结束必须具备：

- focused tests 或文档阶段等效检查；
- 真实资料 E2E 证据或 `needs_review` 原因；
- PRD/spec review；
- false-green audit；
- acceptance audit report；
- public artifact redaction check；
- protected legacy diff check。

## 4. 最终出门条件

V2.81-V2.85 最终 accepted 需要：

- 真实文档资料人工验收 accepted；
- 真实资料导入、解析、Wiki artifact、检索/GraphRAG、Source trace、质量治理至少覆盖约定关键路径；
- 所有 accepted 结论有 artifact refs、截图证据、命令或真实 API/CLI/MCP 结果；
- `codexPat`、`HarnessOS`、`Navia` 有 accepted 或 structured unavailable/blocker，不可用不算 accepted；
- human approval 已记录或 release readiness 保持 `needs_review`；
- protected legacy 文件无 diff；
- final release accepted 不得绕过任何高风险项。

## 5. 阻断条件

出现以下情况必须停止并回到开发计划：

- 把思维导图方向 OK 写成真实资料验收 accepted；
- 把 `structured_unavailable`、`structured_blocker`、`needs_review` 写成 accepted；
- 用 mock-only document 证明真实资料体验；
- 以截图替代 source trace 或 artifact refs；
- GraphRAG 输出被写成 full call graph 或 runtime topology；
- public artifact 泄露本地绝对路径、secret、token、raw traceback；
- 需要修改 protected legacy 文件但没有用户明确批准。
