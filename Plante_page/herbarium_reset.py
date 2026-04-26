#!/usr/bin/env python3
"""
Herbarium — Réinitialisation des images
Remet les placeholders sur toutes les pages d'un dossier,
afin de permettre une nouvelle récupération d'images propre.
"""

import json
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION  (seules 2 variables à changer)
# ══════════════════════════════════════════════

DOSSIER_HTML = "./W_Plante_page"
LOG_FILE     = "reset_log_images_W.json"

# ══════════════════════════════════════════════
#  RÉINITIALISATION
# ══════════════════════════════════════════════

def reinitialiser_image(soup):
    """Remet un placeholder vide à la place de l'image existante."""
    image_frame = soup.find("div", class_="plant-image-frame")
    if not image_frame:
        return False

    # Vider complètement le frame
    image_frame.clear()

    # Remettre le placeholder visible (comme à l'origine)
    placeholder = soup.new_tag("div",
        id="img-placeholder",
        attrs={"class": "plant-img-placeholder", "style": "display:flex"}
    )
    image_frame.append(placeholder)

    # Remettre le crédit vide caché
    credit_div = soup.new_tag("div",
        id="img-credit",
        attrs={"class": "plant-img-credit", "style": "display:none"}
    )
    image_frame.append(credit_div)

    return True


def traiter_fichier(chemin):
    contenu = chemin.read_text(encoding="utf-8")
    soup    = BeautifulSoup(contenu, "html.parser")

    image_frame = soup.find("div", class_="plant-image-frame")
    if not image_frame:
        print(f"  ⚠  Pas de plant-image-frame : {chemin.name}")
        return "skip"

    succes = reinitialiser_image(soup)
    if succes:
        chemin.write_text(str(soup), encoding="utf-8")
        return "ok"
    return "erreur"


def reinitialiser_log():
    """Vide le log pour forcer le retraitement de tous les fichiers."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
    print(f"  📋 Log réinitialisé : {LOG_FILE}")


def main():
    print("═" * 55)
    print("  Herbarium — Réinitialisation des images")
    print("═" * 55)

    dossier = Path(DOSSIER_HTML)
    if not dossier.exists():
        print(f"\n❌ Dossier introuvable : {DOSSIER_HTML}")
        return

    fichiers = sorted(dossier.glob("*.html"))
    print(f"\n📂 {len(fichiers)} fichiers HTML trouvés")
    print(f"⚠  Toutes les images vont être supprimées pour être récupérées à nouveau.\n")

    confirmation = input("Confirmer ? (oui/non) : ").strip().lower()
    if confirmation != "oui":
        print("Annulé.")
        return

    print()
    compteurs = {"ok": 0, "skip": 0, "erreur": 0}

    for i, chemin in enumerate(fichiers, 1):
        print(f"[{i}/{len(fichiers)}] {chemin.name}")
        resultat = traiter_fichier(chemin)
        compteurs[resultat] = compteurs.get(resultat, 0) + 1

    # Réinitialiser le log après avoir traité tous les fichiers
    reinitialiser_log()

    print("\n" + "═" * 55)
    print(f"  ✅ {compteurs['ok']} réinitialisées  |  "
          f"⏭  {compteurs['skip']} ignorées  |  "
          f"✗ {compteurs.get('erreur', 0)} erreurs")
    print(f"\n  Tu peux maintenant relancer herbarium_images.py !")
    print("═" * 55)


if __name__ == "__main__":
    main()
