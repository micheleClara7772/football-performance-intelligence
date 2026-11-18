"""Tests de détection d'image et d'analyse de séquence vidéo."""
import io
from hashlib import sha256
import json
import numpy as np
import pytest

from fpi.video_analysis import detector as d
from fpi.video_analysis.pipeline import analyze_video, _sample_times


def test_model_checksum_and_cleanup(tmp_path, monkeypatch):
    raw = b"test only, not actual model"
    monkeypatch.setattr(d, "MODEL_SHA256", sha256(raw).hexdigest())
    target = d.download_model(tmp_path / "models", getter=lambda u: io.BytesIO(raw))
    assert target.read_bytes() == raw
    assert d.download_model(tmp_path / "models", getter=lambda u: None) == target
    target.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="SHA-256"):
        d.download_model(tmp_path / "models")
    target.unlink()
    with pytest.raises(ValueError, match="SHA-256"):
        d.download_model(tmp_path / "models", getter=lambda u: io.BytesIO(b"invalid"))
    assert not list((tmp_path / "models").glob(".yolox*"))


def test_model_output_decoder_and_validation():
    raw = np.zeros((1, 3549, 85), dtype=np.float32)
    decoded = d.decode_yolox(raw)
    assert decoded.shape == (3549, 85)
    assert np.allclose(decoded[0, :4], [0, 0, 8, 8])
    assert np.allclose(decoded[1, :4], [8, 0, 8, 8])
    with pytest.raises(ValueError):
        d.decode_yolox(np.zeros((1, 300, 85), dtype=np.float32))
    with pytest.raises(ValueError):
        d.decode_yolox(np.zeros((1, 3549, 80), dtype=np.float32))


def test_person_and_ball_class_postprocessing():
    pytest.importorskip("cv2")
    raw = np.zeros((1, 3549, 85), dtype=np.float32)
    raw[0, 102, 4] = raw[0, 301, 4] = 0.99
    raw[0, 102, 5] = 0.97
    raw[0, 301, 37] = 0.98
    class MockSession:
        def run(self, *args): return [raw]
    model = d.YOLOXDetector.__new__(d.YOLOXDetector)
    model.session = MockSession()
    model.input_name = "images"
    detections = model.detect_frame(
        np.zeros((416, 416, 3), dtype=np.uint8),
        tile_columns=1, tile_rows=1,
    )
    assert {x.label for x in detections} == {"joueur_candidat", "ballon_candidat"}
    assert all(0 <= x.x1 < x.x2 <= 416 and 0 <= x.y1 < x.y2 <= 416 for x in detections)


def test_sampling_full_match_and_bounds():
    times = _sample_times(92 * 60, 15.0, 24)
    assert len(times) == 24 and times[0] == 0 and times[-1] > 90*60
    assert len(_sample_times(90, 10, 0)) == 9
    for args in ((-1, 15, 12), (60, 0, 12), (60, 5, -1), (20000, 15, 12)):
        with pytest.raises(ValueError):
            _sample_times(*args)


def test_video_pipeline_with_decodable_avi(tmp_path):
    cv2 = pytest.importorskip("cv2")
    source = tmp_path / "sample.avi"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"MJPG"), 4, (160, 120))
    assert writer.isOpened()
    for i in range(40):
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        cv2.circle(frame, (15 + 2*i, 40), 5, (255,255,255), -1)
        writer.write(frame)
    writer.release()
    class Controlled:
        calls = 0
        def detect_frame(self, frame, **kwargs):
            self.calls += 1
            return [d.Detection("joueur_candidat", 0.8, 20, 20, 50, 90),
                    d.Detection("ballon_candidat", 0.6, 30, 40, 41, 51)]
    detector = Controlled()
    report, previews = analyze_video(
        source, detector, sample_interval_seconds=1.0,
        max_frames=4, preview_limit=2,
    )
    assert detector.calls == report.sampled_frames == 4
    assert report.duration_seconds == 10 and report.covered_until_seconds >= 7
    assert report.frames_with_people == report.frames_with_ball_candidates == 4
    assert report.ball_candidates_total == report.person_candidates_total == 4
    assert len(previews) == 2 and previews[0][1][:2] == b"\xff\xd8"
    assert report.to_dict()["analysis_type"] == "video_inference_sampled_not_tracking"
    json.dumps(report.to_dict())
    assert source.exists()


def test_corrupt_video_rejected(tmp_path):
    path = tmp_path / "broken.mp4"
    path.write_bytes(b"not a video")
    with pytest.raises(ValueError, match="OpenCV"):
        analyze_video(path, object())
