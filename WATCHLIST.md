# Watchlist von Claude (eigene Recherche)

Stand: 22.11.2026. Erste Runde, vom Nutzer im Chat angestoßen. Alle Kurse stammen aus Nachrichtenportalen (Schlusskurse 20.11.), nicht von den Handelsplätzen von Trade Republic. Vor jedem Kauf Live-Kurs prüfen. Keine Anlageberatung, Einstiegsbedingungen sind meine Annahmen für das Duell.

## Wie die Watchlist entsteht

- Recherche startet der Nutzer im Chat. "Recherche klein": nur die Einträge unten aktualisieren. "Recherche groß": zusätzlich 2 bis 3 neue Ideen prüfen.
- Kriterien für einen Eintrag: (1) Qualität: Marktstellung, Gewinne, Bilanz. (2) Bewertung gegenüber eigener Historie und Vergleichswerten. (3) Der Grund für den Kursrückgang ist verstanden und bewertbar, kein offenes Verfahren. (4) Passt zur Streuung im Depot, nicht nur eine weitere KI-Wette. (5) Es gibt einen Einstiegsplan in Tranchen mit Stop.
- Gekauft wird nur mit eigener Überzeugung und unter den Regeln des Duells (Cash-Untergrenze etwa 10 %, Backup-Reserve nur bei außergewöhnlicher Chance, ANT nicht).

## Marktlage

Am 20.11. fiel der Nasdaq stark, der Technologiesektor war der schwächste. Seit Oktober haben Basiskonsum, Gesundheit und Versorger etwa 13 % gewonnen, der Nasdaq 100 etwa 13 % verloren. Morgan Stanley spricht von der stärksten defensiven Rotation seit 25 Jahren. Defensive Sektoren sind damit teurer als Technologie, ein Einstieg dort ist kein Schnäppchen. Der VIX lag bei 28,4.

## Einträge

| Titel | Kurs | These | Risiken | Einstieg und Status |
|---|---|---|---|---|
| Microsoft (MSFT, ISIN US5949181045) | 484,52 $ (20.11.), etwa 13 % unter dem 52-Wochen-Hoch von 559,15 $ | Azure +48 %, Auftragsbestand 677 Mrd $ (+73 %), operative Marge nahe 50 %. Erwartetes KGV etwa 24 bis 25 (Folgejahr etwa 20) gegen etwa 33 im 5-Jahres-Schnitt. 53 von 58 Analysten raten zum Kauf, im Schnitt Ziel 636 $. | Dieselbe KI-Investitionswette wie ASML, TSMC und Alphabet. Anthropic greift mit Büro-Werkzeugen Office an (Interessenkonflikt von Claude beachten). EU prüft Azure. Analysten-Abstufung. | Priorität 1. Kursgrenze für Tranche 1: bis 490 $ (etwa 24,5-faches Folgejahres-KGV), zuletzt erreicht, die Bedingung Stabilisierung ist offen. Kein Kauf jetzt. Einstieg in Tranchen: erste Tranche etwa 1 % des Depots (etwa 2.600 €), wenn der Nasdaq Composite an 5 Handelstagen in Folge nicht unter das Tief vom 20.11. fällt. Zweite Tranche frühestens nach der Zinsentscheidung der Fed im Dezember. Stop fest 20 %. Nicht aus der Backup-Reserve. Cash danach etwa 9,7 %. |
| Novo Nordisk B (NOVO-B.CO, ISIN DK0062498333) | 35,18 € (Xetra, 20.11.) | KGV etwa 10, Dividendenrendite etwa 4,5 %, Aktie über 70 % unter dem Hoch. Prognose zum dritten Mal angehoben, Wegovy-Pille übertrifft Erwartungen. | Ab Januar 2027 Listenpreis von Wegovy in den USA etwa 50 % niedriger. Analysten erwarten 2027 kaum Gewinnwachstum, Mehrheit "Halten", Morgan Stanley untergewichtet. Abhängigkeit von Semaglutid, Druck durch Eli Lilly (im Depot). | Günstig, aber Wertfalle möglich. Einstiegskurs etwa 30 € (224 DKK), rund 15 % unter dem Kurs vom 20.11. Kein Kauf vor den nächsten Jahreszahlen (voraussichtlich Anfang Februar 2027, Termin prüfen). Dann prüfen, ob die Gewinne sich stabilisieren. |
| Nvidia (NVDA, ISIN US67066G1040) | 125,53 $ (20.11., −14 % an einem Tag), etwa 48 % unter dem Rekord | Quartalsumsatz 115,8 Mrd $ (+103 %). | SEC prüft die Bilanzierung, Untersuchung in Kalifornien zu China-Lieferungen, Führungswechsel, Regulierung von Chipexporten (Frist des Kongresses am 2.12.). Umfang der Prüfung unklar. | Nur beobachten, kein Einstiegskurs. Kein Kauf, solange die Reichweite der Prüfung offen ist. Neu bewerten, wenn die SEC oder Nvidia den Umfang klärt. |
| GE Vernova (GEV) | 797 $ (10.11., nicht aktuell) | Strom und Netz, Auftragsbestand etwa 200 Mrd $ (Stand 12.11.). | Gleiches KI-Strom-Thema, hohe Bewertung, Cashflow stark von Kundenanzahlungen abhängig. | Beobachten. Kurs und Lage vor Kauf neu prüfen. |
| Alibaba (BABA, ADR) | nicht geprüft | Prüfung nach den Quartalszahlen am 24.11. nach eigenen Kriterien. | China-Regulierung, Exportregeln. | Offen bis 24.11. |
| iShares MSCI India UCITS ETF (ISIN IE00BZCQB185) | nicht geprüft | Indien-Gewichtung steckt schon im EM-ETF, nur bei Rücksetzer eigener ETF. | Inflation 6,09 %, Ölpreis. | Blick am 27.11. |

## Ideen, noch nicht geprüft (aus Artikeln, keine Empfehlung)

Broadcom und Amazon (laut Artikel unter ihrer 5-Jahres-Bewertung), Pfizer (KGV etwa 10), Allianz und Hannover Rück (defensive Versicherer in Europa). Für jede Idee zuerst Qualität und Grund des Kursrückgangs prüfen. Bei Broadcom und Amazon wieder die KI-Korrelation beachten.

## Skript-Watchlist (state.json)

Dort stehen derzeit MSFT, NVDA und NOVO-B.CO. Das Skript meldet einen Tagesverlust ab 10 %. Mit dieser Liste stimmen die drei ersten Einträge überein. Ändern lässt sie sich erst mit den Befehlen WATCH und UNWATCH, die für die nächste Änderungsrunde vorgesehen sind.
