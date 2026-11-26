"""Unit tests for independent ball annotation audit (fixtures are synthetic only)."""
import copy
import unittest

from scripts.audit_soccertrack_ball_gt import audit


def fixture():
    frames = []
    for half in (1, 2):
        for second, visible in ((10.0, True), (20.0, False)):
            frames.append({
                "half": half, "time_seconds": second, "width": 1920,
                "height": 1080, "reviewed": True, "ball_visible": visible,
                "objects": ([{"label": "ball", "bbox_xyxy": [100, 200, 110, 210]}]
                            if visible else []),
            })
    return {"match_id": "117093", "source": "human-independent", "frames": frames}


class AuditBallGTTests(unittest.TestCase):
    def test_two_halves_positive_negative(self):
        report = audit(fixture())
        self.assertTrue(report["independent_gt_audit_passed"])
        self.assertEqual(report["per_half"]["2"]["negative"], 1)

    def test_insufficient_sample_not_validated(self):
        self.assertFalse(audit(fixture(), min_per_half=10)["independent_gt_audit_passed"])

    def test_reject_prediction_as_gt(self):
        data = fixture()
        data["source"] = "model-predictions"
        with self.assertRaises(ValueError):
            audit(data)

    def test_reject_duplicate_time(self):
        data = fixture()
        data["frames"][1]["time_seconds"] = 10.0
        with self.assertRaises(ValueError):
            audit(data)

    def test_reject_missing_negative_review(self):
        data = fixture()
        data["frames"][1]["reviewed"] = False
        with self.assertRaises(ValueError):
            audit(data)

    def test_reject_out_of_bounds(self):
        data = fixture()
        data["frames"][0]["objects"][0]["bbox_xyxy"][2] = 2000
        with self.assertRaises(ValueError):
            audit(data)

    def test_reject_inconsistent_visibility(self):
        data = fixture()
        data["frames"][0]["ball_visible"] = False
        with self.assertRaises(ValueError):
            audit(data)

    def test_reject_nonfinite(self):
        data = fixture()
        data["frames"][0]["time_seconds"] = float("nan")
        with self.assertRaises(ValueError):
            audit(data)


if __name__ == "__main__":
    unittest.main()
