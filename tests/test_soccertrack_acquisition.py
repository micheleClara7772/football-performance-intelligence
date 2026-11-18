"""SoccerTrack v2 selection is a gated one-match download, never implicit."""
import pytest
from scripts.prepare_soccertrack import plan, MATCH_IDS


def test_only_one_match_patterns_and_stable_release():
    p = plan("117093")
    assert p["revision"] == "v1.2"
    assert p["match_id"] == "117093"
    assert len(p["allow_patterns"]) == 4
    assert all("117093" in x for x in p["allow_patterns"])
    assert p["requires_account_agreement"]
    assert not p["automatic_rights_acceptance"]
    assert len(MATCH_IDS) == 10


def test_unknown_match_rejected():
    with pytest.raises(ValueError):
        plan("unknown")
