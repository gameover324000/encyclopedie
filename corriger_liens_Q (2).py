#!/usr/bin/env python3
"""
Herbarium — Correction des liens dans Q.html
Applique la même slugify que le générateur de pages pour avoir des chemins corrects.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

FICHIER_Q = "./encyclopedie/Q.html"

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

contenu = Path(FICHIER_Q).read_text(encoding="utf-8")
soup = BeautifulSoup(contenu, "html.parser")

corriges = 0

for a in soup.find_all("a", class_="plant-link"):
    nom_plante = a.get_text(strip=True)
    if not nom_plante:
        continue
    slug = slugify(nom_plante)
    nouveau_href = f"../Plante_page/Q_Plante_page/{slug}.html"
    if a.get("href") != nouveau_href:
        a["href"] = nouveau_href
        corriges += 1

Path(FICHIER_Q).write_text(str(soup), encoding="utf-8")
print(f"✅ {corriges} liens corrigés dans {FICHIER_Q}")
