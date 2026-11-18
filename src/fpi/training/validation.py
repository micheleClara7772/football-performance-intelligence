"""Contrôles des séances éditées avant leur export ; pas de prescription médicale."""
from __future__ import annotations

import math
from numbers import Real
from typing import Any

REQUIRED_TEXT = ("Phase", "Consigne", "Matériel", "Variante", "Point de vigilance")


def validate_exercises(rows: list[dict[str, Any]], target_minutes: int) -> list[str]:
    """Liste les problèmes d'une séance modifiée sans altérer l'entrée de l'utilisateur."""
    problems: list[str] = []
    if not isinstance(rows, list) or not 1 <= len(rows) <= 15:
        return ["La séance doit contenir entre 1 et 15 exercices."]
    duration_total = 0
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            problems.append(f"Exercice {idx} : ligne non structurée.")
            continue
        for key in REQUIRED_TEXT:
            value = row.get(key)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"Exercice {idx} : champ « {key} » vide.")
            elif len(value) > 1500:
                problems.append(f"Exercice {idx} : « {key} » trop long (1 500 caractères max).")
        time = row.get("Durée (min)")
        if (isinstance(time, bool) or not isinstance(time, Real)
                or not math.isfinite(float(time)) or not float(time).is_integer()
                or time < 1 or time > 120):
            problems.append(f"Exercice {idx} : durée entière attendue entre 1 et 120 min.")
        else:
            duration_total += int(time)
    if duration_total != target_minutes:
        problems.append(f"Total exercices : {duration_total} min (objectif : {target_minutes} min).")
    return problems
