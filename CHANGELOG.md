# Journal des modifications (CHANGELOG)

Toutes les modifications notables apportées au projet **PlateArrangers** sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère aux principes de [Semantic Versioning](https://semver.org/lang/fr/).

## [1.1.0] - 2026-10-16

### ✨ Ajouté
- **Système d'internationalisation modulaire (`i18n.py`)** :
  - Externalisation de l'intégralité des textes de l'application (titres, étiquettes, boutons, messages d'erreurs, dialogues et rapports) sous forme de variables de traduction.
  - Support de fichiers texte simples (`.txt`) au format clé/valeur (`CLE = Valeur`), éditables directement dans le Bloc-notes sans risque d'erreur de syntaxe.
  - Détection automatique et dynamique de tout nouveau fichier de langue placé dans le dossier `languages/`.
  - Sélecteur de langue interactif intégré en haut à droite de la fenêtre, à côté du sélecteur de mode d'apparence.
  - Actualisation dynamique immédiate de l'ensemble de l'interface graphique lors du changement de langue, sans redémarrage nécessaire.
  - Fichier de référence `languages/fr.txt` et pack de langue anglaise `languages/en.txt` fournis.
  - Mécanisme de repli sécurisé (*fallback*) vers le français garantissant la stabilité de l'application en cas de clé manquante dans une traduction externe.
  - Mémorisation de la préférence de langue de l'utilisateur.
  - Prise en charge du dossier `languages/` dans la configuration PyInstaller (`PlateArrangers.spec`) et support des ajouts de langues externes à côté de l'exécutable autonome.
- **Documentation multilingue** :
  - Ajout de la documentation complète en langue anglaise dans `README_EN.md`, le fichier principal `README.md` demeurant en français avec des liens de navigation croisée.

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
