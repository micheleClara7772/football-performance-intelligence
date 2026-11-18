"""Optional soccer-specific ball detection with ONNX Runtime (no paid API).

Compatible with the separately licensed acatorcini/yolov9-soccer-ball
ONNX export (single class, output [1, 5, N]). The optional checkpoint is
AGPL-3.0: a model's license is NOT changed by exporting to ONNX.
Never download or redistribute weights silently. Supply a local ONNX file.
"""
from __future__ import annotations

from pathlib import Path
import math

import numpy as np

from .detector import Detection, _regions


class FootballBallONNX:
    """High-resolution football-ball detector for panorama/broadcast samples.

    Only the object-detection output is used. No ball trajectory, possession,
    stable identity, team affiliation or tactical event is inferred.
    """

    def __init__(self, path: Path, *, threshold: float = 0.20):
        if not 0 < threshold <= 1:
            raise ValueError("Seuil de confiance ballon invalide")
        path = Path(path)
        if not path.is_file() or path.suffix.lower() != ".onnx":
            raise ValueError("Fichier de poids ONNX ballon absent ou invalide")
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise RuntimeError("onnxruntime requis pour le modèle de ballon") from exc
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        opts.inter_op_num_threads = 1
        self.session = ort.InferenceSession(
            str(path), sess_options=opts, providers=["CPUExecutionProvider"],
        )
        inp = self.session.get_inputs()[0]
        self.input_name = inp.name
        dims = inp.shape
        if len(dims) != 4 or dims[1] != 3 or not (
            isinstance(dims[2], int) and isinstance(dims[3], int)
            and 320 <= dims[2] <= 1920 and 320 <= dims[3] <= 1920
        ):
            raise ValueError(f"Entrée ONNX ballon non prise en charge : {dims}")
        self.height, self.width = int(dims[2]), int(dims[3])
        self.threshold = threshold

    @staticmethod
    def _predictions(raw: np.ndarray) -> np.ndarray:
        """Accept [1,5,N] or [1,N,5], and reject invalid output schemas."""
        if not isinstance(raw, np.ndarray) or raw.ndim != 3 or raw.shape[0] != 1:
            raise ValueError("Sortie ONNX ballon inattendue")
        data = raw[0]
        if data.shape[0] == 5 and data.shape[1] != 5:
            data = data.T
        if data.shape[1] != 5:
            raise ValueError(f"Sortie ONNX ballon incompatible : {raw.shape}")
        return data

    def _detect_tile(self, tile: np.ndarray, offset: tuple[int, int]) -> list[Detection]:
        import cv2

        src_h, src_w = tile.shape[:2]
        ratio = min(self.width / src_w, self.height / src_h)
        scaled_w = max(1, min(self.width, round(src_w * ratio)))
        scaled_h = max(1, min(self.height, round(src_h * ratio)))
        resized = cv2.resize(tile, (scaled_w, scaled_h), interpolation=cv2.INTER_LINEAR)
        pad_x = (self.width - scaled_w) // 2
        pad_y = (self.height - scaled_h) // 2
        canvas = np.full((self.height, self.width, 3), 114, dtype=np.uint8)
        canvas[pad_y:pad_y + scaled_h, pad_x:pad_x + scaled_w] = resized
        # Ultralytics ONNX: RGB, float [0..1], NCHW, centred letterbox.
        inp = np.ascontiguousarray(
            canvas[:, :, ::-1].transpose(2, 0, 1)[None], dtype=np.float32,
        ) / 255.0
        outputs = self.session.run(None, {self.input_name: inp})
        if not outputs:
            raise ValueError("Aucune sortie produite par le modèle ballon")
        boxes = self._predictions(outputs[0])
        scores = boxes[:, 4]
        indices = np.flatnonzero(np.isfinite(boxes).all(axis=1) & (scores >= self.threshold))
        if indices.size == 0:
            return []
        # Avoid memory and NMS blow-up from huge low-confidence output maps.
        if indices.size > 1500:
            best = np.argpartition(scores[indices], -1500)[-1500:]
            indices = indices[best]
        xywh = boxes[indices, :4].astype(np.float64, copy=True)
        xywh[:, 0] = (xywh[:, 0] - pad_x) / ratio
        xywh[:, 1] = (xywh[:, 1] - pad_y) / ratio
        xywh[:, 2:] /= ratio
        corners = np.column_stack([
            xywh[:, 0] - xywh[:, 2] / 2,
            xywh[:, 1] - xywh[:, 3] / 2,
            xywh[:, 0] + xywh[:, 2] / 2,
            xywh[:, 1] + xywh[:, 3] / 2,
        ])
        candidate_rects, candidate_scores, candidate_boxes = [], [], []
        for box, confidence in zip(corners, scores[indices]):
            x1 = int(np.clip(box[0], 0, src_w - 1))
            y1 = int(np.clip(box[1], 0, src_h - 1))
            x2 = int(np.clip(box[2], 0, src_w))
            y2 = int(np.clip(box[3], 0, src_h))
            if x2 <= x1 or y2 <= y1:
                continue
            candidate_rects.append([x1, y1, x2 - x1, y2 - y1])
            candidate_scores.append(float(confidence))
            candidate_boxes.append((x1, y1, x2, y2))
        if not candidate_rects:
            return []
        retained = cv2.dnn.NMSBoxes(candidate_rects, candidate_scores, self.threshold, 0.45)
        return [
            Detection(
                "ballon_candidat", candidate_scores[int(j)],
                candidate_boxes[int(j)][0] + offset[0],
                candidate_boxes[int(j)][1] + offset[1],
                candidate_boxes[int(j)][2] + offset[0],
                candidate_boxes[int(j)][3] + offset[1],
            )
            for j in np.asarray(retained, dtype=int).reshape(-1)
        ]

    def detect_frame(self, frame_bgr: np.ndarray, *, tile_columns: int = 2,
                     tile_rows: int = 1) -> list[Detection]:
        import cv2
        if not isinstance(frame_bgr, np.ndarray) or frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
            raise ValueError("Image BGR illisible pour détecteur ballon")
        h, w = frame_bgr.shape[:2]
        if min(h, w) < 32 or max(h, w) > 8192:
            raise ValueError("Dimensions vidéo hors limites")
        found = []
        for x1, y1, x2, y2 in _regions(w, h, tile_columns, tile_rows):
            found.extend(self._detect_tile(frame_bgr[y1:y2, x1:x2], (x1, y1)))
        if not found:
            return []
        boxes = [[d.x1, d.y1, d.x2 - d.x1, d.y2 - d.y1] for d in found]
        kept = cv2.dnn.NMSBoxes(boxes, [d.confidence for d in found], self.threshold, 0.45)
        return sorted(
            (found[int(j)] for j in np.asarray(kept, dtype=int).reshape(-1)),
            key=lambda d: -d.confidence,
        )


class HybridFootballDetector:
    """Use YOLOX for people and specialist ONNX for the ball.

    Crucially, do not add generic COCO ball boxes to specialist predictions:
    these would inflate false positives and misleading counts.
    """

    def __init__(self, person_detector, ball_detector: FootballBallONNX,
                 *, ball_columns: int = 2, ball_rows: int = 1):
        self.person_detector = person_detector
        self.ball_detector = ball_detector
        self.ball_columns = ball_columns
        self.ball_rows = ball_rows

    def detect_frame(self, frame_bgr: np.ndarray, **person_options) -> list[Detection]:
        persons = [
            d for d in self.person_detector.detect_frame(frame_bgr, **person_options)
            if d.label == "joueur_candidat"
        ]
        balls = self.ball_detector.detect_frame(
            frame_bgr, tile_columns=self.ball_columns, tile_rows=self.ball_rows,
        )
        return persons + balls
