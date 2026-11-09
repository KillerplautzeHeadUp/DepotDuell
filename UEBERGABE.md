# Übergabe: Depot-Duell (Claude gegen Nutzer)

Dieses Dokument ersetzt das Gedächtnis eines alten Chats. Ein neuer Chat liest es per Link und kennt danach Regeln, Technik und Entscheidungen.

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
- Beim Lesen von Dateien den Link mit ?v=Zahl am Ende verwenden, sonst kann eine alte Kopie erscheinen. Im Zweifel Screenshot der Seite verlangen.

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
- Alibaba und Xiaomi: Alibaba interessanter (Cloud, Rückkäufe), Xiaomi nach starkem Anstieg weniger Puffer. Noch keine Entscheidung, mit aktuellen Zahlen prüfen.

## Offen
- Check-in freitags (erste Wochenrate 6.11.): Cash von etwa 33.000 € einsetzen. Zweiter Kursanbieter als Ersatz für Yahoo. Feedback zum neuen Graphen. Optional später: echter KI-Agent über die API (grob 0,50 bis 10 $ pro Monat), vorerst kostenlose Variante.
