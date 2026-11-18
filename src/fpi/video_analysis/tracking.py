"""Experimental short-gap bounding-box association, NOT ByteTrack nor identity recognition.

Input is a real FPI sampled-detection JSON. Every track ID is a provisional
image-space association within one video segment; IDs are reset after gaps.
This cannot recover jersey number, team, metric position, or ball possession.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def _box(values):
    if not isinstance(values, (list, tuple)) or len(values) != 4:
        raise ValueError("bbox_xyxy invalide")
    try:
        a, b, c, d = map(float, values)
    except (ValueError, TypeError) as exc:
        raise ValueError("Coordonnées non numériques") from exc
    if not all(map(math.isfinite, (a, b, c, d))) or a >= c or b >= d:
        raise ValueError("bbox_xyxy invalide")
    return (a, b, c, d)


def _iou(a, b):
    w = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    h = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    intersection = w * h
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection)


def _center(a):
    return ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2)


def _cost(previous, current):
    ax, ay = _center(previous)
    bx, by = _center(current)
    scale = max(10.0, math.sqrt((previous[2]-previous[0]) * (previous[3]-previous[1])))
    distance = math.hypot(ax-bx, ay-by) / scale
    overlap = _iou(previous, current)
    # Avoid matching unrelated objects in a crowded panorama.
    if (overlap < 0.05 and distance > 0.8) or distance > 2.0:
        return None
    return distance + (1 - overlap) * 0.4


def associate_detections(report: dict, *, max_gap_seconds: float = 0.6,
                         min_confidence: float = 0.0) -> dict:
    """Associate neighbouring frame detections with one-to-one greedy matching.

    For FPI's 5s/15s default sampling, no consecutive identity is claimed.
    For 5 Hz video sampling IDs may persist locally, with no re-ID guarantee.
    """
    if not 0 < max_gap_seconds <= 5 or not 0 <= min_confidence < 1:
        raise ValueError("Paramètres de suivi invalides")
    if report.get("analysis_type") != "video_inference_sampled_not_tracking":
        raise ValueError("Rapport FPI de détections requis")
    original = report.get("frames")
    if not isinstance(original, list) or not original:
        raise ValueError("Aucune image à associer")
    active = {}
    identities = {}
    result = []
    next_id = 1
    last_time = -1.0
    for frame in original:
        t = float(frame["time_seconds"])
        if not math.isfinite(t) or t <= last_time:
            raise ValueError("Horodatages non strictement croissants")
        last_time = t
        active = {i: s for i, s in active.items()
                  if t - s["time"] <= max_gap_seconds + 1e-9}
        raw = frame.get("detections")
        if not isinstance(raw, list):
            raise ValueError("Détections d'image absentes")
        prepared = []
        for det in raw:
            label = det.get("label")
            if label not in ("joueur_candidat", "ballon_candidat"):
                raise ValueError("Classe de détection inattendue")
            box = _box(det.get("bbox_xyxy"))
            conf = float(det.get("confidence", 1.0))
            if not math.isfinite(conf) or not 0 <= conf <= 1:
                raise ValueError("Confiance invalide")
            if conf >= min_confidence:
                prepared.append((label, box, conf, det))
        pairs = []
        for i, obj in active.items():
            for j, (label, box, _, _) in enumerate(prepared):
                if obj["label"] == label:
                    cost = _cost(obj["box"], box)
                    if cost is not None:
                        pairs.append((cost, i, j))
        pairs.sort()
        assignments = {}
        used_tracks = set()
        for _, i, j in pairs:
            if i not in used_tracks and j not in assignments:
                used_tracks.add(i)
                assignments[j] = i
        enriched = []
        for j, (label, box, _, det) in enumerate(prepared):
            identifier = assignments.get(j)
            if identifier is None:
                identifier = next_id
                next_id += 1
                identities[identifier] = {
                    "track_id": identifier, "label": label,
                    "first_seconds": t, "last_seconds": t, "observations": 0,
                }
            active[identifier] = {"box": box, "label": label, "time": t}
            identities[identifier]["last_seconds"] = t
            identities[identifier]["observations"] += 1
            enriched.append({**det, "track_id": identifier,
                             "association": "continued" if j in assignments else "new"})
        result.append({"time_seconds": t, "detections": enriched})
    return {
        "analysis_type": "experimental_short_gap_bbox_association",
        "source": report.get("source"),
        "max_gap_seconds": max_gap_seconds,
        "frames": result,
        "tracks": list(identities.values()),
        "limitations": [
            "IDs are provisional: no appearance re-identification, team or referee classification.",
            "Scene cuts, occlusions, camera movement and tiny balls can break identities.",
            "Sparse 5-15 second sampling does not provide continuous tracking.",
            "No pitch calibration, distance, speed, possession or validated tactical metric.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="FPI: suivi provisoire de boîtes rapprochées")
    parser.add_argument("--detections", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-gap-seconds", type=float, default=0.6)
    parser.add_argument("--min-confidence", type=float, default=0.0)
    args = parser.parse_args()
    data = json.loads(args.detections.read_text(encoding="utf-8"))
    tracked = associate_detections(data, max_gap_seconds=args.max_gap_seconds,
                                   min_confidence=args.min_confidence)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(tracked, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"FPI_TRACKING_ASSOCIATION: {len(tracked['tracks'])} provisional tracklets; "
          "not validated identity tracking")


if __name__ == "__main__":
    main()
