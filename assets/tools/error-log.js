// Error log: write down every missed or guessed question, say why you missed it, and get a review date.
// Everything stays in this browser (localStorage). Topic list comes from exam-topics.js.
(() => {
  const $ = (id) => document.getElementById(id);
  const TOPICS = window.EXAM_TOPICS || {};
  const KEY = 'ffl-errorlog';
  // reason: [label, days until you retest it, what usually fixes it]
  const REASONS = {
    gap: ['Knowledge gap', 7, 'Go back to the source, relearn it, then retest it after a week.'],
    misread: ['Misread the question', 2, 'Underline the key words and the question stem before you look at the options.'],
    careless: ['Careless slip', 2, 'Add a check step: re-read the answer against the question before you lock it in.'],
    time: ['Ran out of time', 3, 'Practise in timed blocks with checkpoints, and decide when to skip.'],
    strategy: ['Wrong approach', 3, 'Write the steps you should have used, then redo it with those steps.'],
    guess: ['Guessed and got lucky', 2, 'Treat it as a miss: you did not know it, so learn it now.'],
  };
  let state = { exam: 'nclex', items: [] };
  try {
    // Keep only well-formed saved items (an unknown reason or a damaged entry used to stop the log).
    const s = JSON.parse(localStorage.getItem(KEY) || 'null');
    const ymd = (v) => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v);
    if (s && Array.isArray(s.items)) {
      state.items = s.items.filter((i) => i && typeof i.exam === 'string' && typeof i.topic === 'string' && typeof i.what === 'string' && i.reason in REASONS && ymd(i.review))
        .map((i) => ({ ...i, fix: typeof i.fix === 'string' ? i.fix : '', added: ymd(i.added) ? i.added : i.review, fixed: !!i.fixed }));
      if (typeof s.exam === 'string') state.exam = s.exam;
    }
  } catch {}
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch {} };
  const iso = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  const today = () => iso(new Date());
  const plus = (n) => { const d = new Date(); d.setDate(d.getDate() + n); return iso(d); };
  const el = (tag, text, cls) => { const e = document.createElement(tag); if (text != null) e.textContent = text; if (cls) e.className = cls; return e; };

  const examSel = $('el-exam'), topicSel = $('el-topic'), reasonSel = $('el-reason');
  Object.entries(TOPICS).forEach(([slug, e]) => examSel.appendChild(new Option(e.name, slug)));
  Object.entries(REASONS).forEach(([k, v]) => reasonSel.appendChild(new Option(v[0], k)));
  if (!TOPICS[state.exam]) state.exam = Object.keys(TOPICS)[0];
  examSel.value = state.exam;
  const fillTopics = () => { topicSel.replaceChildren(); TOPICS[state.exam].topics.forEach(([n]) => topicSel.appendChild(new Option(n, n))); };

  function render() {
    const mine = state.items.filter((i) => i.exam === state.exam);
    const open = mine.filter((i) => !i.fixed);
    const due = open.filter((i) => i.review <= today()).sort((a, b) => (a.review < b.review ? -1 : 1));
    $('el-total').textContent = String(mine.length);
    $('el-open').textContent = String(open.length);
    $('el-due').textContent = String(due.length);

    const counts = {};
    mine.forEach((i) => { counts[i.reason] = (counts[i.reason] || 0) + 1; });
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
    $('el-insight').textContent = top
      ? 'Most common: ' + REASONS[top[0]][0] + ' (' + top[1] + ' of ' + mine.length + '). ' + REASONS[top[0]][2]
      : 'Log a missed question to see which kind of mistake costs you the most.';
    const bars = $('el-bars');
    bars.replaceChildren();
    Object.entries(REASONS).forEach(([k, v]) => {
      const n = counts[k] || 0;
      if (!n) return;
      const row = el('div', null, 'alloc-row');
      row.append(el('dt', v[0]), el('dd', String(n)));
      const bar = el('div', null, 'bar'); bar.setAttribute('aria-hidden', 'true');
      const fill = el('i'); fill.style.width = Math.round((n / mine.length) * 100) + '%';
      bar.append(fill); row.append(bar); bars.append(row);
    });

    const ul = $('el-list');
    ul.replaceChildren();
    const show = [...open].sort((a, b) => (a.review < b.review ? -1 : 1));
    show.forEach((i) => {
      const li = el('li');
      const info = el('div');
      info.append(el('strong', i.what));
      info.append(el('span', i.topic + ' · ' + REASONS[i.reason][0] + ' · retest ' + (i.review <= today() ? 'now' : 'on ' + i.review), 'el-meta'));
      if (i.fix) info.append(el('span', 'Fix: ' + i.fix, 'el-meta'));
      const done = el('button', 'Fixed it', 'btn btn-soft');
      done.type = 'button';
      done.setAttribute('aria-label', 'Mark fixed: ' + i.what);
      done.addEventListener('click', () => { i.fixed = true; save(); render(); });
      const del = el('button', 'Delete', 'btn btn-quiet');
      del.type = 'button';
      del.setAttribute('aria-label', 'Delete: ' + i.what);
      del.addEventListener('click', () => { state.items = state.items.filter((x) => x.id !== i.id); save(); render(); });
      const acts = el('div', null, 'el-acts'); acts.append(done, del);
      li.append(info, acts);
      if (i.review <= today()) li.classList.add('is-due');
      ul.append(li);
    });
    $('el-empty').hidden = open.length > 0;
  }

  examSel.addEventListener('change', () => { state.exam = examSel.value; save(); fillTopics(); render(); });
  $('el-form').addEventListener('submit', (ev) => {
    ev.preventDefault();
    const what = $('el-what').value.trim();
    const err = $('el-error');
    if (!what) { err.textContent = 'Write a few words about the question or concept.'; $('el-what').focus(); return; }
    err.textContent = '';
    const reason = reasonSel.value;
    state.items.push({ id: Date.now() + Math.random(), exam: state.exam, topic: topicSel.value, what: what.slice(0, 120), reason, fix: $('el-fix').value.trim().slice(0, 120), added: today(), review: plus(REASONS[reason][1]), fixed: false });
    $('el-what').value = ''; $('el-fix').value = '';
    save(); render();
    $('el-what').focus();
  });
  $('el-csv').addEventListener('click', () => {
    const q = (v) => '"' + String(v).replace(/"/g, '""') + '"';
    const rows = [['added', 'exam', 'topic', 'what', 'reason', 'fix', 'retest on', 'fixed'], ...state.items.map((i) => [i.added, TOPICS[i.exam] ? TOPICS[i.exam].name : i.exam, i.topic, i.what, REASONS[i.reason][0], i.fix || '', i.review, i.fixed ? 'yes' : 'no'])];
    const blob = new Blob([rows.map((r) => r.map(q).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'error-log.csv'; document.body.append(a); a.click(); a.remove();
  });
  fillTopics();
  render();
})();
