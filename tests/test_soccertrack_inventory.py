"""No token, internet, video, or gated files used in local inventory tests."""
from types import SimpleNamespace

from scripts.inspect_soccertrack_match import (
    inventory, selected_path, summarize_mot_rows, run,
)


def item(path, size=10):
    return SimpleNamespace(path=path, size=size)


def test_select_only_specific_match_across_layouts():
    assert selected_path("videos/117093/117093_panorama_1st_half.mp4", "117093")
    assert selected_path("videos/117093.mp4", "117093")
    assert selected_path("gsr/117093/117093_2nd.json", "117093")
    assert selected_path("mot/117093.txt", "117093")
    assert not selected_path("videos/117092/117092_panorama_1st_half.mp4", "117093")
    assert not selected_path("gsr/117093_other.json", "117093")
    assert not selected_path("../../.env", "117093")


def test_remote_inventory_reports_only_selected_video_and_annotation_bytes():
    files = [
        item("videos/117093/117093_panorama_1st_half.mp4", 10**9),
        item("videos/117093/117093_panorama_2nd_half.mp4", 2 * 10**9),
        item("gsr/117093/117093_1st.json", 50),
        item("mot/117093.txt", 6200000),
        item("videos/117092/117092_panorama_1st_half.mp4", 99),
    ]
    result = inventory(files, "117093")
    assert result["file_count"] == 4
    assert result["video_file_count"] == 2
    assert result["known_total_bytes"] == 3006200050
    assert all("117092" not in r["path"] for r in result["files"])
    assert result["full_match_downloaded"] is False


def test_mot_summary_is_reference_not_video_inference():
    rows = [
        ["1", "7", "10", "20", "30", "40", "1", "-1", "-1", "-1"],
        ["2", "7", "12", "20", "30", "40", "1", "-1", "-1", "-1"],
        ["2", "9", "44", "30", "32", "48", "1", "-1", "-1", "-1"],
        ["header", "not", "numeric"],
    ]
    result = summarize_mot_rows(rows)
    assert result["parsed_box_rows"] == 3
    assert result["rejected_rows"] == 1
    assert result["unique_annotated_frames"] == 2
    assert result["unique_reference_track_ids"] == 2
    assert result["max_frame"] == 2
    assert result["matches_full_90min"] is False
    assert result["annotations_are_model_inferences"] is False


def test_no_hf_token_fails_closed(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    assert run("117093")["status"] == "NEEDS_AUTHENTICATION"


def test_remote_list_can_be_inspected_without_downloading():
    class FakeApi:
        def list_repo_tree(self, *, path_in_repo, **kwargs):
            if path_in_repo == "videos":
                return iter([item("videos/117093.mp4", 1_000_000)])
            if path_in_repo == "gsr":
                return iter([item("gsr/117093/117093_1st.json", 500)])
            return iter([])
    result = run("117093", client=FakeApi(), token="NEVER_PRINT")
    assert result["status"] == "INVENTORY_VERIFIED"
    assert result["video_file_count"] == 1
    assert result["full_match_downloaded"] is False
    assert "NEVER_PRINT" not in str(result)


def test_remote_exception_not_leak_token():
    class BrokenApi:
        def list_repo_tree(self, **kwargs):
            raise RuntimeError("token=SECRET_PRESENT")
    result = run("117093", client=BrokenApi(), token="SECRET_PRESENT")
    assert result["status"] == "INVENTORY_NOT_VERIFIED"
    assert "SECRET_PRESENT" not in str(result)
