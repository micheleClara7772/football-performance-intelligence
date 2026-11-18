"""Deterministic answers for a temporary, explicitly non-LLM fact explorer."""
from __future__ import annotations

from fpi.analysis.tactical import describe_period_changes, tactical_by_period
from fpi.metrics.collective import metrics_by_period

QUESTIONS = (
    "Comment les tirs évoluent-ils entre les mi-temps ?",
    "Combien de passes ont été tentées et réussies ?",
    "Quels événements de récupération et de pression sont enregistrés ?",
    "Que mesurent ces indicateurs et quelles sont leurs limites ?",
    "Comment les entrées vers le dernier tiers évoluent-elles ?",
    "Quels xG StatsBomb sont disponibles par mi-temps ?",
    "Quelle équipe a tenté le plus de tirs et de passes ?",
    "Dans quel tiers du terrain commencent les passes enregistrées ?",
)


def factual_answer(events: list[dict], teams: tuple[str, str], team: str, question: str) -> str:
    if question not in QUESTIONS:
        raise ValueError("Question non prise en charge dans le mode hors ligne")
    if team not in teams:
        raise ValueError("Équipe absente du match")
    values = describe_period_changes(events, teams, team)
    if question == QUESTIONS[0]:
        a, b = values["shots"]
        return (f"{team} a enregistré {a} tirs en première mi-temps et {b} en deuxième "
                f"(écart de {b - a:+d}). Cette variation descriptive ne suffit pas à établir une cause tactique.")
    if question == QUESTIONS[1]:
        a, b = values["passes"]
        c, d = values["passes_completed"]
        return (f"{team} : {a} passes tentées et {c} réussies en première mi-temps, "
                f"contre {b} tentées et {d} réussies en deuxième. "
                "Une passe est considérée réussie quand le champ `pass.outcome` est absent.")
    if question == QUESTIONS[2]:
        p1, p2 = values["pressures"]
        r1, r2 = values["ball_recoveries"]
        return (f"{team} : {p1} puis {p2} événements `Pressure`, "
                f"{r1} puis {r2} événements `Ball Recovery`. Ce sont des annotations de fournisseur, "
                "pas une mesure exhaustive de l'intensité du pressing ni de son efficacité.")
    if question == QUESTIONS[3]:
        return ("Les mesures proviennent des événements StatsBomb Open Data pour les périodes 1 et 2. "
                "Elles décrivent les occurrences enregistrées et non les intentions de l'entraîneur, "
                "l'efficacité globale du plan tactique ni le tracking continu. "
                "Le mode actuel est déterministe : aucun modèle IA externe n'est appelé.")
    if question == QUESTIONS[4]:
        one, two = values["attacking_third_entries"]
        return (f"{team} : {one} passages vers le dernier tiers en première mi-temps, "
                f"{two} en deuxième (écart {two - one:+d}). "
                "Ce décompte inclut les passes réussies et conduites traversant x=80 "
                "dans les coordonnées du fournisseur ; ce n'est pas toutes les progressions.")
    if question == QUESTIONS[5]:
        rows = metrics_by_period(events, teams)
        rows = rows[rows.team == team].set_index("period")
        def label(period: int) -> str:
            value = rows.loc[period, "xg"]
            return "non disponible" if value is None or value != value else f"{value:.3f}"
        return (f"{team} : xG StatsBomb 1re mi-temps : {label(1)}, "
                f"2e mi-temps : {label(2)}. Les xG ne sont affichés que lorsque "
                "tous les tirs de la période possèdent une valeur du fournisseur ; "
                "ils ne garantissent pas la réalisation d'un but.")
    if question == QUESTIONS[6]:
        stats = metrics_by_period(events, teams).groupby("team")[["shots", "passes"]].sum()
        home, away = teams
        def compare(field: str, title: str) -> str:
            a, b = int(stats.loc[home, field]), int(stats.loc[away, field])
            leader = home if a > b else away if b > a else "égalité"
            return f"{title} : {home} {a}, {away} {b} (plus grand total : {leader})"
        return (compare("shots", "Tirs") + ". " + compare("passes", "Passes tentées")
                + ". Totaux d'événements enregistrés en périodes 1 et 2 seulement.")
    rows = tactical_by_period(events, teams)
    selected = rows[rows.team == team]
    defensive = int(selected["passes_from_defensive_third"].sum())
    middle = int(selected["passes_from_middle_third"].sum())
    attacking = int(selected["passes_from_attacking_third"].sum())
    return (f"{team} : passes enregistrées au départ du tiers défensif : {defensive}, "
            f"tiers central : {middle}, tiers offensif : {attacking}. "
            "Le départ est déterminé à partir de x dans le repère StatsBomb 120×80 "
            "(x < 40, 40 ≤ x < 80, x ≥ 80). Ce ne sont pas des statistiques de possession.")
