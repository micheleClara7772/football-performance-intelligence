"""No-upload video demo: exact provenance and metric integrity."""
import json
from pathlib import Path
import pytest

from fpi.ui.video_showcase import (
    read_verified_demo_report,
    video_is_ready,
)


def _realistic_report():
    return {
        "source_match_id": "117093",
        "clip_seconds": 12.0,
        "processed_frames": 60,
        "processed_fps": 5.0,
        "full_match_90min_tracking_validated": False,
        "ball_tracking_accuracy_validated": False,
        "mot_identity_benchmark": {
            "frames_evaluated": 60,
            "idf1": 0.6299,
            "box_precision": 0.8716,
            "box_recall": 0.6379,
            "id_switches": 10,
            "mot_gt_box_count": 1320,
        },
    }


def test_missing_report_does_not_invent_video_metrics(tmp_path):
    assert read_verified_demo_report(tmp_path / "missing.json") is None
    assert video_is_ready(tmp_path / "missing.mp4", tmp_path / "missing.json") is False


def test_valid_bundled_video_metadata(tmp_path):
    path = tmp_path / "report.json"
    path.write_text(json.dumps(_realistic_report()), encoding="utf-8")
    assert read_verified_demo_report(path)["mot_identity_benchmark"]["idf1"] == 0.6299
    (tmp_path / "real-video.mp4").write_bytes(b"x" * 120_000)
    assert video_is_ready(tmp_path / "real-video.mp4", path)


def test_forbid_fabricated_full_match_claim_and_ball_validation(tmp_path):
    report = _realistic_report()
    for field in ("full_match_90min_tracking_validated",
                  "ball_tracking_accuracy_validated"):
        broken = dict(report, **{field: True})
        file = tmp_path / (field + ".json")
        file.write_text(json.dumps(broken), encoding="utf-8")
        assert read_verified_demo_report(file) is None


def test_reject_unrelated_match_or_corrupt_json(tmp_path):
    source = _realistic_report()
    source["source_match_id"] = "3869486"
    p = tmp_path / "improper.json"
    p.write_text(json.dumps(source), encoding="utf-8")
    assert read_verified_demo_report(p) is None
    p.write_text("{broken", encoding="utf-8")
    assert read_verified_demo_report(p) is None
