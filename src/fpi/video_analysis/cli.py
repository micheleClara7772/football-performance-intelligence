"""Analyze a legally held full match outside Streamlit Cloud upload limits.

Usage:
  python -m fpi.video_analysis.cli --video /private/match.mp4 --out output.json
The video stays at its original path; only detections are exported.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import os

from .detector import YOLOXDetector, download_model
from .football_ball import FootballBallONNX, HybridFootballDetector
from .pipeline import analyze_video


def main() -> None:
    parser = argparse.ArgumentParser(description="FPI - détection sur une vidéo autorisée")
    parser.add_argument("--video", required=True, type=Path, help="Fichier MP4/MKV local licite")
    parser.add_argument("--out", required=True, type=Path, help="Résultat JSON sans médias")
    parser.add_argument("--interval-seconds", type=float, default=15.0)
    parser.add_argument("--max-frames", type=int, default=0,
                        help="0 signifie toute la durée du film, échantillonnée")
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--rows", type=int, default=2)
    parser.add_argument("--model-dir", type=Path, default=Path("data/models"))
    parser.add_argument("--ball-onnx", type=Path, default=None,
                        help="Poids ONNX football spécialisés, optionnels et sous licence séparée")
    parser.add_argument("--ball-threshold", type=float, default=0.20)
    parser.add_argument("--ball-columns", type=int, default=2,
                        help="Tuiles horizontales pour les petits ballons (1 à 4)")
    parser.add_argument("--ball-rows", type=int, default=1,
                        help="Tuiles verticales pour les petits ballons (1 à 3)")
    parser.add_argument("--consent-rights", action="store_true",
                        help="Je dispose des droits de traitement de ces images.")
    args = parser.parse_args()
    if not args.consent_rights:
        parser.error("--consent-rights requis : vérifie les droits de traitement vidéo.")
    model = YOLOXDetector(download_model(args.model_dir))
    if args.ball_onnx is not None:
        specialist = FootballBallONNX(args.ball_onnx, threshold=args.ball_threshold)
        model = HybridFootballDetector(
            model, specialist, ball_columns=args.ball_columns, ball_rows=args.ball_rows,
        )
        print('Modèle spécialisé de ballon activé ; vérifier sa licence AGPL-3.0.')
    summary, previews = analyze_video(
        args.video, model, sample_interval_seconds=args.interval_seconds,
        max_frames=args.max_frames, tile_columns=args.columns, tile_rows=args.rows,
        progress=lambda n, total: print(f"\rFrames traitées : {n}/{total}", end="", flush=True),
    )
    print()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    # Do not write preview media to disk by default.
    print(f"Analyse terminée : {summary.sampled_frames} frames, "
          f"{summary.person_candidates_total} boîtes personnes, "
          f"{summary.ball_candidates_total} boîtes ballons candidats ; "
          f"rapport : {args.out}")


if __name__ == "__main__":
    main()
