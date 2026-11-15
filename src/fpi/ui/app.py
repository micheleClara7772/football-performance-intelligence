"""FPI Streamlit UI: five sections and observed-data-only visualisations."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from fpi.data.statsbomb import (
    DataUnavailableError, DataValidationError, DownloadError,
    download_reference_match, load_reference_match,
)
from fpi.metrics.collective import metrics_by_period, shot_locations

PAGES = ("Dashboard", "Analyse tactique", "Vidéo", "Assistant IA", "Séances")


def _banner() -> None:
    st.set_page_config(page_title="FPI · Football Performance Intelligence", page_icon="⚽", layout="wide")
    st.title("Football Performance Intelligence")
    st.caption("Prototype d'analyse collective · Maroc – Portugal · 10 décembre 2022")
    st.info("MVP en développement. Seuls les indicateurs calculés sur des événements validés peuvent être affichés.")


def _source_panel(metadata: dict | None) -> None:
    st.sidebar.divider()
    st.sidebar.caption("Source : [StatsBomb Open Data](https://github.com/hudl/open-data)")
    st.sidebar.caption("Attribution StatsBomb obligatoire pour publication/partage ; droits de démonstration commerciale à confirmer.")
    if metadata:
        st.sidebar.success(f"Événements contrôlés : {metadata['validated_events']:,}")
        st.sidebar.caption(f"Chargement : {metadata['retrieved_utc']}")


def _import_panel() -> None:
    st.sidebar.subheader("Données du match")
    st.sidebar.caption("L'import utilise une requête externe seulement après clic ; aucun téléchargement automatique.")
    if st.sidebar.button("Importer depuis StatsBomb", type="primary", use_container_width=True):
        with st.sidebar.spinner("Téléchargement et validation…"):
            try:
                match, events, _ = download_reference_match()
                st.sidebar.success(f"{len(events)} événements enregistrés : {match['home_team']['home_team_name']} – {match['away_team']['away_team_name']}")
            except (DataValidationError, DownloadError, OSError) as exc:
                st.sidebar.error(f"Import impossible : {exc}")


def _dashboard(match: dict | None, events: list[dict] | None) -> None:
    st.header("Dashboard collectif")
    if not events or not match:
        st.warning("Aucune donnée vérifiée en cache. Utilise « Importer depuis StatsBomb » dans la barre latérale.")
        st.caption("Aucun nombre de tirs, de passes ou graphique n'est simulé.")
        return
    home, away = (match[side][f"{side}_name"] for side in ("home_team", "away_team"))
    metrics = metrics_by_period(events, (home, away))
    st.subheader(f"{home} {match['home_score']} – {match['away_score']} {away}")
    st.caption("Source : catalogue et événements StatsBomb Open Data (mi-temps réglementaires uniquement)")
    left, middle, right = st.columns(3)
    left.metric("Événements validés", f"{len(events):,}")
    middle.metric(f"Tirs · {home}", str(int(metrics.loc[metrics.team == home, "shots"].sum())))
    right.metric(f"Tirs · {away}", str(int(metrics.loc[metrics.team == away, "shots"].sum())))
    fig = px.bar(metrics, x="period", y="shots", color="team", barmode="group",
                 labels={"period": "Mi-temps", "shots": "Nombre de tirs", "team": "Équipe"},
                 title="Tirs enregistrés par équipe et par période")
    fig.update_xaxes(tickmode="array", tickvals=[1, 2], ticktext=["1re", "2e"])
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(metrics.rename(columns={
        "team": "Équipe", "period": "Période", "events": "Événements",
        "shots": "Tirs", "passes": "Passes tentées", "passes_completed": "Passes réussies",
        "pass_completion_pct": "Passes réussies (%)", "xg": "xG StatsBomb",
    }), hide_index=True, use_container_width=True)
    st.caption("Passes réussies : événements Pass sans pass.outcome. xG affiché seulement s'il est présent pour tous les tirs.")


def _tactics(match: dict | None, events: list[dict] | None) -> None:
    st.header("Analyse tactique · observations descriptives")
    if not events or not match:
        st.warning("L'analyse nécessite des données réelles importées et validées.")
        return
    teams = (match["home_team"]["home_team_name"], match["away_team"]["away_team_name"])
    chosen = st.selectbox("Équipe", teams)
    period_choice = st.radio("Période", [1, 2], horizontal=True, format_func=lambda p: "1re mi-temps" if p == 1 else "2e mi-temps")
    metrics = metrics_by_period(events, teams)
    row = metrics[(metrics.team == chosen) & (metrics.period == period_choice)].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Tirs", int(row.shots))
    c2.metric("Passes tentées", int(row.passes))
    c3.metric("Passes réussies", int(row.passes_completed))
    spots = shot_locations(events, chosen, period_choice)
    if spots.empty:
        st.info("Aucun tir localisé pour cette équipe et cette période.")
    else:
        fig = px.scatter(spots, x="x", y="y", hover_data=["player", "minute"],
                         range_x=[0, 120], range_y=[80, 0],
                         labels={"x": "Longueur (0–120)", "y": "Largeur (0–80)"},
                         title="Positions des tirs enregistrés · repère StatsBomb 120 × 80")
        fig.update_traces(marker={"size": 13, "opacity": 0.8})
        fig.update_layout(yaxis_scaleanchor="x")
        st.plotly_chart(fig, use_container_width=True)
    st.caption("Vue descriptive : ni vidéo, ni preuve de causalité. Les données 360 ne sont pas du tracking continu.")


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
        st.error(f"Cache invalide : {exc}. Réimporte les données pour le réparer.")
        match = events = metadata = None
    _source_panel(metadata)
    if page == "Dashboard":
        _dashboard(match, events)
    elif page == "Analyse tactique":
        _tactics(match, events)
    elif page == "Vidéo":
        _placeholder("Vidéo et annotations", "Stratégie vidéo ouverte : intégration, licences, synchronisation et format restent à valider. Aucun replay n'est copié ou diffusé.")
    elif page == "Assistant IA":
        _placeholder("Assistant IA contextualisé", "Le modèle et le fournisseur ne sont pas configurés. Les futures réponses devront utiliser les données calculées et citer leur provenance.")
    else:
        _placeholder("Générateur de séances", "Ce module proposera des exercices modifiables à partir de constats vérifiés ; une validation humaine sera obligatoire avant utilisation.")
