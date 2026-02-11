# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektuebersicht

**betrugserkennung** – Scam-Erkennung fuer Kleinanzeigen (deutsche Kleinanzeigen-Plattform) mittels lokalem LLM. Lizenz: MIT (LifeguardORG).

Kleinanzeigen ist eine Plattform, die sowohl aus Kaeufer- als auch Verkaeufersicht haeufig von Betrug betroffen ist. Dieses Projekt erkennt Betrug in Chat-Nachrichten mit einem **Hybrid-Ansatz**:

1. **Mustererkennung**: Kuratierte YAML-Datenbank bekannter Betrugsmaschen wird gegen Chat-Text abgeglichen.
2. **LLM-Analyse**: Ein lokales Sprachmodell (Ollama) bewertet Chats auf verdaechtiges Verhalten.
3. **Kontextsignale**: Chat-Metadaten (Anzahl Nachrichten, Timing, etc.) fliessen in den Risiko-Score ein.

Alle Daten bleiben lokal – kein Datentransfer nach aussen. Harte Anforderung fuer DSGVO-Konformitaet.

## Architektur

```
GUI / CLI --> Detection Engine (analyzer.py)
                    |
         +----------+----------+
         |                     |
  Pattern Matcher         LLM Client
  (patterns.yaml)        (Ollama API)
         |                     |
         +----------+----------+
                    |
              Risk Scoring
                    |
           Detection Result

Scraper --> Betrugsberichte --> LLM-Extraktion --> patterns.yaml
```

### Module

- **`src/betrugserkennung/config/`** – Einstellungen via Pydantic + TOML. Defaults in `default.toml`.
- **`src/betrugserkennung/data/`** – Chat-Daten laden, aufbereiten, Datenmodelle (schemas).
- **`src/betrugserkennung/patterns/`** – Betrugsmuster-YAML-Datenbank, Registry und Matcher.
- **`src/betrugserkennung/llm/`** – Lokale LLM-Abstraktion. Aktuell: Ollama. Austauschbar via `client.py`-Interface.
- **`src/betrugserkennung/training/`** – Offline-Pipeline: Datensatz-Aufbereitung, Training, Evaluation.
- **`src/betrugserkennung/detection/`** – Kern-Engine: orchestriert Mustererkennung + LLM-Analyse zu Risiko-Score.
- **`src/betrugserkennung/gui/`** – Test-Weboberflaeche (Gradio/Streamlit) zum schnellen Testen von Chat-Analysen.
- **`src/betrugserkennung/scraper/`** – Automatisches Sammeln von Betrugsberichten (Web, Reddit) und Muster-Extraktion.
- **`src/betrugserkennung/cli/`** – Click-basierte CLI. Einstiegspunkt: `betrugserkennung.cli.main:cli`.

## Tech Stack

- **Python 3.14** (venv unter `.venv/`)
- **Ollama** fuer lokale LLM-Inferenz
- **PyYAML** fuer Betrugsmuster-Definitionen
- **Pydantic** fuer Konfiguration und Datenvalidierung
- **Click** fuer CLI
- **Rich** fuer Terminal-Ausgabe
- **Gradio** oder **Streamlit** fuer Test-GUI
- **requests + BeautifulSoup4** fuer Web-Scraping
- **pytest** fuer Tests
- **Ruff** fuer Linting/Formatierung

## Kommandos

```bash
# Entwicklungsmodus installieren
pip install -e ".[dev]"

# Tests ausfuehren
pytest

# Linter pruefen
ruff check src/ tests/

# Code formatieren
ruff format src/ tests/

# Chat analysieren
betrugserkennung analyze path/to/chat.txt

# Betrugsmuster auflisten
betrugserkennung patterns list

# Test-GUI starten
betrugserkennung gui

# Betrugsberichte scrapen
betrugserkennung scrape --all

# Evaluation ausfuehren
betrugserkennung evaluate --data data/labeled/
```

## Konventionen

- **Sprache**: Ordnernamen und CLI-Kommandos auf Englisch. Kommentare, Docstrings und Beschreibungen auf Deutsch.
- **Imports**: Absolute Imports aus `betrugserkennung.*`.
- **Type Hints**: Pflicht bei allen oeffentlichen Funktionen.
- **Tests**: Spiegeln die `src/`-Struktur unter `tests/`. Fixtures in `conftest.py`.
- **Konfiguration**: Keine hardcodierten Pfade oder Modellnamen. Alles ueber `config/settings.py`.
- **Datenschutz**: Niemals echte Chat-Daten loggen, speichern oder uebertragen. Test-Fixtures verwenden ausschliesslich synthetische Daten.

## Projektziele

- **Zielgenauigkeit**: 95% True-Positive-Rate bei Betrugschats (Kaeuferperspektive).
- **Fokus**: Kaeufer-seitige Betrugserkennung zuerst.
- **Vision**: Hobby-Projekt → Open Source → potenzielles Business-Projekt fuer Kleinanzeigen.

## Datenverzeichnis

Der `data/`-Ordner im Projekt-Root enthaelt Laufzeitdaten (gitignored):
- `data/raw/` – Rohe Chat-Exporte vom Nutzer.
- `data/processed/` – Aufbereitete und normalisierte Chats.
- `data/labeled/` – Gelabelte Chats (`normal` oder `scam`) fuer Training/Evaluation.

Siehe `data/README.md` fuer erwartete Formate.
