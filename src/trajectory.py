"""Résumés, analyses et graphiques de la chute (par vidéo et globale)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

SUIVI = ["init", "ok", "predicted"]                      # images où une position Kalman existe
CODES_STATUT = {"searching": 0, "edge": 1, "lost": 2, "predicted": 3, "init": 4, "ok": 5}
COULEURS_STATUT = ["#d9d9d9", "#ff9f1c", "#e63946", "#ffd166", "#90be6d", "#2a9d8f"]
G = 9.81   # m/s²

def detect_fall_start(df, speed_threshold=60.0, consecutive=3):
    """
    Détecte le début réel de la chute.
    vy positif = mouvement vers le bas.
    Il faut plusieurs mesures consécutives au-dessus du seuil.
    """
    valid = df["status"].eq("ok") & df["vy"].notna()

    moving = valid & (df["vy"] > speed_threshold)

    # Évite de considérer une seule mesure aberrante comme un début de chute
    sustained = (
        moving.rolling(consecutive, min_periods=consecutive)
        .sum()
        .eq(consecutive)
    )

    indices = df.index[sustained]

    if len(indices) == 0:
        return np.nan

    # Retourne le temps de la première mesure de la séquence
    return float(df.loc[indices[0] - consecutive + 1, "t"])

# ------------------------------------------------------------------ calculs
def finite_difference_vy(df):
    """Vitesse verticale brute (différences finies) sur les mesures valides, pour comparaison."""
    vy = pd.Series(np.nan, index=df.index)
    ok = df["y_meas"].notna()
    if ok.sum() >= 2:
        vy[ok] = np.gradient(df.loc[ok, "y_meas"].to_numpy(), df.loc[ok, "t"].to_numpy())
    return vy


def add_derived_columns(df):
    """Temps relatif au début réel de la chute et résidus."""

    df = df.copy()

    # Détection du début de la chute
    t_start = detect_fall_start(df)

    df["t_rel"] = df["t"] - t_start if np.isfinite(t_start) else np.nan

    # Résidus uniquement sur les mesures utilisées
    ok = df["status"] == "ok"

    df["resid_x"] = np.where(
        ok, df["x_meas"] - df["x"], np.nan
    )
    df["resid_y"] = np.where(
        ok, df["y_meas"] - df["y"], np.nan
    )

    return df


def fall_summary(df, mm_per_px=None):
    """Statistiques calculées uniquement sur les mesures réelles."""

    df = df.copy()

    # Début réel de la chute
    t_start = detect_fall_start(df)

    if not np.isfinite(t_start):
        return None

    # Mesures réellement exploitées pendant la chute
    ok = df[
        (df["status"] == "ok") &
        (df["t"] >= t_start)
    ]

    if len(ok) < 3:
        return None

    s = {
        "frames_suivies": int(len(ok)),
        "vy_finale_px_s": float(ok["vy"].iloc[-1]),
        "vy_max_px_s": float(ok["vy"].max()),
        "vy_moyenne_px_s": float(ok["vy"].mean()),
        "ay_moyenne_px_s2": float(ok["ay"].iloc[1:].mean()),
    }

    if mm_per_px:
        s["vy_finale_m_s"] = s["vy_finale_px_s"] * mm_per_px / 1000
        s["vy_max_m_s"] = s["vy_max_px_s"] * mm_per_px / 1000
        s["ay_moyenne_m_s2"] = s["ay_moyenne_px_s2"] * mm_per_px / 1000

    return s

def video_summary(df, name, mm_per_px=None):
    """Une ligne de tableau pour une vidéo : couverture du suivi + chute + diagnostics."""
    suivi = df[df["status"].isin(SUIVI)]
    ok = df[df["status"] == "ok"]
    n_ok = len(ok)
    row = {
        "video": name,
        "qualite": "ok" if n_ok >= 4 else ("insuffisant" if n_ok > 0 else "aucune_piste"),
        "n_images": len(df),
        "n_suivies": len(suivi),
        "n_ok": n_ok,
        "n_predites": int((df["status"] == "predicted").sum()),
        "n_bord": int((df["status"] == "edge").sum()),
        "t_debut_s": float(suivi["t"].iloc[0]) if not suivi.empty else np.nan,
        "duree_suivie_s": float(suivi["t"].iloc[-1] - suivi["t"].iloc[0]) if len(suivi) > 1 else np.nan,
        "y_debut_px": float(suivi["y"].iloc[0]) if not suivi.empty else np.nan,
        "y_fin_px": float(suivi["y"].iloc[-1]) if not suivi.empty else np.nan,
    }
    fall = fall_summary(df, mm_per_px) or {}
    fall.pop("frames_suivies", None)
    row.update(fall)
    # Diagnostics du filtre
    row["rms_residu_px"] = (float(np.sqrt(np.nanmean(ok["resid_x"] ** 2 + ok["resid_y"] ** 2)))
                            if n_ok else np.nan)                      # mesure - Kalman, après correction
    row["nis_moyen"] = float(ok["nis"].mean()) if n_ok and "nis" in ok else np.nan   # attendu ~ 2
    row["diametre_moyen_px"] = float(ok["diameter_px"].mean()) if n_ok else np.nan
    return row


# ------------------------------------------------------------------ graphiques
def _vide(ax, message="pas de données"):
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes, color="gray")


def _bande(ax, t, v, s, k=2, color="tab:blue"):
    ax.fill_between(t, v - k * s, v + k * s, color=color, alpha=0.2, label=f"±{k}σ")


def plot_video_analysis(df, path, title="", meas_std=5.0):
    """Analyse d'une vidéo : trajectoire, x(t), y(t), vy(t), ay(t), résidus (bandes = ±2σ du filtre)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    tr = df[df["status"].isin(SUIVI)]
    if tr.empty:
        fig, a = plt.subplots(figsize=(6, 3))
        _vide(a, f"{title} : aucun objet suivi")
        a.axis("off")
        fig.savefig(path, dpi=120)
        plt.close(fig)
        return
    ms = df[df["x_meas"].notna()]
    vel = df[df["status"].isin(["ok", "predicted"])]
    ok = df[df["status"] == "ok"]
    fd = finite_difference_vy(df)
    s = fall_summary(df)
    sous_titre = (f"{s['frames_suivies']} images suivies | vy finale = {s['vy_finale_px_s']:,.0f} px/s"
                  f" | ay moyenne = {s['ay_moyenne_px_s2']:,.0f} px/s²") if s else ""

    fig, ax = plt.subplots(2, 3, figsize=(17, 9))
    fig.suptitle(f"{title}\n{sous_titre}", fontsize=12)

    a = ax[0, 0]                                                    # trajectoire
    a.plot(ms["x_meas"], ms["y_meas"], "ro", label="mesure")
    a.plot(tr["x"], tr["y"], "b.-", label="Kalman")
    for r in tr.itertuples():
        a.annotate(str(r.frame), (r.x, r.y), textcoords="offset points", xytext=(6, 3), fontsize=7)
    a.invert_yaxis()
    a.set(xlabel="x (px)", ylabel="y (px)", title="Trajectoire (numéro = image)")
    a.legend()

    for a, col, sig, nom in ((ax[0, 1], "x", "sx", "Position horizontale x(t)"),
                             (ax[0, 2], "y", "sy", "Position verticale y(t)")):
        a.plot(ms["t"], ms[f"{col}_meas"], "ro", label="mesure")
        a.plot(tr["t"], tr[col], "b-", label="Kalman")
        _bande(a, tr["t"], tr[col], tr[sig])
        a.set(xlabel="t (s)", ylabel=f"{col} (px)", title=nom)
        a.legend()

    a = ax[1, 0]                                                    # vitesse de chute
    if vel.empty:
        _vide(a)
    else:
        a.plot(df["t"], fd, "ro", label="différences finies")
        a.plot(vel["t"], vel["vy"], "b.-", label="Kalman")
        _bande(a, vel["t"], vel["vy"], vel["svy"])
        a.legend()
    a.set(xlabel="t (s)", ylabel="vy (px/s)", title="Vitesse de chute vy(t)")

    a = ax[1, 1]                                                    # accélération
    if len(vel) < 2:
        _vide(a)
    else:
        a.plot(vel["t"], vel["ay"], "b.-", label="Kalman")
        _bande(a, vel["t"], vel["ay"], vel["say"])
        a.axhline(vel["ay"].iloc[1:].mean(), color="k", ls="--", lw=1, label="moyenne (sans la 1re)")
        a.legend()
    a.set(xlabel="t (s)", ylabel="ay (px/s²)", title="Accélération ay(t)")

    a = ax[1, 2]                                                    # résidus
    if ok.empty:
        _vide(a)
    else:
        a.plot(ok["t"], ok["resid_x"], "o", label="résidu x")
        a.plot(ok["t"], ok["resid_y"], "s", label="résidu y")
        a.axhline(meas_std, color="gray", ls="--", lw=1, label=f"±meas_std ({meas_std:g} px)")
        a.axhline(-meas_std, color="gray", ls="--", lw=1)
        a.legend()
    a.set(xlabel="t (s)", ylabel="mesure − Kalman (px)", title="Résidus (après correction)")

    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_global_analysis(dfs, summary, path):
    """Vue d'ensemble de toutes les vidéos : superposition, accélérations, histogramme, couverture."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    couleurs = plt.cm.tab20(np.linspace(0, 1, 20))
    fig, ax = plt.subplots(2, 3, figsize=(19, 10))
    fig.suptitle(f"Analyse globale — {len(dfs)} vidéo(s) traitée(s)", fontsize=13)

    for i, (nom, df) in enumerate(dfs.items()):
        c = couleurs[i % 20]

        # On conserve uniquement les mesures réellement détectées
        tr = df[df["x_meas"].notna()]

        if tr.empty:
            continue

        # Les vitesses sont calculées uniquement sur les mesures réelles
        vel = tr[tr["vy"].notna()]

        # 1. Trajectoires spatiales
        ax[0, 0].plot(
        tr["x"], tr["y"], ".-",
        color=c, label=nom
        )

        # 2. Position verticale en fonction du temps relatif
        ax[0, 1].plot(
        tr["t_rel"], tr["y"], ".-",
        color=c, label=nom
        )

        # 3. Vitesse verticale en fonction du temps relatif
        ax[0, 2].plot(
        vel["t_rel"], vel["vy"], ".-",
        color=c, label=nom
        )
    ax[0, 0].invert_yaxis()
    ax[0, 0].set(xlabel="x (px)", ylabel="y (px)", title="Trajectoires superposées")
    if len(dfs) <= 12:
        ax[0, 0].legend(fontsize=7)
    ax[0, 1].set(xlabel="temps depuis le début du suivi (s)", ylabel="y (px)", title="Position verticale")
    ax[0, 2].set(xlabel="temps depuis le début du suivi (s)", ylabel="vy (px/s)", title="Vitesse de chute (Kalman)")

    bons = summary[summary["qualite"] == "ok"] if "qualite" in summary else summary.iloc[0:0]
    en_ms = "ay_moyenne_m_s2" in bons and bons["ay_moyenne_m_s2"].notna().any()
    col_ay = "ay_moyenne_m_s2" if en_ms else "ay_moyenne_px_s2"
    col_vy = "vy_finale_m_s" if en_ms else "vy_finale_px_s"
    u_ay, u_vy = ("m/s²", "m/s") if en_ms else ("px/s²", "px/s")

    a = ax[1, 0]                                                    # accélération par vidéo
    if bons.empty:
        _vide(a, "aucune vidéo de qualité 'ok'")
    else:
        v = bons[col_ay].to_numpy(float)
        a.bar(range(len(v)), v, color="tab:blue")
        a.set_xticks(range(len(v)))
        a.set_xticklabels(bons["video"], rotation=90, fontsize=7)
        m = np.nanmean(v)
        a.axhline(m, color="k", ls="--", label=f"moyenne = {m:,.1f}")
        if len(v) > 1:
            sd = np.nanstd(v, ddof=1)
            a.axhspan(m - sd, m + sd, color="gray", alpha=0.15, label=f"± écart-type = {sd:,.1f}")
        if en_ms:
            a.axhline(G, color="tab:red", ls=":", label=f"g = {G} m/s²")
        a.legend(fontsize=8)
    a.set(ylabel=f"ay moyenne ({u_ay})", title="Accélération estimée par vidéo")

    a = ax[1, 1]                                                    # histogramme vy finale
    if bons.empty:
        _vide(a, "aucune vidéo de qualité 'ok'")
    else:
        v = bons[col_vy].to_numpy(float)
        a.hist(v[~np.isnan(v)], bins=min(10, max(len(v), 1)), color="tab:green", edgecolor="k")
    a.set(xlabel=f"vy finale ({u_vy})", ylabel="nombre de vidéos", title="Distribution de la vitesse finale")

    a = ax[1, 2]                                                    # couverture du suivi
    if not dfs:
        _vide(a)
    else:
        n_max = max(len(d) for d in dfs.values())
        mat = np.full((len(dfs), n_max), -1.0)
        for i, d in enumerate(dfs.values()):
            mat[i, :len(d)] = d["status"].map(CODES_STATUT).to_numpy(float)
        cmap = ListedColormap(COULEURS_STATUT).with_extremes(bad="white")
        a.imshow(np.ma.masked_less(mat, 0), aspect="auto", cmap=cmap, vmin=0, vmax=5,
                 interpolation="nearest")
        a.set_yticks(range(len(dfs)))
        a.set_yticklabels(list(dfs.keys()), fontsize=7)
        a.legend(handles=[Patch(color=c, label=k) for k, c in zip(CODES_STATUT, COULEURS_STATUT)],
                 fontsize=7, loc="upper right", ncol=2)
    a.set(xlabel="numéro d'image", title="Couverture du suivi (statut de chaque image)")

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)