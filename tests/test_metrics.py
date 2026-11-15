from fpi.metrics.collective import metrics_by_period, shot_locations

def test_shots_and_passes_by_half(events):
    df = metrics_by_period(events, ("Morocco", "Portugal"))
    assert len(df) == 4
    h1 = df[(df.team == "Morocco") & (df.period == 1)].iloc[0]
    assert h1.shots == 1
    assert h1.passes == 1
    assert h1.passes_completed == 1
    assert h1.pass_completion_pct == 100.0
    assert h1.xg == 0.1
    h2 = df[(df.team == "Morocco") & (df.period == 2)].iloc[0]
    assert h2.shots == 0
    assert h2.passes_completed == 0
    assert h2.xg is None or str(h2.xg) == "nan"
    assert df.shots.sum() == 2

def test_ignore_shootout_period(events):
    events.append({"id": "shootout", "team": {"name": "Morocco"}, "period": 5,
                   "type": {"name": "Shot"}, "shot": {"statsbomb_xg": 0.76}})
    df = metrics_by_period(events, ("Morocco", "Portugal"))
    assert df.shots.sum() == 2

def test_missing_xg_does_not_fake_total(events):
    del events[1]["shot"]["statsbomb_xg"]
    df = metrics_by_period(events, ("Morocco", "Portugal"))
    xg = df[(df.team == "Morocco") & (df.period == 1)].iloc[0].xg
    assert xg is None or str(xg) == "nan"

def test_shot_locations_are_filtered(events):
    locations = shot_locations(events, "Morocco", 1)
    assert len(locations) == 1
    assert locations.iloc[0].x == 100
    assert shot_locations(events, "Morocco", 2).empty
