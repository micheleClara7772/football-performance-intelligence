"""Focused regression tests for staged full-match CV infrastructure."""
import copy
import pytest

from fpi.video_analysis.tracking import associate_detections
from fpi.video_analysis.team_metrics import summarize_team_shape
from scripts.compare_video_detectors import compare_reports


def sample(frames):
    return {
        "analysis_type": "video_inference_sampled_not_tracking",
        "source": "licensed-test-footage.avi", "frames": frames,
    }


def box(label, x, y=20, confidence=0.9):
    return {"label": label, "confidence": confidence,
            "bbox_xyxy": [x, y, x + 16, y + 36]}


def test_short_gap_tracking_provisional_ids_and_class_separation():
    person = "joueur_candidat"
    ball = "ballon_candidat"
    report = sample([
        {"time_seconds": 0.0, "detections": [box(person, 30), box(ball, 160)]},
        {"time_seconds": 0.2, "detections": [box(person, 32), box(ball, 162)]},
        {"time_seconds": 0.4, "detections": [box(person, 35), box(ball, 164)]},
    ])
    old = copy.deepcopy(report)
    result = associate_detections(report)
    assert report == old  # immutable source report
    assert result["analysis_type"] == "experimental_short_gap_bbox_association"
    assert len(result["tracks"]) == 2
    assert [fr["detections"][0]["track_id"] for fr in result["frames"]] == [1, 1, 1]
    assert [fr["detections"][1]["track_id"] for fr in result["frames"]] == [2, 2, 2]
    assert "team" not in result["frames"][0]["detections"][0]


def test_sparsely_sampled_video_does_not_claim_continuous_tracking():
    report = sample([
        {"time_seconds": 0, "detections": [box("joueur_candidat", 10)]},
        {"time_seconds": 15, "detections": [box("joueur_candidat", 10)]},
    ])
    result = associate_detections(report)
    assert len(result["tracks"]) == 2
    assert [r["track_id"] for r in result["tracks"]] == [1, 2]


def test_reject_nonmonotonic_and_invalid_bboxes():
    with pytest.raises(ValueError, match="croissants"):
        associate_detections(sample([
            {"time_seconds": 0, "detections": []},
            {"time_seconds": 0, "detections": []},
        ]))
    with pytest.raises(ValueError, match="bbox"):
        associate_detections(sample([
            {"time_seconds": 0, "detections": [
                {"label": "ballon_candidat", "bbox_xyxy": [3, 3, 1, 1]},
            ]},
        ]))


def test_benchmark_three_images_remains_inconclusive():
    ground = {"frames": [
        {"time_seconds": i, "objects": [
            {"label": "ball", "bbox_xyxy": [10, 10, 20, 20]}]}
        for i in range(3)]}
    base = sample([{"time_seconds": i, "detections": [
        {"label": "ballon_candidat", "bbox_xyxy": [10, 10, 20, 20]}]}
        for i in range(3)])
    spec = sample([{"time_seconds": i, "detections": []} for i in range(3)])
    result = compare_reports(base, spec, ground)
    assert result["sufficient_sample_for_provisional_selection"] is False
    assert result["provisional_winner"] is None
    assert result["detectors"]["yolox"]["metrics"]["ball"]["recall"] == 1
    assert result["detectors"]["specialist"]["metrics"]["ball"]["recall"] == 0


def test_benchmark_large_independent_sample_can_select_provisionally():
    truth = {"frames": [{"time_seconds": i, "objects": [
        {"label": "ball", "bbox_xyxy": [10, 10, 20, 20]}]}
        for i in range(100)]}
    yolox = sample([{"time_seconds": i, "detections": []} for i in range(100)])
    specialist = sample([{"time_seconds": i, "detections": [
        {"label": "ballon_candidat", "bbox_xyxy": [10, 10, 20, 20]}]}
        for i in range(100)])
    result = compare_reports(yolox, specialist, truth)
    assert result["sufficient_sample_for_provisional_selection"] is True
    assert result["provisional_winner"] == "specialist"
    assert result["annotated_balls"] == 100


def test_pitch_metrics_only_calibrated_positions():
    positions = {
        "coordinate_space": "pitch_meters_center_origin",
        "source": "reference-annotation",
        "frames": [
            {"time_seconds": 0, "players": [
                {"role": "player", "team": "left", "x_m": x, "y_m": y}
                for x, y in ((-20, -10), (-20, 10), (-10, 0), (0, -10), (0, 10))
            ]},
            {"time_seconds": 1, "players": [
                {"role": "referee", "team": "left", "x_m": 0, "y_m": 0},
            ]},
        ],
    }
    result = summarize_team_shape(positions)
    assert result["teams"]["left"]["qualified_frames"] == 1
    assert result["teams"]["left"]["median_width_m"] == 20
    assert result["teams"]["left"]["median_depth_m"] == 20
    assert result["teams"]["right"]["median_width_m"] is None
    assert result["total_sampled_frames"] == 2


def test_pitch_metrics_reject_uncalibrated_pixel_data():
    with pytest.raises(ValueError, match="Calibration"):
        summarize_team_shape({"coordinate_space": "image_pixels", "frames": [
            {"time_seconds": 0, "players": []}
        ]})
