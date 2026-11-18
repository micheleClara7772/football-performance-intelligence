"""Short real tracking pipeline guards, no gated media required."""
import pytest
from scripts.render_real_soccertrack_tracking import (
    load_reference_rows, score_real_tracklets,
)


def test_reference_tracks_are_mapped_to_actual_frame_ids():
    rows=[
        ["0","11","20","30","10","50","1","-1","-1","-1"],
        ["0","12","40","30","10","50","1","-1","-1","-1"],
        ["1","11","22","30","10","50","1","-1","-1","-1"],
        ["25","11","30","30","10","50","1","-1","-1","-1"],
    ]
    gt=load_reference_rows(rows,{0,25})
    assert len(gt[0])==2
    assert gt[0][0]["id"]==11
    assert gt[0][0]["bbox_xyxy"]==[20,30,30,80]
    assert len(gt[25])==1
    assert 1 not in gt


def test_identity_score_uses_genuine_motmetrics_when_available():
    pytest.importorskip("motmetrics")
    frame_ids=[0,5,10]
    trk={"frames":[{"detections":[{
        "label":"joueur_candidat", "track_id":"P:0:1",
        "bbox_xyxy":[20+i,30,40+i,80],
    }]} for i in range(3)]}
    gt={i:[{"id":17,"bbox_xyxy":[20+j,30,40+j,80]}]
        for j,i in enumerate(frame_ids)}
    quality=score_real_tracklets(trk,frame_ids,gt)
    assert quality["idf1"]==1
    assert quality["id_switches"]==0
    assert quality["validated_full_match"] is False


def test_tracking_id_switch_detected_when_available():
    pytest.importorskip("motmetrics")
    trk={"frames":[{"detections":[{
        "label":"joueur_candidat", "track_id":tid,
        "bbox_xyxy":[20,30,40,80],
    }]} for tid in ("P:0:1","P:0:1","P:0:2")]}
    gt={k:[{"id":17,"bbox_xyxy":[20,30,40,80]}] for k in (0,5,10)}
    quality=score_real_tracklets(trk,[0,5,10],gt)
    assert quality["id_switches"]>=1
    assert quality["idf1"]<1
