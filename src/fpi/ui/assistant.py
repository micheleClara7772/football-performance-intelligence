"""Assistant français à saisie libre : interprétation locale, aucun LLM externe."""
from __future__ import annotations

import streamlit as st

from fpi.ai.free_text import free_text_answer
from fpi.ui.formatting import team_label, localized_description


def render_assistant(match: dict | None, events: list[dict] | None) -> None:
    st.header("Assistant IA · questions libres")
    st.info(
        "Pose tes questions en français, sans choisir une liste figée. "
        "Les réponses sont calculées gratuitement sur StatsBomb : moteur linguistique local, "
        "non génératif, sans API ni abonnement. Il indique quand une mesure est impossible."
    )
    if not match or not events:
        st.warning("Importer les événements StatsBomb réels pour poser tes questions.")
        return

    teams = (match["home_team"]["home_team_name"], match["away_team"]["away_team_name"])
    team = st.selectbox("Équipe à analyser par défaut", teams, format_func=team_label, key="assistant_team")
    st.caption(
        "Exemples de formulations libres : « Compare les tirs du Maroc et du Portugal », "
        "« Qui sont les joueurs avec le plus de passes ? », « Quel xG du Maroc après 60 minutes ? », "
        "« Quelles récupérations en seconde mi-temps ? »"
    )

    chat_key = f"fpi_free_chat_{match['match_id']}"
    messages = st.session_state.setdefault(chat_key, [])
    for message in messages[-30:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Pose ta question libre sur Maroc–Portugal…", key="fpi_freetext_prompt")
    if prompt:
        messages.append({"role": "user", "content": prompt})
        try:
            answer = free_text_answer(events, teams, team, prompt, match=match)
        except ValueError as exc:
            answer = f"Question non exploitable : {exc}"
        answer = localized_description(answer)
        messages.append({"role": "assistant", "content": answer})
        st.rerun()

    if messages and st.button("Effacer cette conversation", key="assistant_clear"):
        st.session_state[chat_key] = []
        st.rerun()
    st.caption(
        "Source : StatsBomb Open Data, match 3869486. Un résultat factuel provient des événements, "
        "pas d'une observation automatique de la vidéo. L'historique reste en mémoire de cette session."
    )
