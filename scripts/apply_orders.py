#!/usr/bin/env python3
"""Bucht Orders aus einem GitHub-Issue (Text in ISSUE_BODY) in data/state.json."""
import json, os, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
load = lambda *a: json.load(open(P(*a), encoding="utf-8"))

def save(obj, *a):
    with open(P(*a), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

num = lambda s: float(str(s).replace("€", "").replace(" ", "").replace(",", "."))

def main():
    body = os.environ.get("ISSUE_BODY", "")
    st, usr = load("data", "state.json"), load("data", "user.json")
    today, fee, out = dt.date.today().isoformat(), load("data", "state.json")["fee"], []
    find = lambda n: next((p for p in st["positions"] if p["name"].lower() == n.lower()), None)
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        a = [x.strip() for x in line.split(";")] + [""] * 8
        cmd = a[0].upper()
        try:
            if cmd == "KAUF":  # KAUF;Name;Ticker;Waehrung;Stueck;Kurs_EUR;Stop;Hinweis
                name, tick, ccy, qty, price = a[1], a[2], a[3] or "EUR", num(a[4]), num(a[5])
                cost = qty * price + fee
                if cost > st["cash"]:
                    out.append(f"FEHLER: {line} (Cash {st['cash']:.2f} reicht nicht)"); continue
                p = find(name)
                if p:
                    p["buy"] = round((p["qty"] * p["buy"] + qty * price) / (p["qty"] + qty), 4)
                    p["qty"] = round(p["qty"] + qty, 8)
                    if tick: p["ticker"] = tick
                else:
                    st["positions"].append({"name": name, "ticker": tick, "ccy": ccy, "qty": qty, "buy": price,
                                            "stop": num(a[6]) if a[6] else None, "last": price})
                st["cash"] = round(st["cash"] - cost, 2)
                st["trades"].append({"date": today, "side": "Kauf", "name": name, "qty": qty, "price": price, "fee": fee, "note": a[7]})
                out.append(f"OK Kauf {qty:g} x {name} zu {price:.2f} EUR")
            elif cmd == "VERKAUF":  # VERKAUF;Name;Stueck;Kurs_EUR;Hinweis
                p = find(a[1]); qty, price = num(a[2]), num(a[3])
                if not p or qty > p["qty"] + 1e-9:
                    out.append(f"FEHLER: {line} (Position oder Stueckzahl passt nicht)"); continue
                st["cash"] = round(st["cash"] + qty * price - fee, 2)
                p["qty"] = round(p["qty"] - qty, 8)
                if p["qty"] <= 1e-9: st["positions"].remove(p)
                st["trades"].append({"date": today, "side": "Verkauf", "name": a[1], "qty": qty, "price": price, "fee": fee, "note": a[4]})
                out.append(f"OK Verkauf {qty:g} x {a[1]} zu {price:.2f} EUR")
            elif cmd == "EINZAHLUNG":  # EINZAHLUNG;Betrag;Hinweis
                amt = num(a[1]); st["cash"] = round(st["cash"] + amt, 2)
                st["deposits"].append({"date": today, "amount": amt, "note": a[2]})
                out.append(f"OK Einzahlung {amt:.2f} EUR")
            elif cmd == "STOP":  # STOP;Name;Anteil (leer = kein Stop)
                p = find(a[1]); p["stop"] = num(a[2]) if a[2] else None; out.append(f"OK Stop {a[1]}: {a[2] or 'keiner'}")
            elif cmd == "TICKER":  # TICKER;Name;Kuerzel
                p = find(a[1]); p["ticker"] = a[2]; out.append(f"OK Ticker {a[1]}: {a[2]}")
            elif cmd == "USER":  # USER;Datum;Index
                d, i = a[1] or today, num(a[2])
                usr = [u for u in usr if u["date"] != d] + [{"date": d, "idx": i}]
                usr.sort(key=lambda u: u["date"]); out.append(f"OK Dein Index {d}: {i}")
            else:
                out.append(f"UNBEKANNT: {line}")
        except Exception as e:
            out.append(f"FEHLER: {line} ({e})")
    save(st, "data", "state.json"); save(usr, "data", "user.json")
    open(P("order_result.txt"), "w", encoding="utf-8").write("\n".join(out) or "Keine Orders erkannt.")
    print("\n".join(out))

if __name__ == "__main__":
    main()
