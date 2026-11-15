from pathlib import Path
import pytest


def test_app_starts_offline():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    # No source data is shipped. An error on cache absence must not crash the app.
    at = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    assert len(at.exception) == 0
    assert any("Dashboard" in s for s in at.sidebar.radio[0].options)
    assert len(at.sidebar.radio[0].options) == 5
    for label in at.sidebar.radio[0].options:
        at.sidebar.radio[0].set_value(label).run()
        assert len(at.exception) == 0, label
