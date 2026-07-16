# V2.116-V2.120 Detailed Test Fixtures and Negative Cases

## 1. Deterministic Fixtures

除真实 `/mnt/c/workspace` E2E 外，必须准备确定性 fixture：

```text
tmp_workspace/
  project_a/
    docs/scan.png
    docs/scan.png.ocr-anchor.txt
    docs/text.pdf
  project_b/
    package.json
  upstream/
    v2_111_115_artifacts/
```

真实 workspace E2E 用于覆盖现实输入；deterministic fixture 用于稳定验证状态机、schema、stale 和安全负向用例。

## 2. Required Positive Cases

| Case ID | Requirement |
| --- | --- |
| TC-OCR-001 | sidecar anchor + provider available -> output_ref/output_hash/anchor_hit 后 accepted |
| TC-SRC-001 | import_ref + query_ref + source_trace_refs 同源 -> accepted |
| TC-UI-001 | headless page has required selectors and screenshot hash -> accepted |
| TC-BLD-001 | complete normalized binding digest matches executable/env/sandbox/project input/runtime/network/output policy and command succeeds -> accepted |
| TC-GATE-001 | all high-risk rows accepted -> final accepted |

## 3. Required Negative Cases

| Case ID | Negative condition | Expected result |
| --- | --- | --- |
| TC-RUN-001 | cross-run artifact 未在 source_run_refs 中声明 | final gate structured_blocker |
| TC-RUN-002 | input hash changed after latest run | stale structured_blocker |
| TC-RUN-003 | source_run_refs 声明跨 run artifact 且 lineage_root/input hash/artifact hash 均匹配 | allowed lineage-bound input |
| TC-OCR-002 | tesseract missing | OCR row structured_unavailable |
| TC-OCR-003 | OCR execution succeeded but anchor_hit=false | needs_review |
| TC-OCR-004 | direct-text PDF extracted | source evidence only, OCR not accepted |
| TC-OCR-005 | chi_sim language pack missing for Chinese anchor | structured_unavailable |
| TC-SRC-002 | import/query/source refs from different source_id | not accepted |
| TC-SRC-003 | file exists but no import_ref | not accepted |
| TC-UI-002 | screenshot file exists but DOM selector missing | not accepted |
| TC-UI-003A | browser executable/library missing | structured_unavailable |
| TC-UI-003B | capture blocked by sandbox/runtime policy | structured_blocker |
| TC-UI-003C | page is blank, app 500, or DOM contract broken | failed |
| TC-BLD-002 | approval digest differs from normalized binding digest | command skipped, not accepted |
| TC-BLD-003A | cwd symlink escape attempt rejected before execution | structured_blocker |
| TC-BLD-003B | path escape guard bypassed or original project actually written | failed |
| TC-BLD-004 | command contains shell metacharacters | blocked |
| TC-BLD-005 | timeout leaves child process alive | failed |
| TC-BLD-006 | logs contain secret-like value after redaction | failed |
| TC-BLD-007 | managed sandbox unavailable | proposal generated, execution skipped, structured_blocker |
| TC-BLD-008 | approval lacks sandbox/env/executable/project input digest | command skipped, not accepted |
| TC-DEC-001 | approved_out_of_scope expired | cannot satisfy final accepted |
| TC-DEC-002 | decision revoked | cannot satisfy final accepted |
| TC-DEC-003 | revoke lacks revokes_decision_id | schema validation fails |
| TC-SCHEMA-001 | any JSON artifact lacks Shared Artifact Envelope | schema validation fails |
| TC-SCHEMA-002 | business fields appear outside data | schema validation fails |
| TC-UI-004 | UI exposes anchor/decision write button in this stage | test fails |
| TC-READ-001 | read/report triggers build side effects | test fails |

## 4. Test Mapping

- `test_v2_116_ocr_anchor_provider_closure.py` covers TC-OCR-*。
- `test_v2_117_source_trace_batch_closure.py` covers TC-SRC-*。
- `test_v2_118_headless_ui_visual_acceptance.py` covers TC-UI-*。
- `test_v2_119_safe_build_allowlist_governance.py` covers TC-BLD-*。
- `test_v2_120_final_portfolio_acceptance_rerun.py` covers TC-RUN-*、TC-DEC-*、TC-GATE-*、TC-SCHEMA-*、TC-READ-*。
- `test_public_surface_guard.py` covers CLI/MCP/HTTP registration and protected file boundaries。
