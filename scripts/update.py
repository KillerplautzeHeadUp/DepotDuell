#!/usr/bin/env python3
"""Taegliches Update des Depot-Duells: Kurse holen, bewerten, Stop-Loss pruefen, Daten schreiben."""
import json, os, datetime as dt, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
load = lambda *a: json.load(open(P(*a), encoding="utf-8"))

def save(obj, *a):
    with open(P(*a), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

def notify(text):
    print("MELDUNG:", text)
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
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
        return {t: (fake.get(t), None) for t in tickers}
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

def main():
    st, hist, usr = load("data", "state.json"), load("data", "history.json"), load("data", "user.json")
    today = dt.date.today()
    ds = today.isoformat()
    warn, fee = [], st["fee"]

    tickers = {p["ticker"] for p in st["positions"] if p.get("ticker")}
    tickers |= {st["benchmark"]["ticker"], "EURUSD=X"} | set(st.get("watch", []))
    st.setdefault("orders", [])
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
        notify(f"Wochenrate {st['weekly_rate']} EUR gebucht. Claude setzt sie beim naechsten Check-in ein.")

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
                cost = o["qty"] * pr + fee
                if cost > st["cash"] or (ex is None and len(st["positions"]) >= 90):
                    notify(f"Auftrag nicht ausgefuehrt (Cash oder 90-Positionen-Grenze): Kauf {o['name']}")
                    pending.append(o); continue
                if ex:
                    ex["buy"] = round((ex["qty"] * ex["buy"] + o["qty"] * pr) / (ex["qty"] + o["qty"]), 4)
                    ex["qty"] = round(ex["qty"] + o["qty"], 8); ex["last"] = round(pr, 4)
                else:
                    st["positions"].append({"name": o["name"], "ticker": o["ticker"], "ccy": o["ccy"], "qty": o["qty"],
                                            "buy": round(pr, 4), "stop": o.get("stop"), "last": round(pr, 4)})
                st["cash"] = round(st["cash"] - cost, 2)
                st["trades"].append({"date": ds, "side": "Kauf", "name": o["name"], "qty": o["qty"], "price": round(pr, 2),
                                     "fee": fee, "note": "Limit-Auftrag. " + o.get("note", "")})
                notify(f"AUFTRAG ausgefuehrt: Kauf {o['qty']:g} x {o['name']} zu {pr:.2f} EUR (Grenze {o['limit']}).")
                continue
        elif ex and ex.get("ticker"):
            pr = price_of(ex["ticker"], ex["ccy"])
            if pr is not None and pr >= o["limit"]:
                q = min(o["qty"], ex["qty"])
                st["cash"] = round(st["cash"] + q * pr - fee, 2)
                ex["qty"] = round(ex["qty"] - q, 8)
                if ex["qty"] <= 1e-9:
                    st["positions"].remove(ex)
                st["trades"].append({"date": ds, "side": "Verkauf", "name": o["name"], "qty": q, "price": round(pr, 2),
                                     "fee": fee, "note": "Limit-Auftrag. " + o.get("note", "")})
                notify(f"AUFTRAG ausgefuehrt: Verkauf {q:g} x {o['name']} zu {pr:.2f} EUR (Grenze {o['limit']}).")
                continue
        pending.append(o)
    st["orders"] = pending

    rows, keep = [], []
    for p in st["positions"]:
        last, prev = px.get(p.get("ticker"), (None, None)) if p.get("ticker") else (None, None)
        if last is None:
            price = p.get("last", p["buy"])
            warn.append(f"Kein Kurs fuer {p['name']} (Ticker '{p.get('ticker', '')}'), letzter bekannter Wert genutzt.")
        else:
            price = eur(p["ccy"], last)
            p["last"] = round(price, 4)
        # Stop-Loss
        if p.get("stop") and price <= p["buy"] * (1 - p["stop"]):
            st["cash"] += p["qty"] * price - fee
            st["trades"].append({"date": ds, "side": "Verkauf", "name": p["name"], "qty": p["qty"],
                                 "price": round(price, 2), "fee": fee, "note": f"Stop-Loss -{int(p['stop']*100)} %"})
            notify(f"STOP-LOSS: {p['name']} verkauft zu {price:.2f} EUR (Kauf {p['buy']:.2f}).")
            continue
        keep.append(p)
        if last and prev and last / prev - 1 <= -0.08:
            notify(f"Starker Tagesverlust bei {p['name']}: {100*(last/prev-1):.1f} %. Claude prueft beim Check-in.")
        rows.append({"name": p["name"], "ticker": p.get("ticker", ""), "qty": p["qty"], "buy": p["buy"],
                     "price": round(price, 2), "pct": round((price / p["buy"] - 1) * 100, 2),
                     "value": round(p["qty"] * price, 2), "stop": p.get("stop")})
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

    out = {"updated": dt.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y %H:%M Uhr"), "value": value,
           "cash": round(st["cash"], 2), "reserve": st["reserve"], "rate": st["weekly_rate"],
           "series": hist, "user": usr, "positions": rows, "trades": st["trades"][::-1][:60],
           "deposits": st["deposits"], "orders": st["orders"], "warnings": warn}
    save(st, "data", "state.json"); save(hist, "data", "history.json"); save(out, "docs", "data.json")
    print(f"Fertig: Wert {value} EUR, Index {idx}, Benchmark {bench}, Warnungen: {len(warn)}")

if __name__ == "__main__":
    main()
