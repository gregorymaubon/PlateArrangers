# 🔬 PlateArrangers

Application de renommage et de réorganisation automatisée d'images d'acquisition pour plaques de microscopie 96 puits.

Contact : @gmaubon / maubon.com

---

## 📋 Présentation

Lors de campagnes d'imagerie haut contenu (HCS / High-Content Screening) ou d'acquisitions automatisées sur des microplaques 96 puits, les instruments exportent souvent les clichés TIFF sous des noms séquentiels bruts peu explicites.

**PlateArrangers** permet d'organiser et de renommer ces séries d'images en leur appliquant une nomenclature normalisée et rigoureuse, en associant chaque cliché à sa coordonnée de puits, son champ de vision et sa longueur d'onde, en fonction du séquencement des images d'entrée expliqué ci-dessous.

---

## ✨ Fonctionnalités principales

- **Interface graphique moderne** : Conçue avec [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), intégrant le support dynamique des thèmes *Sombre*, *Clair* et *Système*.
- **Détection dynamique des fichiers** : Analyse en temps réel du dossier source avec indicateur visuel (badge vert/rouge) du nombre d'images TIFF (`.tif`, `.tiff`, `.TIF`, `.TIFF`) détectées.
- **Support des plaques partielles** : Prise en charge d'un puits de départ personnalisable (ex. `A01`, `C04`), permettant de traiter des plaques dont l'acquisition n'a pas débuté au premier puits.
- **Gestion multicanale et multichamp** : Paramétrage libre du nombre de champs de vision par puits et du nombre de longueurs d'onde / canaux d'acquisition.
- **Traitement non-destructif** : Les fichiers sources ne sont jamais modifiés ni déplacés ; ils sont copiés avec préservation des métadonnées (`shutil.copy2`).
- **Arrêt automatique sécurisé** : Le processus s'interrompt proprement dès que tous les fichiers physiques sources ont été attribués, évitant les erreurs d'index.
- **Rapport de traçabilité complet** : Génération automatique d'un fichier `rapport_renommage.txt` dans le dossier de destination, détaillant la configuration et la correspondance exacte entre chaque ancien et nouveau nom.
- **Raccourci explorateur** : Dialogue de fin d'opération permettant d'ouvrir directement le dossier de destination dans l'explorateur de fichiers Windows.

---

## 📥 Format des fichiers d'entrée & Séquence d'acquisition

### Format des fichiers bruts
Les fichiers produits par l'instrument d'imagerie sont nommés de façon linéaire et séquentielle :
```text
Tile000001.tif
Tile000002.tif
Tile000003.tif
...
```
*(Extensions prises en charge : `.tif`, `.tiff`, `.TIF`, `.TIFF`)*

### Correspondance sur la plaque 96 puits
Chaque image brute correspond à :
- Un **Puits (`P`)** sur la microplaque 96 puits, caractérisé par une **Ligne (`L`)** allant de `A` à `H` et une **Colonne (`C`)** allant de `1` à `12` (ex. `A01`, `B03`, `H12`).
- Une **Longueur d'onde (`W`)** (canal d'acquisition), allant de `W1` à `W[nb_longueurs_onde]`.
- Un **Champ de vision (`S`)** (*Site / Field*) à l'intérieur de ce puits, allant de `S1` à `S[nb_champs]`.

### Ordre de la séquence d'acquisition
L'instrument nomme les images linéairement selon l'ordonnancement précis suivant :
1. **Point de départ** : Il commence par le premier champ (`S1`) du puits de départ (par défaut puits 1 sur la ligne `A` et colonne `1`, soit `A01`) dans la première longueur d'onde (`W1`).
2. **Acquisition des champs** : Il effectue ensuite le champ suivant (`S2`), puis `S3`, jusqu'au dernier champ prévu pour ce puits.
3. **Passage aux longueurs d'onde suivantes** : Quand le dernier champ de ce puits est fait, il passe à la seconde longueur d'onde (`W2`) et reprend l'acquisition des champs (`S1`, `S2`...).
4. **Passage au puits suivant** : Quand toutes les longueurs d'onde de ce puits sont faites, il passe au puits suivant sur la même ligne (colonne `2`, ex. `A02`), et ainsi de suite.
5. **Passage à la ligne suivante** : Quand il termine le dernier puits en colonne `12` de la ligne `A` (`A12`), il passe au premier puits de la ligne suivante (colonne `1` de la ligne `B`, soit `B01`), et ainsi de suite.
6. **Fin de plaque** : Ce balayage se poursuit de manière continue jusqu'au dernier puits de la plaque (`H12`) ou jusqu'à ce que la totalité des images disponibles soit traitée.

---

## 🏷️ Nomenclature des fichiers générés

Le nom de chaque fichier de sortie respecte le format standardisé suivant :

```text
[NomProjet]-[Puits]-[Colonne]-[Ligne]-S[Champ]-W[LongueurDOnde].[EXT]
```

### Exemple :
Pour un projet nommé `Experience_01`, le 2ᵉ champ et la 1ʳᵉ longueur d'onde du puits **B03** donneront :
```text
Experience_01-B03-03-B-S2-W1.TIFF
```

### Détail des composantes :
- **`[NomProjet]`** : Nom du projet ou de la manipulation (ex. `Exp01`, `Screening_HeLa`).
- **`[Puits]`** : Coordonnée standardisée sur la plaque 96 puits (de `A01` à `H12`).
- **`[Colonne]`** : Numéro de colonne sur 2 chiffres (de `01` à `12`).
- **`[Ligne]`** : Lettre de la ligne (de `A` à `H`).
- **`S[Champ]`** : Numéro du champ de vision (*Site / Field*), de `S1` à `S[nb_champs]`.
- **`W[LongueurDOnde]`** : Numéro du canal / longueur d'onde (*Wavelength*), de `W1` à `W[nb_longueurs_onde]`.
- **`.[EXT]`** : Extension d'origine conservée en majuscules (ex. `.TIFF`).

---

## 🚀 Installation & Utilisation

### Prérequis
- **Python 3.8+**
- Bibliothèque Python :
  ```bash
  pip install customtkinter
  ```

### Lancement de l'application
Exécutez simplement le script principal :
```bash
python app.py
```

### Utilisation pas-à-pas
1. **Dossier Source** : Cliquez sur *Parcourir...* pour sélectionner le dossier contenant vos images TIFF brutes. Le compteur affiche instantanément le nombre de fichiers détectés.
2. **Dossier Destination** : Sélectionnez le dossier où seront copiées et renommées les images.
3. **Paramètres** :
   - Renseignez le **Nom du projet**.
   - Indiquez le **Puits de départ** (ex: `A01`).
   - Saisissez le **Nombre de champs** par puits.
   - Saisissez le **Nombre de longueurs d'onde**.
4. **Lancement** : Cliquez sur **🚀 Lancer le traitement**.
5. Une fois terminé, une fenêtre de confirmation s'affiche et vous propose d'ouvrir directement le dossier de destination pour vérifier les images et consulter `rapport_renommage.txt`.

---

## 📦 Compilation en Exécutable Autonome (.exe)

L'application peut être compilée sous forme d'exécutable autonome pour Windows sans nécessiter l'installation préalable de Python :

```bash
pip install pyinstaller
pyinstaller PlateArrangers.spec
```

L'exécutable généré sera disponible dans le dossier `dist/PlateArrangers/` ou `dist/PlateArrangers.exe`.

---

## 📂 Structure du Projet

```text
PlateArrangers/
├── app.py                   # Interface graphique CustomTkinter et point d'entrée
├── generateur_plaques.py    # Module autonome / script de renommage en ligne de commande
├── PlateArrangers.spec      # Fichier de configuration PyInstaller pour la compilation
├── CHANGELOG.md             # Historique des versions et changements
└── README.md                # Documentation du projet
```
