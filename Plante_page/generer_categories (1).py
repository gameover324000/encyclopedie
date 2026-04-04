#!/usr/bin/env python3
"""
Herbarium — Générateur Remèdes, Culinaires & Cosmétiques (via Ollama)
Pour chaque plante, génère et insère les 3 nouvelles sections si pertinent.
La numérotation s'adapte selon les sections déjà présentes.
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

DOSSIER_HTML = "./Y_Plante_page"
LOG_FILE     = "generation_log_categories.json"
OLLAMA_URL   = "http://localhost:11434/api/generate"
MODELE       = "gemma3:4b"

# ══════════════════════════════════════════════
#  DÉFINITION DES CATÉGORIES
# ══════════════════════════════════════════════

CATEGORIES = [
    {
        "id":      "remedes-soins",
        "titre":   "Remèdes & Soins",
        "badge":   "💊 Remèdes",
        "couleur": "badge--remedy",
        "prompt_key": "remedes",
    },
    {
        "id":      "culinaires",
        "titre":   "Usages Culinaires",
        "badge":   "🍽️ Culinaire",
        "couleur": "badge--culinary",
        "prompt_key": "culinaires",
    },
    {
        "id":      "cosmetiques",
        "titre":   "Cosmétiques",
        "badge":   "✨ Cosmétique",
        "couleur": "badge--cosmetic",
        "prompt_key": "cosmetiques",
    },
]

# ══════════════════════════════════════════════
#  PROMPTS
# ══════════════════════════════════════════════

PROMPT_TEMPLATE = """Tu es un expert en phytothérapie et en botanique.
On te donne le nom d'une plante. Tu dois déterminer si cette plante est utilisée dans le domaine "{domaine}".

Plante : {nom}
Famille : {famille}

Réponds UNIQUEMENT avec un JSON valide, sans texte avant ni après, sans balises markdown, sans ```json.

Format exact :
{{
  "has_usage": true ou false,
  "usages": [
    {{
      "nom": "Nom de la préparation ou usage",
      "origine": "Pays ou région d'origine ou tradition",
      "ingredients": [
        {{"nom": "ingrédient 1", "est_plante": true}},
        {{"nom": "ingrédient 2", "est_plante": false}}
      ],
      "utilisation": "Description courte de la préparation ou utilisation (2-3 phrases)",
      "effets": ["effet 1", "effet 2"],
      "contre_indications": ["contre-indication 1"],
      "lutte_contre": ["problème 1", "problème 2"]
    }}
  ]
}}

Domaines :
- remedes : remèdes traditionnels, médecine par les plantes, décoctions, cataplasmes, huiles essentielles médicinales
- culinaires : usages en cuisine, épices, condiments, recettes traditionnelles, boissons alimentaires
- cosmetiques : soins de la peau, cheveux, cosmétiques naturels, masques, huiles de beauté

Si has_usage est false : {{"has_usage": false, "usages": []}}
Sois factuel, ne invente pas de propriétés non documentées."""


# ══════════════════════════════════════════════
#  CSS INJECTÉ
# ══════════════════════════════════════════════

STYLES_EXTRA = """
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
"""


def extraire_infos(soup):
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


def generer_donnees_categorie(nom, famille, domaine):
    prompt = PROMPT_TEMPLATE.format(nom=nom, famille=famille, domaine=domaine)
    response = requests.post(OLLAMA_URL, json={
        "model": MODELE,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1000}
    }, timeout=120)
    response.raise_for_status()
    texte = response.json()["response"].strip()
    texte = re.sub(r"```json|```", "", texte).strip()
    match = re.search(r'\{.*\}', texte, re.DOTALL)
    if match:
        texte = match.group(0)
    return json.loads(texte)


def compter_sections_existantes(soup):
    """Compte le nombre de sections déjà présentes pour numéroter correctement."""
    sections = soup.find_all("section", class_="plant-section")
    return len(sections)


def chiffre_romain(n):
    romains = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
    return romains[n - 1] if 1 <= n <= 10 else str(n)


def ajouter_badge(soup, badge_texte, badge_classe):
    badges_span = soup.find("span", class_="plant-badges")
    if not badges_span:
        return
    # Vérifier si déjà présent
    if badge_texte in badges_span.get_text():
        return
    badge = soup.new_tag("span", attrs={"class": f"badge {badge_classe}"})
    badge.string = badge_texte
    badges_span.append(badge)


def ajouter_lien_sommaire(soup, section_id, numero, titre):
    toc = soup.find("nav", class_="sidebar-toc")
    if not toc:
        return
    for a in toc.find_all("a"):
        if section_id in a.get("href", ""):
            return
    lien = soup.new_tag("a", href=f"#{section_id}", attrs={"class": "toc-link"})
    lien.string = f"{chiffre_romain(numero)}. {titre}"
    toc.append(lien)


def construire_section(soup, cat, usages, numero):
    section = soup.new_tag("section", attrs={
        "class": "plant-section",
        "id": cat["id"]
    })

    h2 = soup.new_tag("h2", attrs={"class": "section-heading"})
    num_span = soup.new_tag("span", attrs={"class": "sh-num"})
    num_span.string = f"{chiffre_romain(numero)}."
    h2.append(num_span)
    h2.append(f" {cat['titre']}")
    section.append(h2)

    card_class = {
        "remedes-soins": "usage-card--remedy",
        "culinaires":    "usage-card--culinary",
        "cosmetiques":   "usage-card--cosmetic",
    }.get(cat["id"], "")

    link_class = {
        "remedes-soins": "usage-link--remedy",
        "culinaires":    "usage-link--culinary",
        "cosmetiques":   "usage-link--cosmetic",
    }.get(cat["id"], "")

    for usage in usages:
        article = soup.new_tag("div", attrs={"class": f"usage-card {card_class}"})

        # Nom
        h3 = soup.new_tag("h3", attrs={"class": "usage-name"})
        a_nom = soup.new_tag("a", href="#", attrs={"class": f"usage-link {link_class}"})
        a_nom.string = usage.get("nom", "Usage")
        h3.append(a_nom)
        article.append(h3)

        # Origine
        if usage.get("origine"):
            p = soup.new_tag("p", attrs={"class": "usage-origine"})
            em = soup.new_tag("em")
            em.string = f"Origine : "
            p.append(em)
            p.append(usage["origine"])
            article.append(p)

        # Ingrédients
        if usage.get("ingredients"):
            label = soup.new_tag("p", attrs={"class": "usage-label"})
            label.string = "Ingrédients :"
            article.append(label)
            ul = soup.new_tag("ul", attrs={"class": "usage-ingredients"})
            for ing in usage["ingredients"]:
                li = soup.new_tag("li")
                nom_ing = ing.get("nom", "") if isinstance(ing, dict) else str(ing)
                est_plante = ing.get("est_plante", False) if isinstance(ing, dict) else False
                if est_plante:
                    a = soup.new_tag("a", href="#", attrs={"class": "ingredient-plant-link"})
                    a.string = nom_ing
                    li.append(a)
                else:
                    li.string = nom_ing
                ul.append(li)
            article.append(ul)

        # Utilisation / recette
        if usage.get("utilisation"):
            label = soup.new_tag("p", attrs={"class": "usage-label"})
            label.string = "Utilisation :"
            article.append(label)
            p = soup.new_tag("p", attrs={"class": "usage-utilisation"})
            p.string = usage["utilisation"]
            article.append(p)

        # Effets
        if usage.get("effets"):
            label = soup.new_tag("p", attrs={"class": "usage-label"})
            label.string = "Effets :"
            article.append(label)
            ul = soup.new_tag("ul", attrs={"class": "usage-effets"})
            for eff in usage["effets"]:
                li = soup.new_tag("li")
                li.string = eff
                ul.append(li)
            article.append(ul)

        # Contre-indications
        if usage.get("contre_indications"):
            label = soup.new_tag("p", attrs={"class": "usage-label"})
            label.string = "Contre-indications :"
            article.append(label)
            ul = soup.new_tag("ul", attrs={"class": "usage-contre"})
            for ci in usage["contre_indications"]:
                li = soup.new_tag("li")
                li.string = ci
                ul.append(li)
            article.append(ul)

        # Lutte contre
        if usage.get("lutte_contre"):
            label = soup.new_tag("p", attrs={"class": "usage-label"})
            label.string = "Indiqué contre :"
            article.append(label)
            ul = soup.new_tag("ul", attrs={"class": "usage-lutte"})
            for lut in usage["lutte_contre"]:
                li = soup.new_tag("li")
                li.string = lut
                ul.append(li)
            article.append(ul)

        section.append(article)

    return section


def ajouter_styles(soup):
    head = soup.find("head")
    if not head:
        return
    for style in soup.find_all("style"):
        if "badge--remedy" in style.get_text():
            return
    style_tag = soup.new_tag("style")
    style_tag.string = STYLES_EXTRA
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
        print(f"  ⚠  Nom introuvable, ignoré.")
        log[nom_fichier] = "erreur_nom"
        return "erreur"

    print(f"  🌿 {nom} ({famille or '?'})")

    ajouter_styles(soup)
    body_inner = soup.find("div", class_="plant-body-inner")
    modifie = False

    # Supprimer uniquement les sections des 3 catégories si elles existent déjà
    # Ne touche PAS à la section Thés/Tisanes
    for cat in CATEGORIES:
        existing = soup.find("section", id=cat["id"])
        if existing:
            prev = existing.find_previous_sibling("div", class_="plant-divider")
            if prev:
                prev.decompose()
            existing.decompose()
        # Supprimer le lien sommaire pour le recréer avec le bon numéro
        toc = soup.find("nav", class_="sidebar-toc")
        if toc:
            for a in toc.find_all("a"):
                if cat["id"] in a.get("href", ""):
                    a.decompose()

    # Compter les sections restantes (Description, Précautions, Thés éventuel...)
    numero_courant = compter_sections_existantes(soup) + 1

    for cat in CATEGORIES:
        try:
            donnees = generer_donnees_categorie(nom, famille or "inconnue", cat["prompt_key"])
        except json.JSONDecodeError as e:
            print(f"    ✗ JSON invalide pour {cat['titre']} : {e}")
            continue
        except Exception as e:
            print(f"    ✗ Erreur {cat['titre']} : {e}")
            continue

        if not donnees.get("has_usage") or not donnees.get("usages"):
            print(f"    ○ Pas d'usage {cat['titre']}")
            continue

        print(f"    ✓ {len(donnees['usages'])} usage(s) {cat['titre']}")

        numero = numero_courant
        numero_courant += 1  # Incrémenter seulement si section réellement ajoutée

        ajouter_badge(soup, cat["badge"], cat["couleur"])
        ajouter_lien_sommaire(soup, cat["id"], numero, cat["titre"])

        section = construire_section(soup, cat, donnees["usages"], numero)

        if body_inner:
            divider = soup.new_tag("div", attrs={"class": "plant-divider"})
            span_div = soup.new_tag("span")
            span_div.string = "✦"
            divider.append(span_div)
            body_inner.append(divider)
            body_inner.append(section)
            modifie = True

    if modifie:
        with open(chemin_html, "w", encoding="utf-8") as f:
            f.write(str(soup))

    log[nom_fichier] = "ok"
    print(f"  ✓  Fichier sauvegardé")
    return "ok"


def verifier_ollama():
    try:
        requests.get("http://localhost:11434", timeout=5)
        return True
    except:
        return False


def main():
    print("═" * 55)
    print("  Herbarium — Remèdes / Culinaires / Cosmétiques")
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
