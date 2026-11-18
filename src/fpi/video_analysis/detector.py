"""YOLOX-Nano ONNX : personnes (COCO 0) et ballons de sport (COCO 32).

Implémentation autonome : aucun contenu FIFA téléchargé, poids vérifiés SHA-256.
Le code YOLOX est Apache 2.0 ; l'usage des poids pré-entraînés doit être revu
séparément pour toute commercialisation.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import os
import tempfile
from urllib.request import Request, urlopen

import numpy as np

MODEL_URL = (
    "https://github.com/Megvii-BaseDetection/YOLOX/releases/"
    "download/0.1.1rc0/yolox_nano.onnx"
)
MODEL_SHA256 = "c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d"
MODEL_SIZE = (416, 416)
MODEL_MAX_BYTES = 15_000_000
PERSON_CLASS = 0
BALL_CLASS = 32

@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    # pixels in source video coordinates
    x1: int
    y1: int
    x2: int
    y2: int

    def to_dict(self) -> dict:
        return {
            "label": self.label, "confidence": round(self.confidence, 4),
            "bbox_xyxy": [self.x1, self.y1, self.x2, self.y2],
        }


def download_model(directory: Path, getter=None) -> Path:
    """Download only after an explicit user action. Verify exact model bytes."""
    directory = Path(directory)
    path = directory / "yolox_nano.onnx"
    if path.exists():
        existing = sha256(path.read_bytes()).hexdigest()
        if existing != MODEL_SHA256:
            raise ValueError("Modèle local présent mais empreinte SHA-256 invalide")
        return path

    directory.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".yolox-nano-", dir=directory)
    try:
        digest = sha256()
        size = 0
        with os.fdopen(fd, "wb") as dest:
            if getter is not None:
                stream = getter(MODEL_URL)
            else:
                req = Request(MODEL_URL, headers={"User-Agent": "FPI/1.0 model-license-review"})
                stream = urlopen(req, timeout=45)
            with stream:
                while True:
                    chunk = stream.read(256 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MODEL_MAX_BYTES:
                        raise ValueError("Modèle trop volumineux : téléchargement refusé")
                    digest.update(chunk)
                    dest.write(chunk)
        if digest.hexdigest() != MODEL_SHA256:
            raise ValueError(
                "Empreinte SHA-256 du modèle différente de la référence : "
                "refus de charger des poids non vérifiés"
            )
        os.replace(temporary, path)
        return path
    finally:
        Path(temporary).unlink(missing_ok=True)


def decode_yolox(raw: np.ndarray, size=MODEL_SIZE) -> np.ndarray:
    """Decode YOLOX anchor-free logits per 8/16/32 strides; no box invention."""
    if raw.ndim != 3 or raw.shape[0] != 1 or raw.shape[2] != 85:
        raise ValueError(f"Sortie YOLOX inattendue : {raw.shape}")
    grids, strides = [], []
    for stride in (8, 16, 32):
        gy, gx = np.meshgrid(
            np.arange(size[0] // stride), np.arange(size[1] // stride),
            indexing="ij",
        )
        grid = np.stack([gx, gy], axis=-1).reshape(-1, 2)
        grids.append(grid)
        strides.append(np.full((grid.shape[0], 1), stride))
    grid = np.concatenate(grids, axis=0)
    stride = np.concatenate(strides, axis=0)
    if raw.shape[1] != grid.shape[0]:
        raise ValueError("Nombre d'ancres du modèle incohérent")
    out = raw[0].copy()
    out[:, :2] = (out[:, :2] + grid) * stride
    out[:, 2:4] = np.exp(np.clip(out[:, 2:4], -20, 20)) * stride
    return out


def _regions(width: int, height: int, columns: int, rows: int):
    """Overlapping tiles make small distant players/balls less tiny."""
    if not 1 <= columns <= 4 or not 1 <= rows <= 3:
        raise ValueError("Découpage vidéo non pris en charge")
    if (columns, rows) == (1, 1):
        return [(0, 0, width, height)]
    tile_w = int(np.ceil(width / columns * 1.12))
    tile_h = int(np.ceil(height / rows * 1.12))
    result = []
    for r in range(rows):
        for c in range(columns):
            x1 = min(max(0, int(c * width / columns) - tile_w // 18), width - 1)
            y1 = min(max(0, int(r * height / rows) - tile_h // 18), height - 1)
            x2 = min(width, x1 + tile_w)
            y2 = min(height, y1 + tile_h)
            if x2 - x1 >= 16 and y2 - y1 >= 16:
                result.append((x1, y1, x2, y2))
    return result


class YOLOXDetector:
    """CPU inference with bounded threads; model is loaded only when requested."""

    def __init__(self, model_path: Path):
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise RuntimeError("Installer les dépendances vidéo depuis requirements.txt") from exc
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(
            str(model_path), sess_options=options, providers=["CPUExecutionProvider"],
        )
        self.input_name = self.session.get_inputs()[0].name
        dims = self.session.get_inputs()[0].shape
        if len(dims) != 4 or dims[2:4] != list(MODEL_SIZE):
            raise ValueError(f"Modèle ONNX incompatible : entrée {dims}")

    def _detect_tile(self, tile: np.ndarray, offset: tuple[int, int], *,
                     person_threshold: float, ball_threshold: float) -> list[Detection]:
        import cv2
        height, width = tile.shape[:2]
        ratio = min(MODEL_SIZE[0] / height, MODEL_SIZE[1] / width)
        resized = cv2.resize(
            tile, (max(1, int(width * ratio)), max(1, int(height * ratio))),
            interpolation=cv2.INTER_LINEAR,
        )
        # YOLOX reference preprocessor: BGR, [0,255], top-left, fill 114.
        canvas = np.full((MODEL_SIZE[0], MODEL_SIZE[1], 3), 114, dtype=np.uint8)
        canvas[:resized.shape[0], :resized.shape[1]] = resized
        tensor = canvas.transpose(2, 0, 1).astype(np.float32)[None]
        raw = self.session.run(None, {self.input_name: tensor})[0]
        pred = decode_yolox(raw)
        results = []
        for cls, label, threshold in (
            (PERSON_CLASS, "joueur_candidat", person_threshold),
            (BALL_CLASS, "ballon_candidat", ball_threshold),
        ):
            scores = pred[:, 4] * pred[:, cls + 5]
            good = np.flatnonzero(np.isfinite(scores) & (scores >= threshold))
            if good.size == 0:
                continue
            centers = pred[good, :4] / ratio
            xyxy = np.column_stack((
                centers[:, 0] - centers[:, 2] / 2,
                centers[:, 1] - centers[:, 3] / 2,
                centers[:, 0] + centers[:, 2] / 2,
                centers[:, 1] + centers[:, 3] / 2,
            ))
            boxes = []
            confidences = []
            candidates = []
            for box, confidence in zip(xyxy, scores[good]):
                x1 = int(np.clip(box[0], 0, width - 1))
                y1 = int(np.clip(box[1], 0, height - 1))
                x2 = int(np.clip(box[2], 0, width))
                y2 = int(np.clip(box[3], 0, height))
                if x2 <= x1 or y2 <= y1:
                    continue
                boxes.append([x1, y1, x2 - x1, y2 - y1])
                confidences.append(float(confidence))
                candidates.append((x1, y1, x2, y2))
            if not boxes:
                continue
            indices = cv2.dnn.NMSBoxes(boxes, confidences, threshold, 0.45)
            for index in np.asarray(indices, dtype=int).reshape(-1):
                x1, y1, x2, y2 = candidates[index]
                results.append(Detection(
                    label, confidences[index], x1 + offset[0], y1 + offset[1],
                    x2 + offset[0], y2 + offset[1],
                ))
        return results

    def detect_frame(self, frame_bgr: np.ndarray, *,
                     tile_columns: int = 2, tile_rows: int = 2,
                     person_threshold: float = 0.25,
                     ball_threshold: float = 0.16) -> list[Detection]:
        import cv2
        if not isinstance(frame_bgr, np.ndarray) or frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
            raise ValueError("Frame BGR illisible")
        height, width = frame_bgr.shape[:2]
        if min(height, width) < 32 or max(height, width) > 8192:
            raise ValueError("Dimensions vidéo hors limites")
        found = []
        for x1, y1, x2, y2 in _regions(width, height, tile_columns, tile_rows):
            found.extend(self._detect_tile(
                frame_bgr[y1:y2, x1:x2], (x1, y1),
                person_threshold=person_threshold, ball_threshold=ball_threshold,
            ))
        # NMS global across overlapping tiles, separately by predicted class.
        selected = []
        for label, threshold in (("joueur_candidat", person_threshold),
                                 ("ballon_candidat", ball_threshold)):
            candidates = [d for d in found if d.label == label]
            if not candidates:
                continue
            boxes = [[d.x1, d.y1, d.x2 - d.x1, d.y2 - d.y1] for d in candidates]
            keep = cv2.dnn.NMSBoxes(boxes, [d.confidence for d in candidates], threshold, 0.5)
            selected.extend(candidates[int(i)] for i in np.asarray(keep, dtype=int).reshape(-1))
        return sorted(selected, key=lambda x: (x.label, -x.confidence))
