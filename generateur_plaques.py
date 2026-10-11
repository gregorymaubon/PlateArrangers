import os
import shutil

def renommer_plaques(dossier_source, dossier_destination, nom_projet, nb_champs, nb_longueurs_onde, puits_depart="A01"):
    # 1. Collecter et trier de manière stricte les fichiers TIFF
    extensions = ('.tif', '.tiff', '.TIF', '.TIFF')
    fichiers_sources = sorted([f for f in os.listdir(dossier_source) if f.endswith(extensions)])
    
    total_images_disponibles = len(fichiers_sources)
    if total_images_disponibles == 0:
        return "Erreur : Aucun fichier TIFF trouvé dans le dossier source.", 0

    # 2. Préparer les structures de la plaque 96 puits
    lignes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    colonnes = range(1, 13)
    
    # Valider et décoder le puits de départ (ex: "C04" -> ligne 'C', colonne 4)
    puits_depart = puits_depart.strip().upper()
    if len(puits_depart) < 2 or puits_depart[0] not in lignes or not puits_depart[1:].isdigit():
        return "Erreur : Format du puits de départ invalide (Ex: A01, C04).", 0
        
    lig_start = puits_depart[0]
    col_start = int(puits_depart[1:])
    
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
                    continue # On saute ce puits, l'instrument n'a pas imagé ici
            
            # Boucles imbriquées : Longueurs d'onde puis Champs
            for w in range(1, nb_longueurs_onde + 1):
                for s in range(1, nb_champs + 1):
                    
                    # ARRÊT AUTOMATIQUE : Si plus aucun fichier physique n'est disponible
                    if index_fichier >= total_images_disponibles:
                        break
                    
                    ancien_nom = fichiers_sources[index_fichier]
                    chemin_source = os.path.join(dossier_source, ancien_nom)
                    
                    # Construction du nouveau nom : [nom]-[P]-[C]-[L]-[S]-[W].TIFF
                    nouveau_nom = f"{nom_projet}-{puits_actuel}-{c:02d}-{l}-S{s}-W{w}.TIFF"
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
        f.write(f"--- RAPPORT DE RENOMMAGE ---\n")
        f.write(f"Projet : {nom_projet}\n")
        f.write(f"Images détectées dans le dossier source : {total_images_disponibles}\n")
        f.write(f"Images effectivement traitées : {len(historique_renommage)}\n")
        f.write(f"Puits de départ : {puits_depart}\n")
        f.write(f"Configuration demandée : {nb_champs} champs, {nb_longueurs_onde} longueurs d'onde\n\n")
        f.write(f"{'ANCIEN NOM':<30} | {'NOUVEAU NOM':<50}\n")
        f.write("-" * 85 + "\n")
        for ancien, nouveau in historique_renommage:
            f.write(f"{ancien:<30} | {nouveau:<50}\n")

    return f"Succès ! {len(historique_renommage)} images traitées. Rapport généré.", len(historique_renommage)