# V2.76-V2.80 Visual Evidence Reproduction Guide

> This guide supports human audit of the committed visual evidence. It does not claim that final release is accepted, and it does not replace focused tests, real E2E evidence, or PRD/spec review.

## Committed Source Page

- Source page: `docs/V2.x/visual_acceptance_assets/v2_76_80/scenario_capture.html`
- Committed screenshots: `docs/V2.x/visual_acceptance_assets/v2_76_80/*.png`
- Visual manifest: `docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_VISUAL_EVIDENCE_MANIFEST.json`
- Audit report: `docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_VISUAL_ACCEPTANCE_REPORT.html`

The source page contains these human-auditable sections:

1. `V2.76-V2.80 项目验收硬化：维护者总览`
2. `目标架构与当前实现`
3. `场景 1：验收矩阵对齐`
4. `场景 2：外部项目真实绑定`
5. `场景 3：CI Warning 出门门禁`
6. `场景 4：维护者状态面板`
7. `场景 5：发布就绪闭环`

## Non-Interactive Metadata Check

This check verifies that the committed screenshots named in the manifest exist and still match the recorded dimensions and color counts.

```bash
python3 - <<'PY'
import json
from pathlib import Path
from PIL import Image

manifest = json.loads(Path("docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_VISUAL_EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
issues = []
for shot in manifest["screenshots"]:
    path = Path(shot["path"])
    if not path.exists():
        issues.append((shot["id"], "missing", str(path)))
        continue
    image = Image.open(path)
    colors = image.convert("RGB").getcolors(maxcolors=10000000)
    actual = (image.size[0], image.size[1], len(colors or []))
    expected = (shot["width"], shot["height"], shot["color_count"])
    if actual != expected:
        issues.append((shot["id"], "metadata_mismatch", expected, actual))

print("visual_manifest_items", len(manifest["screenshots"]))
print("visual_manifest_issues", len(issues))
for issue in issues:
    print("ISSUE", issue)
PY
```

Expected result:

```text
visual_manifest_items 7
visual_manifest_issues 0
```

## Optional Headless Browser Recheck

If Chrome or Chromium is installed, use a temporary output directory so the committed screenshots are not overwritten during review.

```bash
mkdir -p .tmp/v2_76_80_visual_recheck
SCENARIO_URL="file://$PWD/docs/V2.x/visual_acceptance_assets/v2_76_80/scenario_capture.html"
CHROME_BIN="${CHROME_BIN:-google-chrome}"

"$CHROME_BIN" \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --window-size=1280,900 \
  --screenshot=.tmp/v2_76_80_visual_recheck/scenario_first_view.png \
  "$SCENARIO_URL"
```

If the host uses a different binary, set `CHROME_BIN`, for example:

```bash
CHROME_BIN=chromium ./your-review-command
```

This command validates that the source page can render headlessly. It does not prove final release readiness and should not rewrite `needs_review` or `structured_unavailable` to `accepted`.

## Audit Boundaries

- The committed screenshots are evidence of the visual report state, not evidence that external projects became available.
- `codexPat`, `HarnessOS`, and `Navia` remain `structured_unavailable` until real readable repository paths are provided and rerun.
- Human release approval remains `needs_review`.
- Visual evidence must be interpreted together with the focused test results and `V2_76_80_PROJECT_ACCEPTANCE_HARDENING_REAL_E2E_EVIDENCE.json`.
