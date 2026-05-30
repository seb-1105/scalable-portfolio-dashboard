# Portfolio Dashboard

Lokales, datenschutzfreundliches Portfolio-Tracking auf Basis der Scalable Capital Transaktionshistorie.  
Keine Cloud, keine externen Server – alle Daten bleiben im Browser.

---

## Funktionen

- **CSV-Import** aus Scalable Capital (Konto → Transaktionen → Export)
- **Automatische ISIN-Auflösung** via OpenFIGI → Yahoo Finance Ticker
- **Live-Kurse** über lokalen yfinance-Server (alle Weltbörsen, kein CORS)
- **FX-Umrechnung** in EUR (open.er-api.com)
- **WACC-Berechnung** (Weighted Average Cost of Capital) für den Ø Kaufpreis
- **Verkaufte Positionen** werden erkannt, ausgegraut und mit realisiertem G/V ausgewiesen
- **Hover-Tooltip** auf jede Position zeigt komplette Kauf-/Verkaufshistorie
- **Donut-Chart** zur Portfolioverteilung
- **Monatlicher G/V-Chart** (realisierte Gewinne/Verluste)
- **5 Summary-Kacheln**: Kapital · Aktueller Wert · Gesamtgewinn · Unrealisierter G/V · Positionen
- Alle Daten werden im `localStorage` des Browsers gespeichert (kein Account nötig)

---

## Voraussetzungen

- Python 3.8 oder neuer (bereits installiert prüfen: `python3 --version`)
- Finnhub.io API-Key zur Abrufung von Live Kursdaten (Registrierung erforderlich)
- Keine weiteren manuellen Installationen nötig – `start.py` erledigt alles

---

## Starten (empfohlen)

```bash
# macOS / Linux
python3 start.py

# Windows
python start.py
```

Das Skript:
1. Erstellt automatisch eine virtuelle Umgebung (`.venv`)
2. Installiert alle Abhängigkeiten (`yfinance`)
3. Startet den Kursserver auf `http://localhost:8765`
4. Öffnet `portfolio-dashboard.html` automatisch im Browser

Dann einfach die Scalable Capital CSV per Drag & Drop ins Dashboard ziehen.  
Server stoppen: **Strg+C** im Terminal.

---

## Manueller Start (alternativ)

### 1. Kursserver starten

```bash
cd /pfad/zum/Portfolio-Dashboard
python3 price_server.py
```

### 2. Dashboard öffnen

`portfolio-dashboard.html` im Browser öffnen (Doppelklick oder `open portfolio-dashboard.html`).

### 3. CSV importieren

Scalable Capital → Konto → Transaktionen → Export als CSV  
→ Datei per Drag & Drop auf das Dashboard ziehen oder über „CSV importieren" auswählen.

---

## Projektstruktur

```
Portfolio-Dashboard/
├── portfolio-dashboard.html   # Komplettes Frontend (eine Datei, keine Dependencies)
├── price_server.py            # Lokaler HTTP-Server für yfinance-Kurse (Port 8765)
└── README.md
```

---

## Technische Details

### CSV-Format (Scalable Capital)

| Spalte      | Beschreibung                         |
|-------------|--------------------------------------|
| date        | Transaktionsdatum (DD.MM.YY)         |
| time        | Uhrzeit                              |
| status      | `Executed` / `Cancelled`            |
| description | Wertpapier-Name                      |
| assetType   | Security / ...                       |
| type        | `Buy` / `Sell` / `Savings Plan`     |
| isin        | ISIN des Wertpapiers                 |
| shares      | Stückzahl                            |
| price       | Stückpreis                           |
| amount      | Gesamtbetrag (negativ bei Käufen)    |
| fee / tax   | Gebühren / Steuern                   |
| currency    | Handelswährung                       |

Nur Zeilen mit `status = Executed` und `type = Buy/Sell/Savings Plan` werden verarbeitet.  
Die CSV wird **chronologisch sortiert** verarbeitet (älteste zuerst), damit WACC und Bestandsrechnung korrekt sind.

### ISIN-Auflösung

1. Cache prüfen (`localStorage`, Version 2)
2. Batch-Auflösung via [OpenFIGI API](https://www.openfigi.com/) (kostenlos, kein Key)
3. Finnhub als Einzelfallback (optionaler API Key)
4. Direkte ISIN an yfinance-Server (funktioniert für viele Wertpapiere)

### Ticker-Fallbacks (CoinShares ETPs)

Einige CoinShares-ETPs sind auf Yahoo Finance Deutschland nicht gelistet.  
`price_server.py` enthält eine `TICKER_FALLBACK`-Dict mit Alternativ-Tickern:

| Ticker (Xetra) | Fallback          | Grund                            |
|----------------|-------------------|----------------------------------|
| CETH.DE        | GB00BLD4ZM24      | ISIN direkt (kein Xetra-Listing) |
| XRRL.DE        | XRPL.PA           | Euronext Paris                   |
| CSDA.DE        | CSDA.PA           | Euronext Paris                   |

Weitere Fallbacks können in `TICKER_FALLBACK` in `price_server.py` eingetragen werden.

### Kursserver-API

```
GET /health
→ {"ok": true}

GET /prices?tickers=AAPL,ASML.AS,IE00BFZXGZ54
→ {"AAPL": {"price": 213.45, "currency": "USD"}, ...}
```

---

## Datenschutz

- Keine Daten verlassen deinen Browser (außer Kursabfragen an Yahoo Finance / OpenFIGI)
- CSV-Daten werden ausschließlich in `localStorage` gespeichert
- Der Kursserver läuft lokal und ist nur über `localhost` erreichbar
