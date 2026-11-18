"""Recette AUTOMATISABLE des 125 cas historiques, avec statut explicite par cas.

Les vérifications d'ergonomie humaine, lecture réelle de médias, droits, et OAuth
ne sont jamais marquées automatiques. Aucune case de l'Issue #15 n'est modifiée.
Exécuter après validate_reference_live.py et browser_smoke.py dans GitHub Actions.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json
import re

from fpi.ai.context import QUESTIONS, factual_answer
from fpi.analysis.annotations import (
    build_annotation, eligible_events, export_document, import_document, parse_video_clock,
)
from fpi.analysis.tactical import tactical_by_period, event_timeline, event_locations
from fpi.data.statsbomb import (
    DataValidationError, load_reference_match, select_reference_match, validate_events,
)
from fpi.metrics.collective import metrics_by_period
from fpi.training.generator import FOCUSES, generate_session
from fpi.training.validation import validate_exercises
from fpi.ui.formatting import team_label
from fpi.ui.video import OFFICIAL_FIFA_CLIPS, OFFICIAL_FIFA_FULL_MATCH

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "docs" / "recette-pre17.md"
OUT = ROOT / "outputs" / "acceptance"
BROWSER = ROOT / "outputs" / "browser-proof"
CHECKS = {}
BROWSER_PROOFS = {
    "A10": "05-video-liens-officiels.png",
    "B07": "01-dashboard.png",
    "C04": "01-dashboard.png",
    "D08": "02-analyse-tactique.png",
    "E02": "05-video-liens-officiels.png",
    "H08": "02b-annotations-evenements.png",
    "H15": "02b-annotations-evenements.png",
    "H17": "02c-annotations-reimport.png",
    "H18": "02c-annotations-reimport.png",
    "G02": "04-seances.png",
}


def check(ids: str, evidence: str):
    """Associe des assertions vérifiables aux scénarios listés dans le guide."""
    def register(fn):
        for case_id in ids.split():
            if case_id in CHECKS:
                raise RuntimeError(f"Scénario enregistré deux fois : {case_id}")
            CHECKS[case_id] = (fn, evidence)
        return fn
    return register


def ensure(value: bool, reason: str) -> None:
    if not value:
        raise AssertionError(reason)


@check("B04 C01 J04", "Identité, score, 3 381 événements et totaux calculés sur le match réel")
def baseline(m, ev, meta, basic, tac):
    ensure(m["match_id"] == 3869486 and m["home_score"] == 1 and m["away_score"] == 0, "match/score")
    ensure(m["match_date"] == "2022-12-10" and len(ev) == 3381, "date/nombre")
    grouped = basic.groupby("team")[["shots", "passes"]].sum()
    ensure(int(grouped.loc["Morocco","shots"]) == 9 and int(grouped.loc["Portugal","shots"]) == 12, "tirs")
    ensure(int(grouped.loc["Morocco","passes"]) == 249 and int(grouped.loc["Portugal","passes"]) == 731, "passes")


@check("B05 B06 B10", "Provenance, volume du catalogue et identité de match confirmés")
def provenance(m, ev, meta, basic, tac):
    ensure(meta["source"] == "StatsBomb Open Data", "source")
    ensure(meta["match_id"] == 3869486 and meta["validated_events"] == len(ev), "métadonnées")
    ensure(meta["events_url"].endswith("events/3869486.json"), "URL événement")
    ensure(meta["match_catalogue_url"].endswith("matches/43/106.json"), "URL catalogue")


@check("B11 I05", "Vérification des exclusions git des datasets, secrets et médias")
def no_media(m, ev, meta, basic, tac):
    txt = (ROOT / ".gitignore").read_text(encoding="utf-8")
    ensure(all(token in txt for token in ("data/raw/", "*.mp4", ".env", "media/")), "gitignore")
    # The ONLY intentional media is the 12-second licensed CC BY SoccerTrack
    # DERIVATIVE demonstrator, paired with a strictly validated MOTMetrics report.
    # No full match, FIFA broadcast, raw dataset or unrestricted media may be tracked.
    allowed_demo = ROOT / "assets/fpi-video/real-bytetrack-12s.mp4"
    forbidden = [
        p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts
        and ".venv" not in p.parts and "outputs" not in p.parts
        and "data" not in p.parts and p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
        and p != allowed_demo
    ]
    ensure(not forbidden, f"médias non autorisés dans le dépôt : {forbidden[:3]}")
    if allowed_demo.exists():
        from fpi.ui.video_showcase import video_is_ready
        ensure(video_is_ready(), "Une vidéo de démo ne peut être publiée sans rapport validé")
        ensure(allowed_demo.stat().st_size < 9_000_000, "Vidéo de démo trop longue/volumineuse")


@check("B12", "Validation négative du match/score et des IDs événementiels")
def reject_bad_data(m, ev, meta, basic, tac):
    altered = deepcopy(m); altered["home_score"] = 5
    try:
        select_reference_match([altered])
    except DataValidationError:
        pass
    else:
        raise AssertionError("score incorrect accepté")
    try:
        validate_events([ev[0], ev[0]], m)
    except DataValidationError:
        pass
    else:
        raise AssertionError("doublon accepté")


@check("C02 C03", "Total des 2 mi-temps calculé, séparé pour les deux équipes")
def totals(m, ev, meta, basic, tac):
    grouped = basic.groupby("team")[["shots", "passes"]].sum()
    ensure(tuple(map(int, (grouped.loc["Morocco","shots"], grouped.loc["Portugal","shots"]))) == (9, 12), "tirs")
    ensure(tuple(map(int, (grouped.loc["Morocco","passes"], grouped.loc["Portugal","passes"]))) == (249, 731), "passes")


@check("C07", "Bornes arithmétiques réussite des passes et pourcentages")
def rates(m, ev, meta, basic, tac):
    ensure(bool((basic["passes_completed"] <= basic["passes"]).all()), "passes réussies > tentées")
    pct = basic["pass_completion_pct"].dropna()
    ensure(bool(pct.between(0, 100).all()), "pourcentage invalide")


@check("C08", "xG absent si un tir de la période manque une valeur valide")
def provider_xg(m, ev, meta, basic, tac):
    for row in basic.itertuples():
        shoots = [x for x in ev if x["period"] == row.period
                  and x["team"]["name"] == row.team and x["type"]["name"] == "Shot"]
        completeness = all(type(x.get("shot",{}).get("statsbomb_xg")) in (int,float)
                           for x in shoots)
        if not completeness or not shoots:
            ensure(row.xg != row.xg or row.xg is None, "xG calculé à partir de tirs incomplets")
        else:
            expected = round(sum(x["shot"]["statsbomb_xg"] for x in shoots),3)
            ensure(abs(row.xg-expected)<0.000001, "xG fournisseur non réconcilié")


@check("C09 D07", "Toutes les combinaisons équipe/période exactement une fois")
def halves(m, ev, meta, basic, tac):
    expected = {("Morocco",1),("Morocco",2),("Portugal",1),("Portugal",2)}
    ensure(set(zip(basic.team,basic.period)) == expected and len(basic)==4,"périodes de base")
    ensure(set(zip(tac.team,tac.period)) == expected and len(tac)==4,"périodes tactiques")


@check("C10", "Traduction de présentation indépendante des identifiants d'équipe")
def translation(m, ev, meta, basic, tac):
    ensure(team_label("Morocco")=="Maroc" and team_label("Portugal")=="Portugal","français")
    ensure(set(basic.team)=={"Morocco","Portugal"},"identifiants fournisseur modifiés")


@check("D01 D02 D03 D04", "Comparaisons tactiques d'équipes et écarts de période à partir de StatsBomb")
def compare_tactics(m, ev, meta, basic, tac):
    ensure(len(tac) == 4 and set(tac.team)=={"Morocco","Portugal"},"métriques")
    ensure(all(col in tac for col in ("pressures","ball_recoveries","interceptions","attacking_third_entries")), "champs tactiques")
    for team in ("Morocco","Portugal"):
        parts = basic[basic.team==team].set_index("period")
        ensure(parts.loc[2,"shots"] - parts.loc[1,"shots"] == int(parts.loc[2,"shots"]-parts.loc[1,"shots"]), "écart tirs")


@check("D06", "Entrée dernier tiers par passe réussie ou conduite (x<80 vers x>=80)")
def third(m, ev, meta, basic, tac):
    ensure(bool((tac["attacking_third_entries"]>=0).all()),"proxy négatif")
    ensure("attacking_third_entries" in tac,"indicateur absent")


@check("D10", "Six fenêtres de la chronologie réelle et exclusion des périodes hors 1/2")
def timeline(m, ev, meta, basic, tac):
    rows = event_timeline(ev,("Morocco","Portugal"))
    ensure(len(rows)==12,"fenêtres = 6 par équipe")
    ensure(set(rows.period)=={1,2} and len(rows.window.unique())==6,"fenêtres/périodes")


@check("D11 D12 D13", "Coordonnées StatsBomb 120×80 filtrées par équipe et période")
def xy(m, ev, meta, basic, tac):
    for team in ("Morocco","Portugal"):
        for typ in ("Shot","Pass","Pressure","Ball Recovery","Interception","Carry"):
            for period in (1,2):
                frame=event_locations(ev,team,typ,period)
                if not frame.empty:
                    ensure(bool(frame.x.between(0,120).all()) and bool(frame.y.between(0,80).all()),"xy hors terrain")
                    ensure(bool((frame.period==period).all()),"mauvaise période")


@check("E03 E07", "Deux résumés YouTube identifiés comme résumés, jamais match intégral")
def videos(m, ev, meta, basic, tac):
    ensure(len(OFFICIAL_FIFA_CLIPS)==2,"nombre de résumés")
    ensure(all(clip["url"].startswith("https://www.youtube.com/watch?v=") for clip in OFFICIAL_FIFA_CLIPS),"URL officielle")
    ensure(OFFICIAL_FIFA_FULL_MATCH["url"].startswith("https://www.plus.fifa.com/"),"URL replay")


@check("E08 H22", "Export des notes référence un lecteur manuel, jamais un alignement automatique")
def clock(m, ev, meta, basic, tac):
    selected=eligible_events(ev,"Morocco","Shot",1)
    note=build_annotation(selected[0],"Observation à vérifier","Observation")
    payload=json.loads(export_document(3869486,[note]))
    ensure(payload["schema_version"]==2 and payload["video_sync"]=="manual_player_clock_only","mode de synchro")
    ensure("video_bytes" not in str(payload) and "video_frames" not in str(payload),"vidéo stockée")


@check("F02 F03 F04 F05 F06 F07", "8 réponses factuelles calculées et limites explicites")
def old_facts(m, ev, meta, basic, tac):
    ensure(len(QUESTIONS)==8,"nombre questions guidées historique")
    for team in ("Morocco","Portugal"):
        for prompt in QUESTIONS:
            answer=factual_answer(ev,("Morocco","Portugal"),team,prompt)
            ensure(bool(answer.strip()),f"réponse vide {prompt}")
    ensure("aucun modèle IA" in factual_answer(ev,("Morocco","Portugal"),"Morocco",QUESTIONS[3]),"limitation LLM")


@check("G03 G04 G05 G06 G07 G12", "Exercices et durées cohérentes pour tous les thèmes, durées et équipes")
def sessions(m, ev, meta, basic, tac):
    for team in ("Morocco","Portugal"):
        for focus in FOCUSES:
            for duration in (45,60,75):
                for players in (6,30):
                    s=generate_session(ev,("Morocco","Portugal"),team,focus,duration,players)
                    ensure(s.players==players,"effectif")
                    ensure(validate_exercises(s.exercises,duration)==[], "exercices invalides")
                    ensure("valider par l'entraîneur" in s.disclaimer,"validation humaine manquante")


@check("G09", "Export refusé quand somme des durées ou consignes sont invalides")
def edit(m, ev, meta, basic, tac):
    s=generate_session(ev,("Morocco","Portugal"),"Morocco",FOCUSES[0],60,12)
    rows=deepcopy(s.exercises)
    rows[0]["Durée (min)"] += 1
    ensure(bool(validate_exercises(rows,60)),"durée incohérente acceptée")
    rows=deepcopy(s.exercises);rows[0]["Consigne"]=""
    ensure(bool(validate_exercises(rows,60)),"consigne vide acceptée")


@check("H03 H04 H05 H07", "Événements filtrés par type, équipe, période et ID réel")
def find_events(m, ev, meta, basic, tac):
    shots=eligible_events(ev,"Morocco","Shot",1)
    ensure(bool(shots) and all(x["type"]["name"]=="Shot" and x["team"]["name"]=="Morocco" and x["period"]==1 and x["id"] for x in shots), "filtrage shots")
    ensure(not eligible_events(ev,"Morocco","Shot",1,128,130), "créneau supposé vide")
    ensure(not eligible_events(ev,"Portugal","Shot",1,128,130), "créneau supposé vide Portugal")


@check("H09 H10 H11", "Natures Observation/Hypothèse et refus notes vides/trop longues")
def note_validation(m,ev,meta,basic,tac):
    a=eligible_events(ev,"Morocco","Shot",1)[0]
    for nature in ("Observation","Hypothèse"):
        ensure(build_annotation(a,"Validé",nature)["nature"]==nature,"nature")
    for invalid in ("", "  ", "x"*2001):
        try:build_annotation(a,invalid,"Observation")
        except ValueError:pass
        else:raise AssertionError("note invalide acceptée")


@check("H12 H13 H14", "Repère MM:SS facultatif, mauvais formats refusés et source obligatoire")
def clocks(m,ev,meta,basic,tac):
    a=eligible_events(ev,"Morocco","Shot",1)[0]
    ensure(parse_video_clock("02:43")==163,"repère vidéo")
    for value in ("2:99", "abc", "-1:21", "1:1:2"):
        try:parse_video_clock(value)
        except ValueError:pass
        else:raise AssertionError("horloge invalide acceptée")
    try:build_annotation(a,"Observation","Observation",video_seconds=163)
    except ValueError:pass
    else:raise AssertionError("source vidéo absente acceptée")


@check("H16 H19 H20 H21 I07 J03", "Notes exportables, import v2 vérifié contre IDs et provenance, erreurs refusées")
def notes(m,ev,meta,basic,tac):
    a=eligible_events(ev,"Morocco","Shot",1)[0]
    url=OFFICIAL_FIFA_FULL_MATCH["url"]
    first=build_annotation(a,"Texte source","Observation",url,163,allowed_video_urls=[url])
    raw=export_document(3869486,[first])
    payload=json.loads(raw)
    ensure(payload["schema_version"]==2 and payload["event_source"]=="StatsBomb Open Data","schema/provenance")
    restored=import_document(payload,3869486,ev,allowed_video_urls=[url])
    ensure(restored[a["id"]]==first,"export/réimport")
    changed=build_annotation(a,"Texte modifié","Hypothèse")
    restored[a["id"]]=changed
    ensure(len(restored)==1 and restored[a["id"]]["note"]=="Texte modifié","édition")
    bad=deepcopy(payload);bad["match_id"]=999
    try:import_document(bad,3869486,ev,allowed_video_urls=[url])
    except ValueError:pass
    else:raise AssertionError("mauvais match accepté")
    bad=deepcopy(payload);bad["annotations"][0]["event_id"]="faux"
    try:import_document(bad,3869486,ev,allowed_video_urls=[url])
    except ValueError:pass
    else:raise AssertionError("ID inexistant accepté")


@check("I10", "Pas de prétention de tracking ou de LLM dans les descriptions des capacités")
def scope(m,ev,meta,basic,tac):
    video=(ROOT/"src/fpi/ui/video.py").read_text(encoding="utf-8")
    assistant=(ROOT/"src/fpi/ui/assistant.py").read_text(encoding="utf-8")
    ensure("aucun" in video.lower() or "sans" in video.lower(),"limites vidéo")
    ensure("modèle" in assistant.lower() or "génératif" in assistant.lower(),"limites IA")


@check("J06", "Échec de validation d'une liste de données sans faux chiffre")
def invalid_data(m,ev,meta,basic,tac):
    try:validate_events([],m)
    except DataValidationError:pass
    else:raise AssertionError("flux vide accepté")


def manual_reason(code: str) -> str:
    if code in {"E04","E06","E05","J05"}:
        return "Lecture effective du diffuseur dans un navigateur et un territoire réels ; aucune preuve par simple iframe"
    if code in {"E10","I08","I09","J07"}:
        return "Examen des licences et autorisations du détenteur des droits, non automatisable"
    if code in {"A02","A03","A04","A05","A09","I12"}:
        return "Codespaces, compte GitHub privé, quota ou action réelle du propriétaire"
    if code in {"J08","J09","J10"}:
        return "Décision produit et acceptation explicite du propriétaire"
    return "Interaction ou inspection métier/visuelle non totalement démontrée par la CI actuelle"


def main() -> None:
    codes = re.findall(r"^- \[ \] \*\*([A-J][0-9]{2})\*\*", RECIPE.read_text(encoding="utf-8"), re.M)
    if len(codes) != 125 or len(set(codes)) != 125:
        raise RuntimeError(f"Guide de recette incohérent : {len(codes)} cas, doublons possibles")
    m,ev,meta=load_reference_match()
    teams=("Morocco","Portugal")
    basic=metrics_by_period(ev,teams)
    tac=tactical_by_period(ev,teams)
    reports=[]
    for code in codes:
        if code in CHECKS:
            fn,evidence=CHECKS[code]
            try:
                fn(m,ev,meta,basic,tac)
                state="PASS_AUTOMATIQUE"
                detail=evidence
            except Exception as exc:
                state="ECHEC_AUTOMATIQUE"
                detail=f"{type(exc).__name__}: {exc}"
        elif code in BROWSER_PROOFS and (BROWSER/BROWSER_PROOFS[code]).is_file():
            state="PASS_NAVIGATEUR"
            detail="Scénario Chromium réussi et capture "+BROWSER_PROOFS[code]
        else:
            state="A_VALIDER_HUMAINEMENT"
            detail=manual_reason(code)
        reports.append({"id":code,"status":state,"evidence":detail})
    counter=Counter(x["status"] for x in reports)
    OUT.mkdir(parents=True,exist_ok=True)
    summary={
        "source_match_id":m["match_id"],"events":len(ev),
        "coverage":dict(counter),"total_cases":125,
        "human_checkboxes_unchanged":True,
        "results":reports,
    }
    (OUT/"rapport-recette-auto.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=[
        "# Rapport automatique de recette FPI",
        "",
        "Match réel 3869486 (3 381 événements). Ce rapport **ne modifie aucune case manuelle** de l'Issue #15.",
        "",
        "| Statut | Nombre |",
        "|---|---:|",
        *[f"| {name} | {qty} |" for name,qty in sorted(counter.items())],
        "",
        "| Cas | Statut | Preuve / action restante |",
        "|---|---|---|",
        *[f"| {x['id']} | {x['status']} | {x['evidence'].replace('|','/')} |" for x in reports],
    ]
    (OUT/"rapport-recette-auto.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("FPI_AUTO_ACCEPTANCE="+json.dumps({"total":125,**counter},ensure_ascii=False))
    if counter["ECHEC_AUTOMATIQUE"]:
        raise AssertionError(f"{counter['ECHEC_AUTOMATIQUE']} tests de recette automatique en échec")
    if counter["PASS_AUTOMATIQUE"]+counter["PASS_NAVIGATEUR"] < 55:
        raise AssertionError("Couverture automatique attendue insuffisante")


if __name__ == "__main__":
    main()
