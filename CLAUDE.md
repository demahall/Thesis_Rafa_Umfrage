# CLAUDE.md – Projekt Rafa (Thesis-Auswertung)

Stand: 2026-11-20 (Planung abgeschlossen, bereit für Preprocessing-Skript). Quelle: `Project_rafa_raw_instruction.md` (Rafas Rohanweisung, Indonesisch/Deutsch gemischt), Rückfrage-Antworten von Rafa vom 19.11., Prüfung der Dateien.
Arbeitssprache mit dem User: Deutsch. Code und Variablennamen: Englisch/original.

## 1. Ziel
Auswertung und Datenvisualisierung einer Umfrage für Rafas Thesis ("cadstraining-study", SoSci-Survey-Export).
Kern der Studie: **Vorher/Nachher-Vergleich** (t1 vs. t2) von Acceptance, Mental Model und Trust, nachdem die Teilnehmer Informationsmaterial (Manual = Text, oder Video) zu einem automatisierten Fahrsystem (Level 3) bekommen haben.

Status: **Preprocessing fertig** (`preprocessing.py` → `output/data_clean.csv`, N = 30). **Deskriptive Auswertung fertig** (`analysis.py` → `output/results_descriptive.csv` + `output/plots/`). Eingabe ist jetzt `raw_data_rafa.csv` (42 Fälle, Stand 20.11.).

## 2. Dateien
| Datei | Inhalt |
|---|---|
| `raw_data_rafa.csv` | **Eingabedaten** (aktueller Survey-Export, 42 Fälle × 144 Spalten; ersetzt `data_rafa.csv`) |
| `preprocessing.py` | Preprocessing-Skript, Start: `python3 preprocessing.py` (Python 3.9, pandas) |
| `analysis.py` | Deskriptive Auswertung (M, SD, Min, Max), Start: `python3 analysis.py` (pandas, matplotlib) |
| `visualization.py` | Nur Visualisierung (Rafas Aufgabe 1: MM-Spaghetti-Plot pro Gruppe), Start: `python3 visualization.py` |
| `output/` | `data_clean.csv`, `sample_table.csv`, `preprocessing_log.txt`, `results_descriptive.csv`, `plots/` |
| `variables_cadstraining-study_2026-11-17_10-34.csv` | Variablenliste: Label, Typ, Fragetext pro Spalte |
| `values_cadstraining-study_2026-11-17_10-37.csv` | Wertelabels (Code → Bedeutung) |
| `Archive/` | Original-Exporte (Rohdaten csv/xlsx vom 17.11., Codebook xlsx). Nicht verändern. |
| `Project_rafa_raw_instruction.md` | Rafas Rohanweisung (Original, nur Ergänzungen anhängen) |

**Technisch:** Alle CSVs sind **UTF-16 LE, tab-getrennt, CRLF**. Einlesen z. B. mit `pd.read_csv(path, encoding="utf-16", sep="\t")`. Fehlend = `-9` ("Not answered") bzw. leer.
Original-Daten nie überschreiben. Bereinigte Daten als neue Datei ausgeben.

## 3. Variablen
Namenskonvention: `<Konstrukt><Occasion>_<Item>`, z. B. `MM01_02` = Mental Model, **01 = before (t1)**, **02 = after (t2)**, Item 02.
Konstrukte: **AC** Acceptance, **MM** Mental Model, **TR** Trust.

### Nicht benötigt
SERIAL, REF, QUESTNNR, MODE (und technische Spalten wie MAILSENT, Q_VIEWER, MISSING, MISSREL, TIME_RSI, TIME001–004).

### Verwendet
- `CASE`: eindeutige ID.
- `STARTED`: Startzeit. Aktuell nicht wichtig, kann später relevant werden.
- `STATUS`: `complete` = vollständig (Filter, siehe 4).
- `TIME_SUM`: Gesamtdauer. `TIME005`–`TIME009`: Zeit auf Seite 5–9 (wichtig).
- `RG01`: Zufallszuteilung des Materials (1–8, siehe 5). `RG01_CP` laut Label "complete clearances of the ballot" (Bedeutung unklar, nicht von Rafa erwähnt).
- **Demografie:** `Alter` (Kategorien 1–7: 1 = 18–25, 2 = 26–35, 3 = 36–45, 4 = 46–55, 5 = 56–65, 6 = 66–75, 7 = 76+), `Gender` (1 w, 2 m, 3 divers), `Fuehrerscheinbesitz` (**1 = hat Führerschein**, 2 = hat keinen), `Fuehrerschein` (Jahre Besitz, offen), `Fahrleistung` (1 = 0–5.000 km bis 5 = >20.000 km pro Jahr).
- **FAS-Nutzungshäufigkeit** (1 = never … 5 = always): `FAS_TWW` (Totwinkelassistent), `FAS_Spurwarner`, `FAS_Tempomat`, `FAS_Spurhalte`, `FAS_ACC`. FAS = Fahrerassistenzsystem.
- **`Erfahrung`** (L3-Erfahrung): 1 = Drive Pilot (Mercedes EQS), 2 = Personal Pilot (BMW 7er), 3 = keine. **Teilnehmer mit Erfahrung (1 oder 2) markieren** (nicht ausfiltern).
- **Wissensquellen `DD15`:** `DD15_01`–`DD15_08` sind Checkboxen (1 = nicht angekreuzt, 2 = angekreuzt). `DD15` selbst = **Anzahl der angekreuzten Quellen**, oder `-1` bei "keine/Sonstige". Die Frage-ID 15 ist unwichtig (es gibt nur DD15). Geprüft: `DD15` stimmt in den Daten mit der Anzahl der `2`en überein.
- Metadaten `FINISHED`, `LASTPAGE`, `MAXPAGE`: nur Kontrolle.

### Skalen der Messitems
| Konstrukt | Items | Skala |
|---|---|---|
| AC (t1 `AC01_*`, t2 `AC02_*`) | 01–09 | 1–5, bipolar (Gegensatzpaare, z. B. Useful/Useless). Polung je Item verschieden, siehe 6.1 |
| MM (`MM01_*`, `MM02_*`) | 01–27 | 1–6, "strongly disagree" … "strongly agree" |
| TR (`TR01_*`, `TR02_*`) | 01–12 | 1–7, "not at all" … "extremely" |

## 4. Preprocessing (Reihenfolge)
1. **Nur komplette Fälle:** `STATUS == "complete"`. Alle anderen raus.
2. Bei kompletten Fällen zusätzlich:
   - **Alter ≥ 18.** Prüfen. Die Kategorien beginnen bei 18–25, deshalb greift der Filter praktisch nicht. Trotzdem im Skript explizit prüfen und protokollieren.
   - **Führerschein vorhanden:** `Fuehrerscheinbesitz == 1`. Wer 2 hat, wird gefiltert.
3. **Mental Model umkodieren:** nur **`MMxx_06`** wird umgekehrt (für t1 und t2: `MM01_06`, `MM02_06`). Umkehr auf der 1–6-Skala: `7 − x`. **Alle anderen MM-Items bleiben unangetastet.** (von Rafa bestätigt, siehe 7.1.)
4. **AC umkodieren** (−2…+2, Items 01,02,04,05,07,09 gespiegelt, 03,06,08 nur verschoben), siehe 6.1. TR: keine Umkodierung, Skalenbildung siehe 6.2.

## 5. Gruppen (`RG01`) und Auswertungslogik
`RG01` Codes: 1 = Manual Group 1, 2 = Video Group 1, 3 = Manual Group 2, 4 = Video Group 2, 5 = Manual Group 3, 6 = Video Group 3, 7 = Manual Group 4, 8 = Video Group 4.
Ungerade Codes = **Manual (Text)**, gerade Codes = **Video**.

**Ergebnis:** pro Gruppe Vergleich vorher vs. nachher (`xx01` gegen `xx02`) für AC, MM, TR.
Rafa: "Gruppe 1 = Antwort 1 und 2, Gruppe 2 = Antwort 3 und 4, usw."

**Inhalt der Gruppen (Rafa, 20.11.):** Group 1–4 = unterschiedliche **CADS-Level** (ob das Auto automatisiert bzw. teilautomatisiert fährt). Pro Level gibt es zwei Instruktionen: **Manual (Text)** und **Video**.

**Auswertungsebenen (Rafa, 20.11., "wahrscheinlich"):** (1) **Gruppe (CADS-Level)**, (2) **Material (Manual vs. Video)**, (3) **Before-After (t1 vs. t2)**. Details zur Kombination: siehe 6.4. Ableitung als Spalten `group` = 1–4 (aus Code 1+2, 3+4, 5+6, 7+8) und `medium` = manual/video, ohne etwas zu verwerfen. Alle drei Varianten werden ausgegeben (siehe 6.4):
- **A:** 4 Gruppen, Manual und Video zusammengefasst (Code 1+2, 3+4, 5+6, 7+8).
- **B:** Innerhalb jeder Gruppe Manual vs. Video vergleichen.
- **C:** Über alle Gruppen hinweg Manual (ungerade) vs. Video (gerade).

## 6. Konstrukte (Antwort von Rafa, 19.11.)
### 6.1 Acceptance (AC): zwei Komponenten
- **Usefulness:** `AC_01, 03, 05, 07, 09`
- **Satisfaction:** `AC_02, 04, 06, 08`
- Die Zahlenbedeutung der Skala ist je Item unterschiedlich (Pole links/rechts wechseln, z. B. 01 Useful=1/Useless=5, aber 03 Bad=1/Good=5), die Rohzahlen sind also nicht direkt vergleichbar.
- **Preprocessing (Stand 20.11., Vorgabe vom User, bestätigt 20.11.):** Skala **1–5 → −2 bis +2**, so dass bei **allen** Items **+2 = positive Bewertung** und −2 = negative Bewertung ist.
  - Items **`AC_01, 02, 04, 05, 07, 09`** (links positiv): **gespiegelt**, `score = 3 − x` (1 → +2, 2 → +1, 3 → 0, 4 → −1, 5 → −2).
  - Items **`AC_03, 06, 08`** (rechts positiv): **nicht gespiegelt**, nur verschoben, `score = x − 3` (1 → −2, 5 → +2).
  - Gilt für t1 (`AC01_*`) und t2 (`AC02_*`).
  - **Bestätigt (20.11.):** 03, 06, 08 werden nicht gespiegelt.
- **Auswertung AC (Vorgabe vom User, 20.11.):**
  1. Pro Teilnehmer **zwei Subskalen-Scores**: **Usefulness** = Mittelwert aus `AC_01, 03, 05, 07, 09`, **Satisfaction** = Mittelwert aus `AC_02, 04, 06, 08` (nach der Umkodierung).
  2. Beides jeweils für **before (`AC01_`)** und **after (`AC02_`)** berechnen.
  3. **Über alle Teilnehmer mitteln**, also Usefulness before/after und Satisfaction before/after, jeweils Durchschnitt aller Personen.
  - Aufschlüsselung nach Gruppe/Material: siehe 6.4 (alle Varianten).

### 6.2 Trust (TR): zwei Komponenten, getrennt auswerten
- **Distrust:** `TR_01` bis `TR_05`. **Je höher der Wert, desto weniger Vertrauen.** Nicht umkehren, nur so interpretieren.
- **Trust:** `TR_06` bis `TR_12`. Logik normal (höher = mehr Vertrauen).
- Distrust und Trust **nicht zu einem Gesamtscore mischen.**
- `TR_12` ("I am familiar with the system"): wird **in Trust mitgerechnet**. **Rafas Bestätigung steht noch aus** (Stand 20.11.). Falls Rafa anders entscheidet, nur die Item-Liste der Trust-Subskala ändern.
- Statistik pro Auswertung: **Mittelwert (M), Standardabweichung (SD), Minimum, Maximum**, über die drei Auswertungsebenen aus 6.4.

### 6.3 Mental Model (MM): drei Kategorien (Rafa, 20.11.)
Die Survey-Items sind schon korrekt gepolt (nur `MM_06` wird im Preprocessing umgekehrt, siehe 4.3).
- **Functions:** `MM_11, 12, 14, 16, 17, 18, 19, 20, 23` (9 Items)
- **Limitations:** `MM_06, 09, 10, 13, 15, 21, 22, 24` (8 Items)
- **Operations:** `MM_25, 26, 27` (3 Items)
- **In keiner Kategorie:** `MM_01, 02, 03, 04, 05, 07, 08` (7 Items). **Entscheidung (20.11.): komplett nicht in die Auswertung aufnehmen** (weder Item-, Kategorie- noch Gesamtebene). Die Spalten bleiben in den Rohdaten bzw. `data_clean.csv` erhalten. Gesamt-MM = die 20 zugeordneten Items.

Drei Berechnungsebenen (jeweils für t1 `MM01_*` und t2 `MM02_*`):
1. **Pro Item** (nur die 20 zugeordneten): M, SD, Min, Max über die Teilnehmer.
2. **Pro Kategorie:** Durchschnitt der Item-Mittelwerte, Durchschnitt der Item-SDs, sowie **Min = kleinster Einzelwert, Max = größter Einzelwert** über alle Items der Kategorie (Min der Item-Minima, Max der Item-Maxima, Rohwerte). Stichproben-SD (n−1).
3. **Gesamt-MM:** M, SD, Min, Max über die 20 zugeordneten Items (gleiche Logik wie Kategorie).

### 6.4 Auswertungsebenen für AC, MM, TR (Stand 20.11., Rafa "wahrscheinlich")
Alle drei Konstrukte werden über **Gruppe (CADS-Level) × Material (Manual/Video) × Before/After** ausgewertet. **Entscheidung (20.11.): alle Varianten ausgeben:** gesamt, pro Gruppe, pro Material, pro Gruppe × Material, jeweils before/after. Rafa wählt später aus, was in die Thesis kommt (Zellen bei Gruppe × Material nur n ≈ 2–3).

**Ebenen für AC und TR (Entscheidung 20.11.):** wie bei MM jeweils **M, SD, Min, Max** auf Item-Ebene und Subskalen-Ebene (AC: Usefulness/Satisfaction, TR: Distrust/Trust). **Kein Gesamtscore** über beide Subskalen. Bei AC gelten Item-Werte nach der Umkodierung (−2…+2). Die frühere Vorgabe (Person-Mittel, dann Mittel über alle Teilnehmer, 6.1) bleibt als Subskalen-Mittel enthalten.

Ableitung: Gruppe aus `RG01` (1+2 → 1, 3+4 → 2, 5+6 → 3, 7+8 → 4), Material = ungerade Manual, gerade Video.

## 7. Offene Punkte / Pending
1. **MM-Reversal: GEKLÄRT (Rafa, 20.11.):** nur `MM_06` wird umgekehrt. Die anderen als "(reversed)" markierten Items (`09, 10, 13, 15, 21, 22, 24, 27`) hat das Survey-Tool schon umgepolt, **nicht** nochmal umkehren.
2. **AC-Scoring −2…+2:** erledigt, bestätigt (6.1).
3. **Gruppierung der Auswertung:** wahrscheinlich Gruppe (CADS-Level) × Material × Before/After, siehe 5 und 6.4. Kombination entschieden (7.10).
4. **Statistik:** **deskriptiv + Plots**, Kennzahlen M, SD, Min, Max (MM zusätzlich auf Item-, Kategorie-, Gesamtebene). Keine Signifikanztests, bis Rafa etwas anderes sagt.
5. `STARTED`, Zeitvariablen `TIME005–009`, `TIME_SUM`: Verwendungszweck offen ("Auswertung noch nicht überlegt"). Beibehalten und in der Auswertung bereitstellen.
6. `RG01_CP`: **nicht wichtig, unberührt lassen** (Entscheidung 20.11.).
7. Rafa-Notiz zu Wissensquellen: `DD15` = Anzahl der Kreuze, `-1` bei "keine" (bestätigt in den Daten).
8. **MM-Items ohne Kategorie:** geklärt, nicht in der Auswertung (6.3).
9. **Kategorie-Min/Max und SD:** geklärt (Rohwerte, Stichproben-SD n−1), siehe 6.3.
10. **Kombination Gruppe × Material × Before/After:** geklärt, alle Varianten (6.4).
11. **`TR_12` in Trust:** umgesetzt, **wartet auf Rafas Bestätigung**.
12. **Rückbestätigung bei Rafa (nicht blockierend):** Ausschluss der MM-Items `01–05, 07, 08`; AC/TR ohne Gesamtscore; Stichproben-SD (n−1).

## 7a. Entscheidungen "Grill-Me"-Runden (20.11.)
- **Complete-Filter:** nur `STATUS == "complete"`. `FINISHED` nur als Gegencheck protokollieren.
- **Missings:** `-9`/leer in **Messitems (AC, MM, TR)** = Umfrage nicht fertig → **Fall ausschließen** (und im Log nennen). `-9`/leer in **allen anderen Variablen** (Demografie, FAS, DD15 usw.) → **kein Ausschluss**, Wert als fehlend (NaN) behandeln.
- **Zeit-Qualitätsfilter:** keiner (von Rafa bestätigt, 20.11.). `TIME_SUM`, `TIME005–009` werden nur berichtet (kein Speeder-Ausschluss, bis Rafa einen Grenzwert nennt).
- **Technik:** Python (pandas), Ausgabe als **UTF-8 CSV** (Komma) plus Log-Datei der Filterschritte. Rohdaten unverändert.
- **MM-Auswertung:** definiert, siehe 6.3.
- **TR-Auswertung:** definiert, siehe 6.2 und 6.4.
- **L3-Erfahrung:** neue Flag-Spalte `l3_experience` (1 bei `Erfahrung` ∈ {1, 2}, sonst 0). Diese Personen **zählen in der Hauptauswertung mit** (N=22), ein Sensitivitätscheck ohne sie ist möglich.
- **Stichprobentabelle:** Das Preprocessing erzeugt zusätzlich eine deskriptive Tabelle nach dem Filter (N, Alter, Gender, Fahrleistung, FAS-Nutzung, DD15, `TIME_SUM`, `TIME005–009`), gesamt und pro `RG01`-Code.
- **Ausgabe:** Skript `preprocessing.py` im Projektordner, Ergebnisse in **`output/`** (`data_clean.csv`, `sample_table.csv`, `preprocessing_log.txt`, `ac_scores.csv`). Die Original-CSV wird nie verändert, umkodierte Werte stehen **nur in der neuen CSV** (`data_clean.csv`). Innerhalb von `data_clean.csv` bleiben die Rohspalten erhalten und die abgeleiteten Spalten kommen als neue Spalten dazu (z. B. `MM01_06_rev`, `AC01_01_s`, `AC_useful_t1`, `group`, `medium`, `l3_experience`). **Entschieden (20.11.):** Rohspalten und umkodierte Spalten gemeinsam in der neuen CSV.
- **Umfang des Skripts:** Preprocessing, danach Auswertung von AC, MM und TR (Definitionen siehe 6.1–6.4). Der Skriptumfang (Preprocessing in `preprocessing.py`, Auswertung getrennt in z. B. `analysis.py`) wird beim Schreiben festgelegt.
- **Validierungs-Checks (Plausibilitätsprüfungen im Log):** **alle vier aktiv** (Ergebnis im Log, kein stilles Korrigieren): (1) Wertebereiche AC 1–5, MM 1–6, TR 1–7, FAS 1–5, Alter 1–7, Gender 1–3; (2) `DD15` = Anzahl der Kreuze in `DD15_01–08`, sonst −1; (3) bei `Fuehrerscheinbesitz = 1` muss `Fuehrerschein` > 0 sein; (4) AC/MM/TR je t1 und t2 vollständig, `RG01` in 1–8.

## 8. Checks (vor der Auswertung durchführen und berichten)
- [x] Wie viele Personen bestehen den Preprocessing-Teil "complete" (Status, Alter, Führerschein)?
- [x] Ist der Mental-Model-Preprocessing-Schritt (Umkehr `MM_06`) abgeschlossen und geprüft?
- [x] N pro `RG01`-Code und pro Gruppe/Medium nach dem Filter.

### Ergebnis Preprocessing mit `raw_data_rafa.csv` (20.11., reproduzierbar per Skript)
- 42 Fälle → 32 `complete` (entfernt CASE 72, 73, 80, 110, 115, 141, 151, 157, 167, 169) → **30** nach Führerschein-Filter (raus CASE 83, 148) → **30** nach Messitem-Check (keine fehlenden Items). Alter-Filter ändert nichts. `FINISHED` identisch mit `STATUS`.
- N pro `RG01`: 1: 4, 2: 4, 3: 3, 4: 4, 5: 4, 6: 4, 7: 2, 8: 5. Pro Gruppe: 1: 8, 2: 7, 3: 8, 4: 7. Manual 13, Video 17.
- L3-Erfahrung: CASE 144, 145. Alle vier Plausibilitätsprüfungen bestanden. `MM_06` umgekehrt (Kontrolle x + rev = 7).
- `data_clean.csv`: 30 Zeilen, 175 Spalten (144 Rohspalten + abgeleitete: `MM01_06_rev`, `MM02_06_rev`, 18 × `AC0t_ii_s`, `ac_useful/ac_satisf/tr_distrust/tr_trust` je `_t1`/`_t2`, `group`, `medium`, `l3_experience`).
- `sample_table.csv` nicht Teil der Pflicht (Rafa wollte nur `data_clean.csv`), aber miterzeugt.

### Ergebnis Auswertung (`analysis.py`, 20.11.)
- `results_descriptive.csv` (855 Zeilen): Spalten `slice_type, slice, n, construct, level, name, method, M/SD/Min/Max_t1, M/SD/Min/Max_t2, delta_M`. Schnitte: gesamt, pro Gruppe, pro Material, pro Gruppe × Material.
- Ebenen: Item (AC 9, MM 20 zugeordnete, TR 12), Subskala/Kategorie, MM gesamt (20 Items). Subskalen in **zwei Methoden** (Spalte `method`): `item_aggregate` = MM-Logik (Mittel der Item-M und Item-SD, Min der Item-Minima, Max der Item-Maxima) und `person_score` = Personen-Mittel, dann M/SD/Min/Max über Teilnehmer. Welche in die Thesis kommt, entscheidet Rafa.
- SD = Stichproben-SD (n−1). AC auf −2…+2, `MM_06` als `_rev`.
- Plots: nicht mehr in `analysis.py`. Alte Balkenplots (`*_before_after`, `*_items`) wurden am 22.11. gelöscht. Plots kommen ausschließlich aus `visualization.py`.
- Gesamt (N = 30), Personen-Mittel t1 → t2: AC usefulness 0,83 → 0,77, satisfaction 0,70 → 0,74; TR distrust 3,63 → 3,57, trust 4,44 → 4,77; MM functions 4,24 → 4,37, limitations 3,35 → 3,75, operations 3,91 → 4,14. Manuell gegengerechnet (MM functions t1).
- Zellen Gruppe × Material haben n = 2–5, Kennzahlen dort nur grob zu lesen.

### Vorab-Prüfung der alten Datei `data_rafa.csv` (19.11., überholt)
- 32 Fälle gesamt, **24 `complete`** (8 Abbrecher: CASE 72, 73, 80, 110, 115, 141, 151, 157).
- Von den 24: **22 mit Führerschein** (raus: CASE 83 und 148, beide kein Führerschein). Alter-Filter ändert nichts.
- **N = 22 nach Filter.** Verteilung RG01: Code 1: 3, 2: 3, 3: 2, 4: 3, 5: 3, 6: 3, 7: 2, 8: 3. Das heißt **2–3 Personen pro Zelle**, nur deskriptiv sinnvoll.
- L3-Erfahrung: 2 Personen mit Drive Pilot, 20 ohne.
- Diese Zahlen sind nur eine Vorabschau, die Checks in Abschnitt 8 müssen mit Code reproduzierbar laufen.

## 9. Arbeitsweise
- Erst Preprocessing + Checks, danach Auswertung/Visualisierung.
- Jeder Umkodierungsschritt wird dokumentiert (welche Items, welche Formel, wie viele Fälle betroffen).
- Rohdaten bleiben unverändert, Ergebnisse als neue Dateien.
- Bei Widersprüchen zwischen Rafas Notizen und Codebook: nicht raten, hier unter 7 festhalten und Rafa fragen.

## 10. Verlauf
- 2026-11-17: Survey-Exporte (Daten, Variablen, Values, Codebook) erzeugt.
- 2026-11-19: Rohanweisung gelesen, Daten geprüft, Widersprüche gefunden. Entscheidungen: nur `MM_06` umkehren, Gruppenlogik A/B/C offenhalten, Statistik nur deskriptiv + Plots. Rafa-Antworten zu AC/TR eingearbeitet. Dieses CLAUDE.md erstellt.
- 2026-11-20: AC-Scoring definiert (Items 01,02,04,05,07,09 gespiegelt, 03,06,08 verschoben, Ergebnis −2…+2) und AC-Auswertung festgelegt (Usefulness/Satisfaction je Person, before/after, Mittel über alle Teilnehmer).
- 2026-11-20 (Grill-Me, Runden 1–2): Filter, Missing-Regeln, Zeitvariablen, Tooling, L3-Flag, Stichprobentabelle entschieden. (Danach durch Rafas Antworten ergänzt, siehe vorherige Zeile.)
- 2026-11-20 (Rafa-Antworten): MM_06 allein umkehren (Rest vom Tool gepolt), MM-Kategorien und Berechnungsebenen definiert, TR_12 vorerst in Trust, Gruppe = CADS-Level, kein Zeitfilter.
- 2026-11-20 (Grill-Me Runde 3): MM-Items ohne Kategorie ausgeschlossen, Kategorie-Min/Max = Rohwerte, AC/TR auf Item- und Subskalen-Ebene, alle Gruppen-/Material-Varianten ausgeben.
- 2026-11-20 (Abschluss): `TR_12` in Trust übernommen, wartet auf Rafas Bestätigung. Planung abgeschlossen, nächster Schritt: `preprocessing.py`.
- 2026-11-20 (Preprocessing): `raw_data_rafa.csv` (42 Fälle) eingelesen, `preprocessing.py` geschrieben und ausgeführt → `output/data_clean.csv` (N = 30). Nächster Schritt: Auswertung (Abschnitt 6).
- 2026-11-20 (Auswertung): `analysis.py` geschrieben und ausgeführt → `output/results_descriptive.csv` und Plots. Offen: Rafas Bestätigung (TR_12, MM-Ausschluss, Methode `item_aggregate` vs. `person_score`).
- 2026-11-22 (Visualisierung, Aufgabe 1): `visualization.py` → `output/plots/mm_spaghetti_group1–4.png`. Spaghetti-/Paired-Slope-Plot, 2×2 (Functions, Limitations, Operations, Total), eine Linie pro Person (Personen-Mittel über die Items der Kategorie, Total = 20 Items), X: t1 (pre)/t2 (post), Y: 1–6, Manual blau/Punkt/durchgezogen, Video rot/Quadrat/gestrichelt, Legende oben rechts, Grid an, Titel „Mental Model Scores for group N“. Visualisierung bleibt in eigenem Skript. Annahme: „Mental“ = Manual.
- Verlauf-Zusatz 2026-11-21/22: Repo https://github.com/demahall/Thesis_Rafa_Umfrage (öffentlich, ohne Rohdaten; `.gitignore`: `raw_data_rafa.csv`, `output/data_clean.csv`, `Archive/`). `output/Auswertung_MM.csv` (MM-Items pro Gruppe 1–4, vorher/nachher) erzeugt von `analysis.py`.
- 2026-11-22 (Visualisierung, Aufgabe 2): `visualization.py` erweitert um Trust/Distrust (2×1, Trust = TR_06–12 links, Distrust = TR_01–05 rechts, Y 1–7, Titel „Trust and Distrust Group N“) → `output/plots/tr_spaghetti_group1–4.png`. Plot-Code aus `analysis.py` entfernt, alte Balkenplots gelöscht.
- 2026-11-22 (Visualisierung, Aufgabe 3): `visualization.py` erweitert um Acceptance (2×1, Usefulness links, Satisfaction rechts, Y −2…+2, Titel „Acceptance Scores for Group N“) → `output/plots/ac_spaghetti_group1–4.png`. Darstellung wie bei MM/TR.
