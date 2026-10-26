// GPA calculator (US 4.0 scale): semester GPA from letter grades and credits, plus cumulative GPA.
(() => {
  const $ = (id) => document.getElementById(id);
  const POINTS = { 'A+': 4.0, A: 4.0, 'A-': 3.7, 'B+': 3.3, B: 3.0, 'B-': 2.7, 'C+': 2.3, C: 2.0, 'C-': 1.7, 'D+': 1.3, D: 1.0, 'D-': 0.7, F: 0 };
  const key = 'ffl-gpa';
  const list = $('gpa-rows');

  const options = Object.keys(POINTS).map((g) => `<option value="${g}">${g}</option>`).join('');
  function addRow(row = { name: '', credits: 3, grade: 'A' }) {
    const li = document.createElement('li');
    li.className = 'gpa-row';
    li.innerHTML = `
      <input type="text" aria-label="Course name" placeholder="Course" maxlength="60" value="${row.name.replace(/"/g, '&quot;')}">
      <input type="number" aria-label="Credits" min="0" max="12" step="0.5" value="${row.credits}" inputmode="decimal">
      <select aria-label="Grade">${options}</select>
      <button class="btn btn-quiet row-remove" type="button" aria-label="Remove course">Remove</button>`;
    li.querySelector('select').value = row.grade;
    list.appendChild(li);
  }

  function rows() {
    return [...list.querySelectorAll('.gpa-row')].map((li) => {
      const [name, credits, grade] = li.querySelectorAll('input, select');
      return { name: name.value, credits: parseFloat(credits.value) || 0, grade: grade.value };
    });
  }

  function calc() {
    const r = rows();
    const credits = r.reduce((s, x) => s + x.credits, 0);
    const points = r.reduce((s, x) => s + x.credits * POINTS[x.grade], 0);
    const term = credits ? points / credits : 0;
    $('r-term').textContent = credits ? term.toFixed(2) : '–';
    $('r-credits').textContent = credits;

    const prevGpa = parseFloat($('prevGpa').value);
    const prevCredits = parseFloat($('prevCredits').value);
    if (!Number.isNaN(prevGpa) && !Number.isNaN(prevCredits) && prevCredits > 0 && prevGpa >= 0 && prevGpa <= 4.0) {
      const cum = (prevGpa * prevCredits + points) / (prevCredits + credits);
      $('r-cum').textContent = cum.toFixed(2);
    } else {
      $('r-cum').textContent = '–';
    }
    try { localStorage.setItem(key, JSON.stringify({ rows: r, prevGpa: $('prevGpa').value, prevCredits: $('prevCredits').value })); } catch {}
  }

  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(key) || 'null'); } catch {}
  (saved?.rows?.length ? saved.rows : [{ name: '', credits: 3, grade: 'A' }, { name: '', credits: 3, grade: 'B+' }, { name: '', credits: 4, grade: 'B' }]).forEach(addRow);
  if (saved) { $('prevGpa').value = saved.prevGpa || ''; $('prevCredits').value = saved.prevCredits || ''; }

  $('add-course').addEventListener('click', () => { addRow(); calc(); list.lastElementChild.querySelector('input').focus(); });
  list.addEventListener('click', (e) => {
    if (!e.target.closest('.row-remove')) return;
    e.target.closest('.gpa-row').remove();
    calc();
  });
  document.getElementById('gpa-form').addEventListener('input', calc);
  document.getElementById('gpa-form').addEventListener('submit', (e) => { e.preventDefault(); calc(); });
  calc();
})();
