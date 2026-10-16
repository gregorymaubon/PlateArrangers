import os
import shutil
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from i18n import I18nManager

# Set CustomTkinter theme and color options
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"


def renommer_plaques(dossier_source, dossier_destination, nom_projet, nb_champs, nb_longueurs_onde, puits_depart="A01", tr=None):
    """
    Fonction de renommage d'images de plaques 96 puits avec support de l'internationalisation.
    """
    if tr is None:
        tr = I18nManager().tr

    # 1. Collecter et trier les fichiers TIFF
    extensions = ('.tif', '.tiff', '.TIF', '.TIFF')
    if not os.path.exists(dossier_source):
        return False, tr("ERR_SOURCE_NOT_FOUND")

    fichiers_sources = sorted([f for f in os.listdir(dossier_source) if f.endswith(extensions)])
    
    total_images_disponibles = len(fichiers_sources)
    if total_images_disponibles == 0:
        return False, tr("ERR_NO_TIFF_FOUND")

    # 2. Préparer les structures de la plaque 96 puits
    lignes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    colonnes = range(1, 13)
    
    # Valider et décoder le puits de départ (ex: "C04" -> ligne 'C', colonne 4)
    puits_depart = puits_depart.strip().upper()
    if len(puits_depart) < 2 or puits_depart[0] not in lignes or not puits_depart[1:].isdigit():
        return False, tr("ERR_START_WELL_FORMAT")
        
    lig_start = puits_depart[0]
    col_start = int(puits_depart[1:])
    if col_start < 1 or col_start > 12:
        return False, tr("ERR_START_WELL_COL")
    
    os.makedirs(dossier_destination, exist_ok=True)
    
    index_fichier = 0
    commence_a_traiter = False
    historique_renommage = []

    # 3. Parcours de la plaque
    for l in lignes:
        for c in colonnes:
            puits_actuel = f"{l}{c:02d}"
            
            # Vérifier si on a atteint le puits de départ
            if not commence_a_traiter:
                if l == lig_start and c == col_start:
                    commence_a_traiter = True
                else:
                    continue  # On saute ce puits
            
            # Boucles imbriquées : Longueurs d'onde puis Champs
            for w in range(1, nb_longueurs_onde + 1):
                for s in range(1, nb_champs + 1):
                    
                    # ARRÊT AUTOMATIQUE : Si plus aucun fichier physique n'est disponible
                    if index_fichier >= total_images_disponibles:
                        break
                    
                    ancien_nom = fichiers_sources[index_fichier]
                    chemin_source = os.path.join(dossier_source, ancien_nom)
                    
                    # Extension d'origine
                    ext = os.path.splitext(ancien_nom)[1]
                    if not ext.isupper():
                        ext = ext.upper()
                    
                    # Construction du nouveau nom : [nom]-[P]-[C]-[L]-[S]-[W].TIFF
                    nouveau_nom = f"{nom_projet}-{puits_actuel}-{c:02d}-{l}-S{s}-W{w}{ext}"
                    chemin_dest = os.path.join(dossier_destination, nouveau_nom)
                    
                    # Copie physique du fichier
                    shutil.copy2(chemin_source, chemin_dest)
                    
                    # Sauvegarde pour le rapport final
                    historique_renommage.append((ancien_nom, nouveau_nom))
                    index_fichier += 1
                    
                if index_fichier >= total_images_disponibles:
                    break
            if index_fichier >= total_images_disponibles:
                break
        if index_fichier >= total_images_disponibles:
            break

    # 4. Création du fichier rapport_renommage.txt
    chemin_rapport = os.path.join(dossier_destination, "rapport_renommage.txt")
    col_old = tr("REPORT_COL_OLD")
    col_new = tr("REPORT_COL_NEW")

    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"{tr('REPORT_TITLE')}\n")
        f.write(f"{tr('REPORT_PROJECT', project=nom_projet)}\n")
        f.write(f"{tr('REPORT_IMAGES_DETECTED', count=total_images_disponibles)}\n")
        f.write(f"{tr('REPORT_IMAGES_PROCESSED', count=len(historique_renommage))}\n")
        f.write(f"{tr('REPORT_START_WELL', well=puits_depart)}\n")
        f.write(f"{tr('REPORT_CONFIG', fields=nb_champs, wavelengths=nb_longueurs_onde)}\n\n")
        f.write(f"{col_old:<35} | {col_new:<55}\n")
        f.write("-" * 93 + "\n")
        for ancien, nouveau in historique_renommage:
            f.write(f"{ancien:<35} | {nouveau:<55}\n")

    msg = tr("MSG_SUCCESS_SUMMARY", count=len(historique_renommage), path=chemin_rapport)
    return True, msg


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialisation du gestionnaire de langues
        self.i18n = I18nManager()

        self.title(self.i18n.tr("WINDOW_TITLE"))
        self.geometry("820x680")
        self.minsize(740, 620)

        # Configure grid expansion
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main scrollable or centered container frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.i18n.tr("HEADER_TITLE"),
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text=self.i18n.tr("HEADER_SUBTITLE"),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Top right controls (Sélecteur de langue + Sélecteur de thème)
        self.header_controls = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_controls.grid(row=0, column=1, rowspan=2, sticky="e")

        # Sélecteur de langue
        available_langs = self.i18n.get_available_languages()
        self.lang_menu = ctk.CTkOptionMenu(
            self.header_controls,
            values=available_langs,
            command=self.changer_langue,
            width=115
        )
        self.lang_menu.grid(row=0, column=0, padx=(0, 10))
        self.lang_menu.set(self.i18n.current_language)

        # Sélecteur de thème
        self.current_theme_mode = "System"
        self.theme_map_to_mode = {
            self.i18n.tr("THEME_SYSTEM"): "System",
            self.i18n.tr("THEME_DARK"): "Dark",
            self.i18n.tr("THEME_LIGHT"): "Light",
            "System": "System",
            "Dark": "Dark",
            "Light": "Light"
        }
        self.theme_menu = ctk.CTkOptionMenu(
            self.header_controls,
            values=[self.i18n.tr("THEME_SYSTEM"), self.i18n.tr("THEME_DARK"), self.i18n.tr("THEME_LIGHT")],
            command=self.changer_theme,
            width=105
        )
        self.theme_menu.grid(row=0, column=1)
        self.theme_menu.set(self.i18n.tr("THEME_SYSTEM"))

        # Separator
        self.sep1 = ctk.CTkFrame(self.main_frame, height=2, fg_color=("gray80", "gray30"))
        self.sep1.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # --- SECTION 1: DOSSIERS SOURCE ET DESTINATION ---
        self.folders_card = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.folders_card.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.folders_card.grid_columnconfigure(1, weight=1)

        # Section title
        self.folders_title = ctk.CTkLabel(
            self.folders_card,
            text=self.i18n.tr("SECTION_FOLDERS_TITLE"),
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.folders_title.grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 8), sticky="w")

        # Dossier Source
        self.lbl_source = ctk.CTkLabel(self.folders_card, text=self.i18n.tr("LBL_SOURCE"), font=ctk.CTkFont(weight="bold"))
        self.lbl_source.grid(row=1, column=0, padx=15, pady=8, sticky="w")

        self.entry_source = ctk.CTkEntry(self.folders_card, placeholder_text=self.i18n.tr("PLACEHOLDER_SOURCE"))
        self.entry_source.grid(row=1, column=1, padx=(5, 10), pady=8, sticky="ew")
        self.entry_source.bind("<KeyRelease>", lambda e: self.actualiser_compteur_images())

        self.btn_browse_source = ctk.CTkButton(
            self.folders_card,
            text=self.i18n.tr("BTN_BROWSE"),
            width=100,
            command=self.parcourir_source
        )
        self.btn_browse_source.grid(row=1, column=2, padx=(0, 15), pady=8)

        # Dossier Destination
        self.lbl_dest = ctk.CTkLabel(self.folders_card, text=self.i18n.tr("LBL_DEST"), font=ctk.CTkFont(weight="bold"))
        self.lbl_dest.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")

        self.entry_dest = ctk.CTkEntry(self.folders_card, placeholder_text=self.i18n.tr("PLACEHOLDER_DEST"))
        self.entry_dest.grid(row=2, column=1, padx=(5, 10), pady=(0, 15), sticky="ew")

        self.btn_browse_dest = ctk.CTkButton(
            self.folders_card,
            text=self.i18n.tr("BTN_BROWSE"),
            width=100,
            command=self.parcourir_destination
        )
        self.btn_browse_dest.grid(row=2, column=2, padx=(0, 15), pady=(0, 15))

        # --- STATS BADGE (DYNAMIC IMAGE COUNT) ---
        self.badge_frame = ctk.CTkFrame(self.main_frame, fg_color=("gray90", "#1E293B"), corner_radius=8)
        self.badge_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.badge_frame.grid_columnconfigure(0, weight=1)

        self.lbl_count = ctk.CTkLabel(
            self.badge_frame,
            text=self.i18n.tr("LBL_COUNT", count=0),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1D4ED8", "#60A5FA")
        )
        self.lbl_count.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # --- SECTION 2: PARAMÈTRES DU RENOMMAGE ---
        self.params_card = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.params_card.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.params_card.grid_columnconfigure((1, 3), weight=1)

        self.params_title = ctk.CTkLabel(
            self.params_card,
            text=self.i18n.tr("SECTION_PARAMS_TITLE"),
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.params_title.grid(row=0, column=0, columnspan=4, padx=15, pady=(12, 10), sticky="w")

        # Nom du projet
        self.lbl_nom_projet = ctk.CTkLabel(self.params_card, text=self.i18n.tr("LBL_PROJECT_NAME"))
        self.lbl_nom_projet.grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")

        self.entry_nom_projet = ctk.CTkEntry(self.params_card, placeholder_text=self.i18n.tr("PLACEHOLDER_PROJECT_NAME"))
        self.entry_nom_projet.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="ew")

        # Puits de départ (défaut A01)
        self.lbl_puits = ctk.CTkLabel(self.params_card, text=self.i18n.tr("LBL_START_WELL"))
        self.lbl_puits.grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")

        self.entry_puits = ctk.CTkEntry(self.params_card, placeholder_text=self.i18n.tr("PLACEHOLDER_START_WELL"))
        self.entry_puits.insert(0, "A01")
        self.entry_puits.grid(row=1, column=3, padx=(0, 15), pady=8, sticky="ew")

        # Nombre de champs
        self.lbl_champs = ctk.CTkLabel(self.params_card, text=self.i18n.tr("LBL_FIELDS"))
        self.lbl_champs.grid(row=2, column=0, padx=(15, 5), pady=(0, 15), sticky="w")

        self.entry_champs = ctk.CTkEntry(self.params_card, placeholder_text=self.i18n.tr("PLACEHOLDER_FIELDS"))
        self.entry_champs.grid(row=2, column=1, padx=(0, 15), pady=(0, 15), sticky="ew")

        # Nombre de longueurs d'onde
        self.lbl_longeurs = ctk.CTkLabel(self.params_card, text=self.i18n.tr("LBL_WAVELENGTHS"))
        self.lbl_longeurs.grid(row=2, column=2, padx=(15, 5), pady=(0, 15), sticky="w")

        self.entry_longeurs = ctk.CTkEntry(self.params_card, placeholder_text=self.i18n.tr("PLACEHOLDER_WAVELENGTHS"))
        self.entry_longeurs.grid(row=2, column=3, padx=(0, 15), pady=(0, 15), sticky="ew")

        # --- STATUS & ACTION BUTTON ---
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=5, column=0, padx=20, pady=(5, 0))

        self.btn_run = ctk.CTkButton(
            self.main_frame,
            text=self.i18n.tr("BTN_RUN"),
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color=("#2563EB", "#3B82F6"),
            hover_color=("#1D4ED8", "#2563EB"),
            command=self.lancer_traitement
        )
        self.btn_run.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Synchroniser l'état initial des textes et des compteurs
        self.actualiser_compteur_images()

    def changer_langue(self, lang_name):
        """Change la langue active et rafraîchit immédiatement l'interface."""
        self.i18n.set_language(lang_name)
        self.actualiser_textes_ui()

    def changer_theme(self, mode_texte):
        """Change le mode d'apparence (Système, Sombre, Clair)."""
        mode = self.theme_map_to_mode.get(mode_texte, "System")
        self.current_theme_mode = mode
        ctk.set_appearance_mode(mode)

    def actualiser_textes_ui(self):
        """Met à jour l'ensemble des textes affichés dans l'interface graphique."""
        tr = self.i18n.tr

        # Fenêtre et En-tête
        self.title(tr("WINDOW_TITLE"))
        self.title_label.configure(text=tr("HEADER_TITLE"))
        self.subtitle_label.configure(text=tr("HEADER_SUBTITLE"))

        # Actualiser la liste des langues dans le menu déroulant
        available_langs = self.i18n.get_available_languages()
        self.lang_menu.configure(values=available_langs)
        if self.i18n.current_language in available_langs:
            self.lang_menu.set(self.i18n.current_language)

        # Actualiser le menu du thème
        self.theme_map_to_mode = {
            tr("THEME_SYSTEM"): "System",
            tr("THEME_DARK"): "Dark",
            tr("THEME_LIGHT"): "Light",
            "System": "System",
            "Dark": "Dark",
            "Light": "Light"
        }
        self.theme_menu.configure(values=[tr("THEME_SYSTEM"), tr("THEME_DARK"), tr("THEME_LIGHT")])
        mode_to_label = {
            "System": tr("THEME_SYSTEM"),
            "Dark": tr("THEME_DARK"),
            "Light": tr("THEME_LIGHT")
        }
        self.theme_menu.set(mode_to_label.get(self.current_theme_mode, tr("THEME_SYSTEM")))

        # Section 1 : Dossiers
        self.folders_title.configure(text=tr("SECTION_FOLDERS_TITLE"))
        self.lbl_source.configure(text=tr("LBL_SOURCE"))
        self.entry_source.configure(placeholder_text=tr("PLACEHOLDER_SOURCE"))
        self.btn_browse_source.configure(text=tr("BTN_BROWSE"))
        self.lbl_dest.configure(text=tr("LBL_DEST"))
        self.entry_dest.configure(placeholder_text=tr("PLACEHOLDER_DEST"))
        self.btn_browse_dest.configure(text=tr("BTN_BROWSE"))

        # Compteur d'images
        self.actualiser_compteur_images()

        # Section 2 : Paramètres
        self.params_title.configure(text=tr("SECTION_PARAMS_TITLE"))
        self.lbl_nom_projet.configure(text=tr("LBL_PROJECT_NAME"))
        self.entry_nom_projet.configure(placeholder_text=tr("PLACEHOLDER_PROJECT_NAME"))
        self.lbl_puits.configure(text=tr("LBL_START_WELL"))
        self.entry_puits.configure(placeholder_text=tr("PLACEHOLDER_START_WELL"))
        self.lbl_champs.configure(text=tr("LBL_FIELDS"))
        self.entry_champs.configure(placeholder_text=tr("PLACEHOLDER_FIELDS"))
        self.lbl_longeurs.configure(text=tr("LBL_WAVELENGTHS"))
        self.entry_longeurs.configure(placeholder_text=tr("PLACEHOLDER_WAVELENGTHS"))

        # Bouton d'action
        self.btn_run.configure(text=tr("BTN_RUN"))

    def parcourir_source(self):
        dossier = filedialog.askdirectory(title=self.i18n.tr("DIALOG_SELECT_SOURCE_TITLE"))
        if dossier:
            self.entry_source.delete(0, tk.END)
            self.entry_source.insert(0, dossier)
            self.actualiser_compteur_images()

    def parcourir_destination(self):
        dossier = filedialog.askdirectory(title=self.i18n.tr("DIALOG_SELECT_DEST_TITLE"))
        if dossier:
            self.entry_dest.delete(0, tk.END)
            self.entry_dest.insert(0, dossier)

    def actualiser_compteur_images(self):
        dossier_source = self.entry_source.get().strip()
        count = 0
        if dossier_source and os.path.exists(dossier_source) and os.path.isdir(dossier_source):
            extensions = ('.tif', '.tiff', '.TIF', '.TIFF')
            try:
                fichiers = [f for f in os.listdir(dossier_source) if f.endswith(extensions)]
                count = len(fichiers)
            except Exception:
                count = 0

        self.lbl_count.configure(text=self.i18n.tr("LBL_COUNT", count=count))
        if count > 0:
            self.lbl_count.configure(text_color=("#16A34A", "#4ADE80"))  # Vert
        else:
            self.lbl_count.configure(text_color=("#DC2626", "#F87171"))  # Rouge

    def valider_champs(self):
        tr = self.i18n.tr
        dossier_source = self.entry_source.get().strip()
        dossier_dest = self.entry_dest.get().strip()
        nom_projet = self.entry_nom_projet.get().strip()
        puits_depart = self.entry_puits.get().strip()
        str_champs = self.entry_champs.get().strip()
        str_longeurs = self.entry_longeurs.get().strip()

        if not dossier_source or not os.path.exists(dossier_source):
            messagebox.showerror(tr("ERR_INPUT_TITLE"), tr("ERR_SOURCE_INVALID"))
            return None

        if not dossier_dest:
            messagebox.showerror(tr("ERR_INPUT_TITLE"), tr("ERR_DEST_MISSING"))
            return None

        if not nom_projet:
            messagebox.showerror(tr("ERR_INPUT_TITLE"), tr("ERR_PROJECT_MISSING"))
            return None

        if not puits_depart:
            messagebox.showerror(tr("ERR_INPUT_TITLE"), tr("ERR_START_WELL_MISSING"))
            return None

        try:
            nb_champs = int(str_champs)
            if nb_champs <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(tr("ERR_INPUT_TITLE"), tr("ERR_FIELDS_INVALID"))
            return None

        try:
            nb_longeurs = int(str_longeurs)
            if nb_longeurs <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(tr("ERR_INPUT_TITLE"), tr("ERR_WAVELENGTHS_INVALID"))
            return None

        return (dossier_source, dossier_dest, nom_projet, nb_champs, nb_longeurs, puits_depart)

    def afficher_dialogue_succes(self, message, dossier_destination):
        tr = self.i18n.tr
        popup = ctk.CTkToplevel(self)
        popup.title(tr("POPUP_SUCCESS_TITLE"))
        popup.geometry("540x270")
        popup.resizable(False, False)
        popup.grab_set()  # Rendre la boîte de dialogue modale

        # Centrer par rapport à la fenêtre principale
        popup.geometry(f"+{self.winfo_x() + 130}+{self.winfo_y() + 180}")

        lbl_icon = ctk.CTkLabel(
            popup,
            text=tr("POPUP_SUCCESS_HEADER"),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#16A34A", "#4ADE80")
        )
        lbl_icon.pack(padx=20, pady=(20, 10))

        lbl_msg = ctk.CTkLabel(
            popup,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=480,
            justify="center"
        )
        lbl_msg.pack(padx=20, pady=10)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(padx=20, pady=15, fill="x")

        def ouvrir_dossier():
            try:
                os.startfile(dossier_destination)
            except Exception as e:
                messagebox.showerror(tr("ERR_OPEN_FOLDER_TITLE"), tr("ERR_OPEN_FOLDER_MSG", error=str(e)))

        btn_open = ctk.CTkButton(
            btn_frame,
            text=tr("BTN_OPEN_DEST"),
            command=ouvrir_dossier,
            fg_color=("#16A34A", "#22C55E"),
            hover_color=("#15803D", "#16A34A")
        )
        btn_open.pack(side="left", expand=True, padx=10)

        btn_close = ctk.CTkButton(
            btn_frame,
            text=tr("BTN_CLOSE"),
            command=popup.destroy,
            width=100
        )
        btn_close.pack(side="right", expand=True, padx=10)

    def lancer_traitement(self):
        valeurs = self.valider_champs()
        if not valeurs:
            return

        dossier_source, dossier_dest, nom_projet, nb_champs, nb_longeurs, puits_depart = valeurs

        self.status_label.configure(text=self.i18n.tr("STATUS_RUNNING"), text_color=("#2563EB", "#60A5FA"))
        self.update_idletasks()

        succes, message = renommer_plaques(
            dossier_source=dossier_source,
            dossier_destination=dossier_dest,
            nom_projet=nom_projet,
            nb_champs=nb_champs,
            nb_longueurs_onde=nb_longeurs,
            puits_depart=puits_depart,
            tr=self.i18n.tr
        )

        self.status_label.configure(text="")

        if succes:
            self.afficher_dialogue_succes(message, dossier_dest)
        else:
            messagebox.showerror(self.i18n.tr("ERR_PROCESSING_TITLE"), message)


if __name__ == "__main__":
    app = App()
    app.mainloop()
