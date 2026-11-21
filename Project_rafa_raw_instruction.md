## Project Rafa: bantu auswertung buat thesisnya 
- Goal: Auswertung, Datenvisualisierung von einer Umfrage
- Input: csv File: data_rafa.csv (hasil Survey)
- Penjelasan setiap ID Frage (Spalten) di values_cadstraining-study_2026-11-17_10-37.csv
	- Case: Unique ID for input
	- Seriel ga butuh
	- Reference ga butuh
	- Questnnr ga butuh
	- Mode ga butuh
	- Started: Time Started kapan (ga terlalu penting tapi bisa jadi penting ntar, belom kepikiran auswertungnya)
	- Ausgewertete Variables
		- ID Frage Konvention: Variable+Occasion_Questionnumber. 
			- Beispiel: MM01_02: Mental Model before for second question 
			- AC: Acceptance
			- MM: Mental Model
			- TR: Trust
			- 01: Before
			- 02:After
	- Demographic:
		- Alter: (Note: Please check this diatas 18 tahun apa engga, dibawah 18 filter out)
		- Gender
		- Führerscheinbesitz (Note: Please check apakah yang ngisi questioner punya führerschein apa engga. 1 indicate punya, kalo ga punya filter out)
		- Führerschein
		- Fahrleistung
	- Lu seberapa seringkah makai system ini (gatau nama termnya) , contohnya system blind spot assist:
		- FAS_TWW. Wobei FAS: Fahrassistentssystem
		- FAS_Spurwarner
		- FAS_Tempomat
		- FAS_Spurhalte
		- FAS_ACC
	- Erfahrung: L3 (Note: Tandain yang udah punya experience)
		- If yes: 
			- Drive Pilot in Mercedez EQS
			- Personal Pilot in BMW 7 Series
		- No
	- Knowledge Source: (DD):
		- Example: DD15_01
		- 15 for frage ID (not so important, because it has only DD15)
		- 01 to 08: checkbox options
		- keine: others checkbox options with -1 OR (important) the number of checkbox selection (multiple select is possible, that means if someone check x boxes, DD15 will say x, if not is -1)
	- TIME_SUM: Berapa lama dia ngerjain interview nya
	- TIME005-TIME009 : Spent di page ke 5-9 (important).
	- RG01: Random Generator (yang di generate text atau video dan di grup mana)
		- ada 1-8: siehe variables_cadstraining-study_2026-11-17_10-34.csv
	- STATUS: complete ga dia ngisi umfragenya (Note: filter out yang ga complete)
- Penjelasan setiap ID jawaban di variables_cadstraining-study_2026-11-17_10-34.csv

### Preprocessing Step:
-  Complete (filter out yang engga)
	- if complete , then
		- Alter, Führerscheinbesitz (Alter über 18. Führerscheinbesitz sollte haben)
- Mental Model (MM) Question (Reversed Code, umgekehrt ausgewertet)
	- Für ID Frage:  Measurement Item : MMxx_06, MMxx_09 - MMxx_27 (ini bisa reversed bisa engga, only for context)
		- MMxx_06 itu musti di reversed
		- Selain itu Measurment Items  yang lain  gausah di sentuh2 lagi
        
### Check
- Berapa orang yang lolos Preprocessing Step Complete Part
- Check if preprocessing step for Mental model already completed
### Ergebnis: 
- Per grup (siehe RG01 ) Beispiel Grup 1, dann Antwort 1 und 2, Grup 2, dann Antwort 3 und 4, usw., liat question perbedaan sebelum dan sesudah dikasih (ausgewertete Variables) z.B : TR01_xx und TR02_xx dan auswerten hasilnya.
---
### Update 2026-11-20 (AC Scoring und Auswertung)
- AC_01,02,04,05,07,09: Antworten spiegeln (-2 <-> +2); AC_03,06,08: nicht spiegeln. Skala 1-5 wird zu -2..+2, +2 = positiv.
- Auswertung: pro Teilnehmer usefulness = Mittel(AC_01,03,05,07,09), satisfaction = Mittel(AC_02,04,06,08); jeweils fuer before (AC01_) und after (AC02_); danach Durchschnitt ueber alle Teilnehmer.

---
### Update 2026-11-20 (Antwort Rafa: MM, TR, Gruppen)
- MM_06 reverse; die anderen Items hat das Survey-Tool schon umgepolt (nicht reversen).
- MM Kategorien: functions = MM_11,12,14,16,17,18,19,20,23; limitations = MM_06,09,10,13,24,15,21,22; operations = MM_25,26,27. Pro Item M, SD, Min, Max; pro Kategorie Mittel der Item-M und Item-SD plus Min/Max; gesamt MM M, SD, Min, Max (3 Ebenen: Item, Kategorie, gesamt).
- TR_12: noch nicht sicher, vorerst in Trust. Auswertung mit M, SD, Min, Max.
- Auswertungsebenen (wahrscheinlich): Gruppe (CADS-Level), Material (Manual/Video), Before-After.
- Gruppen = CADS-Level (automatisch/teilautomatisch), je Level zwei Instruktionen: Manual (Text) und Video.
- Kein Zeitfilter.
- Entscheidungen im Gespräch: MM_01-05,07,08 nicht auswerten; Kategorie-Min/Max aus Rohwerten; AC/TR auf Item- und Subskalen-Ebene; alle Gruppen-/Material-Varianten ausgeben.
