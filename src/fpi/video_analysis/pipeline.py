"""Video sampling and inference: source footage remains local and is never exported."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import math

import numpy as np

from .detector import Detection


@dataclass(frozen=True)
class VideoSummary:
    source: str
    duration_seconds: float
    width: int
    height: int
    estimated_fps: float
    sampled_frames: int
    interval_seconds: float
    covered_until_seconds: float
    frames_with_people: int
    frames_with_ball_candidates: int
    person_candidates_total: int
    ball_candidates_total: int
    per_frame: tuple[dict, ...]

    def to_dict(self) -> dict:
        return {
            "analysis_type": "video_inference_sampled_not_tracking",
            "source": self.source,
            "duration_seconds": round(self.duration_seconds, 2),
            "width": self.width, "height": self.height,
            "estimated_fps": round(self.estimated_fps, 3),
            "sampled_frames": self.sampled_frames,
            "sample_interval_seconds": self.interval_seconds,
            "covered_until_seconds": round(self.covered_until_seconds, 2),
            "frames_with_people": self.frames_with_people,
            "frames_with_ball_candidates": self.frames_with_ball_candidates,
            "person_candidates_total": self.person_candidates_total,
            "ball_candidates_total": self.ball_candidates_total,
            "frames": list(self.per_frame),
            "limitations": [
                "COCO person includes referees, coaches and audience; not automatic team identity.",
                "COCO sports ball detection may miss a small ball; absence is not proof of no ball.",
                "No player identity tracking, formation, speed, distances or possession inferred.",
                "Only sampled frames were analyzed, not every pixel of every video frame.",
                "Video timestamps are not automatically synchronized to StatsBomb.",
            ],
        }


def _sample_times(duration: float, interval: float, max_frames: int) -> list[float]:
    if not math.isfinite(interval) or not 0.2 <= interval <= 120:
        raise ValueError("Échantillonnage attendu entre 0,2 et 120 secondes")
    if max_frames < 0 or max_frames > 5000:
        raise ValueError("Nombre de frames supérieur à la limite de sécurité")
    if not 0.0 < duration <= 4 * 60 * 60:
        raise ValueError("Vidéo invalide ou trop longue (maximum 4 heures)")
    count = max(1, math.ceil(duration / interval))
    if max_frames and count > max_frames:
        # Sampling the entire duration, not just the first minutes.
        return [float(x) for x in np.linspace(0, max(0, duration - interval), max_frames)]
    return [float(i * interval) for i in range(count)]


def render_preview(frame: np.ndarray, detections: list[Detection]) -> bytes:
    import cv2
    canvas = frame.copy()
    for d in detections:
        color = (42, 204, 42) if d.label == "joueur_candidat" else (40, 165, 255)
        cv2.rectangle(canvas, (d.x1, d.y1), (d.x2, d.y2), color, 2)
        cv2.putText(
            canvas, ("person" if d.label == "joueur_candidat" else "sports ball")
            + f" {d.confidence:.2f}",
            (d.x1, max(12, d.y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1,
        )
    # Prevent huge preview in app, original full match footage never exported.
    scale = min(1, 1000 / max(canvas.shape[:2]))
    if scale < 1:
        canvas = cv2.resize(canvas, None, fx=scale, fy=scale)
    ok, encoded = cv2.imencode(".jpg", canvas, [cv2.IMWRITE_JPEG_QUALITY, 78])
    if not ok:
        raise ValueError("Impossible de créer l'aperçu des détections")
    return encoded.tobytes()


def analyze_video(
    path: Path,
    detector,
    *,
    sample_interval_seconds: float = 15.0,
    max_frames: int = 0,
    preview_limit: int = 3,
    tile_columns: int = 2,
    tile_rows: int = 2,
    progress: Callable[[int, int], None] | None = None,
) -> tuple[VideoSummary, list[tuple[float, bytes]]]:
    """Sample across the full timeline and run *real* detector on decoded frames."""
    import cv2

    path = Path(path)
    if path.suffix.lower() not in (".mp4", ".mov", ".mkv", ".avi", ".webm"):
        raise ValueError("Formats autorisés : MP4, MOV, MKV, AVI ou WebM")
    if not path.is_file():
        raise ValueError("Le fichier vidéo n'existe pas")
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError("OpenCV ne peut pas ouvrir cette vidéo")
    try:
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        num_frames = float(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not (math.isfinite(fps) and 0 < fps <= 240 and math.isfinite(num_frames) and num_frames > 0):
            raise ValueError("Métadonnées FPS/durée illisibles")
        if width < 64 or height < 64 or width > 8192 or height > 8192:
            raise ValueError("Résolution vidéo non prise en charge")
        duration = num_frames / fps
        times = _sample_times(duration, sample_interval_seconds, max_frames)
        frames = []
        previews = []
        people_frames = ball_frames = people_total = ball_total = 0
        for index, requested_time in enumerate(times):
            capture.set(cv2.CAP_PROP_POS_MSEC, requested_time * 1000)
            ok, frame = capture.read()
            if not ok or frame is None:
                continue
            detections = detector.detect_frame(
                frame, tile_columns=tile_columns, tile_rows=tile_rows,
            )
            count_people = sum(d.label == "joueur_candidat" for d in detections)
            count_balls = sum(d.label == "ballon_candidat" for d in detections)
            people_total += count_people
            ball_total += count_balls
            people_frames += bool(count_people)
            ball_frames += bool(count_balls)
            frames.append({
                "time_seconds": round(requested_time, 2),
                "person_candidates": count_people,
                "sports_ball_candidates": count_balls,
                "detections": [d.to_dict() for d in detections],
            })
            if len(previews) < preview_limit:
                previews.append((requested_time, render_preview(frame, detections)))
            if progress:
                progress(index + 1, len(times))
        if not frames:
            raise ValueError("Aucune frame décodable aux instants demandés")
        return (
            VideoSummary(
                path.name, duration, width, height, fps, len(frames),
                sample_interval_seconds, max(x["time_seconds"] for x in frames),
                people_frames, ball_frames, people_total, ball_total,
                tuple(frames),
            ),
            previews,
        )
    finally:
        capture.release()
