#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herbarium — Analyse des usages par catégorie dans un dossier lettre
Parcourt tous les fichiers HTML du dossier et génère un rapport .txt
listant pour chaque catégorie (Thés, Remèdes, Culinaires, Cosmétiques)
les usages uniques et les plantes associées.

Usage :
    python analyse_lettre.py <chemin_dossier_lettre>
    python analyse_lettre.py ./A_Plante_page

Génère un fichier : analyse_<LETTRE>_<DATE>.txt  (dans le dossier analysé)
"""

import os
import sys
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

CATEGORIES = {
    "thes_tisanes": {
        "label"      : "Thés & Tisanes",
        "section_id" : "thes-tisanes",
        "card_class" : "tea-card",
        "titre_tag"  : "h3",
        "titre_class": "tea-name",
    },
    "remedes": {
        "label"      : "Remèdes & Soins",
        "section_id" : "remedes-soins",
        "card_class" : "usage-card--remedy",
        "titre_tag"  : "h3",
        "titre_class": "usage-name",
    },
    "culinaires": {
        "label"      : "Culinaires",
        "section_id" : "culinaires",
        "card_class" : "usage-card--culinary",
        "titre_tag"  : "h3",
        "titre_class": "usage-name",
    },
    "cosmetiques": {
        "label"      : "Cosmétiques",
        "section_id" : "cosmetiques",
        "card_class" : "usage-card--cosmetic",
        "titre_tag"  : "h3",
        "titre_class": "usage-name",
    },
}

# ══════════════════════════════════════════════
#  LECTURE DES FICHIERS HTML
# ══════════════════════════════════════════════

def get_nom_plante(soup):
    """Récupère le nom scientifique depuis <h1 class='plant-sci-name'>."""
    tag = soup.find("h1", class_="plant-sci-name")
    if tag:
        return tag.get_text(strip=True)
    title = soup.find("title")
    if title:
        return title.get_text(strip=True).split("—")[0].strip()
    return "Plante inconnue"


def extraire_usages(soup, config):
    """
    Retourne la liste des titres d'usages trouvés dans la section.
    Cherche d'abord par section_id, puis directement par card_class (fallback).
    """
    usages = []

    section = soup.find(id=config["section_id"])
    if section:
        for carte in section.find_all(class_=config["card_class"]):
            titre = carte.find(config["titre_tag"], class_=config["titre_class"])
            if titre:
                usages.append(titre.get_text(strip=True))

    if not usages:
        for carte in soup.find_all(class_=config["card_class"]):
            titre = carte.find(config["titre_tag"], class_=config["titre_class"])
            if titre:
                usages.append(titre.get_text(strip=True))

    return usages


def analyser_fichier(chemin_html):
    """Analyse un fichier HTML et retourne ses données de plante."""
    with open(chemin_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    return {
        "nom"       : get_nom_plante(soup),
        "fichier"   : os.path.basename(chemin_html),
        "categories": {
            cle: extraire_usages(soup, config)
            for cle, config in CATEGORIES.items()
        }
    }

# ══════════════════════════════════════════════
#  ANALYSE DU DOSSIER
# ══════════════════════════════════════════════

def analyser_dossier(chemin_dossier):
    """Parcourt tous les .html du dossier et retourne la liste des résultats."""
    fichiers_html = sorted([
        f for f in os.listdir(chemin_dossier)
        if f.endswith(".html")
    ])

    if not fichiers_html:
        print(f"  ⚠  Aucun fichier HTML trouvé dans : {chemin_dossier}")
        return []

    resultats = []
    for nom_fichier in fichiers_html:
        chemin = os.path.join(chemin_dossier, nom_fichier)
        try:
            r = analyser_fichier(chemin)
            resultats.append(r)
            print(f"  ✓  {r['nom']}")
        except Exception as e:
            print(f"  ✗  Erreur sur {nom_fichier} : {e}")

    return resultats

# ══════════════════════════════════════════════
#  GÉNÉRATION DU RAPPORT
# ══════════════════════════════════════════════

def generer_rapport(resultats, lettre):
    """
    Format du fichier .txt généré :

        Thés & Tisanes :
        Tisane pour l'insomnie = Plante A, Plante B
        Décoction du matin     = Plante C

        Remèdes & Soins :
        Cataplasme anti-douleur = Plante A
        ...

    Les catégories sans aucun usage sont omises.
    Les titres en doublon sont comptés une seule fois (titres uniques).
    """
    now    = datetime.now().strftime("%d/%m/%Y à %H:%M")
    lignes = []

    lignes.append(f"Herbarium — Dossier {lettre.upper()}")
    lignes.append(f"Généré le {now}")

    for cle, config in CATEGORIES.items():

        # Regrouper : titre_usage → [plante1, plante2, ...]  (sans doublon de plante)
        par_titre = defaultdict(list)
        for r in resultats:
            for titre in r["categories"][cle]:
                if r["nom"] not in par_titre[titre]:
                    par_titre[titre].append(r["nom"])

        if not par_titre:
            continue  # catégorie vide → on saute

        lignes.append("")
        lignes.append(f"{config['label']} ({len(par_titre)} unique(s)) :")
        for titre, plantes in par_titre.items():
            lignes.append(f"{titre} = {', '.join(plantes)}")

    return "\n".join(lignes)

# ══════════════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════════════

def main():
    print("═" * 55)
    print("  Herbarium — Analyse d'un dossier lettre")
    print("═" * 55)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    chemin_dossier = sys.argv[1].rstrip("/\\")

    if not os.path.isdir(chemin_dossier):
        print(f"\n❌  Dossier introuvable : {chemin_dossier}")
        sys.exit(1)

    lettre = os.path.basename(chemin_dossier).upper()

    print(f"\n📂 Dossier : {chemin_dossier}\n")

    resultats = analyser_dossier(chemin_dossier)

    if not resultats:
        sys.exit(0)

    rapport    = generer_rapport(resultats, lettre)
    date_str   = datetime.now().strftime("%Y%m%d_%H%M")
    nom_log    = f"analyse_{lettre}_{date_str}.txt"
    chemin_log = os.path.join(chemin_dossier, nom_log)

    with open(chemin_log, "w", encoding="utf-8") as f:
        f.write(rapport)

    nb = len(resultats)
    print(f"\n  {'═' * 51}")
    print(f"  ✅ {nb} plante(s) analysée(s)")
    print(f"  📋 Rapport : {chemin_log}")
    print(f"  {'═' * 51}\n")


if __name__ == "__main__":
    main()
