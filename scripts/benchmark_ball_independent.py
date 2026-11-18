"""Quantitative ball-detection benchmark on 100 independently labelled football images.

GT: skaczylo/Football-Image-Dataset, val split: YOLO class 0 = ball.
Do not mistake 100 still images for a 90-minute video validation.
Weights/images remain in an ephemeral runner; only summary and 4 small
CC BY 4.0 attribution-bearing proof thumbnails can be archived privately.
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path
from time import perf_counter

import cv2
from huggingface_hub import hf_hub_download

from fpi.video_analysis.detector import YOLOXDetector, download_model
from fpi.video_analysis.football_ball import FootballBallONNX
from scripts.evaluate_video_detections import evaluate

DATASET = "skaczylo/Football-Image-Dataset"
CITATION = "https://github.com/skaczylo/Football-Image-Dataset"
BALL_MODEL = "acatorcini/yolov9-soccer-ball"
BALL_WEIGHT = "v9b_best.onnx"


def parse_yolo_ball_annotations(text: str, width: int, height: int) -> list[dict]:
    if width < 64 or height < 64:
        raise ValueError("Dimensions invalides")
    balls = []
    for row in text.splitlines():
        tokens = row.strip().split()
        if not tokens:
            continue
        if len(tokens) < 5:
            raise ValueError("Ligne YOLO tronquée")
        if tokens[0] not in ("0", "1", "2"):
            raise ValueError("Classe YOLO inconnue")
        if tokens[0] != "0":
            continue
        x, y, w, h = map(float, tokens[1:5])
        if not all(map(math.isfinite, (x,y,w,h))) or not all(
            0 <= z <= 1 for z in (x,y,w,h)
        ) or w <= 0 or h <= 0:
            raise ValueError("Boîte YOLO invalide")
        box = [
            max(0.0, (x-w/2)*width), max(0.0, (y-h/2)*height),
            min(float(width), (x+w/2)*width),
            min(float(height), (y+h/2)*height),
        ]
        if box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError("Boîte vide")
        balls.append({"label": "ball", "bbox_xyxy": box})
    return balls


def _thumbnail(image, truth, yolox, specialist):
    """Display model boxes and reference boxes on copies of a licensed still."""
    canvas = image.copy()
    h, w = canvas.shape[:2]
    for name, objects, color in (
        ("GT", truth, (0, 200, 0)),
        ("YOLOX", yolox, (20, 20, 250)),
        ("YOLOv9", specialist, (250, 120, 20)),
    ):
        for d in objects:
            xyxy = d["bbox_xyxy"]
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
            cv2.putText(canvas, name, (x1, max(14, y1-3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    new_w = min(w, 960)
    resized = cv2.resize(canvas, (new_w, max(1, int(h*new_w/w))))
    cv2.putText(resized, "CC BY 4.0 skaczylo / Football-Image-Dataset",
                (8, resized.shape[0]-8), cv2.FONT_HERSHEY_SIMPLEX,
                0.40, (245,245,245), 2)
    return resized


def benchmark(root: Path, *, proof_dir: Path | None = None,
              max_images: int = 100, iou: float = 0.30) -> dict:
    if not 1 <= max_images <= 100 or not 0 < iou <= 1:
        raise ValueError("Sélection invalide")
    imgs = root / "images" / "val"
    labels = root / "labels" / "val"
    filenames = sorted(imgs.glob("*.jpg"))[:max_images]
    if not filenames:
        raise ValueError("Aucune image de validation disponible")
    if any(not (labels / (p.stem + ".txt")).is_file() for p in filenames):
        raise ValueError("Il manque des annotations indépendantes")
    with tempfile.TemporaryDirectory(prefix="fpi-independent-balls-") as temp:
        weights = Path(temp)
        yolox = YOLOXDetector(download_model(weights / "yolox"))
        model_file = hf_hub_download(
            repo_id=BALL_MODEL, filename=BALL_WEIGHT,
            local_dir=str(weights / "specialist"),
        )
        specialist = FootballBallONNX(Path(model_file), threshold=0.20)
        predictions = {"YOLOX": {"frames": []}, "YOLOv9": {"frames": []}}
        gt = {"frames": []}
        runtimes = {"YOLOX": 0.0, "YOLOv9": 0.0}
        sample_visuals = 0
        labels_found = 0
        for index, photo in enumerate(filenames):
            frame = cv2.imread(str(photo))
            if frame is None:
                raise ValueError("Image JPEG illisible")
            height, width = frame.shape[:2]
            truth = parse_yolo_ball_annotations(
                (labels / (photo.stem + ".txt")).read_text(encoding="utf-8"),
                width, height,
            )
            labels_found += len(truth)
            gt["frames"].append({"time_seconds": float(index), "objects": truth})
            start = perf_counter()
            a = [d.to_dict() for d in yolox.detect_frame(
                frame, tile_columns=4, tile_rows=3,
                ball_threshold=0.08) if d.label == "ballon_candidat"]
            runtimes["YOLOX"] += perf_counter() - start
            start = perf_counter()
            b = [d.to_dict() for d in specialist.detect_frame(
                frame, tile_columns=2, tile_rows=1)
                if d.label == "ballon_candidat"]
            runtimes["YOLOv9"] += perf_counter() - start
            predictions["YOLOX"]["frames"].append(
                {"time_seconds": float(index), "detections": a})
            predictions["YOLOv9"]["frames"].append(
                {"time_seconds": float(index), "detections": b})
            if proof_dir is not None and sample_visuals < 4 and truth:
                proof_dir.mkdir(parents=True, exist_ok=True)
                preview = _thumbnail(frame, truth, a, b)
                if not cv2.imwrite(str(proof_dir / f"ball-example-{index:03d}.jpg"), preview):
                    raise RuntimeError("Impossible de sauvegarder la vignette CC BY")
                sample_visuals += 1
        if labels_found < 30:
            raise ValueError("Pas assez de ballons GT pour benchmark")
        comparison = {}
        for model, outputs in predictions.items():
            result = evaluate(outputs, gt, iou_threshold=iou,
                              tolerance_seconds=0.01)
            comparison[model] = {
                "metrics": result["metrics"]["ball"],
                "real_cpu_inference_seconds": round(runtimes[model], 2),
                "milliseconds_per_frame": round(1000*runtimes[model]/len(filenames), 1),
                "predicted_ball_boxes": sum(len(f["detections"]) for f in outputs["frames"]),
            }
        a, b = comparison["YOLOX"]["metrics"], comparison["YOLOv9"]["metrics"]
        winner = None
        if a["f1"] is not None and b["f1"] is not None:
            if a["f1"] != b["f1"]:
                winner = "YOLOX" if a["f1"] > b["f1"] else "YOLOv9"
            else:
                winner = "tie"
        return {
            "validation_type": "independent_still_image_ball_boxes",
            "provenance": DATASET, "citation": CITATION,
            "declared_license": "CC BY 4.0; underlying broadcast rights require verification",
            "images_evaluated": len(filenames),
            "annotated_ball_boxes": labels_found,
            "iou_threshold": iou,
            "ball_detection_results": comparison,
            "provisional_ball_model_winner": winner,
            "real_match_90min_validated": False,
            "tracking_quality_validated": False,
            "notes": [
                "Held-out still images only: these are not SoccerTrack match video frames.",
                "False positives include predictions on ball-negative images.",
                "Model selection on this set must be confirmed on separate match footage.",
                "YOLOv9 model weights remain AGPL-3.0; no model redistributed.",
            ],
        }


def main():
    p = argparse.ArgumentParser(description="FPI — vraie comparaison de ballons sur 100 images")
    p.add_argument("--dataset-root", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("outputs/ball-comparison.json"))
    p.add_argument("--proof-dir", type=Path)
    p.add_argument("--max-images", type=int, default=100)
    args = p.parse_args()
    report = benchmark(args.dataset_root, max_images=args.max_images,
                       proof_dir=args.proof_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print("FPI_REAL_BALL_BENCHMARK=" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
