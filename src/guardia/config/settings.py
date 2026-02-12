"""Einstellungen fuer Guardia – laedt aus default.toml und Umgebungsvariablen."""

from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from pydantic import BaseModel

# Pfad zur Standard-Konfigurationsdatei (liegt neben diesem Modul)
_DEFAULT_CONFIG_PATH = Path(__file__).parent / "default.toml"


class LlmSettings(BaseModel):
    """Einstellungen fuer die lokale LLM-Verbindung (Ollama)."""

    host: str = "http://localhost:11434"
    model: str = "llama3.1:8b"
    max_tokens: int = 1024
    temperature: float = 0.1


class DetectionSettings(BaseModel):
    """Einstellungen fuer die Betrugserkennung."""

    risk_threshold: float = 0.6
    pattern_weight: float = 0.4


class DataSettings(BaseModel):
    """Pfade fuer Datenverzeichnisse."""

    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    labeled_dir: str = "data/labeled"


class Settings(BaseModel):
    """Gesamte Konfiguration – kombiniert alle Teilbereiche."""

    llm: LlmSettings = LlmSettings()
    detection: DetectionSettings = DetectionSettings()
    data: DataSettings = DataSettings()


def load_settings(config_path: Path | None = None) -> Settings:
    """Laedt Einstellungen aus einer TOML-Datei.

    Args:
        config_path: Pfad zur TOML-Datei. Wenn None, wird default.toml verwendet.

    Returns:
        Settings-Objekt mit allen Einstellungen.
    """
    path = config_path or _DEFAULT_CONFIG_PATH

    if not path.exists():
        # Kein Config-File gefunden → Standard-Werte verwenden
        return Settings()

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    return Settings(**raw)
