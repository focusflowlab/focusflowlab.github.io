// Final grade calculator: the score you need on the final to reach a target course grade.
(() => {
  const $ = (id) => document.getElementById(id);
  const form = $('final-form');
  const out = $('final-result');
  const err = $('final-error');
  const key = 'ffl-final-grade';

  try {
    const s = JSON.parse(localStorage.getItem(key) || 'null');
    if (s) { $('current').value = s.current; $('weight').value = s.weight; $('target').value = s.target; }
  } catch {}

  const need = (current, weight, target) => (target - current * (1 - weight)) / weight;
  const fmt = (n) => (Math.round(n * 10) / 10).toString();

  function describe(n) {
    if (n <= 0) return 'You’ve already got this grade, even with a zero on the final.';
    if (n > 100) return 'That’s above 100%, so this grade is out of reach unless there’s extra credit.';
    if (n > 90) return 'Tough but possible. Start with your weakest topics and use practice tests.';
    return 'Very doable with a steady plan.';
  }

  function calc() {
    const current = parseFloat($('current').value);
    const weight = parseFloat($('weight').value) / 100;
    const target = parseFloat($('target').value);
    if ([current, weight, target].some((v) => Number.isNaN(v))) { out.hidden = true; err.textContent = ''; return; }
    if (weight <= 0 || weight >= 1) { err.textContent = 'The final should be worth more than 0% and less than 100%.'; out.hidden = true; return; }
    if (current < 0 || current > 150 || target < 0 || target > 150) { err.textContent = 'Use percentages, for example 82 for 82%.'; out.hidden = true; return; }
    err.textContent = '';
    const n = need(current, weight, target);
    $('r-need').textContent = n <= 0 ? '0%' : fmt(n) + '%';
    $('r-note').textContent = describe(n);
    const rows = [['A', 90], ['B', 80], ['C', 70], ['D', 60]].map(([g, t]) => {
      const v = need(current, weight, t);
      const shown = v <= 0 ? 'Already there' : v > 100 ? 'Out of reach' : fmt(v) + '%';
      return `<tr><td>${g} (${t}%)</td><td class="mono">${shown}</td></tr>`;
    }).join('');
    $('r-table').innerHTML = rows;
    out.hidden = false;
    try { localStorage.setItem(key, JSON.stringify({ current: $('current').value, weight: $('weight').value, target: $('target').value })); } catch {}
  }

  form.addEventListener('submit', (e) => { e.preventDefault(); calc(); });
  form.addEventListener('input', calc);
  calc();
})();
