#!/usr/bin/env python3
"""Bucht Orders aus einem GitHub-Issue (Text in ISSUE_BODY) in data/state.json."""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

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
    st.setdefault("orders", [])
    common.ensure(st)
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
                price = round(price * (1 + common.spread(common.cls_of(name))), 4)
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
                                            "stop": num(a[6]) if a[6] else None, "last": price,
                                            "cls": common.cls_of(name), "since": today})
                st["cash"] = round(st["cash"] - cost, 2)
                st["trades"].append({"date": today, "side": "Kauf", "name": name, "qty": qty, "price": price, "fee": fee, "note": a[7]})
                out.append(f"OK Kauf {qty:g} x {name} zu {price:.2f} EUR")
            elif cmd == "VERKAUF":  # VERKAUF;Name;Stueck;Kurs_EUR;Hinweis
                p = find(a[1]); qty, price = num(a[2]), num(a[3])
                if not p or qty > p["qty"] + 1e-9:
                    out.append(f"FEHLER: {line} (Position oder Stueckzahl passt nicht)"); continue
                price = round(price * (1 - common.spread(p.get("cls", "stock"))), 4)
                st["cash"] = round(st["cash"] + qty * price - fee, 2)
                tx = common.tax_on(st, (qty * (price - p["buy"]) - fee) * common.factor(p, dt.date.today()))
                p["qty"] = round(p["qty"] - qty, 8)
                if p["qty"] <= 1e-9: st["positions"].remove(p)
                st["trades"].append({"date": today, "side": "Verkauf", "name": a[1], "qty": qty, "price": price, "fee": fee, "note": a[4]})
                out.append(f"OK Verkauf {qty:g} x {a[1]} zu {price:.2f} EUR, Steuer {tx:.2f} EUR")
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
            elif cmd == "LIMITKAUF":  # LIMITKAUF;Name;Ticker;Waehrung;Grenze_EUR;Stueck;GueltigBis;Stop;Hinweis
                dt.date.fromisoformat(a[6])
                st["orders"].append({"side": "KAUF", "name": a[1], "ticker": a[2], "ccy": a[3] or "EUR", "limit": num(a[4]),
                                     "qty": num(a[5]), "valid_until": a[6], "stop": num(a[7]) if a[7] else None, "note": a[8]})
                out.append(f"OK Auftrag: Kauf {a[5]} x {a[1]} bei <= {a[4]} EUR, gueltig bis {a[6]}")
            elif cmd == "LIMITVERKAUF":  # LIMITVERKAUF;Name;Grenze_EUR;Stueck;GueltigBis;Hinweis
                dt.date.fromisoformat(a[4])
                st["orders"].append({"side": "VERKAUF", "name": a[1], "limit": num(a[2]), "qty": num(a[3]),
                                     "valid_until": a[4], "note": a[5]})
                out.append(f"OK Auftrag: Verkauf {a[3]} x {a[1]} bei >= {a[2]} EUR, gueltig bis {a[4]}")
            elif cmd == "LOESCHEN":  # LOESCHEN;Name  (entfernt offene Auftraege dieses Titels)
                n = len(st["orders"]); st["orders"] = [o for o in st["orders"] if o["name"].lower() != a[1].lower()]
                out.append(f"OK {n - len(st['orders'])} Auftrag/Auftraege fuer {a[1]} geloescht")
            elif cmd == "KERN":  # KERN;PAUSE  |  KERN;AN  |  KERN;ANTEIL;0,3
                c = common.core(st)
                if a[1].upper() == "PAUSE": c["paused"] = True
                elif a[1].upper() == "AN": c["paused"] = False
                elif a[1].upper() == "ANTEIL": c["share"] = num(a[2])
                else: raise ValueError("PAUSE, AN oder ANTEIL")
                out.append(f"OK Kern-Sparplan: {'pausiert' if c['paused'] else 'aktiv'}, Anteil {c['share']:.0%}")
            else:
                out.append(f"UNBEKANNT: {line}")
        except Exception as e:
            out.append(f"FEHLER: {line} ({e})")
    save(st, "data", "state.json"); save(usr, "data", "user.json")
    open(P("order_result.txt"), "w", encoding="utf-8").write("\n".join(out) or "Keine Orders erkannt.")
    print("\n".join(out))

if __name__ == "__main__":
    main()
