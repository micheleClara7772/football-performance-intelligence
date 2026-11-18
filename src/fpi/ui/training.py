"""Coach-editable and exportable training draft UI."""
from __future__ import annotations

import json
from dataclasses import asdict

import pandas as pd
import streamlit as st

from fpi.training.generator import FOCUSES, generate_session
from fpi.training.validation import validate_exercises
from fpi.ui.formatting import team_label, localized_description


def render_training(match: dict | None, events: list[dict] | None) -> None:
    st.header("Générateur de séances · propositions modifiables")
    st.caption("Le choix du thème et l'approbation finale relèvent du staff technique. Aucun diagnostic automatique n'est établi.")
    if not match or not events:
        st.warning("Importer les événements réels pour disposer d'un contexte chiffré avant de générer une proposition.")
        return
    teams = (match["home_team"]["home_team_name"], match["away_team"]["away_team_name"])
    with st.form("training_form"):
        team = st.selectbox("Équipe", teams, format_func=team_label, key="training_team")
        focus = st.selectbox("Objectif choisi par l'entraîneur", FOCUSES, key="training_focus")
        duration = st.select_slider("Durée totale", options=[45, 60, 75], value=60, key="training_duration")
        players = st.number_input("Nombre de joueurs", min_value=6, max_value=30, value=18, step=1, key="training_players")
        submitted = st.form_submit_button("Proposer une séance", type="primary")
    if submitted:
        st.session_state["fpi_training_draft"] = generate_session(events, teams, team, focus, duration, int(players))
        st.session_state["fpi_training_revision"] = st.session_state.get("fpi_training_revision", 0) + 1
    draft = st.session_state.get("fpi_training_draft")
    if draft is None:
        st.info("Sélectionne les paramètres, puis génère une proposition.")
        return
    st.subheader(f"{team_label(draft.team)} · {draft.focus} · {draft.duration_minutes} minutes")
    st.info(localized_description(draft.observation))
    st.warning(draft.disclaimer)
    st.caption("Modifie les consignes, durées, matériel, variantes ou points de vigilance ci-dessous.")
    proposed = pd.DataFrame(draft.exercises)
    edited = st.data_editor(
        proposed, width="stretch", hide_index=True, num_rows="dynamic",
        key=f"training_editor_{st.session_state.get('fpi_training_revision', 0)}",
    )
    rows = edited.to_dict(orient="records")
    problems = validate_exercises(rows, draft.duration_minutes)
    if problems:
        for problem in problems:
            st.warning(problem)
        st.error("Export bloqué : corrige la durée totale, les champs vides et les valeurs invalides.")
        return
    st.success(f"Séance cohérente : {len(rows)} exercices, {draft.duration_minutes} minutes. Validation du staff toujours nécessaire.")
    output = asdict(draft)
    output["match_id"] = match["match_id"]
    output["source"] = "StatsBomb Open Data · données événementielles vérifiées"
    output["exercises"] = rows
    output["approval"] = "À valider par l'entraîneur"
    st.download_button(
        "Exporter la proposition en JSON",
        json.dumps(output, ensure_ascii=False, indent=2),
        file_name="fpi-proposition-seance.json", mime="application/json",
    )
