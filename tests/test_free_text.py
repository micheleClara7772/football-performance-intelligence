"""Questions libres, métriques strictes et refus des diagnostics non sourcés."""
import pytest

from fpi.ai.free_text import free_text_answer

TEAMS = ("Morocco", "Portugal")


@pytest.mark.parametrize("prompt,expected", [
    ("Combien de tirs du Maroc ?", ("Morocco : 1", "tirs")),
    ("Quel xG pour le Maroc en première mi-temps ?", ("0.1", "1re mi-temps")),
    ("Compare les tirs du Maroc et du Portugal", ("Morocco : 1", "Portugal : 1")),
    ("Combien de passes du Maroc ?", ("Morocco : 2", "1 réussies")),
    ("Combien de pressions en seconde période ?", ("2e mi-temps", "pressions")),
    ("Qui sont les joueurs avec le plus de tirs ?", ("Player A", "Joueurs")),
    ("Quand les tirs ont eu lieu ?", ("1re mi-temps 1", "2e mi-temps 0")),
    ("Analyse et bilan du Maroc", ("tirs", "passes")),
    ("Quels buts ont été marqués ?", ("buts", "Morocco")),
    ("Les tirs entre 30 et 45 minutes au Maroc", ("minutes 30 à 45", "Morocco : 1")),
])
def test_free_text_questions(events, match, prompt, expected):
    answer = free_text_answer(events, TEAMS, "Morocco", prompt, match=match)
    for value in expected:
        assert value in answer, (prompt, answer)


def test_unanswerable_question_states_limit(events):
    answer = free_text_answer(events, TEAMS, "Morocco", "Pourquoi le Maroc a-t-il gagné ?")
    assert "ne peux pas" in answer and "causalité" in answer
    answer = free_text_answer(events, TEAMS, "Morocco", "Quelle était la vitesse maximale des joueurs ?")
    assert "ne peux pas" in answer
    unknown = free_text_answer(events, TEAMS, "Morocco", "Peux-tu me conseiller une couleur de maillot ?")
    assert "mesure fiable" in unknown
    for invalid in ("", "a", "x" * 601):
        with pytest.raises(ValueError):
            free_text_answer(events, TEAMS, "Morocco", invalid)
    with pytest.raises(ValueError):
        free_text_answer(events, TEAMS, "Spain", "Les tirs de Maroc")


def test_source_not_video_and_no_paid_service(events):
    answer = free_text_answer(events, TEAMS, "Morocco", "Interceptions et récupérations")
    assert "StatsBomb Open Data" in answer and "analyse vidéo" in answer
