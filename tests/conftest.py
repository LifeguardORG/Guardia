"""Gemeinsame Test-Fixtures fuer die gesamte Testsuite."""

from pathlib import Path

import pytest

# Pfad zum Testdaten-Verzeichnis
TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture
def sample_normal_chat() -> str:
    """Gibt einen synthetischen normalen Chat zurueck."""
    return (TEST_DATA_DIR / "sample_chat_normal.txt").read_text(encoding="utf-8")


@pytest.fixture
def sample_scam_chat() -> str:
    """Gibt einen synthetischen Betrugschat zurueck."""
    return (TEST_DATA_DIR / "sample_chat_scam.txt").read_text(encoding="utf-8")
