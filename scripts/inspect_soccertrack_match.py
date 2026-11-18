"""Authenticated, metadata-only inventory of one SoccerTrack v2 match.

Optional: inspect one small real MOT reference text (never upload it).
No video, GSR, raw calibration, or full dataset are downloaded by this tool.
All tokens are taken from HF_TOKEN and never printed or persisted.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.prepare_soccertrack import DATASET, MATCH_IDS, REVISION


def selected_path(path: str, match_id: str) -> bool:
    """Strictly match one match across both plausible released layouts."""
    path = path.lstrip("/")
    parts = path.split("/")
    if not parts or parts[0] not in {"videos", "gsr", "bas", "ball", "mot", "raw"}:
        return False
    if match_id in parts[1:-1]:
        return True
    basename = parts[-1]
    if basename in (match_id + ".mp4", match_id + ".txt"):
        return True
    if parts[0] == "videos" and basename.startswith(match_id + "_panorama_"):
        return True
    if parts[0] == "gsr" and basename in (match_id + "_1st.json", match_id + "_2nd.json"):
        return True
    if parts[0] == "bas" and basename.startswith(match_id + "_12_class_"):
        return True
    return False


def inventory(files, match_id: str) -> dict:
    if match_id not in MATCH_IDS:
        raise ValueError("ID de match inconnu")
    results = []
    for item in files:
        path = str(getattr(item, "path", "")).lstrip("/")
        if not selected_path(path, match_id):
            continue
        size = getattr(item, "size", None)
        if size is not None and (not isinstance(size, int) or size < 0):
            size = None
        results.append({"path": path, "size_bytes": size})
    results.sort(key=lambda x: x["path"])
    return {
        "dataset": DATASET,
        "revision": REVISION,
        "match_id": match_id,
        "files": results,
        "file_count": len(results),
        "known_total_bytes": sum(row["size_bytes"] or 0 for row in results),
        "unknown_size_file_count": sum(row["size_bytes"] is None for row in results),
        "video_file_count": sum(r["path"].startswith("videos/") for r in results),
        "gsr_file_count": sum(r["path"].startswith("gsr/") for r in results),
        "full_match_downloaded": False,
        "automatic_video_inference_run": False,
        "note": "Remote metadata only; file sizes exclude runtime/cache/model overhead.",
    }


def summarize_mot_rows(rows, *, fps: float = 25.0) -> dict:
    if not 0 < fps <= 120:
        raise ValueError("FPS de référence invalide")
    count, rejected = 0, 0
    first, last = None, None
    frames, tracks = set(), set()
    for row in rows:
        if not row or row[0].strip().startswith("#"):
            continue
        if len(row) < 6:
            rejected += 1
            continue
        try:
            frame, identifier = int(float(row[0])), int(float(row[1]))
            x, y, w, h = (float(v) for v in row[2:6])
            if (frame < 0 or not all(math.isfinite(v) for v in (x, y, w, h))
                    or w <= 0 or h <= 0):
                raise ValueError("bad MOT row")
        except (ValueError, TypeError, OverflowError):
            rejected += 1
            continue
        count += 1
        frames.add(frame)
        tracks.add(identifier)
        first = frame if first is None else min(first, frame)
        last = frame if last is None else max(last, frame)
    return {
        "parsed_box_rows": count,
        "rejected_rows": rejected,
        "unique_annotated_frames": len(frames),
        "unique_reference_track_ids": len(tracks),
        "min_frame": first,
        "max_frame": last,
        "reference_span_seconds_at_25fps": round((last-first+1)/fps, 3)
        if last is not None else None,
        "annotations_are_model_inferences": False,
        "matches_full_90min": bool(last is not None and last-first+1 >= fps*90*60),
        "warning": (
            "MOT metadata are a reference, not a detector benchmark. "
            "This file may cover clips, not the entire match."
        ),
    }


def collect_remote_inventory(client, match_id: str, *, token: str) -> dict:
    files = []
    folders = ("videos", "gsr", "bas", "ball", "mot", "raw")
    for folder in folders:
        # Only list filenames and sizes. No raw file payloads.
        for entry in client.list_repo_tree(
            repo_id=DATASET, repo_type="dataset", revision=REVISION,
            path_in_repo=folder, recursive=True, expand=True, token=token,
        ):
            if getattr(entry, "size", None) is not None:
                files.append(entry)
    result = inventory(files, match_id)
    result["remote_listed_categories"] = list(folders)
    return result


def run(match_id: str, *, download_mot: bool = False,
        client=None, downloader=None, token: str | None = None) -> dict:
    if match_id not in MATCH_IDS:
        raise ValueError("ID de match inconnu")
    token = token or os.environ.get("HF_TOKEN")
    if not token:
        return {
            "status": "NEEDS_AUTHENTICATION", "match_id": match_id,
            "full_match_downloaded": False, "automatic_video_inference_run": False,
        }
    if client is None or (download_mot and downloader is None):
        from huggingface_hub import HfApi, hf_hub_download
        client = client or HfApi()
        downloader = downloader or hf_hub_download
    try:
        result = collect_remote_inventory(client, match_id, token=token)
    except Exception as exc:
        return {
            "status": "INVENTORY_NOT_VERIFIED", "error_type": type(exc).__name__,
            "match_id": match_id, "full_match_downloaded": False,
            "automatic_video_inference_run": False,
        }
    result["status"] = "INVENTORY_VERIFIED"
    if download_mot:
        path = f"mot/{match_id}.txt"
        eligible = next((f for f in result["files"] if f["path"] == path), None)
        if eligible is None or eligible["size_bytes"] is None or eligible["size_bytes"] > 25 * 1024**2:
            result["mot_reference"] = {"status": "NOT_DOWNLOADED", "reason": "missing_or_too_large"}
        else:
            try:
                with TemporaryDirectory(prefix="fpi-one-mot-") as folder:
                    location = downloader(
                        repo_id=DATASET, repo_type="dataset", revision=REVISION,
                        filename=path, token=token, local_dir=folder,
                    )
                    file_path = Path(location)
                    if file_path.stat().st_size > 25 * 1024**2:
                        raise ValueError("MOT file exceeds 25MB")
                    with file_path.open("r", encoding="utf-8-sig", newline="") as stream:
                        ref = summarize_mot_rows(csv.reader(stream))
                result["mot_reference"] = {"status": "PARSED", **ref}
            except Exception as exc:
                result["mot_reference"] = {
                    "status": "NOT_PARSED", "error_type": type(exc).__name__,
                }
    return result


def main() -> None:
    p = argparse.ArgumentParser(description="FPI — inventaire privé SoccerTrack, sans vidéo")
    p.add_argument("--match-id", default="117093", choices=MATCH_IDS)
    p.add_argument("--out", type=Path, default=Path("outputs/soccertrack-117093-inventory.json"))
    p.add_argument("--download-mot", action="store_true",
                   help="Seulement le petit fichier MOT de ce match (<=25 MiB)")
    args = p.parse_args()
    result = run(args.match_id, download_mot=args.download_mot)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("FPI_SOCCERTRACK_INVENTORY=" + result["status"])
    print("FPI_SOCCERTRACK_MOT=" + result.get("mot_reference", {}).get("status", "NOT_REQUESTED"))
    if result["status"] != "INVENTORY_VERIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
