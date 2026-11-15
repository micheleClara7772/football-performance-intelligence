"""Validation à la demande du véritable Maroc–Portugal (10/12/2022).

Nécessite un réseau externe. Les JSON téléchargés sont conservés exclusivement
dans FPI_DATA_DIR, hors du dépôt ; ce script ne publie aucune donnée tierce.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from fpi.ai.context import QUESTIONS, factual_answer
from fpi.analysis.tactical import tactical_by_period, event_timeline, event_locations
from fpi.data.statsbomb import download_reference_match, load_reference_match
from fpi.metrics.collective import metrics_by_period
from fpi.training.generator import FOCUSES, generate_session


def main() -> None:
    directory = Path(os.environ["FPI_DATA_DIR"]).resolve()
    match, events, provenance = download_reference_match(directory)
    reloaded_match, reloaded_events, loaded_provenance = load_reference_match(directory)
    assert len(events) == len(reloaded_events) == provenance["validated_events"]
    assert reloaded_match["match_id"] == 3869486
    assert loaded_provenance["events_url"].endswith("/events/3869486.json")
    teams = (match["home_team"]["home_team_name"], match["away_team"]["away_team_name"])
    assert teams == ("Morocco", "Portugal")
    assert (match["home_score"], match["away_score"]) == (1, 0)
    assert len(events) > 1000, "Le flux ne contient pas assez d'événements pour le match complet."

    collective = metrics_by_period(events, teams)
    tactical = tactical_by_period(events, teams)
    timeline = event_timeline(events, teams)
    assert len(collective) == len(tactical) == 4
    assert not timeline.empty
    assert (collective["shots"].sum() > 0) and (collective["passes"].sum() > 0)
    for team in teams:
        assert len(event_locations(events, team, "Shot", 1)) > 0
        answer = factual_answer(events, teams, team, QUESTIONS[0])
        assert isinstance(answer, str) and len(answer) > 10
        session = generate_session(events, teams, team, FOCUSES[0], 60, 18)
        assert len(session.exercises) > 0

    result = {
        "source": provenance["source"],
        "match_id": match["match_id"],
        "date": match["match_date"],
        "home": teams[0],
        "away": teams[1],
        "score": [match["home_score"], match["away_score"]],
        "events": len(events),
        "shots": {team: int(collective.loc[collective.team == team, "shots"].sum()) for team in teams},
        "passes": {team: int(collective.loc[collective.team == team, "passes"].sum()) for team in teams},
        "tactical_rows": len(tactical),
        "timeline_rows": len(timeline),
        "checks": "PASS",
        "commercial_reuse_permission": "NOT CONFIRMED",
        "media_rights": "NOT CONFIRMED",
    }
    print("FPI_REAL_MATCH_VALIDATION=" + json.dumps(result, ensure_ascii=False))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("\n## Maroc–Portugal — test sur les événements réels\n\n")
            handle.write("| Vérification | Résultat |\n|---|---|\n")
            for key, value in result.items():
                handle.write(f"| {key} | {value} |\n")
            handle.write("\nCe test ne confirme **ni** les droits commerciaux **ni** les droits de vidéo.\n")


if __name__ == "__main__":
    main()
