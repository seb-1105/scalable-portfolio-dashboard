# Portfolio Dashboard

Local, privacy-friendly portfolio tracking based on your Scalable Capital transaction history.  
No cloud, no external servers — all data stays in your browser.

---

## Features

- **CSV import** from Scalable Capital (Account → Transactions → Export)
- **Automatic ISIN resolution** via OpenFIGI → Yahoo Finance ticker
- **Live prices** via local yfinance server (all global exchanges, no CORS issues)
- **FX conversion** to EUR (open.er-api.com)
- **WACC calculation** (Weighted Average Cost of Capital) for the average purchase price
- **Sold positions** are automatically detected, greyed out, and shown with realised P&L
- **Hover tooltip** on each position shows the complete buy/sell history
- **Donut chart** for portfolio allocation
- **Monthly P&L chart** (realised gains/losses)
- **5 summary cards**: Capital · Current Value · Total P&L · Unrealised P&L · Positions
- All data is stored in the browser's `localStorage` — no account required

---

## Requirements

- Python 3.8 or newer (check with: `python3 --version`)
- A Scalable Capital transaction history `.csv` file
- No further manual installation needed — `start.py` handles everything

---

## Quick Start (recommended)

```bash
# macOS / Linux
python3 start.py

# Windows
python start.py
```

The script will:
1. Automatically create a virtual environment (`.venv`)
2. Install all dependencies (`yfinance`)
3. Start the price server at `http://localhost:8765`
4. Open `portfolio-dashboard.html` automatically in your browser

Then simply drag and drop your Scalable Capital CSV onto the dashboard.  
You can export it in Scalable under Home → Transactions → three dots (top right) → Select All → Export transactions as CSV.  
Note: this must be done manually each time — automated export is not yet supported by Scalable.

Stop the server: **Ctrl+C** in the terminal.

---

## Manual Start (alternative)

### 1. Start the price server

```bash
cd /path/to/Portfolio-Dashboard
python3 price_server.py
```

### 2. Open the dashboard

Open `portfolio-dashboard.html` in your browser (double-click or `open portfolio-dashboard.html`).

### 3. Import CSV

Scalable Capital → Account → Transactions → Export as CSV  
→ Drag and drop the file onto the dashboard or click "CSV importieren".

---

## Project Structure

```
Portfolio-Dashboard/
├── portfolio-dashboard.html   # Complete frontend (single file, no external dependencies)
├── price_server.py            # Local HTTP server for yfinance prices (port 8765)
├── start.py                   # Cross-platform setup & start script
├── requirements.txt           # Python dependencies
└── README.md
```

---

## Technical Details

### CSV Format (Scalable Capital)

| Column      | Description                              |
|-------------|------------------------------------------|
| date        | Transaction date (DD.MM.YY)              |
| time        | Time of transaction                      |
| status      | `Executed` / `Cancelled`                |
| description | Security name                            |
| assetType   | Security / ...                           |
| type        | `Buy` / `Sell` / `Savings Plan`         |
| isin        | ISIN of the security                     |
| shares      | Number of shares                         |
| price       | Price per share                          |
| amount      | Total amount (negative for purchases)    |
| fee / tax   | Fees / taxes                             |
| currency    | Trading currency                         |

Only rows with `status = Executed` and `type = Buy / Sell / Savings Plan` are processed.  
The CSV is sorted **chronologically** (oldest first) before processing, so WACC and position calculations are correct.

### ISIN Resolution

1. Check cache (`localStorage`, version 2)
2. Batch resolution via [OpenFIGI API](https://www.openfigi.com/) (free, no key required)
3. Finnhub as single-item fallback (optional API key)
4. Send ISIN directly to yfinance server (works for many securities)

### Ticker Fallbacks (CoinShares ETPs)

Some CoinShares ETPs are not listed on Yahoo Finance Germany.  
`price_server.py` contains a `TICKER_FALLBACK` dict with alternative tickers:

| Ticker (Xetra) | Fallback     | Reason                              |
|----------------|--------------|-------------------------------------|
| CETH.DE        | GB00BLD4ZM24 | Direct ISIN (no Xetra listing)      |
| XRRL.DE        | XRPL.PA      | Euronext Paris                      |
| CSDA.DE        | CSDA.PA      | Euronext Paris                      |

Additional fallbacks can be added to `TICKER_FALLBACK` in `price_server.py`.

### Price Server API

```
GET /health
→ {"ok": true}

GET /prices?tickers=AAPL,ASML.AS,IE00BFZXGZ54
→ {"AAPL": {"price": 213.45, "currency": "USD"}, ...}
```

---

## Privacy

- No data ever leaves your browser (except price requests to Yahoo Finance / OpenFIGI)
- CSV data is stored exclusively in `localStorage`
- The price server runs locally and is only accessible via `localhost`
