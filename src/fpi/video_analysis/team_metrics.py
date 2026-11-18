"""Descriptive team shape metrics in CALIBRATED pitch metres, not raw pixels.

Only run this on reference game-state data or video detections that were
independently calibrated to a 105x68m pitch and assigned to known teams.
Do not calculate physical distances from pixel bounding boxes.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, median

PITCH_X = 52.5
PITCH_Y = 34.0


def _point(record):
    if record.get("role") not in ("player", "goalkeeper"):
        return None
    if record.get("team") not in ("left", "right"):
        return None
    try:
        x, y = float(record["x_m"]), float(record["y_m"])
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError("Position terrain non exploitable") from exc
    if not (math.isfinite(x) and math.isfinite(y)):
        raise ValueError("Position non finie")
    # Do not truncate valid coordinates outside field lines.
    return record["team"], x, y


def _zone(x, y):
    col = min(2, max(0, int(((x + PITCH_X) / (2 * PITCH_X)) * 3)))
    row = min(2, max(0, int(((y + PITCH_Y) / (2 * PITCH_Y)) * 3)))
    return f"{col}_{row}"


def summarize_team_shape(payload: dict, *, min_players: int = 5) -> dict:
    """Aggregate width/depth/centroid and coverage across independently timed frames."""
    if payload.get("coordinate_space") != "pitch_meters_center_origin":
        raise ValueError("Calibration terrain en mètres requise; pixels interdits")
    if not 2 <= min_players <= 11:
        raise ValueError("min_players hors bornes")
    frames = payload.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("Observations de joueurs absentes")
    aggregates = {side: {"sampled_frames": 0, "widths_m": [], "depths_m": [],
                         "centroids_x_m": [], "centroids_y_m": [],
                         "compactions_m": [], "occupancy": {}} for side in ("left", "right")}
    last_time = -1.0
    for frame in frames:
        ts = float(frame["time_seconds"])
        if not math.isfinite(ts) or ts <= last_time:
            raise ValueError("Horodatages non croissants")
        last_time = ts
        people = frame.get("players")
        if not isinstance(people, list):
            raise ValueError("Liste des joueurs manquante")
        observed = {"left": [], "right": []}
        for player in people:
            value = _point(player)
            if value is not None:
                side, x, y = value
                observed[side].append((x, y))
        for side, points in observed.items():
            if len(points) < min_players:
                continue
            a = aggregates[side]
            xs, ys = zip(*points)
            cx, cy = mean(xs), mean(ys)
            a["sampled_frames"] += 1
            a["widths_m"].append(max(ys)-min(ys))
            a["depths_m"].append(max(xs)-min(xs))
            a["centroids_x_m"].append(cx)
            a["centroids_y_m"].append(cy)
            a["compactions_m"].append(
                mean(math.hypot(x-cx, y-cy) for x, y in points))
            for x, y in points:
                zone = _zone(x, y)
                a["occupancy"][zone] = a["occupancy"].get(zone, 0) + 1
    summary = {}
    for side, item in aggregates.items():
        seen = item["sampled_frames"]
        summary[side] = {
            "qualified_frames": seen,
            "median_width_m": round(median(item["widths_m"]), 2) if seen else None,
            "median_depth_m": round(median(item["depths_m"]), 2) if seen else None,
            "mean_centroid_m": [
                round(mean(item["centroids_x_m"]), 2),
                round(mean(item["centroids_y_m"]), 2),
            ] if seen else None,
            "mean_player_spread_m": round(mean(item["compactions_m"]), 2) if seen else None,
            "occupancy_3x3_counts": item["occupancy"],
        }
    return {
        "analysis_type": "descriptive_reference_pitch_positions_not_video_inference",
        "coordinate_space": payload["coordinate_space"],
        "source": payload.get("source", "unspecified"),
        "total_sampled_frames": len(frames),
        "min_players": min_players,
        "teams": summary,
        "caveats": [
            "Metrics require reliable calibrated positions and team assignments.",
            "Camera movement, missed detections and calibration errors can bias results.",
            "No attacking direction, pressing, speed, possession or causal tactical claim inferred.",
            "Not directly connected to FPI's pixel detections; benchmark against ground truth first.",
        ],
    }


def main():
    p = argparse.ArgumentParser(description="FPI — métriques spatiales sur terrain calibré")
    p.add_argument("--positions", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--min-players", type=int, default=5)
    args = p.parse_args()
    report = summarize_team_shape(
        json.loads(args.positions.read_text(encoding="utf-8")),
        min_players=args.min_players,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"FPI_PITCH_METRICS qualified_frames={sum(x['qualified_frames'] for x in report['teams'].values())}")


if __name__ == "__main__":
    main()
