// Récupération du bouton
const backToTopButton = document.getElementById('backToTop');
    
// Afficher ou masquer le bouton en fonction du défilement
window.addEventListener('scroll', function () {
    if (window.scrollY > 200) {
        backToTopButton.classList.add('show');
    } else {
        backToTopButton.classList.remove('show');
    }
});

// Remonter en haut de la page lors du clic
backToTopButton.addEventListener('click', function (e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});