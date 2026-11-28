#!/usr/bin/env python3
"""Taegliches Update des Depot-Duells: Kurse holen, bewerten, Stop-Loss pruefen, Daten schreiben."""
import json, os, sys, datetime as dt, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
load = lambda *a: json.load(open(P(*a), encoding="utf-8"))

def save(obj, *a):
    with open(P(*a), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

def notify(text):
    print("MELDUNG:", text)
    tok, chat = (os.environ.get("TELEGRAM_TOKEN") or "").strip(), (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    if not (tok and chat):
        return
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", data, timeout=20)
    except Exception as e:
        print("Telegram-Fehler:", e)

def fetch(tickers):
    """Gibt {ticker: (letzter Kurs, Vortagesschluss)} zurueck; None bei Fehlern."""
    if os.environ.get("FAKE"):
        fake = json.loads(os.environ.get("FAKE_PX", "{}"))
        return {t: (tuple(fake[t]) if isinstance(fake.get(t), list) else (fake.get(t), None)) for t in tickers}
    import yfinance as yf
    out = {}
    for t in tickers:
        last = prev = None
        try:
            tk = yf.Ticker(t)
            try:
                last = float(tk.fast_info["last_price"])
                prev = float(tk.fast_info["previous_close"])
            except Exception:
                h = tk.history(period="5d")["Close"].dropna()
                if len(h):
                    last = float(h.iloc[-1])
                    prev = float(h.iloc[-2]) if len(h) > 1 else None
        except Exception as e:
            print("Kursfehler", t, e)
        out[t] = (last, prev)
    return out

# ISINs fuer Lang & Schwarz (Schluessel = Yahoo-Ticker). Neue Titel hier ergaenzen, sonst gibt es keine Zweitquelle.
ISINS = {"EUNL.DE": "IE00B4L5Y983", "IS3N.DE": "IE00BKM4GZ66", "4GLD.DE": "DE000A0S9GB0", "ASML.AS": "NL0010273215",
         "LLY": "US5324571083", "TTE.PA": "FR0000120271", "JPM": "US46625H1005", "TSM": "US8740391003",
         "SIE.DE": "DE0007236101", "GOOGL": "US02079K3059", "EUNN.DE": "IE00B4L5YX21"}
LS_BASE = "https://www.ls-tc.de/_rpc/json/"
LS_HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
          "Referer": "https://www.ls-tc.de/", "Accept": "application/json, text/plain, */*"}

def _get_json(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def _find_key(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and v not in (None, ""):
                return v
            r = _find_key(v, key)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = _find_key(v, key)
            if r is not None:
                return r
    return None

def ls_price(isin, cache):
    """Letzter Kurs in EUR bei Lang & Schwarz (ls-tc.de) als (Kurs, Alter in Minuten), None bei Fehler.
    Die Kennung wird in cache gemerkt."""
    if os.environ.get("FAKE"):
        v = json.loads(os.environ.get("FAKE_LS", "{}")).get(isin)
        return None if v is None else (tuple(v) if isinstance(v, list) else (v, 0))
    try:
        iid = cache.get(isin)
        if not iid:
            res = _get_json(LS_BASE + ".lstc/instrument/search/main?" + urllib.parse.urlencode({"q": isin, "localeId": 2}), LS_HDR)
            iid = _find_key(res, "instrumentId")
            if iid is None:
                return None
            cache[isin] = iid
        q = urllib.parse.urlencode({"container": "chart1", "instrumentId": iid, "marketId": 1, "quotetype": "mid",
                                    "series": "intraday,history", "type": "", "localeId": 2})
        ser = _get_json(LS_BASE + "instrument/chart/dataForInstrument?" + q, LS_HDR).get("series", {})
        rows = (ser.get("intraday") or {}).get("data") or (ser.get("history") or {}).get("data") or []
        v = float(rows[-1][1]) if rows else None
        if not v or v <= 0:
            return None
        # L&S nennt die Uhrzeit in deutscher Ortszeit (als UTC-Zahl verpackt), daher den Zeitversatz addieren
        off = dt.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Berlin")).utcoffset().total_seconds()
        age = (dt.datetime.now(dt.timezone.utc).timestamp() + off - rows[-1][0] / 1000) / 60
        return v, max(0, round(age))
    except Exception as e:
        print("L&S-Fehler", isin, e)
        return None

def td_price(symbol):
    """Letzter Kurs bei Twelve Data (nur mit Schluessel TWELVE_DATA_KEY), None bei Fehler."""
    if os.environ.get("FAKE"):
        return json.loads(os.environ.get("FAKE_TD", "{}")).get(symbol)
    key = (os.environ.get("TWELVE_DATA_KEY") or "").strip()
    if not key:
        return None
    try:
        v = float(_get_json("https://api.twelvedata.com/price?" + urllib.parse.urlencode({"symbol": symbol, "apikey": key}))["price"])
        return v if v > 0 else None
    except Exception as e:
        print("Twelve-Data-Fehler", symbol, e)
        return None

def second_source(st, px, fx, warn, ds):
    """Zweite Kursquelle: Lang & Schwarz (EUR) fuer Titel mit ISIN, Twelve Data fuer Bitcoin.
    Ersetzt einen fehlenden Yahoo-Kurs und warnt bei mehr als 3 % Abweichung."""
    try:
        cache = load("data", "ls_ids.json")
    except Exception:
        cache = {}
    before = dict(cache)
    for p in st["positions"]:
        t = p.get("ticker")
        if not t:
            continue
        isin = p.get("isin") or ISINS.get(t)
        if isin and not p.get("isin"):
            p["isin"] = isin  # ISIN beim Titel merken
        if isin:
            r = ls_price(isin, cache)
            alt, age = r if r else (None, None)
        else:
            alt, age = (td_price("BTC/EUR") if "BTC" in t.upper() else None), 0
        if alt is None:
            continue
        usd = p["ccy"] == "USD"
        ylast = px.get(t, (None, None))[0]
        if ylast is None:
            px[t] = (alt * fx if usd else alt, None)
            warn.append(f"{p['name']}: Kein Yahoo-Kurs, Kurs der Zweitquelle genutzt (Alter {age} Min.).")
            continue
        dev = (ylast / fx if usd else ylast) / alt - 1
        # Nur vergleichen, wenn der Zweitkurs frisch ist: die L&S-Reihe kann in schnellen Maerkten hinterherhinken
        if age is not None and age <= 30 and abs(dev) > 0.03 and p.get("dev_alert") != ds:
            p["dev_alert"] = ds
            notify(f"KURSABWEICHUNG {p['name']}: Yahoo {(ylast / fx if usd else ylast):.2f} EUR, Zweitquelle {alt:.2f} EUR ({dev * 100:+.1f} %, Zweitkurs {age} Min. alt). Bitte pruefen.")
    if cache != before:
        save(cache, "data", "ls_ids.json")

def _today():
    return dt.date.fromisoformat(os.environ["FAKE_TODAY"]) if os.environ.get("FAKE_TODAY") else dt.date.today()

def load_meta():
    try:
        m = load("data", "user_meta.json")
    except Exception:
        m = {"start": load("data", "state.json")["start_capital"], "deposits": 1441.5}
    m.setdefault("weekly", 365.0); m.setdefault("from", "2026-11-02"); m.setdefault("last_counted", "2026-10-26")
    return m

def accrue_user_deposits():
    """Zaehlt deinen Sparplan (montags) automatisch als Einzahlung."""
    m, today = load_meta(), _today()
    d, n = dt.date.fromisoformat(m["last_counted"]) + dt.timedelta(days=7), 0
    while d <= today:
        if d.isoformat() >= m["from"] and m["weekly"] > 0:
            m["deposits"] = round(m["deposits"] + m["weekly"], 2); n += 1
        m["last_counted"] = d.isoformat(); d += dt.timedelta(days=7)
    save(m, "data", "user_meta.json")
    if n:
        notify(f"Dein Sparplan: {n} Rate(n) a {m['weekly']:.0f} EUR als Einzahlung gezaehlt (Summe {m['deposits']:.2f} EUR).")

WANT_CHECKIN = False
WANT_WATCH = False
# Anzeigenamen und ISINs der urspruenglichen Skript-Watchlist (geprueft per Suche); weitere Titel kommen per WATCH-Befehl
WATCH_SEED = {"MSFT": ("Microsoft", "US5949181045"), "NVDA": ("Nvidia", "US67066G1040"),
              "NOVO-B.CO": ("Novo Nordisk B", "DK0062498333")}

def de(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def msg_date(m):
    """Datum der Telegram-Nachricht (deutsche Zeit), sonst heutiges Datum."""
    try:
        z = __import__("zoneinfo").ZoneInfo("Europe/Berlin")
        return dt.datetime.fromtimestamp(m["date"], z).date().isoformat()
    except Exception:
        return dt.date.today().isoformat()

def public_user(usr, meta):
    """Nutzerdaten fuer die oeffentlichen Dateien. Mit PRIVAT AN nur der Index."""
    if meta.get("private"):
        return [{"date": x["date"], "idx": x["idx"]} for x in usr], {"private": True}
    keys = ("start", "deposits", "weekly", "from", "last_counted")
    return usr, {k: meta[k] for k in keys if k in meta}

def set_stop(name, share, trail):
    """Telegram: MITLAUFEND;Name;Anteil (vom Hoch) oder FEST;Name;Anteil (vom Kaufkurs)."""
    st = load("data", "state.json")
    p = next((x for x in st["positions"] if x["name"].lower() == name.strip().lower()), None)
    if p is None:
        notify("Position nicht gefunden: " + name + ". Vorhanden: " + ", ".join(x["name"] for x in st["positions"]))
        return
    p["stop"] = share
    if trail:
        p["trail"] = True
        p["high"] = max(p.get("last", p["buy"]), p["buy"])
    else:
        p.pop("trail", None); p.pop("high", None)
    save(st, "data", "state.json")
    ref = p["high"] if trail else p["buy"]
    notify(f"Stop {p['name']}: -{share * 100:.0f} % {'vom Hoch (mitlaufend)' if trail else 'vom Kaufkurs (fest)'}, aktuell bei {ref * (1 - share):.2f} EUR.")

def process_telegram():
    """Liest Nachrichten deines Bots (nur von deiner Chat-ID).
    DEPOT <Wert> [EINZAHLUNG <Betrag>], SPARPLAN <Betrag|AUS>, CHECKIN, PRIVAT AN|AUS,
    MITLAUFEND;Name;Anteil, FEST;Name;Anteil."""
    global WANT_CHECKIN, WANT_WATCH
    tok = (os.environ.get("TELEGRAM_TOKEN") or "").strip()
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    if not chat:
        return
    if os.environ.get("FAKE_TG"):
        updates = json.loads(os.environ["FAKE_TG"])
    elif tok:
        try:
            off = load("data", "tg_offset.json").get("offset")
        except Exception:
            off = None
        url = f"https://api.telegram.org/bot{tok}/getUpdates" + (f"?offset={off}" if off else "")
        try:
            updates = json.load(urllib.request.urlopen(url, timeout=20))["result"]
        except Exception as e:
            print("Telegram-Abruf-Fehler:", e)
            return
    else:
        return
    if not updates:
        return
    meta = load_meta()
    usr = load("data", "user.json")
    for u in updates:
        m = u.get("message") or {}
        if str(m.get("chat", {}).get("id")) != chat:
            continue
        raw = (m.get("text") or "").strip()
        if raw.upper().startswith(("MITLAUFEND;", "FEST;")):
            try:
                cmd, name, share = [x.strip() for x in raw.split(";")[:3]]
                sh = float(share.replace(",", "."))
                if not 0 < sh < 1:
                    raise ValueError
                set_stop(name, sh, cmd.upper() == "MITLAUFEND")
            except Exception:
                notify("Nicht verstanden. Schreibe z. B.: MITLAUFEND;Eli Lilly;0,12   oder   FEST;Eli Lilly;0,20")
            continue
        w = raw.upper().replace(",", ".").replace("€", "").split()
        if "CHECKIN" in w:
            WANT_CHECKIN = True
            continue
        if "WATCHLIST" in w:
            WANT_WATCH = True
            continue
        if "PRIVAT" in w:
            try:
                meta["private"] = w[w.index("PRIVAT") + 1] == "AN"
                notify("Privat-Modus " + ("AN: Depotwert und Einzahlungen stehen nicht mehr in der Seite. Hinweis: data/user.json und data/user_meta.json im Repository bleiben sichtbar, solange das Repository oeffentlich ist." if meta["private"] else "AUS: Depotwert und Einzahlungen stehen wieder in der Seite."))
            except Exception:
                notify("Nicht verstanden. Schreibe: PRIVAT AN   oder   PRIVAT AUS")
            continue
        if "SPARPLAN" in w:
            try:
                i = w.index("SPARPLAN"); meta["weekly"] = 0.0 if w[i + 1] == "AUS" else float(w[i + 1])
                notify(f"Dein Sparplan: {meta['weekly']:.2f} EUR pro Woche (montags).")
            except Exception:
                notify("Nicht verstanden. Schreibe z. B.: SPARPLAN 365   oder   SPARPLAN AUS")
            if "DEPOT" not in w:
                continue
        try:
            val = float(w[w.index("DEPOT") + 1])
            dep = float(w[w.index("EINZAHLUNG") + 1]) if "EINZAHLUNG" in w else 0.0
        except Exception:
            notify("Nicht verstanden. Schreibe z. B.: DEPOT 280650   oder   DEPOT 281015 EINZAHLUNG 365")
            continue
        meta["deposits"] = round(meta["deposits"] + dep, 2)
        idx = round((val - meta["deposits"]) / meta["start"] * 100, 2)
        day = msg_date(m)  # Datum der Nachricht, nicht des Laufs
        usr = [x for x in usr if x["date"] != day] + [{"date": day, "idx": idx, "value": round(val, 2),
                                                        "deposits": meta["deposits"]}]
        usr.sort(key=lambda x: x["date"])
        notify(f"Dein Depot: Index {idx:.2f} ({idx - 100:+.2f} %) seit Start, bereinigt um {meta['deposits']:.2f} EUR Einzahlungen.")
    save(usr, "data", "user.json")
    save(meta, "data", "user_meta.json")
    save({"offset": max(u["update_id"] for u in updates) + 1}, "data", "tg_offset.json")

def patch_public_files():
    """Schreibt Nutzerdaten (Index, Depotwert, Einzahlungen) in docs/data.json und docs/checkin.json neu,
    ohne Kurse abzurufen (fuer den Telegram-Lauf am Wochenende)."""
    meta, usr = load_meta(), load("data", "user.json")
    pu, pm = public_user(usr, meta)
    for fn in ("data.json", "checkin.json"):
        try:
            d = load("docs", fn)
        except Exception:
            continue
        d["user"] = pu if fn == "data.json" else (pu[-1] if pu else None)
        d["user_meta"] = pm
        save(d, "docs", fn)

def watch_stats(t):
    """Kurs, Vortag, 52-Wochen-Hoch und Waehrung eines Watchlist-Titels (Yahoo)."""
    if os.environ.get("FAKE"):
        return json.loads(os.environ.get("FAKE_WATCH", "{}")).get(t)
    try:
        import yfinance as yf
        fi = yf.Ticker(t).fast_info
        return {"last": float(fi["last_price"]), "prev": float(fi["previous_close"]),
                "high": float(fi["year_high"]), "ccy": str(fi["currency"])}
    except Exception as e:
        print("Watchlist-Fehler", t, e)
        return None

def watch_rows(st, cache):
    """Zeilen fuer die Watchlist: Kurs, Veraenderung heute, Abstand zum 52-Wochen-Hoch, Kurs bei Lang & Schwarz."""
    rows, info = [], st.get("watch_info", {})
    for t in st.get("watch", []):
        name, isin = WATCH_SEED.get(t, (t, None))
        inf = info.get(t, {})
        name, isin, reason = inf.get("name", name), inf.get("isin", isin), inf.get("reason", "")
        s = watch_stats(t) or {}
        ls = ls_price(isin, cache) if isin else None
        ok = s.get("last") and s.get("prev")
        entry = inf.get("entry")
        rows.append({"ticker": t, "name": name, "isin": isin, "reason": reason, "ccy": s.get("ccy"),
                     "entry": entry, "entry_note": inf.get("entry_note", ""),
                     "to_entry": round((s["last"] / entry - 1) * 100, 1) if entry and s.get("last") else None,
                     "price": round(s["last"], 2) if s.get("last") else None,
                     "day": round((s["last"] / s["prev"] - 1) * 100, 2) if ok else None,
                     "below_high": round((s["last"] / s["high"] - 1) * 100, 1) if s.get("last") and s.get("high") else None,
                     "ls_eur": round(ls[0], 2) if ls else None, "ls_age": ls[1] if ls else None})
    return rows

def watch_text(ck):
    L = []
    for w in ck.get("watch") or []:
        b = []
        if w.get("price") is not None:
            b.append(f"{de(w['price'], 2)} {w.get('ccy') or ''}".strip())
        if w.get("day") is not None:
            b.append(f"{w['day']:+.1f} % heute".replace(".", ","))
        if w.get("below_high") is not None:
            b.append("am 52W-Hoch" if w["below_high"] >= 0 else f"{abs(w['below_high']):.0f} % unter 52W-Hoch")
        if w.get("ls_eur") is not None:
            b.append(f"L&S {de(w['ls_eur'], 2)} EUR ({w['ls_age']} Min.)")
        if w.get("entry"):
            hit = w.get("to_entry") is not None and w["to_entry"] <= 0
            b.append(f"Einstieg bis {de(w['entry'], 2)} " + ("(Kursgrenze erreicht)" if hit else
                     f"(Kurs {w['to_entry']:.0f} % darueber)" if w.get("to_entry") is not None else ""))
        L.append(f"{w['name']}: " + (", ".join(b) or "kein Kurs"))
    return L

def checkin_text(ck):
    u = ck.get("user")
    sg = lambda x: f"{x:+.2f}".replace(".", ",")
    L = [f"Check-in, Stand {ck['updated']}",
         f"Depot {de(ck['value'])} EUR, Cash {de(ck['cash'])} EUR ({de(ck['cash_pct'], 1)} %)",
         f"Claude {sg(ck['claude_idx'] - 100)} %, Welt-ETF {sg(ck['bench_idx'] - 100)} %" +
         (f", Du {sg(u['idx'] - 100)} % ({u['date']})" if u else "")]
    if u and u.get("value") is not None:
        L.append(f"Dein Depot {de(u['value'])} EUR, Einzahlungen {de(u['deposits'], 2)} EUR")
    L.append("Positionen (Veraenderung, Puffer bis Stop):")
    for p in sorted(ck["positions"], key=lambda r: -r["weight"]):
        sd = "kein Stop" if p["stop_dist"] is None else f"Stop {p['stop_dist']:.1f} %" + (" mitlaufend" if p["trail"] else "")
        L.append(f"{p['name']} {p['pct']:+.1f} %, {sd}".replace(".", ","))
    if ck.get("watch"):
        L.append("Watchlist:")
        L += watch_text(ck)
    if ck["orders"]:
        L.append("Offene Auftraege: " + ", ".join(f"{o['side']} {o['name']}" for o in ck["orders"]))
    if ck["warnings"]:
        L.append("Hinweise: " + " ".join(ck["warnings"]))
    return "\n".join(L)

def flush_checkin():
    """Schickt auf Wunsch (Telegram: CHECKIN) den kompakten Stand zurueck."""
    global WANT_CHECKIN, WANT_WATCH
    if WANT_CHECKIN or WANT_WATCH:
        try:
            ck = load("docs", "checkin.json")
            if WANT_CHECKIN:
                notify(checkin_text(ck))
            else:
                notify("Watchlist (letzte Kurse):\n" + ("\n".join(watch_text(ck)) or "leer"))
        except Exception as e:
            notify("Auswertung nicht verfuegbar: " + str(e))
        WANT_CHECKIN = WANT_WATCH = False

def year_high(ticker):
    if os.environ.get("FAKE"):
        return json.loads(os.environ.get("FAKE_HIGH", "{}")).get(ticker)
    try:
        import yfinance as yf
        h = yf.Ticker(ticker).history(period="1y")["Close"].dropna()
        return float(h.max()) if len(h) else None
    except Exception:
        return None

def get_dividends(ticker):
    """Liste von (Ex-Tag, Betrag je Stueck in Handelswaehrung)."""
    if os.environ.get("FAKE"):
        return [tuple(x) for x in json.loads(os.environ.get("FAKE_DIV", "{}")).get(ticker, [])]
    try:
        import yfinance as yf
        return [(d.strftime("%Y-%m-%d"), float(v)) for d, v in yf.Ticker(ticker).dividends.items()]
    except Exception as e:
        print("Dividendenfehler", ticker, e)
        return []

def main():
    accrue_user_deposits()
    process_telegram()
    st, hist, usr = load("data", "state.json"), load("data", "history.json"), load("data", "user.json")
    today = dt.date.fromisoformat(os.environ["FAKE_TODAY"]) if os.environ.get("FAKE_TODAY") else dt.date.today()
    ds = today.isoformat()
    warn, fee = [], st["fee"]

    tickers = {p["ticker"] for p in st["positions"] if p.get("ticker")}
    tickers |= {st["benchmark"]["ticker"], "EURUSD=X"} | set(st.get("watch", []))
    st.setdefault("orders", [])
    common.ensure(st)
    tickers |= {o["ticker"] for o in st["orders"] if o.get("ticker")}
    px = fetch(sorted(tickers))
    fx = px["EURUSD=X"][0] or st.get("last_fx", 1.12)
    st["last_fx"] = fx
    eur = lambda ccy, v: v / fx if ccy == "USD" else v
    try:
        second_source(st, px, fx, warn, ds)
    except Exception as e:
        print("Zweitquelle uebersprungen:", e)

    # Wochenrate jeden Freitag ab savings_from
    dep_today = sum(d["amount"] for d in st["deposits"] if d["date"] == ds)
    if today.weekday() == 4 and ds >= st["savings_from"] and st.get("last_deposit") != ds:
        st["cash"] += st["weekly_rate"]
        st["deposits"].append({"date": ds, "amount": st["weekly_rate"], "note": "Wochenrate"})
        st["last_deposit"] = ds
        dep_today += st["weekly_rate"]
        notify(f"Wochenrate {st['weekly_rate']} EUR gebucht. Ein Teil geht in den Kern-Sparplan, der Rest bleibt Cash fuer den naechsten Check-in.")

    # Dividenden (Steuer wird sofort abgezogen)
    chk = st.get("div_checked", st["start_date"])
    for p in st["positions"]:
        if p["cls"] not in ("stock", "etf") or not p.get("ticker"):
            continue
        for d, amt in get_dividends(p["ticker"]):
            if chk < d <= ds and d > p["since"]:
                per = eur(p["ccy"], amt)
                gross = round(p["qty"] * per, 2)
                st["cash"] = round(st["cash"] + gross, 2)
                tx = common.tax_on(st, gross * common.factor(p, today))
                st["trades"].append({"date": ds, "side": "Dividende", "name": p["name"], "qty": p["qty"], "price": round(per, 4),
                                     "fee": 0, "note": f"Ex-Tag {d}, brutto {gross:.2f} EUR, Steuer {tx:.2f} EUR"})
                notify(f"DIVIDENDE {p['name']}: brutto {gross:.2f} EUR, Steuer {tx:.2f} EUR.")
    st["div_checked"] = ds

    # Bedingte Auftraege (Limit-Orders)
    def price_of(tk, ccy):
        l = px.get(tk, (None, None))[0] if tk else None
        return None if l is None else eur(ccy, l)
    pending = []
    for o in st["orders"]:
        if ds > o["valid_until"]:
            notify(f"Auftrag abgelaufen: {o['side']} {o['name']} (Grenze {o['limit']} EUR)")
            continue
        ex = next((x for x in st["positions"] if x["name"] == o["name"]), None)
        if o["side"] == "KAUF":
            pr = price_of(o["ticker"], o["ccy"])
            if pr is not None and pr <= o["limit"]:
                epr = pr * (1 + common.spread(common.cls_of(o["name"])))
                cost = o["qty"] * epr + fee
                if cost > st["cash"] or (ex is None and len(st["positions"]) >= 90):
                    notify(f"Auftrag nicht ausgefuehrt (Cash oder 90-Positionen-Grenze): Kauf {o['name']}")
                    pending.append(o); continue
                if ex:
                    ex["buy"] = round((ex["qty"] * ex["buy"] + o["qty"] * epr) / (ex["qty"] + o["qty"]), 4)
                    ex["qty"] = round(ex["qty"] + o["qty"], 8); ex["last"] = round(pr, 4)
                    if o.get("isin") and not ex.get("isin"): ex["isin"] = o["isin"]
                else:
                    st["positions"].append({"name": o["name"], "ticker": o["ticker"], "ccy": o["ccy"], "qty": o["qty"],
                                            "buy": round(epr, 4), "stop": o.get("stop"), "last": round(pr, 4),
                                            "cls": common.cls_of(o["name"]), "since": ds, "isin": o.get("isin")})
                st["cash"] = round(st["cash"] - cost, 2)
                st["trades"].append({"date": ds, "side": "Kauf", "name": o["name"], "qty": o["qty"], "price": round(epr, 2),
                                     "fee": fee, "note": "Limit-Auftrag. " + o.get("note", "")})
                notify(f"AUFTRAG ausgefuehrt: Kauf {o['qty']:g} x {o['name']} zu {epr:.2f} EUR (Grenze {o['limit']}).")
                continue
        elif ex and ex.get("ticker"):
            pr = price_of(ex["ticker"], ex["ccy"])
            if pr is not None and pr >= o["limit"]:
                q = min(o["qty"], ex["qty"]); epr = pr * (1 - common.spread(ex["cls"]))
                st["cash"] = round(st["cash"] + q * epr - fee, 2)
                tx = common.tax_on(st, (q * (epr - ex["buy"]) - fee) * common.factor(ex, today))
                ex["qty"] = round(ex["qty"] - q, 8)
                if ex["qty"] <= 1e-9:
                    st["positions"].remove(ex)
                st["trades"].append({"date": ds, "side": "Verkauf", "name": o["name"], "qty": q, "price": round(epr, 2),
                                     "fee": fee, "note": f"Limit-Auftrag, Steuer {tx:.2f} EUR. " + o.get("note", "")})
                notify(f"AUFTRAG ausgefuehrt: Verkauf {q:g} x {o['name']} zu {epr:.2f} EUR, Steuer {tx:.2f} EUR.")
                continue
        pending.append(o)
    st["orders"] = pending

    # Kern-Sparplan: Teil der Wochenrate geht automatisch in den am staerksten untergewichteten Kern-ETF (Sparplan ohne Gebuehr)
    cr = common.core(st)
    if st.get("last_deposit") == ds and st.get("last_core") != ds and not cr["paused"]:
        st["last_core"] = ds
        share, rule = cr["share"], "Basis"
        if cr.get("auto", True):  # Autopilot-Regeln (von Claude festgelegt)
            q = st["cash"] / max(1.0, st["cash"] + sum(p["qty"] * p.get("last", p["buy"]) for p in st["positions"]))
            hi, bp = year_high(st["benchmark"]["ticker"]), price_of(st["benchmark"]["ticker"], "EUR")
            if hi and bp and bp / hi - 1 <= -0.10:
                share, rule = 0.8, "Welt-ETF über 10 % unter Jahreshoch"
            elif q > 0.25:
                share, rule = 0.7, "Cash-Quote über 25 %"
            elif q < 0.10:
                share, rule = 0.3, "Cash-Quote unter 10 %"
        cr["effective"], cr["rule"] = share, rule
        amt = round(min(st["weekly_rate"] * share, st["cash"]), 2)
        tg = {}
        for p in st["positions"]:
            if p["name"] in cr["targets"]:
                tg[p["name"]] = (p, price_of(p.get("ticker"), p["ccy"]) or p.get("last", p["buy"]))
        if tg and amt > 0:
            tot = sum(p["qty"] * pr for p, pr in tg.values()) + amt
            name = max(tg, key=lambda n: cr["targets"][n] * tot - tg[n][0]["qty"] * tg[n][1])
            p, pr = tg[name]
            qty = round(amt / pr, 4); cost = round(qty * pr, 2)
            p["buy"] = round((p["qty"] * p["buy"] + cost) / (p["qty"] + qty), 4)
            p["qty"] = round(p["qty"] + qty, 8)
            st["cash"] = round(st["cash"] - cost, 2)
            st["trades"].append({"date": ds, "side": "Kauf", "name": name, "qty": qty, "price": round(pr, 2), "fee": 0,
                                 "note": "Kern-Sparplan"})
            notify(f"KERN-SPARPLAN: {qty:g} x {name} zu {pr:.2f} EUR ({cost:.2f} EUR). Anteil {share:.0%} ({rule}).")

    rows, keep = [], []
    for p in st["positions"]:
        last, prev = px.get(p.get("ticker"), (None, None)) if p.get("ticker") else (None, None)
        if last is not None and prev and abs(last / prev - 1) > 0.30:
            warn.append(f"Unplausibler Kurssprung bei {p['name']} ({100*(last/prev-1):.0f} %), Kurs ignoriert.")
            last = None
        if last is None:
            price = p.get("last", p["buy"])
            warn.append(f"Kein Kurs fuer {p['name']} (Ticker '{p.get('ticker', '')}'), letzter bekannter Wert genutzt.")
            p["miss"] = p.get("miss", 0) + 1
            if p["miss"] == 4:  # etwa zwei Stunden ohne Kurs
                notify(f"KURSAUSFALL: {p['name']} seit {p['miss']} Laeufen ohne Kurs (Yahoo). Werte sind veraltet.")
        else:
            price = eur(p["ccy"], last)
            p["last"] = round(price, 4)
            p.pop("miss", None)
        # Stop-Loss (fest vom Kaufkurs, oder mitlaufend vom Hoch seit Aktivierung)
        ref = p["buy"]
        if p.get("trail"):
            p["high"] = max(p.get("high", p["buy"]), price)
            ref = p["high"]
        if p.get("stop") and price <= ref * (1 - p["stop"]):
            epr = price * (1 - common.spread(p["cls"]))
            st["cash"] = round(st["cash"] + p["qty"] * epr - fee, 2)
            tx = common.tax_on(st, (p["qty"] * (epr - p["buy"]) - fee) * common.factor(p, today))
            st["trades"].append({"date": ds, "side": "Verkauf", "name": p["name"], "qty": p["qty"], "price": round(epr, 2),
                                 "fee": fee, "note": f"Stop-Loss -{int(p['stop']*100)} %{' vom Hoch' if p.get('trail') else ''}, Steuer {tx:.2f} EUR"})
            notify(f"STOP-LOSS: {p['name']} verkauft zu {epr:.2f} EUR (Kauf {p['buy']:.2f}), Steuer {tx:.2f} EUR.")
            continue
        keep.append(p)
        if last and prev and last / prev - 1 <= -0.08:
            notify(f"Starker Tagesverlust bei {p['name']}: {100*(last/prev-1):.1f} %. Claude prueft beim Check-in.")
        rows.append({"name": p["name"], "ticker": p.get("ticker", ""), "qty": p["qty"], "buy": p["buy"],
                     "price": round(price, 2), "pct": round((price / p["buy"] - 1) * 100, 2),
                     "value": round(p["qty"] * price, 2), "stop": p.get("stop"),
                     "gain": round(p["qty"] * (price - p["buy"]), 2), "region": common.meta(p)[0],
                     "sector": common.meta(p)[1], "origin": common.origin(st, p["name"]),
                     "trail": bool(p.get("trail")),
                     "stop_price": round(ref * (1 - p["stop"]), 2) if p.get("stop") else None,
                     "stop_dist": round((1 - ref * (1 - p["stop"]) / price) * 100, 1) if p.get("stop") and price else None})
        sd = rows[-1]["stop_dist"]
        if sd is not None and sd < 5 and p.get("stop_alert") != ds:
            p["stop_alert"] = ds  # hoechstens eine Warnung pro Tag und Titel
            notify(f"STOP-NAEHE {p['name']}: nur noch {sd:.1f} % bis zum Stop bei {rows[-1]['stop_price']:.2f} EUR.")
    st["positions"] = keep

    # Chancen-Hinweis fuer die Backup-Reserve (Watchlist, Tagesverlust ab 10 %)
    for t in st.get("watch", []):
        last, prev = px.get(t, (None, None))
        if last and prev and last / prev - 1 <= -0.10:
            notify(f"CHANCE pruefen: {t} {100*(last/prev-1):.1f} % an einem Tag. Backup-Reserve {st['reserve']} EUR steht bereit.")

    value = round(st["cash"] + sum(r["value"] for r in rows), 2)
    for r in rows:
        r["weight"] = round(r["value"] / value * 100, 1)

    prev_rec = [h for h in hist if h["date"] < ds]
    prev_rec = prev_rec[-1] if prev_rec else {"value": st["start_capital"], "idx": 100.0}
    idx = round(prev_rec["idx"] * (value - dep_today) / prev_rec["value"], 2)
    bl = px[st["benchmark"]["ticker"]][0]
    bench = round(bl / st["benchmark"]["start_price"] * 100, 2) if bl else (hist[-1]["bench"] if hist else 100.0)
    hist = [h for h in hist if h["date"] != ds] + [{"date": ds, "value": value, "idx": idx, "bench": bench}]

    # Wochenbericht freitags abends per Telegram
    now_b = dt.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Berlin"))
    hour = int(os.environ.get("FAKE_HOUR", now_b.hour))
    if today.weekday() == 4 and hour >= 19 and st.get("last_report") != ds:
        st["last_report"] = ds
        srt = sorted(rows, key=lambda r: r["pct"])
        u = usr[-1]["idx"] if usr else None
        pi = st.get("report_idx")
        wk = f"{100 * (idx / pi - 1):+.2f} %" if pi else "–"
        st["report_idx"] = idx
        eu = lambda x: f"{x:,.0f}".replace(",", ".")
        fmt = lambda r: f"{r['name']} {r['pct']:+.1f} %"
        notify(f"Wochenbericht {ds}\nDepot: {eu(value)} EUR, Cash {eu(st['cash'])} EUR\n"
               f"Claude: {idx - 100:+.2f} % seit Start (Woche {wk})\nWelt-ETF: {bench - 100:+.2f} %\n"
               f"Du: {'–' if u is None else format(u - 100, '+.2f') + ' % (Stand ' + usr[-1]['date'] + ')'}\n"
               f"Beste: {', '.join(fmt(r) for r in srt[::-1][:3])}\nSchwaechste: {', '.join(fmt(r) for r in srt[:3])}\n"
               f"Steuern bisher: {st['tax']['paid']:.2f} EUR")

    # Stress-Pause: Tagesverlust ueber 7 % stoppt den Kern-Sparplan bis zum naechsten Check-in
    if idx / prev_rec["idx"] - 1 <= -0.07 and not cr["paused"]:
        cr["paused"] = True
        notify(f"Kern-Sparplan pausiert: Tagesverlust {100 * (idx / prev_rec['idx'] - 1):.1f} %. Claude entscheidet beim naechsten Check-in.")

    # Auswertung: Risiko, Aufteilung, Herkunft der Entscheidungen, Tagesverlauf
    ser, bs = [h["idx"] for h in hist], [h["bench"] for h in hist]
    def mdd(a):
        peak, m = a[0], 0.0
        for x in a:
            peak = max(peak, x); m = min(m, x / peak - 1)
        return round(m * 100, 2)
    risk = {"n": len(ser), "mdd": mdd(ser), "mdd_b": mdd(bs), "vol": None, "beta": None}
    if len(ser) >= 21:
        import statistics as S
        r1 = [ser[i] / ser[i - 1] - 1 for i in range(1, len(ser))]; r2 = [bs[i] / bs[i - 1] - 1 for i in range(1, len(bs))]
        risk["vol"] = round(S.pstdev(r1) * (252 ** 0.5) * 100, 1)
        vb = S.pvariance(r2)
        if vb > 0:
            m1, m2 = S.mean(r1), S.mean(r2)
            risk["beta"] = round(sum((x - m1) * (y - m2) for x, y in zip(r1, r2)) / len(r1) / vb, 2)
    reg, sec, og = {"Cash": round(st["cash"] / value * 100, 1)}, {"Cash": round(st["cash"] / value * 100, 1)}, {}
    for r in rows:
        reg[r["region"]] = round(reg.get(r["region"], 0) + r["weight"], 1)
        sec[r["sector"]] = round(sec.get(r["sector"], 0) + r["weight"], 1)
        g = og.setdefault(r["origin"], {"cost": 0.0, "gain": 0.0, "n": 0})
        g["cost"] += r["qty"] * r["buy"]; g["gain"] += r["gain"]; g["n"] += 1
    origin = [{"name": k, "n": v["n"], "cost": round(v["cost"]), "gain": round(v["gain"], 2),
               "pct": round(v["gain"] / v["cost"] * 100, 2) if v["cost"] else 0} for k, v in og.items()]
    try:
        intr = load("data", "intraday.json")
    except Exception:
        intr = []
    now_i = dt.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Berlin"))
    intr.append({"t": now_i.strftime("%Y-%m-%d %H:%M"), "v": idx, "b": bench})
    cut = (today - dt.timedelta(days=7)).isoformat()
    intr = [x for x in intr if x["t"][:10] >= cut]
    save(intr, "data", "intraday.json")

    pu, pm = public_user(usr, load_meta())
    try:
        wc = load("data", "ls_ids.json")
    except Exception:
        wc = {}
    wc0 = dict(wc)
    try:
        wrows = watch_rows(st, wc)
    except Exception as e:
        print("Watchlist uebersprungen:", e)
        wrows = []
    if wc != wc0:
        save(wc, "data", "ls_ids.json")
    out = {"updated": dt.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y %H:%M Uhr"), "value": value,
           "cash": round(st["cash"], 2), "reserve": st["reserve"], "rate": st["weekly_rate"],
           "series": hist, "user": pu, "user_meta": pm,  # Einzahlungen des Nutzers (bei PRIVAT AN nur Index)
           "positions": rows, "trades": st["trades"][::-1][:60],
           "deposits": st["deposits"], "orders": st["orders"], "tax_paid": st["tax"]["paid"], "core": st["core"], "risk": risk,
           "alloc": {"region": reg, "sector": sec}, "watch": wrows, "origin": origin, "intraday": intr, "start": st["start_capital"], "warnings": warn}
    ck = {"updated": out["updated"], "value": value, "cash": out["cash"], "cash_pct": round(st["cash"] / value * 100, 1),
          "claude_idx": idx, "bench_idx": bench, "user": pu[-1] if pu else None, "user_meta": pm, "core": st["core"],
          "positions": [{"name": r["name"], "price": r["price"], "pct": r["pct"], "weight": r["weight"], "stop_price": r["stop_price"],
                         "stop_dist": r["stop_dist"], "trail": r["trail"]} for r in rows],
          "trades": st["trades"][::-1][:5], "orders": st["orders"], "warnings": warn, "watch": wrows}
    save(st, "data", "state.json"); save(hist, "data", "history.json"); save(out, "docs", "data.json"); save(ck, "docs", "checkin.json")
    print(f"Fertig: Wert {value} EUR, Index {idx}, Benchmark {bench}, Warnungen: {len(warn)}")
    flush_checkin()

if __name__ == "__main__":
    main()
