"""Bounded true-pixel inference spanning one FULL 45+min SoccerTrack half.

The resulting report documents timeline sampling, NOT every-frame tracking,
player ID, ball precision or calibrated tactical metrics. This is a staging
step toward evaluation on a licensed 90-minute match.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from scripts.prepare_soccertrack import DATASET, REVISION

MATCH = "117093"
MAX_VIDEO_BYTES = 4 * 1024**3
MIN_FREE_BYTES = 11 * 1024**3


def temporal_coverage(summary, *, interval_seconds: float) -> dict:
    times = [float(x["time_seconds"]) for x in summary.per_frame]
    duration = float(summary.duration_seconds)
    if not times or not 0 < duration <= 4*60*60:
        raise ValueError("Chronologie invalide")
    expected = max(1, math.ceil(duration/interval_seconds))
    windows = {}
    for t in times:
        w = int(t//300)
        windows[w] = windows.get(w,0) + 1
    complete = (
        summary.sampled_frames >= math.ceil(expected * 0.95)
        and times[0] <= interval_seconds
        and times[-1] >= duration - 2*interval_seconds
    )
    return {
        "reported_duration_seconds": round(duration, 2),
        "first_decoded_sample_seconds": times[0],
        "last_decoded_sample_seconds": times[-1],
        "expected_sample_count": expected,
        "decoded_sample_count": len(times),
        "sample_completion_ratio": round(len(times)/expected,4),
        "samples_per_five_minute_window": windows,
        "coverage_95pct_of_requested_timestamps": complete,
        "all_source_frames_analyzed": False,
        "continuous_tracking": False,
    }


def analyze_half(*, token: str, half: str,
                 interval_seconds: float=15.0,
                 specialist_enabled: bool=True) -> dict:
    if half not in ("1st","2nd"):
        raise ValueError("Mi-temps SoccerTrack inconnue")
    if interval_seconds not in (10.0,15.0,30.0):
        raise ValueError("Échantillonnage autorisé : 10, 15 ou 30 secondes")
    from huggingface_hub import HfApi, hf_hub_download
    from fpi.video_analysis.detector import YOLOXDetector, download_model
    from fpi.video_analysis.football_ball import FootballBallONNX, HybridFootballDetector
    from fpi.video_analysis.pipeline import analyze_video

    path = f"videos/{MATCH}/{MATCH}_panorama_{half}_half.mp4"
    api = HfApi()
    entries = list(api.list_repo_tree(
        repo_id=DATASET, repo_type="dataset", revision=REVISION,
        path_in_repo=f"videos/{MATCH}", recursive=False, expand=True, token=token))
    matched = [e for e in entries if e.path == path]
    if len(matched) != 1 or not isinstance(matched[0].size, int):
        raise ValueError("Vidéo officielle SoccerTrack non trouvée")
    declared_bytes = matched[0].size
    if not 0 < declared_bytes <= MAX_VIDEO_BYTES:
        raise ValueError("Taille vidéo au-dessus du budget autorisé")
    free_bytes = shutil.disk_usage("/tmp").free
    if free_bytes < max(MIN_FREE_BYTES, 2*declared_bytes+2*1024**3):
        raise ValueError("Espace temporaire insuffisant, aucun téléchargement")
    with TemporaryDirectory(prefix=f"fpi-full-half-{half}-") as private:
        video = hf_hub_download(
            repo_id=DATASET, repo_type="dataset", revision=REVISION,
            filename=path, local_dir=private, token=token)
        if Path(video).stat().st_size != declared_bytes:
            raise ValueError("Vidéo transférée incomplète ou modifiée")
        yolox = YOLOXDetector(download_model(Path(private)/"models"))
        class FinePeople:
            def __init__(self, base): self.base=base
            def detect_frame(self, frame_bgr, **opts):
                return self.base.detect_frame(frame_bgr, person_threshold=0.20,
                                              ball_threshold=0.08, **opts)

        experiments = [
            ("yolox_4x3", FinePeople(yolox)),
        ]
        if specialist_enabled:
            checkpoint = hf_hub_download(
                repo_id="acatorcini/yolov9-soccer-ball",
                filename="v9b_best.onnx",
                local_dir=str(Path(private)/"specialist"),
            )
            ball = FootballBallONNX(Path(checkpoint), threshold=0.20)
            experiments.append((
                "hybrid_yolox_people_yolov9_ball",
                HybridFootballDetector(FinePeople(yolox),ball,
                                       ball_columns=2,ball_rows=1),
            ))
        runs=[]
        first_timeline=None
        for name, detector in experiments:
            started=perf_counter()
            summary, _=analyze_video(
                Path(video), detector, sample_interval_seconds=interval_seconds,
                max_frames=0, preview_limit=0, tile_columns=4, tile_rows=3,
            )
            runtime=round(perf_counter()-started,2)
            coverage=temporal_coverage(summary,interval_seconds=interval_seconds)
            timestamps=[x["time_seconds"] for x in summary.per_frame]
            if first_timeline is None: first_timeline=timestamps
            elif timestamps!=first_timeline:
                raise ValueError("Les modèles ne couvrent pas les mêmes instants")
            if not coverage["coverage_95pct_of_requested_timestamps"]:
                raise ValueError("La vidéo réelle n'a pas couvert toute la période")
            runs.append({
                "model":name,
                "cpu_inference_and_decode_seconds":runtime,
                "person_candidate_boxes":summary.person_candidates_total,
                "ball_candidate_boxes_unscored":summary.ball_candidates_total,
                "frames_with_person_candidates":summary.frames_with_people,
                "frames_with_ball_candidates_unscored":summary.frames_with_ball_candidates,
                "temporal_coverage":coverage,
                # Limited report avoids media, identities and massive row counts.
                "sample_timeline_seconds": timestamps,
            })
        return {
            "validation_type":"real_video_full_half_sampled_inference_not_tracking",
            "dataset":DATASET,"revision":REVISION,
            "match_id":MATCH,"half":half,
            "source_size_bytes":declared_bytes,
            "source_license":"SoccerTrack v2 CC BY 4.0; user authorized access",
            "sampling_interval_seconds":interval_seconds,
            "runs":runs,
            "both_models_same_frames":len(runs)==2,
            "full_match_90min_completed":False,
            "continuous_identity_tracking_validated":False,
            "ball_precision_recall_validated_on_this_video":False,
            "caveat":(
                "One complete half TIMELINE sampled at intervals, not every frame. "
                "Ball counts are unverified candidates; no image-plane ball GT, "
                "no identity/jersey/team verification or StatsBomb synchronization."
            ),
        }


def main():
    p=argparse.ArgumentParser(description="FPI — détection vraie sur mi-temps entière")
    p.add_argument("--half",choices=("1st","2nd"),required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--interval-seconds",type=float,default=15.0)
    p.add_argument("--no-specialist",action="store_true")
    p.add_argument("--consent-rights",action="store_true")
    args=p.parse_args()
    if not args.consent_rights:
        p.error("--consent-rights requis après vérification de la licence")
    token=os.environ.get("HF_TOKEN")
    if not token: p.error("HF_TOKEN absent du secret GitHub")
    try:
        report=analyze_half(
            token=token,half=args.half,interval_seconds=args.interval_seconds,
            specialist_enabled=not args.no_specialist)
    except Exception as exc:
        # Never print signed CDN URLs, download credentials or full HTTP messages.
        raise SystemExit("FPI_FULL_HALF=FAILED type="+type(exc).__name__) from None
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                        encoding="utf-8")
    print("FPI_FULL_HALF=TIMELINE_SAMPLED_VALIDATED_NOT_TRACKING")
    print("FPI_FULL_HALF_SUMMARY="+json.dumps({
        "match_id":report["match_id"],"half":report["half"],
        "source_size_bytes":report["source_size_bytes"],
        "models":[{"model":r["model"],
                   "ball_candidate_boxes_unscored":r["ball_candidate_boxes_unscored"],
                   "person_candidate_boxes":r["person_candidate_boxes"],
                   "cpu_seconds":r["cpu_inference_and_decode_seconds"],
                   "coverage":r["temporal_coverage"]["sample_completion_ratio"]}
                  for r in report["runs"]],
        "full_match_90min_completed":False,
    }))


if __name__=="__main__":
    main()
