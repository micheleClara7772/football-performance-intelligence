"""Signaux football calculables sur un match entier à partir d'événements StatsBomb.

Ces compteurs n'utilisent aucun pixel ni tracking et ne démontrent pas la cause
d'une action. Seules les périodes réglementaires 1 et 2 sont agrégées.
"""
from __future__ import annotations

from collections import defaultdict
from math import isfinite

import pandas as pd


ADVANCED_LABELS = {
    "progressive_passes": "Passes progressives (proxy)",
    "switches_of_play": "Renversements latéraux (proxy)",
    "high_recoveries": "Récupérations en moitié adverse",
    "final_third_recoveries": "Récupérations dans dernier tiers",
    "shot_assists": "Passes associées à un tir (fournisseur)",
    "goal_assists": "Passes décisives (fournisseur)",
    "box_shots": "Tirs depuis la surface (proxy)",
    "pressures_then_recovery_8s": "Récupérations dans 8 s après pression (proximité)",
}
ADVANCED_DESCRIPTIONS = {
    "progressive_passes": "Passes réussies partant de x<80 et avançant d'au moins 15 unités vers le but.",
    "switches_of_play": "Passes réussies dont le décalage latéral absolu est au moins 35 unités.",
    "high_recoveries": "Événements Ball Recovery avec x>=60, moitié adverse du terrain StatsBomb.",
    "final_third_recoveries": "Événements Ball Recovery avec x>=80, dernier tiers dans le repère StatsBomb.",
    "shot_assists": "Passes dont StatsBomb signale explicitement pass.shot_assist.",
    "goal_assists": "Passes dont StatsBomb signale explicitement pass.goal_assist.",
    "box_shots": "Tirs dont le départ se situe dans le rectangle x>=102 et 18<=y<=62.",
    "pressures_then_recovery_8s": "Récupérations dans les 8 secondes suivant un événement Pressure de la même équipe ; proximité temporelle, aucune causalité démontrée.",
}


def _name(event: dict, field: str) -> str:
    val = event.get(field)
    return val.get("name", "") if isinstance(val, dict) else ""


def _coords(value) -> tuple[float,float] | None:
    if not isinstance(value, (list, tuple)) or len(value)<2:
        return None
    x,y=value[:2]
    if type(x) not in (int,float) or type(y) not in (int,float):
        return None
    if not (isfinite(x) and isfinite(y) and 0<=x<=120 and 0<=y<=80):
        return None
    return float(x),float(y)


def _clock(event: dict) -> int | None:
    minute,second=event.get("minute"),event.get("second")
    if type(minute) is not int or type(second) is not int:
        return None
    if not 0<=minute<=130 or not 0<=second<=59:
        return None
    return minute*60+second


def advanced_metrics_by_period(events: list[dict], teams: tuple[str,str]) -> pd.DataFrame:
    """Une ligne par équipe/mi-temps, statistiques descriptives seulement."""
    stats=defaultdict(lambda:{key:0 for key in ADVANCED_LABELS})
    last_pressure={}
    possessions=defaultdict(set)
    shot_possessions=defaultdict(set)
    ordered=sorted(
        enumerate(events),
        key=lambda pair:(pair[1].get("period") if type(pair[1].get("period")) is int else 99,
                         _clock(pair[1]) if _clock(pair[1]) is not None else 999999, pair[0]),
    )
    for _,ev in ordered:
        team=_name(ev,"team")
        period=ev.get("period")
        if team not in teams or period not in (1,2):
            continue
        key=(team,period)
        name=_name(ev,"type")
        start=_coords(ev.get("location"))
        sec=_clock(ev)
        possession=ev.get("possession")
        poss_team=_name(ev,"possession_team")
        if type(possession) is int and possession>=0 and poss_team in teams:
            possessions[(poss_team,period)].add(possession)
        if name=="Shot":
            if start and start[0]>=102 and 18<=start[1]<=62:
                stats[key]["box_shots"]+=1
            if type(possession) is int and possession>=0:
                shot_possessions[key].add(possession)
        if name=="Pressure" and sec is not None:
            last_pressure[key]=sec
        if name=="Ball Recovery":
            if start and start[0]>=60:
                stats[key]["high_recoveries"]+=1
            if start and start[0]>=80:
                stats[key]["final_third_recoveries"]+=1
            if sec is not None and key in last_pressure and 0<=sec-last_pressure[key]<=8:
                stats[key]["pressures_then_recovery_8s"]+=1
        if name=="Pass":
            data=ev.get("pass")
            if not isinstance(data,dict):
                continue
            if data.get("shot_assist") is True:
                stats[key]["shot_assists"]+=1
            if data.get("goal_assist") is True:
                stats[key]["goal_assists"]+=1
            end=_coords(data.get("end_location"))
            if not start or not end or data.get("outcome"):
                continue
            if start[0]<80 and end[0]-start[0]>=15:
                stats[key]["progressive_passes"]+=1
            if abs(end[1]-start[1])>=35:
                stats[key]["switches_of_play"]+=1
    rows=[]
    for team in teams:
        for period in (1,2):
            key=(team,period)
            known_possessions=possessions[key]
            with_shot=len(known_possessions & shot_possessions[key]) if known_possessions else None
            rows.append({
                "team":team, "period":period, **stats[key],
                "possessions_annotated":len(known_possessions) if known_possessions else None,
                "possessions_with_shot":with_shot,
                "possession_shot_pct":round(100*with_shot/len(known_possessions),1) if known_possessions else None,
            })
    return pd.DataFrame(rows)
