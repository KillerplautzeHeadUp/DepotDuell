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

def process_telegram():
    """Liest Nachrichten deines Bots (nur von deiner Chat-ID): DEPOT <Wert> [EINZAHLUNG <Betrag>]."""
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
    today = dt.date.today().isoformat()
    for u in updates:
        m = u.get("message") or {}
        if str(m.get("chat", {}).get("id")) != chat:
            continue
        w = (m.get("text") or "").upper().replace(",", ".").replace("€", "").split()
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
        # NEU: Depotwert und Einzahlungssumme je Meldung mitspeichern (steht dann in data.json)
        usr = [x for x in usr if x["date"] != today] + [{"date": today, "idx": idx, "value": round(val, 2),
                                                          "deposits": meta["deposits"]}]
        usr.sort(key=lambda x: x["date"])
        notify(f"Dein Depot: Index {idx:.2f} ({idx - 100:+.2f} %) seit Start, bereinigt um {meta['deposits']:.2f} EUR Einzahlungen.")
    save(usr, "data", "user.json")
    save(meta, "data", "user_meta.json")
    save({"offset": max(u["update_id"] for u in updates) + 1}, "data", "tg_offset.json")

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
                else:
                    st["positions"].append({"name": o["name"], "ticker": o["ticker"], "ccy": o["ccy"], "qty": o["qty"],
                                            "buy": round(epr, 4), "stop": o.get("stop"), "last": round(pr, 4),
                                            "cls": common.cls_of(o["name"]), "since": ds})
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
        else:
            price = eur(p["ccy"], last)
            p["last"] = round(price, 4)
        # Stop-Loss
        if p.get("stop") and price <= p["buy"] * (1 - p["stop"]):
            epr = price * (1 - common.spread(p["cls"]))
            st["cash"] = round(st["cash"] + p["qty"] * epr - fee, 2)
            tx = common.tax_on(st, (p["qty"] * (epr - p["buy"]) - fee) * common.factor(p, today))
            st["trades"].append({"date": ds, "side": "Verkauf", "name": p["name"], "qty": p["qty"], "price": round(epr, 2),
                                 "fee": fee, "note": f"Stop-Loss -{int(p['stop']*100)} %, Steuer {tx:.2f} EUR"})
            notify(f"STOP-LOSS: {p['name']} verkauft zu {epr:.2f} EUR (Kauf {p['buy']:.2f}), Steuer {tx:.2f} EUR.")
            continue
        keep.append(p)
        if last and prev and last / prev - 1 <= -0.08:
            notify(f"Starker Tagesverlust bei {p['name']}: {100*(last/prev-1):.1f} %. Claude prueft beim Check-in.")
        rows.append({"name": p["name"], "ticker": p.get("ticker", ""), "qty": p["qty"], "buy": p["buy"],
                     "price": round(price, 2), "pct": round((price / p["buy"] - 1) * 100, 2),
                     "value": round(p["qty"] * price, 2), "stop": p.get("stop"),
                     "gain": round(p["qty"] * (price - p["buy"]), 2), "region": common.meta(p)[0],
                     "sector": common.meta(p)[1], "origin": common.origin(st, p["name"])})
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
               f"Du: {'–' if u is None else format(u - 100, '+.2f') + ' %'}\n"
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

    out = {"updated": dt.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y %H:%M Uhr"), "value": value,
           "cash": round(st["cash"], 2), "reserve": st["reserve"], "rate": st["weekly_rate"],
           "series": hist, "user": usr, "user_meta": load_meta(),  # NEU: Einzahlungen des Nutzers in data.json
           "positions": rows, "trades": st["trades"][::-1][:60],
           "deposits": st["deposits"], "orders": st["orders"], "tax_paid": st["tax"]["paid"], "core": st["core"], "risk": risk,
           "alloc": {"region": reg, "sector": sec}, "origin": origin, "intraday": intr, "start": st["start_capital"], "warnings": warn}
    save(st, "data", "state.json"); save(hist, "data", "history.json"); save(out, "docs", "data.json")
    print(f"Fertig: Wert {value} EUR, Index {idx}, Benchmark {bench}, Warnungen: {len(warn)}")

if __name__ == "__main__":
    main()
