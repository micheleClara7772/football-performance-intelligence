"""Parcours réel Streamlit via navigateur Chromium headless, avec captures de preuve."""
from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("FPI_BROWSER_URL", "http://127.0.0.1:8501")
OUT = Path(os.environ.get("FPI_SCREENSHOT_DIR", "outputs/browser-proof"))
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    with sync_playwright() as tool:
        browser = tool.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=1)
        page.goto(BASE, wait_until="domcontentloaded", timeout=60_000)
        page.get_by_role("heading", name="Dashboard collectif").wait_for(timeout=90_000)
        page.get_by_text("Événements validés").first.wait_for(timeout=60_000)
        page.locator('[data-testid="stPlotlyChart"]').first.wait_for(timeout=45_000)
        assert not page.get_by_text("Aucune donnée vérifiée en cache.").count()
        page.screenshot(path=str(OUT / "01-dashboard.png"), full_page=True)

        sidebar = page.locator('[data-testid="stSidebar"]')
        sidebar.get_by_text("Analyse tactique", exact=True).click()
        page.get_by_role("heading", name="Analyse tactique · indicateurs observés").wait_for(timeout=90_000)
        page.get_by_text("Comparaison des mi-temps", exact=True).first.wait_for(timeout=60_000)
        assert page.locator('[data-testid="stPlotlyChart"]').count() >= 1
        page.screenshot(path=str(OUT / "02-analyse-tactique.png"), full_page=True)

        sidebar.get_by_text("Assistant IA", exact=True).click()
        page.get_by_role("heading", name="Assistant IA · fondation factuelle").wait_for(timeout=60_000)
        page.get_by_role("button", name="Obtenir la réponse calculée").click()
        page.get_by_text("Source : StatsBomb Open Data", exact=False).last.wait_for(timeout=60_000)
        page.screenshot(path=str(OUT / "03-assistant-factuel.png"), full_page=True)

        sidebar.get_by_text("Séances", exact=True).click()
        page.get_by_role("heading", name="Générateur de séances · propositions modifiables").wait_for(timeout=60_000)
        page.get_by_role("button", name="Proposer une séance").click()
        page.get_by_role("button", name="Exporter la proposition en JSON").wait_for(timeout=60_000)
        page.screenshot(path=str(OUT / "04-seances.png"), full_page=True)

        sidebar.get_by_text("Vidéo", exact=True).click()
        page.get_by_role("heading", name="Vidéo et annotations").wait_for(timeout=60_000)
        page.get_by_text("Stratégie vidéo ouverte", exact=False).wait_for(timeout=60_000)
        page.screenshot(path=str(OUT / "05-video-non-arbitree.png"), full_page=True)

        assert page.locator('[data-testid="stException"]').count() == 0
        browser.close()
        print("FPI_BROWSER_SMOKE=PASS, five pages, screenshots in", OUT)


if __name__ == "__main__":
    main()
