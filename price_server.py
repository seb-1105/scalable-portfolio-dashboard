#!/usr/bin/env python3
"""
Lokaler Kursserver für Portfolio Dashboard
─────────────────────────────────────────
Nutzt yfinance (kein CORS-Problem, alle Weltbörsen).

Start:   python3 price_server.py
Läuft:   http://localhost:8765

Abhängigkeit installieren:
    pip install yfinance
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, urllib.parse, concurrent.futures

try:
    import yfinance as yf
except ImportError:
    print("yfinance fehlt. Installieren mit:  pip install yfinance")
    raise SystemExit(1)

PORT = 8765

# Tickers, die Yahoo Finance nicht direkt kennt → Fallback auf funktionierende Alternative
# (gleiche Produkte, anderer Handelsplatz oder ISIN direkt)
TICKER_FALLBACK = {
    'CETH.DE':  'GB00BLD4ZM24',  # CoinShares Physical Staked Ethereum (ISIN)
    'XRRL.DE':  'XRPL.PA',       # CoinShares XRP ETP (Paris, EUR)
    'CSDA.DE':  'CSDA.PA',       # CoinShares Physical Staked Cardano (Paris, EUR)
}


def fetch_one(sym: str):
    """Holt Preis + Währung für einen einzelnen Ticker via yfinance.
    Nutzt TICKER_FALLBACK wenn der direkte Ticker bei Yahoo nicht verfügbar ist."""
    actual = TICKER_FALLBACK.get(sym, sym)
    try:
        fi = yf.Ticker(actual).fast_info
        price    = fi.last_price
        currency = fi.currency
        if price and float(price) > 0:
            return sym, {"price": round(float(price), 6), "currency": currency}
    except Exception:
        pass
    return sym, None


class Handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._send(200, b"{}")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # ── Healthcheck ──────────────────────────────────────────────
        if parsed.path == "/health":
            self._send(200, json.dumps({"ok": True}).encode())
            return

        # ── Batch-Kursabfrage ────────────────────────────────────────
        if parsed.path == "/prices":
            params  = urllib.parse.parse_qs(parsed.query)
            raw     = params.get("tickers", [""])[0]
            tickers = [t.strip() for t in raw.split(",") if t.strip()]

            result = {}
            if tickers:
                # Parallele Abfragen (ThreadPool, max. 12 gleichzeitig)
                with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
                    futures = {ex.submit(fetch_one, sym): sym for sym in tickers}
                    for fut in concurrent.futures.as_completed(futures):
                        sym, data = fut.result()
                        if data:
                            result[sym] = data

            self._send(200, json.dumps(result).encode())
            return

        self._send(404, b'{"error":"not found"}')

    def _send(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type",  "application/json")
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Kompaktes Logging: Methode + Pfad + Statuscode
        print(f"  {self.command:7s} {self.path[:80]:80s}  →  {args[1]}")


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"Portfolio Kursserver läuft  ▶  http://localhost:{PORT}")
    print("Stoppen mit Ctrl+C\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\nServer gestoppt.")
