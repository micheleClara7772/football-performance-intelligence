"""Independent truth parser checks; no web/model needed."""
import pytest
from scripts.benchmark_ball_independent import parse_yolo_ball_annotations


def test_extract_only_ball_truth_with_pixel_coordinates():
    labels = ("1 0.20 0.45 0.10 0.20\n"
              "0 0.50 0.50 0.02 0.04\n"
              "2 0.70 0.50 0.02 0.07\n")
    out = parse_yolo_ball_annotations(labels, 1000, 500)
    assert len(out) == 1
    assert out[0]["label"] == "ball"
    assert out[0]["bbox_xyxy"] == [490, 240, 510, 260]


def test_no_ball_label_is_hard_negative():
    assert parse_yolo_ball_annotations("1 0.5 0.5 0.1 0.2\n", 1280, 720) == []
    assert parse_yolo_ball_annotations("", 1280, 720) == []


def test_reject_corrupt_truth_and_wrong_class():
    for text in ("3 0.5 0.5 0.1 0.1", "0 0.5 0.5 0.0 0.1",
                 "0 0.5 0.5 nan 0.1", "0 0.5 0.5"):
        with pytest.raises(ValueError):
            parse_yolo_ball_annotations(text, 1000, 700)
