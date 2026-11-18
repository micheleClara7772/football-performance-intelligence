"""Inférence YOLOX réelle sur un exemple vidéo SoccerTrack v2 réutilisable CC BY.

Échantillon public : AtomScott/SoccerTrack-v2 docs/assets/demo-tracking.mp4.
Vidéo chargée dans un runner éphémère, supprimée après le test.
"""
from pathlib import Path
import json
import os
from urllib.request import Request, urlopen

from fpi.video_analysis.detector import YOLOXDetector, download_model
from fpi.video_analysis.pipeline import analyze_video

CLIP = "https://raw.githubusercontent.com/AtomScott/SoccerTrack-v2/main/docs/assets/demo-tracking.mp4"


def main():
    target = Path(os.environ.get("FPI_CV_PROOF_DIR", "outputs/video-proof"))
    target.mkdir(parents=True, exist_ok=True)
    video = target / "soccertrack-source.mp4"
    req = Request(CLIP, headers={"User-Agent": "FPI CC-BY test runner"})
    with urlopen(req, timeout=45) as response, video.open("wb") as handle:
        size = 0
        while True:
            chunk = response.read(128 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > 8_000_000:
                raise ValueError("CC-BY clip exceeded bounded download limit")
            handle.write(chunk)
    model = YOLOXDetector(download_model(target / "models"))
    summary, previews = analyze_video(
        video, model, sample_interval_seconds=1.0, max_frames=18,
        preview_limit=3, tile_columns=2, tile_rows=2,
    )
    assert summary.sampled_frames >= 3, "No valid video frames decoded"
    assert summary.frames_with_people > 0, (
        "The real ONNX detector failed to find people on the soccer test footage"
    )
    for i, (_, image) in enumerate(previews):
        (target / f"ccby-detection-{i:02d}.jpg").write_bytes(image)
    (target / "soccertrack-real-inference.json").write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    video.unlink(missing_ok=True)
    print("FPI_REAL_VIDEO_MODEL=PASS "+json.dumps({
        "source": "SoccerTrack-v2 demo tracking, CC BY 4.0",
        "frames": summary.sampled_frames,
        "frames_with_people": summary.frames_with_people,
        "frames_with_ball_candidates": summary.frames_with_ball_candidates,
        "person_boxes": summary.person_candidates_total,
        "ball_boxes": summary.ball_candidates_total,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
