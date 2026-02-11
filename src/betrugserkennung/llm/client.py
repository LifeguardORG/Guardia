"""LLM Client Interface – Abstrakte Basis fuer alle LLM-Anbindungen."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from betrugserkennung.data.schemas import Chat


@dataclass
class LlmResponse:
    """Strukturierte Antwort des LLM nach einer Chat-Analyse.

    Attributes:
        verdict: Einschaetzung des LLM (z.B. "scam", "normal", "verdaechtig").
        confidence: Konfidenz der Einschaetzung (0.0 – 1.0).
        reasoning: Begruendung des LLM in natuerlicher Sprache.
        risk_factors: Liste erkannter Risikofaktoren.
    """

    verdict: str
    confidence: float
    reasoning: str
    risk_factors: list[str] = field(default_factory=list)


class BaseLlmClient(ABC):
    """Abstrakte Basisklasse fuer LLM-Clients.

    Jede konkrete Implementierung (Ollama, llama.cpp, etc.) muss diese
    Methoden implementieren. So kann der LLM-Provider ausgetauscht werden
    ohne die restliche Logik zu aendern.
    """

    @abstractmethod
    def analyze_chat(self, chat: Chat) -> LlmResponse:
        """Analysiert einen Chat auf Betrugsmerkmale.

        Args:
            chat: Der zu analysierende Chat-Verlauf.

        Returns:
            Strukturierte Analyse mit Verdict, Konfidenz und Begruendung.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Prueft ob der LLM-Server erreichbar ist.

        Returns:
            True wenn der Server antwortet, sonst False.
        """
