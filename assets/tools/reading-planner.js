// Reading planner: pages per day to finish by a deadline, with optional review days at the end.
(() => {
  const $ = (id) => document.getElementById(id);
  const form = $('reading-form');
  const out = $('reading-result');
  const err = $('reading-error');
  const key = 'ffl-reading';

  try {
    const s = JSON.parse(localStorage.getItem(key) || 'null');
    if (s) Object.entries(s).forEach(([k, v]) => { const el = $(k); if (el) el.type === 'checkbox' ? (el.checked = v) : (el.value = v); });
  } catch {}

  const day0 = () => { const d = new Date(); d.setHours(0, 0, 0, 0); return d; };
  const nice = (d) => d.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });

  function calc() {
    const total = parseInt($('totalPages').value, 10);
    const done = parseInt($('pagesRead').value || '0', 10);
    const deadline = $('deadline').value;
    const perWeek = parseInt($('readDays').value, 10);
    const review = $('reviewDays').checked;
    if (!total || !deadline) { out.hidden = true; err.textContent = ''; return; }
    if (done >= total) { err.textContent = 'You’ve already read it all.'; out.hidden = true; return; }
    const end = new Date(deadline + 'T00:00:00');
    const days = Math.round((end - day0()) / 86400000);
    if (days < 1) { err.textContent = 'Pick a deadline after today.'; out.hidden = true; return; }
    err.textContent = '';

    // Reading days from today up to the day before the deadline, skipping rest days evenly.
    const all = [];
    for (let i = 0; i < days; i++) { const d = day0(); d.setDate(d.getDate() + i); all.push(d); }
    const keep = all.filter((_, i) => i % 7 < perWeek);
    const reviewCount = review ? Math.min(2, Math.max(0, keep.length - 1)) : 0;
    const readDays = keep.slice(0, keep.length - reviewCount);
    const reviewList = keep.slice(keep.length - reviewCount);
    if (!readDays.length) { err.textContent = 'Not enough days. Move the deadline or read every day.'; out.hidden = true; return; }

    const left = total - done;
    const per = Math.ceil(left / readDays.length);
    $('r-per').textContent = per;
    $('r-days').textContent = readDays.length;
    $('r-left').textContent = left;
    let page = done + 1;
    const rows = readDays.map((d) => {
      const to = Math.min(total, page + per - 1);
      const row = page <= total ? `<tr><td>${nice(d)}</td><td class="mono">${page}–${to}</td></tr>` : '';
      page = to + 1;
      return row;
    }).join('') + reviewList.map((d) => `<tr><td>${nice(d)}</td><td>Review: skim your notes, recall the main points</td></tr>`).join('');
    $('r-table').innerHTML = rows;
    out.hidden = false;
    try {
      localStorage.setItem(key, JSON.stringify({ totalPages: $('totalPages').value, pagesRead: $('pagesRead').value, deadline, readDays: $('readDays').value, reviewDays: review }));
    } catch {}
  }

  form.addEventListener('submit', (e) => { e.preventDefault(); calc(); });
  form.addEventListener('input', calc);
  calc();
})();
