"""Annotations textuelles reliées aux événements StatsBomb (sans copie de vidéo).

Le minutage de match provient des événements du fournisseur. Le minutage d'un
replay ou résumé FIFA est saisi manuellement ; aucune synchronisation n'est déduite.
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

EVENT_TYPES = ("Shot", "Pass", "Pressure", "Ball Recovery", "Interception", "Carry")
NOTE_TYPES = ("Observation", "Hypothèse")
MAX_NOTES = 250
MAX_TEXT_LENGTH = 2000


def _name(event: dict, field: str) -> str:
    value = event.get(field)
    return value.get("name", "") if isinstance(value, dict) else ""


def _valid_clock(event: dict) -> bool:
    minute, second = event.get("minute"), event.get("second", 0)
    return (
        isinstance(minute, int) and not isinstance(minute, bool) and 0 <= minute <= 130
        and isinstance(second, int) and not isinstance(second, bool) and 0 <= second <= 59
    )


def eligible_events(
    events: Iterable[dict], team: str, event_type: str, period: int,
    first_minute: int = 0, last_minute: int = 130,
) -> list[dict]:
    """Retourne uniquement des événements réels portant un ID et un minutage."""
    if event_type not in EVENT_TYPES or period not in (1, 2) or first_minute > last_minute:
        raise ValueError("Filtres d'événements incorrects")
    chosen = []
    for event in events:
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id or not _valid_clock(event):
            continue
        if _name(event, "team") != team or _name(event, "type") != event_type:
            continue
        if event.get("period") != period or not first_minute <= event["minute"] <= last_minute:
            continue
        chosen.append(event)
    return sorted(chosen, key=lambda ev: (ev["minute"], ev.get("second", 0), ev["id"]))


def parse_video_clock(text: str) -> int | None:
    """MM:SS du lecteur officiel, indépendant des minutes du match."""
    value = text.strip()
    if not value:
        return None
    parts = value.split(":")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        raise ValueError("Minutage du résumé attendu au format MM:SS")
    minutes, seconds = map(int, parts)
    if not 0 <= minutes <= 999 or not 0 <= seconds < 60:
        raise ValueError("Minutage du résumé incorrect")
    return minutes * 60 + seconds


def format_video_clock(seconds: int | None) -> str:
    if seconds is None:
        return ""
    if isinstance(seconds, bool) or not isinstance(seconds, int) or not 0 <= seconds < 60000:
        raise ValueError("Minutage vidéo incorrect")
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def build_annotation(
    event: dict, note: str, nature: str, video_url: str | None = None,
    video_seconds: int | None = None, *, allowed_video_urls: Iterable[str] = (),
) -> dict[str, Any]:
    """Contrôle la note et conserve la provenance d'un événement réel."""
    if not isinstance(event.get("id"), str) or not event["id"] or not _valid_clock(event):
        raise ValueError("Événement sans identifiant ou minutage valide")
    if event.get("period") not in (1, 2):
        raise ValueError("Période non prise en charge")
    if _name(event, "type") not in EVENT_TYPES or not _name(event, "team"):
        raise ValueError("Type ou équipe incorrects")
    if not isinstance(note, str) or not 1 <= len(note.strip()) <= MAX_TEXT_LENGTH:
        raise ValueError("La note doit contenir entre 1 et 2000 caractères")
    if nature not in NOTE_TYPES:
        raise ValueError("Nature de note inconnue")
    if video_url is not None and video_url not in allowed_video_urls:
        raise ValueError("Source vidéo non référencée")
    if video_seconds is not None:
        format_video_clock(video_seconds)
        if video_url is None:
            raise ValueError("Un minutage vidéo nécessite une source")
    return {
        "event_id": event["id"],
        "team": _name(event, "team"),
        "event_type": _name(event, "type"),
        "period": event["period"],
        "match_minute": event["minute"],
        "match_second": event.get("second", 0),
        "nature": nature,
        "note": note.strip(),
        "video_url": video_url,
        "video_seconds": video_seconds,
    }


def export_document(match_id: int, annotations: Iterable[dict]) -> str:
    """Exporte uniquement les notes et des références, jamais les JSON StatsBomb."""
    data = sorted(annotations, key=lambda item: (item["period"], item["match_minute"], item["match_second"], item["event_id"]))
    if len(data) > MAX_NOTES:
        raise ValueError("Trop d'annotations")
    return json.dumps({
        "schema_version": 2,
        "match_id": match_id,
        "event_source": "StatsBomb Open Data",
        "video_sync": "manual_player_clock_only",
        "annotations": data,
    }, ensure_ascii=False, indent=2)


def import_document(
    payload: Any, match_id: int, events: Iterable[dict], *,
    allowed_video_urls: Iterable[str] = (),
) -> dict[str, dict]:
    """Réimporte des notes en validant chaque ID contre le match chargé."""
    if not isinstance(payload, dict) or payload.get("schema_version") not in (1, 2) or payload.get("match_id") != match_id:
        raise ValueError("Fichier d'annotations incompatible avec ce match")
    if payload.get("event_source") != "StatsBomb Open Data":
        raise ValueError("Provenance StatsBomb absente ou invalide")
    expected_clock = "manual_summary_clock_only" if payload["schema_version"] == 1 else "manual_player_clock_only"
    if payload.get("video_sync") != expected_clock:
        raise ValueError("Mode de minutage vidéo non reconnu")
    entries = payload.get("annotations")
    if not isinstance(entries, list) or len(entries) > MAX_NOTES:
        raise ValueError("Liste d'annotations absente ou trop volumineuse")
    event_index = {ev["id"]: ev for ev in events if isinstance(ev.get("id"), str)}
    output = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Format d'annotation incorrect")
        event = event_index.get(entry.get("event_id"))
        if event is None or entry["event_id"] in output:
            raise ValueError("ID d'événement inconnu ou en double")
        valid = build_annotation(
            event, entry.get("note"), entry.get("nature"),
            video_url=entry.get("video_url"),
            video_seconds=entry.get("video_seconds"),
            allowed_video_urls=allowed_video_urls,
        )
        if any(entry.get(key) != valid[key] for key in ("team", "event_type", "period", "match_minute", "match_second")):
            raise ValueError("Métadonnées incompatibles avec l'événement source")
        output[valid["event_id"]] = valid
    return output
