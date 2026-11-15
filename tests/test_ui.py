import pytest

def test_app_starts_offline():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file("app.py", default_timeout=15).run()
    assert len(at.exception) == 0
    assert any("Dashboard" in s for s in at.sidebar.radio[0].options)
    assert len(at.sidebar.radio[0].options) == 5
