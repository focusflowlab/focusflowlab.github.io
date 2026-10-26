// Flashcards with spaced review. Cards live in this browser. Each review moves a card along
// 1, 3, 7, 14, 30 and 60 days when you get it right, and back to tomorrow when you don't.
(() => {
  const $ = (id) => document.getElementById(id);
  const key = 'ffl-flashcards';
  const STEPS = [1, 3, 7, 14, 30, 60];
  const today = () => new Date().toISOString().slice(0, 10);
  const addDays = (n) => { const d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  let cards = [];
  try { cards = JSON.parse(localStorage.getItem(key) || '[]'); } catch {}
  const save = () => { try { localStorage.setItem(key, JSON.stringify(cards)); } catch {} };
  const due = () => cards.filter((c) => c.due <= today());

  let queue = [];
  let current = null;

  function renderList() {
    $('fc-count').textContent = cards.length;
    $('fc-due').textContent = due().length;
    $('fc-list').innerHTML = cards.map((c, i) => `<li><span><strong>${esc(c.front)}</strong><em>${esc(c.back)}</em></span><span class="fc-next">${c.due <= today() ? 'Due today' : 'Next: ' + c.due}</span><button class="btn btn-quiet" type="button" data-del="${i}" aria-label="Delete card">Delete</button></li>`).join('');
    $('fc-empty').hidden = cards.length > 0;
    $('fc-start').disabled = due().length === 0;
    $('fc-start').textContent = due().length ? `Review ${due().length} due card${due().length === 1 ? '' : 's'}` : 'Nothing due today';
  }

  function show() {
    const box = $('fc-study');
    if (!queue.length) { box.hidden = true; $('fc-done').hidden = false; current = null; renderList(); return; }
    current = queue[0];
    box.hidden = false; $('fc-done').hidden = true;
    $('fc-front').textContent = current.front;
    $('fc-back').textContent = current.back;
    $('fc-back-wrap').hidden = true;
    $('fc-reveal').hidden = false;
    $('fc-rate').hidden = true;
    $('fc-left').textContent = `${queue.length} left`;
  }

  $('fc-add').addEventListener('submit', (e) => {
    e.preventDefault();
    const front = $('fcFront').value.trim();
    const back = $('fcBack').value.trim();
    if (!front || !back) { $('fc-error').textContent = 'Fill in both sides of the card.'; return; }
    $('fc-error').textContent = '';
    cards.push({ front: front.slice(0, 300), back: back.slice(0, 600), step: 0, due: today() });
    save(); renderList();
    $('fcFront').value = ''; $('fcBack').value = ''; $('fcFront').focus();
  });

  $('fc-list').addEventListener('click', (e) => {
    const b = e.target.closest('[data-del]');
    if (!b) return;
    cards.splice(Number(b.dataset.del), 1); save(); renderList();
  });

  $('fc-start').addEventListener('click', () => { queue = due(); show(); $('fc-study').scrollIntoView({ behavior: 'smooth', block: 'center' }); });
  $('fc-reveal').addEventListener('click', () => { $('fc-back-wrap').hidden = false; $('fc-reveal').hidden = true; $('fc-rate').hidden = false; $('fc-good').focus(); });

  function rate(knew) {
    if (!current) return;
    if (knew) {
      current.step = Math.min(current.step + 1, STEPS.length - 1);
      current.due = addDays(STEPS[current.step - 1] || 1);
      queue.shift();
    } else {
      current.step = 0;
      current.due = addDays(1);
      queue.push(queue.shift()); // see it again before you finish today
      if (queue.length === 1 && queue[0] === current) queue = [];
    }
    save(); show();
  }
  $('fc-again').addEventListener('click', () => rate(false));
  $('fc-good').addEventListener('click', () => rate(true));

  $('fc-export').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(cards, null, 2)], { type: 'application/json' }));
    const a = document.createElement('a'); a.href = url; a.download = 'focusflow-flashcards.json';
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $('fc-import').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      const ok = Array.isArray(data) ? data.filter((c) => c && typeof c.front === 'string' && typeof c.back === 'string') : [];
      cards = cards.concat(ok.map((c) => ({ front: c.front.slice(0, 300), back: c.back.slice(0, 600), step: Number(c.step) || 0, due: /^\d{4}-\d{2}-\d{2}$/.test(c.due) ? c.due : today() })));
      save(); renderList();
      $('fc-error').textContent = `${ok.length} card${ok.length === 1 ? '' : 's'} imported.`;
    } catch { $('fc-error').textContent = 'That file isn’t a FocusFlow flashcard file.'; }
    e.target.value = '';
  });

  renderList();
})();
