// Flashcards with spaced review. Cards live in this browser. Each review moves a card along
// 1, 3, 7, 14, 30 and 60 days when you get it right, and back to tomorrow when you don't.
(() => {
  const $ = (id) => document.getElementById(id);
  const key = 'ffl-flashcards';
  const STEPS = [1, 3, 7, 14, 30, 60];
  // Local calendar dates (toISOString is UTC, which is yesterday or tomorrow near midnight, e.g. before 5 AM in Lahore).
  const localDate = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  const today = () => localDate(new Date());
  const addDays = (n) => { const d = new Date(); d.setDate(d.getDate() + n); return localDate(d); };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // Keep only well-formed saved cards (a damaged or old entry used to stop the whole tool).
  const clean = (c) => ({ front: c.front.slice(0, 300), back: c.back.slice(0, 600), step: Math.min(Math.max(Math.floor(Number(c.step)) || 0, 0), STEPS.length), due: /^\d{4}-\d{2}-\d{2}$/.test(c.due) ? c.due : today() });
  const valid = (c) => c && typeof c.front === 'string' && typeof c.back === 'string' && c.front.trim() !== '' && c.back.trim() !== '';
  let cards = [];
  const load = () => { try { const v = JSON.parse(localStorage.getItem(key) || '[]'); cards = Array.isArray(v) ? v.filter(valid).map(clean) : []; } catch { cards = []; } };
  load();
  const save = () => ffSave(key, cards);
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
    load(); // keep cards another tab added
    cards.push({ front: front.slice(0, 300), back: back.slice(0, 600), step: 0, due: today() });
    save(); renderList();
    $('fc-status').textContent = 'Card added.';
    $('fcFront').value = ''; $('fcBack').value = ''; $('fcFront').focus();
  });

  $('fc-list').addEventListener('click', (e) => {
    const b = e.target.closest('[data-del]');
    if (!b) return;
    const gone = cards.splice(Number(b.dataset.del), 1)[0]; save();
    $('fc-status').textContent = 'Card deleted.';
    // A deleted card leaves the review too, even the one on screen.
    if (gone && queue.includes(gone)) { queue = queue.filter((c) => c !== gone); show(); } else renderList();
  });
  // Another tab saved: take its deck; cards under review are matched by their text.
  window.addEventListener('storage', (ev) => {
    if (ev.key !== key) return;
    load();
    const same = (a) => cards.find((c) => c.front === a.front && c.back === a.back);
    const wasOn = current;
    queue = queue.map(same).filter(Boolean);
    if (wasOn) { if (queue[0] && same(wasOn) === queue[0]) current = queue[0]; else show(); }
    renderList();
  });

  $('fc-start').addEventListener('click', () => { queue = due(); show(); $('fc-study').scrollIntoView({ behavior: 'smooth', block: 'center' }); });
  $('fc-reveal').addEventListener('click', () => { $('fc-back-wrap').hidden = false; $('fc-reveal').hidden = true; $('fc-rate').hidden = false; $('fc-good').focus(); });

  function rate(knew) {
    if (!current) return;
    if (knew) {
      current.step = Math.min(current.step + 1, STEPS.length); // step n waits STEPS[n - 1] days, so the last step is the 60-day one
      current.due = addDays(STEPS[current.step - 1]);
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
      const ok = Array.isArray(data) ? data.filter(valid).map(clean) : [];
      if (!ok.length) throw new Error('no cards');
      // Skip cards already in the deck (same front and back), so importing a file twice does not double it.
      const have = new Set(cards.map((c) => c.front + '\n' + c.back));
      const add = ok.filter((c) => { const k = c.front + '\n' + c.back; if (have.has(k)) return false; have.add(k); return true; });
      cards = cards.concat(add);
      const saved = save(); renderList();
      const skipped = ok.length - add.length;
      $('fc-error').textContent = `${add.length} card${add.length === 1 ? '' : 's'} imported` + (skipped ? `, ${skipped} already in your deck` : '') + (saved ? '.' : ', for this visit only.');
    } catch { $('fc-error').textContent = 'That file isn’t a FocusFlow flashcard file.'; }
    e.target.value = '';
  });

  renderList();
})();
