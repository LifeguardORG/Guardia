"""Prompt-Templates – Systemanweisungen und Analyse-Prompts fuer das LLM."""

from __future__ import annotations

from guardia.data.schemas import Chat

# Systemanweisung: Definiert die Rolle und das Verhalten des LLM.
SYSTEM_PROMPT = """\
Du bist ein Experte fuer Betrugserkennung auf der Plattform Kleinanzeigen \
(ehemals eBay Kleinanzeigen). Deine Aufgabe ist es, Chat-Verlaeufe zwischen \
Kaeufern und Verkaeufern zu analysieren und einzuschaetzen, ob es sich um \
einen Betrugsversuch handelt.

Du kennst typische Betrugsmaschen wie:
- Zahlung ausserhalb der Plattform (Bankueberweisung, PayPal Freunde)
- Kuenstlicher Zeitdruck ("andere Interessenten", "muss heute raus")
- Phishing-Links (gefaelschte Bezahlseiten)
- Kommunikation ausserhalb der Plattform (WhatsApp, Telegram)
- Dreiecksbetrug (Versand vor Zahlungsbestaetigung)
- Unrealistisch niedrige Preise
- Forderung persoenlicher Daten (Ausweis, IBAN)
- Anzahlung/Reservierungsgebuehr vor Warenerhallt

Analysiere den Chat aus der Kaeuferperspektive. Antworte IMMER im folgenden \
JSON-Format und in KEINEM anderen Format:

{
  "verdict": "fraud" oder "normal" oder "verdaechtig",
  "confidence": 0.0 bis 1.0,
  "reasoning": "Deine Begruendung in 2-3 Saetzen",
  "risk_factors": ["Faktor 1", "Faktor 2"]
}
"""

# Analyse-Prompt: Wird mit dem konkreten Chat-Text gefuellt.
ANALYSIS_PROMPT_TEMPLATE = """\
Analysiere den folgenden Kleinanzeigen-Chat auf Betrugsmerkmale:

--- CHAT-VERLAUF ---
{chat_text}
--- ENDE CHAT ---

Gib deine Einschaetzung als JSON zurueck.
"""


def format_chat_for_prompt(chat: Chat) -> str:
    """Formatiert einen Chat fuer die Verwendung im LLM-Prompt.

    Jede Nachricht wird als 'Sender: Text' dargestellt, eine pro Zeile.

    Args:
        chat: Der zu formatierende Chat.

    Returns:
        Mehrzeiliger String im Format 'Sender: Nachricht'.
    """
    return chat.full_text


def build_analysis_prompt(chat: Chat) -> str:
    """Baut den vollstaendigen Analyse-Prompt fuer einen Chat.

    Args:
        chat: Der zu analysierende Chat.

    Returns:
        Fertig formatierter Prompt-String.
    """
    chat_text = format_chat_for_prompt(chat)
    return ANALYSIS_PROMPT_TEMPLATE.format(chat_text=chat_text)
