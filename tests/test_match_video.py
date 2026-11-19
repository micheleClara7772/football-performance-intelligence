"""The coach's match explorer must never pretend to decode FIFA videos."""
import pytest
from fpi.ui.match_video import select_moments, CATEGORIES


def event(kind, minute, second, team="Morocco", period=1, **extra):
    return {
        "type": {"name": kind}, "minute": minute, "second": second,
        "period": period, "team": {"name": team},
        "player": {"name": "Un joueur"}, **extra,
    }


def test_real_match_moments_filter_and_sort_by_clock():
    events = [
        event("Shot", 75, 4, team="Portugal", period=2),
        event("Ball Recovery", 12, 1),
        event("Shot", 24, 2),
        event("Pass", 40, 3, **{"pass":{"shot_assist":True}}),
        event("Pass", 42, 3, **{"pass":{"shot_assist":False}}),
        event("Shot", 102, 3, period=3),
    ]
    moments = select_moments(events)
    assert [x["Action"] for x in moments] == [
        "Récupération", "Tir", "Passe menant à un tir", "Tir",
    ]
    shots = select_moments(events, category="Tirs")
    assert [x["Minute du match"] for x in shots] == ["24:02", "75:04"]
    assert select_moments(events, category="Tirs", team="Morocco")[0]["Équipe"] == "Maroc"
    assert len(select_moments(events, category="Tirs", team="Portugal")) == 1


def test_match_video_filters_reject_unverified_or_fabricated_inputs():
    with pytest.raises(ValueError):
        select_moments([], team="France")
    with pytest.raises(ValueError):
        select_moments([], category="Ballon détecté automatiquement")
    with pytest.raises(ValueError):
        select_moments([], start=90, end=20)


def test_no_false_clip_timestamp_or_extra_time_as_regular_play():
    moments = select_moments([
        event("Shot", 25, 24), event("Shot", 25, 24, period=3),
        event("Shot", 26, 1, period=4), event("Shot", 26, 7, period=2),
    ])
    assert len(moments) == 2
    assert all("Minute du match" in r for r in moments)
    assert all("Vidéo" not in r for r in moments)


def test_replay_link_is_a_provider_url_not_a_video_download():
    from fpi.ui.video import OFFICIAL_FIFA_FULL_MATCH, OFFICIAL_FIFA_CLIPS
    assert "plus.fifa.com" in OFFICIAL_FIFA_FULL_MATCH["url"]
    assert all(c["url"].startswith("https://www.youtube.com/") for c in OFFICIAL_FIFA_CLIPS)
    assert "Ballon détecté automatiquement" not in CATEGORIES
