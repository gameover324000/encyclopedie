#!/usr/bin/env python3
"""
Herbarium — Nettoyage des doublons de sections Thés et correction numérotation
Supprime la première section thé (ancien format) et remet la numérotation correcte.
"""

from pathlib import Path
from bs4 import BeautifulSoup

DOSSIER_HTML = "./Y_Plante_page"

# Correspondance id -> numéro romain correct dans le sommaire
SECTIONS_ORDRE = [
    ("description",   "I.",    "I. Description"),
    ("precautions",   "II.",   "II. Précautions"),
    ("thes-tisanes",  "III.",  "III. Thés / Tisanes"),
    ("remedes-soins", None,    "Remèdes & Soins"),
    ("culinaires",    None,    "Usages Culinaires"),
    ("cosmetiques",   None,    "Cosmétiques"),
]

CHIFFRES_ROMAINS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

dossier = Path(DOSSIER_HTML)
fichiers = sorted(dossier.glob("*.html"))
corriges = 0

for chemin in fichiers:
    contenu = chemin.read_text(encoding="utf-8")
    soup = BeautifulSoup(contenu, "html.parser")
    modifie = False

    # ══ 1. Supprimer la première section thé si elle est en double ══
    # L'ancien format contient "Recettes documentées"
    toutes_sections = soup.find_all("section", class_="plant-section")
    sections_thes = [s for s in toutes_sections if s.find(string=lambda t: t and "Recettes documentées" in t)]

    for ancienne in sections_thes:
        # Supprimer aussi le diviseur qui précède
        prev = ancienne.find_previous_sibling("div", class_="plant-divider")
        if prev:
            prev.decompose()
        ancienne.decompose()
        modifie = True

    # ══ 2. Corriger la numérotation des sections ══
    # Récupérer les sections présentes dans l'ordre
    body_inner = soup.find("div", class_="plant-body-inner")
    if not body_inner:
        continue

    sections_presentes = body_inner.find_all("section", class_="plant-section")
    numero = 1

    for section in sections_presentes:
        section_id = section.get("id", "")
        h2 = section.find("h2", class_="section-heading")
        if not h2:
            numero += 1
            continue

        num_span = h2.find("span", class_="sh-num")
        if num_span:
            ancien = num_span.get_text(strip=True)
            nouveau = f"{CHIFFRES_ROMAINS[numero - 1]}."
            if ancien != nouveau:
                num_span.string = nouveau
                modifie = True

        numero += 1

    # ══ 3. Corriger le sommaire ══
    toc = soup.find("nav", class_="sidebar-toc")
    if toc:
        # Supprimer les liens en double dans le sommaire
        vus = set()
        for a in toc.find_all("a"):
            href = a.get("href", "")
            if href in vus:
                a.decompose()
                modifie = True
            else:
                vus.add(href)

        # Remettre les bons numéros dans le sommaire
        numero = 1
        for section in body_inner.find_all("section", class_="plant-section"):
            section_id = section.get("id", "")
            lien = toc.find("a", href=f"#{section_id}")
            if lien:
                texte = lien.get_text(strip=True)
                # Remplacer le numéro au début
                nouveau_texte = f"{CHIFFRES_ROMAINS[numero - 1]}. " + ". ".join(texte.split(". ")[1:])
                if texte != nouveau_texte:
                    lien.string = nouveau_texte
                    modifie = True
            numero += 1

    if modifie:
        chemin.write_text(str(soup), encoding="utf-8")
        corriges += 1
        print(f"  ✓ Corrigé : {chemin.name}")

print(f"\n✅ {corriges} fichiers corrigés sur {len(fichiers)} au total.")
