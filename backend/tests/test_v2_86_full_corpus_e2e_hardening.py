import json

from data_service.code_assets.real_document_full_corpus_release.full_corpus import FullCorpusE2EHardeningService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v286"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_86_PRD.md").write_text("# V2.86 PRD\n\n全量真实文档验收。\n", encoding="utf-8")
    (docs / "V2_86_REPORT.html").write_text("<html><body><h1>验收报告</h1><p>真实文档</p></body></html>", encoding="utf-8")
    (docs / "V2_86_SCHEMA.json").write_text('{"phase": "V2.86", "status": "planned"}', encoding="utf-8")
    (docs / "V2_86_TARGET.drawio").write_text("<mxfile><diagram>目标架构</diagram></mxfile>", encoding="utf-8")
    (docs / ".tmp").mkdir()
    (docs / ".tmp" / "ignored.md").write_text("ignored", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V286")["asset"].codebase_id
    return workspace, codebase_id


def test_v286_full_corpus_uses_real_docs_and_source_trace(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = FullCorpusE2EHardeningService(workspace, workspace_id="v286").build_full_corpus(codebase_id)
    run = payload["data"]["full_corpus_run"]

    assert payload["status"] == "accepted"
    assert run["input_scope"] == "docs/V2.x"
    assert run["processed_count"] == 4
    assert {row["parser"] for row in run["rows"]} == {"markdown", "html", "json", "drawio"}
    assert all(row["source_ref"].startswith("repo://docs/V2.x/") for row in run["rows"])
    assert payload["data"]["parser_failures"]["failures"] == []
    assert "does not claim full call graph" in run["graph_claim_boundary"]
    assert str(tmp_path) not in json.dumps(payload, ensure_ascii=False)


def test_v286_html_section_extractor_bug_is_structured_blocker(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    asset = CodebaseRegistry(workspace, workspace_id="v286").describe(codebase_id)
    bad_html = asset.root_path / "docs" / "V2.x" / "V2_86_BAD.html"
    bad_html.write_text("name 'Section' is not defined", encoding="utf-8")

    payload = FullCorpusE2EHardeningService(workspace, workspace_id="v286").build_full_corpus(codebase_id)
    failures = payload["data"]["parser_failures"]["failures"]

    assert payload["status"] == "structured_blocker"
    assert any(item["failure_category"] == "extractor_bug" for item in failures)
    assert any(item["kind"] == "structured_blocker" for item in payload["unresolved"])
