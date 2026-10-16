import os
import sys
import json
import logging

logger = logging.getLogger(__name__)

# Dictionnaire de référence en français (utilisé par défaut et en cas de clé manquante)
DEFAULT_STRINGS = {
    "LANG_NAME": "Français",
    "WINDOW_TITLE": "PlateArrangers - Renommage d'Images de Plaques 96 Puits",
    "HEADER_TITLE": "🔬 PlateArrangers - Renommage d'Images",
    "HEADER_SUBTITLE": "Organisez et renommez vos acquisitions de microplaques 96 puits facilement.",
    "THEME_SYSTEM": "Système",
    "THEME_DARK": "Sombre",
    "THEME_LIGHT": "Clair",
    "SECTION_FOLDERS_TITLE": "📁 Emplacements des Dossiers",
    "LBL_SOURCE": "Dossier Source :",
    "PLACEHOLDER_SOURCE": "Sélectionnez le dossier contenant vos images TIFF...",
    "LBL_DEST": "Dossier Destination :",
    "PLACEHOLDER_DEST": "Sélectionnez le dossier de destination...",
    "BTN_BROWSE": "Parcourir...",
    "LBL_COUNT": "Nombre d'images trouvées : {count}",
    "SECTION_PARAMS_TITLE": "⚙️ Paramètres du Renommage",
    "LBL_PROJECT_NAME": "Nom du projet :",
    "PLACEHOLDER_PROJECT_NAME": "Ex: Experience_01",
    "LBL_START_WELL": "Puits de départ :",
    "PLACEHOLDER_START_WELL": "A01",
    "LBL_FIELDS": "Nombre de champs :",
    "PLACEHOLDER_FIELDS": "Ex: 4",
    "LBL_WAVELENGTHS": "Nombre de longueurs d'onde :",
    "PLACEHOLDER_WAVELENGTHS": "Ex: 2",
    "BTN_RUN": "🚀 Lancer le traitement",
    "STATUS_RUNNING": "Traitement en cours...",
    "DIALOG_SELECT_SOURCE_TITLE": "Sélectionner le dossier source des images TIFF",
    "DIALOG_SELECT_DEST_TITLE": "Sélectionner le dossier de destination",
    "ERR_INPUT_TITLE": "Erreur de Saisie",
    "ERR_SOURCE_INVALID": "Veuillez sélectionner un dossier source valide.",
    "ERR_DEST_MISSING": "Veuillez sélectionner un dossier de destination.",
    "ERR_PROJECT_MISSING": "Veuillez indiquer un Nom de projet.",
    "ERR_START_WELL_MISSING": "Veuillez indiquer le puits de départ (par défaut A01).",
    "ERR_FIELDS_INVALID": "Le nombre de champs doit être un nombre entier positif.",
    "ERR_WAVELENGTHS_INVALID": "Le nombre de longueurs d'onde doit être un nombre entier positif.",
    "ERR_PROCESSING_TITLE": "Erreur lors du traitement",
    "ERR_SOURCE_NOT_FOUND": "Erreur : Le dossier source spécifié n'existe pas.",
    "ERR_NO_TIFF_FOUND": "Erreur : Aucun fichier TIFF (tif, tiff) trouvé dans le dossier source.",
    "ERR_START_WELL_FORMAT": "Erreur : Format du puits de départ invalide. Doit être au format A01 à H12.",
    "ERR_START_WELL_COL": "Erreur : La colonne du puits de départ doit être comprise entre 01 et 12.",
    "POPUP_SUCCESS_TITLE": "Succès du Traitement",
    "POPUP_SUCCESS_HEADER": "🎉 Traitement Terminé !",
    "MSG_SUCCESS_SUMMARY": "Succès ! {count} images traitées avec succès.\n\nLe rapport a été sauvegardé dans :\n{path}",
    "BTN_OPEN_DEST": "📂 Ouvrir le dossier destination",
    "BTN_CLOSE": "Fermer",
    "ERR_OPEN_FOLDER_TITLE": "Erreur",
    "ERR_OPEN_FOLDER_MSG": "Impossible d'ouvrir le dossier : {error}",
    "REPORT_TITLE": "--- RAPPORT DE RENOMMAGE ---",
    "REPORT_PROJECT": "Projet : {project}",
    "REPORT_IMAGES_DETECTED": "Images détectées dans le dossier source : {count}",
    "REPORT_IMAGES_PROCESSED": "Images effectivement traitées : {count}",
    "REPORT_START_WELL": "Puits de départ : {well}",
    "REPORT_CONFIG": "Configuration demandée : {fields} champs, {wavelengths} longueurs d'onde",
    "REPORT_COL_OLD": "ANCIEN NOM",
    "REPORT_COL_NEW": "NOUVEAU NOM",
}


def get_languages_directories():
    """
    Retourne la liste des dossiers susceptibles de contenir les fichiers de langues (.txt).
    Prend en compte l'exécution directe, l'environnement virtuel et le packaging PyInstaller.
    """
    directories = []
    
    # 1. Dossier 'languages' relatif au présent fichier script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories.append(os.path.join(base_dir, "languages"))
    
    # 2. Si compilé avec PyInstaller (_MEIPASS)
    if hasattr(sys, "_MEIPASS"):
        directories.append(os.path.join(sys._MEIPASS, "languages"))
        
    # 3. Dossier de l'exécutable (permet à l'utilisateur de poser un .txt à côté de l'exe)
    if hasattr(sys, "frozen") and sys.executable:
        directories.append(os.path.join(os.path.dirname(sys.executable), "languages"))
        
    # 4. Dossier de travail actuel
    cwd_lang = os.path.join(os.getcwd(), "languages")
    if cwd_lang not in directories:
        directories.append(cwd_lang)

    # Déduplication en conservant l'ordre
    unique_dirs = []
    for d in directories:
        if d not in unique_dirs:
            unique_dirs.append(d)
    return unique_dirs


def parse_language_file(file_path):
    """
    Lit un fichier texte de langue (clé = valeur) en UTF-8 (supporte BOM utf-8-sig).
    Retourne le dictionnaire des traductions et le nom d'affichage de la langue.
    """
    translations = {}
    lang_name = None
    
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                stripped = line.strip()
                # Ignorer lignes vides ou commentaires
                if not stripped or stripped.startswith("#") or stripped.startswith(";"):
                    continue
                if "=" in stripped:
                    key, val = stripped.split("=", 1)
                    key = key.strip()
                    # Remplacement des \n échappés en vrais retours à la ligne
                    val = val.strip().replace(r"\n", "\n")
                    translations[key] = val
                    if key == "LANG_NAME":
                        lang_name = val
    except Exception as e:
        logger.warning(f"Erreur lors de la lecture du fichier de langue '{file_path}': {e}")
        return None, {}

    if not lang_name:
        # Repli sur le nom de fichier sans extension
        lang_name = os.path.splitext(os.path.basename(file_path))[0].capitalize()

    return lang_name, translations


class I18nManager:
    """
    Gestionnaire d'internationalisation de PlateArrangers.
    """
    def __init__(self, default_lang="Français"):
        self.available_languages = {}  # { "Français": "/path/to/fr.txt" }
        self.translations = {}
        self.current_language = default_lang
        self.config_file = self._get_config_path()
        
        self.refresh_available_languages()
        
        # Charger la langue enregistrée ou la langue par défaut
        saved_lang = self.load_saved_preference()
        if saved_lang and saved_lang in self.available_languages:
            self.set_language(saved_lang, save_pref=False)
        else:
            self.set_language(default_lang if default_lang in self.available_languages else "Français", save_pref=False)

    def _get_config_path(self):
        """Détermine l'emplacement du fichier de configuration utilisateur."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, ".platearrangers_settings.json")
        try:
            # Vérifier si on peut écrire dans le dossier
            test_file = os.path.join(base_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("")
            os.remove(test_file)
            return config_path
        except Exception:
            # Repli sur le dossier personnel utilisateur si répertoire protégé
            home_dir = os.path.expanduser("~")
            return os.path.join(home_dir, ".platearrangers_settings.json")

    def load_saved_preference(self):
        """Récupère la langue précédemment choisie par l'utilisateur."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("language")
            except Exception:
                pass
        return None

    def save_preference(self, lang_name):
        """Enregistre la préférence de langue dans le fichier de configuration."""
        try:
            data = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            data["language"] = lang_name
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Impossible de sauvegarder la préférence de langue : {e}")

    def refresh_available_languages(self):
        """
        Scanne tous les dossiers de langues pour répertorier les fichiers .txt disponibles.
        Garantit que le français est toujours présent.
        """
        self.available_languages = {}
        for directory in get_languages_directories():
            if os.path.exists(directory) and os.path.isdir(directory):
                try:
                    for filename in os.listdir(directory):
                        if filename.lower().endswith(".txt"):
                            file_path = os.path.join(directory, filename)
                            lang_name, _ = parse_language_file(file_path)
                            if lang_name:
                                self.available_languages[lang_name] = file_path
                except Exception as e:
                    logger.warning(f"Erreur d'accès au dossier '{directory}': {e}")

        # Toujours garantir au moins 'Français'
        if "Français" not in self.available_languages:
            self.available_languages["Français"] = None

    def get_available_languages(self):
        """Retourne la liste des noms de langues disponibles."""
        self.refresh_available_languages()
        langs = list(self.available_languages.keys())
        # Mettre 'Français' en tête de liste si présent
        if "Français" in langs:
            langs.remove("Français")
            langs.insert(0, "Français")
        return langs

    def set_language(self, lang_name, save_pref=True):
        """
        Définit la langue active et charge les traductions correspondantes.
        Combine le dictionnaire de base DEFAULT_STRINGS avec les traductions chargées.
        """
        self.current_language = lang_name
        loaded_dict = {}
        file_path = self.available_languages.get(lang_name)
        
        if file_path and os.path.exists(file_path):
            _, parsed_dict = parse_language_file(file_path)
            if parsed_dict:
                loaded_dict = parsed_dict

        # Fusion : les chaînes par défaut françaises sont utilisées en cas de clé manquante
        merged = dict(DEFAULT_STRINGS)
        merged.update(loaded_dict)
        self.translations = merged

        if save_pref:
            self.save_preference(lang_name)

    def tr(self, key, **kwargs):
        """
        Traduit la clé demandée dans la langue active.
        Remplace les paramètres éventuels {param} en toute sécurité.
        """
        text = self.translations.get(key)
        if text is None:
            text = DEFAULT_STRINGS.get(key, key)

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text
