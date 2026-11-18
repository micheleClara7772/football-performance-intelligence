"""Evaluate real FPI detections against independently labelled frames.

Input truth format:
{
  "frames": [
    {"time_seconds": 15.0,
     "objects": [
       {"label": "person", "bbox_xyxy": [10,20,40,80]},
       {"label": "ball", "bbox_xyxy": [100,60,110,70]}
     ]}
  ]
}
Only *fully labelled* sampled frames should be included, with ALL visible
persons and balls, including zero-object frames. Never conflate number of
automatic detections with measured precision/recall.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


LABELS = {
    "person": "person", "player": "person", "referee": "person",
    "joueur_candidat": "person",
    "ball": "ball", "sports_ball": "ball", "ballon_candidat": "ball",
}


def _box(obj: dict) -> tuple[float, float, float, float]:
    coords = obj.get("bbox_xyxy")
    if not isinstance(coords, list) or len(coords) != 4:
        raise ValueError("Boîte attendue au format bbox_xyxy [x1,y1,x2,y2]")
    try:
        x1, y1, x2, y2 = [float(v) for v in coords]
    except (ValueError, TypeError) as exc:
        raise ValueError("Coordonnées de boîte non numériques") from exc
    if not all(math.isfinite(v) for v in (x1, y1, x2, y2)) or x2 <= x1 or y2 <= y1:
        raise ValueError("Coordonnées de boîte invalides")
    return x1, y1, x2, y2


def _iou(first: tuple, second: tuple) -> float:
    x1 = max(first[0], second[0])
    y1 = max(first[1], second[1])
    x2 = min(first[2], second[2])
    y2 = min(first[3], second[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    a = (first[2] - first[0]) * (first[3] - first[1])
    b = (second[2] - second[0]) * (second[3] - second[1])
    return intersection / (a + b - intersection) if a + b - intersection else 0.0


def _group_objects(frame: dict, *, truth: bool) -> dict:
    objects = frame.get("objects") if truth else frame.get("detections")
    if not isinstance(objects, list):
        raise ValueError("Liste d'objets annotés/détectés manquante")
    out = {"person": [], "ball": []}
    for item in objects:
        label = LABELS.get(item.get("label"))
        if label is None:
            raise ValueError(f"Classe inconnue : {item.get('label')!r}")
        out[label].append(_box(item))
    return out


def evaluate(detections: dict, annotations: dict, *,
             iou_threshold: float = 0.3,
             tolerance_seconds: float = 0.6) -> dict:
    if not 0 < iou_threshold <= 1 or not 0 <= tolerance_seconds <= 5:
        raise ValueError("Seuil IoU ou tolérance temporelle invalide")
    predicted = detections.get("frames")
    reference = annotations.get("frames")
    if not isinstance(predicted, list) or not isinstance(reference, list) or not reference:
        raise ValueError("Images de détection et annotations non vides requises")
    if "analysis_type" in detections and detections["analysis_type"] != "video_inference_sampled_not_tracking":
        raise ValueError("Rapport de détection vidéo non pris en charge")
    totals = {"person": {"tp": 0, "fp": 0, "fn": 0},
              "ball": {"tp": 0, "fp": 0, "fn": 0}}
    used = set()
    for ground_frame in reference:
        timestamp = float(ground_frame["time_seconds"])
        if not math.isfinite(timestamp) or timestamp < 0:
            raise ValueError("Horodatage vérité terrain invalide")
        ground = _group_objects(ground_frame, truth=True)
        eligible = [
            (abs(float(p["time_seconds"]) - timestamp), j, p)
            for j, p in enumerate(predicted)
            if j not in used and abs(float(p["time_seconds"]) - timestamp) <= tolerance_seconds
        ]
        if not eligible:
            found = {"person": [], "ball": []}
        else:
            _, frame_index, frame = min(eligible, key=lambda x: (x[0], x[1]))
            used.add(frame_index)
            found = _group_objects(frame, truth=False)
        for label in ("person", "ball"):
            gt, pr = ground[label], found[label]
            # Greedy one-to-one matches ordered by IoU, no double credit.
            matches = sorted(
                [(_iou(a, b), i, j) for i, a in enumerate(gt)
                 for j, b in enumerate(pr)],
                reverse=True,
            )
            gt_used, pr_used = set(), set()
            for overlap, i, j in matches:
                if overlap < iou_threshold:
                    break
                if i not in gt_used and j not in pr_used:
                    gt_used.add(i)
                    pr_used.add(j)
            tp = len(gt_used)
            totals[label]["tp"] += tp
            totals[label]["fn"] += len(gt) - tp
            totals[label]["fp"] += len(pr) - tp

    metrics = {}
    for label, count in totals.items():
        tp, fp, fn = (count[k] for k in ("tp", "fp", "fn"))
        metrics[label] = {
            **count,
            "precision": round(tp / (tp + fp), 4) if tp + fp else None,
            "recall": round(tp / (tp + fn), 4) if tp + fn else None,
            "f1": round(2 * tp / (2 * tp + fp + fn), 4)
            if 2 * tp + fp + fn else None,
        }
    return {
        "validation_type": "independent_bbox_precision_recall_on_labelled_frames",
        "iou_threshold": iou_threshold,
        "timestamp_tolerance_seconds": tolerance_seconds,
        "fully_annotated_frames": len(reference),
        "matched_frames": len(used),
        "missing_prediction_frames": len(reference) - len(used),
        "metrics": metrics,
        "warning": (
            "Metrics reflect annotated frames only, not unlabelled match footage. "
            "No tracking/possession accuracy is inferred."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="FPI — évaluer les boîtes sur vérité terrain")
    parser.add_argument("--detections", required=True, type=Path)
    parser.add_argument("--annotations", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--iou", type=float, default=0.3)
    parser.add_argument("--time-tolerance", type=float, default=0.6)
    args = parser.parse_args()
    predictions = json.loads(args.detections.read_text(encoding="utf-8"))
    ground_truth = json.loads(args.annotations.read_text(encoding="utf-8"))
    report = evaluate(predictions, ground_truth, iou_threshold=args.iou,
                      tolerance_seconds=args.time_tolerance)
    report_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report_text, encoding="utf-8")
    print(report_text)


if __name__ == "__main__":
    main()
