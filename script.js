/* ════════════════════════════════════════
   HERBARIUM — script.js
   Encyclopédie botanique
════════════════════════════════════════ */

/* ══════════════════════════════════
   BARRE DE RECHERCHE + AUTOCOMPLÉTION
══════════════════════════════════ */
const searchInput = document.getElementById('search-input');
const searchBtn   = document.getElementById('search-btn');

let searchIndex = [];
let suggestionBox = null;

// Charger le search_index.json au chargement de la page
fetch('search_index.json')
  .then(r => r.json())
  .then(data => {
    searchIndex = data;
    creerBoiteSuggestions();
  })
  .catch(() => {
    // Si le fichier n'existe pas encore, la recherche fonctionne quand même
    // mais sans autocomplétion
  });

function creerBoiteSuggestions() {
  suggestionBox = document.createElement('div');
  suggestionBox.id = 'search-suggestions';
  suggestionBox.style.cssText = `
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fdf6e9;
    border: 1px solid rgba(139, 109, 56, 0.25);
    border-top: none;
    border-radius: 0 0 6px 6px;
    box-shadow: 0 8px 24px rgba(30, 18, 8, 0.12);
    max-height: 320px;
    overflow-y: auto;
    z-index: 1000;
    display: none;
  `;

  // Le parent du input doit être en position relative
  const searchWrap = document.querySelector('.search-wrap');
  searchWrap.style.position = 'relative';
  searchWrap.appendChild(suggestionBox);
}

function normaliser(str) {
  return str.toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, ''); // retire les accents
}

function afficherSuggestions(query) {
  if (!suggestionBox || query.length < 2) {
    cacherSuggestions();
    return;
  }

  const queryNorm = normaliser(query);

  // Cherche dans noms scientifiques ET noms communs
  const resultats = searchIndex.filter(plante => {
    const sciMatch = normaliser(plante.nom_scientifique).includes(queryNorm);
    const commMatch = plante.noms_communs.some(n => normaliser(n).includes(queryNorm));
    return sciMatch || commMatch;
  }).slice(0, 8); // max 8 suggestions

  if (resultats.length === 0) {
    cacherSuggestions();
    return;
  }

  suggestionBox.innerHTML = resultats.map(plante => {
    const toxBadge = plante.toxique
      ? '<span style="color:#b91c1c;font-size:0.7em;margin-left:6px;">⚠ Toxique</span>'
      : '';
    const nomCommun = plante.noms_communs.length > 0
      ? `<span style="color:#8b6d38;font-size:0.78em;display:block;">${plante.noms_communs[0]}</span>`
      : '';
    return `
      <div class="suggestion-item" data-href="${plante.fichier}" style="
        padding: 10px 16px;
        cursor: pointer;
        border-bottom: 1px solid rgba(139,109,56,0.1);
        transition: background 0.15s;
        font-family: 'EB Garamond', serif;
      ">
        <span style="font-style:italic;">${plante.nom_scientifique}</span>${toxBadge}
        ${nomCommun}
      </div>
    `;
  }).join('');

  // Hover et clic sur chaque suggestion
  suggestionBox.querySelectorAll('.suggestion-item').forEach(item => {
    item.addEventListener('mouseenter', () => item.style.background = 'rgba(139,109,56,0.08)');
    item.addEventListener('mouseleave', () => item.style.background = '');
    item.addEventListener('click', () => {
      window.location.href = item.dataset.href;
    });
  });

  suggestionBox.style.display = 'block';
}

function cacherSuggestions() {
  if (suggestionBox) suggestionBox.style.display = 'none';
}

// Écoute la frappe
searchInput.addEventListener('input', function () {
  afficherSuggestions(this.value.trim());
});

// Ferme les suggestions en cliquant ailleurs
document.addEventListener('click', function (e) {
  if (!e.target.closest('.search-wrap')) cacherSuggestions();
});

// Navigation clavier dans les suggestions
searchInput.addEventListener('keydown', function (e) {
  if (!suggestionBox || suggestionBox.style.display === 'none') return;
  const items = suggestionBox.querySelectorAll('.suggestion-item');
  const active = suggestionBox.querySelector('.suggestion-active');
  let idx = Array.from(items).indexOf(active);

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (active) active.classList.remove('suggestion-active');
    idx = (idx + 1) % items.length;
    items[idx].classList.add('suggestion-active');
    items[idx].style.background = 'rgba(139,109,56,0.12)';
    searchInput.value = items[idx].querySelector('span').textContent;
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (active) active.classList.remove('suggestion-active');
    idx = (idx - 1 + items.length) % items.length;
    items[idx].classList.add('suggestion-active');
    items[idx].style.background = 'rgba(139,109,56,0.12)';
    searchInput.value = items[idx].querySelector('span').textContent;
  } else if (e.key === 'Escape') {
    cacherSuggestions();
  } else if (e.key === 'Enter') {
    if (active) {
      window.location.href = active.dataset.href;
    } else {
      handleSearch();
    }
  }
});

function handleSearch() {
  const query = searchInput.value.trim();
  if (query.length === 0) return;
  cacherSuggestions();
  window.location.href = `recherche.html?q=${encodeURIComponent(query)}`;
}

searchBtn.addEventListener('click', handleSearch);


/* ══════════════════════════════════
   ANIMATION D'ENTRÉE AU SCROLL
══════════════════════════════════ */
const observerOptions = {
  threshold: 0.12,
  rootMargin: '0px 0px -40px 0px'
};

const observer = new IntersectionObserver(function (entries) {
  entries.forEach(function (entry) {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.cat-section, .plant-card').forEach(function (el) {
  el.classList.add('fade-in');
  observer.observe(el);
});

const animStyle = document.createElement('style');
animStyle.textContent = `
  .fade-in {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.6s ease, transform 0.6s ease;
  }
  .fade-in.visible {
    opacity: 1;
    transform: translateY(0);
  }
`;
document.head.appendChild(animStyle);


/* ══════════════════════════════════
   NAV — OMBRE AU SCROLL
══════════════════════════════════ */
const nav = document.querySelector('nav');

window.addEventListener('scroll', function () {
  nav.style.boxShadow = window.scrollY > 10
    ? '0 2px 16px rgba(30, 18, 8, 0.10)'
    : 'none';
});


/* ══════════════════════════════════
   MENU HAMBURGER MOBILE
══════════════════════════════════ */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');

hamburger.addEventListener('click', function () {
  hamburger.classList.toggle('open');
  navLinks.classList.toggle('open');
});

navLinks.querySelectorAll('a').forEach(function (link) {
  link.addEventListener('click', function () {
    hamburger.classList.remove('open');
    navLinks.classList.remove('open');
  });
});

document.addEventListener('click', function (e) {
  if (!nav.contains(e.target)) {
    hamburger.classList.remove('open');
    navLinks.classList.remove('open');
  }
});
