// Practice score tracker: log question sets by topic, see accuracy per topic, and get a suggested split of next week's hours.
// Everything stays in this browser (localStorage). The topic list and blueprint weights come from exam-topics.js.
(() => {
  const $ = (id) => document.getElementById(id);
  const TOPICS = window.EXAM_TOPICS || {};
  const KEY = 'ffl-scores';
  let state = { exam: 'nclex', target: 75, hours: 20, entries: [] };
  try { const s = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s && Array.isArray(s.entries)) state = { ...state, ...s }; } catch {}
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch {} };
  const today = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
  const el = (tag, text, cls) => { const e = document.createElement(tag); if (text != null) e.textContent = text; if (cls) e.className = cls; return e; };

  const examSel = $('sc-exam'), topicSel = $('sc-topic');
  Object.entries(TOPICS).forEach(([slug, e]) => examSel.appendChild(new Option(e.name, slug)));
  if (!TOPICS[state.exam]) state.exam = Object.keys(TOPICS)[0];
  examSel.value = state.exam;
  $('sc-date').value = today();
  $('sc-target').value = state.target;
  $('sc-hours').value = state.hours;

  function fillTopics() {
    topicSel.replaceChildren();
    TOPICS[state.exam].topics.forEach(([n]) => topicSel.appendChild(new Option(n, n)));
  }

  function stats() {
    const list = state.entries.filter((e) => e.exam === state.exam);
    const by = new Map(TOPICS[state.exam].topics.map(([n, w]) => [n, { name: n, weight: w, right: 0, total: 0 }]));
    list.forEach((e) => { const t = by.get(e.topic); if (t) { t.right += e.right; t.total += e.total; } });
    return { list, rows: [...by.values()] };
  }

  // Suggested share: blueprint weight, raised when a topic is below your target, and raised a little when you have no data yet.
  function suggest(rows, target) {
    const raw = rows.map((r) => {
      if (!r.total) return r.weight * 1.3;
      const gap = Math.max(0, target - (r.right / r.total) * 100) / Math.max(target, 1);
      return r.weight * (1 + 2 * gap);
    });
    const sum = raw.reduce((a, b) => a + b, 0) || 1;
    return raw.map((v) => v / sum);
  }

  function render() {
    const { list, rows } = stats();
    const target = state.target;
    const right = list.reduce((a, e) => a + e.right, 0), total = list.reduce((a, e) => a + e.total, 0);
    $('sc-overall').textContent = total ? Math.round((right / total) * 100) + '%' : '-';
    $('sc-count').textContent = String(total);
    const sorted = [...list].sort((a, b) => (a.date < b.date ? -1 : 1));
    let trend = '-';
    if (sorted.length >= 4) {
      const half = Math.floor(sorted.length / 2);
      const pct = (arr) => { const t = arr.reduce((a, e) => a + e.total, 0); return t ? (arr.reduce((a, e) => a + e.right, 0) / t) * 100 : 0; };
      const d = Math.round(pct(sorted.slice(half)) - pct(sorted.slice(0, half)));
      trend = (d > 0 ? '+' : '') + d + ' pts';
    }
    $('sc-trend').textContent = trend;

    const share = suggest(rows, target);
    const hours = Number(state.hours) || 0;
    const body = $('sc-table');
    body.replaceChildren();
    const wsum = rows.reduce((a, r) => a + r.weight, 0) || 1;
    // Whole percents and half hours shared by largest remainder, so the column adds up to 100% and to the hours entered.
    const split = (units) => {
      const raw = share.map((s) => s * units), c = raw.map(Math.floor);
      let spare = units - c.reduce((a, b) => a + b, 0);
      raw.map((v, i) => [v - c[i], i]).sort((a, b) => b[0] - a[0]).forEach(([, i]) => { if (spare > 0) { c[i]++; spare--; } });
      return c;
    };
    const pcts = split(100), halves = split(Math.round(hours * 2));
    rows.map((r, i) => ({ r, s: share[i], pct: pcts[i], h: halves[i] / 2 })).sort((a, b) => b.s - a.s).forEach(({ r, pct, h }) => {
      const tr = el('tr');
      const acc = r.total ? Math.round((r.right / r.total) * 100) : null;
      const status = acc === null ? 'No data yet' : acc >= target ? 'At target' : acc >= target - 10 ? 'Close' : 'Below target';
      tr.append(el('th', r.name));
      tr.lastChild.setAttribute('scope', 'row');
      tr.append(el('td', acc === null ? '-' : acc + '% (' + r.right + '/' + r.total + ')'));
      tr.append(el('td', status, 'sc-' + status.toLowerCase().replace(/[^a-z]+/g, '-')));
      tr.append(el('td', Math.round((r.weight / wsum) * 100) + '%'));
      tr.append(el('td', pct + '%' + (hours ? ' (' + h + ' h)' : '')));
      body.append(tr);
    });

    const weak = rows.filter((r) => r.total && (r.right / r.total) * 100 < target).sort((a, b) => a.right / a.total - b.right / b.total).slice(0, 3);
    $('sc-advice').textContent = !total
      ? 'Add your first practice set to see where your hours should go.'
      : weak.length
        ? 'Weakest so far: ' + weak.map((r) => r.name + ' (' + Math.round((r.right / r.total) * 100) + '%)').join(', ') + '. Give these the most time next week, and redo the missed questions.'
        : 'Every topic with data is at or above your target. Keep mixing topics and check the ones with no data yet.';

    const planLink = $('sc-plan');
    planLink.hidden = !weak.some((r) => r.total >= 10);
    $('sc-plan-link').href = '/study-plan/' + state.exam + '/';

    const ul = $('sc-list');
    ul.replaceChildren();
    sorted.slice().reverse().forEach((e) => {
      const li = el('li');
      li.append(el('span', e.date + ': ' + e.topic + ', ' + e.right + ' of ' + e.total + (e.note ? ' (' + e.note + ')' : '')));
      const b = el('button', 'Remove', 'btn btn-quiet');
      b.type = 'button';
      b.setAttribute('aria-label', 'Remove entry from ' + e.date + ' for ' + e.topic);
      b.addEventListener('click', () => { state.entries = state.entries.filter((x) => x.id !== e.id); save(); render(); });
      li.append(b);
      ul.append(li);
    });
    $('sc-empty').hidden = list.length > 0;
  }

  examSel.addEventListener('change', () => { state.exam = examSel.value; save(); fillTopics(); render(); });
  $('sc-target').addEventListener('change', () => { state.target = Math.min(100, Math.max(1, Number($('sc-target').value) || 75)); save(); render(); });
  $('sc-hours').addEventListener('change', () => { state.hours = Math.max(0, Number($('sc-hours').value) || 0); save(); render(); });
  $('sc-form').addEventListener('submit', (ev) => {
    ev.preventDefault();
    const right = Math.floor(Number($('sc-right').value)), total = Math.floor(Number($('sc-total').value));
    const err = $('sc-error');
    if (!(total >= 1) || !(right >= 0) || right > total) { err.textContent = 'Enter how many you got right and the total, with right not more than total.'; return; }
    err.textContent = '';
    state.entries.push({ id: Date.now() + Math.random(), exam: state.exam, topic: topicSel.value, date: $('sc-date').value || today(), right, total, note: $('sc-note').value.trim().slice(0, 60) });
    $('sc-right').value = ''; $('sc-total').value = ''; $('sc-note').value = '';
    save(); render();
    $('sc-right').focus();
  });
  $('sc-csv').addEventListener('click', () => {
    const q = (v) => '"' + String(v).replace(/"/g, '""') + '"';
    const rows = [['date', 'exam', 'topic', 'right', 'total', 'note'], ...state.entries.map((e) => [e.date, TOPICS[e.exam] ? TOPICS[e.exam].name : e.exam, e.topic, e.right, e.total, e.note || ''])];
    const blob = new Blob([rows.map((r) => r.map(q).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'practice-scores.csv'; document.body.append(a); a.click(); a.remove();
  });
  $('sc-clear').addEventListener('click', () => {
    if (!state.entries.some((e) => e.exam === state.exam)) return;
    if (confirm('Delete all saved scores for ' + TOPICS[state.exam].name + ' in this browser?')) { state.entries = state.entries.filter((e) => e.exam !== state.exam); save(); render(); }
  });
  fillTopics();
  render();
})();
