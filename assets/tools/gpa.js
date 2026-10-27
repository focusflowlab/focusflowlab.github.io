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

  function rows() {
    return [...list.querySelectorAll('.gpa-row')].map((li) => {
      const [name, credits] = li.querySelectorAll('input');
      const [grade, level] = li.querySelectorAll('select');
      return { name: name.value, credits: parseFloat(credits.value) || 0, grade: grade.value, level: level.value };
    });
  }

  function calc() {
    const r = rows();
    const credits = r.reduce((s, x) => s + x.credits, 0);
    const points = r.reduce((s, x) => s + x.credits * POINTS[x.grade], 0);
    // Weighted points: an F stays 0 whatever the level, as most schools do.
    const wpoints = r.reduce((s, x) => s + x.credits * (POINTS[x.grade] > 0 ? POINTS[x.grade] + BONUS[x.level] : 0), 0);
    const anyWeighted = r.some((x) => x.level !== 'regular');
    $('r-term').textContent = credits ? (points / credits).toFixed(2) : '–';
    $('r-weighted').textContent = credits && anyWeighted ? (wpoints / credits).toFixed(2) : '–';
    $('r-credits').textContent = credits;

    const prevGpa = parseFloat($('prevGpa').value);
    const prevCredits = parseFloat($('prevCredits').value);
    const hasPrev = !Number.isNaN(prevGpa) && !Number.isNaN(prevCredits) && prevCredits > 0 && prevGpa >= 0 && prevGpa <= 5;
    $('r-cum').textContent = hasPrev && credits ? ((prevGpa * prevCredits + points) / (prevCredits + credits)).toFixed(2) : '–';

    // What GPA do I need next term to reach a target?
    const target = parseFloat($('targetGpa').value);
    const nextCredits = parseFloat($('nextCredits').value);
    const out = $('r-need');
    if (!Number.isNaN(target) && !Number.isNaN(nextCredits) && nextCredits > 0) {
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
  (saved?.rows?.length ? saved.rows : [{ name: '', credits: 3, grade: 'A' }, { name: '', credits: 3, grade: 'B+' }, { name: '', credits: 4, grade: 'B' }]).forEach(addRow);
  if (saved) ['prevGpa', 'prevCredits', 'targetGpa', 'nextCredits'].forEach((k) => { if (saved[k] != null) $(k).value = saved[k]; });

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
