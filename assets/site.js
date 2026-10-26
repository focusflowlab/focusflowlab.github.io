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

// Mega menu: the section links open a panel. Without this script they simply go to the section page.
(() => {
  const items = [...document.querySelectorAll('.nav-item')];
  if (!items.length) return;
  document.documentElement.classList.add('js-nav');
  const close = (except) => items.forEach((it) => {
    if (it === except) return;
    it.classList.remove('open');
    it.querySelector('.nav-trigger').setAttribute('aria-expanded', 'false');
  });
  items.forEach((it) => {
    const trigger = it.querySelector('.nav-trigger');
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const open = !it.classList.contains('open');
      close(it);
      it.classList.toggle('open', open);
      trigger.setAttribute('aria-expanded', String(open));
    });
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('.nav-item')) close(); });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const open = items.find((it) => it.classList.contains('open'));
    if (open) { close(); open.querySelector('.nav-trigger').focus(); }
  });
})();
