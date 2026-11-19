"""Parcours réel Streamlit via navigateur Chromium headless, avec captures de preuve."""
from __future__ import annotations

import json
import os
import time
from urllib.error import URLError
from urllib.request import urlopen
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("FPI_BROWSER_URL", "http://127.0.0.1:8501")
OUT = Path(os.environ.get("FPI_SCREENSHOT_DIR", "outputs/browser-proof"))
OUT.mkdir(parents=True, exist_ok=True)


def wait_for_server(timeout: int = 90) -> None:
    """Attendre la santé de Streamlit avant toute connexion navigateur."""
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            with urlopen(BASE + "/_stcore/health", timeout=3) as response:
                if response.status == 200:
                    return
        except (OSError, URLError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"Streamlit inaccessible après {timeout}s : {last_error}")


def main() -> None:
    wait_for_server()
    with sync_playwright() as tool:
        browser = tool.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=1, accept_downloads=True)
        page.goto(BASE, wait_until="domcontentloaded", timeout=60_000)
        page.get_by_role("heading", name="Maroc 1 – 0 Portugal · Coupe du monde 2022").wait_for(timeout=90_000)
        page.get_by_text("Événements validés").first.wait_for(timeout=60_000)
        page.locator('[data-testid="stPlotlyChart"]').first.wait_for(timeout=45_000)
        assert not page.get_by_text("Les actions du match ne sont pas encore chargées.").count()
        page.screenshot(path=str(OUT / "01-dashboard.png"), full_page=True)

        sidebar = page.locator('[data-testid="stSidebar"]')
        sidebar.get_by_text("Analyse tactique", exact=True).click()
        page.get_by_role("heading", name="Analyse tactique · indicateurs observés").wait_for(timeout=90_000)
        page.get_by_text("Comparaison des mi-temps", exact=True).first.wait_for(timeout=60_000)
        assert page.locator('[data-testid="stPlotlyChart"]').count() >= 1
        page.screenshot(path=str(OUT / "02-analyse-tactique.png"), full_page=True)
        page.get_by_role("tab", name="Signaux avancés").click()
        page.get_by_text("Signaux avancés sur la totalité du match").wait_for(timeout=45_000)
        page.get_by_text("Passes progressives (proxy)").first.wait_for(timeout=45_000)
        page.screenshot(path=str(OUT / "02d-signaux-avances.png"), full_page=True)
        page.get_by_role("tab", name="Annotations").click()
        page.get_by_text("Annotations d'événements vérifiés").wait_for(timeout=45_000)
        page.get_by_role("textbox", name="Observation tactique ou hypothèse à vérifier").fill(
            "Note de validation du parcours sur un événement réel, sans vidéo copiée."
        )
        page.get_by_role("button", name="Enregistrer l'annotation").click()
        page.get_by_text("Annotation enregistrée dans cette session", exact=False).wait_for(timeout=45_000)
        page.get_by_role("button", name="Exporter les annotations en JSON").wait_for(timeout=45_000)
        page.screenshot(path=str(OUT / "02b-annotations-evenements.png"), full_page=True)
        with page.expect_download(timeout=45_000) as file_event:
            page.get_by_role("button", name="Exporter les annotations en JSON").click()
        output_notes = OUT / "temporary-annotations.json"
        file_event.value.save_as(str(output_notes))
        exported = json.loads(output_notes.read_text(encoding="utf-8"))
        assert exported["match_id"] == 3869486
        assert exported["schema_version"] == 2
        assert exported["video_sync"] == "manual_player_clock_only"
        assert len(exported["annotations"]) == 1
        assert exported["annotations"][0]["note"].startswith("Note de validation")

        # Nouvelle session navigateur : export/import réels, sans re-saisie ni faux événements.
        fresh = browser.new_context(viewport={"width": 1440, "height": 960}, accept_downloads=True)
        imported_page = fresh.new_page()
        imported_page.goto(BASE, wait_until="domcontentloaded", timeout=60_000)
        imported_page.get_by_role("heading", name="Maroc 1 – 0 Portugal · Coupe du monde 2022").wait_for(timeout=90_000)
        imported_page.locator('[data-testid="stSidebar"]').get_by_text("Analyse tactique", exact=True).click()
        imported_page.get_by_role("tab", name="Annotations").click()
        imported_page.locator('input[type="file"]').set_input_files(str(output_notes))
        imported_page.get_by_role("button", name="Charger les annotations du fichier").click()
        from playwright.sync_api import expect
        expect(imported_page.get_by_role("textbox", name="Observation tactique ou hypothèse à vérifier")).to_have_value(
            "Note de validation du parcours sur un événement réel, sans vidéo copiée.",
            timeout=45_000,
        )
        imported_page.screenshot(path=str(OUT / "02c-annotations-reimport.png"), full_page=True)
        fresh.close()
        output_notes.unlink(missing_ok=True)

        sidebar.get_by_text("Questions", exact=True).click()
        page.get_by_role("heading", name="Questions sur le match").wait_for(timeout=60_000)
        ask = page.locator('[data-testid="stChatInput"] textarea')
        ask.fill("Compare les tirs du Maroc et du Portugal")
        ask.press("Enter")
        page.get_by_text("Maroc : 9", exact=False).wait_for(timeout=45_000)
        page.get_by_text("Portugal : 12").wait_for(timeout=45_000)
        page.screenshot(path=str(OUT / "03-assistant-factuel.png"), full_page=True)

        sidebar.get_by_text("Séances", exact=True).click()
        page.get_by_role("heading", name="Préparer une séance").wait_for(timeout=60_000)
        page.get_by_role("button", name="Proposer une séance").click()
        page.get_by_role("button", name="Exporter la proposition en JSON").wait_for(timeout=60_000)
        page.screenshot(path=str(OUT / "04-seances.png"), full_page=True)

        sidebar.get_by_text("Revoir les actions", exact=True).click()
        page.get_by_role("heading", name="Revoir les actions · Maroc – Portugal").wait_for(timeout=60_000)
        page.get_by_role("link", name="Ouvrir Maroc–Portugal en intégralité sur FIFA+").wait_for(timeout=60_000)
        page.get_by_role("link", name="Regarder ce résumé sur YouTube (solution fiable)").wait_for(timeout=60_000)
        assert page.locator('iframe[src*="plus.fifa.com"]').count() == 0
        assert page.locator('input[type="file"]').count() == 0, "L'écran du coach ne demande pas d'upload"
        page.get_by_role("tab", name="Explorer les actions").click()
        page.get_by_text("Retrouver les moments importants").wait_for(timeout=45_000)
        page.get_by_text("Actions trouvées").wait_for(timeout=45_000)
        page.get_by_role("button", name="Comprendre les différences entre les équipes").click()
        page.get_by_role("heading", name="Analyse tactique · indicateurs observés").wait_for(timeout=45_000)
        assert page.locator('[data-testid="stException"]').count() == 0
        sidebar.get_by_text("Démo technique", exact=True).click()
        page.get_by_role("heading", name="Démonstration technique · suivi de joueurs").wait_for(timeout=45_000)
        player = page.locator("video").first
        player.wait_for(timeout=30_000)
        page.wait_for_function(
            "() => { const v = document.querySelector('video'); "
            "return v && v.readyState >= 1 && v.videoWidth > 0; }",
            timeout=45_000,
        )
        duration = player.evaluate("v => v.duration")
        assert 11 <= duration <= 13, f"Durée MP4 H264 imprévue: {duration}"
        print("FPI_REAL_BROWSER_VIDEO=DECODABLE_H264_12S", duration)
        page.screenshot(path=str(OUT / "00-demo-video-sans-upload.png"), full_page=True)
        page.get_by_role("button", name="Explorer l'analyse tactique").click()
        page.get_by_role("heading", name="Analyse tactique · indicateurs observés").wait_for(timeout=45_000)
        sidebar.get_by_text("Démo technique", exact=True).click()
        page.get_by_role("button", name="Revoir les actions Maroc–Portugal").click()
        page.get_by_role("heading", name="Revoir les actions · Maroc – Portugal").wait_for(timeout=45_000)
        assert page.locator('[data-testid="stException"]').count() == 0
        page.get_by_role("button", name="Continuer : Analyse tactique").click()
        page.get_by_role("heading", name="Analyse tactique · indicateurs observés").wait_for(timeout=45_000)
        assert page.locator('[data-testid="stException"]').count() == 0
        browser.close()
        print("FPI_BROWSER_SMOKE=PASS, coach actions and both video-demo callbacks, screenshots in", OUT)


if __name__ == "__main__":
    main()
