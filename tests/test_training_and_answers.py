from dataclasses import asdict

import pytest

from fpi.ai.context import QUESTIONS, factual_answer
from fpi.training.generator import FOCUSES, generate_session

TEAMS = ("Morocco", "Portugal")


def test_training_sums_duration_and_source_observations(events):
    for duration in (45, 60, 75):
        draft = generate_session(events, TEAMS, "Morocco", FOCUSES[2], duration, 14)
        assert sum(item["Durée (min)"] for item in draft.exercises) == duration
        assert draft.players == 14
        assert draft.duration_minutes == duration
        assert "1 tirs" in draft.observation or "1 tir" in draft.observation
        assert "valider par l'entraîneur" in draft.disclaimer
        assert asdict(draft)["focus"] == FOCUSES[2]


def test_training_rejects_uncontrolled_parameters(events):
    with pytest.raises(ValueError):
        generate_session(events, TEAMS, "Morocco", "Mauvais thème")
    with pytest.raises(ValueError):
        generate_session(events, TEAMS, "Morocco", FOCUSES[0], 80)
    with pytest.raises(ValueError):
        generate_session(events, TEAMS, "Morocco", FOCUSES[0], 60, 4)


def test_fact_explorer_reports_only_observed_values(events):
    answer = factual_answer(events, TEAMS, "Morocco", QUESTIONS[0])
    assert "1 tirs" in answer or "1 tir" in answer
    assert "0 en deuxième" in answer
    p = factual_answer(events, TEAMS, "Morocco", QUESTIONS[1])
    assert "1 passes tentées" in p or "1 passe" in p
    assert "pass.outcome" in p
    assert "aucun modèle IA" in factual_answer(events, TEAMS, "Morocco", QUESTIONS[3])
    with pytest.raises(ValueError):
        factual_answer(events, TEAMS, "Morocco", "Donne un diagnostic tactique certain")


def test_extended_factual_questions_use_only_provider_counts(events):
    entries = factual_answer(events, TEAMS, "Morocco", QUESTIONS[4])
    assert "première mi-temps" in entries and "deuxième" in entries
    xg = factual_answer(events, TEAMS, "Morocco", QUESTIONS[5])
    assert "0.100" in xg and "non disponible" in xg
    comparison = factual_answer(events, TEAMS, "Morocco", QUESTIONS[6])
    assert "Morocco 1" in comparison and "Portugal 1" in comparison
    origins = factual_answer(events, TEAMS, "Morocco", QUESTIONS[7])
    assert "tiers défensif" in origins and "StatsBomb" in origins
    assert len(QUESTIONS) == 8


def test_training_exercise_validator_rejects_invalid_edits(events):
    from copy import deepcopy
    from fpi.training.validation import validate_exercises
    original = generate_session(events, TEAMS, "Morocco", FOCUSES[1], 60, 18).exercises
    assert validate_exercises(original, 60) == []
    assert all("Matériel" in row and "Variante" in row for row in original)
    rows = deepcopy(original)
    rows[0]["Durée (min)"] = -5
    rows[1]["Consigne"] = " "
    errors = validate_exercises(rows, 60)
    assert any("durée" in err for err in errors)
    assert any("Consigne" in err for err in errors)
    assert any("Total exercices" in err for err in errors)
    rows = deepcopy(original)
    rows[0]["Durée (min)"] += 5
    assert any("objectif" in err for err in validate_exercises(rows, 60))
    assert validate_exercises([], 60)
