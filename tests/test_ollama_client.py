"""Tests fuer den Ollama Client – mit gemocktem Ollama-Server."""

import json
from unittest.mock import MagicMock, patch

from betrugserkennung.config.settings import LlmSettings
from betrugserkennung.data.schemas import Chat, Message
from betrugserkennung.llm.client import LlmResponse
from betrugserkennung.llm.ollama_client import OllamaClient


def _make_test_chat() -> Chat:
    """Erstellt einen einfachen Test-Chat."""
    return Chat(
        messages=[
            Message(sender="Verkaeufer", text="PS5 fuer 150 Euro, Schnaeppchen!"),
            Message(sender="Kaeufer", text="Kann ich die abholen?"),
            Message(
                sender="Verkaeufer",
                text="Bin im Urlaub. Bitte per Bankueberweisung bezahlen.",
            ),
        ]
    )


def _make_mock_response(verdict: str = "scam", confidence: float = 0.9) -> MagicMock:
    """Erstellt eine gemockte Ollama-Antwort."""
    response_json = json.dumps({
        "verdict": verdict,
        "confidence": confidence,
        "reasoning": "Verdaechtig wegen Zahlung ausserhalb der Plattform.",
        "risk_factors": ["Bankueberweisung", "Zeitdruck", "Kein Abholen moeglich"],
    })
    mock_response = MagicMock()
    mock_response.message.content = response_json
    return mock_response


class TestOllamaClientAnalyze:
    """Tests fuer die analyze_chat-Methode."""

    @patch("betrugserkennung.llm.ollama_client.ollama.Client")
    def test_analyze_scam_chat(self, mock_client_class: MagicMock):
        """Scam-Chat wird als 'scam' mit hoher Konfidenz erkannt."""
        mock_instance = MagicMock()
        mock_instance.chat.return_value = _make_mock_response("scam", 0.9)
        mock_client_class.return_value = mock_instance

        client = OllamaClient(LlmSettings())
        result = client.analyze_chat(_make_test_chat())

        assert isinstance(result, LlmResponse)
        assert result.verdict == "scam"
        assert result.confidence == 0.9
        assert len(result.risk_factors) > 0
        assert "Bankueberweisung" in result.risk_factors

    @patch("betrugserkennung.llm.ollama_client.ollama.Client")
    def test_analyze_normal_chat(self, mock_client_class: MagicMock):
        """Normaler Chat wird als 'normal' erkannt."""
        mock_instance = MagicMock()
        mock_instance.chat.return_value = _make_mock_response("normal", 0.1)
        mock_client_class.return_value = mock_instance

        client = OllamaClient(LlmSettings())
        result = client.analyze_chat(_make_test_chat())

        assert result.verdict == "normal"
        assert result.confidence == 0.1

    @patch("betrugserkennung.llm.ollama_client.ollama.Client")
    def test_analyze_invalid_json(self, mock_client_class: MagicMock):
        """Bei ungueltigem JSON wird Fallback-Response zurueckgegeben."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.message.content = "Das ist kein JSON!"
        mock_instance.chat.return_value = mock_response
        mock_client_class.return_value = mock_instance

        client = OllamaClient(LlmSettings())
        result = client.analyze_chat(_make_test_chat())

        assert result.verdict == "unknown"
        assert result.confidence == 0.0
        assert "parsen" in result.reasoning.lower() or "json" in result.reasoning.lower()


class TestOllamaClientAvailability:
    """Tests fuer die is_available-Methode."""

    @patch("betrugserkennung.llm.ollama_client.ollama.Client")
    def test_server_available_model_found(self, mock_client_class: MagicMock):
        """Server erreichbar und Modell vorhanden → True."""
        mock_instance = MagicMock()
        mock_model = MagicMock()
        mock_model.model = "llama3.1:8b"
        mock_list = MagicMock()
        mock_list.models = [mock_model]
        mock_instance.list.return_value = mock_list
        mock_client_class.return_value = mock_instance

        client = OllamaClient(LlmSettings())
        assert client.is_available() is True

    @patch("betrugserkennung.llm.ollama_client.ollama.Client")
    def test_server_available_model_missing(self, mock_client_class: MagicMock):
        """Server erreichbar aber Modell nicht installiert → False."""
        mock_instance = MagicMock()
        mock_model = MagicMock()
        mock_model.model = "mistral:7b"
        mock_list = MagicMock()
        mock_list.models = [mock_model]
        mock_instance.list.return_value = mock_list
        mock_client_class.return_value = mock_instance

        client = OllamaClient(LlmSettings())
        assert client.is_available() is False

    @patch("betrugserkennung.llm.ollama_client.ollama.Client")
    def test_server_unreachable(self, mock_client_class: MagicMock):
        """Server nicht erreichbar → False."""
        mock_instance = MagicMock()
        mock_instance.list.side_effect = ConnectionError("Server nicht erreichbar")
        mock_client_class.return_value = mock_instance

        client = OllamaClient(LlmSettings())
        assert client.is_available() is False


class TestParseResponse:
    """Tests fuer das Parsen der LLM-Antwort."""

    def test_parse_vollstaendig(self):
        """Vollstaendige JSON-Antwort wird korrekt geparst."""
        client = OllamaClient.__new__(OllamaClient)
        raw = json.dumps({
            "verdict": "scam",
            "confidence": 0.85,
            "reasoning": "Klar ein Betrug.",
            "risk_factors": ["IBAN", "Zeitdruck"],
        })
        result = client._parse_response(raw)
        assert result.verdict == "scam"
        assert result.confidence == 0.85
        assert result.risk_factors == ["IBAN", "Zeitdruck"]

    def test_parse_fehlende_felder(self):
        """Fehlende Felder werden mit Defaults aufgefuellt."""
        client = OllamaClient.__new__(OllamaClient)
        raw = json.dumps({"verdict": "normal"})
        result = client._parse_response(raw)
        assert result.verdict == "normal"
        assert result.confidence == 0.0
        assert result.risk_factors == []

    def test_parse_confidence_clamping(self):
        """Confidence wird auf 0.0-1.0 begrenzt."""
        client = OllamaClient.__new__(OllamaClient)
        raw = json.dumps({"verdict": "scam", "confidence": 5.0})
        result = client._parse_response(raw)
        assert result.confidence == 1.0

        raw_neg = json.dumps({"verdict": "scam", "confidence": -0.5})
        result_neg = client._parse_response(raw_neg)
        assert result_neg.confidence == 0.0
