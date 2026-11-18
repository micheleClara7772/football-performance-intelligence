"""Unit tests: no live gated access or secret required."""
from pathlib import Path
from scripts.check_soccertrack_access import check_access, DATASET, REVISION, SMALL_FILE


def test_missing_token_fails_closed(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    import huggingface_hub
    monkeypatch.setattr(huggingface_hub, "get_token", lambda: None)
    assert check_access()["status"] == "NEEDS_AUTHENTICATION"


def test_verified_access_with_mocked_downloader(tmp_path):
    seen = {}
    def fake_download(**kwargs):
        seen.update(kwargs)
        path = Path(kwargs["local_dir"]) / "proof.md"
        path.write_text("authorized only", encoding="utf-8")
        return str(path)
    result = check_access(token="DO_NOT_PRINT", downloader=fake_download)
    assert result["verified_file_access"] is True
    assert result["full_match_downloaded"] is False
    assert seen["repo_id"] == DATASET and seen["revision"] == REVISION
    assert seen["filename"] == SMALL_FILE
    assert seen["force_download"] is True
    assert "DO_NOT_PRINT" not in str(result)


def test_bad_credentials_are_not_leaked():
    def forbidden(**kwargs):
        raise RuntimeError("token=UNSAFE_SECRET_SHOULD_NOT_APPEAR")
    result = check_access(token="UNSAFE_SECRET_SHOULD_NOT_APPEAR", downloader=forbidden)
    assert result["status"] == "ACCESS_NOT_VERIFIED"
    assert result["verified_file_access"] is False
    assert "UNSAFE_SECRET_SHOULD_NOT_APPEAR" not in str(result)
