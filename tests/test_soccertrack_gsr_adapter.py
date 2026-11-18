"""No huge dataset is required to verify released-GSR schema extraction."""
import pytest
from scripts.convert_soccertrack_gsr import convert_gsr_records, _frame_index
from fpi.video_analysis.team_metrics import summarize_team_shape


def record(index, team="left", role="player", x=10.0, y=-3.0):
    return {
        "image_id": f"3{index + 1:06d}",
        "supercategory": "object",
        "attributes": {"role": role, "team": team, "jersey": "12"},
        "bbox_image": {"x": 4, "y": 5, "w": 30, "h": 80},
        "bbox_pitch": {"x_bottom_middle": x, "y_bottom_middle": y},
    }


def test_released_coco_schema_and_half_relative_timestamp():
    rows = [
        record(0), record(0, team="right", x=-5),
        record(1), record(125, x=20), record(250, x=30),
        {"supercategory": "pitch", "image_id": "3000001"},
    ]
    extracted = convert_gsr_records(iter(rows), every_seconds=5)
    assert extracted["selected_player_observations"] == 4
    assert [f["time_seconds"] for f in extracted["frames"]] == [0, 5, 10]
    assert extracted["frames"][0]["players"][0]["x_m"] == 10
    assert extracted["reference_type"] == "independent_gsr_not_video_detection"


def test_reference_supports_shape_calculation_without_fake_video_attribution():
    extracted = convert_gsr_records(
        (record(0, x=i*5, y=i*2) for i in range(5)), every_seconds=5)
    report = summarize_team_shape(extracted)
    assert report["teams"]["left"]["qualified_frames"] == 1
    assert report["teams"]["left"]["median_width_m"] == 8
    assert report["teams"]["left"]["median_depth_m"] == 20


def test_bad_frame_id_rejected():
    assert _frame_index("3000001") == 0
    assert _frame_index("3000126") == 125
    with pytest.raises(ValueError, match="image_id"):
        _frame_index("0000")
