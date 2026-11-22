#!/usr/bin/env python3
"""Deskriptive Auswertung fuer Projekt Rafa (siehe CLAUDE.md, Abschnitt 6).

Eingabe : output/data_clean.csv (aus preprocessing.py)
Ausgabe : output/results_descriptive.csv  (alle Kennzahlen, lange Tabelle)
          output/plots/*.png
Start   : python3 analysis.py

Kennzahlen: M, SD (Stichproben-SD, n-1), Min, Max; jeweils t1 (before), t2 (after), Delta M = M_t2 - M_t1.
Ebenen   : Item, Subskala/Kategorie, MM gesamt.
Schnitte : gesamt, pro Gruppe (CADS-Level), pro Material, pro Gruppe x Material.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
PLOTS = OUT / "plots"

# ---- Definitionen (CLAUDE.md Abschnitt 6) -----------------------------------
AC_SUB = {"usefulness": [1, 3, 5, 7, 9], "satisfaction": [2, 4, 6, 8]}
TR_SUB = {"distrust": list(range(1, 6)), "trust": list(range(6, 13))}  # TR_12 vorlaeufig Trust
MM_CAT = {
    "functions": [11, 12, 14, 16, 17, 18, 19, 20, 23],
    "limitations": [6, 9, 10, 13, 15, 21, 22, 24],
    "operations": [25, 26, 27],
}
MM_ALL = sorted(i for v in MM_CAT.values() for i in v)  # 20 Items, MM_01-05/07/08 nicht ausgewertet


def col(construct, t, i):
    """Spaltenname der auszuwertenden Variante eines Items."""
    if construct == "AC":
        return "AC%02d_%02d_s" % (t, i)          # umgerechnet -2..+2
    if construct == "MM":
        return "MM%02d_%02d_rev" % (t, i) if i == 6 else "MM%02d_%02d" % (t, i)
    return "TR%02d_%02d" % (t, i)


def stats(s):
    s = s.dropna()
    return {"M": s.mean(), "SD": s.std(ddof=1) if len(s) > 1 else np.nan, "Min": s.min(), "Max": s.max()}


def item_stats(d, construct, t, i):
    return stats(d[col(construct, t, i)])


def aggregate(d, construct, t, items):
    """MM-Logik: Mittel der Item-M, Mittel der Item-SD, Min der Item-Minima, Max der Item-Maxima."""
    st = [item_stats(d, construct, t, i) for i in items]
    return {"M": np.mean([x["M"] for x in st]),
            "SD": np.nanmean([x["SD"] for x in st]),
            "Min": np.min([x["Min"] for x in st]),
            "Max": np.max([x["Max"] for x in st])}


def person_score(d, construct, t, items):
    """Person-Mittel ueber die Items, danach M/SD/Min/Max ueber Teilnehmer."""
    return stats(d[[col(construct, t, i) for i in items]].mean(axis=1))


def slices(df):
    out = [("gesamt", "alle", df)]
    for g in sorted(df["group"].unique()):
        out.append(("gruppe", "Gruppe %d" % g, df[df["group"] == g]))
    for m in ("manual", "video"):
        out.append(("material", m, df[df["medium"] == m]))
    for g in sorted(df["group"].unique()):
        for m in ("manual", "video"):
            out.append(("gruppe_x_material", "Gruppe %d / %s" % (g, m),
                        df[(df["group"] == g) & (df["medium"] == m)]))
    return out


def build_rows(df):
    rows = []
    for stype, sname, d in slices(df):
        if len(d) == 0:
            continue

        def add(construct, level, name, method, f):
            r1, r2 = f(1), f(2)
            row = {"slice_type": stype, "slice": sname, "n": len(d), "construct": construct,
                   "level": level, "name": name, "method": method}
            for k in ("M", "SD", "Min", "Max"):
                row[k + "_t1"] = r1[k]
            for k in ("M", "SD", "Min", "Max"):
                row[k + "_t2"] = r2[k]
            row["delta_M"] = r2["M"] - r1["M"]
            rows.append(row)

        # Item-Ebene
        for i in range(1, 10):
            add("AC", "item", "AC_%02d" % i, "item", lambda t, i=i: item_stats(d, "AC", t, i))
        for i in MM_ALL:
            add("MM", "item", "MM_%02d" % i, "item", lambda t, i=i: item_stats(d, "MM", t, i))
        for i in range(1, 13):
            add("TR", "item", "TR_%02d" % i, "item", lambda t, i=i: item_stats(d, "TR", t, i))
        # Subskalen / Kategorien (beide Methoden)
        for name, its in AC_SUB.items():
            add("AC", "subscale", name, "item_aggregate", lambda t, its=its: aggregate(d, "AC", t, its))
            add("AC", "subscale", name, "person_score", lambda t, its=its: person_score(d, "AC", t, its))
        for name, its in TR_SUB.items():
            add("TR", "subscale", name, "item_aggregate", lambda t, its=its: aggregate(d, "TR", t, its))
            add("TR", "subscale", name, "person_score", lambda t, its=its: person_score(d, "TR", t, its))
        for name, its in MM_CAT.items():
            add("MM", "category", name, "item_aggregate", lambda t, its=its: aggregate(d, "MM", t, its))
            add("MM", "category", name, "person_score", lambda t, its=its: person_score(d, "MM", t, its))
        # MM gesamt (20 Items)
        add("MM", "total", "MM gesamt (20 Items)", "item_aggregate", lambda t: aggregate(d, "MM", t, MM_ALL))
        add("MM", "total", "MM gesamt (20 Items)", "person_score", lambda t: person_score(d, "MM", t, MM_ALL))
    return pd.DataFrame(rows)


# ---- Plots ------------------------------------------------------------------
COL = {"t1": "#9aa5b1", "t2": "#2b6cb0"}


def bar_panel(ax, res, slice_names, names, title, ylim, hline=None):
    x = np.arange(len(slice_names))
    w = 0.8 / (2 * len(names))
    for ni, name in enumerate(names):
        sub = res[(res["name"] == name)].set_index("slice")
        for ti, t in enumerate(("t1", "t2")):
            pos = x + (ni * 2 + ti - (len(names) * 2 - 1) / 2) * w
            m = [sub.loc[s, "M_" + t] if s in sub.index else np.nan for s in slice_names]
            sd = [sub.loc[s, "SD_" + t] if s in sub.index else np.nan for s in slice_names]
            ax.bar(pos, m, w * 0.95, yerr=sd, color=COL[t], alpha=1.0 if ni == 0 else 0.6,
                   capsize=2, edgecolor="white", linewidth=0.5,
                   label=("%s %s" % (name, "vorher" if t == "t1" else "nachher")))
    ax.set_xticks(x)
    ax.set_xticklabels(["%s\n(n=%d)" % (s, res[res["slice"] == s]["n"].iloc[0]) for s in slice_names],
                       fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_ylim(*ylim)
    if hline is not None:
        ax.axhline(hline, color="black", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)


def make_plots(res):
    PLOTS.mkdir(parents=True, exist_ok=True)
    spec = [
        ("AC", "subscale", ["usefulness", "satisfaction"], (-2.2, 2.6), 0, "Acceptance (-2 bis +2)"),
        ("TR", "subscale", ["distrust", "trust"], (0.5, 7.8), None, "Trust (1 bis 7)"),
        ("MM", "category", ["functions", "limitations", "operations"], (0.5, 6.8), None, "Mental Model (1 bis 6)"),
    ]
    for construct, level, names, ylim, hl, title in spec:
        r = res[(res["construct"] == construct) & (res["level"] == level) & (res["method"] == "person_score")]
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), gridspec_kw={"width_ratios": [1, 2.2, 1.6]})
        panels = [
            (["alle"], "Gesamt"),
            (["Gruppe %d" % g for g in range(1, 5)], "Pro Gruppe (CADS-Level)"),
            (["manual", "video"], "Pro Material"),
        ]
        for ax, (sl, tt) in zip(axes, panels):
            sl = [s for s in sl if s in set(r["slice"])]
            bar_panel(ax, r, sl, names, tt, ylim, hl)
        h, l = axes[0].get_legend_handles_labels()
        fig.legend(h, l, loc="lower center", ncol=len(l), fontsize=8, frameon=False)
        fig.suptitle("%s: vorher vs. nachher (M, Fehlerbalken = SD, Personen-Mittel)" % title, fontsize=11)
        fig.tight_layout(rect=(0, 0.08, 1, 0.95))
        fig.savefig(PLOTS / ("%s_before_after.png" % construct.lower()), dpi=150)
        plt.close(fig)

    # Item-Plot: Delta M je Item (gesamt)
    for construct, n_items in (("AC", 9), ("MM", 20), ("TR", 12)):
        r = res[(res["construct"] == construct) & (res["level"] == "item") & (res["slice"] == "alle")]
        fig, ax = plt.subplots(figsize=(9, 4))
        x = np.arange(len(r))
        ax.bar(x - 0.2, r["M_t1"], 0.4, yerr=r["SD_t1"], color=COL["t1"], capsize=2, label="vorher")
        ax.bar(x + 0.2, r["M_t2"], 0.4, yerr=r["SD_t2"], color=COL["t2"], capsize=2, label="nachher")
        ax.set_xticks(x)
        ax.set_xticklabels(r["name"], rotation=60, fontsize=7)
        ax.set_title("%s pro Item, alle Teilnehmer (M, SD)" % construct, fontsize=10)
        ax.legend(frameon=False, fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        if construct == "AC":
            ax.axhline(0, color="black", lw=0.6)
        fig.tight_layout()
        fig.savefig(PLOTS / ("%s_items.png" % construct.lower()), dpi=150)
        plt.close(fig)


def export_mm_items(res):
    """Auswertung_MM.csv: MM-Items (20) pro Gruppe 1-4, vorher/nachher."""
    labels = {}
    vf = BASE / "variables_cadstraining-study_2026-11-17_10-34.csv"
    if vf.exists():
        v = pd.read_csv(vf, encoding="utf-16", sep="\t", dtype=str, keep_default_na=False)
        for _, r in v[v["VAR"].str.match(r"MM01_\d\d$")].iterrows():
            labels["MM_" + r["VAR"][-2:]] = r["LABEL"].replace("MM_t1: ", "")
    cat_of = {i: c for c, its in MM_CAT.items() for i in its}
    x = res[(res["construct"] == "MM") & (res["level"] == "item") & (res["slice_type"] == "gruppe")].copy()
    x["item_nr"] = x["name"].str[3:].astype(int)
    x["gruppe"] = x["slice"].str[-1].astype(int)
    x["kategorie"] = x["item_nr"].map(cat_of)
    x["item_text"] = x["name"].map(labels)
    x["_c"] = x["kategorie"].map({"functions": 0, "limitations": 1, "operations": 2})
    x = x.sort_values(["gruppe", "_c", "item_nr"])
    cols = ["gruppe", "n", "kategorie", "name", "item_text",
            "M_t1", "SD_t1", "Min_t1", "Max_t1", "M_t2", "SD_t2", "Min_t2", "Max_t2", "delta_M"]
    out = x[cols].rename(columns={"name": "item"})
    out.to_csv(OUT / "Auswertung_MM.csv", index=False, encoding="utf-8")
    return len(out)


def main():
    df = pd.read_csv(OUT / "data_clean.csv")
    res = build_rows(df)
    num = [c for c in res.columns if c.startswith(("M_", "SD_", "Min_", "Max_")) or c == "delta_M"]
    res[num] = res[num].round(3)
    res.to_csv(OUT / "results_descriptive.csv", index=False, encoding="utf-8")
    make_plots(res)
    print("Auswertung_MM.csv: %d Zeilen" % export_mm_items(res))
    print("N = %d, Zeilen in results_descriptive.csv: %d" % (len(df), len(res)))
    show = res[(res["slice"] == "alle") & (res["level"] != "item") & (res["method"] == "person_score")]
    print(show[["construct", "name", "M_t1", "SD_t1", "M_t2", "SD_t2", "delta_M"]].to_string(index=False))
    print("Plots in", PLOTS)


if __name__ == "__main__":
    main()
