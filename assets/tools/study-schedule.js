// Study schedule maker: share your study hours across subjects until each one's exam.
// Each day's hours go to subjects whose exam hasn't happened yet, weighted by priority and by
// how close the exam is, so nearer exams get more time. Hours are rounded to half-hour blocks.
(() => {
  const $ = (id) => document.getElementById(id);
  const list = $('ss-rows');
  const out = $('ss-result');
  const err = $('ss-error');
  const key = 'ffl-study-schedule';

  const iso = (d) => d.toISOString().slice(0, 10);
  const day0 = () => { const d = new Date(); d.setHours(12, 0, 0, 0); return d; };
  const parse = (s) => new Date(s + 'T12:00:00');
  const nice = (d) => d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function addRow(row = { name: '', date: '', priority: '2' }) {
    const li = document.createElement('li');
    li.className = 'ss-row';
    li.innerHTML = `
      <input type="text" aria-label="Subject" placeholder="Subject" maxlength="40" value="${esc(row.name)}">
      <input type="date" aria-label="Exam date" value="${row.date}">
      <select aria-label="How much work it needs"><option value="1">Light</option><option value="2">Normal</option><option value="3">Heavy</option></select>
      <button class="btn btn-quiet row-remove" type="button" aria-label="Remove subject">Remove</button>`;
    li.querySelector('select').value = row.priority;
    list.appendChild(li);
  }

  function read() {
    return [...list.querySelectorAll('.ss-row')].map((li) => {
      const [n, d, p] = li.querySelectorAll('input, select');
      return { name: n.value.trim(), date: d.value, priority: p.value };
    });
  }

  function build() {
    const subjects = read().filter((s) => s.name && s.date);
    const hours = Math.min(14, Math.max(0.5, parseFloat($('ssHours').value) || 0));
    const perWeek = parseInt($('ssDays').value, 10);
    try { localStorage.setItem(key, JSON.stringify({ rows: read(), hours: $('ssHours').value, days: $('ssDays').value })); } catch {}
    if (!subjects.length) { out.hidden = true; err.textContent = ''; return; }
    const today = day0();
    const future = subjects.filter((s) => parse(s.date) > today);
    if (!future.length) { err.textContent = 'Add at least one exam date after today.'; out.hidden = true; return; }
    err.textContent = '';
    const last = new Date(Math.max(...future.map((s) => parse(s.date))));
    const days = Math.round((last - today) / 86400000);
    if (days > 200) { err.textContent = 'That’s more than 200 days away. Come back nearer the time for a tighter schedule.'; out.hidden = true; return; }

    const weeks = [];
    for (let i = 0; i < days; i++) {
      if (i % 7 >= perWeek) continue;
      const d = new Date(today); d.setDate(d.getDate() + i);
      const live = future.filter((s) => parse(s.date) > d);
      if (!live.length) continue;
      const w = live.map((s) => {
        const left = Math.max(1, Math.round((parse(s.date) - d) / 86400000));
        return Number(s.priority) * (1 + 14 / (left + 7));
      });
      const total = w.reduce((a, b) => a + b, 0);
      const week = Math.floor(i / 7);
      weeks[week] = weeks[week] || { start: new Date(d), hours: {} };
      live.forEach((s, j) => {
        const h = Math.round((hours * w[j] / total) * 2) / 2;
        weeks[week].hours[s.name] = (weeks[week].hours[s.name] || 0) + h;
      });
    }
    const names = future.sort((a, b) => parse(a.date) - parse(b.date)).map((s) => s.name);
    const head = `<tr><th>Week</th>${names.map((n) => `<th>${esc(n)}</th>`).join('')}</tr>`;
    const body = weeks.filter(Boolean).map((wk, i) => `<tr><td><strong>Week ${i + 1}</strong><span>from ${nice(wk.start)}</span></td>${names.map((n) => `<td class="mono">${wk.hours[n] ? wk.hours[n] + ' h' : '–'}</td>`).join('')}</tr>`).join('');
    const exams = future.map((s) => `<li><strong>${esc(s.name)}</strong> exam on ${nice(parse(s.date))}</li>`).join('');
    $('ss-table').innerHTML = `<thead>${head}</thead><tbody>${body}</tbody>`;
    $('ss-exams').innerHTML = exams;
    out.hidden = false;
  }

  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(key) || 'null'); } catch {}
  if (saved) { $('ssHours').value = saved.hours; $('ssDays').value = saved.days; }
  (saved?.rows?.length ? saved.rows : [{ name: '', date: '', priority: '2' }, { name: '', date: '', priority: '2' }]).forEach(addRow);

  $('add-subject').addEventListener('click', () => { addRow(); list.lastElementChild.querySelector('input').focus(); });
  list.addEventListener('click', (e) => { if (e.target.closest('.row-remove')) { e.target.closest('.ss-row').remove(); build(); } });
  $('ss-form').addEventListener('submit', (e) => { e.preventDefault(); build(); out.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
  $('ss-print').addEventListener('click', () => window.print());
  build();
})();
