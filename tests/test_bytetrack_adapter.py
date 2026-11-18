"""Real tracker integration smoke on synthetic detections, not a match benchmark."""
import pytest
from fpi.video_analysis.bytetrack_adapter import track_with_bytetrack


def detection(x, t):
    return {
        "time_seconds": t,
        "detections": [{
            "label": "joueur_candidat", "confidence": 0.95,
            "bbox_xyxy": [x, 10, x+20, 60],
        }],
    }


def report(frames):
    return {"analysis_type": "video_inference_sampled_not_tracking",
            "source": "synthetic", "frames": frames}


def test_actual_bytetrack_keeps_one_id_when_object_stationary():
    pytest.importorskip("trackers")
    pytest.importorskip("supervision")
    tracked = track_with_bytetrack(report([
        detection(20, 0.0), detection(20, 0.2), detection(20, 0.4),
        detection(20, 0.6), detection(20, 0.8),
    ]))
    ids = [frame["detections"][0]["track_id"] for frame in tracked["frames"]]
    known = [x for x in ids if x is not None]
    assert len(known) >= 2, ids
    assert len(set(known)) == 1, ids
    assert known[0].startswith("P:0:")


def test_actual_bytetrack_resets_after_long_gap():
    pytest.importorskip("trackers")
    pytest.importorskip("supervision")
    tracked = track_with_bytetrack(report([
        detection(20, 0.0), detection(20, 0.2), detection(20, 0.4),
        detection(20, 15.0), detection(20, 15.2), detection(20, 15.4),
    ]))
    ids = [fr["detections"][0]["track_id"] for fr in tracked["frames"]]
    earlier = {x for x in ids[:3] if x is not None}
    later = {x for x in ids[3:] if x is not None}
    assert earlier and later
    assert earlier.isdisjoint(later)
    assert all(x.startswith("P:1:") for x in later)


def test_bytetrack_rejects_nonmonotonic_data_before_inference():
    pytest.importorskip("trackers")
    with pytest.raises(ValueError, match="croissants"):
        track_with_bytetrack(report([detection(10, 0.0), detection(10, 0.0)]))
