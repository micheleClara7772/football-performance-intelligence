"""Run with dedicated staff/coach accounts. Creates one review dossier on the target."""
import json
import os
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

URL = os.environ["FPI_TEST_URL"].rstrip("/")
OUT = Path(os.environ.get("FPI_CAPTURE_DIR", "/tmp/fpi-receipts"))
OUT.mkdir(parents=True, exist_ok=True)


def login(driver, role):
    opts = {"headless": True}
    if os.getenv("FPI_BROWSER_PATH"):
        opts["executable_path"] = os.environ["FPI_BROWSER_PATH"]
    if os.getenv("FPI_BROWSER_ARGS"):
        opts["args"] = json.loads(os.environ["FPI_BROWSER_ARGS"])
    if os.getenv("FPI_TEST_PROXY"):
        opts["proxy"] = {"server": os.environ["FPI_TEST_PROXY"]}
    browser = driver.chromium.launch(**opts)
    page = browser.new_page(locale="fr-FR")
    page.set_default_timeout(45000)
    page.goto(URL, wait_until="domcontentloaded")
    page.get_by_label("Identifiant").fill(os.environ[f"FPI_{role}_NAME"])
    page.get_by_label("Mot de passe").fill(os.environ[f"FPI_{role}_PASSWORD"])
    page.get_by_role("button", name="Se connecter").click()
    expect(page.get_by_role("heading", name="Dossiers tactiques")).to_be_visible(timeout=45000)
    return browser, page


def capture(page, role):
    for width in (375, 768, 1024, 1440):
        page.set_viewport_size({"width": width, "height": 900})
        page.evaluate("window.scrollTo(0,0)")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(OUT / f"{role}-{width}.png"))


def action_request(action):
    def matches(response):
        return (response.url.endswith("/api/portal") and response.request.method == "POST"
                and response.request.post_data_json.get("action") == action)
    return matches


with sync_playwright() as driver:
    staff_browser, staff = login(driver, "STAFF")
    capture(staff, "staff")
    staff.get_by_label("Scénario").select_option("Transitions après perte")
    with staff.expect_response(action_request("create")) as created:
        staff.get_by_role("button", name="Lancer l’analyse").click()
    dossier = created.value.json()["id"]
    staff.get_by_role("button", name="Ouvrir la revue").click()
    staff.get_by_role("button", name="Valider les observations retenues").wait_for()
    staff.locator("details.evidence summary").first.click()
    staff.locator("textarea").first.fill("Contrôle de recette sur un événement StatsBomb.")
    staff.locator("select[name=decision]").first.select_option("Retenue")
    staff.get_by_role("button", name="Enregistrer la décision").first.click()
    expect(staff.get_by_text("1 observation(s) retenue(s) pour publication.")).to_be_visible(timeout=45000)
    coach_browser, coach = login(driver, "COACH")
    open_dossier = coach.locator('[data-action="open:'+dossier+'"]')
    expect(open_dossier).to_have_count(0)
    staff.get_by_role("button", name="Valider les observations retenues").click()
    staff.get_by_role("button", name="Publier pour l’entraîneur").click()
    staff.get_by_role("button", name="Préparer une nouvelle version").wait_for()
    coach.get_by_role("button", name="Mes dossiers").click()
    open_dossier.click()
    coach.get_by_role("heading", name="Observations validées").wait_for()
    capture(coach, "coach")
    coach.get_by_label("Recherche factuelle").fill("Compare les pertes entre les mi-temps")
    coach.get_by_role("button", name="Rechercher").click()
    expect(coach.locator("#answer")).to_contain_text("1 action(s)", timeout=45000)
    with coach.expect_download() as download:
        coach.get_by_role("button", name="Exporter le dossier JSON").click()
    assert len(json.loads(download.value.path().read_text())["items"]) == 1
    print("Staff, publication, entraîneur, recherche, export, quatre largeurs : OK.")
    coach_browser.close()
    staff_browser.close()
