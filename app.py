import os
import shutil
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Set CustomTkinter theme and color options
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"


def renommer_plaques(dossier_source, dossier_destination, nom_projet, nb_champs, nb_longueurs_onde, puits_depart="A01"):
    """
    Fonction de renommage d'images de plaques 96 puits.
    """
    # 1. Collecter et trier les fichiers TIFF
    extensions = ('.tif', '.tiff', '.TIF', '.TIFF')
    if not os.path.exists(dossier_source):
        return False, "Erreur : Le dossier source spécifié n'existe pas."

    fichiers_sources = sorted([f for f in os.listdir(dossier_source) if f.endswith(extensions)])
    
    total_images_disponibles = len(fichiers_sources)
    if total_images_disponibles == 0:
        return False, "Erreur : Aucun fichier TIFF (tif, tiff) trouvé dans le dossier source."

    # 2. Préparer les structures de la plaque 96 puits
    lignes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    colonnes = range(1, 13)
    
    # Valider et décoder le puits de départ (ex: "C04" -> ligne 'C', colonne 4)
    puits_depart = puits_depart.strip().upper()
    if len(puits_depart) < 2 or puits_depart[0] not in lignes or not puits_depart[1:].isdigit():
        return False, "Erreur : Format du puits de départ invalide. Doit être au format A01 à H12."
        
    lig_start = puits_depart[0]
    col_start = int(puits_depart[1:])
    if col_start < 1 or col_start > 12:
        return False, "Erreur : La colonne du puits de départ doit être comprise entre 01 et 12."
    
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
                    continue # On saute ce puits
            
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
                    
                if index_fichier >= total_images_disponibles: break
            if index_fichier >= total_images_disponibles: break
        if index_fichier >= total_images_disponibles: break

    # 4. Création du fichier rapport.txt
    chemin_rapport = os.path.join(dossier_destination, "rapport_renommage.txt")
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write("--- RAPPORT DE RENOMMAGE ---\n")
        f.write(f"Projet : {nom_projet}\n")
        f.write(f"Images détectées dans le dossier source : {total_images_disponibles}\n")
        f.write(f"Images effectivement traitées : {len(historique_renommage)}\n")
        f.write(f"Puits de départ : {puits_depart}\n")
        f.write(f"Configuration demandée : {nb_champs} champs, {nb_longueurs_onde} longueurs d'onde\n\n")
        f.write(f"{'ANCIEN NOM':<35} | {'NOUVEAU NOM':<55}\n")
        f.write("-" * 93 + "\n")
        for ancien, nouveau in historique_renommage:
            f.write(f"{ancien:<35} | {nouveau:<55}\n")

    msg = f"Succès ! {len(historique_renommage)} images traitées avec succès.\n\nLe rapport a été sauvegardé dans :\n{chemin_rapport}"
    return True, msg


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PlateArrangers - Renommage d'Images de Plaques 96 Puits")
        self.geometry("780x680")
        self.minsize(720, 620)

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

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🔬 PlateArrangers - Renommage d'Images",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Organisez et renommez vos acquisitions de microplaques 96 puits facilement.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Appearance mode selector top right
        self.theme_menu = ctk.CTkOptionMenu(
            self.header_frame,
            values=["System", "Dark", "Light"],
            command=self.changer_theme,
            width=100
        )
        self.theme_menu.grid(row=0, column=1, rowspan=2, sticky="e")
        self.theme_menu.set("System")

        # Separator
        self.sep1 = ctk.CTkFrame(self.main_frame, height=2, fg_color=("gray80", "gray30"))
        self.sep1.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # --- SECTION 1: DOSSIERS SOURCE ET DESTINATION ---
        self.folders_frame = ctk.CTkCTkFrame if hasattr(ctk, 'CTkCTkFrame') else ctk.CTkFrame
        self.folders_card = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.folders_card.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.folders_card.grid_columnconfigure(1, weight=1)

        # Section title
        self.folders_title = ctk.CTkLabel(
            self.folders_card,
            text="📁 Emplacements des Dossiers",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.folders_title.grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 8), sticky="w")

        # Dossier Source
        self.lbl_source = ctk.CTkLabel(self.folders_card, text="Dossier Source :", font=ctk.CTkFont(weight="bold"))
        self.lbl_source.grid(row=1, column=0, padx=15, pady=8, sticky="w")

        self.entry_source = ctk.CTkEntry(self.folders_card, placeholder_text="Sélectionnez le dossier contenant vos images TIFF...")
        self.entry_source.grid(row=1, column=1, padx=(5, 10), pady=8, sticky="ew")
        self.entry_source.bind("<KeyRelease>", lambda e: self.actualiser_compteur_images())

        self.btn_browse_source = ctk.CTkButton(
            self.folders_card,
            text="Parcourir...",
            width=100,
            command=self.parcourir_source
        )
        self.btn_browse_source.grid(row=1, column=2, padx=(0, 15), pady=8)

        # Dossier Destination
        self.lbl_dest = ctk.CTkLabel(self.folders_card, text="Dossier Destination :", font=ctk.CTkFont(weight="bold"))
        self.lbl_dest.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")

        self.entry_dest = ctk.CTkEntry(self.folders_card, placeholder_text="Sélectionnez le dossier de destination...")
        self.entry_dest.grid(row=2, column=1, padx=(5, 10), pady=(0, 15), sticky="ew")

        self.btn_browse_dest = ctk.CTkButton(
            self.folders_card,
            text="Parcourir...",
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
            text="Nombre d'images trouvées : 0",
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
            text="⚙️ Paramètres du Renommage",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.params_title.grid(row=0, column=0, columnspan=4, padx=15, pady=(12, 10), sticky="w")

        # Nom du projet
        self.lbl_nom_projet = ctk.CTkLabel(self.params_card, text="Nom du projet :")
        self.lbl_nom_projet.grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")

        self.entry_nom_projet = ctk.CTkEntry(self.params_card, placeholder_text="Ex: Experience_01")
        self.entry_nom_projet.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="ew")

        # Puits de départ (défaut A01)
        self.lbl_puits = ctk.CTkLabel(self.params_card, text="Puits de départ :")
        self.lbl_puits.grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")

        self.entry_puits = ctk.CTkEntry(self.params_card, placeholder_text="A01")
        self.entry_puits.insert(0, "A01")
        self.entry_puits.grid(row=1, column=3, padx=(0, 15), pady=8, sticky="ew")

        # Nombre de champs
        self.lbl_champs = ctk.CTkLabel(self.params_card, text="Nombre de champs :")
        self.lbl_champs.grid(row=2, column=0, padx=(15, 5), pady=(0, 15), sticky="w")

        self.entry_champs = ctk.CTkEntry(self.params_card, placeholder_text="Ex: 4")
        self.entry_champs.grid(row=2, column=1, padx=(0, 15), pady=(0, 15), sticky="ew")

        # Nombre de longueurs d'onde
        self.lbl_longeurs = ctk.CTkLabel(self.params_card, text="Nombre de longueurs d'onde :")
        self.lbl_longeurs.grid(row=2, column=2, padx=(15, 5), pady=(0, 15), sticky="w")

        self.entry_longeurs = ctk.CTkEntry(self.params_card, placeholder_text="Ex: 2")
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
            text="🚀 Lancer le traitement",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color=("#2563EB", "#3B82F6"),
            hover_color=("#1D4ED8", "#2563EB"),
            command=self.lancer_traitement
        )
        self.btn_run.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Initial check for source image count
        self.actualiser_compteur_images()

    def changer_theme(self, mode):
        ctk.set_appearance_mode(mode)

    def parcourir_source(self):
        dossier = filedialog.askdirectory(title="Sélectionner le dossier source des images TIFF")
        if dossier:
            self.entry_source.delete(0, tk.END)
            self.entry_source.insert(0, dossier)
            self.actualiser_compteur_images()

    def parcourir_destination(self):
        dossier = filedialog.askdirectory(title="Sélectionner le dossier de destination")
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

        self.lbl_count.configure(text=f"Nombre d'images trouvées : {count}")
        if count > 0:
            self.lbl_count.configure(text_color=("#16A34A", "#4ADE80"))  # Green when files found
        else:
            self.lbl_count.configure(text_color=("#DC2626", "#F87171"))  # Red when 0 files

    def valider_champs(self):
        dossier_source = self.entry_source.get().strip()
        dossier_dest = self.entry_dest.get().strip()
        nom_projet = self.entry_nom_projet.get().strip()
        puits_depart = self.entry_puits.get().strip()
        str_champs = self.entry_champs.get().strip()
        str_longeurs = self.entry_longeurs.get().strip()

        if not dossier_source or not os.path.exists(dossier_source):
            messagebox.showerror("Erreur de Saisie", "Veuillez sélectionner un dossier source valide.")
            return None

        if not dossier_dest:
            messagebox.showerror("Erreur de Saisie", "Veuillez sélectionner un dossier de destination.")
            return None

        if not nom_projet:
            messagebox.showerror("Erreur de Saisie", "Veuillez indiquer un Nom de projet.")
            return None

        if not puits_depart:
            messagebox.showerror("Erreur de Saisie", "Veuillez indiquer le puits de départ (par défaut A01).")
            return None

        try:
            nb_champs = int(str_champs)
            if nb_champs <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Erreur de Saisie", "Le nombre de champs doit être un nombre entier positif.")
            return None

        try:
            nb_longeurs = int(str_longeurs)
            if nb_longeurs <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Erreur de Saisie", "Le nombre de longueurs d'onde doit être un nombre entier positif.")
            return None

        return (dossier_source, dossier_dest, nom_projet, nb_champs, nb_longeurs, puits_depart)

    def afficher_dialogue_succes(self, message, dossier_destination):
        popup = ctk.CTkToplevel(self)
        popup.title("Succès du Traitement")
        popup.geometry("520x260")
        popup.resizable(False, False)
        popup.grab_set()  # Make window modal

        # Center popup relative to main window
        popup.geometry(f"+{self.winfo_x() + 130}+{self.winfo_y() + 180}")

        lbl_icon = ctk.CTkLabel(
            popup,
            text="🎉 Traitement Terminé !",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#16A34A", "#4ADE80")
        )
        lbl_icon.pack(padx=20, pady=(20, 10))

        lbl_msg = ctk.CTkLabel(
            popup,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=460,
            justify="center"
        )
        lbl_msg.pack(padx=20, pady=10)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(padx=20, pady=15, fill="x")

        def ouvrir_dossier():
            try:
                os.startfile(dossier_destination)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier : {e}")

        btn_open = ctk.CTkButton(
            btn_frame,
            text="📂 Ouvrir le dossier destination",
            command=ouvrir_dossier,
            fg_color=("#16A34A", "#22C55E"),
            hover_color=("#15803D", "#16A34A")
        )
        btn_open.pack(side="left", expand=True, padx=10)

        btn_close = ctk.CTkButton(
            btn_frame,
            text="Fermer",
            command=popup.destroy,
            width=100
        )
        btn_close.pack(side="right", expand=True, padx=10)

    def lancer_traitement(self):
        valeurs = self.valider_champs()
        if not valeurs:
            return

        dossier_source, dossier_dest, nom_projet, nb_champs, nb_longeurs, puits_depart = valeurs

        self.status_label.configure(text="Traitement en cours...", text_color=("#2563EB", "#60A5FA"))
        self.update_idletasks()

        succes, message = renommer_plaques(
            dossier_source=dossier_source,
            dossier_destination=dossier_dest,
            nom_projet=nom_projet,
            nb_champs=nb_champs,
            nb_longueurs_onde=nb_longeurs,
            puits_depart=puits_depart
        )

        self.status_label.configure(text="")

        if succes:
            self.afficher_dialogue_succes(message, dossier_dest)
        else:
            messagebox.showerror("Erreur lors du traitement", message)


if __name__ == "__main__":
    app = App()
    app.mainloop()
