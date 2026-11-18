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

    st.divider()
    st.subheader("4. Détection automatique dans un fichier vidéo autorisé")
    st.caption(
        "YOLOX-Nano détecte des personnes et des ballons de sport à partir des pixels. "
        "Les personnes peuvent être des arbitres ou spectateurs ; les ballons petits "
        "peuvent ne pas être détectés. Aucun suivi d'identité n'est garanti."
    )
    st.warning(
        "Charge uniquement un fichier pour lequel tu disposes des droits de traitement. "
        "Une URL FIFA+/YouTube/Footballia ne fournit pas automatiquement ces droits."
    )
    demo = st.checkbox(
        "Utiliser l'extrait de démonstration libre SoccerTrack v2 (CC BY 4.0)",
        key="fpi_video_ccby_demo",
    )
    if demo:
        st.caption(
            "Vidéo : SoccerTrack v2, © Atom Scott et contributeurs, CC BY 4.0. "
            "Source : https://github.com/AtomScott/SoccerTrack-v2 "
            "La démonstration montre un match amateur, PAS Maroc–Portugal."
        )
    permission = st.checkbox(
        "Je confirme être autorisé à transmettre et analyser cette vidéo",
        key="fpi_video_permission",
    )
    upload = st.file_uploader(
        "MP4, MOV, MKV, WebM ou AVI (100 Mo maximum)",
        type=["mp4", "mov", "mkv", "webm", "avi"], key="fpi_user_video",
    )
    interval = st.slider("Échantillonner toutes les X secondes", 1, 60, 15, key="fpi_video_interval")
    maximum = st.slider("Nombre maximal de frames", 4, 40, 16, 4, key="fpi_video_max_frames")
    st.caption(
        "Pour les matchs longs dépassant 100 Mo, une CLI privée existe : "
        "python -m fpi.video_analysis.cli --video CHEMIN.mp4 --out rapport.json "
        "--max-frames 0 --interval-seconds 15 --consent-rights"
    )
    if st.button(
        "Détecter les joueurs et ballons candidats", type="primary",
        disabled=not(permission and (upload is not None or demo)), key="fpi_video_analyze",
    ):
        from pathlib import Path
        import tempfile
        from fpi.video_analysis.detector import YOLOXDetector, download_model
        from fpi.video_analysis.pipeline import analyze_video

        suffix = ".mp4" if demo else Path(upload.name).suffix.lower()
        if suffix not in (".mp4", ".mov", ".mkv", ".webm", ".avi"):
            st.error("Format vidéo refusé.")
            return
        if not demo and upload.size > 100 * 1024 * 1024:
            st.error("Ce fichier dépasse 100 Mo : utiliser la CLI privée.")
            return
        try:
            with st.spinner("Chargement du détecteur et analyse des images…"):
                model = YOLOXDetector(download_model(Path("data/models")))
                with tempfile.TemporaryDirectory(prefix="fpi-video-") as folder:
                    source = Path(folder) / ("private" + suffix)
                    if demo:
                        from urllib.request import Request, urlopen
                        url = (
                            "https://raw.githubusercontent.com/AtomScott/SoccerTrack-v2/"
                            "main/docs/assets/demo-tracking.mp4"
                        )
                        req = Request(url, headers={"User-Agent": "FPI CC-BY demonstration"})
                        with urlopen(req, timeout=45) as response, source.open("wb") as dest:
                            read_bytes = 0
                            while chunk := response.read(128 * 1024):
                                read_bytes += len(chunk)
                                if read_bytes > 8_000_000:
                                    raise ValueError("Extrait libre supérieur à 8 Mo")
                                dest.write(chunk)
                    else:
                        source.write_bytes(upload.getvalue())
                    summary, previews = analyze_video(
                        source, model, sample_interval_seconds=float(interval),
                        max_frames=maximum, preview_limit=3, tile_columns=2, tile_rows=2,
                    )
            st.session_state["fpi_video_last_result"] = ("SoccerTrack CC BY 4.0" if demo else upload.name, summary.to_dict(), previews)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            st.error(f"Analyse impossible : {exc}")

    if "fpi_video_last_result" in st.session_state:
        import json
        name, result, previews = st.session_state["fpi_video_last_result"]
        st.success(
            f"{name} : {result['sampled_frames']} images analysées sur "
            f"{result['duration_seconds'] / 60:.1f} minutes de vidéo."
        )
        left, right = st.columns(2)
        left.metric("Images avec personnes candidates", result["frames_with_people"])
        right.metric("Images avec ballon candidat", result["frames_with_ball_candidates"])
        if result["frames_with_ball_candidates"] == 0:
            st.warning("Aucun ballon détecté ; cela ne prouve pas son absence.")
        st.dataframe(
            [{"Temps (s)": x["time_seconds"], "Personnes": x["person_candidates"],
              "Ballons": x["sports_ball_candidates"]} for x in result["frames"]],
            width="stretch", hide_index=True,
        )
        for timestamp, picture in previews:
            st.image(picture, caption=f"Boîtes issues du modèle · {timestamp:.1f} s")
        st.download_button(
            "Exporter le rapport JSON (sans vidéo)",
            json.dumps(result, ensure_ascii=False, indent=2),
            file_name="fpi-detections-video.json", mime="application/json",
        )
        st.caption(
            "Aucun fichier source conservé. Ces observations sont des candidats "
            "visuels, pas des métriques tactiques validées ni une synchronisation StatsBomb."
        )

    st.divider()
    from fpi.ui.video_pitch_metrics import render_calibrated_video_metrics
    render_calibrated_video_metrics()
