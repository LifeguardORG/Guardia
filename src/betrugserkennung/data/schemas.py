"""Datenmodelle – Strukturen fuer Chat-Nachrichten, Chats und Labels."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


@dataclass
class Message:
    """Eine einzelne Nachricht in einem Chat-Verlauf."""

    sender: str
    text: str
    timestamp: datetime | None = None


@dataclass
class Chat:
    """Ein kompletter Chat-Verlauf zwischen Kaeufer und Verkaeufer."""

    messages: list[Message]
    source_file: Path | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def message_count(self) -> int:
        """Anzahl der Nachrichten im Chat."""
        return len(self.messages)

    @property
    def full_text(self) -> str:
        """Gibt den gesamten Chat als lesbaren Text zurueck."""
        lines = []
        for msg in self.messages:
            lines.append(f"{msg.sender}: {msg.text}")
        return "\n".join(lines)

    @classmethod
    def from_text(cls, text: str, source_file: Path | None = None) -> Chat:
        """Erstellt einen Chat aus einem Text im Format 'Sender: Nachricht'.

        Zeilen ohne Doppelpunkt werden der letzten Nachricht angehaengt.
        """
        messages: list[Message] = []

        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue

            if ": " in line:
                sender, msg_text = line.split(": ", 1)
                messages.append(Message(sender=sender.strip(), text=msg_text.strip()))
            elif messages:
                # Zeile ohne Sender → an letzte Nachricht anhaengen
                messages[-1].text += f" {line}"

        return cls(messages=messages, source_file=source_file)


class Label(Enum):
    """Label fuer gelabelte Chats."""

    NORMAL = "normal"
    SCAM = "scam"
    UNKNOWN = "unknown"


@dataclass
class LabeledChat(Chat):
    """Ein Chat mit zugeordnetem Label (normal oder scam)."""

    label: Label = Label.UNKNOWN
