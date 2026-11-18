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
    # Independent ball evaluation on genuine football frames with YOLO labels.
    # Attribution: skaczylo / Football Image Dataset, declared CC BY 4.0.
    # Derived labels may be re-used under CC BY; originals remain ephemeral.
    import cv2
    import numpy as np

    ball_sources = [
        "NED_VS_FRA_mp4-20",
        "NED_VS_FRA_mp4-21",
        "NED_VS_FRA_mp4-22",
    ]
    matches = 0
    candidate_count = 0
    sources_used = 0
    for stem in ball_sources:
        base = "https://raw.githubusercontent.com/skaczylo/Football-Image-Dataset/main/"
        photo_req = Request(base + "images/val/" + stem + ".jpg",
                            headers={"User-Agent": "FPI research CI/1.0"})
        label_req = Request(base + "labels/val/" + stem + ".txt",
                            headers={"User-Agent": "FPI research CI/1.0"})
        with urlopen(photo_req, timeout=45) as response:
            content = response.read(1_000_000)
        with urlopen(label_req, timeout=45) as response:
            labels = response.read(20_000).decode("utf-8")
        photo = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
        if photo is None:
            raise AssertionError("A football validation image could not be decoded")
        height, width = photo.shape[:2]
        ground_truth = [
            [float(v) for v in line.split()[1:]]
            for line in labels.splitlines()
            if line.strip().startswith("0 ")
        ]
        assert ground_truth, "This image is supposed to have a labelled ball"
        guesses = model.detect_frame(
            photo, tile_columns=4, tile_rows=3, ball_threshold=0.08,
        )
        balls = [d for d in guesses if d.label == "ballon_candidat"]
        candidate_count += len(balls)
        sources_used += 1
        # Compare centers to manual labels, not merely presence of boxes.
        for gx, gy, gw, gh in ground_truth:
            gt_x, gt_y = gx * width, gy * height
            if any(
                abs((d.x1 + d.x2) / 2 - gt_x) <= max(gw * width * 1.2, 18)
                and abs((d.y1 + d.y2) / 2 - gt_y) <= max(gh * height * 1.2, 18)
                for d in balls
            ):
                matches += 1
    print("FPI_REAL_BALL_EVALUATION=" + json.dumps({
        "dataset": "skaczylo/Football-Image-Dataset (CC BY 4.0 claimed)",
        "images": sources_used,
        "ball_candidates": candidate_count,
        "ground_truth_matches": matches,
    }))
    assert matches >= 1, (
        "The base YOLOX model did not localize any labelled soccer ball "
        "in three true football frames; ball detection needs improvement"
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
