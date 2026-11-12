// Practice score tracker: log question sets by topic, see accuracy per topic, and get a suggested split of next week's hours.
// Everything stays in this browser (localStorage). The topic list and blueprint weights come from exam-topics.js.
(() => {
  const $ = (id) => document.getElementById(id);
  const TOPICS = window.EXAM_TOPICS || {};
  const KEY = 'ffl-scores';
  const MAX = 5000; // questions per entry; above this it is almost always a typo (one entry once read 30 of 4,566,505)
  const counted = (e) => e.total <= MAX;
  const today = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
  let state = { exam: 'nclex', target: 75, hours: 20, entries: [] };
  try {
    // Keep only well-formed saved data (a damaged or old entry could show NaN or stop the tracker).
    const s = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (s && Array.isArray(s.entries)) {
      state.entries = s.entries.filter((e) => e && typeof e.exam === 'string' && typeof e.topic === 'string' && Number.isInteger(e.right) && Number.isInteger(e.total) && e.total >= 1 && e.right >= 0 && e.right <= e.total)
        .map((e) => ({ ...e, date: /^\d{4}-\d{2}-\d{2}$/.test(e.date) ? e.date : today(), note: typeof e.note === 'string' ? e.note : '' }));
      if (typeof s.exam === 'string') state.exam = s.exam;
      if (Number(s.target) >= 1 && Number(s.target) <= 100) state.target = Number(s.target);
      if (Number(s.hours) >= 0) state.hours = Number(s.hours);
    }
  } catch {}
  const save = () => ffSave(KEY, state);
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
    // Entries saved before the limit stay listed (so they can be removed) but are left out of every figure.
    const by = new Map(TOPICS[state.exam].topics.map(([n, w]) => [n, { name: n, weight: w, right: 0, total: 0 }]));
    list.filter(counted).forEach((e) => { const t = by.get(e.topic); if (t) { t.right += e.right; t.total += e.total; } });
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
    const used = list.filter(counted);
    const right = used.reduce((a, e) => a + e.right, 0), total = used.reduce((a, e) => a + e.total, 0);
    $('sc-overall').textContent = total ? Math.round((right / total) * 100) + '%' : '-';
    $('sc-count').textContent = String(total);
    const sorted = [...list].sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.id - b.id)), sortedUsed = sorted.filter(counted);
    let trend = '-';
    if (sortedUsed.length >= 4) {
      const half = Math.floor(sortedUsed.length / 2);
      const pct = (arr) => { const t = arr.reduce((a, e) => a + e.total, 0); return t ? (arr.reduce((a, e) => a + e.right, 0) / t) * 100 : 0; };
      const d = Math.round(pct(sortedUsed.slice(half)) - pct(sortedUsed.slice(0, half)));
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
      const exact = r.total ? (r.right / r.total) * 100 : null, acc = exact === null ? null : Math.round(exact);
      // Status from the unrounded value, so 74.6% with a 75 target is not 'At target' while listed as weakest.
      const status = acc === null ? 'No data yet' : exact >= target ? 'At target' : exact >= target - 10 ? 'Close' : 'Below target';
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
      li.append(el('span', e.date + ': ' + e.topic + ', ' + e.right + ' of ' + e.total + (e.note ? ' (' + e.note + ')' : '') + (counted(e) ? '' : ' (not counted: over ' + MAX.toLocaleString('en-US') + ' questions, please remove)')));
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
  // Target 1 to 100 and hours 0 to 100 (the boxes' limits): a value outside is refused with a message and the box goes back.
  const setting = (id, key, msg) => $(id).addEventListener('change', () => {
    const f = ffField($(id));
    if (f.v === null || !f.ok) { $('sc-error').textContent = msg; $(id).value = state[key]; return; }
    $('sc-error').textContent = ''; state[key] = f.v; save(); render();
  });
  setting('sc-target', 'target', 'Target accuracy is a whole number from 1 to 100.');
  setting('sc-hours', 'hours', 'Study hours next week: 0 to 100.');
  $('sc-form').addEventListener('submit', (ev) => {
    ev.preventDefault();
    // The boxes' own limits (shared reader): a blank box is not 0, and 2.5 is not quietly saved as 2.
    const R = ffField($('sc-right')), T = ffField($('sc-total'));
    const right = R.v, total = T.v;
    const err = $('sc-error');
    if (right === null || total === null) { err.textContent = 'Enter how many you got right and how many questions in total.'; return; }
    if (Number.isFinite(total) && total > MAX) { err.textContent = 'One entry can be at most ' + MAX.toLocaleString('en-US') + ' questions. Check the total, or log a big question bank in parts.'; return; }
    if (!R.ok || !T.ok || right > total) { err.textContent = 'Use whole numbers, with right not more than the total (at least 1).'; return; }
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
