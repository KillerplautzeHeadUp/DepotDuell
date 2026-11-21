# Übergabe: Depot-Duell (Claude gegen Nutzer)

Stand: 21.11.2026 (Depotstand 20.11. 22:38 Uhr, Nutzer 263.000 € laut Nutzer) (bei jedem Check-in aktualisieren)

Dieses Dokument ersetzt das Gedächtnis eines alten Chats. Ein neuer Chat liest es per Link und kennt danach Regeln, Technik und Entscheidungen.

## Adressen

- Repository: https://github.com/killerplautzeheadup/DepotDuell
- Seite (öffentlich): https://killerplautzeheadup.github.io/DepotDuell/
- Live-Daten der Seite, wird alle 30 Minuten aktualisiert und ist meist frischer als der Raw-Link: https://killerplautzeheadup.github.io/DepotDuell/data.json
- Zustand (kann eine alte Kopie sein): https://raw.githubusercontent.com/killerplautzeheadup/DepotDuell/main/data/state.json
- Diese Übergabe: https://raw.githubusercontent.com/killerplautzeheadup/DepotDuell/main/UEBERGABE.md

Alle Nutzerdaten (Index, Depotwert, Einzahlungen) stehen in der data.json der Seite (Felder "user" und "user_meta", zuletzt geprüft am 21.11.). Die Raw-Links zu user.json und user_meta.json nicht verwenden, sie liefern oft eine alte Kopie.

## Ablauf eines Check-ins (für Claude)

1. Übergabe lesen und den "Stand" oben prüfen.
2. Aktuellen Stand holen: zuerst die data.json der Seite abrufen und das Feld "updated" prüfen. Der Abruf kann eine zwischengespeicherte Kopie liefern (am 10.11. abends kam eine Kopie von morgens). Ist "updated" älter als ein Tag oder erkennbar älter als die Läufe, den Nutzer um einen Screenshot der Tabelle "Positionen" bitten oder um den eingefügten Inhalt von state.json. Nicht raten, nicht mit alten Zahlen arbeiten.
3. Alle Positionen mit den letzten Kursen der Handelsplätze von Trade Republic vergleichen (Websuche), Stop-Loss und Cash-Quote prüfen.
4. Depotwert und neue Einzahlungen des Nutzers erfragen. In der data.json stehen "user" (Datum, Index, Depotwert, Einzahlungssumme je Meldung) und "user_meta" (Einzahlungssumme, Sparrate, letzte gezählte Rate). Fehlen die Felder oder ist die Kopie alt, den Nutzer direkt fragen.
5. Eigene Entscheidungen treffen und begründen. Order-Zeilen mit exakten Namen aus der Positionsliste liefern. Danach diese Übergabe aktualisieren (Stand, Positionen, Entscheidungen).
6. Wenn kein Zugriff auf aktuelle Daten besteht: dem Nutzer offen sagen, was fehlt, und danach fragen.

## Regeln des Nutzers

- Reine Simulation. Start 23.10.2026, Startkapital 279.700 €. Backup-Reserve 30.000 €: nur bei außergewöhnlicher Chance, dann Nachricht an den Nutzer. Höchstens 90 Aktien, kein Totalverlust, Kosten wie Trade Republic (1 € je Order).
- Claude entscheidet Käufe, Verkäufe, Stop-Loss, Gewichte, Sparplan-Anteil und Cash allein. Hinweise des Nutzers sind nur ein Anlass. Gekauft wird nur, wenn Claude die Aktie auch ohne den Hinweis gekauft hätte. Jeder Trade bekommt den Vermerk "eigene Recherche" oder "durch Nutzerthema angestoßen".
- Kursregel: Bei jedem Gespräch alle Positionen mit den letzten Kursen der Handelsplätze von Trade Republic (gettex, Lang & Schwarz, Tradegate, Stuttgart, Xetra) vergleichen. Nicht auf fehlende Schlusskurse verweisen. Quelle und Zeitpunkt nennen, Schätzungen kennzeichnen.
- Sparrate: 365 € pro Woche für beide. Claude: freitags, 50 % davon automatisch in Kern-ETFs (Welt 60 %, Schwellenländer 20 %, Japan 20 %), Rest Cash. Nutzer: montags, das Skript zählt sie automatisch als Einzahlung.
- Steuern (Näherung): 26,375 %, ohne Kirchensteuer, Freibetrag 1.000 €, 30 % Teilfreistellung bei Aktien-ETFs, Gold und Bitcoin nach einem Jahr steuerfrei.
- Vergleich: Rendite in Prozent seit Start, bereinigt um Einzahlungen (Nutzer-Zuschuss 1.076,50 € für PepsiCo, 610,80 € aus seiner Reserve für Booking, 501 € am 10.11. und 1.251 € am 19.11. für ASML, Sparpläne). Die ASML-Käufe des Nutzers werden dem Nutzer als Einzahlung gezählt (Meldung per Telegram, "EINZAHLUNG").
- Stil: Deutsch, kurz, handytauglich, ehrlich. Keine erfundenen Zahlen, Annahmen kennzeichnen, Fehler offen nennen.
- Interessenkonflikt: Claude ist von Anthropic. Anthropic-Aktie (IPO, Kürzel ANT) wird im Duell nicht von Claude gekauft.

## Grenzen von Claude

- Handelt nur, wenn der Nutzer schreibt. Kein Hintergrund-Agent. Kein Zugriff auf das echte Trade-Republic-Depot. Schreibzugriff auf GitHub nur über Issues des Nutzers. Der Nutzer kann Dateien im Repository nicht selbst bearbeiten, Änderungen kommen als komplette neue Datei, die er ersetzt.
- Der Lesezugriff auf raw.githubusercontent.com liefert oft eine alte Kopie, auch mit ?v=Zahl. Auch die Seiten-Adresse kann zwischengespeichert sein. Verlässlich sind: den Inhalt von data/state.json vom Nutzer einfügen lassen, ein Screenshot der Seite, oder die GitHub-Pages-Adresse der data.json mit geprüftem Zeitstempel "updated".
- Die Websuche liefert oft keine aktuellen Einzelkurse (Aktien, ETFs). Dann Skript-Kurse (Yahoo) verwenden und offen sagen, dass sie nicht gegengeprüft sind. Verlässlich per Suche sind meist Ölpreis, Gold, Bitcoin und Indexstände.

## Technik

- Repository killerplautzeheadup/DepotDuell (öffentlich), Seite per GitHub Pages (Ordner docs). Skript scripts/update.py (Hilfsfunktionen in scripts/common.py, Order-Verarbeitung in scripts/apply_orders.py).
- Workflows in .github/workflows:
  - update.yml "Depot aktualisieren": alle 30 Minuten, Montag bis Freitag, 6 bis 21 Uhr UTC (etwa 7 bis 22 Uhr deutscher Zeit), außerdem von Hand startbar. Ruft update.py auf und speichert mit git add -A.
  - Orders-Workflow "Orders buchen": startet bei neuem Issue mit Titel "Order" vom Repository-Besitzer, bucht die Orders, ruft update.py auf, speichert data und docs, antwortet im Issue und schließt es.
  - Beide Workflows teilen die Gruppe "depot" und laufen nie gleichzeitig. Geplante Läufe starten bei GitHub oft verspätet.
- Das Skript liefert: Kurse von Yahoo Finance, Stop-Loss, bedingte Aufträge, Dividenden, Steuern, Kern-Sparplan mit Autopilot, Telegram-Auswertung, Wochenbericht freitags ab 19 Uhr per Telegram.
- Wahrheit: data/state.json. Verlauf: data/history.json, Nutzer-Index: data/user.json, Einzahlungen des Nutzers: data/user_meta.json. Telegram-Position: data/tg_offset.json. Tagesverlauf: data/intraday.json. Veröffentlicht wird docs/data.json.
- Telegram: Montag bis Freitag im update-Lauf, am Wochenende im eigenen Workflow telegram.yml (scripts/tg_only.py, ohne Kursabruf). Eine DEPOT-Meldung bekommt das Datum der Nachricht.
- Dateien (14.11.): docs/checkin.json (kompakter Stand, klein, bevorzugt abrufen statt der großen data.json), scripts/tg_only.py, .github/workflows/telegram.yml.
- Zweite Kursquelle (seit 15.11.): Lang & Schwarz (ls-tc.de, inoffizielle Website-Schnittstelle, Kurse in EUR) für alle Titel mit ISIN (Feld "isin" je Position; die Tabelle ISINS in update.py ist nur die Startbelegung für die ersten Titel), Twelve Data (Schlüssel als GitHub-Secret TWELVE_DATA_KEY, kostenlose Stufe) nur für Bitcoin. Yahoo bleibt Hauptquelle. Fehlt ein Yahoo-Kurs, nimmt das Skript die Zweitquelle. Bei mehr als 3 % Abweichung kommt eine Telegram-Warnung (KURSABWEICHUNG, einmal pro Tag und Titel). Die L&S-Kennungen stehen in data/ls_ids.json. Twelve Data liefert in der kostenlosen Stufe nur US-Titel und Krypto, für Europa kam HTTP 404.
- Probelauf 15.11. (Workflow "Kursquellen pruefen", scripts/ls_probe.py): Yahoo und L&S lagen bei den Europa-Titeln innerhalb von etwa 1 % (ASML am weitesten, +0,9 %). US-Titel passten nach Umrechnung mit dem Dollarkurs (etwa 1,105) auf etwa 0,3 %. Twelve Data und Yahoo lagen bei US-Titeln und Bitcoin auf Cent genau.
- Telegram-Befehle: CHECKIN (Bot schickt den kompakten Stand), PRIVAT AN/AUS (Depotwert und Einzahlungen aus Seite und docs-Dateien ausblenden, Rohdateien in data/ bleiben bei öffentlichem Repository sichtbar), MITLAUFEND;Name;Anteil (Stop vom Hoch), FEST;Name;Anteil (Stop vom Kaufkurs). Der Name wird ohne Beachtung der Schreibweise gesucht.
- Stop mitlaufend: Position bekommt "trail" und "high" in state.json. Warnung per Telegram, wenn ein Kurs 4 Läufe fehlt (Kursausfall).
- Stop-Loss: Standard ist ein fester Abstand vom Kaufkurs. Optional mitlaufend vom höchsten Kurs seit Aktivierung (Telegram-Befehl MITLAUFEND). Die Seite zeigt Stop-Kurs und Puffer je Position.
- Orders per Issue mit Titel "Order", eine Zeile je Befehl:
  - `KAUF;Name;Ticker;Währung;Stück;Kurs;Stop;Hinweis;NEU oder leer;ISIN` (Claude trägt bei jedem Kauf die ISIN in die Zeile ein, geprüft per Suche; ohne ISIN gibt es keine Zweitquelle für den Titel)
  - `VERKAUF;Name;Stück;Kurs;Hinweis`
  - `EINZAHLUNG;Betrag;Hinweis`
  - `STOP;Name;Anteil` (fest vom Kaufkurs)
  - `MITLAUFEND;Name;Anteil` (vom Hoch seit Aktivierung), `FEST;Name;Anteil`
  - `TICKER;Name;Kürzel`
  - `USER;Datum;Index`
  - `LIMITKAUF;Name;Ticker;Währung;Grenze;Stück;GültigBis;Stop;Hinweis;ISIN`
  - `LIMITVERKAUF;Name;Grenze;Stück;GültigBis;Hinweis`
  - `LOESCHEN;Name`
  - `INFO;Name;Region;Branche`
  - `ZUSAMMENFUEHREN;Alter Name;Ziel-Name`
  - `KERN;PAUSE`, `KERN;AN`, `KERN;ANTEIL;0,3`, `KERN;AUTO;AN` oder `AUS`
- Namensschutz (apply_orders.py, 14.11.): Unbekannte Namen bei VERKAUF, STOP, TICKER, INFO, LIMITVERKAUF und ZUSAMMENFUEHREN werden mit Vorschlag abgelehnt. Ein KAUF mit neuem Namen, aber gleichem Ticker oder sehr ähnlichem Namen wie eine vorhandene Position wird abgelehnt, außer die Zeile endet auf `;NEU`.
- Wichtig: Der Name muss exakt wie in der Positionsliste stehen (zum Beispiel "iShares Core MSCI World"), sonst entsteht eine zweite Position. Dann hilft ZUSAMMENFUEHREN.
- Telegram-Bot: "DEPOT 280650", "DEPOT 281500 EINZAHLUNG 610,80", "SPARPLAN 365" oder "SPARPLAN AUS".
- Autopilot: Kern-Anteil 80 % bei Welt-ETF über 10 % unter Jahreshoch, 70 % bei Cash über 25 %, 30 % bei Cash unter 10 %. Tagesverlust über 7 % pausiert den Sparplan.

## Entscheidungen bisher

- Start 23.10.: Welt-ETF, EM-ETF, Xetra-Gold, ASML, Eli Lilly, TotalEnergies. Danach JPMorgan, TSMC, Siemens (eigene Recherche), Bitcoin klein (4 %, Stop −35 %, Krypto bewusst auf eine Position begrenzt), Alphabet am 29.10. nach Kurssturz (durch Nutzerthema angestoßen, mäßige Überzeugung, 2 %), Japan-ETF am 30.10.
- Indien wurde am 30.10. ausgelassen (Ölpreis über 110 $, wahrscheinlich bezogen auf Dated Brent). Kein Nachkauf bei Alphabet. Chip-Werte nicht in den Abverkauf gekauft.
- 9.11.: Alibaba und Xiaomi geprüft. Kein Kauf. Xiaomi nein (Gewinnrückgang, hohe Schwankung). Alibaba (ADR, Kürzel BABA, nicht die Hongkong-Aktie) erst nach den Zahlen am 24.11. nach eigenen Kriterien prüfen.
- 9.11.: Doppelbuchung "Welt-ETF" (falscher Name) per VERKAUF;Welt-ETF;47;126,86 korrigiert. Lehre: Namen in Orders exakt aus der Positionsliste kopieren.
- 10.11.: Check-in, keine Trades. Cash mit 9,8 % an der Untergrenze, US-Inflationsdaten standen an. Skript erweitert (user_meta und Depotwert in data.json).
- 10. bis 12.11. auf Anfrage des Nutzers geprüft, kein Kauf: ASML und TSMC nicht nachkaufen (stark korrelierte AI-Wette, zusammen 12,9 %), GE Vernova (Watchlist, hängt am selben AI-Strom-Thema, Bewertung hoch, Kurs schwankt 4 bis 9 % pro Tag), Anthropic-IPO (Interessenkonflikt, nicht kaufen).
- 13.11.: Check-in, keine Käufe. Kern-Sparplan automatisch: 109,50 € (30 % der Wochenrate wegen Cash unter 10 %) in iShares Core MSCI Japan IMI, 1,5266 Stück zu 71,73 €. Indien trotz Ölpreis unter 100 $ nicht gekauft (Sensex etwa 12 % im Monat gestiegen, Zuflüsse ausländischer Anleger über 8 Mrd $, Inflation in Indien 6,09 %, Ölpreis wieder steigend, kein geprüfter ETF-Kurs).
- Eli Lilly: Stop wurde danach auf mitlaufend 12 % vom Hoch umgestellt (Stand 20.11.: Stop-Kurs 1.171,01, Puffer 4,7 %). Vorschlag "fest 5 %" vom 13.11. ist damit erledigt.
- Korrektur 13.11.: Die Angabe "Brent-Hoch 118 $ am 30.10." war falsch. Das Jahreshoch von 118,35 $ war am 31.3.2026. Im November lag Brent bisher zwischen 91 und 105 $.
- 20.11.: Kern-Sparplan automatisch, 2,6248 Stück Japan-ETF zu 69,53 € (Basis-Anteil 50 %).
- 21.11.: Check-in nach dem Ausverkauf vom 20.11. Keine Käufe, keine Verkäufe, Stops unverändert (eigene Recherche). Gründe: Cash 10,7 % knapp über der Untergrenze, Treiber des Ausverkaufs (Zinsangst, KI-Zweifel, SEC-Prüfung bei Nvidia) nicht gedreht, kein fallendes Messer fangen. Backup-Reserve unangetastet, keine außergewöhnliche Chance. TSMC-Stop wird nicht gesenkt. Anthropic-IPO (Handelsbeginn 19.11.) nicht gekauft, Interessenkonflikt.
- Nutzer: ASML-Kauf über 1.251 € am 19.11. per Telegram als Einzahlung gemeldet, in der Summe 5.600,30 € enthalten.

## Stand am 20.11.2026 (data.json, updated 20.11.2026 22:38 Uhr)

- Depotwert 262.617,87 €, Cash 27.991,38 € (10,7 %).
- Seit Start (bereinigt um Einzahlungen): Claude −6,95 % (Index 93,05), Vergleichsindex Welt-ETF −5,31 % (94,69), Nutzer etwa −7,97 % (Index etwa 92,03, Depotwert 263.000 € laut Nutzer, Einzahlungen 5.600,30 €; letzter Eintrag in data.json: 19.11., 272.500 €, Index 95,42).
- Verlauf Claude-Index: 15.11. 100,43, 16.11. 99,41, 17.11. 97,62, 18.11. 96,99, 19.11. 96,48, 20.11. 93,05.
- Risiko laut Skript: maximaler Rückgang Claude −8,86 %, Vergleichsindex −6,84 %, Volatilität 20,6 %, Beta 0,97.
- Kern-Sparplan: Basis-Anteil 50 %, wirksam 50 % (Regel "Basis").
- Einzahlungen des Nutzers bis 19.11.: 5.600,30 €. Letzte automatisch gezählte Montagsrate: 16.11. Nächste am 23.11.

Positionen (Stück, Kaufkurs, Skript-Kurs 20.11. 22:38, Veränderung seit Kauf, Gewicht):

| Position | Stück | Kauf | Kurs | Veränderung | Gewicht |
|---|---|---|---|---|---|
| iShares Core MSCI World | 550 | 129,36 | 122,71 | −5,1 % | 25,7 % |
| iShares Core MSCI EM IMI | 615 | 45,40 | 40,96 | −9,8 % | 9,6 % |
| Xetra-Gold | 205 | 116,37 | 103,78 | −10,8 % | 8,1 % |
| ASML | 19 | 1.393,20 | 1.168,00 | −16,2 % | 8,5 % |
| Eli Lilly | 19 | 1.143,57 | 1.228,56 | +7,4 % | 8,9 % |
| TotalEnergies | 280 | 81,54 | 78,19 | −4,1 % | 8,3 % |
| JPMorgan Chase | 40 | 295,95 | 283,20 | −4,3 % | 4,3 % |
| TSMC | 30 | 373,54 | 290,66 | −22,2 % | 3,3 % |
| Siemens | 45 | 256,80 | 254,65 | −0,8 % | 4,4 % |
| Bitcoin | 0,15 | 71.923,82 | 53.668,42 | −25,4 % | 3,1 % |
| Alphabet (Klasse A) | 22 | 262,70 | 241,94 | −7,9 % | 2,0 % |
| iShares Core MSCI Japan IMI | 124,7615 | 72,87 | 67,03 | −8,0 % | 3,2 % |

Stops: ASML fest 25 % (Stop-Kurs 1.044,90, Puffer 10,5 %), Eli Lilly mitlaufend 12 % (Stop-Kurs 1.171,01, Puffer 4,7 %), TotalEnergies fest 20 % (Puffer 16,6 %), JPMorgan fest 20 % (Puffer 16,4 %), TSMC fest 25 % (Stop-Kurs 280,16, **Puffer 3,6 %**), Siemens fest 20 % (Puffer 19,3 %), Bitcoin fest 35 % (Stop-Kurs 46.750,48, Puffer 12,9 %), Alphabet fest 25 % (Puffer 18,6 %). ETFs und Gold ohne Stop.

Marktlage 20.11. (Quellen: dpa-AFX/ARIVA, finanzen.net, goldesel.de; Einzelkurse der Positionen nicht unabhängig geprüft): Ausverkauf an der Wall Street. Nasdaq 100 −5,61 % auf 25.028,98, S&P 500 −3,70 % auf 6.910,39, Dow Jones −1,93 % auf 48.147,33. Nvidia etwa −14 % nach Bericht über SEC-Prüfung der Bilanzierung. Nasdaq Composite über 16 % unter dem Hoch vom 6.10., Jahresgewinn aufgebraucht. Treiber: Inflations- und Zinsängste (Fed, mögliche weitere Zinserhöhungen), Zweifel am KI-Investitionsboom, Nahost-Konflikt (USA, Israel, Iran). Anthropic-IPO (Handelsbeginn 19.11.) ohne Rückenwind. Gold und Bitcoin gaben laut Skript-Kursen ebenfalls deutlich nach (Xetra-Gold −8 %, Bitcoin −14 % seit 13.11.).

## Offen

- Montag 23.11.: Folgen des Ausverkaufs prüfen, vor allem TSMC-Stop (Puffer 3,6 %), Eli-Lilly-Stop (4,7 %), Bitcoin am Wochenende. Cash-Quote beachten (Untergrenze 10 %; bei Cash unter 10 % wirkt der Sparplan nur mit 30 %).
- Backup-Reserve 30.000 €: weiter unberührt. Einsatz nur bei außergewöhnlicher Chance, dann Nachricht an den Nutzer.
- Alibaba nach den Zahlen am 24.11. prüfen (ADR BABA, eigene Kriterien).
- Indien weiter beobachten, nächster Blick am 27.11.: Rücksetzer im Sensex, Ölpreis unter 100 $ stabil, Inflationsdaten Indien. Dann mit frischem Live-Kurs den iShares MSCI India UCITS ETF (ISIN IE00BZCQB185) mit etwa 2 % prüfen, Cash-Quote beachten.
- Anthropic-IPO: Kein Kauf durch Claude.
- Depotwert und Einzahlungen des Nutzers abfragen (zuletzt Stand 20.11., 263.000 €, Einzahlungen 5.600,30 €).
- Zweitquelle beobachten (Hinweise und KURSABWEICHUNG-Meldungen), nach einigen Wochen prüfen, ob L&S als Hauptquelle taugt.
- Optional später: echter KI-Agent über die API (grob 0,50 bis 10 $ pro Monat), vorerst kostenlose Variante.
