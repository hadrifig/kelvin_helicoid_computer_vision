"""Filtre de Kalman à accélération constante (2D) et suivi de l'objet."""
import numpy as np


class ConstantAccelerationKalman:
    """État : [x, vx, ax, y, vy, ay] (px, px/s, px/s²). Mesure : (x, y) en px."""

    def __init__(self, dt, meas_std=5.0, jerk_psd=1e8, v_max=15000.0, a_max=60000.0):
        self.dt = dt
        self.meas_std = meas_std
        self.v_max, self.a_max = v_max, a_max
        self.R = np.eye(2) * meas_std ** 2
        self.H = np.zeros((2, 6))
        self.H[0, 0] = self.H[1, 3] = 1.0
        # Modèle par axe : [pos, vit, acc], bruit = saut d'accélération (jerk) blanc
        F1 = np.array([[1, dt, dt ** 2 / 2], [0, 1, dt], [0, 0, 1]])
        Q1 = jerk_psd * np.array([[dt ** 5 / 20, dt ** 4 / 8, dt ** 3 / 6],
                                  [dt ** 4 / 8, dt ** 3 / 3, dt ** 2 / 2],
                                  [dt ** 3 / 6, dt ** 2 / 2, dt]])
        self.F = np.zeros((6, 6))
        self.Q = np.zeros((6, 6))
        for s in (slice(0, 3), slice(3, 6)):
            self.F[s, s] = F1
            self.Q[s, s] = Q1
        self.x = np.zeros(6)
        self.P = np.eye(6)

    def init(self, z):
        """Premier point : position connue, vitesse et accélération très incertaines."""
        self.x = np.array([z[0], 0.0, 0.0, z[1], 0.0, 0.0])
        sp, sv, sa = self.meas_std, self.v_max, self.a_max
        self.P = np.diag([sp ** 2, sv ** 2, sa ** 2, sp ** 2, sv ** 2, sa ** 2])

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

    def mahalanobis2(self, z):
        """Distance² de Mahalanobis entre la mesure z et la prédiction."""
        nu = np.asarray(z, float) - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        return float(nu @ np.linalg.solve(S, nu))

    def update(self, z):
        nu = np.asarray(z, float) - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ nu
        I_KH = np.eye(6) - K @ self.H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R @ K.T   # forme de Joseph

    @property
    def state(self):
        x = self.x
        return {"x": x[0], "vx": x[1], "ax": x[2], "y": x[3], "vy": x[4], "ay": x[5]}


class KalmanTracker:
    """Suit un objet : prédiction, association par Mahalanobis, gestion des trous.

    Statuts : searching (rien suivi), init (1er point), ok (mesure utilisée),
    predicted (mesure absente/rejetée, position prédite), lost (piste abandonnée).
    """

    GATE_99 = 9.21   # seuil du chi² à 2 ddl (99 %)

    def __init__(self, fps, bounds=None, max_missed=3, **kf_kwargs):
        self.kf = ConstantAccelerationKalman(1.0 / fps, **kf_kwargs)
        self.bounds = bounds          # (largeur, hauteur) de l'image
        self.max_missed = max_missed
        self.active = False
        self.missed = 0

    def step(self, measurements):
        """measurements : liste de (x, y). Renvoie (statut, état|None, indice_mesure|None)."""
        if not self.active:
            if not measurements:
                return "searching", None, None
            self.kf.init(measurements[0])
            self.active, self.missed = True, 0
            return "init", self.kf.state, 0

        self.kf.predict()
        used = None
        if measurements:
            d2 = [self.kf.mahalanobis2(m) for m in measurements]
            best = int(np.argmin(d2))
            if d2[best] < self.GATE_99:
                used = best
        if used is not None:
            self.kf.update(measurements[used])
            self.missed = 0
            return "ok", self.kf.state, used

        self.missed += 1
        st = self.kf.state
        outside = self.bounds is not None and not (
            0 <= st["x"] <= self.bounds[0] and 0 <= st["y"] <= self.bounds[1])
        if self.missed > self.max_missed or outside:
            self.active = False
            return "lost", None, None
        return "predicted", st, None