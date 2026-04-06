#!/usr/bin/env python3
"""
Herbarium — Récupération automatique d'images pour les plantes sans photo
Sources utilisées dans l'ordre : GBIF → iNaturalist → Wikimedia Commons
"""

import re
import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

DOSSIER_HTML = "./Q_Plante_page"
LOG_FILE     = "generation_log_images_Q.json"

HEADERS = {
    "User-Agent": "Herbarium-Bot/1.0 (encyclopedie botanique personnelle)"
}

# ══════════════════════════════════════════════
#  SOURCES D'IMAGES
# ══════════════════════════════════════════════

def chercher_gbif(nom_scientifique):
    """Cherche une image via l'API GBIF."""
    try:
        # Récupérer l'ID de l'espèce
        r = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": nom_scientifique, "strict": False},
            headers=HEADERS, timeout=10
        )
        data = r.json()
        taxon_key = data.get("usageKey") or data.get("speciesKey")
        if not taxon_key:
            return None, None

        # Chercher des occurrences avec media
        r2 = requests.get(
            "https://api.gbif.org/v1/occurrence/search",
            params={"taxonKey": taxon_key, "mediaType": "StillImage", "limit": 5},
            headers=HEADERS, timeout=10
        )
        data2 = r2.json()
        for result in data2.get("results", []):
            for media in result.get("media", []):
                url = media.get("identifier", "")
                credit = media.get("rightsHolder") or media.get("publisher") or "GBIF"
                if url and url.startswith("http") and any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    return url, f"© {credit} / GBIF"
    except Exception as e:
        print(f"      GBIF erreur : {e}")
    return None, None


def chercher_inaturalist(nom_scientifique):
    """Cherche une image via l'API iNaturalist."""
    try:
        r = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": nom_scientifique, "rank": "species,genus", "per_page": 3},
            headers=HEADERS, timeout=10
        )
        data = r.json()
        for result in data.get("results", []):
            photo = result.get("default_photo")
            if photo:
                url = photo.get("medium_url") or photo.get("url", "")
                attribution = photo.get("attribution", "iNaturalist")
                # Convertir en taille plus grande si possible
                url = url.replace("/medium/", "/large/").replace("/square/", "/large/")
                if url and url.startswith("http"):
                    return url, attribution
    except Exception as e:
        print(f"      iNaturalist erreur : {e}")
    return None, None


def chercher_wikimedia(nom_scientifique):
    """Cherche une image via l'API Wikimedia Commons."""
    try:
        # Chercher la page Wikipedia
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": nom_scientifique,
                "prop": "pageimages",
                "pithumbsize": 800,
                "format": "json"
            },
            headers=HEADERS, timeout=10
        )
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            thumb = page.get("thumbnail", {})
            if thumb.get("source"):
                # Agrandir l'image
                url = thumb["source"].replace("/320px-", "/800px-").replace("/200px-", "/800px-")
                return url, "© Wikimedia Commons"
    except Exception as e:
        print(f"      Wikimedia erreur : {e}")
    return None, None


def trouver_image(nom_scientifique):
    """Essaie les sources dans l'ordre jusqu'à trouver une image."""
    print(f"    → GBIF...")
    url, credit = chercher_gbif(nom_scientifique)
    if url:
        print(f"    ✓ Trouvée sur GBIF")
        return url, credit

    print(f"    → iNaturalist...")
    url, credit = chercher_inaturalist(nom_scientifique)
    if url:
        print(f"    ✓ Trouvée sur iNaturalist")
        return url, credit

    print(f"    → Wikimedia...")
    url, credit = chercher_wikimedia(nom_scientifique)
    if url:
        print(f"    ✓ Trouvée sur Wikimedia")
        return url, credit

    print(f"    ✗ Aucune image trouvée")
    return None, None


# ══════════════════════════════════════════════
#  INSERTION DANS LE HTML
# ══════════════════════════════════════════════

def inserer_image(soup, nom, url_image, credit):
    """Remplace le placeholder par une vraie image."""
    image_frame = soup.find("div", class_="plant-image-frame")
    if not image_frame:
        return False

    # Vérifier si déjà une vraie image
    img_existante = image_frame.find("img", class_="plant-img")
    if img_existante and img_existante.get("src", "").startswith("http"):
        return False  # Déjà une image, on ne touche pas

    # Vider le frame
    image_frame.clear()

    # Créer la balise img
    img = soup.new_tag("img",
        src=url_image,
        alt=nom,
        id="plant-img",
        attrs={
            "class": "plant-img loaded",
            "loading": "lazy"
        }
    )
    image_frame.append(img)

    # Placeholder caché
    placeholder = soup.new_tag("div",
        id="img-placeholder",
        attrs={"class": "plant-img-placeholder", "style": "display:none"}
    )
    image_frame.append(placeholder)

    # Crédit
    credit_div = soup.new_tag("div",
        id="img-credit",
        attrs={"class": "plant-img-credit", "style": "display:block"}
    )
    credit_div.string = credit
    image_frame.append(credit_div)

    return True


def a_deja_image(soup):
    """Vérifie si la page a déjà une vraie image."""
    placeholder = soup.find("div", class_="plant-img-placeholder")
    if not placeholder:
        return True
    style = placeholder.get("style", "").replace(" ", "")
    if "display:none" in style:
        return True  # placeholder caché = image présente
    return False


# ══════════════════════════════════════════════
#  LOG
# ══════════════════════════════════════════════

def charger_log():
    if Path(LOG_FILE).exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauvegarder_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════
#  TRAITEMENT
# ══════════════════════════════════════════════

def extraire_nom(soup):
    h1 = soup.find("h1", class_="plant-sci-name")
    return h1.get_text(strip=True) if h1 else ""


def traiter_fichier(chemin, log):
    nom_fichier = chemin.name

    if log.get(nom_fichier) == "ok":
        print(f"  ⏭  Déjà traité : {nom_fichier}")
        return "skip"

    contenu = chemin.read_text(encoding="utf-8")
    soup = BeautifulSoup(contenu, "html.parser")

    if a_deja_image(soup):
        log[nom_fichier] = "ok_existante"
        return "skip"

    nom = extraire_nom(soup)
    if not nom:
        log[nom_fichier] = "erreur_nom"
        return "erreur"

    print(f"  🌿 {nom}")

    url, credit = trouver_image(nom)

    if not url:
        log[nom_fichier] = "no_image"
        return "ok"

    succes = inserer_image(soup, nom, url, credit)
    if succes:
        chemin.write_text(str(soup), encoding="utf-8")
        log[nom_fichier] = "ok"
        print(f"  ✓  Image insérée")
        return "ok"
    else:
        log[nom_fichier] = "erreur_insertion"
        return "erreur"


def main():
    print("═" * 55)
    print("  Herbarium — Récupération automatique d'images")
    print("═" * 55)

    dossier = Path(DOSSIER_HTML)
    if not dossier.exists():
        print(f"\n❌ Dossier introuvable : {DOSSIER_HTML}")
        return

    fichiers = sorted(dossier.glob("*.html"))
    print(f"\n📂 {len(fichiers)} fichiers HTML trouvés\n")

    log = charger_log()
    compteurs = {"ok": 0, "skip": 0, "erreur": 0}

    for i, chemin in enumerate(fichiers, 1):
        print(f"[{i}/{len(fichiers)}] {chemin.name}")
        resultat = traiter_fichier(chemin, log)
        compteurs[resultat] = compteurs.get(resultat, 0) + 1
        sauvegarder_log(log)
        time.sleep(0.3)  # Pause pour ne pas surcharger les APIs

    print("\n" + "═" * 55)
    print(f"  ✅ {compteurs['ok']} traitées  |  "
          f"⏭  {compteurs['skip']} ignorées  |  "
          f"✗ {compteurs['erreur']} erreurs")
    print(f"  📋 Log : {LOG_FILE}")
    print("═" * 55)


if __name__ == "__main__":
    main()
