/* ════════════════════════════════════════
   HERBARIUM — sommaire.js
   JavaScript spécifique à la page sommaire
   Ce fichier s'ajoute à script.js
════════════════════════════════════════ */

/* ══════════════════════════════════
   SURLIGNAGE ACTIF DANS LA BARRE
   DE NAVIGATION DES CATÉGORIES
   La catégorie visible se met en
   surbrillance automatiquement au scroll.
══════════════════════════════════ */
const catSections = document.querySelectorAll('.cat-block');
const catNavLinks = document.querySelectorAll('.cat-nav-link');

const catObserver = new IntersectionObserver(function (entries) {
  entries.forEach(function (entry) {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      catNavLinks.forEach(function (link) {
        link.classList.toggle('active', link.dataset.target === id);
      });
    }
  });
}, { rootMargin: '-30% 0px -60% 0px' });

catSections.forEach(function (section) {
  catObserver.observe(section);
});


/* ══════════════════════════════════
   DÉFILEMENT FLUIDE AU CLIC
   Sur les liens de la barre catégories,
   on fait défiler doucement vers la section.
══════════════════════════════════ */
catNavLinks.forEach(function (link) {
  link.addEventListener('click', function (e) {
    e.preventDefault();
    const targetId = link.dataset.target;
    const target = document.getElementById(targetId);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});


/* ══════════════════════════════════
   BOUTON RETOUR EN HAUT
   Remonte en douceur tout en haut
   de la page au clic.
══════════════════════════════════ */
const backTopBtn = document.querySelector('.back-top');

if (backTopBtn) {
  backTopBtn.addEventListener('click', function (e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}
