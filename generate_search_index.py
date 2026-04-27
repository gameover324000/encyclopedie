"""
generate_search_index.py
------------------------
Génère ou complète le fichier search_index.json pour la barre de recherche d'Herbarium.
- Lance sur une lettre : python generate_search_index.py Z
- Lance sur plusieurs lettres : python generate_search_index.py Z Y Q
- Lance sur toutes les lettres : python generate_search_index.py --all

Le script ajoute les nouvelles entrées sans écraser les existantes.
"""

import os
import json
import sys
import glob
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
# CONFIG — adapte ces chemins si besoin
# ══════════════════════════════════════════════

# Dossier racine du projet (là où se trouve index.html)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Dossier contenant les sous-dossiers de plantes (ex: encyclopedie/z/zabelia-biflora.html)
ENCYCLOPEDIE_DIR = os.path.join(ROOT_DIR, "encyclopedie")

# Fichier de sortie
OUTPUT_FILE = os.path.join(ROOT_DIR, "search_index.json")

# ══════════════════════════════════════════════


def extraire_donnees_plante(filepath):
    """Extrait nom scientifique, noms communs et famille depuis un fichier HTML de plante."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Nom scientifique
    h1 = soup.find("h1", class_="plant-sci-name")
    if not h1:
        return None
    nom_sci = h1.get_text(strip=True)

    # Noms communs
    common_span = soup.find("span", class_="common-list")
    noms_communs = common_span.get_text(strip=True) if common_span else ""
    # Transforme en liste si séparés par des virgules
    noms_communs_list = [n.strip() for n in noms_communs.split(",") if n.strip()] if noms_communs else []

    # Famille
    family_tag = soup.find("span", class_="plant-family-tag")
    famille = family_tag.get_text(strip=True) if family_tag else ""

    # Toxicité (badge)
    badge = soup.find("span", class_="badge")
    toxique = False
    if badge:
        texte_badge = badge.get_text(strip=True).lower()
        toxique = "toxique" in texte_badge and "non" not in texte_badge

    # URL relative depuis la racine du projet
    url_relative = os.path.relpath(filepath, ROOT_DIR).replace("\\", "/")

    return {
        "nom_scientifique": nom_sci,
        "noms_communs": noms_communs_list,
        "famille": famille,
        "toxique": toxique,
        "fichier": url_relative
    }


def charger_index_existant():
    """Charge le search_index.json existant ou retourne une liste vide."""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def sauvegarder_index(index):
    """Sauvegarde le search_index.json."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"✅ search_index.json sauvegardé ({len(index)} entrées au total)")


def traiter_lettre(lettre):
    """Traite tous les fichiers HTML d'une lettre et retourne les entrées extraites."""
    lettre = lettre.upper()
    dossier = os.path.join(ENCYCLOPEDIE_DIR, lettre)

    if not os.path.isdir(dossier):
        print(f"⚠️  Dossier introuvable : {dossier}")
        return []

    fichiers = glob.glob(os.path.join(dossier, "*.html"))
    # Exclure les fichiers index (ex: Z.html)
    fichiers = [f for f in fichiers if not os.path.basename(f).startswith("index")]

    if not fichiers:
        print(f"⚠️  Aucun fichier HTML trouvé dans {dossier}")
        return []

    print(f"📂 Lettre {lettre} : {len(fichiers)} fichiers trouvés")
    resultats = []
    erreurs = 0

    for filepath in fichiers:
        try:
            donnees = extraire_donnees_plante(filepath)
            if donnees:
                resultats.append(donnees)
        except Exception as e:
            print(f"   ❌ Erreur sur {os.path.basename(filepath)} : {e}")
            erreurs += 1

    print(f"   ✔ {len(resultats)} plantes extraites, {erreurs} erreurs")
    return resultats


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_search_index.py Z")
        print("  python generate_search_index.py Z Y Q")
        print("  python generate_search_index.py --all")
        sys.exit(1)

    # Déterminer les lettres à traiter
    if sys.argv[1] == "--all":
        lettres = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    else:
        lettres = [l.upper() for l in sys.argv[1:]]

    # Charger l'index existant
    index = charger_index_existant()
    print(f"📖 Index existant : {len(index)} entrées")

    # Construire un set des fichiers déjà indexés pour éviter les doublons
    fichiers_existants = {entree["fichier"] for entree in index}

    # Traiter chaque lettre
    nouvelles_entrees = 0
    for lettre in lettres:
        entrees = traiter_lettre(lettre)
        for entree in entrees:
            if entree["fichier"] not in fichiers_existants:
                index.append(entree)
                fichiers_existants.add(entree["fichier"])
                nouvelles_entrees += 1

    print(f"\n🌿 {nouvelles_entrees} nouvelles plantes ajoutées à l'index")

    # Trier par nom scientifique
    index.sort(key=lambda x: x["nom_scientifique"].lower())

    # Sauvegarder
    sauvegarder_index(index)


if __name__ == "__main__":
    main()
