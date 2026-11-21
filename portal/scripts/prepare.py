"""Prepare evidence from StatsBomb Open Data match 3869486, in provider order."""
import math
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TEAMS = {"Morocco": "Maroc", "Portugal": "Portugal", "Argentina":"Argentine", "France":"France"}
TYPES = {"Pass": "Passe", "Carry": "Conduite", "Shot": "Tir", "Dispossessed": "Dépossession", "Miscontrol": "Contrôle manqué", "Ball Recovery": "Récupération", "Interception": "Interception", "Pressure": "Pression", "Ball Receipt*": "Réception"}


def candidates(events, period_ends):
    rows = []
    for i, event in enumerate(events):
        team = event["team"]["name"]
        period = event["period"]
        if period not in period_ends or team not in TEAMS or not event.get("location"):
            continue
        x, y = event["location"][:2]
        kind = event["type"]["name"]
        detail = event.get(kind.lower(), {})
        end = detail.get("end_location", [])[:2]
        tags = []
        following = []
        if kind in ("Pass", "Carry") and end and not detail.get("outcome"):
            if x < 80 and end[0] - x >= 15:
                tags.append("Passe progressive" if kind == "Pass" else "Conduite progressive")
            if x < 80 <= end[0]:
                tags.append("Entrée dans le dernier tiers")
            if kind == "Pass" and abs(end[1] - y) >= 35:
                tags.append("Renversement")
        if kind in ("Miscontrol", "Dispossessed") and event["possession_team"]["name"] == team:
            for nxt in events[i+1:]:
                delta = (nxt["minute"]-event["minute"])*60+nxt["second"]-event["second"]
                if nxt["period"] != period or delta > 8:
                    break
                if delta >= 0 and nxt["type"]["name"] in TYPES:
                    following.append({"id": nxt["id"], "s": delta, "action": TYPES[nxt["type"]["name"]], "team": TEAMS[nxt["team"]["name"]]})
            tags.append("Perte candidate")
        if tags:
            second = event["minute"]*60 + event["second"]
            lower = [0, 0, 45*60, 90*60, 105*60][period]
            upper = period_ends[period]
            start = max(lower, second-8)
            finish = min(upper, second + max(8, math.ceil(event.get("duration", 0))))
            before = []
            for prior in reversed(events[max(0,i-48):i]):
                t = prior["minute"]*60+prior["second"]
                if prior["period"] != period or t < start:
                    break
                if t <= second and prior["type"]["name"] in TYPES:
                    before.append(dict(s=t-second, action=TYPES[prior["type"]["name"]],team=TEAMS[prior["team"]["name"]], id=prior["id"]))
                    if len(before)==3: break
            rows.append(dict(kind=TYPES[kind], start=start, finish=finish, before=before[::-1],id=event["id"], team=TEAMS[team], p=period, clock=f'{event["minute"]:02}:{event["second"]:02}', player=event.get("player", {}).get("name", "Collectif"), x=x, y=y, end=end, tags=tags, after=following))
    return rows


if __name__ == "__main__":
    # Match metadata comes from StatsBomb competition 43, season 106.
    catalog = json.loads(Path(sys.argv[1]).read_text())
    output = []
    for source in sys.argv[2:]:
        path = Path(source)
        match_id = path.stem
        meta = next(m for m in catalog if str(m["match_id"]) == match_id)
        events = sorted(json.loads(path.read_text()), key=lambda e: e["index"])
        assert len({e["id"] for e in events}) == len(events)
        ends = {e["period"]:e["minute"]*60+e["second"] for e in events if e["type"]["name"]=="Half End" and e["period"]<=4}
        teams = [TEAMS[meta[k][k+"_name"]] for k in ("home_team","away_team")]
        penalties = [sum(e["period"]==5 and TEAMS[e["team"]["name"]]==t and e.get("shot",{}).get("outcome",{}).get("name")=="Goal" for e in events) for t in teams]
        output.append(dict(id=match_id,teams=teams,score=[meta["home_score"],meta["away_score"]],date=meta["match_date"],stage={"Quarter-finals":"Quart de finale","Final":"Finale"}[meta["competition_stage"]["name"]],penalties=penalties,ends=ends,count=len(events),items=candidates(events,ends)))
    raw=json.dumps(output,ensure_ascii=False,separators=(",",":")).encode()
    (ROOT/"lib/catalog.json.gz").write_bytes(gzip.compress(raw,mtime=0))
