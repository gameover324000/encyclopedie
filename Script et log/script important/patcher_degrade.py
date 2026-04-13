#!/usr/bin/env python3
"""
Herbarium — Patcher les pages selon toxicité
- Plante toxique    → warning-banner en rouge très sombre (#3d0a0a)
- Plante non toxique → dégradé bas header remplacé par bande beige pleine (#f4ecd5)
                     + suppression de la precaution-card--safe
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

DOSSIER_HTML  = "./U_Plante_page"   # ← change la lettre selon la lettre traitée

BEIGE         = "#f4ecd5"
ROUGE_SOMBRE  = "#3d0a0a"


def est_toxique(soup):
    """Détecte si la plante est toxique via le badge ou le warning-banner."""
    if soup.find("span", class_=lambda c: c and "badge--toxic" in c):
        return True
    if soup.find("div", class_="warning-banner"):
        return True
    return False


def patcher_warning_banner(soup):
    """Assombrit la warning-banner sur les pages toxiques."""
    banner = soup.find("div", class_="warning-banner")
    if not banner:
        return False

    # Chercher le style .warning-banner dans les balises <style>
    for style_tag in soup.find_all("style"):
        texte = style_tag.string or ""
        if "warning-banner" in texte:
            nouveau = re.sub(
                r'(\.warning-banner\s*\{[^}]*background\s*:\s*)[^;]+;',
                rf'\g<1>{ROUGE_SOMBRE};',
                texte
            )
            if nouveau != texte:
                style_tag.string = nouveau
                return True

    # Si pas trouvé dans <style>, injecter un style inline
    head = soup.find("head")
    if head:
        style_tag = soup.new_tag("style")
        style_tag.string = f".warning-banner {{ background: {ROUGE_SOMBRE} !important; }}"
        head.append(style_tag)
        return True

    return False


def patcher_degrade(soup):
    """Remplace le dégradé bas du header par une bande beige pleine (pages non toxiques)."""
    for div in soup.find_all("div", style=True):
        style = div.get("style", "")
        if "linear-gradient" in style and "pointer-events:none" in style:
            div["style"] = (
                f"height:60px;"
                f"background:{BEIGE};"
                f"pointer-events:none;"
                f"margin-top:-20px;"
            )
            return True
    return False


def supprimer_card_safe(soup):
    """Supprime l'encadré Non toxique (precaution-card--safe)."""
    card = soup.find("div", class_=lambda c: c and "precaution-card--safe" in c)
    if card:
        card.decompose()
        return True
    return False


def traiter_fichier(chemin_html):
    with open(chemin_html, "r", encoding="utf-8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")
    toxique = est_toxique(soup)
    modifie = False

    if toxique:
        if patcher_warning_banner(soup):
            modifie = True
    else:
        if patcher_degrade(soup):
            modifie = True
        if supprimer_card_safe(soup):
            modifie = True

    if modifie:
        with open(chemin_html, "w", encoding="utf-8") as f:
            f.write(str(soup))
        statut = "☠  toxique" if toxique else "🌿 non toxique"
        print(f"  ✓  [{statut}] {chemin_html.name}")
    else:
        print(f"  ⏭  Rien à modifier : {chemin_html.name}")

    return modifie


def main():
    print("═" * 55)
    print("  Herbarium — Patcher pages toxiques / non toxiques")
    print("═" * 55)

    dossier = Path(DOSSIER_HTML)
    if not dossier.exists():
        print(f"\n❌ Dossier introuvable : {DOSSIER_HTML}")
        return

    fichiers = sorted(dossier.glob("*.html"))
    print(f"📂 {len(fichiers)} fichiers HTML trouvés\n")

    modifies = 0
    for chemin in fichiers:
        if traiter_fichier(chemin):
            modifies += 1

    print("\n" + "═" * 55)
    print(f"  ✅ {modifies} fichiers modifiés sur {len(fichiers)}")
    print("═" * 55)


if __name__ == "__main__":
    main()
