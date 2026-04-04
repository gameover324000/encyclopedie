#!/usr/bin/env python3
"""
Herbarium — Complétion de la classification taxonomique via GBIF
Ajoute les niveaux manquants : Règne, Sous-règne, Division, Classe,
Sous-classe, Ordre, Famille, Genre en gardant les existants.
"""

import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

DOSSIER_HTML = "./Y_Plante_page"
LOG_FILE     = "generation_log_taxo.json"
HEADERS      = {"User-Agent": "Herbarium-Bot/1.0"}

# Ordre d'affichage des rangs taxonomiques
RANGS_ORDRE = [
    ("kingdom",     "Règne"),
    ("subkingdom",  "Sous-règne"),
    ("division",    "Division"),
    ("class",       "Classe"),
    ("subclass",    "Sous-classe"),
    ("order",       "Ordre"),
    ("family",      "Famille"),
    ("genus",       "Genre"),
    ("species",     "Espèce"),
]

# Correspondance français -> clé GBIF (pour les rangs déjà présents)
FR_TO_GBIF = {
    "règne":      "kingdom",
    "sous-règne": "subkingdom",
    "division":   "division",
    "classe":     "class",
    "sous-classe":"subclass",
    "ordre":      "order",
    "famille":    "family",
    "genre":      "genus",
    "espèce":     "species",
}

# ══════════════════════════════════════════════
#  GBIF
# ══════════════════════════════════════════════

def recuperer_classification_gbif(nom_scientifique):
    """Récupère la classification complète depuis GBIF."""
    try:
        r = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": nom_scientifique, "strict": False, "verbose": False},
            headers=HEADERS, timeout=10
        )
        data = r.json()

        if data.get("matchType") == "NONE":
            return None

        classification = {}
        for rang_gbif, _ in RANGS_ORDRE:
            valeur = data.get(rang_gbif) or data.get(rang_gbif + "Key") and None
            if data.get(rang_gbif):
                classification[rang_gbif] = data[rang_gbif]

        return classification if classification else None

    except Exception as e:
        print(f"    ✗ GBIF erreur : {e}")
        return None


# ══════════════════════════════════════════════
#  HTML
# ══════════════════════════════════════════════

def lire_taxo_existante(soup):
    """Lit les rangs taxonomiques déjà présents dans le HTML."""
    existants = {}
    for row in soup.find_all("div", class_="taxo-row"):
        dt = row.find("dt")
        dd = row.find("dd")
        if dt and dd:
            label = dt.get_text(strip=True).lower()
            valeur = dd.get_text(strip=True)
            cle_gbif = FR_TO_GBIF.get(label)
            if cle_gbif:
                existants[cle_gbif] = valeur
    return existants


def construire_taxo_complete(soup, classification_gbif, existants):
    """Construit la liste complète des rangs à afficher."""
    # Fusionner : priorité aux données existantes, compléter avec GBIF
    fusion = {}
    for rang_gbif, _ in RANGS_ORDRE:
        if rang_gbif in existants:
            fusion[rang_gbif] = existants[rang_gbif]
        elif rang_gbif in classification_gbif:
            fusion[rang_gbif] = classification_gbif[rang_gbif]

    return fusion


def mettre_a_jour_taxo(soup, classification_complete):
    """Remplace le dl.plant-taxo par la version complète."""
    taxo_dl = soup.find("dl", class_="plant-taxo")
    if not taxo_dl:
        return False

    taxo_dl.clear()

    for rang_gbif, label_fr in RANGS_ORDRE:
        valeur = classification_complete.get(rang_gbif)
        if not valeur:
            continue

        row = soup.new_tag("div", attrs={"class": "taxo-row"})
        dt = soup.new_tag("dt")
        dt.string = label_fr
        dd = soup.new_tag("dd")

        # Mettre en italique pour genre et espèce
        if rang_gbif in ("genus", "species"):
            em = soup.new_tag("em")
            em.string = valeur
            dd.append(em)
        else:
            dd.string = valeur

        row.append(dt)
        row.append(dd)
        taxo_dl.append(row)

    return True


def extraire_nom(soup):
    h1 = soup.find("h1", class_="plant-sci-name")
    return h1.get_text(strip=True) if h1 else ""


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

def traiter_fichier(chemin, log):
    nom_fichier = chemin.name

    if log.get(nom_fichier) == "ok":
        print(f"  ⏭  Déjà traité : {nom_fichier}")
        return "skip"

    contenu = chemin.read_text(encoding="utf-8")
    soup = BeautifulSoup(contenu, "html.parser")

    nom = extraire_nom(soup)
    if not nom:
        print(f"  ⚠  Nom introuvable, ignoré.")
        log[nom_fichier] = "erreur_nom"
        return "erreur"

    print(f"  🌿 {nom}")

    # Lire ce qui existe déjà
    existants = lire_taxo_existante(soup)

    # Récupérer depuis GBIF
    classification_gbif = recuperer_classification_gbif(nom)
    if not classification_gbif:
        print(f"    ✗ Non trouvé sur GBIF")
        log[nom_fichier] = "gbif_not_found"
        return "ok"

    # Fusionner et mettre à jour
    classification_complete = construire_taxo_complete(soup, classification_gbif, existants)
    succes = mettre_a_jour_taxo(soup, classification_complete)

    if succes:
        chemin.write_text(str(soup), encoding="utf-8")
        nb = len(classification_complete)
        print(f"    ✓ {nb} rangs insérés")
        log[nom_fichier] = "ok"
        return "ok"
    else:
        print(f"    ✗ dl.plant-taxo introuvable")
        log[nom_fichier] = "erreur_div"
        return "erreur"


def main():
    print("═" * 55)
    print("  Herbarium — Complétion taxonomique via GBIF")
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
        time.sleep(0.3)  # Pause pour ne pas surcharger GBIF

    print("\n" + "═" * 55)
    print(f"  ✅ {compteurs['ok']} traités  |  "
          f"⏭  {compteurs['skip']} ignorés  |  "
          f"✗ {compteurs['erreur']} erreurs")
    print(f"  📋 Log : {LOG_FILE}")
    print("═" * 55)


if __name__ == "__main__":
    main()
