"""Libellés français utilisés dans l'interface, sans modifier les événements StatsBomb."""
from __future__ import annotations

_TEAM_LABELS = {"Morocco": "Maroc", "Portugal": "Portugal"}
_EVENT_LABELS = {
    "Shot": "Tir", "Pass": "Passe", "Pressure": "Pression",
    "Ball Recovery": "Récupération de balle", "Interception": "Interception",
    "Carry": "Conduite",
}


def team_label(team: str) -> str:
    """Le modèle métier conserve les identifiants d'équipe du fournisseur."""
    return _TEAM_LABELS.get(team, team)


def event_label(event_type: str) -> str:
    return _EVENT_LABELS.get(event_type, event_type)


def localized_team_frame(frame):
    """Copie uniquement destinée à l'affichage des graphiques Plotly/Streamlit."""
    return frame.assign(team=frame["team"].map(team_label))


def localized_description(description: str) -> str:
    """Traduction d'un nom d'équipe dans un texte de présentation uniquement."""
    return description.replace("Morocco", "Maroc")
