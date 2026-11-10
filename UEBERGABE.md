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
- Wenn kein Zugriff auf aktuelle Daten besteht: dem Nutzer offen sagen, was fehlt, und danach fragen.

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

## Technik
- Repository killerplautzeheadup/DepotDuell (öffentlich), Seite per GitHub Pages. Skript alle 30 Minuten an Börsentagen (Kurse von Yahoo Finance, Stop-Loss, bedingte Aufträge, Dividenden, Steuern, Kern-Sparplan mit Autopilot, Wochenbericht freitags abends per Telegram).
- Wahrheit: data/state.json. Verlauf: data/history.json, Nutzer-Index: data/user.json, Einzahlungen des Nutzers: data/user_meta.json.
- Orders per Issue mit Titel "Order", eine Zeile je Befehl: KAUF;Name;Ticker;Währung;Stück;Kurs;Stop;Hinweis | VERKAUF;Name;Stück;Kurs;Hinweis | EINZAHLUNG;Betrag;Hinweis | STOP;Name;Anteil | TICKER;Name;Kürzel | USER;Datum;Index | LIMITKAUF;Name;Ticker;Währung;Grenze;Stück;GültigBis;Stop;Hinweis | LIMITVERKAUF;Name;Grenze;Stück;GültigBis;Hinweis | LOESCHEN;Name | INFO;Name;Region;Branche | ZUSAMMENFUEHREN;Alter Name;Ziel-Name | KERN;PAUSE, KERN;AN, KERN;ANTEIL;0,3, KERN;AUTO;AN oder AUS.
- Wichtig: Der Name muss exakt wie in der Positionsliste stehen (zum Beispiel "iShares Core MSCI World"), sonst entsteht eine zweite Position. Dann hilft ZUSAMMENFUEHREN.
- Telegram-Bot: "DEPOT 280650", "DEPOT 281500 EINZAHLUNG 610,80", "SPARPLAN 365" oder "SPARPLAN AUS".
- Autopilot: Kern-Anteil 80 % bei Welt-ETF über 10 % unter Jahreshoch, 70 % bei Cash über 25 %, 30 % bei Cash unter 10 %. Tagesverlust über 7 % pausiert den Sparplan.

## Entscheidungen bisher
- Start 23.10.: Welt-ETF, EM-ETF, Xetra-Gold, ASML, Eli Lilly, TotalEnergies. Danach JPMorgan, TSMC, Siemens (eigene Recherche), Bitcoin klein (4 %, Stop −35 %, Krypto bewusst auf eine Position begrenzt), Alphabet am 29.10. nach Kurssturz (durch Nutzerthema angestoßen, mäßige Überzeugung, 2 %), Japan-ETF am 30.10.
- Indien vorerst ausgelassen (Ölpreis über 110 $). Kein Nachkauf bei Alphabet. Chip-Werte nicht in den Abverkauf gekauft.

## Stand am 9./10.11.2026
- Seit Start (bereinigt um Einzahlungen): Claude etwa −0,5 %, Nutzer −0,44 %, Welt-ETF etwa −0,9 %. Cash etwa 27.553 € (Quote knapp unter 10 %, der Autopilot setzt dann den Kern-Anteil am nächsten Freitag auf 30 %).
- Positionen (Stück, Kaufkurs): iShares Core MSCI World 550 (129,36), iShares Core MSCI EM IMI 615 (45,40), Xetra-Gold 205 (116,37), ASML 19 (1.393,20), Eli Lilly 19 (1.143,57), TotalEnergies 280 (81,54), JPMorgan Chase 40 (295,95), TSMC 30 (373,54), Siemens 45 (256,80), Bitcoin 0,15 (71.923,82), Alphabet (Klasse A) 22 (262,70), iShares Core MSCI Japan IMI 120,61 (72,95).
- Einzahlungen des Nutzers bis 9.11.: 2.782,30 € (inklusive 610,80 € aus seiner Reserve für Booking und seiner Montagsraten).
- 9.11.: Alibaba und Xiaomi geprüft. Kein Kauf. Xiaomi nein (Gewinnrückgang, hohe Schwankung). Alibaba (ADR, Kürzel BABA, nicht die Hongkong-Aktie) erst nach den Zahlen am 24.11. nach eigenen Kriterien prüfen.
- 9.11.: Doppelbuchung "Welt-ETF" (falscher Name) per VERKAUF;Welt-ETF;47;126,86 korrigiert. Lehre: Namen in Orders exakt aus der Positionsliste kopieren.

## Offen
- Check-in freitags (erste Wochenrate 6.11.): Cash von etwa 27.500 € gezielt einsetzen, Alibaba nach den Zahlen am 24.11. prüfen. Zweiter Kursanbieter als Ersatz für Yahoo. Feedback zum neuen Graphen. Optional später: echter KI-Agent über die API (grob 0,50 bis 10 $ pro Monat), vorerst kostenlose Variante.
