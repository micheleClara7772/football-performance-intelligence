"""Métriques déterministes à partir des événements StatsBomb, sans causalité tactique."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable
import pandas as pd


def _type(event: dict) -> str:
    return event.get("type", {}).get("name", "")


def _team(event: dict) -> str:
    return event.get("team", {}).get("name", "")


def metrics_by_period(events: Iterable[dict], teams: tuple[str, str]) -> pd.DataFrame:
    """Regulation halves 1/2; pass succeeds when pass.outcome is absent."""
    counts = defaultdict(lambda: {"events": 0, "shots": 0, "passes": 0,
                                  "passes_completed": 0, "xg": 0.0, "xg_shots": 0})
    for event in events:
        period = event.get("period")
        team = _team(event)
        if period not in (1, 2) or team not in teams:
            continue
        row = counts[(team, period)]
        row["events"] += 1
        if _type(event) == "Shot":
            row["shots"] += 1
            xg = event.get("shot", {}).get("statsbomb_xg")
            if isinstance(xg, (float, int)) and not isinstance(xg, bool) and xg >= 0:
                row["xg"] += float(xg)
                row["xg_shots"] += 1
        if _type(event) == "Pass":
            row["passes"] += 1
            if not event.get("pass", {}).get("outcome"):
                row["passes_completed"] += 1
    data = []
    for team in teams:
        for period in (1, 2):
            row = counts[(team, period)]
            data.append({
                "team": team, "period": period, "events": row["events"],
                "shots": row["shots"], "passes": row["passes"],
                "passes_completed": row["passes_completed"],
                "pass_completion_pct": round(row["passes_completed"] / row["passes"] * 100, 1)
                if row["passes"] else None,
                "xg": round(row["xg"], 3) if row["xg_shots"] == row["shots"] and row["shots"] > 0 else None,
            })
    return pd.DataFrame.from_records(data)


def shot_locations(events: Iterable[dict], team: str, period: int | None = None) -> pd.DataFrame:
    """Emplacements des tirs dans le repère événementiel StatsBomb 120×80."""
    rows = []
    for event in events:
        if _team(event) != team or _type(event) != "Shot":
            continue
        if period is not None and event.get("period") != period:
            continue
        xy = event.get("location")
        if not (isinstance(xy, (list, tuple)) and len(xy) >= 2):
            continue
        x, y = xy[0], xy[1]
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (x, y)) and 0 <= x <= 120 and 0 <= y <= 80:
            rows.append({"x": x, "y": y, "period": event.get("period"),
                         "minute": event.get("minute"), "player": event.get("player", {}).get("name", "Inconnu")})
    return pd.DataFrame.from_records(rows, columns=["x", "y", "period", "minute", "player"])
