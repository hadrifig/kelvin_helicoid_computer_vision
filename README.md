# Hélicoïde isotrope de Kelvin — Vision par ordinateur

## Présentation du projet

Ce projet vise à développer une chaîne de traitement en vision par ordinateur afin de suivre et de reconstruire le mouvement d'hélicoïdes isotropes en chute dans un fluide visqueux.

L'objectif est d'étudier expérimentalement le couplage entre translation et rotation de géométries d'hélicoïdes optimisées, inspirées du concept d'hélicoïde isotrope proposé par Lord Kelvin.

À partir de vidéos des expériences, nous cherchons à estimer la trajectoire, l'orientation et le mouvement de rotation des particules au cours du temps.

## Objectifs

- Traiter les vidéos expérimentales des hélicoïdes en chute.
- Détecter et suivre les hélicoïdes d'une image à l'autre.
- Reconstruire la trajectoire 2D ou 3D des particules, selon le dispositif expérimental.
- Estimer l'orientation et le mouvement de rotation des particules.
- Extraire des mesures quantitatives et produire des visualisations.
- Valider les résultats obtenus par vision par ordinateur à partir des observations expérimentales.

## Architecture initiale du dépôt

```text
kelvin_helicoid_computer_vision/
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── exploration.ipynb
├── src/
│   ├── video_processing.py
│   ├── object_tracking.py
│   ├── trajectory.py
│   └── rotation.py
├── tests/
└── results/
    ├── figures/
    └── tables/
```

### Rôle des dossiers

- `data/raw/` : vidéos expérimentales originales.
- `data/processed/` : données extraites et traitées.
- `notebooks/` : exploration des données et essais d'algorithmes.
- `src/` : code source de la chaîne de traitement.
- `tests/` : tests des fonctions développées.
- `results/figures/` : graphiques et visualisations.
- `results/tables/` : tableaux de mesures et résultats numériques.

Les vidéos brutes et les données volumineuses ne sont pas destinées à être versionnées directement sur GitHub par défaut.

## Technologies utilisées

- **Python** : langage principal de développement.
- **OpenCV** : traitement vidéo, analyse d'images et suivi d'objets.
- **NumPy** : calcul numérique.
- **Matplotlib** : visualisation des trajectoires et des résultats.
- **Pandas** : manipulation et analyse des données.
- **Jupyter Notebook** : exploration interactive et prototypage.

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
python -m pip install opencv-python numpy matplotlib pandas jupyter
```

## Fonctionnement de la chaîne de traitement

Le développement sera organisé progressivement dans le dossier `src/`.

1. **Traitement vidéo** : chargement des vidéos, extraction des images et prétraitement.
2. **Détection et suivi** : localisation de l'hélicoïde et suivi de sa position au fil des images.
3. **Reconstruction de trajectoire** : estimation de la position de la particule en fonction du temps.
4. **Estimation de la rotation** : détermination de l'orientation et de la dynamique de rotation de l'hélicoïde.
5. **Analyse des résultats** : production de graphiques, de tableaux et de mesures quantitatives.

Les algorithmes et méthodes retenus seront précisés au fur et à mesure de l'avancement du projet.

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
- Documenter les algorithmes, leurs paramètres et les versions des bibliothèques.
- Enregistrer les mesures traitées dans des formats documentés, comme CSV.
- Distinguer les données brutes, les données traitées et les résultats finaux.
- Ne pas publier de données volumineuses ou confidentielles sans autorisation.

## État d'avancement

**Statut :** initialisation du dépôt et mise en place de l'environnement de développement.

# Roadmap du module Computer Vision

Objectif : mesurer la **trajectoire** et la **rotation** d'hélicoïdes isotropes en chute libre dans un fluide visqueux, avec une précision angulaire suffisante pour détecter le couplage translation-rotation (signal faible).

Approche : **pipeline simple et validé d'abord** (monoculaire, 2D), puis complexification (3D, multi-caméras, filtrage) seulement si la précision s'avère insuffisante.

## Vue d'ensemble

| Phase | Contenu | Durée estimée |
|---|---|---|
| 1 | Setup environnement | 0,5 jour |
| 2 | Calibration caméra | 1 jour |
| 3 | Détection 2D | 1 jour |
| 4 | Tracking | 1 jour |
| 5 | Rotation (ArUco) | 2–3 jours |
| 6 | Validation cas contrôlé | 2 jours |
| — | **Jalon 1 : pipeline monoculaire fonctionnel** | **~2 semaines** |
| 7 | Correction de réfraction | 2–3 jours |
| 8 | Filtrage (Kalman) | 2 jours |
| 9 | Stéréovision | 1 semaine |
| 10 | Pose 3D (6 DDL) | 1 semaine |
| 11 | Extraction du couplage | 1 semaine |
| 12 | Documentation / livrable | 1 semaine (continu) |

## Phase 1 · Mise en place (0,5 jour)

- Repo Git ( branches `main` + `dev`, revue de code entre pairs).
- Environnement Python : `opencv-python`, `numpy`, `scipy`, `matplotlib` ; environnements verrouillés ( `requirements.txt` ou `uv/pip-tools`).
- Convention de nommage des données brutes : `data/ YYYY-MM-DD_experience / video .mp4 + metadata (json)` — la métadonnée (fluide, température, particule, fps) est indispensable pour l'analyse.

**Sortie :** repo clonable, vidéo de test lisible par `cv2.VideoCapture`.

## Phase 2 · Calibration caméra (1 jour)

- Imprimer une mire chessboard ( `cv2.findChessboardCorners`), filmer ~20 poses couvrant tout le champ.
- `cv2.calibrateCamera` → matrice intrinsèque (focale, centre optique) + coefficients de distorsion.
- Conserver les paramètres en JSON versionné ( `calib/intrinsics.json`).

**Sortie :** images dé-distordues via `cv2.undistort`.

## Phase 3 · Détection 2D (1 jour)

- Fond contrasté + éclairage diffus ; seuillage automatique d'Otsu ( `cv2.threshold`).
- Plus grand contour : `cv2.findContours` ; centroïde : `cv2.moments`.
- Nettoyage morphologique ( `cv2.morphologyEx`) contre le bruit et bulles.

**Sortie :** positions pixel (x, y) par frame. → C'est la **trajectoire**.

## Phase 4 · Tracking (1 jour)

- Association du plus proche voisin entre frames (distance euclidienne + limite de déplacement).
- Détection des frames problématiques (sortie de champ, occlusion) → log, pas de data silencieuse.

**Sortie :** série temporelle propre `t, x, y` avec trous explicitement marqués.

## Phase 5 · Rotation via ArUco (2–3 jours)

- Coller/intégrer 2–3 **marqueurs ArUco** ( `cv2.aruco`) sur la particule — à valider avec les encadrants pour ne pas perturber l'hydrodynamique (légers, symétriques en masse).
- Détection : `detectMarkers` → angle 2D par frame ; lever les ambiguïtés avec plusieurs marqueurs à orientations connues.
- Ambiguïté 180° (proche de la caméra) : arbitrage par la trajectoire du centroïde.

**Sortie :** angle de rotation θ(t), résolution visée ~1°.

## Phase 6 · Validation cas contrôlé (2 jours)

- Sphère marquée avec rotation **imposée connue** (chute ou support motorisé).
- Comparer mesure vs vérité terrain → erreur angulaire et biais systématique.
- Cette valeur est le critère GO/NO-GO : si erreur << rotation attendue du couplage, le design expérimental est validé.

**Sortie :** note interne « précision de la chaîne de mesure = X° ».

## Jalon 1 (~2 semaines)

Pipeline monoculaire complet : vidéo → trajectoire + rotation. Première chute d'un hélicoïde réel possible, conclusion sur la suffisance du monoculaire.

## Phase 7 · Correction de réfraction (2–3 jours)

- Rayons déviés aux interfaces air/verre/fluide (Snell-Descartes) → biais de position.
- Option simple : calibration directe dans le fluide (grille immergée) → on « apprend » la déformation plutôt que la modéliser.
- Option propre : modèle géométrique multi-interfaces, correction par frame.

## Phase 8 · Filtrage (2 jours)

- Filtre de Kalman 1D par axe (position, vitesse, angle) : lissage + interpolation des trous.
- Ne filtrer qu'**après** validation — sinon on risque d'effacer le signal faible qu'on cherche.

## Phase 9 · Stéréovision (1 semaine) — si nécessaire

- 2 caméras synchronisées : `stereoCalibrate` (intrinsèques + rotation/translation relatives).
- Triangulation : `cv2.triangulatePoints` → position 3D complète.

## Phase 10 · Pose 3D complète (1 semaine)

- `cv2.solvePnP` sur 4+ marqueurs → attitude 3D complète de la particule.
- Nécessaire seulement si le couplage doit être observé en 3D (couplage isotrope → toutes orientations).

## Phase 11 · Extraction du couplage (1 semaine)

- Régression θ(t) vs trajectoire x(t) : la pente estimate le couplage translation-rotation.
- Quantification d'incertitudes : bootstrap sur les répétitions de chutes (n ≥ 10).
- Comparaison aux prédictions théoriques des codes MATLAB des encadrants.

## Phase 12 · Documentation & livrable (en continu)

- README, docstrings, notebooks de démo reproductibles.
- Structure du livrable 3 : `code/ + data/ traitée + figures + scripts reproductibles`.

## Règles de développement

1. **Simple d'abord** : aucune phase avancée avant validation de la précédente.
2. Un module = une responsabilité (calibration, détection, tracking, reconstruction, analyse).
3. Tout fichier de sortie est reproductible depuis les données brutes + le code versionné.
4. Tests systématiques sur cas contrôlés avant toute donnée réelle.

## Contributeurs

- Hadrien Figadère
- Florian Thollot
- Encadrants scientifiques

## Licence

Aucune licence n'a été définie à ce stade. Les conditions de réutilisation et de diffusion du code devront être discutées avec les encadrants avant toute publication publique du dépôt.
