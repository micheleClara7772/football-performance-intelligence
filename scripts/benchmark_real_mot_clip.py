"""Run TRUE YOLOX inference on a private, licensed 4-minute SoccerTrack MOT clip.

Bounded test: 305 MB clip, 6 MB annotations, <=30 sampled frames,
0 previews or distributed video frames. This is NOT full-match validation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from scripts.evaluate_video_detections import evaluate
from scripts.prepare_soccertrack import DATASET, REVISION

MATCH_ID = "117093"
VIDEO = f"mot/clips/{MATCH_ID}.mp4"
MOT = f"mot/{MATCH_ID}.txt"
VIDEO_MAX_BYTES = 400 * 1024**2
MOT_MAX_BYTES = 25 * 1024**2


def reference_for_samples(rows, sample_times, fps, width, height):
    """Match zero-based MOT frames to sampled video timestamps at original FPS.

    All rows for each selected frame are required; ignore unrelated frames.
    """
    if not (math.isfinite(fps) and 1 <= fps <= 120):
        raise ValueError("FPS de vidéo invalide")
    if width < 64 or height < 64:
        raise ValueError("Vidéo trop petite")
    target = {int(round(float(t)*fps)): float(t) for t in sample_times}
    matches = {index: [] for index in target}
    incompatible = 0
    total = 0
    for row in rows:
        if not row or row[0].lstrip().startswith("#") or len(row) < 6:
            continue
        try:
            index = int(float(row[0]))
            if index not in target:
                continue
            x, y, w, h = [float(v) for v in row[2:6]]
            if not all(math.isfinite(v) for v in (x, y, w, h)) or w <= 0 or h <= 0:
                continue
        except (ValueError, OverflowError):
            continue
        total += 1
        if x < -0.1*width or y < -0.1*height or x+w > 1.1*width or y+h > 1.1*height:
            incompatible += 1
            continue
        matches[index].append({"label": "player", "bbox_xyxy": [x,y,x+w,y+h]})
    frames = [
        {"time_seconds": t, "objects": matches[index]}
        for index, t in sorted(target.items())
        if matches[index]
    ]
    return {
        "frames": frames,
        "sampled_times_requested": len(target),
        "sampled_times_with_reference": len(frames),
        "gt_box_count": sum(len(x["objects"]) for x in frames),
        "gt_objects_outside_video_resolution": incompatible,
        "gt_objects_examined": total,
        "geometry_consistent": total > 0 and incompatible / total <= 0.05,
        "identity_tracking_evaluated": False,
        "note": "Reference annotations only; does not label the ball, referees or every COCO person.",
    }


def _size_limit(api, path, token, limit):
    folder = path.rsplit("/", 1)[0]
    matches = [
        item for item in api.list_repo_tree(
            repo_id=DATASET, repo_type="dataset", revision=REVISION,
            path_in_repo=folder, recursive=False, expand=True, token=token,
        )
        if getattr(item, "path", None) == path
    ]
    if len(matches) != 1:
        raise ValueError("Fichier de référence absent de l'inventaire")
    size = getattr(matches[0], "size", None)
    if not isinstance(size, int) or size <= 0 or size > limit:
        raise ValueError("Taille inconnue ou téléchargement au-dessus du plafond")
    return size


def real_mot_benchmark(*, token, samples_interval=8.0, api=None, downloader=None):
    if not 5 <= samples_interval <= 30:
        raise ValueError("Intervalle benchmark limité entre 5 et 30 secondes")
    from huggingface_hub import HfApi, hf_hub_download
    from fpi.video_analysis.detector import YOLOXDetector, download_model
    from fpi.video_analysis.pipeline import analyze_video
    import cv2

    api = api or HfApi()
    downloader = downloader or hf_hub_download
    _size_limit(api, VIDEO, token, VIDEO_MAX_BYTES)
    _size_limit(api, MOT, token, MOT_MAX_BYTES)

    with TemporaryDirectory(prefix="fpi-mot-private-") as private:
        # These are explicitly consented dataset files, not protected replays.
        video = downloader(
            repo_id=DATASET, repo_type="dataset", filename=VIDEO,
            revision=REVISION, token=token, local_dir=private,
        )
        annotations = downloader(
            repo_id=DATASET, repo_type="dataset", filename=MOT,
            revision=REVISION, token=token, local_dir=private,
        )
        if Path(video).stat().st_size > VIDEO_MAX_BYTES or Path(annotations).stat().st_size > MOT_MAX_BYTES:
            raise ValueError("Taille réelle au-dessus de la limite")
        start = perf_counter()
        model = YOLOXDetector(download_model(Path(private) / "models"))
        summary, _ = analyze_video(
            Path(video), model, sample_interval_seconds=samples_interval,
            max_frames=0, preview_limit=0, tile_columns=2, tile_rows=2,
        )
        elapsed = round(perf_counter() - start, 2)
        with Path(annotations).open("r", encoding="utf-8-sig", newline="") as handle:
            ground = reference_for_samples(
                csv.reader(handle),
                [x["time_seconds"] for x in summary.per_frame],
                summary.estimated_fps, summary.width, summary.height,
            )
        if not ground["frames"]:
            raise ValueError("Aucune vérité terrain correspondante dans le clip")
        # MOT ground truth labels only tracked players, not all people or balls;
        # therefore discard any predicted BALL boxes before measuring persons.
        clean_predictions = summary.to_dict()
        for row in clean_predictions["frames"]:
            row["detections"] = [
                det for det in row["detections"]
                if det["label"] == "joueur_candidat"
            ]
        metrics = evaluate(clean_predictions, {"frames": ground["frames"]},
                           iou_threshold=0.3, tolerance_seconds=0.02)
        scoreable = (
            ground["geometry_consistent"]
            and ground["sampled_times_with_reference"] >= 15
            and metrics["missing_prediction_frames"] == 0
        )
        return {
            "validation_type": "real_yolox_video_inference_on_soccertrack_mot_clip",
            "license": "SoccerTrack v2 CC BY 4.0 (attribution required)",
            "match_id": MATCH_ID,
            "dataset_revision": REVISION,
            "real_clip_inference_executed": True,
            "actual_full_match_inference": False,
            "full_match_detection_validated": False,
            "ball_detection_precision_recall_validated": False,
            "continuous_identity_tracking_validated": False,
            "video_width": summary.width,
            "video_height": summary.height,
            "video_fps": summary.estimated_fps,
            "clip_duration_seconds": summary.duration_seconds,
            "sample_interval_seconds": samples_interval,
            "sampled_frames": summary.sampled_frames,
            "covered_until_seconds": summary.covered_until_seconds,
            "person_detection_runtime_seconds": elapsed,
            "model_person_candidates": summary.person_candidates_total,
            "model_ball_candidates_unscored": summary.ball_candidates_total,
            "ground_truth": {k:v for k,v in ground.items() if k != "frames"},
            "person_detection_metrics": metrics["metrics"]["person"] if scoreable else None,
            "quality_scoreable": scoreable,
            "caveat": (
                "4-minute MOT CLIP only. Reference may exclude referees and others; "
                "no image-space ball ground truth. Evaluation on sparse image samples, "
                "not full-frame or 90-minute tracking."
            ),
        }


def main():
    p = argparse.ArgumentParser(description="FPI — vrai benchmark YOLOX sur clip SoccerTrack privé")
    p.add_argument("--out", type=Path, default=Path("outputs/real-mot-117093.json"))
    p.add_argument("--interval-seconds", type=float, default=8.0)
    args = p.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("FPI_REAL_MOT=NEEDS_AUTHENTICATION")
    try:
        report = real_mot_benchmark(token=token, samples_interval=args.interval_seconds)
    except Exception as exc:
        # Do not dump exceptions that could contain signed HF URLs or headers.
        raise SystemExit(f"FPI_REAL_MOT=FAILED ({type(exc).__name__}); voir schéma/ressources")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("FPI_REAL_MOT=" + ("SCORED" if report["quality_scoreable"] else "INFERENCE_ONLY"))
    print("FPI_REAL_MOT_REPORT=" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
