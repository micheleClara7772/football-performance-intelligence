"""Aperçu des images officielles FIFA via le lecteur hébergé YouTube.

Aucun téléchargement, cache ou réhébergement de fichiers vidéo.
L'aperçu technique n'autorise ni l'intégration commerciale, ni l'annotation
sur une copie de la vidéo sans accord écrit des ayants droit.
"""
from __future__ import annotations

import streamlit as st

OFFICIAL_FIFA_CLIPS = (
    {
        "label": "Résumé prolongé FIFA (publié en 2026)",
        "url": "https://www.youtube.com/watch?v=5GVitElttLY",
        "provider": "FIFA · chaîne YouTube officielle",
    },
    {
        "label": "Résumé original FIFA (publié en 2022)",
        "url": "https://www.youtube.com/watch?v=M766FGsv5do",
        "provider": "FIFA · chaîne YouTube officielle",
    },
)


def render_video() -> None:
    st.header("Vidéo et annotations")
    st.subheader("Images réelles du match Maroc – Portugal (2022)")
    st.caption("Vidéos authentiques publiées par FIFA ; résumés, pas la rencontre intégrale.")
    st.info(
        "Aperçu technique interne. La FIFA reste titulaire des droits ; "
        "la réutilisation commerciale et l'annotation sur des clips copiés "
        "nécessitent une autorisation appropriée."
    )

    selected = st.selectbox(
        "Choisir un extrait officiel",
        list(range(len(OFFICIAL_FIFA_CLIPS))),
        format_func=lambda index: OFFICIAL_FIFA_CLIPS[index]["label"],
        key="official_video_selection",
    )
    clip = OFFICIAL_FIFA_CLIPS[selected]
    st.caption(f"Source : {clip['provider']}")
    st.link_button("Regarder les vraies images sur la chaîne FIFA (YouTube)", clip["url"], type="primary")
    st.caption(
        "La lecture dans FPI peut être refusée par YouTube. "
        "La consultation sur la page officielle reste l'option à privilégier."
    )
    if st.toggle("Essayer le lecteur intégré (peut être indisponible)", value=False):
        st.video(clip["url"], autoplay=False)
    st.link_button(
        "Voir également le résumé sur FIFA.com",
        "https://www.fifa.com/fr/watch/4se3MdPEAeiq5n0e9eT14w",
    )

    st.warning(
        "Stratégie vidéo ouverte : intégration commerciale, droits d'annotation "
        "et synchronisation des scènes avec les événements StatsBomb non validés."
    )
    st.caption(
        "Les minutes du lecteur YouTube concernent le montage du résumé. "
        "Elles ne correspondent pas aux minutes du match ; aucun alignement "
        "automatique avec StatsBomb n'est prétendu."
    )
    st.caption(
        "Si la lecture intégrée est refusée par YouTube, utilise le lien officiel. "
        "Aucun replay ou extrait n'est stocké dans FPI."
    )
