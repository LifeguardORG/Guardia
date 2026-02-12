# Datenverzeichnis

Dieses Verzeichnis enthaelt die Laufzeitdaten. Alle Dateien hier (ausser `.gitkeep`) werden von Git ignoriert.

## Ordnerstruktur

| Ordner       | Inhalt                                              |
|--------------|-----------------------------------------------------|
| `raw/`       | Rohe Chat-Exporte (Text, JSON, CSV)                 |
| `processed/` | Aufbereitete und normalisierte Chats                |
| `labeled/`   | Gelabelte Chats fuer Training (`normal` oder `fraud`)|

## Erwartetes Chat-Format

### Textformat (`.txt`)

```
Verkaeufer: Hallo, der Artikel ist noch verfuegbar!
Kaeufer: Super, kann ich den morgen abholen?
Verkaeufer: Klar, schreib mir deine Adresse per WhatsApp: 0170-1234567
```

Jede Zeile: `Rolle: Nachricht`

### Gelabelte Daten

Dateiname-Konvention: `{label}_{id}.txt`
- `fraud_001.txt` – Betrugschat
- `normal_001.txt` – Normaler Chat

## Datenschutz

Echte Chat-Daten duerfen **niemals** ins Repository committed werden. Alle Daten werden lokal verarbeitet (DSGVO-konform).
