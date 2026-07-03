# V2.96 / Phase 172 Development, Acceptance, and Pre-implementation Audit

## 1. Phase Goal

Phase 172 只聚焦 Default CLI Gap Closure。目标是在代码实现开始前冻结 CLI gap 复现命令、CLI/MCP/HTTP parity 验收样本、受保护文件边界和 false-green 拒绝规则。

本文件是 phase-specific planning，不是实现完成证据。

## 2. Current Gap

当前已知 gap：

```text
PYTHONPATH=backend python3 -m data_service code real-acceptance-closure --help
```

该命令当前使用 legacy `_build_parser()` 命令集并拒绝 `code`，因此默认 shell CLI 不能被描述为 accepted。

## 3. Development Plan

实现阶段应优先选择最小变更路线：

1. 审计 `python -m data_service` 默认入口、legacy parser、knowledge code parser 的连接关系。
2. 修复默认 shell CLI 到 code parser 的入口链路，或提供唯一真实可用且文档一致的替代命令。
3. 生成 `cli_gap_closure/cli_surface_result.json`，记录 default shell command、parser inventory、MCP tool inventory、HTTP route inventory 和 gap status。
4. 生成 `cli_gap_closure/cli_surface_report.md`，解释修复结果、保留 gap 或 deprecation 的原因。
5. 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非先获得明确批准。

## 4. Acceptance Plan

Phase 172 accepted 必须同时满足：

- 默认 shell CLI 有真实可复跑命令结果。
- MCP tool inventory 包含 real-acceptance-closure 或 automated-evidence-closure 对应 build/read tools。
- HTTP route inventory 包含对应 read/build route family。
- CLI、MCP、HTTP 三类 surface 指向同一组 persisted artifacts 或明确说明差异。
- focused test 覆盖 default shell CLI gap、parser inventory、MCP/HTTP parity 和 false-green 拒绝。

## 5. Focused Test Target

计划测试：

```text
backend/tests/test_v2_96_default_cli_gap_closure.py
```

计划最终验收命令：

```text
PYTHONPATH=backend python3 -m pytest -q \
  backend/tests/test_v2_96_default_cli_gap_closure.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests

git diff --check

git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 6. False-green Rejection

以下情况不能 accepted：

- 只验证 code parser inventory，但默认 shell CLI 仍失败。
- 只验证 MCP/HTTP，而不验证 CLI。
- CLI 命令返回帮助文本但没有覆盖目标 command group。
- 修改受保护 legacy 文件但没有明确批准。
- 使用文档 claim 代替真实命令输出。

## 7. Pre-implementation Audit

Fatal findings: none.

Major findings: none for documentation readiness.

Minor findings:

- 默认 shell CLI gap 是真实已知缺口，必须在实现阶段通过命令结果关闭或结构化保留。
- 如果修复入口需要触及受保护 legacy 文件，必须停止并请求明确批准。

Audit opinion:

Pass for Phase 172 implementation guidance. Not pass for implementation acceptance.
