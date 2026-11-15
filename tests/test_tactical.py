"""Only synthetic fixtures: no StatsBomb file redistributed in tests."""
import pytest

from fpi.analysis.tactical import tactical_by_period, event_locations, event_timeline, describe_period_changes

TEAMS = ("Morocco", "Portugal")


def ev(name, period=1, team="Morocco", minute=12, location=None, **extra):
    event = {"type": {"name": name}, "period": period, "team": {"name": team}, "minute": minute}
    if location is not None:
        event["location"] = location
    event.update(extra)
    return event


def test_tactical_counts_and_final_third_entries():
    events = [
        ev("Pass", location=[70, 40], **{"pass": {"end_location": [85, 44]}}),
        ev("Pass", location=[78, 30], **{"pass": {"end_location": [90, 30], "outcome": {"name": "Incomplete"}}}),
        ev("Carry", location=[60, 44], carry={"end_location": [100, 40]}),
        ev("Pass", location=[20, 10], **{"pass": {"end_location": [30, 10]}}),
        ev("Pass", period=2, location=[100, 50], **{"pass": {"end_location": [108, 50]}}),
        ev("Pressure", period=2), ev("Pressure", period=2), ev("Ball Recovery", period=2),
        ev("Interception", period=2),
        ev("Pressure", period=3),  # Extra time must not affect regulation counts.
    ]
    result = tactical_by_period(events, TEAMS)
    a = result[(result.team == "Morocco") & (result.period == 1)].iloc[0]
    assert a.attacking_third_entries == 2
    assert a.passes_from_defensive_third == 1
    assert a.passes_from_middle_third == 2
    assert a.passes_from_attacking_third == 0
    b = result[(result.team == "Morocco") & (result.period == 2)].iloc[0]
    assert b.pressures == 2
    assert b.ball_recoveries == 1
    assert b.interceptions == 1
    assert b.attacking_third_entries == 0
    assert len(result) == 4


def test_tactical_missing_coordinates_and_invalid_types():
    data = [ev("Pass", location=[True, 2], **{"pass": {"end_location": [100, 30]}}),
            ev("Carry", location=[77, 40], carry={"end_location": [130, 40]})]
    got = tactical_by_period(data, TEAMS)
    assert got.attacking_third_entries.sum() == 0
    assert event_locations(data, "Morocco", "Pass").empty
    with pytest.raises(ValueError):
        event_locations(data, "Morocco", "Goal Kick")


def test_timeline_includes_stoppage_in_last_window():
    rows = [ev("Shot", period=1, minute=45), ev("Shot", period=2, minute=45),
            ev("Shot", period=2, minute=91), ev("Shot", period=3, minute=101),
            ev("Pass", period=2, minute=61)]
    data = event_timeline(rows, TEAMS)
    assert data.shots.sum() == 3
    team = data[data.team == "Morocco"].reset_index(drop=True)
    assert team.loc[2, "shots"] == 1
    assert team.loc[3, "shots"] == 1
    assert team.loc[5, "shots"] == 1
    assert team.loc[4, "passes"] == 1
    assert len(data) == 12


def test_period_changes_from_fixture(events):
    result = describe_period_changes(events, TEAMS, "Morocco")
    assert result["shots"] == (1, 0)
    assert result["passes"] == (1, 1)
    assert result["attacking_third_entries"] == (0, 0)
    with pytest.raises(ValueError):
        describe_period_changes(events, TEAMS, "Belgium")
