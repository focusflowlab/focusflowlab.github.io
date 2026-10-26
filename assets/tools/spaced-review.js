// Spaced review calendar: review dates for each topic, saved in this browser,
// with a calendar file (.ics) you can import into Google, Apple or Outlook calendar.
(() => {
  const $ = (id) => document.getElementById(id);
  const key = 'ffl-spaced-review';
  const GAPS = [1, 3, 7, 14, 30];
  const form = $('review-form');
  const list = $('review-list');
  const empty = $('review-empty');
  const actions = $('review-actions');

  const load = () => { try { return JSON.parse(localStorage.getItem(key) || '[]'); } catch { return []; } };
  const save = (items) => { try { localStorage.setItem(key, JSON.stringify(items)); } catch {} };
  let topics = load();

  const iso = (d) => d.toISOString().slice(0, 10);
  const parse = (s) => new Date(s + 'T12:00:00');
  const addDays = (s, n) => { const d = parse(s); d.setDate(d.getDate() + n); return iso(d); };
  const today = iso(new Date());
  const nice = (s) => parse(s).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function render() {
    empty.hidden = topics.length > 0;
    actions.hidden = topics.length === 0;
    list.innerHTML = topics.map((t, i) => {
      const dates = GAPS.map((g) => addDays(t.date, g));
      const cells = dates.map((d, n) => `<li class="${d < today ? 'past' : d === today ? 'due' : ''}"><span>Review ${n + 1}</span><strong>${nice(d)}</strong></li>`).join('');
      return `<article class="sheet review-topic">
        <div class="review-head"><h3>${esc(t.name)}</h3><button class="btn btn-quiet" type="button" data-remove="${i}">Remove</button></div>
        <p class="muted">First studied ${nice(t.date)}</p>
        <ol class="review-dates">${cells}</ol>
      </article>`;
    }).join('');
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = $('topic').value.trim();
    const date = $('studied').value || today;
    if (!name) { $('review-error').textContent = 'Add a topic name first.'; return; }
    $('review-error').textContent = '';
    topics.push({ name: name.slice(0, 80), date });
    save(topics); render();
    $('topic').value = ''; $('topic').focus();
  });

  list.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-remove]');
    if (!btn) return;
    topics.splice(Number(btn.dataset.remove), 1);
    save(topics); render();
  });

  $('clear-all').addEventListener('click', () => { topics = []; save(topics); render(); });

  $('download-ics').addEventListener('click', () => {
    const stamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z';
    const icsEsc = (s) => s.replace(/[\\,;]/g, (c) => '\\' + c);
    const events = [];
    topics.forEach((t, ti) => GAPS.forEach((g, n) => {
      const d = addDays(t.date, g).replace(/-/g, '');
      const end = addDays(t.date, g + 1).replace(/-/g, '');
      events.push(['BEGIN:VEVENT', `UID:ffl-${ti}-${n}-${d}@thefocusflowlab.com`, `DTSTAMP:${stamp}`,
        `DTSTART;VALUE=DATE:${d}`, `DTEND;VALUE=DATE:${end}`, `SUMMARY:${icsEsc('Review: ' + t.name)} (${n + 1} of ${GAPS.length})`,
        'DESCRIPTION:Recall first\\, then check your notes. From thefocusflowlab.com/tools/spaced-review/', 'END:VEVENT'].join('\r\n'));
    }));
    const ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//FocusFlow Lab//Spaced Review//EN', 'CALSCALE:GREGORIAN', ...events, 'END:VCALENDAR'].join('\r\n');
    const url = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
    const a = document.createElement('a'); a.href = url; a.download = 'spaced-review.ics';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  $('studied').value = today;
  render();
})();
