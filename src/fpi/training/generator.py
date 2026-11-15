"""Explainable editable training drafts based on verified descriptive counts.

A plan is a coaching template, not a medical, tactical, or AI prescription.
The coach selects the objective; observations do not imply causation.
"""
from __future__ import annotations

from dataclasses import dataclass

from fpi.analysis.tactical import describe_period_changes

FOCUSES = (
    "Circulation et disponibilité",
    "Progression vers le dernier tiers",
    "Création d'occasions",
    "Transition défensive",
)

_DRILLS = {
    FOCUSES[0]: (
        ("Activation avec ballons", "Rondos en petits groupes, soutien court et orientation du corps", "Disponibilité et qualité du premier contrôle"),
        ("Conservation sous contraintes", "Jeu de position avec appuis neutres et limitation de touches adaptable", "Options de passe et soutien au porteur"),
        ("Jeu dirigé", "Séquence de circulation avec sorties vers deux zones cibles", "Communication et mobilité collective"),
    ),
    FOCUSES[1]: (
        ("Activation orientée", "Passes en mouvement vers une zone de progression", "Placement entre les lignes"),
        ("Jeu de progression", "Jeu réduit avec lignes à franchir et cibles par zone", "Conduite, passe verticale et soutien"),
        ("Opposition dirigée", "Deux équipes progressent vers une zone haute définie", "Choix du moment de progression"),
    ),
    FOCUSES[2]: (
        ("Échauffement technique", "Combinaisons courtes et tirs sans opposition intense", "Qualité du dernier geste"),
        ("Créer et finir", "Petites oppositions avec récupération puis recherche d'un tir", "Prise d'information avant la finition"),
        ("Jeu à thème", "Opposition réduite avec points sur occasions créées", "Diversité des situations de tir"),
    ),
    FOCUSES[3]: (
        ("Déplacements défensifs", "Mobilité, orientation du corps et cadrage sans contact", "Distance et coordination"),
        ("Réaction à la perte", "Jeu réduit avec replacement immédiat à la perte de balle", "Communication et couverture"),
        ("Opposition guidée", "Alternance attaque/défense avec retour dans les zones prévues", "Organisation du bloc et compensation"),
    ),
}


@dataclass(frozen=True)
class TrainingDraft:
    team: str
    focus: str
    duration_minutes: int
    players: int
    observation: str
    exercises: list[dict]
    disclaimer: str = "Proposition de travail à adapter et valider par l'entraîneur ; les statistiques ne démontrent pas la cause des difficultés."


def generate_session(events: list[dict], teams: tuple[str, str], team: str,
                     focus: str, duration_minutes: int = 60, players: int = 18) -> TrainingDraft:
    if team not in teams:
        raise ValueError("Équipe non présente dans le match")
    if focus not in FOCUSES:
        raise ValueError("Objectif non pris en charge")
    if not isinstance(duration_minutes, int) or duration_minutes not in (45, 60, 75):
        raise ValueError("Durée attendue : 45, 60 ou 75 minutes")
    if not isinstance(players, int) or not 6 <= players <= 30:
        raise ValueError("Le nombre de participants doit être compris entre 6 et 30")
    changes = describe_period_changes(events, teams, team)
    shots1, shots2 = changes["shots"]
    passes1, passes2 = changes["passes"]
    entries1, entries2 = changes["attacking_third_entries"]
    observation = (
        f"{team} : {shots1} tirs en 1re mi-temps et {shots2} en 2e ; "
        f"{passes1} puis {passes2} passes tentées ; "
        f"{entries1} puis {entries2} entrées vers le dernier tiers enregistrées "
        "(passes réussies et conduites franchissant x=80). "
        "Ces chiffres sont descriptifs et ne suffisent pas à justifier à eux seuls le thème choisi."
    )
    first = max(10, duration_minutes // 4)
    second = duration_minutes // 2
    times = (first, second, duration_minutes - first - second)
    exercises = [{"Phase": f"{i + 1}. {name}", "Durée (min)": times[i], "Consigne": instruction,
                  "Point de vigilance": attention} for i, (name, instruction, attention) in enumerate(_DRILLS[focus])]
    return TrainingDraft(team, focus, duration_minutes, players, observation, exercises)
