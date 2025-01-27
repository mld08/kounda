// Fonction pour animer les nombres
function animateCountUp(element, start, end, duration) {
    let startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const currentValue = Math.floor(progress * (end - start) + start);
      element.textContent = currentValue + "+";

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }

    requestAnimationFrame(step);
  }

  // Initialisation de l'animation pour chaque élément avec data-count
  document.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll("[data-count]");
    counters.forEach(counter => {
      const endValue = parseInt(counter.getAttribute("data-count"), 10);
      animateCountUp(counter, 0, endValue, 2000); // Animation en 2 secondes
    });
  });