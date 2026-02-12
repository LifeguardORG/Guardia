"""Tests fuer die Prompt-Templates."""

from guardia.data.schemas import Chat, Message
from guardia.llm.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    format_chat_for_prompt,
)


def test_system_prompt_nicht_leer():
    """System-Prompt muss Inhalt haben."""
    assert len(SYSTEM_PROMPT) > 100
    assert "Kleinanzeigen" in SYSTEM_PROMPT
    assert "JSON" in SYSTEM_PROMPT


def test_system_prompt_enthaelt_json_format():
    """System-Prompt muss das erwartete JSON-Ausgabeformat beschreiben."""
    assert '"verdict"' in SYSTEM_PROMPT
    assert '"confidence"' in SYSTEM_PROMPT
    assert '"reasoning"' in SYSTEM_PROMPT
    assert '"risk_factors"' in SYSTEM_PROMPT


def test_format_chat_for_prompt():
    """Chat wird als lesbarer Text formatiert."""
    chat = Chat(
        messages=[
            Message(sender="Kaeufer", text="Noch da?"),
            Message(sender="Verkaeufer", text="Ja!"),
        ]
    )
    result = format_chat_for_prompt(chat)
    assert "Kaeufer: Noch da?" in result
    assert "Verkaeufer: Ja!" in result


def test_build_analysis_prompt():
    """Analyse-Prompt enthaelt den Chat-Text."""
    chat = Chat(
        messages=[
            Message(sender="Kaeufer", text="Was kostet das?"),
        ]
    )
    prompt = build_analysis_prompt(chat)
    assert "Was kostet das?" in prompt
    assert "CHAT-VERLAUF" in prompt
    assert "JSON" in prompt or "Einschaetzung" in prompt
