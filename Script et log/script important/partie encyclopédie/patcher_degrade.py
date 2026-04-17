#!/usr/bin/env python3
"""
Herbarium — Patcher les pages selon toxicité
- Plante toxique    → warning-banner en rouge très sombre (#3d0a0a)
                     + overlay ::after en bas du plant-header (#0f0808)
                     + sidebar même couleur que le fond (#0f0808)
- Plante non toxique → dégradé bas header remplacé par bande beige pleine (#f4ecd5)
                     + suppression de la precaution-card--safe
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

DOSSIER_HTML  = "./W_Plante_page"   # ← change la lettre selon la lettre traitée

BEIGE         = "#f4ecd5"
ROUGE_SOMBRE  = "#3d0a0a"
FOND_TOXIQUE  = "#0f0808"
HAUTEUR_BANDE = "45px"


def est_toxique(soup):
    """Détecte si la plante est toxique via le badge ou le warning-banner."""
    if soup.find("span", class_=lambda c: c and "badge--toxic" in c):
        return True
    if soup.find("div", class_="warning-banner"):
        return True
    return False


def patcher_warning_banner(soup):
    """Assombrit la warning-banner sur les pages toxiques."""
    for style_tag in soup.find_all("style"):
        texte = style_tag.string or ""
        if "warning-banner" in texte:
            nouveau = re.sub(
                r'(\.warning-banner\s*\{[^}]*background\s*:\s*)[^;]+;',
                rf'\g<1>{ROUGE_SOMBRE};',
                texte
            )
            nouveau = re.sub(
                r'(nav\s*\{[^}]*background\s*:\s*)transparent;',
                r'\g<1>rgba(15,8,8,0.97);',
                nouveau
            )
            if nouveau != texte:
                style_tag.string = nouveau
                return True
    return False


def patcher_sidebar_et_overlay(soup):
    """Injecte sidebar sombre + overlay ::after en bas du header."""
    head = soup.find("head")
    if not head:
        return False

    # Supprimer l'ancien sidebar-patch s'il existe
    for s in soup.find_all("style"):
        if "sidebar-patch" in (s.get("id") or ""):
            s.decompose()

    style_tag = soup.new_tag("style", id="sidebar-patch")
    style_tag.string = (
        f".plant-sidebar {{ background: {FOND_TOXIQUE} !important; }}\n"
        f".plant-header {{ position: relative; }}\n"
        f".plant-header::after {{\n"
        f"  content: '';\n"
        f"  position: absolute;\n"
        f"  bottom: 0;\n"
        f"  left: 0;\n"
        f"  right: 0;\n"
        f"  height: {HAUTEUR_BANDE};\n"
        f"  background: {FOND_TOXIQUE};\n"
        f"  pointer-events: none;\n"
        f"  z-index: 1;\n"
        f"}}"
    )
    head.append(style_tag)
    return True


def patcher_degrade_non_toxique(soup):
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
        if patcher_sidebar_et_overlay(soup):
            modifie = True
    else:
        if patcher_degrade_non_toxique(soup):
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
