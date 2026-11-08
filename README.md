# Hélicoïde isotrope de Kelvin — Vision par ordinateur

## Présentation du projet

Ce projet vise à développer une chaîne de traitement en vision par ordinateur afin de suivre et de reconstruire le mouvement d'hélicoïdes isotropes en chute dans un fluide visqueux.

L'objectif est d'étudier expérimentalement le couplage entre translation et rotation de géométries d'hélicoïdes optimisées, inspirées du concept d'hélicoïde isotrope proposé par Lord Kelvin.

À partir de vidéos des expériences, nous cherchons à estimer la trajectoire et la vitesse de chute des particules au cours du temps, puis, dans un second temps, leur orientation et leur rotation.

## Objectifs

- Traiter les vidéos expérimentales des objets en chute.
- Détecter et suivre l'objet d'une image à l'autre.
- Reconstruire la trajectoire 2D et estimer la vitesse de chute par filtre de Kalman.
- Extraire des mesures quantitatives avec leurs incertitudes et produire des visualisations.
- Valider la chaîne de mesure (biais, dispersion, cohérence statistique du filtre).
- Comparer l'approche classique (détection par couleur) à une approche apprise (SAM, YOLO) sous contrainte de frugalité (latence CPU, taille du modèle).
- *Perspective :* estimer l'orientation et la rotation des particules, puis le couplage translation-rotation (voir « Perspectives »).

## Architecture du dépôt

```text
kelvin_helicoid_computer_vision/
├── README.md
├── .gitignore
├── requirements.txt
├── pytest.ini
├── data/
│   ├── raw/                          # vidéos originales (non versionnées)
│   └── processed/
├── notebooks/
│   └── exploration.ipynb
├── src/
│   ├── video_processing.py           # lecture vidéo, inventaire d'un dossier de vidéos
│   ├── object_tracking.py            # détection 2D (couleur HSV ou contraste sombre)
│   ├── kalman.py                     # filtre de Kalman à accélération constante + suivi
│   ├── trajectory.py                 # résumés, vitesse de chute, graphiques
│   └── pipeline.py                   # chaîne complète sur un dossier de vidéos
├── tests/
│   ├── test_kalman.py
│   └── test_real_video.py
└── results/
    ├── results_video_processing/     # inventaire des vidéos (CSV)
    └── results_pipeline/             # une analyse par vidéo + un dossier _global
```

Modules prévus par la roadmap : `calibration.py` (phase 3), `simulation.py` et lissage RTS (phase 4), détection apprise SAM / YOLO (phase 5), `benchmark.py` pour la latence (phase 6), comparaison de trackers (phase 7).

### Rôle des dossiers

- `data/raw/` : vidéos expérimentales originales.
- `data/processed/` : données extraites et traitées.
- `notebooks/` : exploration des données et essais d'algorithmes.
- `src/` : code source de la chaîne de traitement.
- `tests/` : tests des fonctions développées.
- `results/results_video_processing/` : tableau d'inventaire des vidéos.
- `results/results_pipeline/<video>/` : trajectoire, graphiques d'analyse et vidéo annotée de chaque vidéo.
- `results/results_pipeline/_global/` : tableau récapitulatif et analyse globale de toutes les vidéos.

Les vidéos brutes et les données volumineuses ne sont pas destinées à être versionnées directement sur GitHub par défaut.

## Technologies utilisées

- **Python** : langage principal de développement.
- **OpenCV** : traitement vidéo, analyse d'images et détection d'objets.
- **NumPy** : calcul numérique et filtre de Kalman.
- **Matplotlib** : visualisation des trajectoires et des résultats.
- **Pandas** : manipulation et analyse des données.
- **pytest** : tests automatisés.
- **Jupyter Notebook** : exploration interactive et prototypage.
- *Prévus (phases 4 à 7) :* SciPy (algorithme hongrois), SAM, Ultralytics (YOLO, ByteTrack, BoT-SORT), ONNX Runtime.

## Installation

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd kelvin_helicoid_computer_vision
```

Remplacer `<URL_DU_DEPOT>` par l'URL HTTPS du dépôt GitHub.

### 2. Créer un environnement virtuel

**Windows (PowerShell) :**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux :**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

Si le fichier `requirements.txt` n'est pas encore renseigné, installer les bibliothèques initiales avec :

```bash
python -m pip install opencv-python numpy pandas matplotlib pytest jupyter
```

## Utilisation

Placer les vidéos dans `data/raw/`, puis, depuis la racine du projet :

```bash
python -m src.video_processing data/raw --count-frames   # inventaire des vidéos
python -m src.pipeline                                    # traite toutes les vidéos de data/raw
python -m src.pipeline --no-video                         # idem, sans vidéo annotée (plus rapide)
python -m src.pipeline --mm-per-px 0.27                   # ajoute les unités physiques (m/s, m/s²)
python -m src.pipeline --video data/raw/test.mp4          # une seule vidéo
python -m pytest -v                                       # tests
```

Les résultats sont écrits dans `results/results_pipeline/`.

## Fonctionnement de la chaîne de traitement

1. **Lecture vidéo** : chargement des vidéos d'un dossier et inventaire (cadence, résolution, nombre d'images).
2. **Détection** : localisation de l'objet par sa couleur (plage HSV réglable) ou par contraste sombre (seuil d'Otsu). Un objet coupé par le bord de l'image est signalé et n'est pas utilisé.
3. **Suivi par filtre de Kalman** : modèle à accélération constante, association des mesures par distance de Mahalanobis, gestion des mesures manquantes. Chaque image reçoit un statut explicite : `searching`, `edge`, `init`, `ok`, `predicted` ou `lost`.
4. **Analyse** : positions, trajectoire, vitesse de chute, accélération, incertitudes (±2σ du filtre), résidus et NIS. Un tableau récapitulatif (`resume_videos.csv`) et une analyse globale sont produits pour l'ensemble des vidéos.

## Travail collaboratif avec Git et GitHub

Le projet est développé en collaboration à l'aide de Git et GitHub.

Avant de commencer à travailler, récupérer les dernières modifications :

```bash
git pull origin main
```

Créer une branche pour chaque fonctionnalité :

```bash
git switch -c feature/suivi-objet
```

Après avoir développé et testé les modifications :

```bash
git add .
git commit -m "Ajout du suivi de l'hélicoïde"
git push -u origin feature/suivi-objet
```

Une *Pull Request* pourra ensuite être créée sur GitHub afin de relire les modifications et de les intégrer à la branche `main`.

Il est recommandé d'éviter les modifications directes sur `main` pour les fonctionnalités importantes.

## Données expérimentales et reproductibilité

Pour garantir la reproductibilité des analyses :

- Documenter la fréquence d'acquisition vidéo et les paramètres de la caméra.
- Préciser les méthodes de calibration et l'échelle spatiale utilisée.
- Documenter les algorithmes, leurs paramètres (`meas_std`, `jerk_psd`, plages HSV) et les versions des bibliothèques.
- Enregistrer les mesures traitées dans des formats documentés, comme CSV.
- Distinguer les données brutes, les données traitées et les résultats finaux.
- Fixer les graines aléatoires (`seed`) des simulations.
- Ne pas publier de données volumineuses ou confidentielles sans autorisation.

## État d'avancement

**Statut :** chaîne de traitement de base fonctionnelle (détection par couleur, filtre de Kalman, analyse par vidéo et globale), testée sur une vidéo de test. L'acquisition des 20 vidéos expérimentales est la prochaine étape.

- [x] Lecture vidéo et inventaire d'un dossier
- [x] Détection 2D par couleur (HSV)
- [x] Filtre de Kalman à accélération constante, avec incertitudes (σ) et NIS
- [x] Pipeline par lot, analyse par vidéo et analyse globale
- [x] Tests automatisés (filtre, vidéo de test, dossier)
- [ ] Phases 1 à 7 de la roadmap ci-dessous

# Roadmap du module Computer Vision

Objectif : mesurer la **trajectoire** et la **vitesse de chute** d'objets en chute par vision par ordinateur, **valider la chaîne de mesure par des chiffres** (biais, dispersion, cohérence du filtre), puis comparer l'approche classique à une approche apprise sous contrainte de frugalité.

Approche : **pipeline simple et validé d'abord** (monoculaire, 2D), puis complexification seulement si les résultats l'exigent.

## Vue d'ensemble

| Phase | Contenu
|---|---|---|
| 1 | Protocole et acquisition
| 2 | Évaluer le filtre de Kalman initial
| 3 | Calibration et échelle
| 4 | Filtre rigoureux : RTS, NIS, Monte Carlo, hongrois
| 5 | Détection apprise : SAM puis YOLO
| 6 | Frugalité : latence CPU, taille du modèle
| 7 | Comparaison de trackers

Jalons :
- **Jalon 1 (après la phase 4)** : chaîne de mesure validée et chiffrée (accélération mesurée avec son incertitude, filtre statistiquement cohérent).
- **Jalon 2 (après la phase 7)** : comparaison approche classique / approche apprise / trackers, avec précision, latence et taille de modèle.


## Contributeurs

- Hadrien Figadère
- Florian Thollot
- Encadrants scientifiques

## Licence

Aucune licence n'a été définie à ce stade. Les conditions de réutilisation et de diffusion du code devront être discutées avec les encadrants avant toute publication publique du dépôt.