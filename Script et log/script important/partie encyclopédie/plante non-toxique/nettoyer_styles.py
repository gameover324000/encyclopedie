#!/usr/bin/env python3
"""
Herbarium — Nettoyage des styles inline
Déplace les styles communs répétés dans chaque page HTML vers plant.css.
Garde uniquement les styles uniques par page (thème toxique, sidebar-patch).
"""

from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

DOSSIER_HTML  = "./Q_Plante_page"   # ← change la lettre selon la lettre traitée
PLANT_CSS     = "../../plant.css"   # ← chemin vers plant.css depuis le dossier HTML

# ══════════════════════════════════════════════
#  STYLES COMMUNS À DÉPLACER VERS plant.css
# ══════════════════════════════════════════════

STYLES_COMMUNS = """
/* ══════════════════════════════════
   THÉ / TISANE
══════════════════════════════════ */
.badge--tea {
  display: inline-block;
  padding: 3px 10px;
  border: 1px solid #7a9e7e;
  color: #4a7a50;
  background: transparent;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  border-radius: 2px;
  margin-left: 6px;
}
.tea-card {
  background: rgba(122,158,126,0.06);
  border-left: 3px solid #7a9e7e;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 0 4px 4px 0;
}
.tea-name { font-size: 1.1rem; margin-bottom: 0.5rem; }
.tea-link { color: #4a7a50; text-decoration: none; border-bottom: 1px solid #7a9e7e; }
.tea-link:hover { color: #2d5c33; }
.tea-label { font-weight: 600; margin: 0.8rem 0 0.3rem; font-size: 0.9rem; color: #5a6a5a; }
.tea-origine { color: #666; font-style: italic; margin: 0.2rem 0; }
.tea-ingredients, .tea-effets, .tea-lutte { margin: 0.2rem 0 0.5rem 1.2rem; }
.tea-ingredients li, .tea-effets li, .tea-lutte li { margin-bottom: 0.2rem; }
.tea-ingredient-link { color: #4a7a50; text-decoration: none; border-bottom: 1px dotted #7a9e7e; }
.tea-ingredient-link:hover { color: #2d5c33; }
.tea-recette { color: #444; line-height: 1.6; }

/* ══════════════════════════════════
   REMÈDES / CULINAIRES / COSMÉTIQUES
══════════════════════════════════ */
.badge--remedy {
  display: inline-block;
  padding: 3px 10px;
  border: 1px solid #9e7a7a;
  color: #7a3f3f;
  background: transparent;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  border-radius: 2px;
  margin-left: 6px;
}
.badge--culinary {
  display: inline-block;
  padding: 3px 10px;
  border: 1px solid #b8972a;
  color: #7a5e10;
  background: transparent;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  border-radius: 2px;
  margin-left: 6px;
}
.badge--cosmetic {
  display: inline-block;
  padding: 3px 10px;
  border: 1px solid #9e7ab8;
  color: #5e3f7a;
  background: transparent;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  border-radius: 2px;
  margin-left: 6px;
}
.usage-card {
  border-left: 3px solid #aaa;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 0 4px 4px 0;
}
.usage-card--remedy   { background: rgba(158,122,122,0.06); border-color: #9e7a7a; }
.usage-card--culinary { background: rgba(184,151,42,0.06);  border-color: #b8972a; }
.usage-card--cosmetic { background: rgba(158,122,184,0.06); border-color: #9e7ab8; }
.usage-name { font-size: 1.1rem; margin-bottom: 0.5rem; }
.usage-link--remedy   { color: #7a3f3f; text-decoration: none; border-bottom: 1px solid #9e7a7a; }
.usage-link--culinary { color: #7a5e10; text-decoration: none; border-bottom: 1px solid #b8972a; }
.usage-link--cosmetic { color: #5e3f7a; text-decoration: none; border-bottom: 1px solid #9e7ab8; }
.usage-link--remedy:hover   { color: #5c2020; }
.usage-link--culinary:hover { color: #4a3800; }
.usage-link--cosmetic:hover { color: #3a1f5c; }
.usage-origine { color: #666; font-style: italic; margin: 0.2rem 0; }
.usage-label { font-weight: 600; margin: 0.8rem 0 0.3rem; font-size: 0.9rem; color: #5a5a6a; }
.usage-ingredients, .usage-effets, .usage-lutte, .usage-contre { margin: 0.2rem 0 0.5rem 1.2rem; }
.usage-ingredients li, .usage-effets li, .usage-lutte li, .usage-contre li { margin-bottom: 0.2rem; }
.ingredient-plant-link { color: #4a7a50; text-decoration: none; border-bottom: 1px dotted #7a9e7e; }
.ingredient-plant-link:hover { color: #2d5c33; }
.usage-utilisation { color: #444; line-height: 1.6; }

/* ══════════════════════════════════
   PRÉCAUTIONS
══════════════════════════════════ */
.precaution-card--safe {
  background: #eef8f0;
  border-color: rgba(61, 107, 74, 0.25);
  color: #2a4a30;
}
.precaution-card--danger {
  border-left: 4px solid #c0392b;
  background: #fbeaea;
  color: #5a1a1a;
}
"""

# Marqueurs pour identifier les blocs à supprimer dans les HTML
MARQUEURS_SUPPRESSION = [
    "badge--tea",
    "tea-card",
    "badge--remedy",
    "badge--culinary",
    "badge--cosmetic",
    "usage-card",
    "precaution-card--safe",
    "precaution-card--danger",
]

# Styles à NE PAS toucher (uniques par page)
MARQUEURS_GARDER = [
    "warning-banner",   # thème toxique
    "sidebar-patch",    # overlay toxique
    ":root",            # variables CSS toxique
]


def style_est_commun(texte):
    """Retourne True si le bloc style contient des styles communs à supprimer."""
    for marqueur in MARQUEURS_SUPPRESSION:
        if marqueur in texte:
            return True
    return False


def style_est_unique(texte):
    """Retourne True si le bloc style contient des styles uniques à garder."""
    for marqueur in MARQUEURS_GARDER:
        if marqueur in texte:
            return True
    return False


def traiter_fichier(chemin_html):
    with open(chemin_html, "r", encoding="utf-8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")
    modifie = False

    for style_tag in soup.find_all("style"):
        texte = style_tag.string or ""

        # Ne pas toucher aux styles uniques
        if style_est_unique(texte):
            continue

        # Supprimer les blocs de styles communs
        if style_est_commun(texte):
            style_tag.decompose()
            modifie = True

    if modifie:
        with open(chemin_html, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"  ✓  Nettoyé : {chemin_html.name}")
    else:
        print(f"  ⏭  Rien à nettoyer : {chemin_html.name}")

    return modifie


def ajouter_styles_plant_css(chemin_css):
    """Ajoute les styles communs à plant.css si pas déjà présents."""
    contenu = chemin_css.read_text(encoding="utf-8")

    if "badge--tea" in contenu:
        print(f"\n⏭  Styles déjà présents dans {chemin_css}")
        return False

    contenu += "\n" + STYLES_COMMUNS
    chemin_css.write_text(contenu, encoding="utf-8")
    print(f"\n✅ Styles ajoutés dans {chemin_css}")
    return True


def main():
    print("═" * 55)
    print("  Herbarium — Nettoyage styles inline → plant.css")
    print("═" * 55)

    dossier = Path(DOSSIER_HTML)
    if not dossier.exists():
        print(f"\n❌ Dossier introuvable : {DOSSIER_HTML}")
        return

    # Chemin vers plant.css (relatif au dossier HTML)
    chemin_css = (dossier / PLANT_CSS).resolve()
    if not chemin_css.exists():
        print(f"\n❌ plant.css introuvable : {chemin_css}")
        return

    # 1. Ajouter les styles communs dans plant.css
    ajouter_styles_plant_css(chemin_css)

    # 2. Nettoyer les HTML
    fichiers = sorted(dossier.glob("*.html"))
    print(f"\n📂 {len(fichiers)} fichiers HTML à nettoyer\n")

    modifies = 0
    for chemin in fichiers:
        if traiter_fichier(chemin):
            modifies += 1

    print("\n" + "═" * 55)
    print(f"  ✅ {modifies} fichiers nettoyés sur {len(fichiers)}")
    print("═" * 55)


if __name__ == "__main__":
    main()
