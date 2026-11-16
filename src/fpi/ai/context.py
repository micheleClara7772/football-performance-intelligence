"""Deterministic answers for a temporary, explicitly non-LLM fact explorer."""
from __future__ import annotations

from fpi.analysis.tactical import describe_period_changes
from fpi.metrics.collective import metrics_by_period

QUESTIONS = (
    "Comment les tirs évoluent-ils entre les mi-temps ?",
    "Combien de passes ont été tentées et réussies ?",
    "Quels événements de récupération et de pression sont enregistrés ?",
    "Que mesurent ces indicateurs et quelles sont leurs limites ?",
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
    return ("Les mesures proviennent des événements StatsBomb Open Data pour les périodes 1 et 2. "
            "Elles décrivent les occurrences enregistrées et non les intentions de l'entraîneur, "
            "l'efficacité globale du plan tactique ni le tracking continu. "
            "Le mode actuel est déterministe : aucun modèle IA externe n'est appelé.")
