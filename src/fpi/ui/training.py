"""Coach-editable and exportable training draft UI."""
from __future__ import annotations

import json
from dataclasses import asdict

import pandas as pd
import streamlit as st

from fpi.training.generator import FOCUSES, generate_session
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
    draft = st.session_state.get("fpi_training_draft")
    if draft is None:
        st.info("Sélectionne les paramètres, puis génère une proposition.")
        return
    st.subheader(f"{team_label(draft.team)} · {draft.focus} · {draft.duration_minutes} minutes")
    st.info(localized_description(draft.observation))
    st.warning(draft.disclaimer)
    st.caption("Modifie les consignes, durées ou points de vigilance dans le tableau ci-dessous.")
    proposed = pd.DataFrame(draft.exercises)
    edited = st.data_editor(proposed, width="stretch", hide_index=True, num_rows="dynamic", key="training_editor")
    total = pd.to_numeric(edited["Durée (min)"], errors="coerce").sum() if "Durée (min)" in edited else 0
    if total != draft.duration_minutes:
        st.warning(f"Durée actuelle des exercices : {total:g} min, différente de l'objectif initial {draft.duration_minutes} min.")
    output = asdict(draft)
    output["exercises"] = edited.to_dict(orient="records")
    output["approval"] = "À valider par l'entraîneur"
    st.download_button("Exporter la proposition en JSON", json.dumps(output, ensure_ascii=False, indent=2),
                       file_name="fpi-proposition-seance.json", mime="application/json")
