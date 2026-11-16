"""Édition et export d'observations tactiques reliées aux événements réels."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from fpi.analysis.annotations import (
    EVENT_TYPES, NOTE_TYPES, MAX_NOTES, build_annotation, eligible_events,
    export_document, format_video_clock, import_document, parse_video_clock,
)
from fpi.ui.formatting import team_label, event_label
from fpi.ui.video import OFFICIAL_FIFA_CLIPS


def _event_title(event: dict) -> str:
    player = event.get("player")
    person = player.get("name", "Non renseigné") if isinstance(player, dict) else "Non renseigné"
    second = event.get("second", 0)
    return f"{event['minute']:02d}:{second:02d} · {person} · {event['id'][:8]}"


def render_annotations(match: dict, events: list[dict], teams: tuple[str, str]) -> None:
    """Annotation facultative, sans téléchargement ni lecture vidéo embarquée."""
    st.subheader("Annotations d'événements vérifiés")
    st.caption(
        "Sélectionne une action enregistrée par StatsBomb, puis ajoute une observation "
        "ou une hypothèse. Les données sources et les notes restent distinctes."
    )
    st.warning(
        "La minute du match et le minutage d'un résumé FIFA sont deux références différentes. "
        "Le minutage du résumé doit être relevé manuellement : aucune synchronisation automatique."
    )
    match_id = match["match_id"]
    state_key = f"fpi_notes_{match_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {}
    notes = st.session_state[state_key]
    c1, c2, c3 = st.columns(3)
    team = c1.selectbox("Équipe de l'action", teams, format_func=team_label, key="annotation_team")
    kind = c2.selectbox("Action", EVENT_TYPES, format_func=event_label, key="annotation_kind")
    period = c3.selectbox("Mi-temps de l'action", (1, 2), format_func=lambda x: f"{x}e mi-temps", key="annotation_period")
    interval = st.slider("Minutes du match à explorer", 0, 130, (0, 130), key="annotation_window")
    filtered = eligible_events(events, team, kind, period, *interval)
    if len(filtered) > 120:
        st.info("Plus de 120 actions trouvées. Réduis l'intervalle des minutes pour une sélection précise.")
        filtered = filtered[:120]
    if not filtered:
        st.info("Aucun événement réel ne correspond à ces filtres.")
    else:
        candidates = {ev["id"]: ev for ev in filtered}
        chosen_id = st.selectbox("Événement StatsBomb", list(candidates), format_func=lambda x: _event_title(candidates[x]), key="annotation_event_id")
        selected = candidates[chosen_id]
        previous = notes.get(chosen_id, {})
        sources = (None, *[clip["url"] for clip in OFFICIAL_FIFA_CLIPS])
        titles = {None: "Aucun extrait associé", **{clip["url"]: clip["label"] for clip in OFFICIAL_FIFA_CLIPS}}
        with st.form(f"annotation_form_{chosen_id}"):
            nature = st.selectbox(
                "Nature de la note", NOTE_TYPES,
                index=NOTE_TYPES.index(previous.get("nature", "Observation")),
                key=f"annotation_nature_{chosen_id}",
            )
            note = st.text_area(
                "Observation tactique ou hypothèse à vérifier",
                value=previous.get("note", ""), max_chars=MAX_TEXT_LENGTH,
                key=f"annotation_text_{chosen_id}",
            )
            source = st.selectbox(
                "Résumé FIFA consulté, facultatif", sources,
                index=sources.index(previous.get("video_url")) if previous.get("video_url") in sources else 0,
                format_func=lambda x: titles[x], key=f"annotation_source_{chosen_id}",
            )
            timestamp = st.text_input(
                "Repère manuel dans le résumé (MM:SS, facultatif)",
                value=format_video_clock(previous.get("video_seconds")),
                help="Minutage du montage YouTube, jamais la minute du match.",
                key=f"annotation_timestamp_{chosen_id}",
            )
            saved = st.form_submit_button("Enregistrer l'annotation")
        if saved:
            try:
                if len(notes) >= MAX_NOTES and chosen_id not in notes:
                    raise ValueError("Limite de 250 annotations atteinte")
                clip_seconds = parse_video_clock(timestamp)
                notes[chosen_id] = build_annotation(
                    selected, note, nature, source, clip_seconds,
                    allowed_video_urls=[clip["url"] for clip in OFFICIAL_FIFA_CLIPS],
                )
                st.success("Annotation enregistrée dans cette session. Exporte le JSON pour la conserver.")
            except ValueError as exc:
                st.error(str(exc))
    st.caption("Les annotations restent dans la session Streamlit. Un export JSON est nécessaire pour les conserver après sa fermeture.")
    if notes:
        records = [
            {"Minute match": f"{note['match_minute']:02d}:{note['match_second']:02d}",
             "Équipe": team_label(note["team"]), "Action": event_label(note["event_type"]),
             "Nature": note["nature"], "Note": note["note"],
             "Résumé (manuel)": format_video_clock(note["video_seconds"])}
            for note in notes.values()
        ]
        st.dataframe(pd.DataFrame(records), hide_index=True, width="stretch")
        st.download_button(
            "Exporter les annotations en JSON",
            export_document(match_id, notes.values()),
            file_name="fpi-annotations-maroc-portugal.json",
            mime="application/json",
            key="annotation_export",
        )
    uploaded = st.file_uploader("Réimporter un fichier JSON d'annotations", type=["json"], key="annotation_upload")
    if uploaded is not None and st.button("Charger les annotations du fichier", key="annotation_load"):
        try:
            raw = uploaded.getvalue()
            if len(raw) > 1_000_000:
                raise ValueError("Fichier d'annotations trop volumineux")
            payload = json.loads(raw.decode("utf-8"))
            imported = import_document(
                payload, match_id, events,
                allowed_video_urls=[clip["url"] for clip in OFFICIAL_FIFA_CLIPS],
            )
            st.session_state[state_key] = imported
            st.success(f"{len(imported)} annotations restaurées depuis le fichier.")
            st.rerun()
        except (ValueError, UnicodeError, TypeError, KeyError, json.JSONDecodeError) as exc:
            st.error(f"Import refusé : {exc}")
