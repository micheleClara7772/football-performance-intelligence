"""Accès aux vidéos officielles du match ; aucun média téléchargé ou hébergé.

Les conditions FIFA+ interdisent de placer sa plateforme dans un cadre tiers :
le replay complet est donc accessible par lien externe seulement. L'intégration
facultative des résumés s'appuie exclusivement sur le lecteur officiel YouTube.
"""
from __future__ import annotations

import streamlit as st

OFFICIAL_FIFA_FULL_MATCH = {
    "label": "Match complet Maroc–Portugal (FIFA+)",
    "url": "https://www.plus.fifa.com/it/content/marocco-portogallo-quarti-di-finale-coppa-del-mondo-fifa-qatar-2022-match-completo/5f1b5797-25d0-4e10-b723-5072b470bae8",
    "provider": "FIFA+ · rediffusion intégrale officielle (disponibilité selon territoire)",
}
OFFICIAL_FIFA_CLIPS = (
    {
        "label": "Résumé prolongé FIFA (2026)",
        "url": "https://www.youtube.com/watch?v=5GVitElttLY",
        "video_id": "5GVitElttLY",
        "provider": "FIFA · chaîne YouTube officielle",
    },
    {
        "label": "Résumé original FIFA (2022)",
        "url": "https://www.youtube.com/watch?v=M766FGsv5do",
        "video_id": "M766FGsv5do",
        "provider": "FIFA · chaîne YouTube officielle",
    },
)


def render_video() -> None:
    st.header("Vidéos officielles · Maroc – Portugal")
    st.caption("Coupe du monde 2022 · Quart de finale du 10 décembre · vraies images, jamais une animation.")

    st.subheader("1. Voir la rencontre intégrale")
    st.link_button(
        "Ouvrir le match complet sur FIFA+",
        OFFICIAL_FIFA_FULL_MATCH["url"],
        type="primary",
        width="stretch",
    )
    st.caption(
        "Replay officiel identifié sur FIFA+. La lecture, la gratuité et la disponibilité "
        "peuvent varier selon le territoire ou nécessiter une connexion à la plateforme."
    )
    st.info(
        "FIFA+ ne permet pas d'intégrer sa plateforme dans une iframe tierce selon ses "
        "conditions d'utilisation. Le match complet s'ouvre donc sur son site officiel, "
        "sans téléchargement, copie ni réhébergement dans FPI."
    )

    st.divider()
    st.subheader("2. Consulter un résumé officiel")
    selected = st.selectbox(
        "Résumé à consulter", list(range(len(OFFICIAL_FIFA_CLIPS))),
        format_func=lambda index: OFFICIAL_FIFA_CLIPS[index]["label"],
        key="official_video_selection",
    )
    clip = OFFICIAL_FIFA_CLIPS[selected]
    st.link_button(
        "Regarder ce résumé sur YouTube (solution fiable)",
        clip["url"],
        width="stretch",
    )

    if st.toggle(
        "Essayer le lecteur YouTube intégré (résumés uniquement)",
        value=False,
        key="official_youtube_embed_attempt",
    ):
        st.caption(
            "Lecteur officiel YouTube uniquement. La disponibilité réelle n'est pas "
            "garantie : si une erreur 153 ou un refus d'intégration s'affiche, "
            "utilise le lien officiel ci-dessus."
        )
        # Native Streamlit iframe: direct URL and normal HTTP Referer (pas de srcdoc).
        # Never iframe FIFA+ itself, prohibited by the provider's platform terms.
        st.iframe(f"https://www.youtube.com/embed/{clip['video_id']}?rel=0", height=420, width="stretch")
    st.caption("Aucun résumé n'est stocké ou rediffusé par FPI.")

    st.divider()
    st.subheader("3. Relier les observations aux événements")
    st.write(
        "L'onglet **Analyse tactique → Annotations** permet de noter les actions "
        "StatsBomb et d'ajouter, si besoin, un repère manuel dans un résumé officiel."
    )
    st.warning(
        "La minute de match StatsBomb n'est pas automatiquement égale au minutage "
        "d'un replay ou d'un montage. Les droits commerciaux StatsBomb/FIFA, "
        "l'inclusion du lecteur et la synchronisation vidéo complète restent non validés."
    )
    st.link_button(
        "Consulter aussi le résumé sur FIFA.com",
        "https://www.fifa.com/fr/watch/4se3MdPEAeiq5n0e9eT14w",
    )
