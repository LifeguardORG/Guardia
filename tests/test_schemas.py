"""Tests fuer die Datenmodelle (Message, Chat, Label)."""

from betrugserkennung.data.schemas import Chat, Label, LabeledChat, Message


def test_message_creation():
    """Message mit Sender und Text erstellen."""
    msg = Message(sender="Kaeufer", text="Ist der Artikel noch da?")
    assert msg.sender == "Kaeufer"
    assert msg.text == "Ist der Artikel noch da?"
    assert msg.timestamp is None


def test_chat_creation():
    """Chat mit mehreren Nachrichten erstellen."""
    messages = [
        Message(sender="Kaeufer", text="Hallo!"),
        Message(sender="Verkaeufer", text="Hi, ja ist noch da."),
    ]
    chat = Chat(messages=messages)
    assert chat.message_count == 2
    assert chat.source_file is None


def test_chat_full_text():
    """full_text gibt den Chat als lesbaren String zurueck."""
    messages = [
        Message(sender="Kaeufer", text="Hallo!"),
        Message(sender="Verkaeufer", text="Hi!"),
    ]
    chat = Chat(messages=messages)
    assert chat.full_text == "Kaeufer: Hallo!\nVerkaeufer: Hi!"


def test_chat_from_text():
    """Chat.from_text parst einen Textblock ins Chat-Format."""
    text = "Kaeufer: Hallo\nVerkaeufer: Hi, ist noch da"
    chat = Chat.from_text(text)
    assert chat.message_count == 2
    assert chat.messages[0].sender == "Kaeufer"
    assert chat.messages[0].text == "Hallo"
    assert chat.messages[1].sender == "Verkaeufer"


def test_chat_from_text_multiline():
    """Zeilen ohne Sender werden der letzten Nachricht angehaengt."""
    text = "Kaeufer: Das ist\neine lange Nachricht\nVerkaeufer: Ok"
    chat = Chat.from_text(text)
    assert chat.message_count == 2
    assert "eine lange Nachricht" in chat.messages[0].text


def test_chat_from_text_empty_lines():
    """Leere Zeilen werden uebersprungen."""
    text = "Kaeufer: Hallo\n\n\nVerkaeufer: Hi"
    chat = Chat.from_text(text)
    assert chat.message_count == 2


def test_label_enum():
    """Label-Enum hat die richtigen Werte."""
    assert Label.NORMAL.value == "normal"
    assert Label.SCAM.value == "scam"
    assert Label.UNKNOWN.value == "unknown"


def test_labeled_chat():
    """LabeledChat hat ein Label-Feld."""
    messages = [Message(sender="Kaeufer", text="Test")]
    chat = LabeledChat(messages=messages, label=Label.SCAM)
    assert chat.label == Label.SCAM
    assert chat.message_count == 1
