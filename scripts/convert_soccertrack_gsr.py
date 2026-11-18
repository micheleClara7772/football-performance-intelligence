"""Memory-bounded SoccerTrack v2 GSR converter for reference pitch metrics.

The *shipped* GSR format is SoccerNet COCO, not the flat array from an
older specification. Its JSON may exceed 2 GiB per half, so stream records
with optional ijson. This produces independent REFERENCE game-state
positions; it does not derive them from FPI's neural video detector.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FPS = 25


def _frame_index(image_id):
    """Released image_id: sequence-prefix plus 6-digit, one-based frame."""
    s = str(image_id)
    if len(s) < 7 or not s.isdecimal():
        raise ValueError("image_id SoccerTrack v2 inattendu")
    n = int(s[-6:]) - 1
    if n < 0:
        raise ValueError("image_id non valide")
    return n


def convert_gsr_records(records, *, every_seconds: int = 5,
                        source: str = "soccertrack-v2-v1.2-gsr"):
    if not 1 <= every_seconds <= 120:
        raise ValueError("Intervalle GSR entre 1 et 120 secondes")
    by_frame = {}
    selected = 0
    for ann in records:
        if ann.get("supercategory") != "object":
            continue
        attributes = ann.get("attributes") or {}
        role = attributes.get("role")
        team = attributes.get("team")
        if role not in ("player", "goalkeeper") or team not in ("left", "right"):
            continue
        frame_idx = _frame_index(ann.get("image_id"))
        if frame_idx % (FPS * every_seconds):
            continue
        pitch = ann.get("bbox_pitch") or {}
        if "x_bottom_middle" not in pitch or "y_bottom_middle" not in pitch:
            continue
        x = float(pitch["x_bottom_middle"])
        y = float(pitch["y_bottom_middle"])
        if not (-1000 < x < 1000 and -1000 < y < 1000):
            raise ValueError("Coordonnées terrain invraisemblables")
        by_frame.setdefault(frame_idx, []).append({
            "role": role,
            "team": team,
            "x_m": x, "y_m": y,
        })
        selected += 1
    return {
        "coordinate_space": "pitch_meters_center_origin",
        "source": source,
        "reference_type": "independent_gsr_not_video_detection",
        "frames": [
            {"time_seconds": frame_idx / FPS, "players": players}
            for frame_idx, players in sorted(by_frame.items())
        ],
        "selected_player_observations": selected,
        "warnings": [
            "These are published reference positions, not FPI model predictions.",
            "Half timestamps start at zero; do not merge halves without verified offsets.",
            "SoccerTrack v2 team sides can flip between halves.",
        ],
    }


def main():
    p = argparse.ArgumentParser(description="FPI — extraction streaming GSR SoccerTrack v2")
    p.add_argument("--gsr", required=True, type=Path,
                   help="Fichier original gsr/<id>/<id>_1st.json ou _2nd.json")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--every-seconds", type=int, default=5)
    args = p.parse_args()
    if not args.gsr.is_file():
        p.error("Fichier GSR privé absent")
    try:
        import ijson
    except ImportError as exc:
        raise SystemExit(
            "Installer ijson dans l'environnement Python isolé pour lire le JSON "
            "de plusieurs gigaoctets sans le charger en mémoire."
        ) from exc
    with args.gsr.open("rb") as handle:
        records = ijson.items(handle, "annotations.item")
        data = convert_gsr_records(records, every_seconds=args.every_seconds,
                                   source=f"soccertrack-v2-v1.2-gsr:{args.gsr.stem}")
    if not data["frames"]:
        raise SystemExit("Aucun joueur trouvé : vérifier le schéma GSR réel de v1.2")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FPI_GSR_REFERENCE=READY (not inferred from video) "
          f"frames={len(data['frames'])} objects={data['selected_player_observations']}")


if __name__ == "__main__":
    main()
