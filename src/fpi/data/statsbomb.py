"""Import StatsBomb Open Data, uniquement après une action explicite."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import requests

from fpi.config import (
    MATCHES_PATH, RAW_BASE_URL, REFERENCE_DATE, REFERENCE_MATCH_ID,
    REFERENCE_TEAMS, data_directory,
)


class DataUnavailableError(RuntimeError):
    """Absence de données de cache vérifiées."""


class DataValidationError(ValueError):
    """Données malformées ou identité du match invalide."""


class DownloadError(RuntimeError):
    """Téléchargement distant impossible."""


def _team_name(match: dict, side: str) -> str:
    team = match.get(side)
    if not isinstance(team, dict):
        raise DataValidationError(f"Données manquantes pour {side}")
    name = team.get(f"{side}_name")
    if not isinstance(name, str) or not name:
        raise DataValidationError(f"Nom d'équipe absent pour {side}")
    return name


def select_reference_match(matches: Any) -> dict:
    """Cherche date + équipes, puis vérifie l'ID, le domicile et le score."""
    if not isinstance(matches, list):
        raise DataValidationError("Le catalogue des matchs n'est pas une liste JSON")
    found = []
    for match in matches:
        if not isinstance(match, dict) or match.get("match_date") != REFERENCE_DATE:
            continue
        home = _team_name(match, "home_team")
        away = _team_name(match, "away_team")
        if {home, away} == REFERENCE_TEAMS:
            found.append(match)
    if len(found) != 1:
        raise DataValidationError(f"Match Maroc–Portugal introuvable ou ambigu ({len(found)})")
    match = found[0]
    if match.get("match_id") != REFERENCE_MATCH_ID:
        raise DataValidationError("L'identifiant du match ne correspond pas au catalogue attendu")
    if (_team_name(match, "home_team"), _team_name(match, "away_team")) != ("Morocco", "Portugal"):
        raise DataValidationError("Ordre domicile/extérieur inattendu ; revue requise")
    if (match.get("home_score"), match.get("away_score")) != (1, 0):
        raise DataValidationError("Score de référence incohérent ; revue requise")
    return match


def validate_events(events: Any, match: dict) -> list[dict]:
    """Vérification structurelle, sans présumer de l'exhaustivité du flux."""
    if not isinstance(events, list) or not events:
        raise DataValidationError("Liste d'événements vide ou invalide")
    allowed_teams = {_team_name(match, "home_team"), _team_name(match, "away_team")}
    ids: set[str] = set()
    periods: set[int] = set()
    for n, event in enumerate(events):
        if not isinstance(event, dict):
            raise DataValidationError(f"Événement {n} non structuré")
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id or event_id in ids:
            raise DataValidationError(f"ID d'événement absent ou dupliqué à la position {n}")
        ids.add(event_id)
        period = event.get("period")
        if not isinstance(period, int) or isinstance(period, bool) or period not in (1, 2, 3, 4, 5):
            raise DataValidationError(f"Période invalide pour l'événement {n}")
        periods.add(period)
        if not isinstance(event.get("type"), dict) or not isinstance(event["type"].get("name"), str):
            raise DataValidationError(f"Type absent pour l'événement {n}")
        team = event.get("team")
        if not isinstance(team, dict) or team.get("name") not in allowed_teams:
            raise DataValidationError(f"Équipe inattendue pour l'événement {n}")
    if not {1, 2}.issubset(periods):
        raise DataValidationError("Le flux doit contenir les deux mi-temps réglementaires")
    return events


def _fetch_json(relative_path: str, getter: Callable[..., Any]) -> Any:
    url = f"{RAW_BASE_URL}/{relative_path}"
    try:
        response = getter(url, timeout=30)
        response.raise_for_status()
        raw = response.content
        if len(raw) > 50_000_000:
            raise DownloadError(f"Taille excessive du fichier {relative_path}")
        return json.loads(raw)
    except (requests.RequestException, ValueError, UnicodeError) as exc:
        raise DownloadError(f"Téléchargement/JSON impossible pour {relative_path}: {exc}") from exc


def _cache_paths(directory: Path) -> dict[str, Path]:
    return {
        "match": directory / "reference_match.json",
        "events": directory / "reference_events.json",
        "provenance": directory / "reference_provenance.json",
    }


def _write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Unique temporary name: two public cloud sessions may import simultaneously.
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_name, path)
    finally:
        Path(temporary_name).unlink(missing_ok=True)


def download_reference_match(
    directory: Path | None = None, *, getter: Callable[..., Any] | None = None
) -> tuple[dict, list[dict], dict]:
    """Télécharge et valide uniquement sur appel explicite. Getter mockable."""
    getter = getter or requests.get
    directory = directory if directory is not None else data_directory()
    catalogue = _fetch_json(MATCHES_PATH, getter)
    match = select_reference_match(catalogue)
    events_path = f"events/{match['match_id']}.json"
    events = validate_events(_fetch_json(events_path, getter), match)
    metadata = {
        "source": "StatsBomb Open Data",
        "provider_repo": "https://github.com/hudl/open-data",
        "match_catalogue_url": f"{RAW_BASE_URL}/{MATCHES_PATH}",
        "events_url": f"{RAW_BASE_URL}/{events_path}",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "match_id": match["match_id"],
        "validated_events": len(events),
        "usage_note": "Attribution requise ; droits de démonstration commerciale à vérifier.",
    }
    paths = _cache_paths(directory)
    _write_json_atomic(paths["match"], match)
    _write_json_atomic(paths["events"], events)
    # La provenance est écrite en dernier ; un lot incomplet est rejeté.
    _write_json_atomic(paths["provenance"], metadata)
    return match, events, metadata


def load_reference_match(directory: Path | None = None) -> tuple[dict, list[dict], dict]:
    """Charge le cache existant, sans requête réseau."""
    directory = directory if directory is not None else data_directory()
    paths = _cache_paths(directory)
    if any(not p.exists() for p in paths.values()):
        raise DataUnavailableError("Aucune donnée locale vérifiée ; import volontaire requis.")
    try:
        match = json.loads(paths["match"].read_text(encoding="utf-8"))
        events = json.loads(paths["events"].read_text(encoding="utf-8"))
        metadata = json.loads(paths["provenance"].read_text(encoding="utf-8"))
        selected = select_reference_match([match])
        validated = validate_events(events, selected)
        if (metadata.get("match_id") != selected["match_id"] or
                metadata.get("validated_events") != len(validated)):
            raise DataValidationError("Traçabilité du cache incohérente")
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise DataValidationError(f"Cache local illisible : {exc}") from exc
    return match, events, metadata
