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
