
document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.querySelector('nav.navbar');

  function checkScroll() {
    if (window.scrollY === 0) {
      navbar.classList.remove('full-width');
    } else {
      navbar.classList.add('full-width');
    }
  }

  // Run on load
  checkScroll();

  // Listen for scroll events
  window.addEventListener('scroll', checkScroll);
});


document.addEventListener('DOMContentLoaded', () => {
  const elements = document.querySelectorAll('[data-fade]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      } else {
        entry.target.classList.remove('visible');
      }
    });
  }, { threshold: 0.1 });

  elements.forEach(el => observer.observe(el));
});

  // Enable tooltips
  document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
      new bootstrap.Tooltip(tooltipTriggerEl);
    });
  });
