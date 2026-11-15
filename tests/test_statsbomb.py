import json
import pytest
import requests

from fpi.data.statsbomb import (
    DataUnavailableError, DataValidationError, DownloadError,
    download_reference_match, load_reference_match, select_reference_match,
    validate_events,
)

def test_select_reference_match(match):
    assert select_reference_match([match, {"match_date": "2022-12-11"}])["match_id"] == 3869486

def test_reference_match_rejects_wrong_score(match):
    match["home_score"] = 0
    with pytest.raises(DataValidationError, match="Score"):
        select_reference_match([match])

def test_reference_match_rejects_wrong_id(match):
    match["match_id"] = 123
    with pytest.raises(DataValidationError, match="identifiant"):
        select_reference_match([match])

def test_validate_events_rejects_duplicate_ids(match, events):
    events[1]["id"] = events[0]["id"]
    with pytest.raises(DataValidationError, match="dupliqué"):
        validate_events(events, match)

def test_validate_events_rejects_missing_second_half(match, events):
    with pytest.raises(DataValidationError, match="deux mi-temps"):
        validate_events([e for e in events if e["period"] == 1], match)

def test_no_cache_means_no_network(tmp_path):
    with pytest.raises(DataUnavailableError):
        load_reference_match(tmp_path)
    assert list(tmp_path.iterdir()) == []

class FakeResponse:
    def __init__(self, content):
        self.content = json.dumps(content).encode("utf-8")
    def raise_for_status(self):
        return None

def test_explicit_download_and_offline_reload(tmp_path, match, events):
    requested_urls = []
    def get(url, **kwargs):
        requested_urls.append(url)
        assert kwargs["timeout"] == 30
        return FakeResponse([match] if "/matches/" in url else events)
    imported = download_reference_match(tmp_path, getter=get)
    assert imported[2]["validated_events"] == 5
    assert len(requested_urls) == 2
    assert imported[2]["events_url"].endswith("events/3869486.json")
    assert load_reference_match(tmp_path)[1] == events
    assert len(requested_urls) == 2
    assert all((tmp_path / p).exists() for p in
               ("reference_match.json", "reference_events.json", "reference_provenance.json"))

def test_incomplete_download_has_no_cache(tmp_path, match):
    def get(url, **kwargs):
        if "/matches/" in url:
            return FakeResponse([match])
        raise requests.Timeout("offline")
    with pytest.raises(DownloadError, match="Téléchargement"):
        download_reference_match(tmp_path, getter=get)
    assert list(tmp_path.iterdir()) == []

def test_corrupt_cache_is_rejected(tmp_path, match, events):
    download_reference_match(tmp_path, getter=lambda url, **kw: FakeResponse([match] if "/matches/" in url else events))
    (tmp_path / "reference_provenance.json").write_text('{"match_id": 4}', encoding="utf-8")
    with pytest.raises(DataValidationError, match="Traçabilité"):
        load_reference_match(tmp_path)
