"""Optional real ByteTrack integration (roboflow/trackers >=2.7).

Run only on dense sequential FPI detections. Does NOT infer a team, number,
ball possession or a calibrated position. IDs reset after sparse gaps.
The proprietary match video is never loaded or redistributed by this module.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

LABELS = ("joueur_candidat", "ballon_candidat")


def track_with_bytetrack(report: dict, *, max_gap_seconds: float = 0.6) -> dict:
    if report.get("analysis_type") != "video_inference_sampled_not_tracking":
        raise ValueError("Rapport source d'inférence FPI requis")
    if not (0 < max_gap_seconds <= 5):
        raise ValueError("Intervalle de réassociation invalide")
    try:
        import supervision as sv
        from trackers import ByteTrackTracker
    except ImportError as exc:
        raise RuntimeError(
            "Installer trackers==2.7.0 dans l'environnement privé pour ByteTrack"
        ) from exc

    source_frames = report.get("frames")
    if not isinstance(source_frames, list) or not source_frames:
        raise ValueError("Images absentes")
    trackers = {}
    last_t = None
    epoch = 0
    frames = []
    identified = set()
    for frame in source_frames:
        t = float(frame["time_seconds"])
        if not math.isfinite(t) or (last_t is not None and t <= last_t):
            raise ValueError("Horodatages non strictement croissants")
        if last_t is not None and t - last_t > max_gap_seconds:
            trackers.clear()
            epoch += 1
        last_t = t
        original = frame.get("detections")
        if not isinstance(original, list):
            raise ValueError("Détections manquantes")
        result = [{**item, "track_id": None} for item in original]
        for label in LABELS:
            selected = [(idx, item) for idx, item in enumerate(original)
                        if item.get("label") == label]
            if not selected:
                # Advance empty frames too, so tracker's age is not frozen.
                if label in trackers:
                    trackers[label].update(sv.Detections.empty())
                continue
            for _, item in selected:
                if len(item.get("bbox_xyxy", [])) != 4:
                    raise ValueError("Boîte attendue bbox_xyxy")
            array = np.array([item["bbox_xyxy"] for _, item in selected], dtype=np.float32)
            confidence = np.array([item.get("confidence", 1) for _, item in selected], dtype=np.float32)
            if (not np.isfinite(array).all() or not np.isfinite(confidence).all()
                    or np.any(array[:, 2:] <= array[:, :2])
                    or np.any((confidence < 0) | (confidence > 1))):
                raise ValueError("Boîtes ou confidences incohérentes")
            observations = sv.Detections(
                xyxy=array,
                confidence=confidence,
                class_id=np.zeros(len(selected), dtype=np.int32),
                data={"fpi_row": np.arange(len(selected), dtype=np.int32)},
            )
            tracker = trackers.get(label)
            if tracker is None:
                tracker = ByteTrackTracker(
                    track_activation_threshold=0.25, minimum_consecutive_frames=1)
                trackers[label] = tracker
            tracked = tracker.update(observations)
            if len(tracked) and "fpi_row" not in tracked.data:
                raise RuntimeError("Tracker n'a pas conservé les indices de détection")
            for idx, track_id in zip(
                tracked.data.get("fpi_row", []),
                getattr(tracked, "tracker_id", []),
            ):
                idx, track_id = int(idx), int(track_id)
                if track_id < 0 or idx < 0 or idx >= len(selected):
                    continue
                # Separate namespaces across classes and gap-driven resets.
                identifier = f"{'P' if label == LABELS[0] else 'B'}:{epoch}:{track_id}"
                result[selected[idx][0]]["track_id"] = identifier
                identified.add(identifier)
        for item in result:
            if item.get("label") not in LABELS:
                raise ValueError("Classe inattendue")
        frames.append({"time_seconds": t, "detections": result})
    return {
        "analysis_type": "bytetrack_provisional_video_tracklets",
        "tracker_package": "roboflow/trackers",
        "source": report.get("source"),
        "max_gap_seconds": max_gap_seconds,
        "tracklets_with_ids": len(identified),
        "frames": frames,
        "caveats": [
            "ByteTrack is used but has not been benchmarked on a full-match labelled video.",
            "IDs reset on long gaps; no team, jersey, referee or appearance re-identification.",
            "Weak or missing ball detections cannot be repaired by this tracker.",
            "No calibration, tactical interpretation or possession inferred.",
        ],
    }


def main():
    p = argparse.ArgumentParser(description="FPI — vrai ByteTrack optionnel, IDs provisoires")
    p.add_argument("--detections", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--max-gap-seconds", type=float, default=0.6)
    args = p.parse_args()
    data = track_with_bytetrack(
        json.loads(args.detections.read_text(encoding="utf-8")),
        max_gap_seconds=args.max_gap_seconds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"FPI_REAL_BYTETRACK=EXECUTED tracklets={data['tracklets_with_ids']} "
          "(identity accuracy not yet evaluated)")


if __name__ == "__main__":
    main()
