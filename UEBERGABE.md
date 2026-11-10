# Übergabe: Depot-Duell (Claude gegen Nutzer)

Stand: 10.11.2026 (bei jedem Check-in aktualisieren)

Dieses Dokument ersetzt das Gedächtnis eines alten Chats. Ein neuer Chat liest es per Link und kennt danach Regeln, Technik und Entscheidungen.

## Adressen

- Repository: https://github.com/killerplautzeheadup/DepotDuell
- Seite (öffentlich): https://killerplautzeheadup.github.io/DepotDuell/
- Live-Daten der Seite, wird alle 30 Minuten aktualisiert und ist meist frischer als der Raw-Link (beim ersten Mal den Zeitstempel "updated" prüfen): https://killerplautzeheadup.github.io/DepotDuell/data.json
- Zustand (kann eine alte Kopie sein): https://raw.githubusercontent.com/killerplautzeheadup/DepotDuell/main/data/state.json
- Diese Übergabe: https://raw.githubusercontent.com/killerplautzeheadup/DepotDuell/main/UEBERGABE.md

## Ablauf eines Check-ins (für Claude)

1. Übergabe lesen und den "Stand" oben prüfen.
2. Aktuellen Stand holen: zuerst die data.json der Seite abrufen. Liegt "updated" nicht länger als ein Tag zurück, verwenden. Sonst den Nutzer um einen Screenshot der Tabelle "Positionen" bitten oder um den eingefügten Inhalt von state.json. Nicht raten, nicht mit alten Zahlen arbeiten.
3. Alle Positionen mit den letzten Kursen der Handelsplätze von Trade Republic vergleichen (Websuche), Stop-Loss und Cash-Quote prüfen.
4. Depotwert und neue Einzahlungen des Nutzers erfragen (er meldet sie per Telegram, sein Index steht in data/user.json).
5. Eigene Entscheidungen treffen und begründen. Order-Zeilen mit exakten Namen aus der Positionsliste liefern. Danach diese Übergabe aktualisieren (Stand, Positionen, Entscheidungen).
6. Wenn kein Zugriff auf aktuelle Daten besteht: dem Nutzer offen sagen, was fehlt, und danach fragen.

## Regeln des Nutzers

- Reine Simulation. Start 23.10.2026, Startkapital 279.700 €. Backup-Reserve 30.000 €: nur bei außergewöhnlicher Chance, dann Nachricht an den Nutzer. Höchstens 90 Aktien, kein Totalverlust, Kosten wie Trade Republic (1 € je Order).
- Claude entscheidet Käufe, Verkäufe, Stop-Loss, Gewichte, Sparplan-Anteil und Cash allein. Hinweise des Nutzers sind nur ein Anlass. Gekauft wird nur, wenn Claude die Aktie auch ohne den Hinweis gekauft hätte. Jeder Trade bekommt den Vermerk "eigene Recherche" oder "durch Nutzerthema angestoßen".
- Kursregel: Bei jedem Gespräch alle Positionen mit den letzten Kursen der Handelsplätze von Trade Republic (gettex, Lang & Schwarz, Tradegate, Stuttgart, Xetra) vergleichen. Nicht auf fehlende Schlusskurse verweisen. Quelle und Zeitpunkt nennen, Schätzungen kennzeichnen.
- Sparrate: 365 € pro Woche für beide. Claude: freitags, 50 % davon automatisch in Kern-ETFs (Welt 60 %, Schwellenländer 20 %, Japan 20 %), Rest Cash. Nutzer: montags, das Skript zählt sie automatisch als Einzahlung.
- Steuern (Näherung): 26,375 %, ohne Kirchensteuer, Freibetrag 1.000 €, 30 % Teilfreistellung bei Aktien-ETFs, Gold und Bitcoin nach einem Jahr steuerfrei.
- Vergleich: Rendite in Prozent seit Start, bereinigt um Einzahlungen (Nutzer-Zuschuss 1.076,50 € für PepsiCo, 610,80 € aus seiner Reserve für Booking, Sparpläne).
- Stil: Deutsch, kurz, handytauglich, ehrlich. Keine erfundenen Zahlen, Annahmen kennzeichnen, Fehler offen nennen.

## Grenzen von Claude

- Handelt nur, wenn der Nutzer schreibt. Kein Hintergrund-Agent. Kein Zugriff auf das echte Trade-Republic-Depot. Schreibzugriff auf GitHub nur über Issues des Nutzers.
- Der Lesezugriff auf raw.githubusercontent.com liefert oft eine alte Kopie, auch mit ?v=Zahl (der Zusatz wird entfernt). Verlässlich sind: den Inhalt von data/state.json vom Nutzer einfügen lassen, ein Screenshot der Seite, oder die GitHub-Pages-Adresse der data.json (muss der Nutzer in die Nachricht schreiben). Vor jedem Check-in Stand und Zeitpunkt der gelesenen Daten prüfen.
- Die Websuche liefert oft keine aktuellen Einzelkurse (Aktien, ETFs). Dann Skript-Kurse (Yahoo) verwenden und offen sagen, dass sie nicht gegengeprüft sind. Verlässlich per Suche sind meist Ölpreis, Gold und Marktüberblick.

## Technik

- Repository killerplautzeheadup/DepotDuell (öffentlich), Seite per GitHub Pages. Skript alle 30 Minuten an Börsentagen (Kurse von Yahoo Finance, Stop-Loss, bedingte Aufträge, Dividenden, Steuern, Kern-Sparplan mit Autopilot, Wochenbericht freitags abends per Telegram).
- Wahrheit: data/state.json. Verlauf: data/history.json, Nutzer-Index: data/user.json, Einzahlungen des Nutzers: data/user_meta.json.
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
- Indien wurde am 30.10. ausgelassen (Ölpreis über 110 $). Kein Nachkauf bei Alphabet. Chip-Werte nicht in den Abverkauf gekauft.
- 9.11.: Alibaba und Xiaomi geprüft. Kein Kauf. Xiaomi nein (Gewinnrückgang, hohe Schwankung). Alibaba (ADR, Kürzel BABA, nicht die Hongkong-Aktie) erst nach den Zahlen am 24.11. nach eigenen Kriterien prüfen.
- 9.11.: Doppelbuchung "Welt-ETF" (falscher Name) per VERKAUF;Welt-ETF;47;126,86 korrigiert. Lehre: Namen in Orders exakt aus der Positionsliste kopieren.
- 10.11.: Check-in, keine Trades (eigene Recherche). Gründe: US-Inflationsdaten stehen heute an, Cash mit 9,8 % an der Untergrenze von 10 %. Indien wird Kandidat, weil die Ölpreis-Bedingung wegfällt (Brent etwa 92 $, Hoch 118 $ am 30.10., minus 22 %). TotalEnergies halten (Stop −20 % weit weg).

## Stand am 10.11.2026 (data.json, updated 10.11.2026 09:24 Uhr)

- Depotwert 280.597,63 €, Cash 27.553,38 € (9,8 %).
- Seit Start (bereinigt um Einzahlungen): Claude −0,32 %, Nutzer −0,44 % (Stand 9.11.), Welt-ETF −0,48 %.
- Risiko laut Skript: maximaler Rückgang Claude −3,98 %, Vergleichsindex −3,35 %.
- Kern-Sparplan: Anteil aktuell 50 % (Basis). Am Freitag setzt der Autopilot wegen Cash unter 10 % auf 30 %.
- Einzahlungen des Nutzers bis 9.11.: 2.782,30 € (inklusive 610,80 € aus seiner Reserve für Booking und seiner Montagsraten). Neue Einzahlungen und Depotwert des Nutzers seit 9.11. sind noch nicht gemeldet.

Positionen (Stück, Kaufkurs, Skript-Kurs 10.11. morgens, Gewicht):

| Position | Stück | Kauf | Kurs | Gewicht |
|---|---|---|---|---|
| iShares Core MSCI World | 550 | 129,36 | 128,97 | 25,3 % |
| iShares Core MSCI EM IMI | 615 | 45,40 | 44,65 | 9,8 % |
| Xetra-Gold | 205 | 116,37 | 117,76 | 8,6 % |
| ASML | 19 | 1.393,20 | 1.353,60 | 9,2 % |
| Eli Lilly | 19 | 1.143,57 | 1.255,93 | 8,5 % |
| TotalEnergies | 280 | 81,54 | 78,33 | 7,8 % |
| JPMorgan Chase | 40 | 295,95 | 304,28 | 4,3 % |
| TSMC | 30 | 373,54 | 345,68 | 3,7 % |
| Siemens | 45 | 256,80 | 275,10 | 4,4 % |
| Bitcoin | 0,15 | 71.923,82 | 66.414,65 | 3,6 % |
| Alphabet (Klasse A) | 22 | 262,70 | 256,31 | 2,0 % |
| iShares Core MSCI Japan IMI | 120,6101 | 72,95 | 70,26 | 3,0 % |

Stops (Anteil unter Hoch): ASML 25 %, Eli Lilly 22 %, TotalEnergies 20 %, JPMorgan 20 %, TSMC 25 %, Siemens 20 %, Bitcoin 35 %, Alphabet 25 %. ETFs und Gold ohne Stop. Keine Position ist nahe am Stop.

Marktlage 10.11.: Brent etwa 92 $ (Hoch 118 $ am 30.10.), Entspannung im US-Iran-Konflikt, aber die US-Seeblockade in der Straße von Hormus bleibt. Bitcoin laut finanzen.net etwa 67.600 € (ohne Zeitstempel, nur Richtwert).

## Offen

- Check-in freitags 13.11. (zweite Wochenrate nach dem 6.11.):
  - Indien prüfen: Wenn Brent bis dahin unter 100 $ bleibt, einen Indien-ETF mit etwa 2 % Gewicht erwägen, mit frischem Live-Kurs (Kandidat: iShares MSCI India UCITS ETF, ISIN IE00BZCQB185, aktueller Kurs noch nicht geprüft). Indien steckt schon im EM-ETF, das wäre eine Übergewichtung. Cash-Quote beachten (Untergrenze 10 %).
  - Cash von etwa 27.500 € nur gezielt einsetzen.
- Alibaba nach den Zahlen am 24.11. prüfen.
- Depotwert und Einzahlungen des Nutzers abfragen (zuletzt Stand 9.11.).
- Zweiter Kursanbieter als Ersatz für Yahoo. Feedback zum neuen Graphen.
- Optional später: echter KI-Agent über die API (grob 0,50 bis 10 $ pro Monat), vorerst kostenlose Variante.
