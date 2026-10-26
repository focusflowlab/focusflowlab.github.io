// Weighted grade calculator: course grade from weighted categories (homework, quizzes, exams...).
(() => {
  const $ = (id) => document.getElementById(id);
  const list = $('wg-rows');
  const key = 'ffl-weighted-grade';

  function addRow(row = { name: '', weight: '', score: '' }) {
    const li = document.createElement('li');
    li.className = 'wg-row';
    li.innerHTML = `
      <input type="text" aria-label="Category" placeholder="Category" maxlength="40" value="${String(row.name).replace(/"/g, '&quot;')}">
      <input type="number" aria-label="Weight in percent" placeholder="Weight %" min="0" max="100" step="0.5" value="${row.weight}" inputmode="decimal">
      <input type="number" aria-label="Score in percent" placeholder="Score %" min="0" max="150" step="0.1" value="${row.score}" inputmode="decimal">
      <button class="btn btn-quiet row-remove" type="button" aria-label="Remove category">Remove</button>`;
    list.appendChild(li);
  }

  function calc() {
    const rows = [...list.querySelectorAll('.wg-row')].map((li) => {
      const [n, w, s] = li.querySelectorAll('input');
      return { name: n.value, weight: parseFloat(w.value), score: parseFloat(s.value), rw: w.value, rs: s.value };
    });
    const graded = rows.filter((r) => !Number.isNaN(r.weight) && !Number.isNaN(r.score) && r.weight > 0);
    const totalWeight = rows.reduce((s, r) => s + (Number.isNaN(r.weight) ? 0 : r.weight), 0);
    const gradedWeight = graded.reduce((s, r) => s + r.weight, 0);
    const sum = graded.reduce((s, r) => s + r.weight * r.score, 0);
    $('r-grade').textContent = gradedWeight ? (sum / gradedWeight).toFixed(1) + '%' : '–';
    $('r-weight').textContent = Math.round(totalWeight * 10) / 10 + '%';
    $('r-done').textContent = Math.round(gradedWeight * 10) / 10 + '%';
    const note = $('r-note');
    if (totalWeight > 100.05) note.textContent = 'Your weights add up to more than 100%. Check your syllabus.';
    else if (gradedWeight && gradedWeight < totalWeight) note.textContent = 'This is your grade so far, from the categories you’ve scored. Leave a score blank for work not graded yet.';
    else if (gradedWeight && totalWeight < 99.95) note.textContent = 'Your weights add up to less than 100%, so this is your grade on the work so far.';
    else note.textContent = '';
    try { localStorage.setItem(key, JSON.stringify(rows.map((r) => ({ name: r.name, weight: r.rw, score: r.rs })))); } catch {}
  }

  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(key) || 'null'); } catch {}
  (saved?.length ? saved : [
    { name: 'Homework', weight: 20, score: '' },
    { name: 'Quizzes', weight: 15, score: '' },
    { name: 'Midterm', weight: 25, score: '' },
    { name: 'Final exam', weight: 40, score: '' }
  ]).forEach(addRow);

  $('add-category').addEventListener('click', () => { addRow(); calc(); list.lastElementChild.querySelector('input').focus(); });
  list.addEventListener('click', (e) => { if (e.target.closest('.row-remove')) { e.target.closest('.wg-row').remove(); calc(); } });
  $('wg-form').addEventListener('input', calc);
  $('wg-form').addEventListener('submit', (e) => { e.preventDefault(); calc(); });
  calc();
})();
