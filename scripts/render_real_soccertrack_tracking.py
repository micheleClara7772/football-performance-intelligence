"""REAL annotated SoccerTrack tracking demonstration with ByteTrack and MOT IDs.

Processes 12 seconds at 5 FPS from independently annotated footage and
measures player association IDF1 and ID switches with MOTMetrics. It is
not full-match tracking, team assignment, calibrated positions or ball GT.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from scripts.prepare_soccertrack import DATASET, REVISION
from scripts.benchmark_real_mot_clip import _size_limit, VIDEO_MAX_BYTES, MOT_MAX_BYTES
from scripts.evaluate_video_detections import _iou
from fpi.video_analysis.bytetrack_adapter import track_with_bytetrack
from fpi.video_analysis.detector import YOLOXDetector, download_model
from fpi.video_analysis.football_ball import FootballBallONNX, HybridFootballDetector

MATCH_ID="117093"
SOURCE=f"mot/clips/{MATCH_ID}.mp4"
REFERENCE=f"mot/{MATCH_ID}.txt"


def load_reference_rows(rows, selected_frames: set[int]):
    reference=defaultdict(list)
    for row in rows:
        if len(row)<6 or row[0].startswith("#"):
            continue
        try:
            frame_idx=int(float(row[0]))
            if frame_idx not in selected_frames:
                continue
            object_id=int(float(row[1]))
            x,y,w,h=(float(v) for v in row[2:6])
        except (ValueError,TypeError):
            continue
        if not all(map(math.isfinite,(x,y,w,h))) or w<=0 or h<=0:
            continue
        reference[frame_idx].append({
            "id":object_id,
            "bbox_xyxy":[x,y,x+w,y+h],
        })
    return reference


def score_real_tracklets(tracked: dict, frame_ids: list[int],
                         ground: dict, *, iou_threshold=0.30):
    """Genuine MOTMetrics IDF1 and switches for this short annotated section."""
    if not 0<iou_threshold<=1 or len(frame_ids)!=len(tracked["frames"]):
        raise ValueError("IDs GT/timestamps incohérents")
    import motmetrics as mm
    acc=mm.MOTAccumulator(auto_id=True)
    # MOTMetrics 1.4 coerces hypothesis IDs to float in pandas.
    # Map ByteTrack's namespaced IDs to stable integers per run.
    numeric_ids={}
    observations=0
    for source_id,frame in zip(frame_ids,tracked["frames"]):
        truth=ground.get(source_id,[])
        predictions=[
            d for d in frame["detections"]
            if d["label"]=="joueur_candidat" and d.get("track_id") is not None
        ]
        gt_ids=[obj["id"] for obj in truth]
        predicted_ids=[]
        for obj in predictions:
            raw_id=obj["track_id"]
            if raw_id not in numeric_ids:
                numeric_ids[raw_id]=len(numeric_ids)+1
            predicted_ids.append(numeric_ids[raw_id])
        distances=np.full((len(truth),len(predictions)), np.nan, dtype=np.float64)
        for i,obj in enumerate(truth):
            for j,pred in enumerate(predictions):
                overlap=_iou(obj["bbox_xyxy"],pred["bbox_xyxy"])
                if overlap>=iou_threshold:
                    distances[i,j]=1-overlap
        acc.update(gt_ids,predicted_ids,distances)
        observations+=len(truth)
    mh=mm.metrics.create()
    result=mh.compute(
        acc,metrics=["idf1","idp","idr","num_switches","num_frames",
                     "num_matches","precision","recall"],
        name="sample")
    data=result.loc["sample"].to_dict()
    def clean(v):
        val=float(v)
        return round(val,4) if math.isfinite(val) else None
    return {
        "mot_gt_box_count":observations,
        "frames_evaluated":int(data["num_frames"]),
        "idf1":clean(data["idf1"]),
        "id_precision":clean(data["idp"]),
        "id_recall":clean(data["idr"]),
        "id_switches":int(data["num_switches"]),
        "matched_gt_boxes":int(data["num_matches"]),
        "box_precision":clean(data["precision"]),
        "box_recall":clean(data["recall"]),
        "iou_threshold":iou_threshold,
        "validated_full_match":False,
        "only_player_ids":True,
        "warning":"12-second sampled 5 FPS clip; no modelled ball GT, team or referee IDs.",
    }


def annotate_video(source:Path,frames:list[dict],frame_ids:list[int],
                   output:Path, *,fps:float):
    cap=cv2.VideoCapture(str(source))
    if not cap.isOpened(): raise ValueError("Vidéo source illisible")
    original_width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if original_width<64 or original_height<64: raise ValueError("Dimensions vidéo")
    width=1600
    height=int(round(original_height*width/original_width/2))*2
    output.parent.mkdir(parents=True,exist_ok=True)
    writer=cv2.VideoWriter(str(output),cv2.VideoWriter_fourcc(*"mp4v"),
                           fps,(width,height))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError("Encodage MP4 indisponible")
    try:
        for source_index,item in zip(frame_ids,frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES,source_index)
            ok,frame=cap.read()
            if not ok: raise ValueError("Frame de visualisation absente")
            target=cv2.resize(frame,(width,height))
            sx,sy=width/original_width,height/original_height
            for det in item["detections"]:
                color=(0,230,70) if det["label"]=="joueur_candidat" else (0,140,255)
                x1,y1,x2,y2=det["bbox_xyxy"]
                a,b,c,d=(int(x1*sx),int(y1*sy),int(x2*sx),int(y2*sy))
                cv2.rectangle(target,(a,b),(c,d),color,2)
                identifier=det.get("track_id") or "?"
                cv2.putText(target,str(identifier),(a,max(13,b-3)),
                            cv2.FONT_HERSHEY_SIMPLEX,0.48,color,2)
            cv2.rectangle(target,(0,height-34),(width,height),(0,0,0),-1)
            cv2.putText(target,
                "IDs PROVISOIRES ByteTrack | equipe/arbitre: inconnus | SoccerTrack v2 CC BY 4.0",
                (15,height-11),cv2.FONT_HERSHEY_SIMPLEX,0.54,(255,255,255),1)
            writer.write(target)
    finally:
        writer.release()
        cap.release()
    if not output.is_file() or output.stat().st_size<1024:
        raise RuntimeError("Vidéo de suivi invalide")


def run(*,token:str,seconds=12.0,sample_fps=5.0,out_dir:Path):
    if seconds!=12.0 or sample_fps!=5.0:
        raise ValueError("Démo bornée à 12 s / 5 FPS pour limiter CPU")
    from huggingface_hub import HfApi,hf_hub_download
    api=HfApi()
    _size_limit(api,SOURCE,token,VIDEO_MAX_BYTES)
    _size_limit(api,REFERENCE,token,MOT_MAX_BYTES)
    with tempfile.TemporaryDirectory(prefix="fpi-bytetrack-real-") as private:
        video=Path(hf_hub_download(repo_id=DATASET,repo_type="dataset",
                                  revision=REVISION,filename=SOURCE,
                                  token=token,local_dir=private))
        labels=Path(hf_hub_download(repo_id=DATASET,repo_type="dataset",
                                   revision=REVISION,filename=REFERENCE,
                                   token=token,local_dir=private))
        cap=cv2.VideoCapture(str(video))
        if not cap.isOpened():raise ValueError("VideoClipError")
        original_fps=cap.get(cv2.CAP_PROP_FPS)
        if not 0<original_fps<=120:raise ValueError("BadFps")
        chosen=[int(round(i*original_fps/sample_fps)) for i in range(int(seconds*sample_fps))]
        yolox=YOLOXDetector(download_model(Path(private)/"models"))
        specialist=FootballBallONNX(Path(hf_hub_download(
            repo_id="acatorcini/yolov9-soccer-ball",filename="v9b_best.onnx",
            local_dir=str(Path(private)/"ball"))),threshold=0.20)
        detector=HybridFootballDetector(yolox,specialist,
                                        ball_columns=2,ball_rows=1)
        extracted=[]
        started=perf_counter()
        try:
            for index,source_frame in enumerate(chosen):
                cap.set(cv2.CAP_PROP_POS_FRAMES,source_frame)
                success,raw=cap.read()
                if not success:raise ValueError("MissingSourceFrame")
                objects=detector.detect_frame(
                    raw,tile_columns=4,tile_rows=3,person_threshold=0.20)
                extracted.append({
                    "time_seconds":round(index/sample_fps,4),
                    "detections":[o.to_dict() for o in objects],
                })
        finally:
            cap.release()
        measured=round(perf_counter()-started,2)
        tracked=track_with_bytetrack({
            "analysis_type":"video_inference_sampled_not_tracking",
            "source":video.name,
            "frames":extracted,
        },max_gap_seconds=0.6)
        with labels.open("r",encoding="utf-8-sig",newline="") as handle:
            reference=load_reference_rows(csv.reader(handle),set(chosen))
        quality=score_real_tracklets(tracked,chosen,reference)
        out_dir.mkdir(parents=True,exist_ok=True)
        rendered=out_dir/"soccertrack-tracks-117093-first12s.mp4"
        annotate_video(video,tracked["frames"],chosen,rendered,fps=sample_fps)
        return {
            "analysis_type":"real_video_dense_mot_byte_track_eval",
            "provenance":"SoccerTrack v2 CC BY 4.0 | AtomScott",
            "source_match_id":MATCH_ID,
            "clip_seconds":seconds,
            "output_video_filename":rendered.name,
            "video_bytes":rendered.stat().st_size,
            "original_fps":original_fps,
            "processed_fps":sample_fps,
            "processed_frames":len(extracted),
            "real_inference_runtime_seconds":measured,
            "person_candidates":sum(
                o["label"]=="joueur_candidat" for f in extracted
                for o in f["detections"]),
            "ball_candidates_unverified":sum(
                o["label"]=="ballon_candidat" for f in extracted
                for o in f["detections"]),
            "tracker":"Roboflow ByteTrack 2.7.0 (real)",
            "mot_identity_benchmark":quality,
            "team_assignment_validated":False,
            "referee_classification_validated":False,
            "ball_tracking_accuracy_validated":False,
            "full_match_90min_tracking_validated":False,
            "limitations":[
                "Only first 12 seconds of a real 4-minute MOT clip were evaluated.",
                "Player track IDs are provisional, not jersey identities.",
                "Ball detection and ball tracking have no ground truth in this MOT dataset.",
                "No pitch calibration, team classification, possession or pressing inferred.",
            ],
        }


def main():
    p=argparse.ArgumentParser(description="FPI — vraie vidéo annotée et métriques IDF1")
    p.add_argument("--out-dir",type=Path,default=Path("outputs/tracking-video-proof"))
    args=p.parse_args()
    token=os.environ.get("HF_TOKEN")
    if not token: p.error("HF_TOKEN manquant")
    try:
        report=run(token=token,out_dir=args.out_dir)
    except Exception as exc:
        # Sanitized exception; no signed URL/token in logs.
        raise SystemExit("FPI_TRACKING_VIDEO=FAILED:"+type(exc).__name__) from None
    (args.out_dir/"tracking-report.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FPI_TRACKING_VIDEO=REAL_12_SECOND_DEMO_NOT_90MIN")
    print("FPI_TRACKING_VIDEO_STATS="+json.dumps(report,ensure_ascii=False))


if __name__=="__main__":
    main()
