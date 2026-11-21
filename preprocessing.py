#!/usr/bin/env python3
"""Preprocessing fuer Projekt Rafa (siehe CLAUDE.md, Abschnitte 4, 7a, 8).

Eingabe : raw_data_rafa.csv (UTF-16 LE, tab-getrennt) - wird nie veraendert
Ausgabe : output/data_clean.csv, output/sample_table.csv, output/preprocessing_log.txt
Start   : python3 preprocessing.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw_data_rafa.csv"
OUT = BASE / "output"

LOG = []


def log(msg=""):
    print(msg)
    LOG.append(msg)


def items(prefix, n):
    return ["%s_%02d" % (prefix, i) for i in range(1, n + 1)]


# ---------------------------------------------------------------- Definitionen
AC_ITEMS = {t: items("AC%02d" % t, 9) for t in (1, 2)}
MM_ITEMS = {t: items("MM%02d" % t, 27) for t in (1, 2)}
TR_ITEMS = {t: items("TR%02d" % t, 12) for t in (1, 2)}
TNAME = {1: "t1", 2: "t2"}

AC_USEFUL = [1, 3, 5, 7, 9]
AC_SATISF = [2, 4, 6, 8]
AC_FLIP = [1, 2, 4, 5, 7, 9]   # links positiv -> 3 - x
AC_SHIFT = [3, 6, 8]           # rechts positiv -> x - 3
TR_DISTRUST = list(range(1, 6))
TR_TRUST = list(range(6, 13))  # TR_12 vorerst in Trust (Rafa-Bestaetigung steht aus)

RANGES = {"AC": (1, 5), "MM": (1, 6), "TR": (1, 7)}
FAS_COLS = ["FAS_TWW", "FAS_Spurwarner", "FAS_Tempomat", "FAS_Spurhalte", "FAS_ACC"]


def main():
    OUT.mkdir(exist_ok=True)
    raw = pd.read_csv(RAW, encoding="utf-16", sep="\t", dtype=str, keep_default_na=False)
    df = raw.copy()
    n0 = len(df)
    log("PREPROCESSING Projekt Rafa")
    log("Eingabe: %s (%d Zeilen, %d Spalten)" % (RAW.name, n0, df.shape[1]))
    log("")

    # Zahlenspalten: leer -> NaN, -9 -> NaN (Not answered)
    numeric = [c for c in df.columns
               if c not in ("SERIAL", "REF", "QUESTNNR", "MODE", "STARTED", "STATUS",
                            "MAILSENT", "LASTDATA")]
    for c in numeric:
        df[c] = pd.to_numeric(df[c].replace("", np.nan), errors="coerce")
    all_items = [c for t in (1, 2) for c in AC_ITEMS[t] + MM_ITEMS[t] + TR_ITEMS[t]]
    missing_code_9 = {c: int((df[c] == -9).sum()) for c in all_items}
    df[all_items + ["Alter", "Gender", "Fuehrerscheinbesitz", "Fahrleistung", "Erfahrung"] + FAS_COLS] = \
        df[all_items + ["Alter", "Gender", "Fuehrerscheinbesitz", "Fahrleistung", "Erfahrung"] + FAS_COLS].replace(-9, np.nan)

    # ------------------------------------------------------------- Filter
    log("== FILTER ==")
    log("Start: N = %d" % n0)

    # 1) complete
    finished_check = df[(df["STATUS"] == "complete") != (df["FINISHED"] == 1)]
    keep = df["STATUS"] == "complete"
    log("1) STATUS == complete: N = %d (entfernt: %d, CASE %s)" % (
        keep.sum(), (~keep).sum(), ", ".join(str(int(x)) for x in df.loc[~keep, "CASE"])))
    log("   Gegencheck FINISHED: %s" % (
        "identisch mit STATUS" if finished_check.empty else
        "ABWEICHUNG bei CASE " + ", ".join(str(int(x)) for x in finished_check["CASE"])))
    df = df[keep].copy()

    # 2) Alter >= 18 (Kategorien 1-7 beginnen bei 18-25)
    bad_alter = df[~df["Alter"].isin(range(1, 8))]
    log("2) Alter >= 18: alle Kategorien (1-7) sind >= 18 Jahre. Ungueltig/fehlend: %d%s" % (
        len(bad_alter), (" (CASE %s, wird NICHT entfernt, nur Warnung)" %
                         ", ".join(str(int(x)) for x in bad_alter["CASE"])) if len(bad_alter) else ""))

    # 3) Fuehrerschein
    no_dl = df["Fuehrerscheinbesitz"] == 2
    miss_dl = df["Fuehrerscheinbesitz"].isna()
    log("3) Fuehrerscheinbesitz == 1: entfernt (Wert 2): %d (CASE %s)" % (
        no_dl.sum(), ", ".join(str(int(x)) for x in df.loc[no_dl, "CASE"])))
    if miss_dl.any():
        log("   WARNUNG: Fuehrerscheinbesitz fehlt bei CASE %s (nicht entfernt, Regel: Missing ausserhalb der Messitems = kein Ausschluss)" %
            ", ".join(str(int(x)) for x in df.loc[miss_dl, "CASE"]))
    df = df[~no_dl].copy()
    log("   N = %d" % len(df))

    # 4) fehlende Messitems -> Ausschluss
    miss_items = df[all_items].isna()
    bad = miss_items.any(axis=1)
    log("4) Fehlende Messitems (AC/MM/TR, -9 oder leer): entfernt: %d" % bad.sum())
    for cid, row in miss_items[bad].iterrows():
        cols = list(row[row].index)
        log("   CASE %d: %d fehlend (%s%s)" % (int(df.loc[cid, "CASE"]), len(cols), ", ".join(cols[:5]),
                                              ", ..." if len(cols) > 5 else ""))
    df = df[~bad].copy()
    log("")
    log(">>> Nach Preprocessing-Filter: N = %d (von %d)" % (len(df), n0))
    log("")

    # ------------------------------------------------------------- Checks
    log("== PLAUSIBILITAETSPRUEFUNGEN ==")
    problems = 0
    # (1) Wertebereiche
    for t in (1, 2):
        for name, cols in (("AC", AC_ITEMS[t]), ("MM", MM_ITEMS[t]), ("TR", TR_ITEMS[t])):
            lo, hi = RANGES[name]
            viol = ((df[cols] < lo) | (df[cols] > hi)).sum().sum()
            if viol:
                problems += 1
                log("  FEHLER Wertebereich %s %s: %d Werte ausserhalb %d-%d" % (name, TNAME[t], viol, lo, hi))
    for col, lo, hi in [("Alter", 1, 7), ("Gender", 1, 3), ("Fahrleistung", 1, 5), ("Erfahrung", 1, 3)] + \
                       [(c, 1, 5) for c in FAS_COLS]:
        v = df[col].dropna()
        viol = int(((v < lo) | (v > hi)).sum())
        if viol:
            problems += 1
            log("  FEHLER Wertebereich %s: %d Werte ausserhalb %d-%d" % (col, viol, lo, hi))
    log("(1) Wertebereiche AC 1-5, MM 1-6, TR 1-7, FAS 1-5, Alter 1-7, Gender 1-3: %s" %
        ("OK" if problems == 0 else "Auffaelligkeiten, siehe oben"))

    # (2) DD15
    dd = ["DD15_%02d" % i for i in range(1, 9)]
    n_checked = (df[dd] == 2).sum(axis=1)
    expected = n_checked.where(n_checked > 0, -1)
    dd_bad = df[df["DD15"].notna() & (df["DD15"] != expected)]
    if len(dd_bad):
        problems += 1
        log("(2) DD15-Konsistenz: FEHLER bei CASE %s" % ", ".join(str(int(x)) for x in dd_bad["CASE"]))
    else:
        log("(2) DD15 = Anzahl der Kreuze (oder -1): OK")

    # (3) Fuehrerschein Jahre
    fs_bad = df[(df["Fuehrerscheinbesitz"] == 1) & ~(df["Fuehrerschein"] > 0)]
    if len(fs_bad):
        problems += 1
        log("(3) Fuehrerschein-Konsistenz: WARNUNG, Jahre fehlen/<=0 bei CASE %s" %
            ", ".join(str(int(x)) for x in fs_bad["CASE"]))
    else:
        log("(3) Fuehrerscheinbesitz = 1 und Jahre > 0: OK")

    # (4) Vollstaendigkeit t1/t2 und RG01
    rg_bad = df[~df["RG01"].isin(range(1, 9))]
    complete_ok = df[all_items].notna().all().all()
    if len(rg_bad) or not complete_ok:
        problems += 1
    log("(4) AC/MM/TR t1+t2 vollstaendig: %s; RG01 in 1-8: %s" % (
        "OK" if complete_ok else "FEHLER",
        "OK" if len(rg_bad) == 0 else "FEHLER bei CASE " + ", ".join(str(int(x)) for x in rg_bad["CASE"])))
    log("Gesamt: %s" % ("alle Pruefungen bestanden" if problems == 0 else "%d Auffaelligkeit(en)" % problems))
    log("")

    # ------------------------------------------------------------- Umkodierung
    log("== UMKODIERUNG ==")
    # MM_06 umkehren (1-6: 7 - x), nur dieses Item
    for t in (1, 2):
        src = "MM%02d_06" % t
        df[src + "_rev"] = 7 - df[src]
    chk = all((df["MM%02d_06" % t] + df["MM%02d_06_rev" % t] == 7).all() for t in (1, 2))
    log("MM_06 (t1, t2) umgekehrt: 7 - x, neue Spalten MM01_06_rev, MM02_06_rev (%d Faelle, Kontrolle x + rev = 7: %s)" %
        (len(df), "OK" if chk else "FEHLER"))
    log("  Alle anderen MM-Items unveraendert (Survey-Tool hat sie bereits gepolt).")

    # AC: -2..+2, +2 = positiv
    for t in (1, 2):
        for i in range(1, 10):
            src = "AC%02d_%02d" % (t, i)
            if i in AC_FLIP:
                df[src + "_s"] = 3 - df[src]
            else:
                df[src + "_s"] = df[src] - 3
    ac_s = ["AC%02d_%02d_s" % (t, i) for t in (1, 2) for i in range(1, 10)]
    ok_range = df[ac_s].min().min() >= -2 and df[ac_s].max().max() <= 2
    log("AC t1/t2 auf -2..+2 umgerechnet (+2 = positiv). Items 01,02,04,05,07,09: 3 - x; Items 03,06,08: x - 3. "
        "Spalten AC0t_ii_s. Wertebereich -2..2: %s" % ("OK" if ok_range else "FEHLER"))

    # Subskalen pro Person
    for t in (1, 2):
        k = TNAME[t]
        df["ac_useful_" + k] = df[["AC%02d_%02d_s" % (t, i) for i in AC_USEFUL]].mean(axis=1)
        df["ac_satisf_" + k] = df[["AC%02d_%02d_s" % (t, i) for i in AC_SATISF]].mean(axis=1)
        df["tr_distrust_" + k] = df[["TR%02d_%02d" % (t, i) for i in TR_DISTRUST]].mean(axis=1)
        df["tr_trust_" + k] = df[["TR%02d_%02d" % (t, i) for i in TR_TRUST]].mean(axis=1)
    log("Subskalen pro Person (Mittel): ac_useful (AC 01,03,05,07,09), ac_satisf (AC 02,04,06,08) - "
        "auf Basis der umgerechneten _s-Spalten; tr_distrust (TR 01-05), tr_trust (TR 06-12, TR_12 vorlaeufig enthalten). "
        "Jeweils _t1 / _t2. TR ohne Umkodierung.")

    # Gruppe / Material
    df["group"] = ((df["RG01"] + 1) // 2).astype(int)
    df["medium"] = np.where(df["RG01"] % 2 == 1, "manual", "video")
    log("Abgeleitet: group = (RG01+1)//2 (1-4 = CADS-Level), medium = manual (ungerade) / video (gerade)")

    # L3-Erfahrung
    df["l3_experience"] = df["Erfahrung"].isin([1, 2]).astype(int)
    log("l3_experience = 1 bei Erfahrung 1 oder 2: %d Person(en), CASE %s. Werden nicht entfernt." % (
        df["l3_experience"].sum(),
        ", ".join(str(int(x)) for x in df.loc[df["l3_experience"] == 1, "CASE"]) or "-"))
    log("")

    # ------------------------------------------------------------- Uebersichten
    log("== ERGEBNIS ==")
    log("N nach Filter: %d" % len(df))
    cnt = df.groupby("RG01").size().reindex(range(1, 9), fill_value=0)
    log("N pro RG01-Code: " + ", ".join("%d: %d" % (k, v) for k, v in cnt.items()))
    log("N pro group (CADS-Level): " + ", ".join("%d: %d" % (k, v) for k, v in df.groupby("group").size().items()))
    log("N pro medium: " + ", ".join("%s: %d" % (k, v) for k, v in df.groupby("medium").size().items()))
    log("Zeiten: TIME_SUM Min %d / Max %d s (kein Filter, nur berichtet)" % (df["TIME_SUM"].min(), df["TIME_SUM"].max()))
    log("")

    # Reihenfolge: Rohspalten + abgeleitete Spalten am Ende (siehe CLAUDE.md)
    derived = ["MM01_06_rev", "MM02_06_rev"] + ac_s + \
              [n + "_" + k for k in ("t1", "t2") for n in ("ac_useful", "ac_satisf", "tr_distrust", "tr_trust")] + \
              ["group", "medium", "l3_experience"]
    out = df[list(raw.columns) + derived].copy()
    for c in out.columns:
        if out[c].dtype == float:
            out[c] = out[c].round(4)
    out.to_csv(OUT / "data_clean.csv", index=False, encoding="utf-8")
    log("geschrieben: output/data_clean.csv (%d Zeilen, %d Spalten)" % out.shape)

    # ------------------------------------------------------------- Stichprobentabelle
    cols = ["gesamt"] + ["RG01=%d" % k for k in range(1, 9)]
    subsets = [df] + [df[df["RG01"] == k] for k in range(1, 9)]
    rows = []
    rows.append(["N", "", *[len(s) for s in subsets]])

    def cat(var, labels):
        for code, lab in labels.items():
            rows.append([var, "%s = %s" % (code, lab), *[int((s[var] == code).sum()) for s in subsets]])

    cat("Alter", {1: "18-25", 2: "26-35", 3: "36-45", 4: "46-55", 5: "56-65", 6: "66-75", 7: "76+"})
    cat("Gender", {1: "female", 2: "male", 3: "diverse"})
    cat("Fahrleistung", {1: "0-5000 km", 2: "5001-10000", 3: "10001-15000", 4: "15001-20000", 5: ">20000"})
    cat("Erfahrung", {1: "Drive Pilot", 2: "Personal Pilot", 3: "keine"})
    for var in ["Fuehrerschein"] + FAS_COLS + ["DD15", "TIME_SUM"] + ["TIME%03d" % i for i in range(5, 10)]:
        for stat, f in (("M", "mean"), ("SD", "std"), ("Min", "min"), ("Max", "max")):
            rows.append([var, stat, *[round(float(getattr(s[var], f)()), 2) if len(s) and s[var].notna().any() else "" for s in subsets]])
    dd = ["DD15_%02d" % i for i in range(1, 9)]
    for d in dd:
        rows.append([d, "angekreuzt", *[int((s[d] == 2).sum()) for s in subsets]])
    rows.append(["DD15", "keine (-1)", *[int((s["DD15"] == -1).sum()) for s in subsets]])
    pd.DataFrame(rows, columns=["variable", "wert"] + cols).to_csv(OUT / "sample_table.csv", index=False, encoding="utf-8")
    log("geschrieben: output/sample_table.csv")

    (OUT / "preprocessing_log.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("geschrieben: output/preprocessing_log.txt")


if __name__ == "__main__":
    sys.exit(main())
