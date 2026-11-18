"""Moteur de questions libres sur événements StatsBomb, sans LLM et sans API payante.

La formulation est libre, mais seules les mesures *explicitement* définies ci-dessous
sont interprétées. Aucun diagnostic tactique ou événement vidéo n'est inféré.
"""
from __future__ import annotations

from collections import Counter
import re
import unicodedata

METRICS = {
    "shots": (r"\btirs?\b", r"\bfrappes?\b", r"\boccasions?\b"),
    "passes": (r"\bpasses?\b", r"\bballons? transmis\b", r"\bcirculation\b"),
    "pressures": (r"\bpressions?\b", r"\bpressing\b"),
    "recoveries": (r"\brecuperations?\b", r"\bballons? recuperes?\b"),
    "interceptions": (r"\binterceptions?\b",),
    "entries": (r"\bdernier tiers\b", r"\bprogressions?\b"),
    "xg": (r"\bxg\b", r"\bexpected goals?\b"),
    "goals": (r"\bbuts?\b", r"\bbuteurs?\b", r"\bmarqu[ea]\b", r"\bscore\b"),
    "carries": (r"\bconduites?\b", r"\bcarries?\b"),
    "dribbles": (r"\bdribbles?\b",),
    "fouls": (r"\bfautes?\b",),
    "offsides": (r"\bhors.jeux?\b", r"\boffside\b"),
    "progressive_passes": (r"\bpasses? progressives?\b",),
    "switches_of_play": (r"\brenversements?\b", r"\bchangements? d.aile\b"),
    "high_recoveries": (r"\brecuperations? hautes?\b",),
    "box_shots": (r"\btirs? (?:dans|depuis) la surface\b",),
    "shot_assists": (r"\bpasses? (?:cles?|decisives? vers un tir)\b",),
    "goal_assists": (r"\bpasses? decisives?\b",),
    "pressures_then_recovery_8s": (r"\brecuperations? apres pressions?\b",),
}
EVENT_TYPES = {
    "shots": "Shot", "passes": "Pass", "pressures": "Pressure",
    "recoveries": "Ball Recovery", "interceptions": "Interception",
    "carries": "Carry", "dribbles": "Dribble", "fouls": "Foul Committed",
    "offsides": "Offside",
}
METRIC_LABELS = {
    "shots": "tirs", "passes": "passes tentées", "pressures": "pressions enregistrées",
    "recoveries": "récupérations enregistrées", "interceptions": "interceptions",
    "entries": "entrées dans le dernier tiers", "xg": "xG StatsBomb",
    "goals": "buts", "carries": "conduites", "dribbles": "dribbles",
    "fouls": "fautes commises", "offsides": "hors-jeu",
    "progressive_passes": "passes progressives", "switches_of_play": "renversements de jeu",
    "high_recoveries": "récupérations hautes", "box_shots": "tirs depuis la surface",
    "shot_assists": "passes précédant un tir", "goal_assists": "passes décisives",
    "pressures_then_recovery_8s": "récupérations après une pression",
}
TEAM_TOKENS = {"Morocco": ("maroc", "morocco", "marocains"),
               "Portugal": ("portugal", "portugais", "portugaise")}


def _normalize(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", value.lower())
                   if not unicodedata.combining(c))


def _get(event: dict, key: str) -> str:
    val = event.get(key)
    return str(val.get("name", "")) if isinstance(val, dict) else ""


def _period(text: str) -> int | None:
    first = bool(re.search(r"\b(1er|1ere|premier|premiere|avant la pause|premiere mi.temps)\b", text))
    second = bool(re.search(r"\b(2eme|2e|deuxieme|seconde|apres la pause|deuxieme mi.temps)\b", text))
    return 1 if first and not second else 2 if second and not first else None


def _time_window(text: str) -> tuple[int | None, int | None]:
    between = re.search(r"\bentre\s+(\d{1,3})\s*(?:et|a|-)\s*(\d{1,3})\b", text)
    if between:
        a, b = map(int, between.groups())
        if 0 <= a <= b <= 130:
            return a, b
        return None, None
    after = re.search(r"\bapres\s+(\d{1,3})\s*(?:e|eme|minutes?|min)?\b", text)
    before = re.search(r"\bavant\s+(\d{1,3})\s*(?:e|eme|minutes?|min)?\b", text)
    if after:
        return min(130, int(after[1]) + 1), 130
    if before:
        return 0, max(0, int(before[1]) - 1)
    return None, None


def _selected_events(events: list[dict], team: str, period: int | None,
                     window: tuple[int | None, int | None]) -> list[dict]:
    first, last = window
    return [
        ev for ev in events
        if ev.get("period") in (1, 2) and _get(ev, "team") == team
        and (period is None or ev["period"] == period)
        and (first is None or (type(ev.get("minute")) is int and first <= ev["minute"]))
        and (last is None or (type(ev.get("minute")) is int and ev["minute"] <= last))
    ]


def _count(selected: list[dict], metric: str) -> tuple[int | float | None, str]:
    if metric in ("progressive_passes", "switches_of_play", "high_recoveries",
                  "box_shots", "shot_assists", "goal_assists", "pressures_then_recovery_8s"):
        from fpi.analysis.advanced import advanced_metrics_by_period, ADVANCED_DESCRIPTIONS
        team = _get(selected[0], "team") if selected else ""
        value = int(advanced_metrics_by_period(selected, (team,))[metric].sum()) if team else 0
        return value, ADVANCED_DESCRIPTIONS[metric]
    if metric == "entries":
        from fpi.analysis.tactical import tactical_by_period
        team = _get(selected[0], "team") if selected else ""
        if not team:
            return 0, ""
        # Filtered event list retains original period and team.
        rows = tactical_by_period(selected, (team,))
        return int(rows["attacking_third_entries"].sum()), "passes réussies ou conduites franchissant x=80"
    if metric == "goals":
        return sum(_get(ev, "type") == "Shot" and _get(ev.get("shot", {}), "outcome") == "Goal"
                   for ev in selected), "buts sur événements Shot/Goal ; buts contre son camp non inférés"
    if metric == "xg":
        shots = [ev for ev in selected if _get(ev, "type") == "Shot"]
        if not shots:
            return None, "aucun tir dans la sélection"
        values = [ev.get("shot", {}).get("statsbomb_xg") for ev in shots]
        if any(type(v) not in (int, float) or not 0 <= v <= 1 for v in values):
            return None, "xG non disponible pour tous les tirs"
        return round(sum(values), 3), "somme des xG StatsBomb fournis, pas buts prédits"
    typ = EVENT_TYPES.get(metric)
    if typ is None:
        return None, "mesure non prise en charge"
    quantity = sum(_get(ev, "type") == typ for ev in selected)
    if metric == "passes":
        completed = sum(_get(ev, "type") == "Pass" and not ev.get("pass", {}).get("outcome") for ev in selected)
        percent = round(completed / quantity * 100, 1) if quantity else None
        return quantity, f"{completed} réussies (réussite {percent if percent is not None else 'non calculable'} %), selon pass.outcome"
    if metric == "pressures":
        return quantity, "événements Pressure, pas une mesure de l'intensité du pressing"
    return quantity, "événements enregistrés par StatsBomb"


def _player_ranking(selected: list[dict], metric: str) -> str:
    typ = EVENT_TYPES.get(metric, "Shot" if metric == "goals" else None)
    if typ is None:
        return "Aucune statistique individuelle fiable pour cette demande."
    counter = Counter()
    for ev in selected:
        if _get(ev, "type") != typ:
            continue
        if metric == "goals" and _get(ev.get("shot", {}), "outcome") != "Goal":
            continue
        player = _get(ev, "player")
        if player:
            counter[player] += 1
    if not counter:
        return "Aucun joueur identifiable dans les événements correspondants."
    return "Joueurs les plus représentés : " + ", ".join(
        f"{name} ({count})" for name, count in sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:5]
    ) + ". Classement par événements enregistrés, pas évaluation de performance."


def free_text_answer(
    events: list[dict], teams: tuple[str, str], selected_team: str, prompt: str, *,
    match: dict | None = None,
) -> str:
    """Répond à des formulations françaises libres, sans appel réseau ni génération.

    Si la demande ne correspond pas à un calcul disponible, reconnaître la limite.
    """
    if selected_team not in teams:
        raise ValueError("Équipe sélectionnée absente du match")
    if not isinstance(prompt, str) or not 2 <= len(prompt.strip()) <= 600:
        raise ValueError("Écris une question de 2 à 600 caractères.")
    text = _normalize(prompt)
    if re.search(r"\b(formation|schema tactique|4.3.3|4.4.2|strategie|pourquoi|cause|video|tracking|vitesse|distance|kilometre|possession)\b", text):
        return (
            "Je ne peux pas déduire une formation, une causalité tactique, la possession réelle, "
            "les vitesses, les distances ou des actions vidéo à partir des seuls événements StatsBomb. "
            "Essaie une question sur les tirs, passes, xG, pressions, récupérations, "
            "joueurs ou entrées dans le dernier tiers."
        )
    metrics = [key for key, patterns in METRICS.items() if any(re.search(p, text) for p in patterns)]
    if "buteur" in text and "goals" not in metrics:
        metrics.append("goals")
    if not metrics:
        if any(word in text for word in ("resume", "bilan", "analyse", "match", "performance")):
            metrics = ["shots", "passes", "pressures", "recoveries"]
        else:
            return (
                "Je peux analyser librement les tirs, passes, xG, pressions, récupérations, "
                "interceptions, buts, conduites et zones de progression, y compris par joueur, "
                "équipe, mi-temps ou intervalle de minutes. Cette question n'a pas de mesure "
                "fiable identifiable dans le flux StatsBomb ; reformule-la."
            )
    explicit = [
        t for t in teams
        if any(re.search(r"\b"+re.escape(token)+r"\b", text) for token in TEAM_TOKENS.get(t, (t.lower(),)))
    ]
    compare = (len(explicit) == 2 or bool(re.search(
        r"\b(compare|comparaison|comparer|deux equipes|plus que|moins que|quelle equipe|entre les equipes)\b", text
    )))
    subject_teams = list(teams) if compare else [explicit[0] if explicit else selected_team]
    period = _period(text)
    window = _time_window(text)
    scope = (
        f"{'1re mi-temps' if period == 1 else '2e mi-temps' if period == 2 else 'mi-temps 1 et 2'}"
        + (f", minutes {window[0]} à {window[1]}" if window[0] is not None else "")
    )
    if match and "score" in text:
        score = f"Score du match : {match['home_score']}–{match['away_score']} (Maroc–Portugal). "
    else:
        score = ""
    result = []
    individual = bool(re.search(r"\b(joueur|joueurs|buteur|buteurs|qui a marque|quel attaquant)\b", text))
    timeline = bool(re.search(r"\b(quand|moments?|chronologie|par quart|par tranche|par minute)\b", text))
    for metric in metrics[:4]:
        lines = []
        for team in subject_teams:
            data = _selected_events(events, team, period, window)
            if individual:
                line = _player_ranking(data, metric)
            elif timeline and metric in EVENT_TYPES and window == (None, None):
                count_by_period = []
                for p in (1, 2):
                    vals, _ = _count([ev for ev in data if ev.get("period") == p], metric)
                    count_by_period.append(int(vals or 0))
                line = f"1re mi-temps {count_by_period[0]}, 2e mi-temps {count_by_period[1]}"
            else:
                value, definition = _count(data, metric)
                line = f"{value if value is not None else 'non disponible'} — {definition}"
            lines.append(f"{team} : {line}")
        result.append(f"{METRIC_LABELS[metric]} ({scope}) : " + " ; ".join(lines))
    return score + "\n\n".join(result) + (
        "\n\nSource : StatsBomb Open Data (événements fournis, périodes 1 et 2). "
        "Ces comptes ne prouvent pas une intention tactique ni un résultat issu d'une analyse vidéo."
    )
