"""Ollama Client – Konkrete LLM-Anbindung ueber die Ollama REST API."""

from __future__ import annotations

import json
import logging

import ollama

from betrugserkennung.config.settings import LlmSettings
from betrugserkennung.data.schemas import Chat
from betrugserkennung.llm.client import BaseLlmClient, LlmResponse
from betrugserkennung.llm.prompts import SYSTEM_PROMPT, build_analysis_prompt

logger = logging.getLogger(__name__)


class OllamaClient(BaseLlmClient):
    """LLM-Client der ueber die Ollama Python-Bibliothek kommuniziert.

    Erwartet einen laufenden Ollama-Server (Standard: http://localhost:11434)
    mit einem installierten Modell (Standard: llama3.1:8b).
    """

    def __init__(self, settings: LlmSettings | None = None) -> None:
        """Initialisiert den Ollama-Client.

        Args:
            settings: LLM-Einstellungen. Wenn None, werden Defaults verwendet.
        """
        self.settings = settings or LlmSettings()
        self.client = ollama.Client(host=self.settings.host)

    def analyze_chat(self, chat: Chat) -> LlmResponse:
        """Analysiert einen Chat auf Betrugsmerkmale via Ollama.

        Sendet den Chat als Prompt an das LLM und parst die JSON-Antwort.
        Bei Parse-Fehlern wird ein Fallback-Response zurueckgegeben.

        Args:
            chat: Der zu analysierende Chat-Verlauf.

        Returns:
            Strukturierte LlmResponse mit Verdict, Konfidenz und Begruendung.
        """
        prompt = build_analysis_prompt(chat)

        logger.info(
            "Sende Chat an Ollama (Modell: %s, Nachrichten: %d)",
            self.settings.model,
            chat.message_count,
        )

        response = self.client.chat(
            model=self.settings.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            options={
                "temperature": self.settings.temperature,
                "num_predict": self.settings.max_tokens,
            },
            format="json",
        )

        raw_content = response.message.content
        logger.debug("Ollama Rohantwort: %s", raw_content)

        return self._parse_response(raw_content)

    def is_available(self) -> bool:
        """Prueft ob der Ollama-Server erreichbar ist und das Modell geladen.

        Returns:
            True wenn Server antwortet, sonst False.
        """
        try:
            models = self.client.list()
            model_names = [m.model for m in models.models]
            available = self.settings.model in model_names
            if not available:
                logger.warning(
                    "Ollama erreichbar, aber Modell '%s' nicht gefunden. "
                    "Verfuegbare Modelle: %s",
                    self.settings.model,
                    model_names,
                )
            return available
        except Exception:
            logger.exception("Ollama-Server nicht erreichbar unter %s", self.settings.host)
            return False

    def _parse_response(self, raw: str) -> LlmResponse:
        """Parst die JSON-Antwort des LLM in eine LlmResponse.

        Versucht die Antwort als JSON zu parsen. Bei Fehlern wird ein
        Fallback mit der Rohantwort als Reasoning zurueckgegeben.

        Args:
            raw: Rohe Textantwort des LLM.

        Returns:
            Geparste LlmResponse.
        """
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("LLM-Antwort ist kein gueltiges JSON: %s", raw[:200])
            return LlmResponse(
                verdict="unknown",
                confidence=0.0,
                reasoning=f"Konnte LLM-Antwort nicht parsen: {raw[:500]}",
                risk_factors=[],
            )

        # Robustes Parsen: Fehlende Felder mit Defaults auffangen
        verdict = str(data.get("verdict", "unknown")).lower().strip()
        confidence = float(data.get("confidence", 0.0))
        reasoning = str(data.get("reasoning", "Keine Begruendung vom LLM erhalten."))
        risk_factors = data.get("risk_factors", [])

        # Confidence auf gueltigen Bereich begrenzen
        confidence = max(0.0, min(1.0, confidence))

        # Sicherstellen dass risk_factors eine Liste von Strings ist
        if not isinstance(risk_factors, list):
            risk_factors = [str(risk_factors)]
        else:
            risk_factors = [str(f) for f in risk_factors]

        return LlmResponse(
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            risk_factors=risk_factors,
        )
