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

  function calc(submitted) {
    // The boxes' own limits (shared reader); a blank box only gets a message when the button is pressed.
    const C = ffField($('current')), W = ffField($('weight')), G = ffField($('target'));
    if ([C, W, G].some((f) => f.v === null)) { out.hidden = true; err.textContent = submitted === true ? 'Fill in all three boxes, as percentages.' : ''; return; }
    if (!W.ok) { err.textContent = 'The final should be worth 1% to 99% of your grade.'; out.hidden = true; return; }
    if (!C.ok || !G.ok) { err.textContent = 'Use percentages from 0 to 150, for example 82 for 82%.'; out.hidden = true; return; }
    const current = C.v, weight = W.v / 100, target = G.v;
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

  form.addEventListener('submit', (e) => { e.preventDefault(); calc(true); });
  form.addEventListener('input', () => calc());
  calc();
})();
