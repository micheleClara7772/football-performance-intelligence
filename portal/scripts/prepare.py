"""Prepare evidence from StatsBomb Open Data match 3869486, in provider order."""
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TEAMS = {"Morocco": "Maroc", "Portugal": "Portugal"}
TYPES = {"Pass": "Passe", "Carry": "Conduite", "Shot": "Tir", "Dispossessed": "Dépossession", "Miscontrol": "Contrôle manqué", "Ball Recovery": "Récupération", "Interception": "Interception", "Pressure": "Pression", "Ball Receipt*": "Réception"}


def candidates(events):
    rows = []
    for i, event in enumerate(events):
        team = event["team"]["name"]
        period = event["period"]
        if period not in (1, 2) or team not in TEAMS or not event.get("location"):
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
            rows.append(dict(id=event["id"], team=TEAMS[team], p=period, clock=f'{event["minute"]:02}:{event["second"]:02}', player=event.get("player", {}).get("name", "Collectif"), x=x, y=y, end=end, tags=tags, after=following))
    return rows


if __name__ == "__main__":
    events = json.loads(Path(sys.argv[1]).read_text())
    assert len(events) == 3381 and events[0]["id"] == "61a31f01-018d-49a3-ab03-14f13f1c245d"
    assert len({e["id"] for e in events}) == len(events)
    raw = json.dumps(candidates(events), ensure_ascii=False, separators=(",", ":")).encode()
    (ROOT / "lib/evidence.json.gz").write_bytes(gzip.compress(raw, mtime=0))
