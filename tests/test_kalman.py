import numpy as np
from src.kalman import KalmanTracker


def _chute(n=20, fps=30.0, a=3000.0, sigma=3.0, seed=1):
    """Mesures bruitées d'une chute à accélération constante (pas de vidéo, juste des nombres)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n) / fps
    x = 300 + 50 * t
    y = 100 + 0.5 * a * t ** 2
    z = np.c_[x, y] + rng.normal(0, sigma, (n, 2))
    return t, z, a * t   # vitesse verticale vraie


def test_vitesse_estimee_proche_de_la_vraie():
    t, z, vy_true = _chute()
    tr = KalmanTracker(30.0, bounds=(1080, 1920))
    vy = []
    for m in z:
        status, st, _ = tr.step([tuple(m)])
        vy.append(st["vy"] if status == "ok" else np.nan)
    assert abs(vy[-1] - vy_true[-1]) / vy_true[-1] < 0.10


def test_mesure_absente_puis_piste_perdue():
    t, z, _ = _chute()
    tr = KalmanTracker(30.0, bounds=(1080, 1920), max_missed=3)
    for m in z[:8]:
        tr.step([tuple(m)])
    statuts = [tr.step([])[0] for _ in range(4)]
    assert statuts == ["predicted", "predicted", "predicted", "lost"]


def test_mesure_aberrante_rejetee():
    t, z, _ = _chute()
    tr = KalmanTracker(30.0, bounds=(1080, 1920))
    for m in z[:10]:
        tr.step([tuple(m)])
    status, st, used = tr.step([(z[10][0] + 500, z[10][1])])   # faux positif à 500 px
    assert status == "predicted" and used is None


def test_rien_a_suivre():
    tr = KalmanTracker(30.0)
    assert tr.step([])[0] == "searching"