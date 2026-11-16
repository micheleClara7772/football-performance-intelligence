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
from fpi.ui.video import render_video
from fpi.ui.formatting import team_label, localized_team_frame

PAGES = ("Tableau de bord", "Analyse tactique", "Vidéo", "Assistant IA", "Séances")


def _banner() -> None:
    st.set_page_config(page_title="FPI · Football Performance Intelligence", page_icon="⚽", layout="wide")
    st.title("Football Performance Intelligence")
    st.caption("Prototype d'analyse collective · Maroc – Portugal · 10 décembre 2022")
    st.info("MVP en développement. Seuls les indicateurs calculés sur des événements validés peuvent être affichés.")


def _source_panel(metadata: dict | None) -> None:
    st.sidebar.divider()
    st.sidebar.caption("Source des données : [StatsBomb Open Data](https://github.com/hudl/open-data)")
    st.sidebar.caption("Attribution StatsBomb obligatoire pour toute publication/partage ; droits de démonstration commerciale à confirmer.")
    if metadata:
        st.sidebar.success(f"Événements contrôlés : {metadata['validated_events']:,}")
        st.sidebar.caption(f"Chargement : {metadata['retrieved_utc']}")


def _import_panel() -> None:
    st.sidebar.subheader("Données du match")
    st.sidebar.caption("L'import utilise une requête externe seulement après clic ; aucun téléchargement automatique.")
    if st.sidebar.button("Importer depuis StatsBomb", type="primary", width="stretch"):
        with st.sidebar.status("Téléchargement et validation…", expanded=False) as status:
            try:
                match, events, _ = download_reference_match()
                status.update(label=f"{len(events)} événements enregistrés", state="complete")
                st.sidebar.success(f"Import vérifié : {team_label(match['home_team']['home_team_name'])} – {team_label(match['away_team']['away_team_name'])}")
            except (DataValidationError, DownloadError, OSError) as exc:
                status.update(label="Import impossible", state="error")
                st.sidebar.error(str(exc))


def _dashboard(match: dict | None, events: list[dict] | None) -> None:
    st.header("Tableau de bord collectif")
    if not events or not match:
        st.warning("Aucune donnée vérifiée en cache. Utilise « Importer depuis StatsBomb » dans la barre latérale.")
        st.caption("Aucun nombre de tirs, de passes ou graphique n'est simulé.")
        return
    home, away = (match[side][f"{side}_name"] for side in ("home_team", "away_team"))
    metrics = metrics_by_period(events, (home, away))
    st.subheader(f"{team_label(home)} {match['home_score']} – {match['away_score']} {team_label(away)}")
    st.caption("Source : catalogue et événements StatsBomb Open Data (mi-temps réglementaires uniquement)")
    left, middle, right = st.columns(3)
    left.metric("Événements validés", f"{len(events):,}")
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


def _placeholder(title: str, description: str) -> None:
    st.header(title)
    st.warning("Module non implémenté — décision ou développement nécessaire.")
    st.write(description)


def main() -> None:
    _banner()
    page = st.sidebar.radio("Navigation", PAGES, index=0)
    _import_panel()
    try:
        match, events, metadata = load_reference_match()
    except DataUnavailableError:
        match = events = metadata = None
    except DataValidationError as exc:
        st.error(f"Cache invalide : {exc}. Réimporte les données vérifiées pour le réparer.")
        match = events = metadata = None
    _source_panel(metadata)
    if page == "Tableau de bord":
        _dashboard(match, events)
    elif page == "Analyse tactique":
        render_tactical(match, events)
    elif page == "Vidéo":
        render_video()
    elif page == "Assistant IA":
        render_assistant(match, events)
    else:
        render_training(match, events)
