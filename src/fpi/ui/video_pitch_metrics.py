"""Honest spatial metrics panel for independently calibrated pitch positions.

This panel NEVER converts raw pixel boxes to pitch distances, and NEVER
presents ground-truth metrics as predictions of FPI's vision model.
"""
from __future__ import annotations

import json
from typing import Any

import streamlit as st

from fpi.video_analysis.team_metrics import summarize_team_shape

MAX_JSON_BYTES = 8 * 1024 * 1024


def parse_and_summarize(blob: bytes) -> dict[str, Any]:
    if not blob or len(blob) > MAX_JSON_BYTES:
        raise ValueError("Rapport absent ou supérieur à 8 Mio")
    try:
        record = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("JSON de positions illisible") from exc
    if not isinstance(record, dict):
        raise ValueError("Schéma de positions incorrect")
    if record.get("coordinate_space") != "pitch_meters_center_origin":
        raise ValueError("Positions non calibrées en mètres : calcul refusé")
    return summarize_team_shape(record, min_players=5)


def build_quality_rows(report: dict) -> list[dict]:
    total=report["total_sampled_frames"]
    if not isinstance(total,int) or total<=0:
        raise ValueError("Nombre d'images de référence invalide")
    rows=[]
    for side,label in (("left","Côté gauche (référence)"),
                       ("right","Côté droit (référence)")):
        info=report["teams"][side]
        n=info["qualified_frames"]
        rows.append({
            "Groupe observé":label,
            "Images exploitables":n,
            "Couverture des annotations (%)":round(100*n/total,1),
            "Largeur médiane (m)":info["median_width_m"],
            "Profondeur médiane (m)":info["median_depth_m"],
            "Dispersion moyenne (m)":info["mean_player_spread_m"],
            "Confiance détection FPI":"Non mesurée",
        })
    return rows


def render_calibrated_video_metrics() -> None:
    st.subheader("5. Indicateurs spatiaux — positions de terrain calibrées")
    st.caption(
        "Largeur, profondeur, dispersion et occupation des zones. "
        "Ces calculs nécessitent des coordonnées terrain en mètres et "
        "l'affectation fiable des joueurs aux deux équipes."
    )
    st.warning(
        "Les données SoccerTrack GSR sont des annotations de référence. "
        "Importer ces positions ne prouve PAS que FPI sait les reconstruire "
        "depuis les pixels vidéo. Aucun chiffre de précision des modèles n'est "
        "déduit de ces annotations."
    )
    uploaded=st.file_uploader(
        "Importer des positions calibrées au format JSON (8 Mio max)",
        type=["json"],key="fpi_pitch_reference_upload",
    )
    if uploaded is None:
        st.caption(
            "Exemple de création d'un rapport : "
            "python -m scripts.convert_soccertrack_gsr --gsr FICHIER.json "
            "--out outputs/positions.json ; conserver les vidéos et GSR hors du Cloud."
        )
        return
    if uploaded.size > MAX_JSON_BYTES:
        st.error("Ce rapport dépasse la limite de 8 Mio.")
        return
    try:
        summary=parse_and_summarize(uploaded.getvalue())
        rows=build_quality_rows(summary)
    except (TypeError,ValueError,KeyError) as exc:
        st.error(f"Positions refusées : {exc}")
        return
    left,right=st.columns(2)
    left.metric("Images analysées (annotations)",summary["total_sampled_frames"])
    right.metric("Fiabilité des détections vidéo FPI","Non mesurée")
    st.dataframe(rows,use_container_width=True,hide_index=True)
    st.caption(
        "Couverture = nombre d'images avec au moins 5 joueurs correctement "
        "renseignés / images dans le JSON. Ce pourcentage n'est PAS une "
        "probabilité de justesse des modèles."
    )
    st.markdown("**Occupation du terrain (grille de référence 3×3)**")
    data=[]
    for team,title in (("left","Côté gauche"),("right","Côté droit")):
        for zone,value in sorted(summary["teams"][team]["occupancy_3x3_counts"].items()):
            data.append({"Groupe":title,"Zone":zone,"Observations":value})
    if data:
        st.dataframe(data,use_container_width=True,hide_index=True)
    else:
        st.info("Pas assez de positions complètes pour établir la répartition spatiale.")
    st.download_button(
        "Exporter les indicateurs (JSON, sans média)",
        data=json.dumps(summary,ensure_ascii=False,indent=2),
        file_name="fpi-formes-equipes-reference.json",mime="application/json",
        key="fpi_pitch_export",
    )
    st.caption(
        "Aucune vitesse, distance parcourue, pressing ou possession n'est "
        "calculée sans calibration vérifiée et suivi d'identité indépendant. "
        "Les équipes peuvent changer de côté à la mi-temps."
    )
