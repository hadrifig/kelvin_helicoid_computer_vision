"""Chaîne : vidéos -> détection -> filtre de Kalman -> analyse."""

import argparse
from collections import deque
from functools import partial
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from src.kalman import KalmanTracker
from src.object_tracking import (
    ORANGE_HI, ORANGE_LO, detect_color, detect_dark, touches_border
)
from src.trajectory import (
    add_derived_columns,
    fall_summary,
    plot_global_analysis,
    plot_video_analysis,
    video_summary
)
from src.video_processing import get_video_info, iter_frames, list_videos


RACINE = Path(__file__).resolve().parent.parent
DOSSIER_ENTREE = RACINE / "data" / "raw"
DOSSIER_SORTIE = RACINE / "results" / "results_pipeline"

CLES_ETAT = (
    "x", "y", "vx", "vy", "ax", "ay",
    "sx", "sy", "svx", "svy", "sax", "say"
)

CLES_VITESSE = (
    "vx", "vy", "ax", "ay",
    "svx", "svy", "sax", "say"
)


def a_depasse_seuil(det, start_frame, y_stop):
    """
    Renvoie True si, après l'initialisation du chronomètre, la
    détection réelle courante dépasse y_stop (y > y_stop).

    Appelée à chaque image : la première fois qu'elle renvoie True,
    la vidéo est arrêtée.
    """
    return (
        y_stop is not None
        and start_frame is not None
        and det is not None
        and det.cy > y_stop
    )


def process_video(
    video_path,
    out_dir,
    mode="color",
    mm_per_px=None,
    meas_std=5.0,
    jerk_psd=1e8,
    max_missed=3,
    hsv_lo=ORANGE_LO,
    hsv_hi=ORANGE_HI,
    write_video=True,
    y_min=0.0,
    y_max=250.0,
    y_stop=1250.0
):
    """
    Traite une vidéo.

    Conditions :
    - Déclenchement du chronomètre lorsque y_min <= y <= y_max.
    - Arrêt de la vidéo lorsque y dépasse y_stop pour la première
      fois après le déclenchement.
    - Les images antérieures au déclenchement sont supprimées
      des résultats d'analyse.

    Renvoie un DataFrame, ou None si le chronomètre n'a jamais
    été déclenché.
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    info = get_video_info(video_path)

    fps = info["fps"]
    W = info["width"]
    H = info["height"]

    if fps <= 0:
        raise ValueError("FPS invalide")

    if y_stop is not None and y_stop >= H:
        print(
            f"ATTENTION : y_stop = {y_stop} px >= hauteur de l'image "
            f"({H} px), l'arrêt ne se déclenchera jamais."
        )

    s = W / 480.0
    th = max(1, int(2 * s))

    detect = (
        partial(
            detect_color,
            hsv_lo=tuple(hsv_lo),
            hsv_hi=tuple(hsv_hi)
        )
        if mode == "color"
        else detect_dark
    )

    tracker = KalmanTracker(
        fps,
        bounds=(W, H),
        max_missed=max_missed,
        meas_std=meas_std,
        jerk_psd=jerk_psd
    )

    writer = (
        cv2.VideoWriter(
            str(out_dir / "annotated.mp4"),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (W, H),
            True
        )
        if write_video else None
    )

    trail = deque(maxlen=30)
    rows = []

    # Image de déclenchement du chronomètre
    start_frame = None

    try:
        for idx, frame in iter_frames(video_path):

            dets = detect(frame)

            # Élimination des objets coupés par les bords
            full = [
                d for d in dets
                if not touches_border(d, W, H)
            ]

            edge = len(full) < len(dets)

            status, st, used = tracker.step(
                [(d.cx, d.cy) for d in full]
            )

            if status == "searching" and edge:
                status = "edge"

            # Détection effectivement utilisée par Kalman
            det = full[used] if used is not None else None

            # ---------------------------------------------
            # INITIALISATION DU CHRONOMÈTRE
            # ---------------------------------------------

            if (
                start_frame is None
                and det is not None
                and y_min <= det.cy <= y_max
            ):
                start_frame = idx

                print(
                    f"Début du chronomètre : image {idx}, "
                    f"y = {det.cy:.1f} px"
                )

            # Temps relatif au déclenchement
            if start_frame is not None:
                t_rel = (idx - start_frame) / fps
            else:
                t_rel = np.nan

            # ---------------------------------------------
            # ENREGISTREMENT DES DONNÉES
            # ---------------------------------------------

            row = {
                "frame": idx,
                "t": t_rel,
                "status": status,
                "x_meas": det.cx if det is not None else np.nan,
                "y_meas": det.cy if det is not None else np.nan,
                "diameter_px": (
                    det.diameter if det is not None else np.nan
                ),
                "nis": (
                    tracker.last_nis
                    if tracker.last_nis is not None
                    else np.nan
                )
            }

            for k in CLES_ETAT:
                row[k] = st[k] if st else np.nan

            if status == "init":
                for k in CLES_VITESSE:
                    row[k] = np.nan

            row["speed"] = (
                float(np.hypot(row["vx"], row["vy"]))
                if st else np.nan
            )

            rows.append(row)

            # ---------------------------------------------
            # VIDÉO ANNOTÉE
            # ---------------------------------------------

            if writer is not None:

                if det is not None:

                    cv2.drawContours(
                        frame,
                        [det.contour],
                        -1,
                        (0, 255, 0),
                        th
                    )

                    cv2.circle(
                        frame,
                        (int(det.cx), int(det.cy)),
                        int(4 * s),
                        (0, 0, 255),
                        -1
                    )

                if st:

                    p = (int(st["x"]), int(st["y"]))
                    trail.append(p)

                    cv2.circle(
                        frame,
                        p,
                        int(9 * s),
                        (255, 0, 0),
                        th
                    )

                points = list(trail)

                for a, b in zip(points[:-1], points[1:]):
                    cv2.line(frame, a, b, (255, 0, 0), th)

                cv2.putText(
                    frame,
                    f"frame {idx} [{status}]",
                    (int(10 * s), int(30 * s)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6 * s,
                    (0, 0, 0),
                    th
                )

                if st and not np.isnan(row["vy"]):

                    txt = f"vy = {row['vy']:7.0f} px/s"

                    if mm_per_px:
                        txt += (
                            f" ({row['vy'] * mm_per_px / 1000:.2f} m/s)"
                        )

                    cv2.putText(
                        frame,
                        txt,
                        (int(10 * s), int(60 * s)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6 * s,
                        (0, 0, 200),
                        th
                    )

                if start_frame is not None:
                    cv2.putText(
                        frame,
                        f"Temps : {t_rel:.3f} s",
                        (int(10 * s), int(90 * s)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6 * s,
                        (0, 0, 200),
                        th
                    )

                writer.write(frame)

            # ---------------------------------------------
            # ARRÊT : y dépasse y_stop pour la première fois
            # ---------------------------------------------

            if a_depasse_seuil(det, start_frame, y_stop):
                print(
                    f"Arrêt de la vidéo : image {idx}, "
                    f"y = {det.cy:.1f} px > {y_stop:.0f} px "
                    f"(t = {t_rel:.3f} s)"
                )
                break

    finally:
        # Libération du writer même en cas d'erreur
        if writer is not None:
            writer.release()

    # -----------------------------------------------------
    # CONSTRUCTION DU DATAFRAME
    # -----------------------------------------------------

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError("Aucune image traitée")

    if start_frame is None:

        print(
            "ATTENTION : aucune détection acceptée "
            f"dans la zone y = {y_min} à {y_max} px."
        )

        # Brut sauvegardé pour diagnostic ; pas d'analyse possible
        df.to_csv(
            out_dir / "trajectory.csv",
            index=False
        )

        return None

    # Suppression des images antérieures au déclenchement
    df = df[df["frame"] >= start_frame].copy()

    # Calcul des grandeurs dérivées
    df = add_derived_columns(df)

    # Alias attendu par plot_global_analysis (trajectory.py)
    df["t_rel"] = df["t"]

    # -----------------------------------------------------
    # EXPORT CSV
    # -----------------------------------------------------

    df.to_csv(
        out_dir / "trajectory.csv",
        index=False
    )

    # Détections réelles uniquement
    df_detectees = df[df["x_meas"].notna()].copy()

    df_detectees.to_csv(
        out_dir / "detections.csv",
        index=False
    )

    # -----------------------------------------------------
    # GRAPHIQUE
    # -----------------------------------------------------

    plot_video_analysis(
        df_detectees,
        out_dir / "analysis.png",
        title=Path(video_path).name,
        meas_std=meas_std
    )

    print(
        f"Images conservées : {len(df)} "
        f"| Détections réelles : {len(df_detectees)}"
    )

    return df


def process_folder(
    folder=DOSSIER_ENTREE,
    out_root=DOSSIER_SORTIE,
    recursive=False,
    **kwargs
):
    """Traite toutes les vidéos d'un dossier."""

    videos = list_videos(folder, recursive)

    if not videos:
        raise FileNotFoundError(
            f"Aucune vidéo dans {folder}"
        )

    out_root = Path(out_root)

    dfs = {}
    rows = []

    for i, v in enumerate(videos, 1):

        name = v.stem

        print(
            f"[{i}/{len(videos)}] {v.name} ...",
            flush=True
        )

        try:

            df = process_video(
                v,
                out_root / name,
                **kwargs
            )

            # Chronomètre jamais déclenché : vidéo ignorée
            if df is None:
                rows.append({
                    "video": name,
                    "qualite": "aucun déclenchement"
                })
                continue

            rows.append(
                video_summary(
                    df,
                    name,
                    kwargs.get("mm_per_px")
                )
            )

            # Ajouté seulement si le résumé a réussi
            dfs[name] = df

        except Exception as e:

            print(f"    ECHEC : {e!r}")

            rows.append({
                "video": name,
                "qualite": f"erreur : {e!r}"
            })

    summary = pd.DataFrame(rows)

    glob = out_root / "_global"
    glob.mkdir(parents=True, exist_ok=True)

    summary.to_csv(
        glob / "resume_videos.csv",
        index=False
    )

    if dfs:

        try:
            plot_global_analysis(
                dfs,
                summary,
                glob / "analyse_globale.png"
            )
        except Exception as e:
            print(f"ECHEC du graphique global : {e!r}")

    else:
        print("Aucune vidéo exploitable : pas de graphique global.")

    return summary, dfs


if __name__ == "__main__":

    ap = argparse.ArgumentParser(
        description=__doc__
    )

    ap.add_argument(
        "--folder",
        default=str(DOSSIER_ENTREE)
    )

    ap.add_argument(
        "--video",
        default=None
    )

    ap.add_argument(
        "--out",
        default=str(DOSSIER_SORTIE)
    )

    ap.add_argument(
        "--recursive",
        action="store_true"
    )

    ap.add_argument(
        "--mode",
        choices=["color", "dark"],
        default="color"
    )

    ap.add_argument(
        "--mm-per-px",
        type=float,
        default=None
    )

    ap.add_argument(
        "--meas-std",
        type=float,
        default=5.0
    )

    ap.add_argument(
        "--jerk-psd",
        type=float,
        default=1e8
    )

    ap.add_argument(
        "--y-min",
        type=float,
        default=0.0
    )

    ap.add_argument(
        "--y-max",
        type=float,
        default=250.0
    )

    ap.add_argument(
        "--y-stop",
        type=float,
        default=1250.0,
        help="arrête la vidéo quand y dépasse cette valeur (px)"
    )

    ap.add_argument(
        "--hsv-lo",
        type=int,
        nargs=3,
        default=list(ORANGE_LO)
    )

    ap.add_argument(
        "--hsv-hi",
        type=int,
        nargs=3,
        default=list(ORANGE_HI)
    )

    ap.add_argument(
        "--no-video",
        action="store_true"
    )

    a = ap.parse_args()

    opts = dict(
        mode=a.mode,
        mm_per_px=a.mm_per_px,
        meas_std=a.meas_std,
        jerk_psd=a.jerk_psd,
        y_min=a.y_min,
        y_max=a.y_max,
        y_stop=a.y_stop,
        hsv_lo=a.hsv_lo,
        hsv_hi=a.hsv_hi,
        write_video=not a.no_video
    )

    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)

    if a.video:

        name = Path(a.video).stem

        df = process_video(
            a.video,
            Path(a.out) / name,
            **opts
        )

        if df is None:
            print("Aucune analyse : le chronomètre n'a pas été déclenché.")
        else:
            print(
                df["status"].value_counts().to_string()
            )

            for k, v in (
                fall_summary(df, a.mm_per_px) or {}
            ).items():

                print(f"{k:>20} : {v:,.2f}")

        print("Résultats :", Path(a.out) / name)

    else:

        summary, _ = process_folder(
            a.folder,
            a.out,
            a.recursive,
            **opts
        )

        cols = [
            "video",
            "qualite",
            "n_ok",
            "vy_finale_px_s",
            "ay_moyenne_px_s2",
            "rms_residu_px",
            "nis_moyen"
        ]

        cols = [
            c for c in cols
            if c in summary.columns
        ]

        print(
            "\n",
            summary[cols].round(1).to_string(index=False)
        )

        print("\nRésultats :", a.out)