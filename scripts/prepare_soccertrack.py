"""Prepare ONE authorized SoccerTrack v2 match without checking videos into Git.

This never accepts Hugging Face terms on the user's behalf and never
downloads anything without --download --access-confirmed.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from shutil import disk_usage
import json

DATASET = "atomscott/soccertrack-v2"
REVISION = "v1.2"
MATCH_IDS = ("117092", "117093", "118575", "118576", "118577",
             "118578", "128057", "128058", "132831", "132877")


def plan(match_id: str):
    if match_id not in MATCH_IDS:
        raise ValueError("Match SoccerTrack v2 inconnu")
    return {
        "dataset": DATASET,
        "revision": REVISION,
        "match_id": match_id,
        "halves": ["1st", "2nd"],
        "allow_patterns": [
            f"videos/{match_id}/*",
            f"gsr/{match_id}/*",
            f"bas/{match_id}/*",
            f"ball/{match_id}/*",
        ],
        "requires_account_agreement": True,
        "automatic_rights_acceptance": False,
        "notes": [
            "Only this match's paths are selected, not the 145 GB dataset.",
            "GSR JSON can exceed 2 GB per half: use streaming JSON readers.",
            "Video frames, GSR and ball-event timing are matched in v1.2 per half.",
            "GSR does not provide independently verified image-space ball boxes.",
        ],
    }


def main():
    p = argparse.ArgumentParser(description="FPI — préparer un match SoccerTrack v2")
    p.add_argument("--match-id", choices=MATCH_IDS, default="117093")
    p.add_argument("--out-dir", type=Path, default=Path("data/raw/soccertrack-v2"))
    p.add_argument("--download", action="store_true")
    p.add_argument("--access-confirmed", action="store_true",
                   help="J'ai accepté les conditions du dataset sur Hugging Face")
    args = p.parse_args()
    selection = plan(args.match_id)
    print(json.dumps(selection, indent=2, ensure_ascii=False))
    if not args.download:
        print("FPI_DATASET_PRECHECK=NO_DOWNLOAD (dry run)")
        return
    if not args.access_confirmed:
        p.error("--access-confirmed est indispensable après acceptation sur Hugging Face")
    free = disk_usage(args.out_dir.resolve().anchor).free
    if free < 8 * 1024**3:
        p.error("Espace libre < 8 GiB : choisir un espace privé adapté aux vidéos 4K")
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit("Installer huggingface_hub dans l'environnement isolé") from exc
    args.out_dir.mkdir(parents=True, exist_ok=True)
    try:
        location = snapshot_download(
            repo_id=DATASET,
            repo_type="dataset",
            revision=REVISION,
            local_dir=str(args.out_dir),
            allow_patterns=selection["allow_patterns"],
        )
    except Exception as exc:
        # Never print full connector URLs, access tokens or credentials.
        raise SystemExit(
            "Téléchargement refusé ou interrompu. Vérifier l'accès Hugging Face, "
            "les permissions, l'espace disque et la disponibilité de v1.2. "
            f"Type d'erreur : {type(exc).__name__}"
        ) from None
    base = Path(location)
    files = [p for folder in ("videos", "gsr", "ball", "bas")
             for p in (base / folder / args.match_id).rglob("*") if p.is_file()]
    print(json.dumps({
        "status": "download_completed_not_validated",
        "dataset": DATASET,
        "match_id": args.match_id,
        "files": len(files),
        "bytes": sum(p.stat().st_size for p in files),
        "local_directory": str(base),
        "notice": "No inference or quality benchmark has been performed by this command.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
