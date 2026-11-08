"""Tableau de résultats, vitesse de chute et graphiques."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def finite_difference_vy(df):
    """Vitesse verticale brute (différences finies) sur les mesures valides, pour comparaison."""
    vy = pd.Series(np.nan, index=df.index)
    ok = df["y_meas"].notna()
    if ok.sum() >= 2:
        vy[ok] = np.gradient(df.loc[ok, "y_meas"].to_numpy(), df.loc[ok, "t"].to_numpy())
    return vy


def fall_summary(df, mm_per_px=None):
    """Résumé de la chute (vy > 0 = vers le bas). Ignore le point 'init' (vitesse inconnue)."""
    ok = df[df["status"].isin(["ok", "predicted"])]
    if ok.empty:
        return None
    s = {
        "frames_suivies": int(len(df[df["status"].isin(["init", "ok", "predicted"])])),
        "vy_finale_px_s": float(ok["vy"].iloc[-1]),
        "vy_max_px_s": float(ok["vy"].max()),
        "vy_moyenne_px_s": float(ok["vy"].mean()),
        # on écarte la 1re accélération : le filtre n'a pas encore convergé
        "ay_moyenne_px_s2": float((ok["ay"].iloc[1:] if len(ok) > 1 else ok["ay"]).mean()),
    }
    if mm_per_px:
        s["vy_finale_m_s"] = s["vy_finale_px_s"] * mm_per_px / 1000.0
        s["vy_max_m_s"] = s["vy_max_px_s"] * mm_per_px / 1000.0
        s["ay_moyenne_m_s2"] = s["ay_moyenne_px_s2"] * mm_per_px / 1000.0
    return s


def plot_results(df, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fd = finite_difference_vy(df)
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    ax[0].plot(df["x_meas"], df["y_meas"], "ro", label="mesure")
    ax[0].plot(df["x"], df["y"], "b.-", label="Kalman")
    ax[0].invert_yaxis()
    ax[0].set(xlabel="x (px)", ylabel="y (px)", title="Trajectoire")
    ax[0].legend()
    ax[1].plot(df["t"], df["y_meas"], "ro", label="mesure")
    ax[1].plot(df["t"], df["y"], "b-", label="Kalman")
    ax[1].set(xlabel="t (s)", ylabel="y (px)", title="Position verticale")
    ax[1].legend()
    ax[2].plot(df["t"], fd, "ro", label="différences finies")
    ax[2].plot(df["t"], df["vy"], "b.-", label="Kalman")
    ax[2].set(xlabel="t (s)", ylabel="vy (px/s)", title="Vitesse de chute")
    ax[2].legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)