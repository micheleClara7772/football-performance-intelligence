"""Tactical exploration UI with explicit descriptive limitations."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from fpi.analysis.tactical import tactical_by_period, event_locations, event_timeline, describe_period_changes
from fpi.metrics.collective import metrics_by_period

_METRIC_LABELS = {
    "shots": "Tirs",
    "passes": "Passes tentées",
    "passes_completed": "Passes réussies",
    "pressures": "Pressures annotées",
    "ball_recoveries": "Ball Recovery annotées",
    "interceptions": "Interceptions annotées",
    "attacking_third_entries": "Entrées dernier tiers (passes/conduites)",
}


def render_tactical(match: dict | None, events: list[dict] | None) -> None:
    st.header("Analyse tactique · indicateurs observés")
    if not match or not events:
        st.warning("Pour comparer les mi-temps, importer d'abord les événements réels depuis la barre latérale.")
        return

    teams = (match["home_team"]["home_team_name"], match["away_team"]["away_team_name"])
    team = st.selectbox("Équipe analysée", teams, key="tactical_team")
    basic = metrics_by_period(events, teams)
    detail = tactical_by_period(events, teams)
    combined = basic.merge(detail, on=["team", "period"], validate="one_to_one")
    focus = combined[combined.team == team].sort_values("period").reset_index(drop=True)
    st.caption("Données : StatsBomb Open Data, uniquement mi-temps réglementaires. Évolution descriptive, sans conclusion causale.")

    comparison, chronology, spatial = st.tabs(["Comparaison des mi-temps", "Chronologie", "Emplacements des événements"])
    with comparison:
        options = ["shots", "passes", "passes_completed", "pressures", "ball_recoveries", "interceptions", "attacking_third_entries"]
        metric = st.selectbox("Indicateur", options, format_func=lambda v: _METRIC_LABELS[v], key="tactical_metric")
        values = describe_period_changes(events, teams, team)
        h1, h2 = values[metric] if metric in values else (int(focus.loc[0, metric]), int(focus.loc[1, metric]))
        a, b, c = st.columns(3)
        a.metric("1re mi-temps", h1)
        b.metric("2e mi-temps", h2)
        c.metric("Écart (2e - 1re)", f"{h2 - h1:+d}")
        fig = px.bar(
            combined, x="period", y=metric, color="team", barmode="group",
            labels={"team": "Équipe", "period": "Mi-temps", metric: _METRIC_LABELS[metric]},
            title=f"{_METRIC_LABELS[metric]} · comparaison des deux équipes",
        )
        fig.update_xaxes(tickmode="array", tickvals=[1, 2], ticktext=["1re", "2e"])
        st.plotly_chart(fig, use_container_width=True)
        show = focus[["period", "shots", "passes", "passes_completed", "pass_completion_pct", "xg", "pressures", "ball_recoveries", "interceptions", "attacking_third_entries"]]
        st.dataframe(show.rename(columns={"period": "Mi-temps", "shots": "Tirs", "passes": "Passes", "passes_completed": "Passes réussies", "pass_completion_pct": "Réussite (%)", "xg": "xG fournisseur", "pressures": "Pressure", "ball_recoveries": "Ball Recovery", "interceptions": "Interception", "attacking_third_entries": "Entrées dernier tiers"}), hide_index=True, use_container_width=True)
        st.caption("Entrées vers le dernier tiers : passes réussies et conduites passant de x<80 à x≥80 ; ne couvre pas toutes les progressions. xG vide lorsque des tirs n'ont pas de valeur fournisseur.")
    with chronology:
        timeline = event_timeline(events, teams)
        kind = st.selectbox("Événements par séquence", ["shots", "passes", "pressures", "ball_recoveries"],
                            format_func=lambda v: _METRIC_LABELS[v], key="timeline_metric")
        fig = px.bar(timeline, x="window", y=kind, color="team", barmode="group",
                     labels={"window": "Fenêtre de match", "team": "Équipe", kind: _METRIC_LABELS[kind]},
                     title=f"{_METRIC_LABELS[kind]} · fenêtres de 15 min")
        fig.update_xaxes(categoryorder="array", categoryarray=timeline["window"].drop_duplicates().tolist())
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Les dernières fenêtres de chaque mi-temps incluent le temps additionnel. Les événements de prolongation et tirs au but sont exclus.")
    with spatial:
        period = st.radio("Période", [1, 2], horizontal=True, key="tactical_period",
                          format_func=lambda x: "1re mi-temps" if x == 1 else "2e mi-temps")
        kind = st.selectbox("Type de localisation", ["Shot", "Pass", "Pressure", "Ball Recovery", "Interception", "Carry"], key="location_kind")
        positions = event_locations(events, team, kind, period)
        if positions.empty:
            st.info("Aucune localisation exploitable pour cette sélection.")
        else:
            fig = px.scatter(positions, x="x", y="y", hover_data=["player", "minute"],
                             range_x=[0, 120], range_y=[80, 0],
                             labels={"x": "x (0–120)", "y": "y (0–80)"},
                             title=f"{kind} · {team} · mi-temps {period}")
            fig.update_traces(marker={"size": 8, "opacity": 0.5})
            fig.update_layout(yaxis_scaleanchor="x")
            st.plotly_chart(fig, use_container_width=True)
        st.caption("Ces points sont des positions d'événements dans le repère StatsBomb (120×80), pas des trajectoires ni un tracking continu.")
