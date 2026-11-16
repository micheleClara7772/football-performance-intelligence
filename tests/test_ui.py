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

def test_official_real_footage_sources_are_provider_hosted():
    from fpi.ui.video import OFFICIAL_FIFA_CLIPS
    assert len(OFFICIAL_FIFA_CLIPS) == 2
    assert all(clip["url"].startswith("https://www.youtube.com/watch?v=") for clip in OFFICIAL_FIFA_CLIPS)
    assert len({clip["url"] for clip in OFFICIAL_FIFA_CLIPS}) == 2


def test_french_labels_preserve_source_team_names():
    import pandas as pd
    from fpi.ui.formatting import team_label, event_label, localized_team_frame, localized_description
    assert team_label('Morocco') == 'Maroc'
    assert team_label('Portugal') == 'Portugal'
    assert event_label('Ball Recovery') == 'Récupération de balle'
    source = pd.DataFrame({'team': ['Morocco', 'Portugal'], 'shots': [9, 12]})
    display = localized_team_frame(source)
    assert display['team'].tolist() == ['Maroc', 'Portugal']
    assert source['team'].tolist() == ['Morocco', 'Portugal']
    assert localized_description('Morocco : 9 tirs') == 'Maroc : 9 tirs'


def test_video_fallback_is_external_and_not_embedded():
    from pathlib import Path
    video = (Path(__file__).resolve().parents[1] / 'src/fpi/ui/video.py').read_text(encoding='utf-8')
    assert 'st.link_button(' in video
    assert 'st.video(' not in video
    assert 'erreur 153' in video
