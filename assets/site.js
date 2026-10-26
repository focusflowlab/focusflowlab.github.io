// One gentle reveal for sections marked data-reveal. Content is visible without this script.
(() => {
  const items = document.querySelectorAll('[data-reveal]');
  if (!items.length || !('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const fold = innerHeight;
  const below = [...items].filter((el) => el.getBoundingClientRect().top > fold);
  if (!below.length) return;
  document.documentElement.classList.add('js-reveal');
  items.forEach((el) => { if (!below.includes(el)) el.classList.add('is-in'); });
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -10% 0px' });
  below.forEach((el) => io.observe(el));
})();
