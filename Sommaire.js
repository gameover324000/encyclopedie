/* ════════════════════════════════════════
   HERBARIUM — sommaire.js
   JavaScript spécifique à la page sommaire
════════════════════════════════════════ */

/* ══════════════════════════════════
   SURLIGNAGE ACTIF AU SCROLL
   La catégorie visible dans la fenêtre
   se met en surbrillance dans la barre.
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
   Clic sur un lien de la barre → défile
   doucement vers la section.
══════════════════════════════════ */
catNavLinks.forEach(function (link) {
  link.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.getElementById(link.dataset.target);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});


/* ══════════════════════════════════
   BOUTON RETOUR EN HAUT
══════════════════════════════════ */
const backTopBtn = document.querySelector('.back-top');

if (backTopBtn) {
  backTopBtn.addEventListener('click', function (e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}
