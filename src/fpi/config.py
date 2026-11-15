"""Paramètres du scénario de référence FPI.

Les identifiants sont une *configuration de sélection*; l'identité réelle du
match est revalidée sur le catalogue officiel à chaque import explicite.
"""
from __future__ import annotations

import os
from pathlib import Path

RAW_BASE_URL = "https://raw.githubusercontent.com/hudl/open-data/master/data"
MATCHES_PATH = "matches/43/106.json"
REFERENCE_MATCH_ID = 3869486
REFERENCE_DATE = "2022-12-10"
REFERENCE_TEAMS = frozenset({"Morocco", "Portugal"})


def data_directory() -> Path:
    """Where runtime data will be cached (never tracked by Git)."""
    configured = os.environ.get("FPI_DATA_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "data" / "raw"
