#!/usr/bin/env python3
"""Probelauf: Vergleicht fuer unsere Positionen Yahoo, Lang & Schwarz (ls-tc.de) und Twelve Data.
Aendert nichts am Depot. Liest nur data/state.json und druckt eine Zeile je Titel."""
import json, os, time, datetime as dt, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = (os.environ.get("TWELVE_DATA_KEY") or "").strip()

# ISINs aus dem Gedaechtnis (Suche nach Anfang des Namens), unbekannte Namen werden per Name gesucht
ISINS = {
    "ishares core msci world": "IE00B4L5Y983", "ishares core msci em": "IE00BKM4GZ66", "xetra-gold": "DE000A0S9GB0",
    "asml": "NL0010273215", "eli lilly": "US5324571083", "totalenergies": "FR0000120271",
    "jpmorgan": "US46625H1005", "tsmc": "US8740391003", "siemens": "DE0007236101", "alphabet": "US02079K3059",
    "ishares core msci japan": "IE00B4L5YX21",
}
MIC = {".DE": "XETR", ".PA": "XPAR", ".AS": "XAMS", ".MI": "XMIL", ".L": "XLON"}
HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
       "Referer": "https://www.ls-tc.de/", "Accept": "application/json, text/plain, */*"}
LS = "https://www.ls-tc.de/_rpc/json/"

def get(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def find_key(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and v not in (None, ""):
                return v
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_key(v, key)
            if r is not None:
                return r
    return None

def yahoo(t):
    try:
        import yfinance as yf
        return f"{float(yf.Ticker(t).fast_info['last_price']):.2f}"
    except Exception as e:
        return f"Fehler {type(e).__name__}"

def lands(name, tick):
    if "btc" in tick.lower() or "bitcoin" in name.lower():
        return "kein ISIN (Krypto)"
    isin = next((v for k, v in ISINS.items() if name.lower().startswith(k)), None)
    try:
        res = get(LS + ".lstc/instrument/search/main?" + urllib.parse.urlencode({"q": isin or name, "localeId": 2}), HDR)
        iid = find_key(res, "instrumentId")
        if iid is None:
            return f"keine Kennung ({isin or name})"
        q = urllib.parse.urlencode({"container": "chart1", "instrumentId": iid, "marketId": 1, "quotetype": "mid",
                                    "series": "intraday,history", "type": "", "localeId": 2})
        ser = get(LS + "instrument/chart/dataForInstrument?" + q, HDR).get("series", {})
        rows = (ser.get("intraday") or {}).get("data") or (ser.get("history") or {}).get("data") or []
        if not rows:
            return f"id {iid}, keine Kursdaten"
        t = dt.datetime.fromtimestamp(rows[-1][0] / 1000, dt.timezone.utc).strftime("%d.%m. %H:%M UTC")
        return f"{rows[-1][1]} ({t})"
    except Exception as e:
        return f"Fehler {type(e).__name__}: {str(e)[:60]}"

def twelve(tick):
    if not KEY:
        return "kein Schluessel"
    if "-EUR" in tick.upper():
        sym, ex = tick.upper().replace("-", "/"), None
    else:
        base, suf = (tick.rsplit(".", 1) + [""])[:2] if "." in tick else (tick, "")
        sym, ex = base, MIC.get("." + suf if suf else "")
    q = {"symbol": sym, "apikey": KEY}
    if ex:
        q["exchange"] = ex
    try:
        r = get("https://api.twelvedata.com/price?" + urllib.parse.urlencode(q))
        if "price" in r:
            return f"{float(r['price']):.2f} ({ex or 'USA/Krypto'})"
        return f"{r.get('status', 'Fehler')}: {str(r.get('message', r))[:90]}"
    except Exception as e:
        return f"Fehler {type(e).__name__}: {str(e)[:60]}"

def main():
    st = json.load(open(os.path.join(ROOT, "data", "state.json"), encoding="utf-8"))
    print("Titel | Yahoo | Lang & Schwarz | Twelve Data   (Dollar-Titel: Yahoo/Twelve in USD, L&S in EUR)")
    for p in st["positions"]:
        t = p.get("ticker") or ""
        print(f"{p['name']} [{t}] | Yahoo {yahoo(t) if t else '-'} | L&S {lands(p['name'], t)} | TD {twelve(t) if t else '-'}", flush=True)
        if KEY:
            time.sleep(8)  # kostenlose Stufe: 8 Abfragen pro Minute

if __name__ == "__main__":
    main()
