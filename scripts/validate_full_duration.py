"""End-to-end full-DURATION seek/coverage test on ORIGINAL synthetic footage.

This validates timestamps, decoding and 90+ minute processing, NOT real
model precision on a whole football match. Real YOLOX inference on licensed
football frames is validated separately in validate_video_model.py.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import cv2
import numpy as np

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
    with TemporaryDirectory(prefix="fpi-full-duration-") as temp:
        path = Path(temp) / "original-green-pitch.avi"
        writer = cv2.VideoWriter(
            str(path), cv2.VideoWriter_fourcc(*"MJPG"), 1, (160, 120),
        )
        if not writer.isOpened():
            raise RuntimeError("Codec AVI/MJPEG OpenCV indisponible")
        try:
            frame = np.zeros((120, 160, 3), dtype=np.uint8)
            frame[:, :, 1] = 130
            # 5520 frames at 1 fps => 92 minutes. A watermark changes
            # regularly to ensure frames are actually encoded/decoded.
            for index in range(5520):
                cv2.rectangle(frame, (0, 0), (60, 20), (0, 130, 0), -1)
                cv2.putText(frame, str(index // 120), (2, 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                writer.write(frame)
        finally:
            writer.release()
        summary, previews = analyze_video(
            path, ControlledInference(), sample_interval_seconds=120,
            max_frames=0, preview_limit=0, tile_columns=1, tile_rows=1,
        )
        times = [row["time_seconds"] for row in summary.per_frame]
        assert summary.duration_seconds >= 5500, summary.duration_seconds
        assert summary.sampled_frames == 46, times
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
