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

## Architecture du dépôt

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

### Jalons prévisionnels

- [ ] Configurer l'environnement Python.
- [ ] Implémenter le chargement vidéo et l'extraction des images.
- [ ] Développer la détection et le suivi de l'hélicoïde.
- [ ] Estimer la trajectoire de la particule.
- [ ] Estimer le mouvement de rotation.
- [ ] Valider les mesures à partir des données expérimentales.
- [ ] Documenter et rendre reproductible l'analyse finale.

## Contributeurs

- Hadrien Figadère
- Membres de l'équipe projet
- Encadrants scientifiques

## Remerciements

Ce projet s'inscrit dans le cadre d'un projet de recherche de troisième année d'école d'ingénieurs consacré à l'étude expérimentale des hélicoïdes isotropes et de leur comportement hydrodynamique.

Le projet bénéficie des ressources expérimentales et de l'accompagnement scientifique des encadrants.

## Licence

Aucune licence n'a été définie à ce stade. Les conditions de réutilisation et de diffusion du code devront être discutées avec les encadrants avant toute publication publique du dépôt.
