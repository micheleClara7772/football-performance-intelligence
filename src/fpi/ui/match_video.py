"""Coach-oriented Morocco–Portugal viewing and real event exploration.

Match events are StatsBomb open-data observations, not frames decoded from FIFA.
FIFA+/YouTube footage stays on its official service; no scraping or false sync.
"""
from __future__ import annotations

import streamlit as st

from fpi.ui.video import OFFICIAL_FIFA_FULL_MATCH, OFFICIAL_FIFA_CLIPS

CATEGORIES = (
    "Actions marquantes", "Tirs", "Récupérations", "Interceptions",
    "Passes menant à un tir", "Pressions",
)


def select_moments(events: list[dict], *, team: str = "Toutes",
                   category: str = "Actions marquantes",
                   start: int = 0, end: int = 130) -> list[dict]:
    """Extract observed actions from real StatsBomb events, never speculative video analysis."""
    if team not in ("Toutes", "Morocco", "Portugal") or category not in CATEGORIES:
        raise ValueError("Filtre inconnu")
    if not 0 <= start <= end <= 130:
        raise ValueError("Intervalle invalide")
    selected = []
    mapping = {
        "Shot": "Tir", "Ball Recovery": "Récupération",
        "Interception": "Interception", "Pressure": "Pression",
    }
    groups = {
        "Tirs": {"Tir"}, "Récupérations": {"Récupération"},
        "Interceptions": {"Interception"},
        "Passes menant à un tir": {"Passe décisive", "Passe menant à un tir"},
        "Pressions": {"Pression"},
    }
    for e in events:
        if e.get("period") not in (1, 2):
            continue
        team_field = e.get("team")
        observed_team = team_field.get("name", "") if isinstance(team_field, dict) else ""
        if observed_team not in ("Morocco", "Portugal") or (team != "Toutes" and observed_team != team):
            continue
        m, sec = e.get("minute"), e.get("second")
        if type(m) is not int or type(sec) is not int or not 0 <= sec < 60 or not start <= m <= end:
            continue
        kind = e.get("type")
        name = kind.get("name", "") if isinstance(kind, dict) else ""
        label = mapping.get(name)
        if name == "Pass" and isinstance(e.get("pass"), dict):
            details = e["pass"]
            if details.get("goal_assist") is True:
                label = "Passe décisive"
            elif details.get("shot_assist") is True:
                label = "Passe menant à un tir"
        if label is None or (category != "Actions marquantes" and label not in groups[category]):
            continue
        player = e.get("player")
        player = player.get("name", "Non renseigné") if isinstance(player, dict) else "Non renseigné"
        selected.append((
            (e["period"], m, sec),
            {"Minute du match": f"{m:02d}:{sec:02d}",
             "Équipe": "Maroc" if observed_team == "Morocco" else "Portugal",
             "Action": label, "Joueur": str(player)},
        ))
    return [row for _, row in sorted(selected, key=lambda item: item[0])]


def _navigate_to(page: str) -> None:
    """Streamlit widget navigation MUST use callback, never post-radio key mutation."""
    st.session_state["fpi_navigation"] = page


def _load_real_events() -> None:
    from fpi.data.statsbomb import download_reference_match
    try:
        with st.spinner("Récupération des actions du match…"):
            download_reference_match()
        st.rerun()
    except (OSError, ValueError, RuntimeError) as exc:
        st.error(f"Le chargement a échoué : {exc}")


def render_match_video(match: dict | None, events: list[dict] | None) -> None:
    st.header("Revoir les actions · Maroc – Portugal")
    st.caption("Quart de finale de la Coupe du monde · 10 décembre 2022 · victoire du Maroc 1 – 0")
    st.write(
        "Regarde les images officielles et retrouve les actions du match : "
        "tirs, récupérations, interceptions et passes menant à un tir."
    )
    st.info(
        "Les actions sont issues des observations du match. "
        "La vidéo est hébergée par son diffuseur officiel. "
        "Les deux ne sont pas encore synchronisées automatiquement."
    )
    watch, explore = st.tabs(["Regarder la rencontre", "Explorer les actions"])

    with watch:
        st.subheader("Match intégral")
        st.link_button(
            "Ouvrir Maroc–Portugal en intégralité sur FIFA+",
            OFFICIAL_FIFA_FULL_MATCH["url"], type="primary", width="stretch",
        )
        st.caption(
            "Le match complet s'ouvre sur FIFA+. Sa lecture dépend du pays et "
            "éventuellement d'un compte. FPI ne télécharge pas et ne réhéberge pas cette vidéo."
        )
        st.subheader("Résumé vidéo")
        selected = st.selectbox(
            "Choisir un résumé officiel",
            list(range(len(OFFICIAL_FIFA_CLIPS))),
            format_func=lambda i: OFFICIAL_FIFA_CLIPS[i]["label"],
            key="official_video_selection",
        )
        clip = OFFICIAL_FIFA_CLIPS[selected]
        st.link_button(
            "Regarder ce résumé sur YouTube (solution fiable)", clip["url"],
            width="stretch",
        )
        if st.toggle(
            "Essayer le lecteur YouTube intégré (résumés uniquement)",
            value=False, key="official_youtube_embed_attempt",
        ):
            st.caption(
                "En cas d'erreur 153 ou de refus d'intégration, utilise le lien "
                "vers le site officiel ci-dessus."
            )
            st.iframe(f"https://www.youtube.com/embed/{clip['video_id']}?rel=0",
                      height=420, width="stretch")
        st.caption("Aucun extrait FIFA n'est stocké sur FPI.")

    with explore:
        st.subheader("Retrouver les moments importants")
        if not match or not events:
            st.info("Charge les actions enregistrées du match pour commencer.")
            st.button("Charger les actions Maroc–Portugal", type="primary",
                      key="fpi_match_moments_load", on_click=_load_real_events)
        else:
            first, second = st.columns(2)
            team = first.selectbox(
                "Équipe", ["Toutes", "Morocco", "Portugal"],
                format_func=lambda k: {"Toutes": "Les deux équipes",
                                       "Morocco": "Maroc",
                                       "Portugal": "Portugal"}[k],
                key="fpi_match_video_team",
            )
            category = second.selectbox("Ce que tu cherches", CATEGORIES,
                                        key="fpi_match_video_category")
            start, end = st.slider("Minutes du match", 0, 130, (0, 100),
                                   key="fpi_match_video_minutes")
            rows = select_moments(events, team=team, category=category,
                                  start=start, end=end)
            st.metric("Actions trouvées", len(rows))
            if rows:
                st.dataframe(rows[:60], hide_index=True, use_container_width=True)
                if len(rows) > 60:
                    st.caption("Seules les 60 premières actions s'affichent. Affine la période.")
            else:
                st.info("Aucune action ne correspond à ces critères.")
            st.caption(
                "Les minutes sont celles du **match** et non celles du lecteur de la vidéo. "
                "Retrouve l'action manuellement dans le replay ; FPI n'ouvre pas encore "
                "le film automatiquement au bon instant."
            )
            st.button("Comprendre les différences entre les équipes",
                      on_click=_navigate_to, args=("Analyse tactique",),
                      use_container_width=True, key="fpi_match_moments_to_tactics")
    st.divider()
    st.subheader("Analyse automatique des images : où en est FPI ?")
    st.write(
        "FPI sait déjà étudier les **actions enregistrées** de Maroc–Portugal. "
        "Pour détecter les joueurs et le ballon directement dans **la vidéo** de "
        "cette rencontre, il faut un fichier vidéo autorisé pour le traitement "
        "informatique. Le simple lien YouTube ou FIFA+ ne suffit pas."
    )
    st.caption(
        "Aucun fichier à téléverser pour utiliser cette page. "
        "Un outil expérimental d'analyse d'autres vidéos autorisées est séparé "
        "dans « Démo technique »."
    )
