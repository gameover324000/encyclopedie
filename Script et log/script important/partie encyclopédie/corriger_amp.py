#!/usr/bin/env python3
"""
Correction rapide : remplace &amp; par & dans les titres Thés & Tisanes
"""

from pathlib import Path

DOSSIER_HTML = "./W_Plante_page"

dossier = Path(DOSSIER_HTML)
fichiers = sorted(dossier.glob("*.html"))
corriges = 0

for chemin in fichiers:
    contenu = chemin.read_text(encoding="utf-8")
    
    nouveau = contenu
    nouveau = nouveau.replace("Thés &amp;amp; Tisanes", "Thés & Tisanes")
    nouveau = nouveau.replace("Thés &amp; Tisanes", "Thés & Tisanes")

    if nouveau != contenu:
        chemin.write_text(nouveau, encoding="utf-8")
        corriges += 1
        print(f"  ✓ Corrigé : {chemin.name}")

print(f"\n✅ {corriges} fichiers corrigés.")
