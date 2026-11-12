// GPA calculator (US 4.0 scale): semester GPA, weighted GPA (Honors +0.5, AP/IB +1.0),
// cumulative GPA, and the GPA you need next term to reach a target.
(() => {
  const $ = (id) => document.getElementById(id);
  const POINTS = { 'A+': 4.0, A: 4.0, 'A-': 3.7, 'B+': 3.3, B: 3.0, 'B-': 2.7, 'C+': 2.3, C: 2.0, 'C-': 1.7, 'D+': 1.3, D: 1.0, 'D-': 0.7, F: 0 };
  const BONUS = { regular: 0, honors: 0.5, ap: 1.0 };
  const key = 'ffl-gpa';
  const list = $('gpa-rows');
  const esc = (s) => String(s).replace(/"/g, '&quot;');

  const options = Object.keys(POINTS).map((g) => `<option value="${g}">${g}</option>`).join('');
  function addRow(row = { name: '', credits: 3, grade: 'A', level: 'regular' }) {
    const li = document.createElement('li');
    li.className = 'gpa-row';
    li.innerHTML = `
      <input type="text" aria-label="Course name" placeholder="Course" maxlength="60" value="${esc(row.name)}">
      <input type="number" aria-label="Credits" min="0" max="12" step="0.5" value="${row.credits}" inputmode="decimal">
      <select aria-label="Grade">${options}</select>
      <select aria-label="Course level"><option value="regular">Regular</option><option value="honors">Honors</option><option value="ap">AP / IB</option></select>
      <button class="btn btn-quiet row-remove" type="button" aria-label="Remove course" title="Remove course">&times;</button>`;
    const [gradeSel, levelSel] = li.querySelectorAll('select');
    gradeSel.value = row.grade;
    levelSel.value = row.level || 'regular';
    list.appendChild(li);
  }

  // A box is blank (null), a number inside its own min/max (shared reader), or bad (NaN).
  const read = (el) => { const f = ffField(el); return f.v === null ? null : f.ok ? f.v : NaN; };
  let badCredits = false;
  function rows() {
    badCredits = false;
    return [...list.querySelectorAll('.gpa-row')].map((li) => {
      const [name, credits] = li.querySelectorAll('input');
      const [grade, level] = li.querySelectorAll('select');
      const c = read(credits);
      if (Number.isNaN(c)) badCredits = true;
      return { name: name.value, credits: c || 0, grade: grade.value, level: level.value };
    });
  }

  function calc() {
    const r = rows();
    const msgs = badCredits ? ['Credits per course are 0 to 12; a course outside that is left out.'] : [];
    const credits = r.reduce((s, x) => s + x.credits, 0);
    const points = r.reduce((s, x) => s + x.credits * POINTS[x.grade], 0);
    // Weighted points: an F stays 0 whatever the level, as most schools do.
    const wpoints = r.reduce((s, x) => s + x.credits * (POINTS[x.grade] > 0 ? POINTS[x.grade] + BONUS[x.level] : 0), 0);
    const anyWeighted = r.some((x) => x.level !== 'regular');
    $('r-term').textContent = credits ? (points / credits).toFixed(2) : '–';
    $('r-weighted').textContent = credits && anyWeighted ? (wpoints / credits).toFixed(2) : '–';
    $('r-credits').textContent = Math.round(credits * 100) / 100;

    // Box limits: GPA 0 to 5 (allows a weighted GPA), credits so far 1 to 1,000, next term 1 to 100.
    const prevGpa = read($('prevGpa')), prevCredits = read($('prevCredits'));
    const target = read($('targetGpa')), nextCredits = read($('nextCredits'));
    if (Number.isNaN(prevGpa)) msgs.push('Current GPA is 0 to 5.');
    if (Number.isNaN(prevCredits)) msgs.push('Credits so far are 1 to 1,000.');
    if (Number.isNaN(target)) msgs.push('Target GPA is 0 to 5.');
    if (Number.isNaN(nextCredits)) msgs.push('Credits next term are 1 to 100.');
    $('gpa-error').textContent = msgs.join(' ');
    const ok = (v) => v !== null && !Number.isNaN(v);
    const hasPrev = ok(prevGpa) && ok(prevCredits);
    $('r-cum').textContent = hasPrev && credits ? ((prevGpa * prevCredits + points) / (prevCredits + credits)).toFixed(2) : '–';

    // What GPA do I need next term to reach a target?
    const out = $('r-need');
    if (ok(target) && ok(nextCredits)) {
      const baseCredits = (hasPrev ? prevCredits : 0) + credits;
      const basePoints = (hasPrev ? prevGpa * prevCredits : 0) + points;
      if (!baseCredits) { out.textContent = 'Add your courses or past GPA first.'; }
      else {
        const need = (target * (baseCredits + nextCredits) - basePoints) / nextCredits;
        out.textContent = need <= 0 ? 'You’re already there.' : need > 4 ? `You’d need ${need.toFixed(2)}, above a 4.0, so it will take more than one term.` : `You need a ${need.toFixed(2)} GPA over your next ${nextCredits} credits.`;
      }
    } else {
      out.textContent = '';
    }
    try { localStorage.setItem(key, JSON.stringify({ rows: r, prevGpa: $('prevGpa').value, prevCredits: $('prevCredits').value, targetGpa: $('targetGpa').value, nextCredits: $('nextCredits').value })); } catch {}
  }

  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(key) || 'null'); } catch {}
  // Keep only well-formed saved rows (a damaged or old entry used to stop the whole calculator).
  if (!saved || typeof saved !== 'object') saved = null;
  const rowsOk = saved && Array.isArray(saved.rows) ? saved.rows.filter((r) => r && typeof r === 'object').map((r) => ({
    name: typeof r.name === 'string' ? r.name : '', credits: Math.max(0, Number(r.credits) || 0),
    grade: r.grade in POINTS ? r.grade : 'A', level: r.level in BONUS ? r.level : 'regular' })) : [];
  (rowsOk.length ? rowsOk : [{ name: '', credits: 3, grade: 'A' }, { name: '', credits: 3, grade: 'B+' }, { name: '', credits: 4, grade: 'B' }]).forEach(addRow);
  if (saved) ['prevGpa', 'prevCredits', 'targetGpa', 'nextCredits'].forEach((k) => { if (saved[k] != null && Number.isFinite(Number(saved[k]))) $(k).value = saved[k]; });

  $('add-course').addEventListener('click', () => { addRow(); calc(); list.lastElementChild.querySelector('input').focus(); });
  list.addEventListener('click', (e) => {
    if (!e.target.closest('.row-remove')) return;
    e.target.closest('.gpa-row').remove();
    calc();
  });
  $('gpa-form').addEventListener('input', calc);
  $('gpa-form').addEventListener('change', calc);
  $('gpa-form').addEventListener('submit', (e) => { e.preventDefault(); calc(); });
  calc();
})();
