"""Temporary deterministic, cited fact explorer, not a language model."""
from __future__ import annotations

import streamlit as st

from fpi.ai.context import QUESTIONS, factual_answer
from fpi.ui.formatting import team_label, localized_description


def render_assistant(match: dict | None, events: list[dict] | None) -> None:
    st.header("Assistant IA · fondation factuelle")
    st.info("Assistant factuel : 8 questions guidées, calculs vérifiables depuis StatsBomb. Aucun modèle génératif, clé API ou coût d'IA.")
    if not match or not events:
        st.info("Importer les événements réels pour activer les réponses factuelles.")
        return
    teams = (match["home_team"]["home_team_name"], match["away_team"]["away_team_name"])
    team = st.selectbox("Équipe", teams, format_func=team_label, key="assistant_team")
    question = st.selectbox("Question factuelle", QUESTIONS, key="assistant_question")
    if st.button("Obtenir la réponse calculée", key="answer_button", type="primary"):
        st.write(localized_description(factual_answer(events, teams, team, question)))
        st.caption("Source : StatsBomb Open Data, événements du match de référence. Règles et définitions dans les modules fpi.metrics et fpi.analysis.")
