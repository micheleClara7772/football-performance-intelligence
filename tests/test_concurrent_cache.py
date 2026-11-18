"""Tests du cache atomic quand plusieurs sessions Streamlit importent en même temps."""
import json
from concurrent.futures import ThreadPoolExecutor

from fpi.data.statsbomb import _write_json_atomic


def test_concurrent_writes_use_distinct_temporary_files(tmp_path):
    target = tmp_path / "reference_events.json"
    def write(i):
        _write_json_atomic(target, {"batch": i, "payload": [i] * 100})
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(write, range(32)))
    saved = json.loads(target.read_text(encoding="utf-8"))
    assert isinstance(saved["batch"], int)
    assert saved["payload"] == [saved["batch"]] * 100
    assert list(tmp_path.glob("*.tmp")) == []
