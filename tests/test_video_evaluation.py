"""Detections are measured against full annotations, not presence alone."""
from scripts.evaluate_video_detections import evaluate
import pytest


def test_perfect_and_false_positive_detection():
    truth = {"frames": [{
        "time_seconds": 0,
        "objects": [{"label": "player", "bbox_xyxy": [0, 0, 10, 20]},
                    {"label": "ball", "bbox_xyxy": [50, 50, 60, 60]}],
    }]}
    predicted = {"analysis_type": "video_inference_sampled_not_tracking",
                 "frames": [{
                     "time_seconds": 0,
                     "detections": [
                         {"label": "joueur_candidat", "bbox_xyxy": [0, 0, 10, 20]},
                         {"label": "ballon_candidat", "bbox_xyxy": [50, 50, 60, 60]},
                         {"label": "ballon_candidat", "bbox_xyxy": [70, 70, 80, 80]},
                     ],
                 }]}
    result = evaluate(predicted, truth)
    assert result["matched_frames"] == 1
    assert result["metrics"]["person"]["precision"] == 1.0
    assert result["metrics"]["person"]["recall"] == 1.0
    assert result["metrics"]["ball"]["tp"] == 1
    assert result["metrics"]["ball"]["fp"] == 1
    assert result["metrics"]["ball"]["precision"] == 0.5


def test_unmatched_annotation_is_false_negative():
    truth = {"frames": [{"time_seconds": 31, "objects": [
        {"label": "ball", "bbox_xyxy": [0, 0, 5, 5]},
    ]}]}
    report = evaluate({"frames": [{"time_seconds": 15, "detections": []}]}, truth)
    assert report["missing_prediction_frames"] == 1
    assert report["metrics"]["ball"]["fn"] == 1
    assert report["metrics"]["ball"]["recall"] == 0.0


def test_bad_labelled_box_rejected():
    with pytest.raises(ValueError, match="invalides"):
        evaluate({"frames": []}, {"frames": [{
            "time_seconds": 0,
            "objects": [{"label": "ball", "bbox_xyxy": [5, 5, 1, 1]}],
        }]})
