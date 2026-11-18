from pathlib import Path
import pytest


def test_app_starts_offline():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    # No source data is shipped. An error on cache absence must not crash the app.
    at = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    assert len(at.exception) == 0
    assert any("Tableau de bord" in s for s in at.sidebar.radio[0].options)
    assert len(at.sidebar.radio[0].options) == 6
    assert at.sidebar.radio[0].options[0] == "Démo vidéo"
    for label in at.sidebar.radio[0].options:
        at.sidebar.radio[0].set_value(label).run()
        assert len(at.exception) == 0, label

def test_official_real_footage_sources_are_provider_hosted():
    from fpi.ui.video import OFFICIAL_FIFA_CLIPS
    assert len(OFFICIAL_FIFA_CLIPS) == 2
    assert all(clip["url"].startswith("https://www.youtube.com/watch?v=") for clip in OFFICIAL_FIFA_CLIPS)
    assert len({clip["url"] for clip in OFFICIAL_FIFA_CLIPS}) == 2
    from fpi.ui.video import OFFICIAL_FIFA_FULL_MATCH
    assert OFFICIAL_FIFA_FULL_MATCH["url"].startswith("https://www.plus.fifa.com/")
    assert "5f1b5797-25d0-4e10-b723-5072b470bae8" in OFFICIAL_FIFA_FULL_MATCH["url"]


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
    assert 'st.iframe(' in video
    assert 'st.iframe(f"https://www.youtube.com/embed/' in video
    assert "OFFICIAL_FIFA_FULL_MATCH[\"url\"]" in video
    assert 'st.iframe(OFFICIAL_FIFA_FULL_MATCH' not in video
    assert 'erreur 153' in video

def test_linux_reference_lock_is_pinned():
    from pathlib import Path
    lock = (Path(__file__).resolve().parents[1] / "requirements/py311-linux.lock").read_text(encoding="utf-8").splitlines()
    names = set()
    for line in lock:
        assert "==" in line and "@" not in line and "git+" not in line
        name, version = line.split("==", 1)
        assert name and version and name.lower() not in names
        names.add(name.lower())
    assert {"streamlit", "pandas", "plotly", "requests", "pytest"}.issubset(names)


def test_guided_navigation_changes_page_without_crash():
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    at = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    assert at.sidebar.radio[0].value == "Démo vidéo"
    next_button = next(b for b in at.button if b.label.startswith("Continuer :"))
    next_button.click().run()
    assert at.sidebar.radio[0].value == "Tableau de bord"
    assert len(at.exception) == 0
