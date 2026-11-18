"""Compare two FPI detector reports on the SAME fully annotated frames.

A winner is not declared unless a meaningful independent benchmark exists.
Runtime numbers must be measured externally and passed explicitly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.evaluate_video_detections import evaluate


def compare_reports(baseline: dict, specialist: dict, truth: dict, *,
                    min_annotated_frames: int = 100, min_ball_objects: int = 30,
                    baseline_runtime_seconds: float | None = None,
                    specialist_runtime_seconds: float | None = None) -> dict:
    frames = truth.get("frames", [])
    if not isinstance(frames, list) or not frames:
        raise ValueError("Annotations indépendantes requises")
    n_ball = sum(obj.get("label") in ("ball", "sports_ball", "ballon_candidat")
                 for frame in frames for obj in frame.get("objects", []))
    base_eval = evaluate(baseline, truth)
    spec_eval = evaluate(specialist, truth)
    enough = (len(frames) >= min_annotated_frames and n_ball >= min_ball_objects
              and base_eval["matched_frames"] == len(frames)
              and spec_eval["matched_frames"] == len(frames))
    results = {"yolox": base_eval, "specialist": spec_eval}
    measured = {}
    for name, runtime in (("yolox", baseline_runtime_seconds),
                          ("specialist", specialist_runtime_seconds)):
        if runtime is not None and runtime <= 0:
            raise ValueError("Durée d'inférence mesurée doit être positive")
        measured[name] = runtime
    winner = None
    if enough:
        a = base_eval["metrics"]["ball"]
        b = spec_eval["metrics"]["ball"]
        # Prefer F1; tie broken by recall. No claim of statistical significance.
        if a["f1"] is not None and b["f1"] is not None:
            k1 = (a["f1"], a["recall"] or 0)
            k2 = (b["f1"], b["recall"] or 0)
            winner = "specialist" if k2 > k1 else ("yolox" if k1 > k2 else "tie")
    return {
        "analysis_type": "comparison_on_independently_annotated_frames",
        "annotated_frames": len(frames),
        "annotated_balls": n_ball,
        "sufficient_sample_for_provisional_selection": enough,
        "provisional_winner": winner,
        "detectors": results,
        "measured_runtime_seconds": measured,
        "notice": (
            "The selection is provisional, not a confidence interval or a full-match "
            "validation. Missing footage and tracking errors remain unmeasured."
        ),
    }


def main():
    p = argparse.ArgumentParser(description="FPI — benchmark YOLOX vs spécialiste")
    p.add_argument("--yolox", required=True, type=Path)
    p.add_argument("--specialist", required=True, type=Path)
    p.add_argument("--annotations", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--yolox-runtime", type=float)
    p.add_argument("--specialist-runtime", type=float)
    args = p.parse_args()
    payload = compare_reports(
        json.loads(args.yolox.read_text(encoding="utf-8")),
        json.loads(args.specialist.read_text(encoding="utf-8")),
        json.loads(args.annotations.read_text(encoding="utf-8")),
        baseline_runtime_seconds=args.yolox_runtime,
        specialist_runtime_seconds=args.specialist_runtime,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"FPI_BENCHMARK provisional_winner={payload['provisional_winner']}; "
          f"annotated_frames={payload['annotated_frames']} "
          f"annotated_balls={payload['annotated_balls']}")


if __name__ == "__main__":
    main()
