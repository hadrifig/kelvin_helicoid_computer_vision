"""Lecture vidéo et inventaire d'un dossier de vidéos."""
from pathlib import Path

import cv2
import pandas as pd

EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}
RACINE = Path(__file__).resolve().parent.parent
DOSSIER_RESULTATS = RACINE / "results" / "results_video_processing"
NOM_TABLEAU = "inventaire_videos.csv"

def iter_frames(path):
    """Générateur (indice, image BGR). Libère la vidéo à la fin."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Impossible d'ouvrir {path}")
    try:
        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            yield idx, frame
            idx += 1
    finally:
        cap.release()


def get_video_info(path) -> dict:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Impossible d'ouvrir {path}")
    info = {
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "n_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }
    cap.release()
    return info


def list_videos(folder, recursive=False):
    """Liste triée des fichiers vidéo d'un dossier."""
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {folder}")
    pattern = "**/*" if recursive else "*"
    return sorted(p for p in folder.glob(pattern)
                  if p.is_file() and p.suffix.lower() in EXTENSIONS)

def save_table(df, out_dir=DOSSIER_RESULTATS, name=NOM_TABLEAU):
    """Enregistre le tableau en CSV (dossier créé si besoin) et renvoie son chemin."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    df.to_csv(path, index=False, encoding="utf-8-sig")   # accents lisibles dans Excel
    return path

def scan_videos(folder, recursive=False, count_frames=False,
                out_dir=DOSSIER_RESULTATS) -> pd.DataFrame:
    """Traite toutes les vidéos d'un dossier, renvoie un tableau (1 ligne par vidéo)
    et l'enregistre dans out_dir (par défaut results/results_video_processing).
    out_dir=None : pas d'enregistrement.

    count_frames=True lit réellement toutes les images (plus lent) : le compteur
    annoncé par le fichier est parfois faux.
    Une vidéo illisible ne bloque pas les autres : elle est signalée dans 'statut'.
    """
    rows = []
    for path in list_videos(folder, recursive):
        row = {"fichier": path.name, "chemin": str(path),
               "taille_Mo": round(path.stat().st_size / 1e6, 2)}
        try:
            info = get_video_info(path)
            row.update(fps=round(info["fps"], 2), largeur=info["width"],
                       hauteur=info["height"], n_frames=info["n_frames"])
            if count_frames:
                row["n_frames_lues"] = sum(1 for _ in iter_frames(path))
            n = row.get("n_frames_lues", info["n_frames"])
            row["duree_s"] = round(n / info["fps"], 3) if info["fps"] > 0 else None
            row["statut"] = "ok" if n > 0 else "vide"
        except Exception as e:                      # fichier corrompu, codec absent...
            row["statut"] = f"erreur : {e}"
        rows.append(row)
    df = pd.DataFrame(rows).convert_dtypes()   # entiers propres même avec des lignes en erreur
    if out_dir is not None and not df.empty:
        df.attrs["fichier_csv"] = str(save_table(df, out_dir))
    return df

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default=str(RACINE / "data" / "raw"),
                    help="dossier contenant les vidéos (défaut : data/raw)")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--count-frames", action="store_true")
    ap.add_argument("--out", default=str(DOSSIER_RESULTATS),
                    help="dossier où enregistrer le tableau")
    a = ap.parse_args()
    df = scan_videos(a.folder, a.recursive, a.count_frames, out_dir=a.out)
    pd.set_option("display.width", 200)
    if df.empty:
        print("Aucune vidéo trouvée dans :", a.folder)
    else:
        print(df.drop(columns="chemin").to_string(index=False))
        print("\nTableau enregistré :", df.attrs["fichier_csv"])