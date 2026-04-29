#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ajouter_emojis_index.py
-----------------------
Lit les fichiers LETTRE.html existants (Y.html, Z.html, etc.)
et ajoute des points colorés alignés en colonnes à côté de chaque lien de plante,
ainsi qu'un tableau de légende en bas de page.

Usage:
  python ajouter_emojis_index.py Y Z
  python ajouter_emojis_index.py --all
"""

import os
import sys
from bs4 import BeautifulSoup

# ============================================================
# CONFIGURATION
# ============================================================
DOSSIER_INDEX  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "encyclopedie")
DOSSIER_RACINE = os.path.dirname(os.path.abspath(__file__))
# ============================================================

# Ordre fixe des 4 catégories
CATEGORIES = [
    {"mots": ["thé", "tisane"],                      "couleur": "#4a7c59", "label": "Thé / Tisane"},
    {"mots": ["remède", "remedes", "soins"],          "couleur": "#b94040", "label": "Remèdes & Soins"},
    {"mots": ["culinaire"],                           "couleur": "#a0a0a8", "label": "Culinaire"},
    {"mots": ["cosmétique", "cosmetique", "beauté"],  "couleur": "#c9a84c", "label": "Cosmétique"},
]

STYLE_POINTS = """
    /* ── Points catégories ── */
    .plant-link {
      display: flex !important;
      align-items: center;
      justify-content: space-between;
    }
    .plant-nom {
      flex: 1;
      font-style: italic;
    }
    .plant-dots {
      display: flex;
      gap: 0;
      flex-shrink: 0;
      margin-left: 8px;
      opacity: 0;
      transition: opacity 0.2s ease;
    }
    .plant-link:hover .plant-dots {
      opacity: 1;
    }
    .plant-dot-cell {
      width: 18px;
      text-align: center;
      line-height: 1;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .plant-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    .plant-dot-empty {
      font-size: .7rem;
      color: rgba(74,51,32,.2);
    }
    /* ── Légende fixe ── */
    .legende-categories {
      position: fixed;
      right: 1.2rem;
      top: 50%;
      transform: translateY(-50%);
      display: flex;
      flex-direction: column;
      gap: .7rem;
      padding: .9rem 1rem;
      border: 1px solid var(--border);
      background: #fff9ee;
      box-shadow: 0 2px 12px rgba(30,18,8,.08);
      border-radius: 6px;
      font-family: 'EB Garamond', serif;
      font-size: .82rem;
      color: var(--ink-muted);
      z-index: 300;
    }
    .legende-titre {
      font-family: 'Playfair Display', serif;
      font-size: .75rem;
      letter-spacing: .08em;
      text-transform: uppercase;
      color: var(--ink-muted);
      margin-bottom: .2rem;
      opacity: .7;
    }
    .legende-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .legende-point {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    @media (max-width: 900px) {
      .legende-categories { display: none; }
    }
"""

LEGENDE_HTML = """
    <div class="legende-categories">
      <div class="legende-titre">Catégories</div>
      <div class="legende-item">
        <span class="legende-point" style="background:#4a7c59;"></span> Thé / Tisane
      </div>
      <div class="legende-item">
        <span class="legende-point" style="background:#b94040;"></span> Remèdes &amp; Soins
      </div>
      <div class="legende-item">
        <span class="legende-point" style="background:#a0a0a8;"></span> Culinaire
      </div>
      <div class="legende-item">
        <span class="legende-point" style="background:#c9a84c;"></span> Cosmétique
      </div>
    </div>
"""


def recuperer_categories_fiche(chemin_fiche):
    """Retourne un set des indices de catégories présentes dans la fiche."""
    if not os.path.exists(chemin_fiche):
        return set()

    try:
        with open(chemin_fiche, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        presentes = set()
        badges = soup.find_all("span", class_="badge")
        for badge in badges:
            texte = badge.get_text(strip=True).lower()
            if "toxique" in texte:
                continue
            for i, cat in enumerate(CATEGORIES):
                if any(mot in texte for mot in cat["mots"]):
                    presentes.add(i)

        return presentes

    except Exception:
        return set()


def generer_dots_html(soup, categories_presentes):
    """Génère le HTML des 4 points colorés alignés en colonnes fixes."""
    wrap = soup.new_tag("span", attrs={"class": "plant-dots"})

    for i, cat in enumerate(CATEGORIES):
        cell = soup.new_tag("span", attrs={"class": "plant-dot-cell"})
        if i in categories_presentes:
            dot = soup.new_tag("span", attrs={
                "class": "plant-dot",
                "style": f"background:{cat['couleur']};",
                "title": cat["label"]
            })
            cell.append(dot)
        else:
            dot = soup.new_tag("span", attrs={"class": "plant-dot-empty"})
            dot.string = "·"
            cell.append(dot)
        wrap.append(cell)

    return wrap


def traiter_fichier_lettre(chemin_lettre_html):
    with open(chemin_lettre_html, "r", encoding="utf-8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")

    # Vérifie si déjà traité
    if soup.find("span", class_="plant-dots"):
        print(f"   ℹ️  Déjà traité : {os.path.basename(chemin_lettre_html)}")
        return 0

    # Ajoute le CSS dans le <style> existant
    style_tag = soup.find("style")
    if style_tag:
        style_tag.string = (style_tag.string or "") + STYLE_POINTS
    else:
        new_style = soup.new_tag("style")
        new_style.string = STYLE_POINTS
        if soup.head:
            soup.head.append(new_style)

    # Traite chaque lien de plante
    liens = soup.select("ul.plant-list a.plant-link")
    modifies = 0
    sans_fiche = 0

    for lien in liens:
        href = lien.get("href", "")
        if not href:
            continue

        # Chemin absolu de la fiche
        dossier_lettre = os.path.dirname(chemin_lettre_html)
        chemin_fiche = os.path.normpath(os.path.join(dossier_lettre, href))

        categories = recuperer_categories_fiche(chemin_fiche)

        # Récupère le texte du lien
        texte = lien.get_text(strip=True)
        lien.clear()

        # Span pour le nom
        span_nom = soup.new_tag("span", attrs={"class": "plant-nom"})
        span_nom.string = texte
        lien.append(span_nom)

        # Span pour les points
        dots = generer_dots_html(soup, categories)
        lien.append(dots)

        if categories:
            modifies += 1
        else:
            sans_fiche += 1

    # Ajoute la légende avant le footer
    legende_soup = BeautifulSoup(LEGENDE_HTML, "html.parser")
    footer = soup.find("footer")
    if footer:
        footer.insert_before(legende_soup)

    # Réécrit le fichier
    with open(chemin_lettre_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"   ✔ {modifies} avec catégories, {sans_fiche} sans catégorie")
    return modifies


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ajouter_emojis_index.py Y Z")
        print("  python ajouter_emojis_index.py --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        lettres = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    else:
        lettres = [l.upper() for l in sys.argv[1:]]

    total = 0
    for lettre in lettres:
        chemin = os.path.join(DOSSIER_INDEX, f"{lettre}.html")
        if not os.path.exists(chemin):
            print(f"⚠️  Fichier introuvable : {chemin}")
            continue
        print(f"📂 Traitement de {lettre}.html...")
        total += traiter_fichier_lettre(chemin)

    print(f"\n🌿 Terminé — {total} liens mis à jour au total")


if __name__ == "__main__":
    main()
