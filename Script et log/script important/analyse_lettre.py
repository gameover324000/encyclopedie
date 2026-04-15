#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║         HERBARIUM — Analyse d'un dossier lettre          ║
║  Compte et liste les usages par catégorie dans les HTML  ║
╚══════════════════════════════════════════════════════════╝

Usage :
    python analyse_lettre.py <chemin_dossier_lettre>
    python analyse_lettre.py ./plantes/A

Génère un fichier log :  analyse_<LETTRE>_<DATE>.txt
"""

import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup


# ─────────────────────────────────────────────
#  Configuration des catégories à détecter
# ─────────────────────────────────────────────
CATEGORIES = {
    "thes_tisanes": {
        "label"      : "Thés & Tisanes",
        "emoji"      : "🍵",
        "section_id" : "thes-tisanes",
        "card_class" : "tea-card",
        "titre_tag"  : "h3",
        "titre_class": "tea-name",
    },
    "remedes": {
        "label"      : "Remèdes & Soins",
        "emoji"      : "💊",
        "section_id" : "remedes-soins",
        "card_class" : "usage-card--remedy",
        "titre_tag"  : "h3",
        "titre_class": "usage-name",
    },
    "culinaires": {
        "label"      : "Culinaires",
        "emoji"      : "🍽️",
        "section_id" : "culinaires",
        "card_class" : "usage-card--culinary",
        "titre_tag"  : "h3",
        "titre_class": "usage-name",
    },
    "cosmetiques": {
        "label"      : "Cosmétiques",
        "emoji"      : "✨",
        "section_id" : "cosmetiques",
        "card_class" : "usage-card--cosmetic",
        "titre_tag"  : "h3",
        "titre_class": "usage-name",
    },
}


# ─────────────────────────────────────────────
#  Extraction du nom scientifique de la plante
# ─────────────────────────────────────────────
def get_nom_plante(soup):
    """Récupère le nom scientifique depuis <h1 class='plant-sci-name'>."""
    tag = soup.find("h1", class_="plant-sci-name")
    if tag:
        return tag.get_text(strip=True)
    # Fallback : balise <title>
    title = soup.find("title")
    if title:
        return title.get_text(strip=True).split("—")[0].strip()
    return "Plante inconnue"


# ─────────────────────────────────────────────
#  Extraction des usages d'une section
# ─────────────────────────────────────────────
def extraire_usages(soup, config):
    """
    Retourne la liste des titres d'usages trouvés dans la section.
    Cherche d'abord par section_id, puis directement par card_class.
    """
    usages = []

    # Stratégie 1 : trouver la section par id, puis les cartes dedans
    section = soup.find(id=config["section_id"])
    if section:
        cartes = section.find_all(class_=config["card_class"])
        for carte in cartes:
            titre_tag = carte.find(config["titre_tag"], class_=config["titre_class"])
            if titre_tag:
                usages.append(titre_tag.get_text(strip=True))

    # Stratégie 2 (fallback) : chercher les cartes partout dans le doc
    if not usages:
        cartes = soup.find_all(class_=config["card_class"])
        for carte in cartes:
            titre_tag = carte.find(config["titre_tag"], class_=config["titre_class"])
            if titre_tag:
                usages.append(titre_tag.get_text(strip=True))

    return usages


# ─────────────────────────────────────────────
#  Analyse d'un fichier HTML
# ─────────────────────────────────────────────
def analyser_fichier(chemin_html):
    """
    Retourne un dict :
    {
        "nom"       : "Nom scientifique",
        "fichier"   : "nom_fichier.html",
        "categories": {
            "thes_tisanes": ["Tisane pour l'insomnie", ...],
            "remedes"     : [...],
            "culinaires"  : [...],
            "cosmetiques" : [...],
        }
    }
    """
    with open(chemin_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    resultat = {
        "nom"       : get_nom_plante(soup),
        "fichier"   : os.path.basename(chemin_html),
        "categories": {}
    }

    for cle, config in CATEGORIES.items():
        resultat["categories"][cle] = extraire_usages(soup, config)

    return resultat


# ─────────────────────────────────────────────
#  Analyse de tout le dossier lettre
# ─────────────────────────────────────────────
def analyser_dossier(chemin_dossier):
    """Parcourt tous les .html du dossier et retourne la liste des résultats."""
    fichiers_html = sorted([
        f for f in os.listdir(chemin_dossier)
        if f.endswith(".html")
    ])

    if not fichiers_html:
        print(f"⚠  Aucun fichier HTML trouvé dans : {chemin_dossier}")
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


# ─────────────────────────────────────────────
#  Génération du rapport texte
# ─────────────────────────────────────────────
def generer_rapport(resultats, lettre, chemin_dossier):
    """
    Construit le contenu du fichier log et retourne la chaîne.
    """
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")
    lignes = []

    # ── En-tête ──────────────────────────────
    lignes.append("╔" + "═" * 62 + "╗")
    lignes.append("║{:^62}║".format("HERBARIUM — Rapport d'analyse"))
    lignes.append("║{:^62}║".format(f"Dossier lettre : {lettre.upper()}"))
    lignes.append("║{:^62}║".format(f"Généré le {now}"))
    lignes.append("╚" + "═" * 62 + "╝")
    lignes.append("")

    nb_plantes = len(resultats)
    lignes.append(f"  Chemin analysé : {chemin_dossier}")
    lignes.append(f"  Plantes trouvées : {nb_plantes}")
    lignes.append("")

    # ── Compteurs globaux ────────────────────
    totaux = {cle: [] for cle in CATEGORIES}  # liste de (nom_plante, titre_usage)

    for r in resultats:
        for cle in CATEGORIES:
            for usage in r["categories"][cle]:
                totaux[cle].append((r["nom"], usage))

    lignes.append("━" * 64)
    lignes.append("  RÉSUMÉ GLOBAL  (titres uniques)")
    lignes.append("━" * 64)
    for cle, config in CATEGORIES.items():
        titres_uniques = set(titre for _, titre in totaux[cle])
        n = len(titres_uniques)
        barre = "█" * min(n, 40)
        lignes.append(f"  {config['emoji']}  {config['label']:<22} {n:>3} unique(s)  {barre}")
    lignes.append("")

    # ── Détail par catégorie ─────────────────
    for cle, config in CATEGORIES.items():
        titres_uniques = set(titre for _, titre in totaux[cle])
        n_unique = len(titres_uniques)
        n_total  = len(totaux[cle])
        doublon_note = f"  ⚠ dont {n_total - n_unique} doublon(s)" if n_total > n_unique else ""

        lignes.append("━" * 64)
        lignes.append(f"  {config['emoji']}  {config['label'].upper()}  ({n_unique} unique(s){doublon_note})")
        lignes.append("━" * 64)

        if not totaux[cle]:
            lignes.append("  (aucun usage recensé dans ce dossier)")
        else:
            # Regrouper les plantes par titre
            from collections import defaultdict
            par_titre = defaultdict(list)
            for nom_plante, titre in totaux[cle]:
                par_titre[titre].append(nom_plante)

            for titre, plantes in par_titre.items():
                doublon = f"  ×{len(plantes)}" if len(plantes) > 1 else ""
                lignes.append(f"  • {titre}{doublon}")
                for p in plantes:
                    lignes.append(f"    └─ {p}")
        lignes.append("")

    # ── Détail par plante ────────────────────
    lignes.append("━" * 64)
    lignes.append("  DÉTAIL PAR PLANTE")
    lignes.append("━" * 64)

    for r in resultats:
        a_des_usages = any(r["categories"][cle] for cle in CATEGORIES)
        lignes.append(f"\n  ▸ {r['nom']}  ({r['fichier']})")

        if not a_des_usages:
            lignes.append("    (aucun usage thématique détecté)")
        else:
            for cle, config in CATEGORIES.items():
                usages = r["categories"][cle]
                if usages:
                    lignes.append(f"    {config['emoji']} {config['label']} :")
                    for u in usages:
                        lignes.append(f"       – {u}")

    lignes.append("")
    lignes.append("━" * 64)
    lignes.append(f"  Fin du rapport  ·  {nb_plantes} plante(s) analysée(s)")
    lignes.append("━" * 64)

    return "\n".join(lignes)


# ─────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    chemin_dossier = sys.argv[1].rstrip("/\\")

    if not os.path.isdir(chemin_dossier):
        print(f"❌  Dossier introuvable : {chemin_dossier}")
        sys.exit(1)

    # Lettre = nom du dernier dossier (ex: "A", "B"...)
    lettre = os.path.basename(chemin_dossier).upper()

    print(f"\n🌿  Herbarium — Analyse du dossier « {lettre} »")
    print(f"    {chemin_dossier}\n")

    resultats = analyser_dossier(chemin_dossier)

    if not resultats:
        sys.exit(0)

    rapport = generer_rapport(resultats, lettre, chemin_dossier)

    # Nom du fichier log
    date_str  = datetime.now().strftime("%Y%m%d_%H%M")
    nom_log   = f"analyse_{lettre}_{date_str}.txt"
    chemin_log = os.path.join(chemin_dossier, nom_log)

    with open(chemin_log, "w", encoding="utf-8") as f:
        f.write(rapport)

    print(f"\n✅  Rapport généré : {chemin_log}\n")

    # Aperçu terminal
    print(rapport)


if __name__ == "__main__":
    main()
