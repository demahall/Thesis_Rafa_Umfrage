#!/usr/bin/env python3
"""Visualisierung Projekt Rafa (nur Plots).

Aufgabe 1: Spaghetti-Plot (Paired Slopegraph) fuer Mental Model, pro Gruppe ein Bild.
  - 2x2 Subplots: functions | limitations / operations | total
  - X: t1 (pre), t2 (post); Y: Mental model scores (Personen-Mittel ueber die Items der Kategorie)
  - Eine Linie pro Teilnehmer. Manual = blau, Punkt, durchgezogen. Video = rot, Quadrat, gestrichelt.
Aufgabe 2: gleicher Plot-Typ fuer Trust (links, TR_06-12) und Distrust (rechts, TR_01-05), 2x1 Subplots, Y 1-7.

Aufgabe 3: gleicher Plot-Typ fuer Acceptance, Usefulness (links) und Satisfaction (rechts), 2x1, Y -2 bis +2.

Eingabe : output/data_clean.csv (aus preprocessing.py)
Ausgabe : output/plots/mm_spaghetti_group1-4.png, output/plots/tr_spaghetti_group1-4.png, output/plots/ac_spaghetti_group1-4.png
Start   : python3 visualization.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from analysis import AC_SUB, MM_CAT, MM_ALL, TR_SUB, col  # gleiche Item-Definitionen wie in der Auswertung

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
PLOTS = OUT / "plots"

STYLE = {
    "manual": {"color": "#1f4fd8", "marker": "o", "ls": "-", "label": "Manual", "dx": -0.02},
    "video": {"color": "#d62728", "marker": "s", "ls": "--", "label": "Video", "dx": 0.02},
}
PANELS = [("functions", MM_CAT["functions"], "Functions"),
          ("limitations", MM_CAT["limitations"], "Limitations"),
          ("operations", MM_CAT["operations"], "Operations"),
          ("total", MM_ALL, "Total")]


def person_scores(d, construct, items, t):
    return d[[col(construct, t, i) for i in items]].mean(axis=1)


def draw_spaghetti(ax, d, construct, items, title, ylabel, ylim):
    """Eine Linie pro Teilnehmer von t1 nach t2, getrennt nach Material."""
    s1, s2 = person_scores(d, construct, items, 1), person_scores(d, construct, items, 2)
    for medium, st in STYLE.items():
        m = d["medium"] == medium
        for a, b in zip(s1[m], s2[m]):
            ax.plot([0 + st["dx"], 1 + st["dx"]], [a, b], color=st["color"], ls=st["ls"],
                    lw=1.4, alpha=0.8, marker=st["marker"], ms=6, clip_on=False)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["t1 (pre)", "t2 (post)"])
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(*ylim)
    ax.set_yticks(range(ylim[0], ylim[1] + 1))
    ax.tick_params(labelleft=True)
    ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.4)
    ax.set_xlabel("Measurement time point")
    ax.set_ylabel(ylabel)


def legend_handles(d):
    return [Line2D([0], [0], color=st["color"], ls=st["ls"], marker=st["marker"], ms=7, lw=1.6,
                   label="%s (n=%d)" % (st["label"], int((d["medium"] == m).sum())))
            for m, st in STYLE.items()]


def plot_mm(df, g):
    d = df[df["group"] == g]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
    for ax, (key, items, title) in zip(axes.ravel(), PANELS):
        draw_spaghetti(ax, d, "MM", items, title, "Mental model scores", (1, 6))
    fig.legend(handles=legend_handles(d), loc="upper right", frameon=True)
    fig.suptitle("Mental Model Scores for group %d" % g, fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = PLOTS / ("mm_spaghetti_group%d.png" % g)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_tr(df, g):
    d = df[df["group"] == g]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    draw_spaghetti(axes[0], d, "TR", TR_SUB["trust"], "Trust", "Trust", (1, 7))
    draw_spaghetti(axes[1], d, "TR", TR_SUB["distrust"], "Distrust", "Distrust", (1, 7))
    fig.legend(handles=legend_handles(d), loc="upper right", frameon=True)
    fig.suptitle("Trust and Distrust Group %d" % g, fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    path = PLOTS / ("tr_spaghetti_group%d.png" % g)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_ac(df, g):
    d = df[df["group"] == g]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    draw_spaghetti(axes[0], d, "AC", AC_SUB["usefulness"], "Usefulness", "Usefulness Scores", (-2, 2))
    draw_spaghetti(axes[1], d, "AC", AC_SUB["satisfaction"], "Satisfaction", "Satisfaction Scores", (-2, 2))
    fig.legend(handles=legend_handles(d), loc="upper right", frameon=True)
    fig.suptitle("Acceptance Scores for Group %d" % g, fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    path = PLOTS / ("ac_spaghetti_group%d.png" % g)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(OUT / "data_clean.csv")
    for g in sorted(df["group"].unique()):
        print("geschrieben:", plot_mm(df, g))
        print("geschrieben:", plot_tr(df, g))
        print("geschrieben:", plot_ac(df, g))


if __name__ == "__main__":
    main()
