"""Détection 2D de l'objet : par couleur (HSV) ou par contraste sombre (Otsu)."""
from dataclasses import dataclass

import cv2
import numpy as np

# Orange saturé sur mur beige (mesuré sur la vidéo test : H~17, S~220)
ORANGE_LO = (5, 110, 100)
ORANGE_HI = (25, 255, 255)


@dataclass
class Detection:
    cx: float
    cy: float
    area: float
    contour: np.ndarray


def _clean_mask(mask, kernel_size):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)    # supprime le bruit
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)   # bouche les petits trous


def _detections_from_mask(mask, min_area):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in contours:
        m = cv2.moments(c)
        if m["m00"] < min_area:
            continue
        out.append(Detection(m["m10"] / m["m00"], m["m01"] / m["m00"], m["m00"], c))
    return sorted(out, key=lambda d: -d.area)   # le plus gros d'abord


def detect_color(frame_bgr, hsv_lo=ORANGE_LO, hsv_hi=ORANGE_HI,
                 min_area=150.0, kernel_size=5):
    """Objets d'une couleur donnée (plage HSV). Ignore ombres et mains."""
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(hsv_lo), np.array(hsv_hi))
    return _detections_from_mask(_clean_mask(mask, kernel_size), min_area)


def detect_dark(frame_bgr, min_area=500.0, kernel_size=5):
    """Objets sombres sur fond clair (seuil d'Otsu)."""
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return _detections_from_mask(_clean_mask(mask, kernel_size), min_area)


def touches_border(det, width, height):
    """Vrai si l'objet est coupé par le bord de l'image (centroïde biaisé)."""
    x, y, w, h = cv2.boundingRect(det.contour)
    return x <= 0 or y <= 0 or x + w >= width or y + h >= height