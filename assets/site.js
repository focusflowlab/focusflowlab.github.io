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

// Study Focus Kit signup: sends the email straight to MailerLite only when the form is submitted.
// No third-party script loads before that, so nothing is stored in the visitor's browser.
(() => {
  const form = document.getElementById('kit-form');
  if (!form) return;
  const input = form.querySelector('#kit-email');
  const status = form.querySelector('#kit-status');
  const button = form.querySelector('button[type="submit"]');
  const say = (text, bad) => { status.textContent = text; status.classList.toggle('is-error', !!bad); input.setAttribute('aria-invalid', bad ? 'true' : 'false'); };
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (form.website.value) return; // spam trap
    const email = input.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { say('Please enter a valid email address.', true); input.focus(); return; }
    button.disabled = true;
    say('Sending\u2026');
    try {
      const data = new FormData(form);
      data.delete('website');
      const res = await fetch(form.action, { method: 'POST', body: data });
      const json = await res.json();
      if (json.success) {
        form.reset();
        say('Check your inbox! Confirm your email and the kit is on its way. If it isn\u2019t there in a few minutes, check your Promotions or Spam folder.');
      } else {
        const msg = json.errors && json.errors.fields && json.errors.fields.email ? json.errors.fields.email[0] : 'Something went wrong. Please try again.';
        say(msg, true);
      }
    } catch {
      say('We couldn\u2019t reach the signup service. Please try again, or email hello@thefocusflowlab.com.', true);
    } finally {
      button.disabled = false;
    }
  });
})();

// Copy buttons: <button data-copy="element-id">
document.querySelectorAll('[data-copy]').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const el = document.getElementById(btn.dataset.copy);
    const status = btn.parentElement.querySelector('.copy-status');
    try { await navigator.clipboard.writeText(el.value); if (status) status.textContent = 'Copied.'; }
    catch { el.select(); if (status) status.textContent = 'Press Ctrl+C to copy.'; }
  });
});
