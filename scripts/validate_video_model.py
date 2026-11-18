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
    # Independent sports-ball test on a visible football photo. The panoramic
    # match demo has a ball only a few pixels wide and may yield zero ball boxes.
    # Credit: Photospook, "Soccer Ball about to be kicked", CC BY-SA 4.0.
    import cv2
    import numpy as np
    from fpi.video_analysis.pipeline import render_preview

    ball_photo_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/"
        "Soccer_Ball_about_to_be_kicked.JPG/"
        "1280px-Soccer_Ball_about_to_be_kicked.JPG"
    )
    req = Request(ball_photo_url, headers={
        "User-Agent": "FPI-CV-validation/1.0 (CC-BY-SA attributed, non-commercial test)"
    })
    with urlopen(req, timeout=45) as response:
        content = response.read(2_000_000)
    photo = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if photo is None:
        raise AssertionError("Could not decode the free-licensed football photograph")
    ball_detections = model.detect_frame(
        photo, tile_columns=2, tile_rows=2, ball_threshold=0.10,
    )
    actual_balls = [d for d in ball_detections if d.label == "ballon_candidat"]
    assert actual_balls, (
        "No real sports-ball candidate found on the visible-ball CC-BY-SA photo"
    )
    (target / "ccby-sa-visible-ball.jpg").write_bytes(
        render_preview(photo, ball_detections)
    )
    print("FPI_REAL_BALL_IMAGE=PASS " + json.dumps({
        "source": "Photospook / Wikimedia Commons CC BY-SA 4.0",
        "sports_ball_candidates": len(actual_balls),
        "confidence_max": round(max(d.confidence for d in actual_balls), 4),
    }))
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
