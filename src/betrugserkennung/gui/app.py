"""Hauptfenster der Betrugserkennung – PyQt6 Desktop-App.

Bietet ein Chat-Eingabefeld, einen Analyse-Button und eine Ergebnis-Anzeige.
Laeuft komplett lokal, keine Daten verlassen den Rechner.
"""

from __future__ import annotations

import sys
from pathlib import Path
from threading import Thread

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from betrugserkennung.config.settings import LlmSettings, load_settings
from betrugserkennung.data.schemas import Chat
from betrugserkennung.llm.client import LlmResponse
from betrugserkennung.llm.ollama_client import OllamaClient

# Pfad zu Beispiel-Chats (aus Testdaten)
_TEST_DATA_DIR = Path(__file__).parent.parent.parent.parent / "tests" / "test_data"

# Farben fuer Risiko-Stufen
_COLORS = {
    "scam": "#e74c3c",       # Rot
    "verdaechtig": "#f39c12", # Orange
    "normal": "#27ae60",      # Gruen
    "unknown": "#95a5a6",     # Grau
}


class _AnalysisWorker(QObject):
    """Hintergrund-Worker fuer die LLM-Analyse (blockiert nicht die GUI)."""

    finished = pyqtSignal(object)  # LlmResponse oder Exception
    error = pyqtSignal(str)

    def __init__(self, client: OllamaClient, chat: Chat) -> None:
        super().__init__()
        self.client = client
        self.chat = chat

    def run(self) -> None:
        """Fuehrt die Analyse im Hintergrund-Thread aus."""
        try:
            result = self.client.analyze_chat(self.chat)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Hauptfenster der Betrugserkennung-App."""

    def __init__(self) -> None:
        super().__init__()
        self.settings = load_settings()
        self.client = OllamaClient(self.settings.llm)
        self._init_ui()
        self._check_ollama_status()

    def _init_ui(self) -> None:
        """Baut die gesamte Benutzeroberflaeche auf."""
        self.setWindowTitle("Betrugserkennung – Kleinanzeigen Scam-Detektor")
        self.setMinimumSize(800, 700)

        # Zentrales Widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # --- Header ---
        header = QLabel("Kleinanzeigen Scam-Detektor")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # --- Ollama-Status ---
        status_row = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Segoe UI", 14))
        self.status_label = QLabel("Pruefe Ollama-Verbindung...")
        self.status_label.setFont(QFont("Segoe UI", 10))
        status_row.addWidget(self.status_indicator)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        layout.addLayout(status_row)

        # --- Vorlagen-Dropdown ---
        template_row = QHBoxLayout()
        template_label = QLabel("Vorlage:")
        template_label.setFont(QFont("Segoe UI", 10))
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "-- Eigenen Chat eingeben --",
            "Beispiel: Normaler Chat",
            "Beispiel: Scam-Chat",
        ])
        self.template_combo.currentIndexChanged.connect(self._on_template_selected)
        template_row.addWidget(template_label)
        template_row.addWidget(self.template_combo)
        template_row.addStretch()
        layout.addLayout(template_row)

        # --- Chat-Eingabe ---
        input_label = QLabel("Chat-Verlauf eingeben:")
        input_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(input_label)

        self.chat_input = QTextEdit()
        self.chat_input.setFont(QFont("Consolas", 10))
        self.chat_input.setPlaceholderText(
            "Kaeufer: Hallo, ist der Artikel noch da?\n"
            "Verkaeufer: Ja, der ist noch verfuegbar!\n"
            "..."
        )
        self.chat_input.setMinimumHeight(180)
        layout.addWidget(self.chat_input)

        # --- Analyse-Button + Fortschritt ---
        button_row = QHBoxLayout()
        self.analyze_btn = QPushButton("  Analysieren")
        self.analyze_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.analyze_btn.setMinimumHeight(44)
        self.analyze_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border-radius: 6px; "
            "padding: 8px 24px; } "
            "QPushButton:hover { background-color: #2980b9; } "
            "QPushButton:disabled { background-color: #bdc3c7; }"
        )
        self.analyze_btn.clicked.connect(self._on_analyze)
        button_row.addWidget(self.analyze_btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Endlos-Animation
        self.progress.setVisible(False)
        self.progress.setMaximumWidth(200)
        button_row.addWidget(self.progress)
        button_row.addStretch()
        layout.addLayout(button_row)

        # --- Trennlinie ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # --- Ergebnis-Bereich ---
        result_label = QLabel("Ergebnis:")
        result_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(result_label)

        # Verdict-Ampel
        self.verdict_label = QLabel("")
        self.verdict_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.verdict_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verdict_label.setMinimumHeight(60)
        self.verdict_label.setStyleSheet(
            "background-color: #ecf0f1; border-radius: 8px; padding: 8px;"
        )
        layout.addWidget(self.verdict_label)

        # Konfidenz
        self.confidence_label = QLabel("")
        self.confidence_label.setFont(QFont("Segoe UI", 12))
        self.confidence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.confidence_label)

        # Begruendung
        reasoning_label = QLabel("Begruendung:")
        reasoning_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(reasoning_label)

        self.reasoning_text = QTextEdit()
        self.reasoning_text.setFont(QFont("Segoe UI", 10))
        self.reasoning_text.setReadOnly(True)
        self.reasoning_text.setMaximumHeight(100)
        layout.addWidget(self.reasoning_text)

        # Risikofaktoren
        risk_label = QLabel("Erkannte Risikofaktoren:")
        risk_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(risk_label)

        self.risk_text = QTextEdit()
        self.risk_text.setFont(QFont("Segoe UI", 10))
        self.risk_text.setReadOnly(True)
        self.risk_text.setMaximumHeight(80)
        layout.addWidget(self.risk_text)

    def _check_ollama_status(self) -> None:
        """Prueft ob Ollama erreichbar ist und aktualisiert den Status-Indikator."""
        available = self.client.is_available()
        if available:
            self.status_indicator.setStyleSheet("color: #27ae60;")  # Gruen
            self.status_label.setText(
                f"Ollama verbunden – Modell: {self.settings.llm.model}"
            )
        else:
            self.status_indicator.setStyleSheet("color: #e74c3c;")  # Rot
            self.status_label.setText(
                f"Ollama nicht erreichbar ({self.settings.llm.host}) "
                f"oder Modell '{self.settings.llm.model}' nicht installiert"
            )

    def _on_template_selected(self, index: int) -> None:
        """Laedt eine Chat-Vorlage ins Eingabefeld."""
        if index == 1:
            # Normaler Chat
            path = _TEST_DATA_DIR / "sample_chat_normal.txt"
            if path.exists():
                self.chat_input.setPlainText(path.read_text(encoding="utf-8").strip())
        elif index == 2:
            # Scam-Chat
            path = _TEST_DATA_DIR / "sample_chat_scam.txt"
            if path.exists():
                self.chat_input.setPlainText(path.read_text(encoding="utf-8").strip())

    def _on_analyze(self) -> None:
        """Startet die Chat-Analyse im Hintergrund-Thread."""
        text = self.chat_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Leerer Chat", "Bitte einen Chat-Verlauf eingeben.")
            return

        # UI in Lade-Zustand versetzen
        self.analyze_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.verdict_label.setText("Analysiere...")
        self.verdict_label.setStyleSheet(
            "background-color: #ecf0f1; border-radius: 8px; padding: 8px; color: #7f8c8d;"
        )
        self.confidence_label.setText("")
        self.reasoning_text.clear()
        self.risk_text.clear()

        # Chat parsen und Analyse im Hintergrund starten
        chat = Chat.from_text(text)
        self.worker = _AnalysisWorker(self.client, chat)
        self.worker.finished.connect(self._on_analysis_done)
        self.worker.error.connect(self._on_analysis_error)

        thread = Thread(target=self.worker.run, daemon=True)
        thread.start()

    def _on_analysis_done(self, result: LlmResponse) -> None:
        """Zeigt das Analyse-Ergebnis in der GUI an."""
        self.analyze_btn.setEnabled(True)
        self.progress.setVisible(False)

        # Verdict mit Farbe
        verdict_display = {
            "scam": "BETRUG ERKANNT",
            "verdaechtig": "VERDAECHTIG",
            "normal": "KEIN BETRUG",
        }.get(result.verdict, result.verdict.upper())

        color = _COLORS.get(result.verdict, _COLORS["unknown"])

        self.verdict_label.setText(verdict_display)
        self.verdict_label.setStyleSheet(
            f"background-color: {color}; color: white; border-radius: 8px; padding: 8px;"
        )

        # Konfidenz
        pct = int(result.confidence * 100)
        self.confidence_label.setText(f"Konfidenz: {pct}%")

        # Begruendung
        self.reasoning_text.setPlainText(result.reasoning)

        # Risikofaktoren
        if result.risk_factors:
            factors = "\n".join(f"  • {f}" for f in result.risk_factors)
            self.risk_text.setPlainText(factors)
        else:
            self.risk_text.setPlainText("Keine Risikofaktoren erkannt.")

    def _on_analysis_error(self, error_msg: str) -> None:
        """Zeigt eine Fehlermeldung bei Analyse-Fehler an."""
        self.analyze_btn.setEnabled(True)
        self.progress.setVisible(False)
        self.verdict_label.setText("FEHLER")
        self.verdict_label.setStyleSheet(
            "background-color: #95a5a6; color: white; border-radius: 8px; padding: 8px;"
        )
        self.reasoning_text.setPlainText(f"Analyse fehlgeschlagen:\n{error_msg}")

        QMessageBox.critical(
            self,
            "Analyse-Fehler",
            f"Die Analyse konnte nicht durchgefuehrt werden:\n\n{error_msg}\n\n"
            "Ist Ollama gestartet? (ollama serve)",
        )


def run_gui() -> None:
    """Startet die PyQt6-GUI-Anwendung."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
