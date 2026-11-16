"""Transparent event-level tactical indicators, not causal explanations.

StatsBomb locations are provider coordinates in a 120x80 pitch reference.
Counts describe annotated events, not possession, tracking, or true pressure.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

import pandas as pd


_PERIODS = (1, 2)
_VALID_EVENT_TYPES = ("Shot", "Pass", "Pressure", "Ball Recovery", "Interception", "Carry")
_WINDOWS = (
    (1, 0, 15, "1re · 0–14 min"),
    (1, 15, 30, "1re · 15–29 min"),
    (1, 30, None, "1re · 30 min et +"),
    (2, 45, 60, "2e · 45–59 min"),
    (2, 60, 75, "2e · 60–74 min"),
    (2, 75, None, "2e · 75 min et +"),
)


def _event_name(event: dict) -> str:
    value = event.get("type")
    return value.get("name", "") if isinstance(value, dict) else ""


def _team_name(event: dict) -> str:
    value = event.get("team")
    return value.get("name", "") if isinstance(value, dict) else ""


def _xy(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, (tuple, list)) or len(value) < 2:
        return None
    x, y = value[:2]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in (x, y)):
        return None
    if not (0 <= x <= 120 and 0 <= y <= 80):
        return None
    return float(x), float(y)


def _successful_pass(event: dict) -> bool:
    data = event.get("pass")
    return isinstance(data, dict) and not data.get("outcome")


def tactical_by_period(events: Iterable[dict], teams: tuple[str, str]) -> pd.DataFrame:
    """Count annotated tactical proxies for each team and regulation half.

    An entry into the attacking third is a completed Pass or a Carry starting
    before x=80 and ending at x>=80 (provider coordinates). Other kinds of
    possession/progression are not inferred. Recovery/pressure counts represent
    event annotations only, NOT verified tactical systems or pressing success.
    """
    base = defaultdict(lambda: {
        "pressures": 0, "ball_recoveries": 0, "interceptions": 0,
        "passes_from_defensive_third": 0, "passes_from_middle_third": 0,
        "passes_from_attacking_third": 0, "attacking_third_entries": 0,
    })
    for event in events:
        period = event.get("period")
        team = _team_name(event)
        if period not in _PERIODS or team not in teams:
            continue
        row = base[(team, period)]
        kind = _event_name(event)
        if kind == "Pressure":
            row["pressures"] += 1
        if kind == "Ball Recovery":
            row["ball_recoveries"] += 1
        if kind == "Interception":
            row["interceptions"] += 1
        start = _xy(event.get("location"))
        if kind == "Pass" and start is not None:
            if start[0] < 40:
                row["passes_from_defensive_third"] += 1
            elif start[0] < 80:
                row["passes_from_middle_third"] += 1
            else:
                row["passes_from_attacking_third"] += 1
        if kind == "Pass" and not _successful_pass(event):
            continue
        if kind in ("Pass", "Carry") and start is not None:
            details = event.get("pass" if kind == "Pass" else "carry")
            end = _xy(details.get("end_location")) if isinstance(details, dict) else None
            if end is not None and start[0] < 80 <= end[0]:
                row["attacking_third_entries"] += 1
    return pd.DataFrame.from_records([
        {"team": team, "period": period, **base[(team, period)]}
        for team in teams for period in _PERIODS
    ])


def event_locations(events: Iterable[dict], team: str, kind: str, period: int | None = None) -> pd.DataFrame:
    """Plotting positions of a specified annotated event type (not tracking)."""
    if kind not in _VALID_EVENT_TYPES:
        raise ValueError(f"Type d'événement non pris en charge : {kind}")
    rows = []
    for event in events:
        if _team_name(event) != team or _event_name(event) != kind:
            continue
        p = event.get("period")
        if p not in _PERIODS or (period is not None and p != period):
            continue
        xy = _xy(event.get("location"))
        if xy is None:
            continue
        person = event.get("player")
        name = person.get("name", "Non renseigné") if isinstance(person, dict) else "Non renseigné"
        rows.append({"x": xy[0], "y": xy[1], "period": p, "minute": event.get("minute"), "player": name})
    return pd.DataFrame.from_records(rows, columns=["x", "y", "period", "minute", "player"])


def event_timeline(events: Iterable[dict], teams: tuple[str, str]) -> pd.DataFrame:
    """Six deterministic 15-minute windows, last window includes stoppage time.

    Timeline uses regulation halves only. For second-half events, the provider
    reports absolute match minutes and minute 45 belongs to 45–59 window.
    """
    counts = defaultdict(lambda: {"shots": 0, "passes": 0, "pressures": 0, "ball_recoveries": 0})
    for event in events:
        period = event.get("period")
        team = _team_name(event)
        minute = event.get("minute")
        if period not in _PERIODS or team not in teams or not isinstance(minute, int) or isinstance(minute, bool):
            continue
        for idx, (p, start, end, _label) in enumerate(_WINDOWS):
            if p == period and minute >= start and (end is None or minute < end):
                kind = _event_name(event)
                column = {"Shot": "shots", "Pass": "passes", "Pressure": "pressures", "Ball Recovery": "ball_recoveries"}.get(kind)
                if column:
                    counts[(team, idx)][column] += 1
                break
    return pd.DataFrame.from_records([
        {"team": team, "window": label, "period": period, "window_order": i, **counts[(team, i)]}
        for team in teams for i, (period, _start, _end, label) in enumerate(_WINDOWS)
    ])


def describe_period_changes(events: Iterable[dict], teams: tuple[str, str], team: str) -> dict[str, tuple[int, int]]:
    """Return observable 1st/2nd-half counts without interpreting their causes."""
    if team not in teams:
        raise ValueError("Équipe absente du match")
    from fpi.metrics.collective import metrics_by_period

    basic = metrics_by_period(events, teams)
    additional = tactical_by_period(events, teams)
    out: dict[str, tuple[int, int]] = {}
    for source, fields in ((basic, ("shots", "passes", "passes_completed")),
                           (additional, ("pressures", "ball_recoveries", "attacking_third_entries"))):
        rows = source[source.team == team].set_index("period")
        for field in fields:
            out[field] = int(rows.loc[1, field]), int(rows.loc[2, field])
    return out
