// Test time calculator: minutes per question and pacing checkpoints.
(() => {
  const $ = (id) => document.getElementById(id);
  const form = $('pace-form');
  const out = $('pace-result');
  const key = 'ffl-pace';
  try {
    const s = JSON.parse(localStorage.getItem(key) || 'null');
    if (s) { $('totalMin').value = s.t; $('questions').value = s.q; $('reviewPct').value = s.r; }
  } catch {}
  // Round the total first: rounding only the minutes part showed "1 h 60 min" for 119.5.
  const fmt = (m) => { const t = Math.round(m), h = Math.floor(t / 60), r = t % 60; return h ? h + ' h ' + r + ' min' : r + ' min'; };
  function calc() {
    const t = Number($('totalMin').value), q = Number($('questions').value), r = Number($('reviewPct').value);
    const err = $('pace-error');
    if (!(t >= 1) || !(q >= 1)) { err.textContent = 'Enter the total minutes and the number of questions.'; out.hidden = true; return; }
    err.textContent = '';
    const review = t * r / 100, work = t - review, per = work / q;
    $('r-min').textContent = (Math.round(per * 100) / 100) + ' min';
    $('r-sec').textContent = Math.round(per * 60) + ' sec';
    $('r-review').textContent = Math.round(review) + ' min';
    // Checkpoint times follow the question number (n x pace), and tiny tests skip "question 0" and repeats.
    const marks = [...new Set([0.25, 0.5, 0.75].map((f) => Math.round(q * f)))].filter((n) => n >= 1 && n < q);
    $('r-points').textContent = marks.map((n) => 'question ' + n + ' by ' + fmt(per * n) + ', ').join('') + 'finish question ' + q + ' by ' + fmt(work) + '.';
    out.hidden = false;
    try { localStorage.setItem(key, JSON.stringify({ t, q, r })); } catch {}
  }
  form.addEventListener('submit', (e) => { e.preventDefault(); calc(); });
  form.addEventListener('change', calc);
  calc();
})();
