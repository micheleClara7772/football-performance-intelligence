"""Tests isolated from optional AGPL model weights: model is never bundled."""
import numpy as np
import pytest

from fpi.video_analysis.detector import Detection
from fpi.video_analysis.football_ball import FootballBallONNX, HybridFootballDetector


def fake_ball_detector(layout="channels_first"):
    class Session:
        def run(self, *args):
            tensor = args[1]["images"]
            assert tensor.shape == (1, 3, 1280, 1280)
            assert tensor.dtype == np.float32
            assert tensor.min() >= 0 and tensor.max() <= 1
            raw = np.array([320, 320, 40, 40, 0.83], dtype=np.float32)
            if layout == "channels_first":
                return [raw.reshape(1, 5, 1)]
            return [raw.reshape(1, 1, 5)]
    detector = FootballBallONNX.__new__(FootballBallONNX)
    detector.session = Session()
    detector.input_name = "images"
    detector.width = detector.height = 1280
    detector.threshold = 0.2
    return detector


@pytest.mark.parametrize("layout", ["channels_first", "channels_last"])
def test_single_class_ball_output_and_letterbox(layout):
    pytest.importorskip("cv2")
    frame = np.full((360, 640, 3), (20, 100, 200), dtype=np.uint8)
    result = fake_ball_detector(layout).detect_frame(
        frame, tile_columns=1, tile_rows=1,
    )
    assert len(result) == 1
    ball = result[0]
    assert ball.label == "ballon_candidat"
    assert 0.82 < ball.confidence < 0.84
    # Input 640x360 -> 1280x720 with 280px centered top padding:
    # centre x=320/2=160, y=(320-280)/2=20.
    assert (ball.x1, ball.y1, ball.x2, ball.y2) == (150, 10, 170, 30)


def test_invalid_ball_schema_rejected():
    with pytest.raises(ValueError, match="incompatible"):
        FootballBallONNX._predictions(np.zeros((1, 10, 6), dtype=np.float32))
    with pytest.raises(ValueError, match="inattendue"):
        FootballBallONNX._predictions(np.zeros((5, 8), dtype=np.float32))


def test_hybrid_filters_generic_ball_boxes():
    person = Detection("joueur_candidat", 0.9, 1, 2, 3, 4)
    generic_ball = Detection("ballon_candidat", 0.4, 8, 9, 11, 12)
    specialist_ball = Detection("ballon_candidat", 0.8, 80, 90, 110, 120)
    class Generic:
        def detect_frame(self, frame, **kwargs):
            assert kwargs["tile_columns"] == 1
            return [person, generic_ball]
    class Specialist:
        def detect_frame(self, frame, **kwargs):
            assert kwargs == {"tile_columns": 2, "tile_rows": 1}
            return [specialist_ball]
    hybrid = HybridFootballDetector(Generic(), Specialist())
    result = hybrid.detect_frame(
        np.zeros((360, 640, 3), dtype=np.uint8), tile_columns=1, tile_rows=1,
    )
    assert result == [person, specialist_ball]
