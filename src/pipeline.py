"""Chaîne : vidéo -> détection -> filtre de Kalman -> vitesse de chute."""
import argparse
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from src.kalman import KalmanTracker
from src.object_tracking import detect_color, detect_dark, touches_border
from src.trajectory import fall_summary, plot_results
from src.video_processing import get_video_info, iter_frames


def process_video(video_path, out_dir, mode="color", mm_per_px=None,
                  meas_std=5.0, jerk_psd=1e8, max_missed=3):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    info = get_video_info(video_path)
    fps, W, H = info["fps"], info["width"], info["height"]
    s = W / 480.0                      # échelle de dessin
    th = max(1, int(2 * s))
    detect = detect_color if mode == "color" else detect_dark

    tracker = KalmanTracker(fps, bounds=(W, H), max_missed=max_missed,
                            meas_std=meas_std, jerk_psd=jerk_psd)
    writer = cv2.VideoWriter(str(out_dir / "annotated.mp4"),
                             cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H), True)
    trail = deque(maxlen=30)
    rows = []

    for idx, frame in iter_frames(video_path):
        dets = detect(frame)
        full = [d for d in dets if not touches_border(d, W, H)]   # objets entiers
        edge = len(full) < len(dets)                              # un objet est coupé
        status, st, used = tracker.step([(d.cx, d.cy) for d in full])
        if status == "searching" and edge:
            status = "edge"

        det = full[used] if used is not None else None
        row = {"frame": idx, "t": idx / fps, "status": status,
               "x_meas": det.cx if det else np.nan,
               "y_meas": det.cy if det else np.nan}
        for k in ("x", "y", "vx", "vy", "ax", "ay"):
            row[k] = st[k] if st else np.nan
        if status == "init":              # vitesse pas encore estimable
            for k in ("vx", "vy", "ax", "ay"):
                row[k] = np.nan
        row["speed"] = float(np.hypot(row["vx"], row["vy"])) if st else np.nan
        rows.append(row)

        # --- annotation ---
        if det is not None:
            cv2.drawContours(frame, [det.contour], -1, (0, 255, 0), th)
            cv2.circle(frame, (int(det.cx), int(det.cy)), int(4 * s), (0, 0, 255), -1)
        if st:
            p = (int(st["x"]), int(st["y"]))
            trail.append(p)
            cv2.circle(frame, p, int(9 * s), (255, 0, 0), th)
        for a, b in zip(list(trail)[:-1], list(trail)[1:]):
            cv2.line(frame, a, b, (255, 0, 0), th)
        cv2.putText(frame, f"frame {idx} [{status}]", (int(10 * s), int(30 * s)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6 * s, (0, 0, 0), th)
        if st and not np.isnan(row["vy"]):
            txt = f"vy = {row['vy']:7.0f} px/s"
            if mm_per_px:
                txt += f" ({row['vy'] * mm_per_px / 1000:.2f} m/s)"
            cv2.putText(frame, txt, (int(10 * s), int(60 * s)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6 * s, (0, 0, 200), th)
        writer.write(frame)
    writer.release()

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "trajectory.csv", index=False)
    plot_results(df, out_dir / "results.png")
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", default="results")
    ap.add_argument("--mode", choices=["color", "dark"], default="color")
    ap.add_argument("--mm-per-px", type=float, default=None)
    a = ap.parse_args()
    df = process_video(a.video, a.out, a.mode, a.mm_per_px)
    print(df["status"].value_counts().to_string())
    print(df.loc[df.status.isin(["init", "ok", "predicted"]),
                 ["frame", "status", "x_meas", "y_meas", "y", "vy", "ay"]].round(1).to_string(index=False))
    for k, v in (fall_summary(df, a.mm_per_px) or {}).items():
        print(f"{k:>20} : {v:,.2f}")