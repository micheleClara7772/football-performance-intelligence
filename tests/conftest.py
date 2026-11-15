"""Synthetic fixtures (tests only, never presented as real match data)."""
from __future__ import annotations
import pytest

@pytest.fixture
def match():
    return {
        "match_id": 3869486, "match_date": "2022-12-10",
        "home_team": {"home_team_name": "Morocco"},
        "away_team": {"away_team_name": "Portugal"},
        "home_score": 1, "away_score": 0,
    }

@pytest.fixture
def events():
    return [
        {"id": "a", "team": {"name": "Morocco"}, "period": 1, "minute": 12, "type": {"name": "Pass"}, "pass": {}},
        {"id": "b", "team": {"name": "Morocco"}, "period": 1, "minute": 40, "type": {"name": "Shot"},
         "location": [100, 30], "shot": {"statsbomb_xg": 0.1}, "player": {"name": "Player A"}},
        {"id": "c", "team": {"name": "Portugal"}, "period": 1, "minute": 36, "type": {"name": "Pass"},
         "pass": {"outcome": {"name": "Incomplete"}}},
        {"id": "d", "team": {"name": "Portugal"}, "period": 2, "minute": 70, "type": {"name": "Shot"},
         "location": [110, 40], "shot": {"statsbomb_xg": 0.3}, "player": {"name": "Player B"}},
        {"id": "e", "team": {"name": "Morocco"}, "period": 2, "minute": 89, "type": {"name": "Pass"},
         "pass": {"outcome": {"name": "Out"}}},
    ]
