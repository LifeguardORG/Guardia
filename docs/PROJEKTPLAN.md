# Projektplan – Guardia

## 1. Vision & Ansprueche

**Was wir bauen:** Eine KI-gestuetzte Scam-Erkennung fuer Kleinanzeigen-Chats.

**Ansprueche:**
- 95% True-Positive-Rate bei Betrugschats
- Lokal & unter DSGVO auswerten – kein Datentransfer nach aussen
- Mit KI-Unterstuetzung (lokales LLM)

**Fokus:**
- Zuerst: Kaeuferperspektive (Kaeufer vor Betrug schuetzen)
- Spaeter: Verkaeuferperspektive (Verkaeufer vor Betrug schuetzen)

**Roadmap:**
1. **Hobby / Versuch** – Funktioniert die Idee ueberhaupt? Prototyp bauen und testen.
2. **Eigene Betaversion** – Stabiles Tool, Open Source, Community-Feedback.
3. **Optionale Vermarktung** – z.B. als Integration bei Kleinanzeigen oder als oeffentlicher Ratgeber.

---

## 2. Gewaelter Ansatz: Hybrid-Loesung

### Warum nicht rein klassisches KI-Learning?
- Braucht >1000 gelabelte Chats (normal vs. Betrug)
- KI lernt Schreibweise und Verhalten
- **Problem:** Wir haben anfangs nicht genug Daten

### Warum nicht rein Betrugs-Muster-Erkennung?
- KI hat Sprachverstaendnis (LLM als Basis)
- Erkennt Betrugsmaschen anhand einer Datenbank
- **Problem:** Erkennt nur bekannte Muster, keine neuen Betrugsarten

### Hybrid-Loesung (unser Weg)
Die KI kombiniert beides:
1. **Sucht nach bekannten Betrugsmustern** (Datenbank)
2. **Gleicht Ergebnis mit trainiertem Verhalten ab** (LLM-Analyse)
3. **Beruecksichtigt Kontext** (Anzahl Nachrichten, Timing, Muster-Kombination)

**Voraussetzungen:**
- Viele Chats als Textform (>100 / 200)
- Datenbank mit Betrugsmustern
- Lokales LLM (Ollama)

---

## 3. Phasen-Uebersicht

| Phase | Name                          | Ziel                                                      |
|-------|-------------------------------|------------------------------------------------------------|
| 1     | LLM-Integration               | Ollama anbinden, Chat an LLM schicken, Antwort bekommen   |
| 2     | Test-GUI                      | Einfache Oberflaeche: Chat eingeben, Ergebnis sehen       |
| 3     | Scam-Methoden & Scraper       | Betrugsmaschen recherchieren, Daten automatisch sammeln    |
| 4     | Mustererkennung               | Pattern-DB + Matcher, Hybrid mit LLM verbinden            |
| 5     | Detection Engine & Scoring    | Alles kombinieren zu einem Risiko-Score                    |
| 6     | Training & Evaluation         | Datensatz-Pipeline, Metriken, 95%-Ziel erreichen          |
| 7     | Polish & Release              | Doku, CI/CD, Open-Source / Beta-Vorbereitung               |

---

## 4. Detaillierte Steps pro Phase

### Phase 1: LLM-Integration

> Ziel: Ollama laeuft, wir koennen einen Chat-Text hinschicken und eine Analyse zurueckbekommen.
> Minimale Infrastruktur (Config, Schemas) wird mitgebaut, soweit noetig.

#### 1.1 Minimale Konfiguration (`src/betrugserkennung/config/`)

- [ ] **`settings.py`** – Pydantic `BaseSettings` fuer LLM-Verbindung
  - `LlmSettings`: `host`, `model`, `max_tokens`, `temperature`
  - Laedt aus `default.toml` und `.env`
- [ ] **`default.toml`** pruefen – Ollama-Defaults muessen stimmen

#### 1.2 Minimale Datenmodelle (`src/betrugserkennung/data/schemas.py`)

- [ ] **`Message`** Dataclass – `sender: str`, `text: str`, `timestamp: datetime | None`
- [ ] **`Chat`** Dataclass – `messages: list[Message]`, `source_file: Path | None`, `metadata: dict`

#### 1.3 LLM Client Interface (`src/betrugserkennung/llm/client.py`)

- [ ] **`LlmResponse`** Dataclass – `verdict: str`, `confidence: float`, `reasoning: str`, `risk_factors: list[str]`
- [ ] **`BaseLlmClient`** Abstrakte Klasse (ABC)
  - `analyze_chat(chat: Chat) -> LlmResponse`
  - `is_available() -> bool`

#### 1.4 Ollama Client (`src/betrugserkennung/llm/ollama_client.py`)

- [ ] **`OllamaClient(BaseLlmClient)`** implementieren
  - `__init__(settings: LlmSettings)`
  - `analyze_chat(chat: Chat) -> LlmResponse` – Ollama API aufrufen
  - `is_available() -> bool` – Server pingen
  - `_build_prompt(chat: Chat) -> str` – Prompt zusammenbauen
  - `_parse_response(raw: str) -> LlmResponse` – JSON-Antwort parsen

#### 1.5 Prompt-Templates (`src/betrugserkennung/llm/prompts.py`)

- [ ] **`SYSTEM_PROMPT`** – "Du bist ein Experte fuer Betrugserkennung auf Kleinanzeigen..."
- [ ] **`ANALYSIS_PROMPT_TEMPLATE`** – Chat-Text + gewuenschtes JSON-Output-Format
- [ ] **`format_chat_for_prompt(chat: Chat) -> str`** – Chat lesbar fuer LLM formatieren

#### 1.6 Tests

- [ ] **`tests/test_ollama_client.py`** – Mock-Test: `analyze_chat()` mit gefakter Antwort
- [ ] **`tests/test_prompts.py`** – Prompt-Formatierung pruefen

#### Erfolgskriterium Phase 1:
> Ollama laeuft lokal. `OllamaClient.analyze_chat(test_chat)` gibt eine strukturierte `LlmResponse` zurueck mit Verdict und Confidence.

---

### Phase 2: Test-GUI

> Ziel: Einfache Weboberflaeche – Chat-Text eingeben, "Analysieren" klicken, Ergebnis sehen.
> Kein Produktions-Frontend, sondern ein schnelles Testtool.

#### 2.1 GUI-Framework einrichten

- [ ] **Abhaengigkeit hinzufuegen**: `gradio` oder `streamlit` in `pyproject.toml`
- [ ] **`src/betrugserkennung/gui/`** Modul erstellen
  - `__init__.py` – Docstring

#### 2.2 Chat-Eingabe-Oberflaeche (`src/betrugserkennung/gui/app.py`)

- [ ] **Chat-Textfeld** – Grosses Eingabefeld fuer kopierten Chat-Verlauf
- [ ] **"Analysieren"-Button** – Sendet Chat an `OllamaClient.analyze_chat()`
- [ ] **Ergebnis-Anzeige**:
  - Verdict (Scam / Kein Scam) mit Farb-Indikator (rot/gruen)
  - Confidence-Score als Balken oder Prozentzahl
  - Begruendung des LLM (reasoning)
  - Erkannte Risikofaktoren als Liste
- [ ] **Ollama-Status** – Anzeige ob LLM erreichbar ist (gruener/roter Punkt)

#### 2.3 Beispiel-Chats

- [ ] **Vorlagen-Dropdown** – "Normaler Chat" und "Scam-Chat" als schnelle Test-Eingaben
  - Laedt aus `tests/test_data/sample_chat_normal.txt` und `sample_chat_scam.txt`

#### 2.4 Startskript

- [ ] **CLI-Kommando**: `betrugserkennung gui` – Startet die Weboberflaeche
- [ ] **Oder**: `python -m betrugserkennung.gui.app` als Direktstart

#### Erfolgskriterium Phase 2:
> Browser oeffnet sich, Chat einfuegen, Button klicken → LLM-Analyse erscheint mit Verdict und Begruendung.

---

### Phase 3: Scam-Methoden sammeln & Scraper

> Ziel: Systematisch Betrugsmaschen recherchieren und Daten sammeln.
> Scraper baut eine Datenbank aus echten Betrugsberichten auf.

#### 3.1 Scam-Methoden recherchieren & dokumentieren

- [ ] **`src/betrugserkennung/patterns/patterns.yaml`** erweitern – Neue Muster aus Recherche
  - Quellen: Verbraucherzentrale, Polizei-Warnungen, Reddit r/Kleinanzeigen, Betrugsberichte
  - Pro Muster: `id`, `name`, `description`, `severity`, `keywords`, `indicators`
- [ ] **Ziel: mindestens 20-30 dokumentierte Betrugsmaschen** (aktuell 10)
  - Neue Kategorien: Fake-Spedition, Treuhand-Betrug, Account-Uebernahme, Fake-Bewertungen, Dreiecks-Masche mit gehackten Accounts, QR-Code-Betrug, etc.

#### 3.2 Scraper-Modul (`src/betrugserkennung/scraper/`)

- [ ] **`__init__.py`** – Docstring
- [ ] **`sources.py`** – Konfiguration der Scraping-Quellen
  - Verbraucherzentrale-Warnungen
  - Polizei-Praevention
  - Reddit / Foren mit Erfahrungsberichten
  - Watchlist Internet
- [ ] **`scraper.py`** – Hauptlogik
  - `BaseScraper` ABC – `scrape() -> list[ScrapedReport]`
  - `ScrapedReport` Dataclass – `source`, `title`, `content`, `date`, `url`
- [ ] **`reddit_scraper.py`** – Reddit-Posts aus relevanten Subreddits scrapen
  - r/Kleinanzeigen, r/de (Betrugs-Posts)
  - Verwendet `praw` (Reddit API) oder `requests` + Parsing
- [ ] **`web_scraper.py`** – Allgemeiner Web-Scraper fuer Warnseiten
  - Verbraucherzentrale, Polizei-Beratung
  - Verwendet `requests` + `beautifulsoup4`
- [ ] **`exporter.py`** – Gescrapte Berichte speichern
  - `export_to_txt(reports: list[ScrapedReport], output_dir: Path)` – Als Textdateien
  - `export_to_json(reports: list[ScrapedReport], output_path: Path)` – Als JSON
  - `update_patterns_yaml(reports: list[ScrapedReport], patterns_path: Path)` – Neue Muster extrahieren und in YAML einfuegen

#### 3.3 LLM-gestuetzte Muster-Extraktion

- [ ] **`pattern_extractor.py`** – LLM analysiert gescrapte Berichte und extrahiert Betrugsmuster
  - `extract_patterns(report: ScrapedReport, llm: BaseLlmClient) -> list[Pattern]`
  - Prompt: "Analysiere diesen Betrugsberucht und extrahiere: Name der Masche, Schluesselwoerter, Warnsignale..."
  - Ergebnisse zur manuellen Pruefung vorschlagen

#### 3.4 CLI-Kommando fuer Scraping

- [ ] **`betrugserkennung scrape`** Kommando
  - `betrugserkennung scrape --source reddit` – Reddit scrapen
  - `betrugserkennung scrape --source web` – Warnseiten scrapen
  - `betrugserkennung scrape --all` – Alle Quellen
  - `betrugserkennung scrape --extract-patterns` – Aus Berichten Muster extrahieren (mit LLM)

#### 3.5 Abhaengigkeiten

- [ ] `pyproject.toml` erweitern: `requests`, `beautifulsoup4`, `praw` (optional) in `[project.optional-dependencies.scraper]`

#### Erfolgskriterium Phase 3:
> `betrugserkennung scrape --all` sammelt Berichte. `patterns.yaml` hat 20+ Muster. Gescrapte Daten liegen in `data/raw/`.

---

### Phase 4: Mustererkennung

> Ziel: Betrugsmuster aus der YAML-DB werden systematisch gegen Chats gematcht.
> Jetzt erst sinnvoll, weil wir ab Phase 3 genug Muster haben.

#### 4.1 Pattern Registry (`src/betrugserkennung/patterns/registry.py`)

- [ ] **`Pattern`** Dataclass – `id`, `name`, `description`, `severity`, `keywords`, `indicators`
- [ ] **`PatternRegistry`** Klasse
  - `load(path: Path) -> PatternRegistry` – YAML laden und validieren
  - `get_all() -> list[Pattern]` – Alle Muster
  - `get_by_id(id: str) -> Pattern | None` – Nach ID
  - `get_by_severity(severity: str) -> list[Pattern]` – Nach Schweregrad
- [ ] **Test: `tests/test_registry.py`**

#### 4.2 Pattern Matcher (`src/betrugserkennung/patterns/matcher.py`)

- [ ] **`PatternMatch`** Dataclass – `pattern`, `matched_keywords`, `matched_messages`, `confidence`
- [ ] **`PatternMatcher`** Klasse
  - `match_chat(chat: Chat) -> list[PatternMatch]`
  - `match_message(message: Message, pattern: Pattern) -> bool`
  - `calculate_confidence(matches: int, total_keywords: int) -> float`
- [ ] **Test: `tests/test_matcher.py`** – Scam-Chat matcht Muster, normaler Chat nicht

#### 4.3 Patterns ins LLM-Prompt integrieren

- [ ] **`prompts.py`** erweitern – `format_patterns_for_prompt(patterns: list[Pattern]) -> str`
- [ ] LLM bekommt bekannte Muster als Kontext → bessere Analyse

#### 4.4 GUI erweitern

- [ ] **Muster-Treffer in GUI anzeigen** – Welche Patterns wurden erkannt? Mit Keywords hervorgehoben.
- [ ] **Pattern-Verwaltung** – Einfache Liste aller Muster in der GUI ansehbar

#### Erfolgskriterium Phase 4:
> Scam-Testchat matcht mindestens 3 Muster. GUI zeigt Muster-Treffer neben LLM-Analyse an.

---

### Phase 5: Detection Engine & Scoring

> Ziel: Muster-Ergebnisse und LLM-Analyse werden zu einem kombinierten Risiko-Score.

#### 5.1 Detection Result (`src/betrugserkennung/detection/result.py`)

- [ ] **`RiskLevel`** Enum – `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- [ ] **`DetectionResult`** Dataclass
  - `risk_score: float` (0.0 – 1.0)
  - `risk_level: RiskLevel`
  - `pattern_matches: list[PatternMatch]`
  - `llm_response: LlmResponse | None`
  - `summary: str`
  - `analyzed_at: datetime`

#### 5.2 Scoring (`src/betrugserkennung/detection/scoring.py`)

- [ ] **`calculate_pattern_score(matches) -> float`** – Gewichtet nach Severity
  - `critical=1.0`, `high=0.8`, `medium=0.5`, `low=0.2`, normalisiert auf 0-1
- [ ] **`calculate_combined_score(pattern_score, llm_confidence, pattern_weight) -> float`**
  - `pattern_weight * pattern_score + (1 - pattern_weight) * llm_confidence`
- [ ] **`score_to_risk_level(score) -> RiskLevel`**
  - `<0.3` LOW, `<0.6` MEDIUM, `<0.85` HIGH, `>=0.85` CRITICAL
- [ ] **Test: `tests/test_scoring.py`**

#### 5.3 Analyzer (`src/betrugserkennung/detection/analyzer.py`)

- [ ] **`Analyzer`** Klasse – Orchestriert alles
  - `analyze(chat: Chat) -> DetectionResult`:
    1. Pattern Matcher
    2. LLM-Analyse
    3. Scores kombinieren
    4. Result bauen
  - `analyze_batch(chats: list[Chat]) -> list[DetectionResult]`
- [ ] **Test: `tests/test_analyzer.py`**

#### 5.4 Restliche Infrastruktur nachholen

- [ ] **`data/loader.py`** – `load_chat()`, `load_chats()`, `load_labeled_chat()`
- [ ] **`data/preprocessor.py`** – `normalize_text()`, `extract_urls()`, `extract_phone_numbers()`, `extract_ibans()`
- [ ] **Tests**: `test_loader.py`, `test_preprocessor.py`

#### 5.5 GUI erweitern

- [ ] **Risiko-Score als Ampel** in der GUI (gruen/gelb/orange/rot)
- [ ] **Detailansicht**: Pattern-Matches + LLM-Analyse + Combined Score

#### 5.6 CLI Kommandos (`src/betrugserkennung/cli/`)

- [ ] **`main.py`** – Click-Gruppe mit `--config` und `--verbose`
- [ ] **`commands.py`**:
  - `analyze <datei>` / `analyze --dir <ordner>`
  - `patterns list` / `patterns show <id>` / `patterns stats`
  - `evaluate --data <ordner>`
  - `status` – Ollama erreichbar? Modell? Anzahl Muster?
  - `gui` – Test-GUI starten
  - `scrape` – Scraper starten
- [ ] **Test: `tests/test_cli.py`**

#### Erfolgskriterium Phase 5:
> `betrugserkennung analyze sample_chat_scam.txt` → `CRITICAL`, Muster + LLM + Score. GUI zeigt Ampel.

---

### Phase 6: Training & Evaluation

> Ziel: System auf echten Daten evaluieren und optimieren. 95%-Ziel erreichen.

#### 6.1 Datensatz-Aufbereitung (`src/betrugserkennung/training/dataset.py`)

- [ ] **`create_dataset(labeled_dir) -> Dataset`** – Train/Test Split (80/20, stratified)
- [ ] **`Dataset`** Dataclass – `train`, `test`, `stats`
- [ ] **`export_dataset_stats(dataset) -> dict`** – Statistiken

#### 6.2 Trainer (`src/betrugserkennung/training/trainer.py`)

- [ ] **`Trainer`** Klasse
  - `run(dataset) -> TrainingResult`
  - `optimize_thresholds(dataset) -> dict` – Beste Schwellenwerte finden
  - Speichert optimierte Config

#### 6.3 Evaluation (`src/betrugserkennung/training/evaluate.py`)

- [ ] **`evaluate(analyzer, test_data) -> EvaluationResult`** – TP, FP, TN, FN, Precision, Recall, F1
- [ ] **`EvaluationResult`** Dataclass
- [ ] **`print_evaluation_report(result)`** – Schoener Report mit Rich
- [ ] **Test: `tests/test_evaluate.py`**

#### 6.4 Daten sammeln & labeln

- [ ] **100-200 Chats sammeln** (Scraper + manuell + Community)
- [ ] **Labeln**: `scam_XXX.txt` / `normal_XXX.txt` in `data/labeled/`
- [ ] **Erste Evaluation** durchfuehren
- [ ] **Iterativ optimieren**: Schwellenwerte, Prompts, Patterns anpassen bis 95% TP

#### Erfolgskriterium Phase 6:
> `betrugserkennung evaluate --data data/labeled/` zeigt >= 95% True Positive Rate.

---

### Phase 7: Polish & Release

> Ziel: Projekt ist bereit als Open-Source Betaversion.

#### 7.1 Dokumentation

- [ ] **`README.md`** komplett ueberarbeiten – Installation, Quick Start, Screenshots
- [ ] **`docs/architecture.md`** – Architektur mit Diagrammen
- [ ] **`docs/patterns.md`** – Anleitung: Neue Betrugsmuster hinzufuegen
- [ ] **`docs/data-format.md`** – Chat-Formate dokumentieren
- [ ] **`CONTRIBUTING.md`** – Beitragsrichtlinien

#### 7.2 CI/CD

- [ ] **`.github/workflows/test.yml`** – pytest + ruff bei jedem Push
- [ ] **`.github/workflows/release.yml`** – Automatisches Release bei Tag

#### 7.3 Qualitaet

- [ ] **100% Type Hints** → `mypy --strict` besteht
- [ ] **Ruff** sauber → `ruff check src/ tests/`
- [ ] **Testabdeckung** >= 80% → `pytest --cov`
- [ ] **Edge Cases**: Leere Chats, kaputte Dateien, Ollama offline

#### 7.4 Verkaeufer-Perspektive (naechste Iteration)

- [ ] Betrugsmuster aus Verkaeufersicht ergaenzen
- [ ] Prompt-Templates fuer Verkaeufer erweitern
- [ ] Testdaten aus Verkaeuferperspektive sammeln
- [ ] CLI/GUI um `--perspective buyer|seller` Option erweitern

#### Erfolgskriterium Phase 7:
> Projekt auf GitHub oeffentlich, README erklaert alles, CI ist gruen, Community kann beitragen.

---

## 5. Voraussetzungen & Abhaengigkeiten

| Was                            | Wofuer                    | Ab Phase |
|--------------------------------|---------------------------|----------|
| Python 3.14 + venv             | Gesamtes Projekt          | 1        |
| Ollama (lokal installiert)     | LLM-Analyse               | 1        |
| LLM-Modell (z.B. llama3.1:8b) | Chat-Analyse              | 1        |
| Pydantic                       | Config + Datenmodelle     | 1        |
| gradio oder streamlit          | Test-GUI                  | 2        |
| requests, beautifulsoup4       | Web-Scraper               | 3        |
| praw (optional)                | Reddit-Scraper            | 3        |
| PyYAML                         | Pattern-Datenbank         | 4        |
| Click + Rich                   | CLI                       | 5        |
| scikit-learn, pandas           | Evaluation                | 6        |
| GitHub Account                 | CI/CD + Release           | 7        |

---

## 6. Zusammenfassung

```
Phase 1: LLM-Integration        ████░░░░░░  Ollama anbinden, erster Chat → Analyse
Phase 2: Test-GUI                ░░██░░░░░░  Weboberflaeche zum Testen
Phase 3: Scam-Methoden+Scraper  ░░░░████░░  Muster recherchieren, Daten sammeln
Phase 4: Mustererkennung         ░░░░░░██░░  Pattern-DB + Matcher
Phase 5: Detection Engine        ░░░░░░░██░  Alles zusammen: Score + CLI + GUI
Phase 6: Training & Eval         ░░░░░░░░██  Daten labeln, 95% erreichen
Phase 7: Polish & Release        ░░░░░░░░░█  Doku, CI/CD, Open Source
```

**Kernidee:** Erst das LLM zum Laufen bringen, dann sofort sichtbar machen (GUI), dann die Datenbasis ausbauen (Scraper), und zum Schluss alles zusammenfuehren und optimieren.
