#!/usr/bin/env python3
"""
Herbarium — Correction des liens dans Q.html
Remplace /plantes/nom-plante par ../Plante_page/Q_Plante_page/nom-plante.html
"""

import re
from pathlib import Path

FICHIER_Q = "./encyclopedie/Q.html"

contenu = Path(FICHIER_Q).read_text(encoding="utf-8")

# Remplacer href="/plantes/xxx" par href="../Plante_page/Q_Plante_page/xxx.html"
nouveau = re.sub(
    r'href="/plantes/([^"]+)"',
    r'href="../Plante_page/Q_Plante_page/\1.html"',
    contenu
)

Path(FICHIER_Q).write_text(nouveau, encoding="utf-8")

# Compter les remplacements
nb = len(re.findall(r'href="../Plante_page/Q_Plante_page/', nouveau))
print(f"✅ {nb} liens corrigés dans {FICHIER_Q}")
