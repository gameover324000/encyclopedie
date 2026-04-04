#!/usr/bin/env python3
"""
Herbarium — Comptage des plantes par catégorie
"""

from pathlib import Path
from bs4 import BeautifulSoup

DOSSIER_HTML = "./Y_Plante_page"

dossier = Path(DOSSIER_HTML)
fichiers = sorted(dossier.glob("*.html"))

compteurs = {
    "thes-tisanes":  {"label": "🍵 Thés / Tisanes",      "count": 0},
    "culinaires":    {"label": "🍽️  Culinaires",          "count": 0},
    "remedes-soins": {"label": "💊 Remèdes & Soins",      "count": 0},
    "cosmetiques":   {"label": "✨ Cosmétiques",           "count": 0},
}

for chemin in fichiers:
    contenu = chemin.read_text(encoding="utf-8")
    soup = BeautifulSoup(contenu, "html.parser")
    for section_id in compteurs:
        if soup.find("section", id=section_id):
            compteurs[section_id]["count"] += 1

print("\n═══════════════════════════════════")
print("  Herbarium — Plantes par catégorie")
print("═══════════════════════════════════")
print(f"  📂 Total plantes : {len(fichiers)}\n")
for cat in compteurs.values():
    print(f"  {cat['label']} : {cat['count']} plantes")
print("═══════════════════════════════════\n")
