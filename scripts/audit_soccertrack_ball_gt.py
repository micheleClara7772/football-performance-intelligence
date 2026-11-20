"""Audit independent SoccerTrack ball annotations before detector scoring.

JSON schema: {"match_id":"117093","source":"human-independent",
"frames":[{"half":1,"time_seconds":15.0,"width":1920,"height":1080,
"reviewed":true,"ball_visible":true,
"objects":[{"label":"ball","bbox_xyxy":[100,200,110,210]}]}]}.
No media or predictions are needed. Reviewed negatives must have zero boxes.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path


def audit(payload: dict, *, min_per_half: int = 1) -> dict:
    if payload.get("match_id") != "117093":
        raise ValueError("Expected authorized match 117093")
    if payload.get("source") not in ("human-independent", "independent-licensed-gt"):
        raise ValueError("Ground truth must have independent provenance")
    frames = payload.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("No annotated frames")
    if min_per_half < 1:
        raise ValueError("Invalid minimum")
    counts = Counter()
    timestamps = {1: set(), 2: set()}
    for index, frame in enumerate(frames):
        half = frame.get("half")
        if type(half) is not int or half not in (1, 2):
            raise ValueError(f"Frame {index}: invalid half")
        t = frame.get("time_seconds")
        if type(t) not in (int, float) or not math.isfinite(t) or t < 0 or t > 7200:
            raise ValueError(f"Frame {index}: invalid time")
        if t in timestamps[half]:
            raise ValueError(f"Frame {index}: duplicate timestamp")
        timestamps[half].add(t)
        w, h = frame.get("width"), frame.get("height")
        if any(type(v) is not int or v <= 0 for v in (w, h)):
            raise ValueError(f"Frame {index}: invalid dimensions")
        if frame.get("reviewed") is not True or type(frame.get("ball_visible")) is not bool:
            raise ValueError(f"Frame {index}: incomplete independent review")
        objects = frame.get("objects")
        if not isinstance(objects, list):
            raise ValueError(f"Frame {index}: missing objects")
        if bool(objects) != frame["ball_visible"]:
            raise ValueError(f"Frame {index}: visibility inconsistent with boxes")
        for obj in objects:
            if not isinstance(obj, dict) or obj.get("label") != "ball":
                raise ValueError(f"Frame {index}: non-ball annotation")
            b = obj.get("bbox_xyxy")
            if not isinstance(b, list) or len(b) != 4 or any(
                type(x) not in (int, float) or not math.isfinite(x) for x in b
            ):
                raise ValueError(f"Frame {index}: invalid box")
            if not (0 <= b[0] < b[2] <= w and 0 <= b[1] < b[3] <= h):
                raise ValueError(f"Frame {index}: box outside image")
        counts[f"half_{half}_reviewed"] += 1
        counts[f"half_{half}_positive"] += int(frame["ball_visible"])
        counts[f"half_{half}_negative"] += int(not frame["ball_visible"])
        counts[f"half_{half}_ball_boxes"] += len(objects)
    ready = all(counts[f"half_{half}_reviewed"] >= min_per_half
                and counts[f"half_{half}_positive"] > 0
                and counts[f"half_{half}_negative"] > 0 for half in (1, 2))
    return {
        "match_id": "117093",
        "independent_gt_audit_passed": ready,
        "frames_reviewed": len(frames),
        "per_half": {str(half): {
            "reviewed": counts[f"half_{half}_reviewed"],
            "positive": counts[f"half_{half}_positive"],
            "negative": counts[f"half_{half}_negative"],
            "ball_boxes": counts[f"half_{half}_ball_boxes"],
            "time_min": min(timestamps[half]) if timestamps[half] else None,
            "time_max": max(timestamps[half]) if timestamps[half] else None,
        } for half in (1, 2)},
        "warning": "Annotation audit only: not a detector benchmark, no TP/FP/FN measured.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Audit independent ball GT across both halves")
    p.add_argument("--annotations", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--min-per-half", type=int, default=10)
    args = p.parse_args()
    report = audit(json.loads(args.annotations.read_text(encoding="utf-8")),
                   min_per_half=args.min_per_half)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    if not report["independent_gt_audit_passed"]:
        raise SystemExit("GT incomplete: both halves require positive and negative frames")


if __name__ == "__main__":
    main()
