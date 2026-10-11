# Journal des modifications (CHANGELOG)

Toutes les modifications notables apportées au projet **PlateArrangers** sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère aux principes de [Semantic Versioning](https://semver.org/lang/fr/).

---

## [1.0.0] - 2026-10-11

### ✨ Ajouté
- **Interface graphique CustomTkinter (`app.py`)** :
  - Interface utilisateur moderne, claire et intuitive.
  - Sélecteur de mode d'apparence (Système, Sombre, Clair).
  - Sélecteurs de répertoires avec boîtes de dialogue natives.
  - Détection dynamique et comptage en temps réel des images TIFF présentes dans le dossier source avec indicateur coloré.
  - Formulaire de paramétrage avec contrôles de validation (nom de projet, puits de départ, nombre de champs, nombre de longueurs d'onde).
  - Dialogue de fin de traitement avec bouton d'accès direct vers le dossier de destination dans l'Explorateur Windows.

- **Moteur de renommage (`generateur_plaques.py` & `app.py`)** :
  - Support du balayage systématique d'une plaque 96 puits (lignes A à H, colonnes 01 à 12).
  - Prise en charge des plaques partielles grâce au paramètre de puits de départ (ex. `A01`, `C04`).
  - Imbrication personnalisable des longueurs d'onde ($W$) et des champs ($S$).
  - Nomenclature standardisée : `[NomProjet]-[Puits]-[Colonne]-[Ligne]-S[Champ]-W[LongueurDOnde].[EXT]`.
  - Copie physique non-destructive des fichiers avec préservation des métadonnées (`shutil.copy2`).
  - Arrêt automatique sans erreur lorsque le stock d'images sources est épuisé.

- **Rapport de traçabilité** :
  - Génération automatique d'un fichier `rapport_renommage.txt` consignant l'ensemble des paramètres d'exécution et le tableau de correspondance complet ancien nom ↔ nouveau nom.

- **Packaging et Déploiement** :
  - Fichier de spécification PyInstaller (`PlateArrangers.spec`) configuré pour la création d'un exécutable Windows autonome (`PlateArrangers.exe`).
  - Documentation complète d'utilisation et d'installation dans `README.md`.
