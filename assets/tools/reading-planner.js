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

  function calc(submitted) {
    // The boxes' own limits (shared reader; parseInt used to read "1e3" as 1 and "2.5" as 2).
    const T = ffField($('totalPages')), D = ffField($('pagesRead'));
    const total = T.v, done = D.v ?? 0;
    const deadline = $('deadline').value;
    const perWeek = parseInt($('readDays').value, 10);
    const review = $('reviewDays').checked;
    if (total === null || !deadline) { out.hidden = true; err.textContent = submitted === true ? 'Enter the total pages and your deadline.' : ''; return; }
    if (!T.ok) { err.textContent = 'Total pages: a whole number from 1 to 20,000.'; out.hidden = true; return; }
    if (!D.ok) { err.textContent = 'Pages already read: a whole number, 0 or more.'; out.hidden = true; return; }
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
    const left = total - done;
    // Never more reading days than pages left, so no day is empty.
    const readDays = keep.slice(0, Math.min(keep.length - reviewCount, left));
    const reviewList = keep.slice(keep.length - reviewCount);
    if (!readDays.length) { err.textContent = 'Not enough days. Move the deadline or read every day.'; out.hidden = true; return; }

    // Spread pages evenly (days differ by at most one page); rounding up every day left the last days empty.
    const n = readDays.length;
    $('r-per').textContent = Math.ceil(left / n);
    $('r-days').textContent = n;
    $('r-left').textContent = left;
    const rows = readDays.map((d, i) => {
      const from = done + Math.floor((left * i) / n) + 1, to = done + Math.floor((left * (i + 1)) / n);
      return `<tr><td>${nice(d)}</td><td class="mono">${from}–${to}</td></tr>`;
    }).join('') + reviewList.map((d) => `<tr><td>${nice(d)}</td><td>Review: skim your notes, recall the main points</td></tr>`).join('');
    $('r-table').innerHTML = rows;
    out.hidden = false;
    try {
      localStorage.setItem(key, JSON.stringify({ totalPages: $('totalPages').value, pagesRead: $('pagesRead').value, deadline, readDays: $('readDays').value, reviewDays: review }));
    } catch {}
  }

  form.addEventListener('submit', (e) => { e.preventDefault(); calc(true); });
  form.addEventListener('input', () => calc());
  calc();
})();
