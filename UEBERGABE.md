# Übergabe: Depot-Duell (Claude gegen Nutzer)

Stand: 13.11.2026, abends (bei jedem Check-in aktualisieren)

Dieses Dokument ersetzt das Gedächtnis eines alten Chats. Ein neuer Chat liest es per Link und kennt danach Regeln, Technik und Entscheidungen.

## Adressen

- Repository: https://github.com/killerplautzeheadup/DepotDuell
- Seite (öffentlich): https://killerplautzeheadup.github.io/DepotDuell/
- Live-Daten der Seite, wird alle 30 Minuten aktualisiert und ist meist frischer als der Raw-Link: https://killerplautzeheadup.github.io/DepotDuell/data.json
- Zustand (kann eine alte Kopie sein): https://raw.githubusercontent.com/killerplautzeheadup/DepotDuell/main/data/state.json
- Diese Übergabe: https://raw.githubusercontent.com/killerplautzeheadup/DepotDuell/main/UEBERGABE.md

Alle Nutzerdaten (Index, Depotwert, Einzahlungen) stehen in der data.json der Seite (Felder "user" und "user_meta", geprüft am 13.11.). Die Raw-Links zu user.json und user_meta.json nicht verwenden, sie liefern oft eine alte Kopie.

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
- Vergleich: Rendite in Prozent seit Start, bereinigt um Einzahlungen (Nutzer-Zuschuss 1.076,50 € für PepsiCo, 610,80 € aus seiner Reserve für Booking, 501 € am 10.11. für ASML, Sparpläne).
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
- Telegram wird nur bei den Läufen Montag bis Freitag ausgewertet. Meldungen vom Wochenende erscheinen erst am Montag mit dem Datum von Montag.
- Stop-Loss: Der Stop ist ein fester Abstand vom Kaufkurs (Kurs fällt auf Kaufkurs mal 1 minus Anteil), er läuft nicht mit. Bei Gewinnern schützt er deshalb den Gewinn nicht, solange er nicht angehoben wird.
- Orders per Issue mit Titel "Order", eine Zeile je Befehl:
  - `KAUF;Name;Ticker;Währung;Stück;Kurs;Stop;Hinweis`
  - `VERKAUF;Name;Stück;Kurs;Hinweis`
  - `EINZAHLUNG;Betrag;Hinweis`
  - `STOP;Name;Anteil`
  - `TICKER;Name;Kürzel`
  - `USER;Datum;Index`
  - `LIMITKAUF;Name;Ticker;Währung;Grenze;Stück;GültigBis;Stop;Hinweis`
  - `LIMITVERKAUF;Name;Grenze;Stück;GültigBis;Hinweis`
  - `LOESCHEN;Name`
  - `INFO;Name;Region;Branche`
  - `ZUSAMMENFUEHREN;Alter Name;Ziel-Name`
  - `KERN;PAUSE`, `KERN;AN`, `KERN;ANTEIL;0,3`, `KERN;AUTO;AN` oder `AUS`
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
- 13.11.: Check-in, keine Käufe. Kern-Sparplan automatisch: 109,50 € (30 % der Wochenrate wegen Cash unter 10 %) in iShares Core MSCI Japan IMI, 1,5266 Stück zu 71,73 €. Indien trotz Ölpreis unter 100 $ nicht gekauft (Sensex etwa 12 % im Monat gestiegen, Zuflüsse ausländischer Anleger über 8 Mrd $, Inflation in Indien 6,09 %, Ölpreis wieder steigend, kein geprüfter ETF-Kurs). Vorschlag: Stop bei Eli Lilly von 22 % auf 5 % unter Kaufkurs anheben (Gewinn von etwa 14 % schützen), siehe Offen.
- Korrektur 13.11.: Die Angabe "Brent-Hoch 118 $ am 30.10." war falsch. Das Jahreshoch von 118,35 $ war am 31.3.2026. Im November lag Brent bisher zwischen 91 und 105 $.

## Stand am 13.11.2026 (data.json, updated 13.11.2026 17:42 Uhr)

- Depotwert 283.210,81 €, Cash 27.808,88 € (9,8 %).
- Seit Start (bereinigt um Einzahlungen): Claude +0,48 % (Index 100,48), Welt-ETF +0,61 %, Nutzer +1,12 % (Index 101,12 am 11.11., Depotwert 286.120 €, Einzahlungen 3.283,30 €).
- Risiko laut Skript: maximaler Rückgang Claude −3,98 %, Vergleichsindex −3,35 %.
- Kern-Sparplan: Basis-Anteil 50 %, wirksam 30 % (Regel "Cash-Quote unter 10 %").
- Einzahlungen des Nutzers bis 11.11.: 3.283,30 € (Start 1.441,50 €, Montagsraten 2. und 9.11., 610,80 € Booking, 501 € für ASML am 10.11.). Nächste Montagsrate am 16.11. wird automatisch gezählt.

Positionen (Stück, Kaufkurs, Skript-Kurs 13.11. 17:42, Gewicht):

| Position | Stück | Kauf | Kurs | Veränderung | Gewicht |
|---|---|---|---|---|---|
| iShares Core MSCI World | 550 | 129,36 | 130,38 | +0,8 % | 25,3 % |
| iShares Core MSCI EM IMI | 615 | 45,40 | 44,94 | −1,0 % | 9,8 % |
| Xetra-Gold | 205 | 116,37 | 113,13 | −2,8 % | 8,2 % |
| ASML | 19 | 1.393,20 | 1.337,40 | −4,0 % | 9,0 % |
| Eli Lilly | 19 | 1.143,57 | 1.305,46 | +14,2 % | 8,8 % |
| TotalEnergies | 280 | 81,54 | 82,06 | +0,6 % | 8,1 % |
| JPMorgan Chase | 40 | 295,95 | 312,25 | +5,5 % | 4,4 % |
| TSMC | 30 | 373,54 | 356,82 | −4,5 % | 3,8 % |
| Siemens | 45 | 256,80 | 278,95 | +8,6 % | 4,4 % |
| Bitcoin | 0,15 | 71.923,82 | 62.277,99 | −13,4 % | 3,3 % |
| Alphabet (Klasse A) | 22 | 262,70 | 266,23 | +1,3 % | 2,1 % |
| iShares Core MSCI Japan IMI | 122,1367 | 72,94 | 71,46 | −2,0 % | 3,1 % |

Stops (fester Abstand vom Kaufkurs): ASML 25 %, Eli Lilly 22 %, TotalEnergies 20 %, JPMorgan 20 %, TSMC 25 %, Siemens 20 %, Bitcoin 35 %, Alphabet 25 %. ETFs und Gold ohne Stop. Keine Position ist nahe am Stop.

Marktlage 13.11.: Brent etwa 96 $ (Wochenverlust, aber wieder steigend, weil Trump ein Abkommen mit dem Iran offenlässt). Gold etwa 3.890 $ je Unze (passt zu Xetra-Gold 113,13 €). Bitcoin etwa 69.000 bis 70.000 $ (etwa 63.000 €, Skript 62.278 € um 17:42). DAX Schluss 26.739 Punkte. US-Techwerte mit neuen Verkaufswellen, Halbleiter und KI schwanken stark. Fed: Zinserhöhung im Dezember wird eingepreist, die Erzeugerpreise waren leicht unter Erwartung. Einzelkurse der Aktien nicht unabhängig geprüft.

## Offen

- Eli Lilly: Stop auf 5 % anheben, falls der Nutzer zustimmt: Issue "Order" mit der Zeile `STOP;Eli Lilly;0,05`. Danach ist die Wirkung in data.json zu prüfen (Stop-Feld bei Lilly).
- Indien weiter beobachten, nächster Blick am 27.11.: Rücksetzer im Sensex, Ölpreis unter 100 $ stabil, Inflationsdaten Indien. Dann mit frischem Live-Kurs den iShares MSCI India UCITS ETF (ISIN IE00BZCQB185) mit etwa 2 % prüfen, Cash-Quote beachten (Untergrenze 10 %).
- Alibaba nach den Zahlen am 24.11. prüfen.
- Anthropic-IPO: Preisfestlegung 18.11., Handelsbeginn 19.11. (Nasdaq, Kürzel ANT). Kein Kauf durch Claude.
- Depotwert und Einzahlungen des Nutzers abfragen (zuletzt Stand 11.11.).
- Zweiter Kursanbieter als Ersatz für Yahoo. Feedback zum neuen Graphen.
- Optional später: echter KI-Agent über die API (grob 0,50 bis 10 $ pro Monat), vorerst kostenlose Variante.
