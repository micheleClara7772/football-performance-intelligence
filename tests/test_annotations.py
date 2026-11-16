"""Les annotations ne sont jamais fondées sur des événements inventés en interface."""
import json

import pytest

from fpi.analysis.annotations import (
    build_annotation, eligible_events, export_document, format_video_clock,
    import_document, parse_video_clock,
)

FIFA_URL = "https://www.youtube.com/watch?v=5GVitElttLY"


def test_filter_real_event_by_team_period_kind_and_clock(events):
    selected = eligible_events(events, "Morocco", "Shot", 1, 30, 45)
    assert [event["id"] for event in selected] == ["b"]
    assert eligible_events(events, "Portugal", "Shot", 1) == []
    with pytest.raises(ValueError):
        eligible_events(events, "Morocco", "Unknown type", 1)


def test_clock_is_from_video_summary_not_from_match():
    assert parse_video_clock("02:43") == 163
    assert format_video_clock(163) == "02:43"
    assert parse_video_clock("") is None
    for value in ("2:99", "-1:21", "abc", "1:1:2"):
        with pytest.raises(ValueError):
            parse_video_clock(value)


def test_notes_require_source_and_manual_video_time(events):
    event = events[1]
    note = build_annotation(
        event, "Déplacement de l'attaquant à revoir", "Hypothèse", FIFA_URL, 43,
        allowed_video_urls=(FIFA_URL,),
    )
    assert note["event_id"] == "b"
    assert note["match_minute"] == 40
    assert note["video_seconds"] == 43
    with pytest.raises(ValueError):
        build_annotation(event, " ", "Observation")
    with pytest.raises(ValueError):
        build_annotation(event, "Action", "Observation", video_seconds=30)
    with pytest.raises(ValueError):
        build_annotation(event, "Action", "Observation", "https://example.org/video")


def test_export_import_roundtrip_verified_match(events):
    annotation = build_annotation(events[1], "Zone à analyser", "Observation")
    raw = export_document(3869486, [annotation])
    output = import_document(json.loads(raw), 3869486, events)
    assert output["b"] == annotation
    assert "Shot" in raw and "reference_events.json" not in raw


def test_import_rejects_foreign_match_event_or_tampered_minute(events):
    annotation = build_annotation(events[1], "Action test", "Observation")
    payload = json.loads(export_document(3869486, [annotation]))
    with pytest.raises(ValueError):
        import_document(payload, 1, events)
    payload["annotations"][0]["match_minute"] = 41
    with pytest.raises(ValueError):
        import_document(payload, 3869486, events)
    payload["annotations"][0]["match_minute"] = 40
    payload["annotations"][0]["event_id"] = "missing"
    with pytest.raises(ValueError):
        import_document(payload, 3869486, events)
