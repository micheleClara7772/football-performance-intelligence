"""Tests use synthetic boxes only: real media is handled by the gated workflow."""
from types import SimpleNamespace

import pytest

from scripts.benchmark_real_mot_clip import reference_for_samples, _size_limit, VIDEO


def row(frame, x=10, y=20, w=30, h=50, track="7"):
    return [str(frame), track, str(x), str(y), str(w), str(h), "1", "-1", "-1", "-1"]


def test_sampled_mot_rows_with_known_25fps_timing():
    res = reference_for_samples(
        iter([row(0), row(0, x=60, track="8"), row(199),
              row(200, x=15), row(400, x=12)]),
        [0.0, 8.0, 16.0], 25, 200, 100,
    )
    assert len(res["frames"]) == 3
    assert res["sampled_times_with_reference"] == 3
    assert res["gt_box_count"] == 4
    assert res["frames"][1]["time_seconds"] == 8
    assert res["frames"][1]["objects"][0]["bbox_xyxy"] == [15, 20, 45, 70]
    assert res["geometry_consistent"] is True
    assert res["identity_tracking_evaluated"] is False


def test_bad_scale_disables_quality_scoring():
    res = reference_for_samples(
        iter([row(0, x=5000)]), [0.0], 25, 200, 100)
    assert res["geometry_consistent"] is False
    assert res["gt_objects_outside_video_resolution"] == 1
    assert not res["frames"]


def test_only_expected_clip_under_400mb_accepted():
    class Api:
        def list_repo_tree(self, **kwargs):
            assert kwargs["token"] == "PRIVATE"
            return [
                SimpleNamespace(path="mot/clips/117092.mp4", size=100),
                SimpleNamespace(path=VIDEO, size=304980773),
            ]
    assert _size_limit(Api(), VIDEO, "PRIVATE", 400*1024*1024) == 304980773
    with pytest.raises(ValueError, match="Taille"):
        _size_limit(Api(), VIDEO, "PRIVATE", 20*1024*1024)


def test_no_reference_frame_is_not_a_ground_truth_zero():
    res = reference_for_samples(iter([row(1)]), [0.0], 25, 200, 100)
    assert res["sampled_times_with_reference"] == 0
    assert res["frames"] == []


def test_exploratory_tiling_selection_uses_measured_f1():
    from scripts.benchmark_real_mot_clip import choose_tiling
    experiments = [
        {"name": "baseline", "quality_scoreable": True,
         "person_detection_metrics": {"f1": 0.25, "recall": 0.17},
         "person_detection_runtime_seconds": 18},
        {"name": "fine", "quality_scoreable": True,
         "person_detection_metrics": {"f1": 0.52, "recall": 0.49},
         "person_detection_runtime_seconds": 46},
    ]
    assert choose_tiling(experiments) == "fine"
    assert choose_tiling([{"quality_scoreable": False}]) is None
