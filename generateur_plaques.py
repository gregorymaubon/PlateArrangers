import os
import shutil
from i18n import I18nManager


def renommer_plaques(dossier_source, dossier_destination, nom_projet, nb_champs, nb_longueurs_onde, puits_depart="A01", tr=None):
    """
    Module autonome de renommage d'images de plaques 96 puits avec support de l'internationalisation.
    """
    if tr is None:
        tr = I18nManager().tr

    # 1. Collecter et trier de manière stricte les fichiers TIFF
    extensions = ('.tif', '.tiff', '.TIF', '.TIFF')
    if not os.path.exists(dossier_source):
        return tr("ERR_SOURCE_NOT_FOUND"), 0

    fichiers_sources = sorted([f for f in os.listdir(dossier_source) if f.endswith(extensions)])
    
    total_images_disponibles = len(fichiers_sources)
    if total_images_disponibles == 0:
        return tr("ERR_NO_TIFF_FOUND"), 0

    # 2. Préparer les structures de la plaque 96 puits
    lignes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    colonnes = range(1, 13)
    
    # Valider et décoder le puits de départ (ex: "C04" -> ligne 'C', colonne 4)
    puits_depart = puits_depart.strip().upper()
    if len(puits_depart) < 2 or puits_depart[0] not in lignes or not puits_depart[1:].isdigit():
        return tr("ERR_START_WELL_FORMAT"), 0
        
    lig_start = puits_depart[0]
    col_start = int(puits_depart[1:])
    if col_start < 1 or col_start > 12:
        return tr("ERR_START_WELL_COL"), 0
    
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
                    continue  # On saute ce puits, l'instrument n'a pas imagé ici
            
            # Boucles imbriquées : Longueurs d'onde puis Champs
            for w in range(1, nb_longueurs_onde + 1):
                for s in range(1, nb_champs + 1):
                    
                    # ARRÊT AUTOMATIQUE : Si plus aucun fichier physique n'est disponible
                    if index_fichier >= total_images_disponibles:
                        break
                    
                    ancien_nom = fichiers_sources[index_fichier]
                    chemin_source = os.path.join(dossier_source, ancien_nom)
                    
                    # Construction du nouveau nom : [nom]-[P]-[C]-[L]-[S]-[W].TIFF
                    ext = os.path.splitext(ancien_nom)[1]
                    if not ext.isupper():
                        ext = ext.upper()
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

    # 4. Création du fichier rapport.txt
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
        f.write(f"{col_old:<30} | {col_new:<50}\n")
        f.write("-" * 85 + "\n")
        for ancien, nouveau in historique_renommage:
            f.write(f"{ancien:<30} | {nouveau:<50}\n")

    msg = tr("MSG_SUCCESS_SUMMARY", count=len(historique_renommage), path=chemin_rapport)
    return msg, len(historique_renommage)