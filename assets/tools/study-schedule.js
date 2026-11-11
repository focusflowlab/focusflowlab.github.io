// Study schedule maker: share your study hours across subjects until each one's exam.
// Each day's hours go to subjects whose exam hasn't happened yet, weighted by priority and by
// how close the exam is, so nearer exams get more time. Hours are rounded to half-hour blocks.
(() => {
  const $ = (id) => document.getElementById(id);
  const list = $('ss-rows');
  const out = $('ss-result');
  const err = $('ss-error');
  const key = 'ffl-study-schedule';

  const day0 =() => { const d = new Date(); d.setHours(12, 0, 0, 0); return d; };
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
    // Keyed by row, not name: two rows called "Math" used to share one tally and both show the total.
    const subjects = read().map((s, i) => ({ ...s, key: 'r' + i })).filter((s) => s.name && s.date);
    const rawHours = parseFloat($('ssHours').value);
    const hours = Math.round(rawHours * 2) / 2; // the field steps by 0.5
    const perWeek = parseInt($('ssDays').value, 10);
    try { localStorage.setItem(key, JSON.stringify({ rows: read(), hours: $('ssHours').value, days: $('ssDays').value })); } catch {}
    if (!subjects.length) { out.hidden = true; err.textContent = ''; return; }
    // A blank or out-of-range field used to count silently as 0.5 h (or 14 h) a day.
    if (!(hours >= 0.5 && hours <= 14) || !(perWeek >= 1 && perWeek <= 7)) { err.textContent = 'Enter your study hours per day (0.5 to 14) and days per week.'; out.hidden = true; return; }
    const today = day0();
    const future = subjects.filter((s) => parse(s.date) > today);
    if (!future.length) { err.textContent = 'Add at least one exam date after today.'; out.hidden = true; return; }
    err.textContent = '';
    const last = new Date(Math.max(...future.map((s) => parse(s.date))));
    const days = Math.round((last - today) / 86400000);
    if (days > 200) { err.textContent = 'That’s more than 200 days away. Come back nearer the time for a tighter schedule.'; out.hidden = true; return; }

    // Each day's hours are handed out in half-hour blocks, one block at a time, to the subject furthest behind its fair share.
    // Rounding each subject on its own drifted from the hours entered (3 h over 4 subjects showed 4 h; over 14 subjects, 0 h),
    // so a day's blocks always add up to exactly the hours entered and small shares build up over the days.
    const blocks = Math.round(hours * 2);
    const owed = {}; const given = {};
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
      live.forEach((s, j) => { owed[s.key] = (owed[s.key] || 0) + blocks * w[j] / total; given[s.key] = given[s.key] || 0; });
      for (let b = 0; b < blocks; b++) {
        let pick = live[0];
        live.forEach((s) => { if (owed[s.key] - given[s.key] > owed[pick.key] - given[pick.key]) pick = s; });
        given[pick.key] += 1;
        weeks[week].hours[pick.key] = (weeks[week].hours[pick.key] || 0) + 0.5;
      }
    }
    const cols = future.sort((a, b) => parse(a.date) - parse(b.date));
    const head = `<tr><th>Week</th>${cols.map((s) => `<th>${esc(s.name)}</th>`).join('')}</tr>`;
    const body = weeks.filter(Boolean).map((wk, i) => `<tr><td><strong>Week ${i + 1}</strong><span>from ${nice(wk.start)}</span></td>${cols.map((s) => `<td class="mono">${wk.hours[s.key] ? wk.hours[s.key] + ' h' : '–'}</td>`).join('')}</tr>`).join('');
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
