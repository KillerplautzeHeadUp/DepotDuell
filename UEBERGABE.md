# Übergabe: Depot-Duell (nur veränderliche Teile)

Stand: 28.11.2026 (Daten vom 27.11. 22:45 Uhr, Wochenende: Schlusskurse vom Freitag). Bei jedem Check-in aktualisieren.

Regeln, Technik, Befehle und Ablauf stehen in DUELL_REGELN.md (Projektdatei). Kriterien und Einträge der Watchlist stehen in WATCHLIST.md im Repository. Bei Widerspruch gilt diese Übergabe. Live-Daten: https://killerplautzeheadup.github.io/DepotDuell/data.json (Zeitstempel "updated" prüfen).

## Stand am 27.11.2026

- Depotwert 271.287,67 €, Cash 28.173,88 € (10,4 %). Backup-Reserve 30.000 € unberührt.
- Seit Start (bereinigt um Einzahlungen): Claude −4,01 % (Index 95,99), Welt-ETF −1,84 % (98,16), Nutzer −2,53 % (Index 97,47, Depotwert 278.600 € laut Nutzer am 28.11., Einzahlungen 5.965,30 €; letzter Eintrag in data.json: 25.11., 273.000 €, 95,47).
- Verlauf Claude-Index: 20.11. 93,05, 23.11. 96,64, 24.11. 94,83, 25.11. 92,96, 26.11. 94,79, 27.11. 95,99.
- Risiko laut Skript: maximaler Rückgang Claude −8,95 %, Welt-ETF −7,19 %, Volatilität 24,7 %, Beta 0,99.
- Kern-Sparplan: Basis-Anteil 50 %, wirksam 50 %. Am 27.11. 2,6468 Stück Japan-ETF zu 68,95 € (die Käufe gehen seit 13.11. jede Woche in den Japan-ETF, weil er am stärksten untergewichtet ist).
- Nächste Montagsrate des Nutzers am 30.11. (wird automatisch gezählt).
- Offene Aufträge laut data.json: keine.

Positionen (Stück, Kaufkurs, Skript-Kurs 27.11. 22:45 Yahoo, Veränderung seit Kauf, Gewicht):

| Position | Stück | Kauf | Kurs | Veränderung | Gewicht |
|---|---|---|---|---|---|
| iShares Core MSCI World | 550 | 129,36 | 127,20 | −1,7 % | 25,8 % |
| iShares Core MSCI EM IMI | 615 | 45,40 | 43,49 | −4,2 % | 9,9 % |
| Xetra-Gold | 205 | 116,37 | 106,72 | −8,3 % | 8,1 % |
| ASML | 19 | 1.393,20 | 1.198,00 | −14,0 % | 8,4 % |
| Eli Lilly | 19 | 1.143,57 | 1.273,33 | +11,4 % | 8,9 % |
| TotalEnergies | 280 | 81,54 | 78,56 | −3,7 % | 8,1 % |
| JPMorgan Chase | 40 | 295,95 | 295,35 | −0,2 % | 4,4 % |
| TSMC | 30 | 373,54 | 323,13 | −13,5 % | 3,6 % |
| Siemens | 45 | 256,80 | 252,60 | −1,6 % | 4,2 % |
| Bitcoin | 0,15 | 71.923,82 | 54.673,29 | −24,0 % | 3,0 % |
| Alphabet (Klasse A) | 22 | 262,70 | 251,45 | −4,3 % | 2,0 % |
| iShares Core MSCI Japan IMI | 127,4083 | 72,78 | 70,38 | −3,3 % | 3,3 % |

Stops und Puffer bis zum Stop: ASML fest 25 % (1.044,90 €, 12,8 %), Eli Lilly mitlaufend 12 % (1.171,01 $, 8,0 %), TotalEnergies fest 20 % (65,23 €, 17,0 %), JPMorgan fest 20 % (236,76 $, 19,8 %), TSMC fest 25 % (280,16 $, 13,3 %), Siemens fest 20 % (205,44 €, 18,7 %), Bitcoin fest 35 % (46.750,48 €, 14,5 %), Alphabet fest 25 % (197,02 $, 21,6 %). ETFs und Gold ohne Stop. Kein Puffer unter 5 %, keine Warnungen im Skript.

Watchlist laut Skript (Kurs, Einstiegskurs): Microsoft 492,85 $ (Einstieg bis 490 $, 0,6 % darüber), Münchener Rück 585,40 € (bis 540 €, 8,4 % darüber), Nestlé 87,34 CHF (bis 78 CHF, 12,0 % darüber), Novo Nordisk B 280,60 DKK (bis 224 DKK, 25,3 % darüber, nicht vor Februar 2027), Nvidia 150,49 $ (kein Einstiegskurs).

Marktlage (Quellen: Portale, nicht unabhängig geprüft): Woche bis 27.11. kräftige Erholung nach dem Ausverkauf vom 20.11.: S&P 500 7.297,49 (+5,6 % seit 20.11.), Nasdaq Composite 24.129,50 (+6,7 %), Dow 50.774,94, VIX etwa 24. Der Nasdaq liegt im November noch 5,1 % im Minus. Belastend: heiße Inflationszahl, neue Zollvorschläge, Wetten auf weitere Fed-Zinserhöhungen. Nvidia: Huang seit 23.11. wieder CEO, Aktie etwa 30 % höher, SEC-Prüfung der Bilanzierung offen. Brent von etwa 89 $ (23.11.) auf über 97 $ (27.11.) wegen Angriffen in Westasien. Sensex 83.339 (−0,7 % in der Woche).

## Entscheidungen bisher

- Start 23.10.: Welt-ETF, EM-ETF, Xetra-Gold, ASML, Eli Lilly, TotalEnergies. Danach JPMorgan, TSMC, Siemens (eigene Recherche), Bitcoin klein (Stop −35 %, Krypto bewusst auf eine Position begrenzt), Alphabet am 29.10. (durch Nutzerthema angestoßen, mäßige Überzeugung, 2 %), Japan-ETF am 30.10.
- 9.11.: Doppelbuchung "Welt-ETF" durch falschen Namen korrigiert. Xiaomi geprüft und abgelehnt (Gewinnrückgang, hohe Schwankung).
- 10. bis 12.11. auf Anfrage geprüft, kein Kauf: ASML und TSMC nicht nachkaufen (stark korrelierte KI-Wette), GE Vernova (Watchlist, hohe Bewertung), Anthropic-IPO (Interessenkonflikt, kein Kauf durch Claude).
- Indien (30.10. und 13.11.) nicht gekauft: Sensex stark gestiegen, hohe Zuflüsse, Inflation 6,09 %, Ölpreis steigt wieder.
- Eli Lilly: Stop auf mitlaufend 12 % vom Hoch umgestellt.
- 21.11.: Nach dem Ausverkauf keine Käufe, keine Verkäufe, Stops unverändert, Backup-Reserve unberührt. Nvidia nicht gekauft (SEC-Prüfung offen, KI-Wette bereits 14 % im Depot).
- 23.11.: Recherche groß. Watchlist neu aufgebaut: Microsoft (Priorität 1), Münchener Rück (2), Nestlé (3), Novo Nordisk, Nvidia. Allianz und Roche geprüft und nicht aufgenommen (Bewertung).
- 28.11.: Check-in, keine Verkäufe, Stops unverändert, kein Anlass für die Backup-Reserve. Alibaba geprüft, nicht aufgenommen: Zahlen kamen schon am 19.11. (nicht am 24.11.). Umsatz +10 %, Cloud +53 %, aber Onlinehandel rückläufig, bereinigtes Ergebnis sinkt, hohe Investitionen belasten den freien Cashflow, dazu China-Risiko und neue US-Chipbeschränkungen (zweite KI-Wette). Neubewertung nur bei Margenwende. Microsoft: Limit-Kauf Tranche 1 vorbereitet (5 Stück, Grenze 450 € entspricht etwa 490 $, gültig bis 11.12.), siehe Offen.

## Offen

- Microsoft: Issue "Order" mit der LIMITKAUF-Zeile aus dem Check-in vom 28.11. anlegen, falls noch nicht geschehen. Bedingung Stabilisierung: der Nasdaq schloss 23., 24., 25. und 27.11. über dem Schlusstief vom 20.11. (22.617,73), der 26.11. war US-Feiertag. Der 30.11. ist der fünfte Handelstag. Tranche 2 nach der Zinsentscheidung der Fed im Dezember, Cash danach etwa 9,6 %.
- Montag 30.11.: Stabilisierung prüfen, Stops und Watchlist-Kurse ansehen.
- Indien: Ölpreis über 97 $ und steigend, kein Einstieg. Nächster Blick Mitte Dezember. Dann mit Live-Kurs den iShares MSCI India UCITS ETF (ISIN IE00BZCQB185) mit etwa 2 % prüfen, Cash-Quote beachten.
- GE Vernova: nicht auf der Skript-Watchlist, Daten alt (797 $ am 10.11.), bei der nächsten Recherche aktualisieren.
- Nutzer: Depotwert per Telegram melden ("DEPOT 278600"), falls noch nicht geschehen.
- Technik für die nächste Änderungsrunde: Das Alter der L&S-Kurse wird mit etwa −55 Minuten angezeigt (L&S nennt deutsche Ortszeit, das Skript rechnet mit UTC), die 30-Minuten-Grenze der Abweichungsprüfung wirkt deshalb nicht wie gedacht. In DUELL_REGELN.md die Zeile ergänzen, dass bei jeder Recherche zuerst data.json abgerufen wird.
- Anthropic-Aktie (ANT): kein Kauf durch Claude.
- Optional später: echter KI-Agent über die API (grob 0,50 bis 10 $ pro Monat).
