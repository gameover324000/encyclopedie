/* ════════════════════════════════════════
   HERBARIUM — script.js
   Encyclopédie botanique
════════════════════════════════════════ */

/* ══════════════════════════════════
   BARRE DE RECHERCHE
   Appuyer sur Entrée ou cliquer "Chercher"
   redirige vers la page encyclopédie
   avec la requête en paramètre URL.
══════════════════════════════════ */
const searchInput = document.getElementById('search-input');
const searchBtn   = document.getElementById('search-btn');

function handleSearch() {
  const query = searchInput.value.trim();
  if (query.length === 0) return;

  // Redirige vers la page encyclopédie avec la recherche en paramètre
  // Modifiez 'encyclopedie.html' par le nom réel de votre page
  window.location.href = `encyclopedie.html?q=${encodeURIComponent(query)}`;
}

searchBtn.addEventListener('click', handleSearch);

searchInput.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') handleSearch();
});


/* ══════════════════════════════════
   ANIMATION D'ENTRÉE AU SCROLL
   Les sections apparaissent en douceur
   lorsqu'elles entrent dans la vue.
══════════════════════════════════ */
const observerOptions = {
  threshold: 0.12,
  rootMargin: '0px 0px -40px 0px'
};

const observer = new IntersectionObserver(function (entries) {
  entries.forEach(function (entry) {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target); // on arrête d'observer une fois visible
    }
  });
}, observerOptions);

// On observe toutes les sections catégories et les cartes plantes
document.querySelectorAll('.cat-section, .plant-card').forEach(function (el) {
  el.classList.add('fade-in');
  observer.observe(el);
});


/* ══════════════════════════════════
   STYLES D'ANIMATION (injectés en JS
   pour ne pas polluer le CSS)
══════════════════════════════════ */
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
   Ajoute une ombre à la nav quand
   l'utilisateur commence à défiler.
══════════════════════════════════ */
const nav = document.querySelector('nav');

window.addEventListener('scroll', function () {
  if (window.scrollY > 10) {
    nav.style.boxShadow = '0 2px 16px rgba(30, 18, 8, 0.10)';
  } else {
    nav.style.boxShadow = 'none';
  }
});
