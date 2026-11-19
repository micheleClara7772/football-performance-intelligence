"""FPI Streamlit interface: a vertical-slice MVP with honest module states."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from fpi.data.statsbomb import (
    DataUnavailableError,
    DataValidationError,
    DownloadError,
    download_reference_match,
    load_reference_match,
)
from fpi.metrics.collective import metrics_by_period
from fpi.ui.tactical import render_tactical
from fpi.ui.assistant import render_assistant
from fpi.ui.training import render_training
from fpi.ui.match_video import render_match_video as render_video
from fpi.ui.video_showcase import render_video_showcase
from fpi.ui.formatting import team_label, localized_team_frame

PAGES = ("Le match", "Revoir les actions", "Analyse tactique", "Questions", "Séances", "Démo technique")


def _banner() -> None:
    st.set_page_config(page_title="FPI · Football Performance Intelligence", page_icon="⚽", layout="wide")
    st.title("Football Performance Intelligence")
    st.caption("Maroc – Portugal 2022 · observer les actions, comprendre le match, préparer une séance")


def _source_panel(metadata: dict | None) -> None:
    st.sidebar.divider()
    with st.sidebar.expander("D’où viennent les chiffres ?"):
        st.caption("Les actions du match sont fournies par [StatsBomb Open Data](https://github.com/hudl/open-data). Ce ne sont pas des analyses automatiques des images.")
        st.caption("Attribution nécessaire ; droits de réutilisation commerciale à vérifier.")
    if metadata:
        st.sidebar.success(f"Événements contrôlés : {metadata['validated_events']:,}")
        st.sidebar.caption(f"Chargement : {metadata['retrieved_utc']}")


def _import_panel() -> None:
    st.sidebar.subheader("Données du match")
    st.sidebar.caption("Charge une fois les actions pour activer toutes les analyses.")
    if st.sidebar.button("Charger les actions du match", type="primary", width="stretch"):
        with st.sidebar.status("Téléchargement et validation…", expanded=False) as status:
            try:
                match, events, _ = download_reference_match()
                status.update(label=f"{len(events)} événements enregistrés", state="complete")
                st.sidebar.success(f"Import vérifié : {team_label(match['home_team']['home_team_name'])} – {team_label(match['away_team']['away_team_name'])}")
            except (DataValidationError, DownloadError, OSError) as exc:
                status.update(label="Import impossible", state="error")
                st.sidebar.error(str(exc))


def _dashboard(match: dict | None, events: list[dict] | None) -> None:
    st.header("Maroc 1 – 0 Portugal · Coupe du monde 2022")
    if not events or not match:
        st.info("Les actions du match ne sont pas encore chargées.")
        if st.button("Afficher les actions et statistiques du match", type="primary",
                     key="fpi_load_from_home"):
            with st.spinner("Chargement des actions réelles du match…"):
                try:
                    download_reference_match()
                    st.rerun()
                except (DataValidationError, DownloadError, OSError) as exc:
                    st.error(f"Le chargement a échoué : {exc}")
        return
    home, away = (match[side][f"{side}_name"] for side in ("home_team", "away_team"))
    metrics = metrics_by_period(events, (home, away))
    st.subheader(f"{team_label(home)} {match['home_score']} – {match['away_score']} {team_label(away)}")
    st.caption("Source : catalogue et événements StatsBomb Open Data (mi-temps réglementaires uniquement)")
    left, middle, right = st.columns(3)
    left.metric("Événements validés", f"{len(events):,}".replace(",", " "))
    middle.metric(f"Tirs · {team_label(home)}", str(int(metrics.loc[metrics.team == home, "shots"].sum())))
    right.metric(f"Tirs · {team_label(away)}", str(int(metrics.loc[metrics.team == away, "shots"].sum())))
    fig = px.bar(localized_team_frame(metrics), x="period", y="shots", color="team", barmode="group",
                 labels={"period": "Mi-temps", "shots": "Nombre de tirs", "team": "Équipe"},
                 title="Tirs enregistrés par équipe et par période")
    fig.update_xaxes(tickmode="array", tickvals=[1, 2], ticktext=["1re", "2e"])
    st.plotly_chart(fig, width="stretch")
    st.dataframe(localized_team_frame(metrics).rename(columns={"team": "Équipe", "period": "Période", "events": "Événements",
                                         "shots": "Tirs", "passes": "Passes tentées", "passes_completed": "Passes réussies",
                                         "pass_completion_pct": "Passes réussies (%)", "xg": "xG StatsBomb"}),
                 hide_index=True, width="stretch")
    st.caption("Passes réussies : passes sans indication d'échec selon le champ fournisseur pass.outcome. xG affiché uniquement lorsque tous les tirs de la période possèdent une valeur StatsBomb.")


def _go_to_next_page() -> None:
    """Navigation de démo guidée, avant l'exécution des widgets au prochain rerun."""
    current = st.session_state.get("fpi_navigation", PAGES[0])
    index = PAGES.index(current) if current in PAGES else 0
    st.session_state["fpi_navigation"] = PAGES[(index + 1) % len(PAGES)]


def main() -> None:
    _banner()
    if st.session_state.get("fpi_navigation") not in (None, *PAGES):
        st.session_state["fpi_navigation"] = PAGES[0]
    page = st.sidebar.radio("Choisir une rubrique", PAGES, index=0, key="fpi_navigation")
    stage = PAGES.index(page)
    st.sidebar.caption(f"Parcours guidé · étape {stage + 1} / {len(PAGES)}")
    _import_panel()
    try:
        match, events, metadata = load_reference_match()
    except DataUnavailableError:
        match = events = metadata = None
    except DataValidationError as exc:
        st.error(f"Cache invalide : {exc}. Réimporte les données vérifiées pour le réparer.")
        match = events = metadata = None
    _source_panel(metadata)
    if page == "Le match":
        _dashboard(match, events)
    elif page == "Revoir les actions":
        render_video(match, events)
    elif page == "Analyse tactique":
        render_tactical(match, events)
    elif page == "Questions":
        render_assistant(match, events)
    elif page == "Séances":
        render_training(match, events)
    else:
        render_video_showcase(match, events)

    st.divider()
    next_name = PAGES[(stage + 1) % len(PAGES)]
    st.button(
        f"Continuer : {next_name}",
        key="fpi_next_step",
        on_click=_go_to_next_page,
        width="stretch",
    )
    st.caption(
        "Parcours : le match → revoir les actions → comprendre le jeu → "
        "poser une question → préparer une séance. La démo technique reste facultative."

    )
