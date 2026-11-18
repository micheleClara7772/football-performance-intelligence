"""Check access to gated SoccerTrack v2 with an ephemeral tiny file.

This is an AUTHORIZATION preflight, not a full-match download or model test.
Never log or return the token, username, account details or raw HTTP errors.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

DATASET = "atomscott/soccertrack-v2"
REVISION = "v1.2"
SMALL_FILE = "mot/README.md"


def check_access(token: str | None = None, downloader=None) -> dict:
    """Force a fresh authenticated small-file fetch to prove actual file access."""
    if token is None:
        token = os.environ.get("HF_TOKEN") or None
        if token is None:
            try:
                from huggingface_hub import get_token
                token = get_token()
            except ImportError:
                pass
    if not token:
        return {
            "status": "NEEDS_AUTHENTICATION",
            "dataset": DATASET,
            "verified_file_access": False,
            "note": "Attach a read-only HF_TOKEN in GitHub Actions or log in in a private Codespace.",
        }
    if downloader is None:
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            return {
                "status": "DEPENDENCY_MISSING",
                "dataset": DATASET,
                "verified_file_access": False,
            }
        downloader = hf_hub_download
    try:
        with TemporaryDirectory(prefix="fpi-hf-access-") as temp:
            p = downloader(
                repo_id=DATASET,
                repo_type="dataset",
                revision=REVISION,
                filename=SMALL_FILE,
                token=token,
                force_download=True,
                local_dir=temp,
            )
            file_path = Path(p)
            if not file_path.is_file() or file_path.stat().st_size == 0:
                raise ValueError("Empty access proof")
    except Exception:
        # The exception may contain private URL headers and other credentials;
        # intentionally keep it out of logs and artifacts.
        return {
            "status": "ACCESS_NOT_VERIFIED",
            "dataset": DATASET,
            "verified_file_access": False,
            "note": "Gated access, network, file availability or token scope may be blocking.",
        }
    return {
        "status": "ACCESS_VERIFIED",
        "dataset": DATASET,
        "revision": REVISION,
        "verified_file_access": True,
        "proof_file": SMALL_FILE,
        "full_match_downloaded": False,
        "full_match_inference_validated": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="FPI — vérifier accès HF sans vidéo")
    parser.add_argument("--out", type=Path, default=Path("outputs/soccertrack-access.json"))
    parser.add_argument("--strict", action="store_true",
                        help="Exit nonzero unless authenticated gated file access is verified")
    args = parser.parse_args()
    result = check_access()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FPI_SOCCERTRACK_ACCESS=" + result["status"])
    if args.strict and not result["verified_file_access"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
