"""Spatial dashboard must never infer model accuracy from reference data."""
import json
import pytest

from fpi.ui.video_pitch_metrics import parse_and_summarize, build_quality_rows


def positions():
    return {
        "coordinate_space":"pitch_meters_center_origin",
        "source":"independent-reference-positions",
        "frames":[
            {"time_seconds":0.0,"players":[
                {"role":"player","team":side,"x_m":x,"y_m":y}
                for side in ("left","right")
                for x,y in [(-20,-10),(-10,10),(0,0),(10,-5),(20,5)]
            ]},
            {"time_seconds":1.0,"players":[]},
        ],
    }


def test_valid_pitch_annotations_display_coverage_not_confidence():
    result=parse_and_summarize(json.dumps(positions()).encode())
    rows=build_quality_rows(result)
    assert result["total_sampled_frames"]==2
    assert len(rows)==2
    assert rows[0]["Couverture des annotations (%)"]==50
    assert rows[1]["Couverture des annotations (%)"]==50
    assert all(x["Confiance détection FPI"]=="Non mesurée" for x in rows)
    assert rows[0]["Largeur médiane (m)"]==20


def test_reject_pixel_boxes_in_spatial_metrics():
    data=positions()
    data["coordinate_space"]="image_pixels"
    with pytest.raises(ValueError,match="calibrées"):
        parse_and_summarize(json.dumps(data).encode())


def test_reject_json_over_limit_and_invalid_content():
    with pytest.raises(ValueError):
        parse_and_summarize(b"z")
    with pytest.raises(ValueError):
        parse_and_summarize(b"a"*(8*1024*1024+1))
