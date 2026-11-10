// Home page "Your focus day": four focus blocks with a timer ring and a self-test after each.
// Choices, today's progress and the day streak are saved in this browser only. Without this script the static list still shows.
(() => {
  const root = document.getElementById('focus-day');
  if (!root) return;
  const $ = (sel) => root.querySelector(sel);
  const KEY = 'ffl-home-focus';
  const BLOCKS = 4;
  const C = 2 * Math.PI * 54;
  const today = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
  const dayBefore = () => { const d = new Date(); d.setDate(d.getDate() - 1); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
  const blank = () => ({ subject: '', len: 25, day: today(), focus: Array(BLOCKS).fill(false), tested: Array(BLOCKS).fill(false), run: null, streak: { last: '', n: 0 } });
  let s = blank();
  try { const saved = JSON.parse(localStorage.getItem(KEY) || 'null'); if (saved && Array.isArray(saved.focus)) s = { ...s, ...saved }; } catch {}
  if (s.day !== today()) { s.day = today(); s.focus = Array(BLOCKS).fill(false); s.tested = Array(BLOCKS).fill(false); s.run = null; }
  if (![25, 45, 50].includes(s.len)) s.len = 25;
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch {} };

  const top = $('#fd-top'), time = $('#fd-time'), state = $('#fd-state'), arc = $('#fd-arc'), go = $('#fd-go'), reset = $('#fd-reset');
  const subject = $('#fd-subject'), count = $('#fd-count'), live = $('#fd-live'), streak = $('#fd-streak');
  const rows = [...root.querySelectorAll('#fd-list li')];
  const lens = [...root.querySelectorAll('input[name="fd-len"]')];
  top.hidden = false;
  arc.setAttribute('stroke-dasharray', C.toFixed(1));
  const baseTitle = document.title;
  let timer = null;

  const current = () => { const i = s.focus.indexOf(false); return i; };
  const fmt = (ms) => { const t = Math.max(0, Math.ceil(ms / 1000)); return String(Math.floor(t / 60)).padStart(2, '0') + ':' + String(t % 60).padStart(2, '0'); };
  const left = () => (s.run ? (s.run.endAt ? s.run.endAt - Date.now() : s.run.left) : s.len * 60000);
  const say = (t) => { live.textContent = t; };

  function paint() {
    const done = s.focus.filter(Boolean).length;
    const i = current();
    const ms = left();
    time.textContent = fmt(ms);
    arc.setAttribute('stroke-dashoffset', (C * (s.run ? 1 - Math.min(1, Math.max(0, ms / (s.len * 60000))) : 0)).toFixed(1));
    root.classList.toggle('is-running', !!(s.run && s.run.endAt));
    count.textContent = done + ' of ' + BLOCKS + ' blocks';
    if (i === -1) { state.textContent = 'All four blocks done'; go.textContent = 'Start again tomorrow'; go.disabled = true; }
    else if (s.run && s.run.endAt) { state.textContent = 'Block ' + (i + 1) + ' of ' + BLOCKS + ': focus'; go.textContent = 'Pause'; go.disabled = false; }
    else if (s.run) { state.textContent = 'Block ' + (i + 1) + ' paused'; go.textContent = 'Resume'; go.disabled = false; }
    else { state.textContent = 'Block ' + (i + 1) + ' of ' + BLOCKS; go.textContent = 'Start block ' + (i + 1); go.disabled = false; }
    reset.hidden = !s.run;
    lens.forEach((r) => { r.checked = Number(r.value) === s.len; r.disabled = !!s.run; });
    rows.forEach((li, k) => {
      li.classList.toggle('is-done', s.focus[k]);
      li.classList.toggle('is-now', k === i);
      li.querySelector('input').checked = s.tested[k];
      li.querySelector('.fd-tag').textContent = s.focus[k] ? 'Done. Now test yourself' : (k === i ? 'Up next' : '');
      li.querySelector('strong').textContent = s.subject.trim() ? s.subject.trim() : 'Focus block';
    });
    streak.textContent = s.streak.n >= 2 && s.streak.last === today() ? s.streak.n + '-day streak' : '';
    if (s.run && s.run.endAt) document.title = '(' + fmt(ms) + ') ' + baseTitle; else document.title = baseTitle;
  }

  function finish() {
    const i = current();
    if (i !== -1) s.focus[i] = true;
    s.run = null;
    if (s.streak.last !== today()) { s.streak = { last: today(), n: s.streak.last === dayBefore() ? s.streak.n + 1 : 1 }; }
    save(); stop(); paint(); root.classList.add('just-done');
    setTimeout(() => root.classList.remove('just-done'), 1600);
    say('Block ' + (i + 1) + ' done. Time for your self-test: close your notes and write down what you remember.');
  }
  function tick() { if (s.run && s.run.endAt && s.run.endAt - Date.now() <= 0) finish(); else paint(); }
  function run() { if (!timer) timer = setInterval(tick, 250); }
  function stop() { clearInterval(timer); timer = null; }

  go.addEventListener('click', () => {
    if (current() === -1) return;
    if (s.run && s.run.endAt) { s.run = { left: s.run.endAt - Date.now() }; stop(); say('Paused.'); }
    else if (s.run) { s.run = { endAt: Date.now() + s.run.left }; run(); say('Resumed.'); }
    else { s.run = { endAt: Date.now() + s.len * 60000 }; run(); say('Block ' + (current() + 1) + ' started. ' + s.len + ' minutes.'); }
    save(); paint();
  });
  reset.addEventListener('click', () => { s.run = null; stop(); save(); paint(); say('Block reset.'); });
  lens.forEach((r) => r.addEventListener('change', () => { if (!s.run) { s.len = Number(r.value); save(); paint(); } }));
  subject.value = s.subject;
  subject.addEventListener('input', () => { s.subject = subject.value.slice(0, 40); save(); paint(); });
  rows.forEach((li, k) => li.querySelector('input').addEventListener('change', (e) => {
    s.tested[k] = e.target.checked;
    save(); paint();
    if (s.tested.every(Boolean)) say('Day complete. Four blocks, four self-tests.');
  }));
  document.addEventListener('visibilitychange', () => { if (!document.hidden) tick(); });
  if (s.run && s.run.endAt) { if (s.run.endAt - Date.now() <= 0) { finish(); } else run(); }
  paint();
})();
