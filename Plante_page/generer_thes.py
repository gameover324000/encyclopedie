#!/usr/bin/env python3
"""
Herbarium — Générateur de sections Thés/Tisanes (via Ollama, 100% gratuit)
Pour chaque plante, vérifie si elle entre dans une recette de thé/tisane,
et si oui, génère + insère une section III dans le HTML.
"""

import os
import re
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════

DOSSIER_HTML  = "./Y_Plante_page"
LOG_FILE      = "generation_log_thes.json"
OLLAMA_URL    = "http://localhost:11434/api/generate"
MODELE        = "gemma3:4b"

# ══════════════════════════════════════════════
#  PROMPT — Détection + génération thé/tisane
# ══════════════════════════════════════════════

PROMPT_DETECTION = """Tu es un expert en phytothérapie et en botanique.
On te donne le nom d'une plante. Tu dois déterminer si cette plante est utilisée comme ingrédient dans un ou plusieurs thés ou tisanes traditionnels ou reconnus.

Plante : {nom}
Famille : {famille}

Réponds UNIQUEMENT avec un JSON valide, sans texte avant ni après, sans balises markdown, sans ```json.
Format exact :
{{
  "has_tea": true ou false,
  "teas": [
    {{
      "nom": "Nom du thé ou tisane",
      "origine": "Pays ou région d'origine",
      "ingredients": ["ingrédient 1", "ingrédient 2", "ingrédient 3"],
      "recette": "Description courte de la préparation (2-3 phrases)",
      "effets": ["effet 1", "effet 2", "effet 3"],
      "lutte_contre": ["problème 1", "problème 2"]
    }}
  ]
}}

Si has_tea est false, retourne juste : {{"has_tea": false, "teas": []}}
Sois factuel et ne invente pas de propriétés non documentées."""


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


def generer_donnees_the(nom, famille):
    """Appelle Ollama pour détecter et générer les infos thé/tisane."""
    prompt = PROMPT_DETECTION.format(nom=nom, famille=famille)
    response = requests.post(OLLAMA_URL, json={
        "model": MODELE,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 800}
    }, timeout=90)
    response.raise_for_status()
    texte = response.json()["response"].strip()

    # Nettoyer les balises markdown éventuelles
    texte = re.sub(r"```json|```", "", texte).strip()

    # Extraire le JSON même s'il y a du texte parasite autour
    match = re.search(r'\{.*\}', texte, re.DOTALL)
    if match:
        texte = match.group(0)

    return json.loads(texte)


def slugify(texte):
    """Convertit un nom en slug pour les URLs."""
    texte = texte.lower()
    texte = re.sub(r'[àâä]', 'a', texte)
    texte = re.sub(r'[éèêë]', 'e', texte)
    texte = re.sub(r'[îï]', 'i', texte)
    texte = re.sub(r'[ôö]', 'o', texte)
    texte = re.sub(r'[ùûü]', 'u', texte)
    texte = re.sub(r'[ç]', 'c', texte)
    texte = re.sub(r'[^a-z0-9]+', '-', texte)
    return texte.strip('-')


def ajouter_badge_the(soup):
    """Ajoute le badge Thé/Tisane dans la zone des badges en haut."""
    badges_span = soup.find("span", class_="plant-badges")
    if not badges_span:
        return

    # Vérifier si le badge existe déjà
    badges_existants = badges_span.get_text()
    if "Thé" in badges_existants or "Tisane" in badges_existants:
        return

    badge = soup.new_tag("span", attrs={"class": "badge badge--tea"})
    badge.string = "🍵 Thé / Tisane"
    badges_span.append(badge)


def ajouter_lien_sommaire(soup):
    """Ajoute le lien III. Thés/Tisanes dans le sommaire sidebar."""
    toc = soup.find("nav", class_="sidebar-toc")
    if not toc:
        return

    # Vérifier si déjà présent
    for a in toc.find_all("a"):
        if "thes" in a.get("href", "") or "Thé" in a.get_text():
            return

    lien = soup.new_tag("a", href="#thes-tisanes", attrs={"class": "toc-link"})
    lien.string = "III. Thés / Tisanes"
    toc.append(lien)


def construire_section_the(soup, teas):
    """Construit la section HTML III. Thés / Tisanes."""
    section = soup.new_tag("section", attrs={"class": "plant-section", "id": "thes-tisanes"})

    # Titre
    h2 = soup.new_tag("h2", attrs={"class": "section-heading"})
    num = soup.new_tag("span", attrs={"class": "sh-num"})
    num.string = "III."
    h2.append(num)
    h2.append(" Thés &amp; Tisanes")
    section.append(h2)

    for tea in teas:
        # Conteneur par thé
        article = soup.new_tag("div", attrs={"class": "tea-card"})

        # Nom du thé en hyperlien
        slug = slugify(tea.get("nom", "the"))
        h3 = soup.new_tag("h3", attrs={"class": "tea-name"})
        a_nom = soup.new_tag("a", href="#", attrs={"class": "tea-link"})
        a_nom.string = tea.get("nom", "Tisane")
        h3.append(a_nom)
        article.append(h3)

        # Origine
        if tea.get("origine"):
            p_origine = soup.new_tag("p", attrs={"class": "tea-origine"})
            em_label = soup.new_tag("em")
            em_label.string = "Origine : "
            p_origine.append(em_label)
            p_origine.append(tea["origine"])
            article.append(p_origine)

        # Ingrédients
        if tea.get("ingredients"):
            p_ing_label = soup.new_tag("p", attrs={"class": "tea-label"})
            p_ing_label.string = "Ingrédients :"
            article.append(p_ing_label)

            ul_ing = soup.new_tag("ul", attrs={"class": "tea-ingredients"})
            for ing in tea["ingredients"]:
                li = soup.new_tag("li")
                a_ing = soup.new_tag("a", href="#", attrs={"class": "tea-ingredient-link"})
                a_ing.string = ing
                li.append(a_ing)
                ul_ing.append(li)
            article.append(ul_ing)

        # Recette
        if tea.get("recette"):
            p_rec_label = soup.new_tag("p", attrs={"class": "tea-label"})
            p_rec_label.string = "Préparation :"
            article.append(p_rec_label)

            p_rec = soup.new_tag("p", attrs={"class": "tea-recette"})
            p_rec.string = tea["recette"]
            article.append(p_rec)

        # Effets
        if tea.get("effets"):
            p_eff_label = soup.new_tag("p", attrs={"class": "tea-label"})
            p_eff_label.string = "Effets :"
            article.append(p_eff_label)

            ul_eff = soup.new_tag("ul", attrs={"class": "tea-effets"})
            for eff in tea["effets"]:
                li = soup.new_tag("li")
                li.string = eff
                ul_eff.append(li)
            article.append(ul_eff)

        # Lutte contre
        if tea.get("lutte_contre"):
            p_lut_label = soup.new_tag("p", attrs={"class": "tea-label"})
            p_lut_label.string = "Indiqué contre :"
            article.append(p_lut_label)

            ul_lut = soup.new_tag("ul", attrs={"class": "tea-lutte"})
            for lut in tea["lutte_contre"]:
                li = soup.new_tag("li")
                li.string = lut
                ul_lut.append(li)
            article.append(ul_lut)

        section.append(article)

    return section


def inserer_section_the(soup, teas):
    """Insère la section thé après la section précautions."""
    # Vérifier si section déjà présente
    existing = soup.find("section", id="thes-tisanes")
    if existing:
        existing.decompose()

    # Trouver la section précautions
    precautions = soup.find("section", id="precautions")
    if not precautions:
        return False

    # Ajouter un diviseur + la section après précautions
    body_inner = soup.find("div", class_="plant-body-inner")
    if not body_inner:
        return False

    # Diviseur
    divider = soup.new_tag("div", attrs={"class": "plant-divider"})
    span_div = soup.new_tag("span")
    span_div.string = "✦"
    divider.append(span_div)

    # Section thé
    section_the = construire_section_the(soup, teas)

    body_inner.append(divider)
    body_inner.append(section_the)

    return True


def ajouter_style_badge(soup):
    """Ajoute le style CSS pour le badge thé si pas déjà présent."""
    # On injecte un style inline minimal pour le badge
    head = soup.find("head")
    if not head:
        return
    # Vérifier si déjà présent
    for style in soup.find_all("style"):
        if "badge--tea" in style.get_text():
            return

    style_tag = soup.new_tag("style")
    style_tag.string = """
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
    """
    head.append(style_tag)


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

    print(f"  🌿 {nom} ({famille or '?'})")

    try:
        donnees = generer_donnees_the(nom, famille or "inconnue")
    except json.JSONDecodeError as e:
        print(f"  ✗  JSON invalide pour {nom_fichier} : {e}")
        log[nom_fichier] = f"erreur_json: {e}"
        return "erreur"
    except requests.exceptions.ConnectionError:
        print("  ✗  Ollama ne répond pas — est-il bien lancé ?")
        log[nom_fichier] = "erreur_connexion"
        return "erreur"
    except Exception as e:
        print(f"  ✗  Erreur pour {nom_fichier} : {e}")
        log[nom_fichier] = f"erreur: {e}"
        return "erreur"

    if not donnees.get("has_tea") or not donnees.get("teas"):
        print(f"  ○  Pas de thé/tisane connu pour {nom}")
        log[nom_fichier] = "ok_no_tea"
        return "ok"

    print(f"  🍵 {len(donnees['teas'])} thé(s) trouvé(s) !")

    ajouter_style_badge(soup)
    ajouter_badge_the(soup)
    ajouter_lien_sommaire(soup)
    inserer_section_the(soup, donnees["teas"])

    with open(chemin_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

    log[nom_fichier] = "ok"
    print(f"  ✓  Section insérée")
    return "ok"


def verifier_ollama():
    try:
        requests.get("http://localhost:11434", timeout=5)
        return True
    except:
        return False


def main():
    print("═" * 55)
    print("  Herbarium — Générateur Thés/Tisanes (Ollama)")
    print("═" * 55)

    if not verifier_ollama():
        print("\n❌ Ollama n'est pas accessible. Lance-le d'abord !")
        return

    print(f"\n✅ Ollama OK — modèle : {MODELE}")

    dossier = Path(DOSSIER_HTML)
    if not dossier.exists():
        print(f"\n❌ Dossier introuvable : {DOSSIER_HTML}")
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
    print(f"  ✅ {compteurs['ok']} traités  |  "
          f"⏭  {compteurs['skip']} ignorés  |  "
          f"✗ {compteurs['erreur']} erreurs")
    print(f"  📋 Log : {LOG_FILE}")
    print("═" * 55)


if __name__ == "__main__":
    main()
