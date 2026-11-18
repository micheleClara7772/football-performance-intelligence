"""End-to-end full-DURATION seek/coverage test on ORIGINAL synthetic footage.

This validates timestamps, decoding and 90+ minute processing, NOT real
model precision on a whole football match. Real YOLOX inference on licensed
football frames is validated separately in validate_video_model.py.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess

from fpi.video_analysis.detector import Detection
from fpi.video_analysis.pipeline import analyze_video


class ControlledInference:
    """Deterministic bounding boxes to isolate long-duration video I/O."""

    def detect_frame(self, frame, **kwargs):
        return [
            Detection("joueur_candidat", 0.9, 30, 20, 50, 90),
            Detection("ballon_candidat", 0.9, 70, 40, 78, 48),
        ]


def main():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg requis pour générer le test 92 minutes")
    with TemporaryDirectory(prefix="fpi-full-duration-") as temp:
        path = Path(temp) / "original-green-pitch.mp4"
        subprocess.run(
            [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "lavfi", "-i", "color=c=green:s=320x180:r=1",
             "-t", "5520", "-an", "-c:v", "libx264", "-preset", "ultrafast",
             "-crf", "46", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
             str(path)],
            check=True, timeout=120, capture_output=True,
        )
        summary, previews = analyze_video(
            path, ControlledInference(), sample_interval_seconds=300,
            max_frames=0, preview_limit=0, tile_columns=1, tile_rows=1,
        )
        times = [row["time_seconds"] for row in summary.per_frame]
        assert summary.duration_seconds >= 5500, summary.duration_seconds
        assert summary.sampled_frames == 19, times
        assert times[0] == 0.0
        assert times[-1] >= 5400, times
        assert times == sorted(set(times))
        assert summary.frames_with_people == summary.sampled_frames
        assert summary.frames_with_ball_candidates == summary.sampled_frames
        assert not previews
        print("FPI_FULL_DURATION_IO=PASS "+json.dumps({
            "synthetic_video_duration_seconds": summary.duration_seconds,
            "sampled_frames": summary.sampled_frames,
            "last_sample_second": summary.covered_until_seconds,
            "actual_model_inference": False,
            "real_match_validation": False,
        }))


if __name__ == "__main__":
    main()
