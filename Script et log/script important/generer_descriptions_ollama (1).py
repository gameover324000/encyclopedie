#!/usr/bin/env python3
"""
Herbarium — Générateur de descriptions botaniques (via Ollama, 100% gratuit)
Lit chaque fichier HTML dans Y_Plante_page/, extrait le nom et la famille,
génère une description via Ollama (gemma3:4b), et l'insère dans la page.
"""

import os
import re
import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION — À MODIFIER SI BESOIN
# ══════════════════════════════════════════════

DOSSIER_HTML  = "./Q_Plante_page"   # ← Chemin vers ton dossier de pages HTML
LOG_FILE      = "generation_log_descriptions_Q.json"
OLLAMA_URL    = "http://localhost:11434/api/generate"
MODELE        = "gemma3:4b"

# ══════════════════════════════════════════════
#  PROMPT — Style de description souhaité
# ══════════════════════════════════════════════

PROMPT_TEMPLATE = """Tu es un botaniste expert qui rédige des fiches pour une encyclopédie botanique en français appelée Herbarium.
Génère une description botanique courte et élégante pour l'espèce suivante.

Nom scientifique : {nom}
Famille : {famille}

Règles strictes :
- 3 à 5 phrases maximum
- Ton neutre et encyclopédique, légèrement littéraire
- Mentionner : port général, feuilles, fleurs si connues, habitat, rôle écologique
- Varier les introductions (ne pas commencer par le nom de l'espèce ni par "Cette plante")
- Ne pas inventer de propriétés médicinales non documentées
- Si l'espèce est peu documentée, rester vague mais plausible selon la famille
- Répondre UNIQUEMENT avec le texte de la description, sans titre ni introduction

Exemples de style attendu :
« Petite plante herbacée poussant dans des zones tempérées et semi-ombragées, souvent au bord des chemins ou dans des clairières. Ses feuilles sont fines et légèrement dentées, donnant un port délicat. Elle produit de petites fleurs discrètes mais régulières au printemps, qui attirent quelques insectes pollinisateurs. Sa présence contribue à la biodiversité locale et à la structure végétale du sol. »

« Plante herbacée rare de montagne, poussant dans les sols humides et légèrement ombragés. Elle possède des feuilles larges et alternes, avec une texture coriace et des nervures marquées. Ses fleurs sont petites et blanches, regroupées en inflorescences discrètes. Elle joue un rôle écologique discret mais important dans la protection des sols et la diversité florale de son habitat. »

Description :"""


def extraire_infos(soup):
    """Extrait le nom scientifique et la famille depuis le HTML."""
    nom, famille = "", ""

    h1 = soup.find("h1", class_="plant-sci-name")
    if h1:
        nom = h1.get_text(strip=True)

    for row in soup.find_all("div", class_="taxo-row"):
        dt = row.find("dt")
        dd = row.find("dd")
        if dt and dd and dt.get_text(strip=True).lower() == "famille":
            famille = dd.get_text(strip=True)
            break

    if not famille:
        tag = soup.find("span", class_="plant-family-tag")
        if tag:
            famille = tag.get_text(strip=True)

    return nom, famille


def generer_description(nom, famille):
    """Appelle Ollama pour générer une description botanique."""
    prompt = PROMPT_TEMPLATE.format(nom=nom, famille=famille)

    response = requests.post(OLLAMA_URL, json={
        "model": MODELE,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 300,
        }
    }, timeout=60)

    response.raise_for_status()
    texte = response.json()["response"].strip()

    # Nettoyer les guillemets ou balises parasites éventuels
    texte = texte.strip('«»"\'')
    texte = re.sub(r'\*+', '', texte)  # enlever les ** de markdown
    return texte.strip()


def inserer_description(soup, nom, description):
    """Remplace le contenu de plant-desc-text par la nouvelle description."""
    desc_div = soup.find("div", class_="plant-desc-text")
    if not desc_div:
        return False

    desc_div.clear()

    # Première ligne : nom en italique + famille
    p_intro = soup.new_tag("p")
    em = soup.new_tag("em")
    em.string = nom
    p_intro.append(em)
    p_intro.append(" est une espèce végétale recensée dans l'encyclopédie Herbarium.")
    desc_div.append(p_intro)

    # Paragraphes de la description générée
    phrases = [p.strip() for p in description.split("\n") if p.strip()]
    for phrase in phrases:
        p_tag = soup.new_tag("p")
        p_tag.string = phrase
        desc_div.append(p_tag)

    return True


def charger_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauvegarder_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def traiter_fichier(chemin_html, log):
    nom_fichier = chemin_html.name

    if log.get(nom_fichier) == "ok":
        print(f"  ⏭  Déjà traité : {nom_fichier}")
        return "skip"

    with open(chemin_html, "r", encoding="utf-8") as f:
        contenu = f.read()

    soup = BeautifulSoup(contenu, "html.parser")
    nom, famille = extraire_infos(soup)

    if not nom:
        print(f"  ⚠  Nom introuvable dans {nom_fichier}, ignoré.")
        log[nom_fichier] = "erreur_nom"
        return "erreur"

    print(f"  🌿 {nom} ({famille or 'famille inconnue'})")

    try:
        description = generer_description(nom, famille or "inconnue")
    except requests.exceptions.ConnectionError:
        print("  ✗  Ollama ne répond pas — est-il bien lancé ?")
        log[nom_fichier] = "erreur_connexion"
        return "erreur"
    except Exception as e:
        print(f"  ✗  Erreur pour {nom_fichier} : {e}")
        log[nom_fichier] = f"erreur: {e}"
        return "erreur"

    succes = inserer_description(soup, nom, description)
    if not succes:
        print(f"  ✗  Div plant-desc-text introuvable dans {nom_fichier}")
        log[nom_fichier] = "erreur_div"
        return "erreur"

    with open(chemin_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

    log[nom_fichier] = "ok"
    print(f"  ✓  OK ({len(description)} caractères)")
    return "ok"


def verifier_ollama():
    """Vérifie qu'Ollama est bien accessible."""
    try:
        r = requests.get("http://localhost:11434", timeout=5)
        return True
    except:
        return False


def main():
    print("═" * 55)
    print("  Herbarium — Générateur de descriptions (Ollama)")
    print("═" * 55)

    if not verifier_ollama():
        print("\n❌ Ollama n'est pas accessible sur localhost:11434")
        print("   Lance Ollama d'abord, puis relance ce script.")
        return

    print(f"\n✅ Ollama détecté — modèle : {MODELE}")

    dossier = Path(DOSSIER_HTML)
    if not dossier.exists():
        print(f"\n❌ Dossier introuvable : {DOSSIER_HTML}")
        print("   Modifie la variable DOSSIER_HTML en haut du script.")
        return

    fichiers = sorted(dossier.glob("*.html"))
    print(f"📂 {len(fichiers)} fichiers HTML trouvés\n")

    log = charger_log()
    compteurs = {"ok": 0, "skip": 0, "erreur": 0}

    for i, chemin in enumerate(fichiers, 1):
        print(f"[{i}/{len(fichiers)}] {chemin.name}")
        resultat = traiter_fichier(chemin, log)
        compteurs[resultat] = compteurs.get(resultat, 0) + 1
        sauvegarder_log(log)

    print("\n" + "═" * 55)
    print(f"  ✅ {compteurs['ok']} générées  |  "
          f"⏭  {compteurs['skip']} ignorées  |  "
          f"✗ {compteurs['erreur']} erreurs")
    print(f"  📋 Log : {LOG_FILE}")
    print("═" * 55)


if __name__ == "__main__":
    main()
