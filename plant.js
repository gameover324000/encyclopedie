/* ════════════════════════════════════════
   HERBARIUM — plant.js
   Logique de la page plante individuelle
════════════════════════════════════════ */

/* ══════════════════════════════════
   1. IMAGE WIKIMEDIA COMMONS
   Récupère automatiquement une image
   depuis l'API Wikimedia en utilisant
   le nom scientifique de la plante.
══════════════════════════════════ */

/**
 * Charge l'image depuis Wikimedia Commons via l'API Wikipedia.
 * @param {string} scientificName  - ex: "Achillea millefolium"
 */
async function loadPlantImage(scientificName) {
  const img         = document.getElementById('plant-img');
  const placeholder = document.getElementById('img-placeholder');
  const credit      = document.getElementById('img-credit');

  if (!img || !scientificName) return;

  // Met à jour le texte du placeholder
  if (placeholder) {
    placeholder.querySelector('.placeholder-text').textContent = 'Recherche de l\'image…';
  }

  try {
    // — Étape 1 : récupération du thumbnail via l'API Wikipedia (REST) ——————
    const wikiTitle = scientificName.replace(/ /g, '_');

    const summaryUrl =
      `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(wikiTitle)}`;

    const resp = await fetch(summaryUrl);
    if (!resp.ok) throw new Error(`Wikipedia API: ${resp.status}`);

    const data = await resp.json();

    // L'API retourne thumbnail.source pour l'image principale
    const imgSrc = data?.thumbnail?.source || data?.originalimage?.source;

    if (!imgSrc) throw new Error('Aucune image disponible');

    // — Étape 2 : affichage ————————————————————————————————————————————————
    img.src = imgSrc;
    img.onload = () => {
      img.classList.add('loaded');
      if (placeholder) placeholder.style.display = 'none';

      // Crédit
      if (credit && data.originalimage) {
        credit.textContent = `© Wikimedia Commons`;
        credit.style.display = 'block';
      }
    };

    img.onerror = () => { showPlaceholderError(placeholder); };

  } catch (err) {
    console.warn('[Herbarium] Image non trouvée:', err.message);
    showPlaceholderError(placeholder);
  }
}

function showPlaceholderError(placeholder) {
  if (!placeholder) return;
  placeholder.querySelector('.placeholder-text').textContent = 'Image non disponible';
  placeholder.querySelector('.placeholder-icon').textContent = '🌿';
}

/* ══════════════════════════════════
   2. SOMMAIRE ACTIF (highlight au scroll)
══════════════════════════════════ */
function initTOC() {
  const sections = document.querySelectorAll('.plant-section[id], .usage-block[id]');
  const tocLinks = document.querySelectorAll('.toc-link, .toc-sublink');

  if (!sections.length || !tocLinks.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          tocLinks.forEach((link) => {
            const href = link.getAttribute('href');
            link.classList.toggle('toc-link--active', href === `#${id}`);
          });
        }
      });
    },
    { rootMargin: '-15% 0px -70% 0px', threshold: 0 }
  );

  sections.forEach((section) => observer.observe(section));
}

/* ══════════════════════════════════
   3. SMOOTH SCROLL pour les liens TOC
══════════════════════════════════ */
function initSmoothScroll() {
  document.querySelectorAll('.toc-link, .toc-sublink').forEach((link) => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (!href || !href.startsWith('#')) return;
      e.preventDefault();

      const target = document.querySelector(href);
      if (!target) return;

      const navH = document.querySelector('nav')?.offsetHeight || 70;
      const top  = target.getBoundingClientRect().top + window.scrollY - navH - 20;

      window.scrollTo({ top, behavior: 'smooth' });
    });
  });
}

/* ══════════════════════════════════
   4. ANIMATION D'ENTRÉE (léger fade-in)
══════════════════════════════════ */
function initPageAnimations() {
  const style = document.createElement('style');
  style.textContent = `
    .plant-header-text,
    .plant-image-wrap,
    .plant-section,
    .usage-block,
    .precaution-card,
    .related-card {
      opacity: 0;
      transform: translateY(14px);
      transition: opacity 0.5s ease, transform 0.5s ease;
    }
    .plant-header-text.visible,
    .plant-image-wrap.visible,
    .plant-section.visible,
    .usage-block.visible,
    .precaution-card.visible,
    .related-card.visible {
      opacity: 1;
      transform: translateY(0);
    }
  `;
  document.head.appendChild(style);

  const animEls = document.querySelectorAll(
    '.plant-header-text, .plant-image-wrap, .plant-section, .usage-block, .precaution-card, .related-card'
  );

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // Décalage progressif entre éléments frères
          const siblings = [...entry.target.parentElement.children];
          const idx = siblings.indexOf(entry.target);
          entry.target.style.transitionDelay = `${idx * 0.07}s`;
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08 }
  );

  animEls.forEach((el) => observer.observe(el));
}

/* ══════════════════════════════════
   5. LIENS VERS PLANTES NON INDEXÉES
   Grise les liens dont la plante
   n'est pas encore dans l'encyclopédie.
══════════════════════════════════ */

/**
 * Marque un lien interne comme "à venir" si la page n'existe pas.
 * À adapter selon votre structure de données réelle.
 * @param {string[]} existingSlugs - liste des slugs disponibles
 */
function markMissingPlantLinks(existingSlugs = []) {
  document.querySelectorAll('.ri-link').forEach((link) => {
    const href = link.getAttribute('href') || '';
    const match = href.match(/\/plante\/([^/]+)/);
    if (!match) return;

    const slug = match[1];
    if (!existingSlugs.includes(slug)) {
      link.classList.add('ri-link--unavailable');
      link.style.cssText = `
        color: var(--ink-muted);
        border-bottom: 1px dashed var(--border);
        pointer-events: none;
        cursor: default;
      `;
      link.setAttribute('title', 'Page en cours de rédaction');
      link.setAttribute('aria-disabled', 'true');
    }
  });
}

/* ══════════════════════════════════
   INIT
══════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {

  // Récupère le nom scientifique depuis le <h1>
  const h1 = document.querySelector('.plant-sci-name');
  const scientificName = h1?.textContent?.trim() || '';
  if (scientificName) loadPlantImage(scientificName);

  initTOC();
  initSmoothScroll();
  initPageAnimations();

  // ── Exemple : passer ici la liste des plantes déjà indexées ──
  // markMissingPlantLinks(['achillea-millefolium', 'melissa-officinalis']);

});
