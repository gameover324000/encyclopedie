#!/usr/bin/env python3
"""
Herbarium — Générateur de pages HTML pour les plantes I
Génère une page HTML par plante avec le même template que les pages Y.
Utilise l'API GBIF pour récupérer famille et taxonomie.
"""

import re
import time
import json
import requests
from pathlib import Path

# ══════════════════════════════════════════════
#  CONFIGURATION
#  ⚠ À MODIFIER à chaque nouvelle lettre
# ══════════════════════════════════════════════

DOSSIER_SORTIE  = "./I_Plante_page"   # ← Dossier de sortie        ex: "./J_Plante_page"
LETTRE          = "I"                 # ← Lettre courante           ex: "J"
LETTRE_HTML     = "I.html"            # ← Fichier index de la lettre ex: "J.html"
LOG_FILE        = "generation_log_pages_I.json"  # ← Fichier log   ex: "generation_log_pages_J.json"
HEADERS         = {"User-Agent": "Herbarium-Bot/1.0"}

# ══════════════════════════════════════════════
#  LISTE DES PLANTES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Coller ici toutes les plantes de la lettre,
#    une par ligne, sans numérotation.
# ══════════════════════════════════════════════

PLANTES = """Ianhedgea minutiflora
Ianthe Salisb.
Ianthopappus corymbosus
Ibatia aristeguietae
Ibatia boliviensis
Ibatia calchaquina
Ibatia ciliata
Ibatia cordata
Ibatia cumanensis
Ixyophora fosterae
Ixyophora luerorum
Ixyophora velastiguii
Ixyophora viridisepala
Ixyoungia yendoi
Izziella Doty, 1978
Izziella formosana
Izziella hommersandii
Izziella kuroshioensis
Izziella vulcanensis""".strip().split("\n")

# ══════════════════════════════════════════════
#  LISTE DES PLANTES TOXIQUES
#  ⚠ À REMPLACER à chaque nouvelle lettre
#  → Mettre ici uniquement les noms présents
#    dans PLANTES qui sont toxiques.
#    Le nom doit être identique (même casse).
#  → Si aucune plante toxique : laisser [] 
# ══════════════════════════════════════════════

PLANTES_TOXIQUES = """Ibatia ciliata
Ibatia cordata""".strip().split("\n")

# Convertir en set pour une recherche rapide
TOXIQUES_SET = set(p.strip() for p in PLANTES_TOXIQUES if p.strip())

# ══════════════════════════════════════════════
#  STATISTIQUES (affichées à la fin)
# ══════════════════════════════════════════════

def afficher_stats_toxicite():
    total       = len(PLANTES)
    nb_toxiques = len(TOXIQUES_SET)
    nb_saines   = total - nb_toxiques

    print(f"\n  🌿 Non toxiques : {nb_saines}")
    print(f"  ☠  Toxiques     : {nb_toxiques}")
    print(f"\n  Plantes toxiques listées :")
    for nom in sorted(TOXIQUES_SET):
        print(f"    · {nom}")

# ══════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════

def slugify(nom):
    """Convertit un nom de plante en nom de fichier HTML."""
    s = nom.lower()
    for src, dst in [('à','a'),('â','a'),('ä','a'),('é','e'),('è','e'),('ê','e'),
                     ('ë','e'),('î','i'),('ï','i'),('ô','o'),('ö','o'),('ù','u'),
                     ('û','u'),('ü','u'),('ç','c'),('ñ','n'),('&',''),('.',''),
                     (',',''),("'",''),('×','x'),('×','-x-')]:
        s = s.replace(src, dst)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s


def recuperer_gbif(nom):
    """Récupère famille, ordre, règne et GBIF ID depuis l'API GBIF."""
    try:
        r = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": nom, "strict": False},
            headers=HEADERS, timeout=10
        )
        data = r.json()
        if data.get("matchType") == "NONE":
            return {}
        return {
            "gbif_id":  data.get("usageKey", ""),
            "famille":  data.get("family", ""),
            "ordre":    data.get("order", ""),
            "classe":   data.get("class", ""),
            "division": data.get("phylum", ""),
            "regne":    data.get("kingdom", "Plantae"),
            "genre":    data.get("genus", ""),
        }
    except:
        return {}


def generer_html(nom, slug, gbif, est_toxique=False):
    """Génère le HTML complet d'une page plante."""
    famille  = gbif.get("famille", "")
    ordre    = gbif.get("ordre", "")
    classe   = gbif.get("classe", "")
    division = gbif.get("division", "")
    regne    = gbif.get("regne", "Plantae")
    genre    = gbif.get("genre", "")
    gbif_id  = gbif.get("gbif_id", "")

    gbif_block = ""
    if gbif_id:
        gbif_block = f"""
            <div class="sg-label">Référence GBIF</div>
            <div class="sg-id">{gbif_id}</div>
            <a href="https://www.gbif.org/species/{gbif_id}" target="_blank" rel="noopener" class="sg-link">Voir sur GBIF ↗</a>"""

    # Construire les lignes taxonomiques
    taxo_rows = ""
    taxo_data = [
        ("Règne",    regne),
        ("Division", division),
        ("Classe",   classe),
        ("Ordre",    ordre),
        ("Famille",  famille),
        ("Genre",    genre),
    ]
    for label, valeur in taxo_data:
        if valeur:
            if label == "Genre":
                taxo_rows += f'<div class="taxo-row"><dt>{label}</dt><dd><em>{valeur}</em></dd></div>\n'
            else:
                taxo_rows += f'<div class="taxo-row"><dt>{label}</dt><dd>{valeur}</dd></div>\n'

    famille_tag = famille or "Indéterminée"

    # ── Badge toxicité ──────────────────────────────────────────
    if est_toxique:
        badge_toxicite = '<span class="badge badge--toxic">✕ Toxique</span>'
    else:
        badge_toxicite = '<span class="badge badge--safe">✓ Non toxique</span>'

    # ── Section précautions adaptée ─────────────────────────────
    if est_toxique:
        precaution_toxique = """
            <div class="precaution-card precaution-card--danger">
              <span class="precaution-ico">☠️</span>
              <div><strong>Plante toxique</strong><br/>
              Cette espèce est considérée comme toxique. Ne pas ingérer et tenir hors de portée des enfants et des animaux.</div>
            </div>"""
    else:
        precaution_toxique = """
            <div class="precaution-card precaution-card--safe">
              <span class="precaution-ico">✅</span>
              <div><strong>Non toxique</strong><br/>
              Cette espèce n'est pas répertoriée comme toxique. Toutefois, consultez un professionnel avant tout usage.</div>
            </div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{nom} — Herbarium</title>
  <meta name="description" content="{nom} — fiche botanique : description, famille {famille_tag}, usages et précautions. Encyclopédie Herbarium." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Cormorant+SC:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../../style.css" />
  <link rel="stylesheet" href="../../plant.css" />
</head>
<body>

  <!-- ══ NAVIGATION ══ -->
  <nav>
    <a class="nav-logo" href="../../index.html"><em>H</em>erbarium</a>
    <ul class="nav-links" id="nav-links">
      <li><a href="../../encyclopedie/index_encyclopedie.html">Encyclopédie</a></li>
      <li><a href="../../toxique.html">Toxicité</a></li>
      <li><a href="../../sommaire.html">Sommaire</a></li>
      <li><a href="#">Boutique</a></li>
      <li><a href="#">À propos</a></li>
    </ul>
    <button class="hamburger" id="hamburger" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </nav>

  <!-- ══ FIL D'ARIANE ══ -->
  <div class="breadcrumb-bar">
    <div class="breadcrumb-inner">
      <a href="../../index.html">Accueil</a>
      <span class="bc-sep">›</span>
      <a href="../../encyclopedie/index_encyclopedie.html">Encyclopédie</a>
      <span class="bc-sep">›</span>
      <a href="../../encyclopedie/I.html">Espèces en « I »</a>
      <span class="bc-sep">›</span>
      <span class="bc-current"><em>{nom}</em></span>
    </div>
  </div>

  <main class="plant-main">

    <!-- ══ EN-TÊTE ══ -->
    <header class="plant-header">
      <div class="plant-header-inner">

        <!-- Colonne texte -->
        <div class="plant-header-text">
          <div class="plant-meta-row">
            <span class="plant-family-tag">{famille_tag}</span>
            <span class="plant-badges">{badge_toxicite}</span>
          </div>

          <h1 class="plant-sci-name">{nom}</h1>

          <p class="plant-common-names">
            <span class="common-label">Noms communs :</span>
            <span class="common-list">{nom}</span>
          </p>

          <dl class="plant-taxo">
            {taxo_rows}
          </dl>
        </div>

        <!-- Image -->
        <div class="plant-image-wrap">
          <div class="plant-image-frame">
            <div class="plant-img-placeholder" id="img-placeholder">
              <span class="placeholder-icon">🌿</span>
              <span class="placeholder-text">Image non disponible</span>
            </div>
          </div>
          <div class="img-deco img-deco--tl"></div>
          <div class="img-deco img-deco--br"></div>
        </div>

      </div>

      <div class="header-ornament">
        <svg viewBox="0 0 400 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <line x1="0" y1="10" x2="160" y2="10" stroke="currentColor" stroke-width="0.5" opacity="0.35"/>
          <path d="M180 10 Q190 2 200 10 Q210 18 220 10" stroke="currentColor" stroke-width="0.8" fill="none" opacity="0.5"/>
          <circle cx="200" cy="10" r="2" fill="currentColor" opacity="0.4"/>
          <line x1="240" y1="10" x2="400" y2="10" stroke="currentColor" stroke-width="0.5" opacity="0.35"/>
        </svg>
      </div>
    </header>

    <!-- ══ CORPS ══ -->
    <div class="plant-body-wrap">
      <div class="plant-body-inner">

        <!-- Description -->
        <section class="plant-section" id="description">
          <h2 class="section-heading">
            <span class="sh-num">I.</span> Description botanique
          </h2>
          <div class="plant-desc-text">
            <p><em>{nom}</em> est une espèce végétale de la famille des {famille_tag}.</p>
            <p>Les données détaillées sur cette espèce sont en cours de rédaction dans notre encyclopédie.</p>
          </div>
        </section>

        <div class="plant-divider"><span>✦</span></div>

        <!-- Précautions -->
        <section class="plant-section" id="precautions">
          <h2 class="section-heading">
            <span class="sh-num">II.</span> Précautions &amp; Informations
          </h2>
          <div class="precaution-grid">
            {precaution_toxique}
            <div class="precaution-card precaution-card--info">
              <span class="precaution-ico">💊</span>
              <div><strong>Usage médical</strong><br/>
              Consulter un professionnel de santé avant tout usage thérapeutique.</div>
            </div>
            <div class="precaution-card precaution-card--info">
              <span class="precaution-ico">🌿</span>
              <div><strong>Identification</strong><br/>
              Assurez-vous de l'identification correcte de l'espèce avant toute utilisation.</div>
            </div>
          </div>
        </section>

      </div><!-- /plant-body-inner -->

      <!-- Sidebar -->
      <aside class="plant-sidebar">
        <div class="sidebar-sticky">
          <div class="sidebar-title">Sommaire</div>
          <nav class="sidebar-toc">
            <a href="#description" class="toc-link toc-link--active">I. Description</a>
            <a href="#precautions" class="toc-link">II. Précautions</a>
          </nav>

          <div class="sidebar-divider"></div>

          <div class="sidebar-gbif">
            {gbif_block}
          </div>
        </div>
      </aside>

    </div><!-- /plant-body-wrap -->
  </main>

  <!-- ══ FOOTER ══ -->
  <footer>
    <strong>Herbarium</strong> — Encyclopédie botanique &nbsp;·&nbsp;
    Données <a href="https://www.gbif.org" target="_blank" rel="noopener" style="color:var(--accent)">GBIF</a> &nbsp;·&nbsp;
    <em>Usage informatif uniquement — ne remplace pas un avis médical</em>
    &nbsp;·&nbsp;
    <a href="../../encyclopedie/I.html" style="color:var(--accent)">← Retour aux espèces en I</a>
  </footer>

  <script src="../../plant.js"></script>
  <script>
    document.getElementById('hamburger').addEventListener('click', function () {{
      this.classList.toggle('open');
      document.getElementById('nav-links').classList.toggle('open');
    }});
  </script>
</body>
</html>"""


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
#  MAIN
# ══════════════════════════════════════════════

def main():
    print("═" * 55)
    print("  Herbarium — Génération pages HTML Lettre I")
    print("═" * 55)

    # Vérifier cohérence : toutes les toxiques sont dans PLANTES
    noms_plantes = set(p.strip() for p in PLANTES if p.strip())
    inconnues = TOXIQUES_SET - noms_plantes
    if inconnues:
        print("\n⚠️  ATTENTION — Ces noms sont dans PLANTES_TOXIQUES")
        print("   mais absents de PLANTES (vérifier la casse) :")
        for n in sorted(inconnues):
            print(f"   · {n}")
        print()

    afficher_stats_toxicite()
    print()

    dossier = Path(DOSSIER_SORTIE)
    dossier.mkdir(parents=True, exist_ok=True)

    log = charger_log()
    total = len(PLANTES)
    print(f"📋 {total} plantes à traiter\n")

    compteurs = {"ok": 0, "skip": 0, "erreur": 0, "toxiques": 0}

    for i, nom in enumerate(PLANTES, 1):
        nom = nom.strip()
        if not nom:
            continue

        slug = slugify(nom)
        nom_fichier = f"{slug}.html"
        chemin = dossier / nom_fichier
        est_toxique = nom in TOXIQUES_SET

        icone_tox = "☠️ " if est_toxique else "🌿"
        print(f"[{i}/{total}] {icone_tox} {nom}")

        if log.get(nom_fichier) == "ok" and chemin.exists():
            print(f"  ⏭  Déjà généré")
            compteurs["skip"] += 1
            continue

        # Récupérer infos GBIF
        gbif = recuperer_gbif(nom)
        if gbif.get("famille"):
            print(f"  📗 {gbif['famille']}")
        else:
            print(f"  ⚠  Famille non trouvée sur GBIF")

        # Générer et sauvegarder
        html = generer_html(nom, slug, gbif, est_toxique=est_toxique)
        chemin.write_text(html, encoding="utf-8")

        log[nom_fichier] = "ok"
        sauvegarder_log(log)
        compteurs["ok"] += 1
        if est_toxique:
            compteurs["toxiques"] += 1

        time.sleep(0.2)  # Respecter l'API GBIF

    print("\n" + "═" * 55)
    print(f"  ✅ {compteurs['ok']} générées  |  "
          f"⏭  {compteurs['skip']} ignorées  |  "
          f"✗ {compteurs['erreur']} erreurs")
    print(f"  ☠  {compteurs['toxiques']} pages toxiques générées")
    print(f"  📂 Fichiers dans : {DOSSIER_SORTIE}")
    print("═" * 55)


if __name__ == "__main__":
    main()
