#!/usr/bin/env python3
"""Bucht Orders aus einem GitHub-Issue (Text in ISSUE_BODY) in data/state.json."""
import json, os, sys, difflib, datetime as dt
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
    names = lambda: [p["name"] for p in st["positions"]]

    def need(n):
        """Position mit exaktem Namen (Gross-/Kleinschreibung egal) oder Fehler mit Vorschlag."""
        p = find(n)
        if p is None:
            close = difflib.get_close_matches(n, names(), n=2, cutoff=0.4)
            hint = "Meinst du: " + " oder ".join(close) + "?" if close else "Vorhanden: " + ", ".join(names())
            raise ValueError(f"Position '{n}' nicht gefunden. {hint}")
        return p

    def share_of(s):
        v = num(s)
        if not 0 < v < 1:
            raise ValueError("Anteil muss zwischen 0 und 1 liegen, z. B. 0,12")
        return v

    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        a = [x.strip() for x in line.split(";")] + [""] * 9
        cmd = a[0].upper()
        try:
            if cmd == "KAUF":  # KAUF;Name;Ticker;Waehrung;Stueck;Kurs_EUR;Stop;Hinweis[;NEU]
                name, tick, ccy, qty, price = a[1], a[2], a[3] or "EUR", num(a[4]), num(a[5])
                if not find(name) and a[8].upper() != "NEU":
                    # Schutz vor Doppelpositionen durch falschen Namen: gleicher Ticker oder sehr aehnlicher Name
                    dup = next((x for x in st["positions"] if tick and x.get("ticker", "").lower() == tick.lower()), None)
                    sim = difflib.get_close_matches(name, names(), n=1, cutoff=0.75)
                    if dup or sim:
                        other = dup["name"] if dup else sim[0]
                        out.append(f"FEHLER: {line} (Name '{name}' ist neu, gehoert aber wohl zu '{other}'. "
                                   f"Mit exaktem Namen wiederholen, oder ;NEU ans Zeilenende, wenn es wirklich eine neue Position ist)")
                        continue
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
                p = need(a[1]); qty, price = num(a[2]), num(a[3])
                if qty > p["qty"] + 1e-9:
                    out.append(f"FEHLER: {line} (nur {p['qty']:g} Stueck vorhanden)"); continue
                price = round(price * (1 - common.spread(p.get("cls", "stock"))), 4)
                st["cash"] = round(st["cash"] + qty * price - fee, 2)
                tx = common.tax_on(st, (qty * (price - p["buy"]) - fee) * common.factor(p, dt.date.today()))
                p["qty"] = round(p["qty"] - qty, 8)
                if p["qty"] <= 1e-9: st["positions"].remove(p)
                st["trades"].append({"date": today, "side": "Verkauf", "name": p["name"], "qty": qty, "price": price, "fee": fee, "note": a[4]})
                out.append(f"OK Verkauf {qty:g} x {p['name']} zu {price:.2f} EUR, Steuer {tx:.2f} EUR")
            elif cmd == "EINZAHLUNG":  # EINZAHLUNG;Betrag;Hinweis
                amt = num(a[1]); st["cash"] = round(st["cash"] + amt, 2)
                st["deposits"].append({"date": today, "amount": amt, "note": a[2]})
                out.append(f"OK Einzahlung {amt:.2f} EUR")
            elif cmd == "STOP":  # STOP;Name;Anteil (fest vom Kaufkurs, leer = kein Stop)
                p = need(a[1]); p["stop"] = share_of(a[2]) if a[2] else None
                p.pop("trail", None); p.pop("high", None)
                out.append(f"OK Stop {p['name']}: {('fest -' + format(p['stop'] * 100, '.0f') + ' % vom Kaufkurs') if p['stop'] else 'keiner'}")
            elif cmd in ("MITLAUFEND", "FEST"):  # MITLAUFEND;Name;Anteil (vom Hoch)  |  FEST;Name;Anteil (vom Kaufkurs)
                p = need(a[1]); sh = share_of(a[2]); p["stop"] = sh
                if cmd == "MITLAUFEND":
                    p["trail"] = True; p["high"] = max(p.get("last", p["buy"]), p["buy"])
                    out.append(f"OK Stop {p['name']}: mitlaufend -{sh * 100:.0f} % vom Hoch, jetzt bei {p['high'] * (1 - sh):.2f} EUR")
                else:
                    p.pop("trail", None); p.pop("high", None)
                    out.append(f"OK Stop {p['name']}: fest -{sh * 100:.0f} % vom Kaufkurs, bei {p['buy'] * (1 - sh):.2f} EUR")
            elif cmd == "TICKER":  # TICKER;Name;Kuerzel
                p = need(a[1]); p["ticker"] = a[2]; out.append(f"OK Ticker {p['name']}: {a[2]}")
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
                p = need(a[1]); dt.date.fromisoformat(a[4])
                st["orders"].append({"side": "VERKAUF", "name": p["name"], "limit": num(a[2]), "qty": num(a[3]),
                                     "valid_until": a[4], "note": a[5]})
                out.append(f"OK Auftrag: Verkauf {a[3]} x {p['name']} bei >= {a[2]} EUR, gueltig bis {a[4]}")
            elif cmd == "LOESCHEN":  # LOESCHEN;Name  (entfernt offene Auftraege dieses Titels)
                n = len(st["orders"]); st["orders"] = [o for o in st["orders"] if o["name"].lower() != a[1].lower()]
                out.append(f"OK {n - len(st['orders'])} Auftrag/Auftraege fuer {a[1]} geloescht")
            elif cmd == "KERN":  # KERN;PAUSE  |  KERN;AN  |  KERN;ANTEIL;0,3
                c = common.core(st)
                if a[1].upper() == "PAUSE": c["paused"] = True
                elif a[1].upper() == "AN": c["paused"] = False
                elif a[1].upper() == "ANTEIL": c["share"] = num(a[2])
                elif a[1].upper() == "AUTO": c["auto"] = a[2].upper() == "AN"
                else: raise ValueError("PAUSE, AN, ANTEIL oder AUTO")
                out.append(f"OK Kern-Sparplan: {'pausiert' if c['paused'] else 'aktiv'}, Anteil {c['share']:.0%}")
            elif cmd == "ZUSAMMENFUEHREN":  # ZUSAMMENFUEHREN;Alter Name;Ziel-Name (fuehrt doppelte Positionen zusammen)
                src, dst = need(a[1]), need(a[2])
                if src is dst:
                    raise ValueError("Alter Name und Ziel-Name sind dieselbe Position")
                tot = src["qty"] + dst["qty"]
                dst["buy"] = round((src["qty"] * src["buy"] + dst["qty"] * dst["buy"]) / tot, 4)
                dst["qty"] = round(tot, 8)
                dst["since"] = min(src.get("since", dst["since"]), dst["since"])
                st["positions"].remove(src)
                for t in st["trades"]:
                    if t["name"] == src["name"]:
                        t["name"] = dst["name"]
                out.append(f"OK {a[1]} in {a[2]} zusammengefuehrt: {dst['qty']:g} Stueck, Schnitt {dst['buy']:.2f} EUR")
            elif cmd == "INFO":  # INFO;Name;Region;Branche
                p = need(a[1]); p["region"], p["sector"] = a[2], a[3]; out.append(f"OK Info {p['name']}: {a[2]}, {a[3]}")
            else:
                out.append(f"UNBEKANNT: {line}")
        except Exception as e:
            out.append(f"FEHLER: {line} ({e})")
    save(st, "data", "state.json"); save(usr, "data", "user.json")
    open(P("order_result.txt"), "w", encoding="utf-8").write("\n".join(out) or "Keine Orders erkannt.")
    print("\n".join(out))

if __name__ == "__main__":
    main()
