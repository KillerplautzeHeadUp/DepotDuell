"""Gemeinsame Hilfen: Steuer-Naeherung (deutsches Privatdepot) und Spreads."""
import datetime as dt

RATE = 0.26375  # 25 % Abgeltungsteuer + 5,5 % Soli, ohne Kirchensteuer

def cls_of(name):
    n = name.lower()
    return "gold" if "gold" in n else "crypto" if "bitcoin" in n else "etf" if n.startswith("ishares") else "stock"

def ensure(st):
    today = dt.date.today()
    st.setdefault("tax", {"year": today.year, "rate": RATE, "allowance": 1000.0, "base": 0.0, "paid": 0.0})
    t = st["tax"]
    if t["year"] != today.year:  # neues Jahr: Freibetrag und Topf zuruecksetzen
        t.update({"year": today.year, "base": 0.0, "paid": 0.0})
    for p in st["positions"]:
        p.setdefault("cls", cls_of(p["name"]))
        if "since" not in p:
            ds = [x["date"] for x in st["trades"] if x["name"] == p["name"] and x["side"] == "Kauf"]
            p["since"] = min(ds) if ds else st["start_date"]

def factor(p, today):
    """Anteil des Ertrags, der steuerpflichtig ist (Teilfreistellung, Haltefrist)."""
    c = p.get("cls", "stock")
    if c == "etf":
        return 0.7  # 30 % Teilfreistellung bei Aktienfonds
    if c in ("gold", "crypto"):
        return 0.0 if (today - dt.date.fromisoformat(p["since"])).days > 365 else 1.0
    return 1.0

def tax_on(st, taxable):
    """Bucht Steuer auf steuerpflichtigen Betrag (Gewinn +, Verlust -). Rueckgabe: gezahlte (+) bzw. erstattete (-) Steuer."""
    t = st["tax"]
    t["base"] = round(t["base"] + taxable, 2)
    due = max(0.0, t["base"] - t["allowance"]) * t["rate"]
    delta = round(due - t["paid"], 2)
    t["paid"] = round(due, 2)
    st["cash"] = round(st["cash"] - delta, 2)
    return delta

def spread(cls):
    return 0.005 if cls == "crypto" else 0.0
