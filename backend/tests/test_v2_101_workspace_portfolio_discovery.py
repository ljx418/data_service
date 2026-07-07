from data_service.workspace_portfolio import WorkspacePortfolioService


def _workspace_fixture(tmp_path, monkeypatch):
    root = tmp_path / "workspace-root"
    repo = root / "data_service"
    docs = repo / "docs"
    media = root / "技术分享"
    cache = root / "node_modules"
    docs.mkdir(parents=True)
    media.mkdir(parents=True)
    cache.mkdir(parents=True)
    (repo / ".git").mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (docs / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    (media / "slides.pptx").write_text("pptx placeholder\n", encoding="utf-8")
    (media / "scan.png").write_text("image placeholder\n", encoding="utf-8")
    managed = tmp_path / "managed" / "v2101"
    managed.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return managed, root


def test_v2101_workspace_portfolio_scan_uses_real_workspace_and_classification_evidence(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioService(managed, workspace_id="v2101").scan(root=root)

    projects = {item["display_name"]: item for item in payload["data"]["project_registry"]["projects"]}
    assert projects["data_service"]["classification"] == "code_project"
    assert projects["data_service"]["evidence_refs"]
    assert projects["技术分享"]["classification"] in {"media_corpus", "doc_project"}
    assert any(item["display_name"] == "node_modules" for item in payload["data"]["project_registry"]["ignored"])
    assert payload["data"]["project_registry"]["status"] == "accepted"
