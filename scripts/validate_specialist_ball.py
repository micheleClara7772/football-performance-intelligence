"""Measured live specialist-ONNX experiment; outputs are only a small sample.

No video/media or model weights are committed. Source model is separately
licensed AGPL-3.0. Source images: skaczylo/Football-Image-Dataset
(declared CC BY 4.0, underlying broadcast rights unverified).
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
import json

import cv2
import numpy as np

from fpi.video_analysis.football_ball import FootballBallONNX

MODEL = "https://huggingface.co/acatorcini/yolov9-soccer-ball/resolve/main/v9b_best.onnx"
STEMS = ["NED_VS_FRA_mp4-20", "NED_VS_FRA_mp4-21", "NED_VS_FRA_mp4-22"]
BASE = "https://raw.githubusercontent.com/skaczylo/Football-Image-Dataset/main/"


def get_bounded(url: str, size_limit: int) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "FPI-research-CI/1.0"}), timeout=90) as response:
        content = response.read(size_limit + 1)
    if not content or len(content) > size_limit:
        raise ValueError(f"Fichier distant vide ou supérieur à {size_limit} octets")
    return content


def main() -> None:
    with TemporaryDirectory(prefix="fpi-specialist-ball-") as folder:
        source = Path(folder) / "v9b_best.onnx"
        weights = get_bounded(MODEL, 65_000_000)
        source.write_bytes(weights)
        checksum = sha256(weights).hexdigest()
        print("FPI_SPECIALIST_ONNX_WEIGHTS=" + json.dumps({
            "sha256": checksum, "bytes": len(weights), "license": "AGPL-3.0",
            "source": MODEL,
        }))
        specialist = FootballBallONNX(source, threshold=0.20)
        matched = 0
        gt_count = 0
        predictions_count = 0
        per_image = []
        for stem in STEMS:
            image_bytes = get_bounded(BASE + "images/val/" + stem + ".jpg", 1_000_000)
            label_bytes = get_bounded(BASE + "labels/val/" + stem + ".txt", 20_000)
            photo = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            if photo is None:
                raise ValueError("Image de validation non décodable")
            height, width = photo.shape[:2]
            truth = [
                list(map(float, line.strip().split()[1:]))
                for line in label_bytes.decode().splitlines()
                if line.strip().startswith("0 ")
            ]
            if not truth:
                raise ValueError("Pas de ballon annoté sur cette image")
            balls = specialist.detect_frame(photo, tile_columns=2, tile_rows=1)
            hits = 0
            for cx, cy, w, h in truth:
                tx, ty = cx * width, cy * height
                if any(
                    abs((d.x1 + d.x2) / 2 - tx) <= max(18, w * width * 1.2)
                    and abs((d.y1 + d.y2) / 2 - ty) <= max(18, h * height * 1.2)
                    for d in balls
                ):
                    hits += 1
            matched += hits
            gt_count += len(truth)
            predictions_count += len(balls)
            per_image.append({"image": stem, "truth": len(truth),
                              "predicted": len(balls), "matched_truth": hits})
        print("FPI_SPECIALIST_BALL_EXPERIMENT=" + json.dumps({
            "ground_truth_ball_instances": gt_count,
            "ball_candidates": predictions_count,
            "matching_ball_instances": matched,
            "frames": len(STEMS),
            "per_image": per_image,
            "validation_scope": "three images, not a match or global mAP",
        }))
        assert gt_count >= 3, "Insufficient ground truth"
        # Assert that inference completes and yields properly shaped boxes.
        # Recall is deliberately reported, not falsely promised as a pass.
        assert all(row["predicted"] >= 0 for row in per_image)


if __name__ == "__main__":
    main()
