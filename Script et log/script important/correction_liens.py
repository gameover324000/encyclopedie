#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herbarium — Correction des liens dans un fichier encyclopédie (ex: W.html)
et dans tous les fichiers HTML du dossier plantes associé.

Corrige :
  1. Les liens plant-link dans le fichier encyclopédie (ex: encyclopedie/W.html)
  2. Le fil d'ariane dans chaque page plante  (breadcrumb → encyclopedie/W.html)
  3. Le lien retour dans le footer            (← Retour aux espèces en W)

Usage :
    python correction_liens.py <lettre>
    python correction_liens.py W

Chemins attendus (modifiables dans CONFIGURATION) :
    encyclopedie/<LETTRE>.html
    <LETTRE>_Plante_page/*.html
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

# Chemin vers le fichier encyclopédie de la lettre
CHEMIN_ENCYCLOPEDIE = "./encyclopedie/{lettre}.html"

# Chemin vers le dossier contenant les pages plantes de la lettre
CHEMIN_DOSSIER_PLANTES = "./{lettre}_Plante_page"

# ══════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════

def slugify(nom):
    s = nom.lower()
    for src, dst in [('à','a'),('â','a'),('ä','a'),('é','e'),('è','e'),('ê','e'),
                     ('ë','e'),('î','i'),('ï','i'),('ô','o'),('ö','o'),('ù','u'),
                     ('û','u'),('ü','u'),('ç','c'),('ñ','n'),('&',''),('.',''),
                     (',',''),("'",''),('×','x')]:
        s = s.replace(src, dst)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

# ══════════════════════════════════════════════
#  CORRECTION DU FICHIER ENCYCLOPÉDIE
# ══════════════════════════════════════════════

def corriger_encyclopedie(lettre):
    """Corrige les liens plant-link dans encyclopedie/<LETTRE>.html."""
    chemin = Path(CHEMIN_ENCYCLOPEDIE.format(lettre=lettre))

    if not chemin.exists():
        print(f"  ⚠  Fichier encyclopédie introuvable : {chemin}")
        return 0

    soup = BeautifulSoup(chemin.read_text(encoding="utf-8"), "html.parser")
    corriges = 0

    for a in soup.find_all("a", class_="plant-link"):
        nom_plante = a.get_text(strip=True)
        if not nom_plante:
            continue
        slug = slugify(nom_plante)
        nouveau_href = f"../Plante_page/{lettre}_Plante_page/{slug}.html"
        if a.get("href") != nouveau_href:
            a["href"] = nouveau_href
            corriges += 1

    chemin.write_text(str(soup), encoding="utf-8")
    print(f"  ✓  {corriges} lien(s) plant-link corrigé(s) dans {chemin}")
    return corriges

# ══════════════════════════════════════════════
#  CORRECTION DES PAGES PLANTES
# ══════════════════════════════════════════════

def corriger_page_plante(chemin_html, lettre):
    """
    Corrige dans une page plante :
      - Le fil d'ariane : lien vers encyclopedie/<LETTRE>.html + texte « Espèces en « L » »
      - Le footer       : lien + texte « ← Retour aux espèces en L »
    """
    contenu = chemin_html.read_text(encoding="utf-8")
    soup    = BeautifulSoup(contenu, "html.parser")
    corriges = 0

    # ── Fil d'ariane ──────────────────────────
    # Cherche le <a> dont le href contient /encyclopedie/ et le texte "Espèces en"
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        texte = a.get_text(strip=True)
        if "encyclopedie/" in href and "Esp" in texte and "ces en" in texte:
            bon_href  = f"../../encyclopedie/{lettre}.html"
            bon_texte = f"Espèces en « {lettre} »"
            if href != bon_href or texte != bon_texte:
                a["href"] = bon_href
                a.clear()
                a.string = bon_texte
                corriges += 1

    # ── Footer ────────────────────────────────
    # Cherche le <a> du footer dont le texte contient "Retour aux espèces"
    footer = soup.find("footer")
    if footer:
        for a in footer.find_all("a", href=True):
            texte = a.get_text(strip=True)
            if "Retour aux esp" in texte:
                bon_href  = f"../../encyclopedie/{lettre}.html"
                bon_texte = f"← Retour aux espèces en {lettre}"
                if a.get("href") != bon_href or texte != bon_texte:
                    a["href"] = bon_href
                    a.clear()
                    a.string = bon_texte
                    corriges += 1

    if corriges:
        chemin_html.write_text(str(soup), encoding="utf-8")

    return corriges


def corriger_dossier_plantes(lettre):
    """Parcourt tous les .html du dossier plantes et corrige chacun."""
    dossier = Path(CHEMIN_DOSSIER_PLANTES.format(lettre=lettre))

    if not dossier.exists():
        print(f"  ⚠  Dossier plantes introuvable : {dossier}")
        return 0

    fichiers = sorted(dossier.glob("*.html"))
    if not fichiers:
        print(f"  ⚠  Aucun fichier HTML dans : {dossier}")
        return 0

    total = 0
    for f in fichiers:
        n = corriger_page_plante(f, lettre)
        if n:
            print(f"  ✓  {f.name}  ({n} correction(s))")
        else:
            print(f"  –  {f.name}  (rien à corriger)")
        total += n

    return total

# ══════════════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════════════

def main():
    print("═" * 55)
    print("  Herbarium — Correction des liens")
    print("═" * 55)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    lettre = sys.argv[1].strip().upper()

    print(f"\n📂 Lettre ciblée : {lettre}\n")

    # 1. Fichier encyclopédie
    print("  [ encyclopedie/{}.html ]".format(lettre))
    n1 = corriger_encyclopedie(lettre)

    # 2. Pages plantes
    print(f"\n  [ {lettre}_Plante_page/*.html ]")
    n2 = corriger_dossier_plantes(lettre)

    total = n1 + n2
    print(f"\n  {'═' * 51}")
    print(f"  ✅ {total} correction(s) au total")
    print(f"  {'═' * 51}\n")


if __name__ == "__main__":
    main()
