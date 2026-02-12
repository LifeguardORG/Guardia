"""Tests fuer das Konfigurationsmanagement."""

from pathlib import Path

from guardia.config.settings import (
    LlmSettings,
    Settings,
    load_settings,
)


def test_default_llm_settings():
    """Standard-Werte fuer LLM-Einstellungen muessen gesetzt sein."""
    settings = LlmSettings()
    assert settings.host == "http://localhost:11434"
    assert settings.model == "llama3.1:8b"
    assert settings.max_tokens == 1024
    assert settings.temperature == 0.1


def test_load_settings_from_default_toml():
    """Settings aus default.toml laden – Werte muessen mit Datei uebereinstimmen."""
    settings = load_settings()
    assert settings.llm.host == "http://localhost:11434"
    assert settings.llm.model == "llama3.1:8b"
    assert settings.detection.risk_threshold == 0.6
    assert settings.detection.pattern_weight == 0.4
    assert settings.data.raw_dir == "data/raw"


def test_load_settings_nonexistent_file():
    """Wenn Config-Datei nicht existiert, werden Defaults verwendet."""
    settings = load_settings(Path("/nicht/vorhanden/config.toml"))
    assert isinstance(settings, Settings)
    assert settings.llm.host == "http://localhost:11434"


def test_settings_complete():
    """Gesamte Settings-Struktur muss alle Teilbereiche enthalten."""
    settings = Settings()
    assert hasattr(settings, "llm")
    assert hasattr(settings, "detection")
    assert hasattr(settings, "data")
