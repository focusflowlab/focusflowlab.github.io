// Behaviour tests for the calculators and exports (the layout scan does not check numbers or dates).
// Run like the layout scan: copy to $TEMP/hmtools (needs puppeteer-core), start `python -m http.server 8765` in the repo root, then
//   cd $TEMP/hmtools && cp <repo>/_tools/behaviour-tests.mjs . && node behaviour-tests.mjs
// Exits 1 if anything fails.
import puppeteer from 'puppeteer-core';
import { existsSync } from 'fs';

const BASE = process.env.BASE || 'http://localhost:8765';
const exe = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const browser = await puppeteer.launch({ executablePath: exe, headless: 'new' });
let failed = 0;
const check = (ok, msg) => { console.log((ok ? 'PASS ' : 'FAIL ') + msg); if (!ok) failed++; };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const newPage = async (opts = {}) => {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  if (opts.tz) await page.emulateTimezone(opts.tz);
  if (opts.fixed) { // freeze "now" at a UTC instant so local and UTC dates differ
    await page.evaluateOnNewDocument((ms) => {
      const Real = Date;
      class Fake extends Real { constructor(...a) { if (a.length === 0) super(ms); else super(...a); } static now() { return ms; } }
      window.Date = Fake;
    }, opts.fixed);
  }
  return page;
};
const dateIn = (days) => { const d = new Date(Date.now() + days * 864e5); return d.toISOString().slice(0, 10); };

// 1. Schedule maker: the hours shown always add up to the hours entered, and no subject is starved.
for (const [hours, n] of [[3, 4], [3, 5], [3, 14], [0.5, 3], [2.5, 7], [14, 5], [1, 9]]) {
  const page = await newPage();
  await page.goto(`${BASE}/tools/study-schedule-maker/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const exam = dateIn(28);
  const res = await page.evaluate(async (hours, n, exam) => {
    const list = document.getElementById('ss-rows');
    list.innerHTML = '';
    document.getElementById('ss-rows').dispatchEvent(new Event('x'));
    for (let i = 0; i < n; i++) document.getElementById('add-subject').click();
    [...list.querySelectorAll('.ss-row')].forEach((li, i) => {
      const [name, date, pr] = li.querySelectorAll('input, select');
      name.value = 'Subject ' + (i + 1); date.value = exam; pr.value = '2';
    });
    document.getElementById('ssHours').value = hours;
    document.getElementById('ssDays').value = '7';
    document.getElementById('ss-form').requestSubmit();
    await new Promise((r) => setTimeout(r, 300));
    const rows = [...document.querySelectorAll('#ss-table tbody tr')].map((tr) => [...tr.querySelectorAll('td.mono')].map((td) => parseFloat(td.textContent) || 0));
    return rows;
  }, hours, n, exam);
  const totals = res.reduce((acc, r) => r.map((v, i) => (acc[i] || 0) + v), []);
  const all = totals.reduce((a, b) => a + b, 0);
  const days = 28; // every day until the exam date is a study day (7 days a week)
  check(Math.abs(all - hours * days) < 1e-9, `schedule ${hours} h/day x ${n} subjects: total ${all} h = ${hours * days} h`);
  check(totals.every((t) => t > 0), `schedule ${hours} h/day x ${n} subjects: every subject gets time (min ${Math.min(...totals)} h)`);
  check(Math.max(...totals) - Math.min(...totals) <= 1, `schedule ${hours} h/day x ${n} subjects: equal priorities stay within 1 h of each other`);
  await page.close();
}

// 2. Calendar export: every event ends after it starts, on the right date, for long days too.
for (const hours of [4, 6, 8, 10, 14]) {
  const page = await newPage();
  await page.goto(`${BASE}/study-plan/gre/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => { window.__blobs = []; const real = URL.createObjectURL.bind(URL); URL.createObjectURL = (b) => { window.__blobs.push(b); return real(b); }; HTMLAnchorElement.prototype.click = function () {}; });
  await page.evaluate((hours, exam) => {
    const f = document.querySelector('form');
    const set = (id, v) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };
    set('examDate', exam); set('hoursPerDay', hours); set('daysPerWeek', '5');
    f.requestSubmit();
  }, hours, dateIn(35));
  await wait(800);
  await page.evaluate(() => document.getElementById('add-cal').click());
  await wait(500);
  const ics = await page.evaluate(async () => (window.__blobs[0] ? await window.__blobs[0].text() : ''));
  const text = ics.replace(/\r\n /g, '');
  const events = [...text.matchAll(/BEGIN:VEVENT[\s\S]*?END:VEVENT/g)].map((m) => m[0]).filter((e) => !e.includes('VALUE=DATE'));
  const stamp = (s) => { const m = s.match(/(\d{4})(\d\d)(\d\d)T(\d\d)(\d\d)(\d\d)/); return new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +m[6]); };
  const parsed = events.map((e) => ({ s: stamp(e.match(/DTSTART:(\S+)/)[1]), e: stamp(e.match(/DTEND:(\S+)/)[1]) }));
  const mins = parsed.map((p) => (p.e - p.s) / 60000);
  check(parsed.length > 0, `calendar ${hours} h/day: ${parsed.length} events found`);
  check(parsed.every((p) => p.e > p.s), `calendar ${hours} h/day: every event ends after it starts`);
  check(parsed.every((p) => { const midnight = new Date(p.s.getFullYear(), p.s.getMonth(), p.s.getDate() + 1); return p.e <= midnight; }), `calendar ${hours} h/day: no event runs past midnight`);
  check(Math.max(...mins) === hours * 60, `calendar ${hours} h/day: longest event is ${Math.max(...mins) / 60} h`);
  check(parsed.every((p) => p.s.getHours() >= 6), `calendar ${hours} h/day: every event starts at 6 am or later`);
  await page.close();
}

// 3. Flashcards climb through all six intervals and stay on 60 days.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/flashcards/`, { waitUntil: 'networkidle0' });
  const seen = [];
  for (const step of [0, 1, 2, 3, 4, 5, 6]) {
    const days = await page.evaluate(async (step) => {
      const local = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      localStorage.setItem('ffl-flashcards', JSON.stringify([{ front: 'Q', back: 'A', step, due: local(new Date()) }]));
      return 0;
    }, step);
    await page.reload({ waitUntil: 'networkidle0' });
    await page.click('#fc-start'); await page.click('#fc-reveal'); await page.click('#fc-good');
    const out = await page.evaluate(() => {
      const c = JSON.parse(localStorage.getItem('ffl-flashcards'))[0];
      const [y, m, d] = c.due.split('-').map(Number); const t = new Date(); const t0 = new Date(t.getFullYear(), t.getMonth(), t.getDate());
      return { step: c.step, days: Math.round((new Date(y, m - 1, d) - t0) / 864e5) };
    });
    seen.push(out);
  }
  const expected = [1, 3, 7, 14, 30, 60, 60];
  check(JSON.stringify(seen.map((s) => s.days)) === JSON.stringify(expected), `flashcards intervals after a correct answer: ${seen.map((s) => s.days).join(', ')} (expected ${expected.join(', ')})`);
  check(Math.max(...seen.map((s) => s.step)) === 6, 'flashcards reach step 6 (the 60-day step) and stop there');
  await page.close();
}

// 4. Dates follow the local calendar, not UTC.
for (const [tz, fixed, localDay, label] of [
  ['Asia/Karachi', Date.UTC(2026, 10, 11, 22, 0, 0), '2026-11-12', 'Lahore 3 AM (UTC is still the 11th)'],
  ['America/Los_Angeles', Date.UTC(2026, 10, 12, 3, 0, 0), '2026-11-11', 'Los Angeles evening (UTC is already the 12th)'],
]) {
  let page = await newPage({ tz, fixed });
  await page.goto(`${BASE}/tools/flashcards/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  await page.type('#fcFront', 'Q'); await page.type('#fcBack', 'A');
  await page.evaluate(() => document.getElementById('fc-add').requestSubmit());
  const due = await page.evaluate(() => (JSON.parse(localStorage.getItem('ffl-flashcards') || '[]')[0] || {}).due);
  check(due === localDay, `flashcards new card due ${due} (local day ${localDay}) - ${label}`);
  await page.close();

  page = await newPage({ tz, fixed });
  await page.evaluateOnNewDocument(() => { const real = Storage.prototype.getItem; window.__keys = []; Storage.prototype.getItem = function (k) { window.__keys.push(k); return real.call(this, k); }; });
  await page.goto(`${BASE}/tools/focus-timer/`, { waitUntil: 'networkidle0' });
  const keys = await page.evaluate(() => window.__keys.filter((k) => k.startsWith('ffl-timer-')));
  check(keys.includes('ffl-timer-' + localDay), `focus timer day key ${keys[0]} (local day ${localDay}) - ${label}`);
  await page.close();

  page = await newPage({ tz, fixed });
  await page.goto(`${BASE}/tools/spaced-review/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  await page.type('#topic', 'Topic');
  await page.evaluate(() => document.getElementById('review-form').requestSubmit());
  await wait(300);
  const res = await page.evaluate((localDay) => {
    const [y, m, d] = localDay.split('-').map(Number);
    const first = new Date(y, m - 1, d + 1, 12);
    const want = first.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });
    return { want, text: document.getElementById('review-list').innerText };
  }, localDay);
  check(res.text.includes(res.want), `spaced review first review is ${res.want} (the day after local ${localDay}) - ${label}`);
  await page.close();
}

// 5. Plan generator across a daylight-saving change (US): one session per day, no day skipped or doubled, exam-day event one day long.
const icsOf = async (page, exam, hours, days) => {
  await page.goto(`${BASE}/study-plan/gre/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => { localStorage.clear(); window.__blobs = []; const real = URL.createObjectURL.bind(URL); URL.createObjectURL = (b) => { window.__blobs.push(b); return real(b); }; HTMLAnchorElement.prototype.click = function () {}; });
  await page.evaluate((exam, hours, days) => {
    const set = (id, v) => { document.getElementById(id).value = v; };
    set('examDate', exam); set('hoursPerDay', hours); set('daysPerWeek', days);
    document.querySelector('form').requestSubmit();
  }, exam, hours, days);
  await wait(500);
  await page.evaluate(() => document.getElementById('add-cal').click());
  await wait(300);
  return (await page.evaluate(async () => (window.__blobs[0] ? await window.__blobs[0].text() : ''))).replace(/\r\n /g, '');
};
for (const [fixed, exam, label] of [[Date.UTC(2027, 1, 28, 17), '2027-03-28', 'spring forward 14 Mar'], [Date.UTC(2027, 9, 20, 16), '2027-11-28', 'fall back 7 Nov'], [Date.UTC(2027, 9, 20, 16), '2027-11-07', 'exam on the fall-back day']]) {
  const page = await newPage({ tz: 'America/New_York', fixed });
  const ics = await icsOf(page, exam, '2', '7');
  const starts = [...ics.matchAll(/DTSTART:(\d{8})T/g)].map((m) => m[1]);
  const want = []; const d = new Date(fixed); const s = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  for (const e = new Date(exam + 'T00:00:00Z'); s < e; s.setUTCDate(s.getUTCDate() + 1)) want.push(s.toISOString().slice(0, 10).replace(/-/g, ''));
  check(JSON.stringify(starts) === JSON.stringify(want), `plan calendar across ${label}: sessions on each day once (${starts.length} of ${want.length}${starts.length ? ', ' + starts[0] + '..' + starts[starts.length - 1] : ''})`);
  const ex = ics.match(/DTSTART;VALUE=DATE:(\d{8})\r\nDTEND;VALUE=DATE:(\d{8})/);
  check(ex && ex[1] === exam.replace(/-/g, '') && ex[2] > ex[1], `plan calendar across ${label}: exam day event ${ex && ex[1]} to ${ex && ex[2]}`);
  const weeks = await page.evaluate(() => [...document.querySelectorAll('.week-when span:first-of-type')].map((x) => x.textContent));
  const sundays = new Set(weeks.map((w) => new Date(w.replace('from ', '') + ', 2027').getDay()));
  check(sundays.size === 1, `plan weeks across ${label} all start on the same weekday (${weeks.join(' | ')})`);
  await page.close();
}

// 6. Plan generator: each week's topic hours add up to the week's hours shown.
for (const [slug, hours, days] of [['nclex', '1.5', '5'], ['mcat', '3', '6'], ['cpa-far', '0.5', '3'], ['gre', '7', '7']]) {
  const page = await newPage();
  await page.goto(`${BASE}/study-plan/${slug}/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.evaluate((exam, hours, days) => {
    const set = (id, v) => { document.getElementById(id).value = v; };
    set('examDate', exam); set('hoursPerDay', hours); set('daysPerWeek', days);
    document.querySelector('form').requestSubmit();
  }, dateIn(40), hours, days);
  await wait(400);
  const bad = await page.evaluate(() => [...document.querySelectorAll('.week')].map((w) => {
    const total = parseFloat(w.querySelector('.week-when span:last-child').textContent);
    const parts = [...w.querySelectorAll('.alloc dd')].map((d) => parseFloat(d.textContent));
    return { total, sum: parts.reduce((a, b) => a + b, 0), neg: parts.some((p) => !(p >= 0)) };
  }).filter((x) => Math.abs(x.total - x.sum) > 1e-9 || x.neg || !(x.total > 0)));
  check(bad.length === 0, `plan ${slug} ${hours} h x ${days} d: topic hours add up to each week's hours (${bad.length ? JSON.stringify(bad[0]) : 'all weeks'})`);
  await page.close();
}

// 7. Test time calculator: no "60 min", no "question 0", checkpoints match the pace per question.
for (const [t, q, r] of [['239', '4', '0'], ['179', '2', '0'], ['60', '1', '10'], ['100', '30', '0'], ['1000', '7', '20']]) {
  const page = await newPage();
  await page.goto(`${BASE}/tools/test-time-calculator/`, { waitUntil: 'networkidle0' });
  const text = await page.evaluate((t, q, r) => {
    document.getElementById('totalMin').value = t; document.getElementById('questions').value = q; document.getElementById('reviewPct').value = r;
    document.getElementById('pace-form').requestSubmit();
    return document.getElementById('pace-result').innerText;
  }, t, q, r);
  // each "question n by T" must equal n x the per-question pace (to the minute)
  const per = (Number(t) * (1 - Number(r) / 100)) / Number(q);
  const toMin = (s) => { const m = s.match(/(?:(\d+) h )?(\d+) min/); return Number(m[1] || 0) * 60 + Number(m[2]); };
  const pts = [...text.matchAll(/question (\d+) by ((?:\d+ h )?\d+ min)/g)].map((m) => [Number(m[1]), toMin(m[2])]);
  const paced = pts.every(([n, m]) => Math.abs(m - n * per) <= 0.5 + 1e-9);
  check(paced && pts.length && !/\b60 min|-\d|question 0\b|NaN/.test(text),`test time ${t} min, ${q} q, ${r}% review: ${text.replace(/\s+/g, ' ').slice(0, 140)}`);
  await page.close();
}

// 8. GPA: a negative credit value cannot lower or inflate the GPA.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/gpa-calculator/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const res = await page.evaluate(() => {
    const rows = [...document.querySelectorAll('.gpa-row')];
    const setRow = (li, c, g) => { const [, cr] = li.querySelectorAll('input'); cr.value = c; li.querySelector('select').value = g; };
    setRow(rows[0], '-3', 'A'); setRow(rows[1], '3', 'B'); setRow(rows[2], '0', 'A');
    document.getElementById('gpa-form').dispatchEvent(new Event('input'));
    return { term: document.getElementById('r-term').textContent, credits: document.getElementById('r-credits').textContent };
  });
  check(res.term === '3.00' && res.credits === '3', `GPA with a -3 credit row: term ${res.term}, credits ${res.credits} (want 3.00, 3)`);
  await page.close();
}

// 9. Reading planner: every reading day has pages, pages run from the next unread page to the last page, no negatives.
for (const [total, done, days, per] of [['10', '0', 6, '7'], ['100', '0', 6, '7'], ['50', '-5', 4, '7'], ['301', '17', 30, '5']]) {
  const page = await newPage();
  await page.goto(`${BASE}/tools/reading-planner/`, { waitUntil: 'networkidle0' });
  const res = await page.evaluate((total, done, deadline, per) => {
    const set = (id, v) => { document.getElementById(id).value = v; };
    set('totalPages', total); set('pagesRead', done); set('deadline', deadline); set('readDays', per);
    document.getElementById('reviewDays').checked = false;
    document.getElementById('reading-form').requestSubmit();
    const ranges = [...document.querySelectorAll('#r-table td.mono')].map((td) => td.textContent.split('–').map(Number));
    return { ranges, days: Number(document.getElementById('r-days').textContent) };
  }, total, done, dateIn(days), per);
  const first = Math.max(0, Number(done)) + 1;
  const okChain = res.ranges.every(([a, b], i) => a >= 1 && b >= a && (i === 0 ? a === first : a === res.ranges[i - 1][1] + 1));
  const okEnd = res.ranges.length && res.ranges[res.ranges.length - 1][1] === Number(total);
  check(okChain && okEnd && res.ranges.length === res.days, `reading ${total} pages, read ${done}, ${days} days: ${res.ranges.length} rows for ${res.days} reading days, ${JSON.stringify(res.ranges.slice(0, 3))}..`);
  await page.close();
}

// 10. Score tracker: suggested hours add up to the weekly hours entered; shares add up to 100%.
for (const [exam, hours] of [['nclex', '7'], ['mcat', '20'], ['gre', '3'], ['usmle-step-1', '13']]) {
  const page = await newPage();
  await page.goto(`${BASE}/tools/practice-score-tracker/`, { waitUntil: 'networkidle0' });
  await page.evaluate((exam) => localStorage.setItem('ffl-scores', JSON.stringify({ exam, target: 75, hours: 0, entries: [] })), exam);
  await page.reload({ waitUntil: 'networkidle0' });
  const res = await page.evaluate((hours) => {
    const h = document.getElementById('sc-hours'); h.value = hours; h.dispatchEvent(new Event('change'));
    const cells = [...document.querySelectorAll('#sc-table tr td:last-child')].map((td) => td.textContent);
    return { exam: document.getElementById('sc-exam').value, pct: cells.reduce((a, c) => a + parseFloat(c), 0), h: cells.reduce((a, c) => a + parseFloat((c.match(/\(([\d.]+) h\)/) || [0, 0])[1]), 0) };
  }, hours);
  check(Math.abs(res.h - Number(hours)) < 1e-9 && res.pct === 100, `score tracker ${res.exam} ${hours} h/week: suggested ${res.h} h, shares ${res.pct}%`);
  await page.close();
}

// 11. Schedule maker: two subjects with the same name still add up to the hours entered.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/study-schedule-maker/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const all = await page.evaluate(async (a, b) => {
    const rows = [...document.querySelectorAll('.ss-row')];
    [[rows[0], a], [rows[1], b]].forEach(([li, d]) => { const [n, dt] = li.querySelectorAll('input'); n.value = 'Math'; dt.value = d; });
    document.getElementById('ssHours').value = 2; document.getElementById('ssDays').value = '7';
    document.getElementById('ss-form').requestSubmit();
    await new Promise((r) => setTimeout(r, 200));
    return [...document.querySelectorAll('#ss-table td.mono')].reduce((s, td) => s + (parseFloat(td.textContent) || 0), 0);
  }, dateIn(14), dateIn(28));
  check(all === 2 * 28, `schedule with two subjects named Math: ${all} h shown (want ${2 * 28})`);
  await page.close();
}

// 12. Final grade: the guide's worked examples, and the A-D table agrees with the formula.
for (const [cur, w, tgt, want] of [['78', '40', '80', '83%'], ['85', '30', '90', '101.7%'], ['85', '30', '88', '95%'], ['95', '20', '70', '0%'], ['0', '50', '50', '100%']]) {
  const page = await newPage();
  await page.goto(`${BASE}/tools/final-grade-calculator/`, { waitUntil: 'networkidle0' });
  const res = await page.evaluate((c, w, t) => {
    document.getElementById('current').value = c; document.getElementById('weight').value = w; document.getElementById('target').value = t;
    document.getElementById('final-form').requestSubmit();
    return { need: document.getElementById('r-need').textContent, rows: [...document.querySelectorAll('#r-table tr')].map((tr) => tr.textContent) };
  }, cur, w, tgt);
  const table = res.rows.every((r) => { const t = Number(r.match(/\((\d+)%\)/)[1]); const v = (t - cur * (1 - w / 100)) / (w / 100); const cell = r.replace(/^.*?\)\s*/, ''); return v <= 0 ? cell === 'Already there' : v > 100 ? cell === 'Out of reach' : cell === Math.round(v * 10) / 10 + '%'; });
  check(res.need === want && table, `final grade ${cur}% now, final ${w}%, want ${tgt}%: needs ${res.need} (want ${want}), A-D table ${table ? 'matches' : 'WRONG ' + res.rows.join(' | ')}`);
  await page.close();
}

// 13. Weighted grade: blank scores are left out; totals are the sums entered.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/weighted-grade-calculator/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const res = await page.evaluate(() => {
    const rows = [...document.querySelectorAll('.wg-row')];
    [['20', '90'], ['15', ''], ['25', '80'], ['40', '']].forEach(([w, s], i) => { const [, wi, si] = rows[i].querySelectorAll('input'); wi.value = w; si.value = s; });
    document.getElementById('wg-form').dispatchEvent(new Event('input'));
    return ['r-grade', 'r-weight', 'r-done'].map((id) => document.getElementById(id).textContent);
  });
  // (20 x 90 + 25 x 80) / 45 = 84.4
  check(JSON.stringify(res) === JSON.stringify(['84.4%', '100%', '45%']), `weighted grade with two ungraded categories: ${res.join(', ')} (want 84.4%, 100%, 45%)`);
  await page.close();
}

// 14. GPA: term, cumulative and the GPA needed next term.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/gpa-calculator/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const res = await page.evaluate(() => {
    const set = (id, v) => { document.getElementById(id).value = v; };
    set('prevGpa', '3.0'); set('prevCredits', '30'); set('targetGpa', '3.2'); set('nextCredits', '15');
    document.getElementById('gpa-form').dispatchEvent(new Event('input'));
    return ['r-term', 'r-cum', 'r-need'].map((id) => document.getElementById(id).textContent);
  });
  // default rows A(3), B+(3), B(4): 33.9 / 10 = 3.39; cumulative (90 + 33.9) / 40 = 3.0975; need (3.2 x 55 - 123.9) / 15 = 3.473
  check(res[0] === '3.39' && res[1] === '3.10' && res[2].includes('3.47'), `GPA term ${res[0]}, cumulative ${res[1]}, next term: ${res[2]} (want 3.39, 3.10, 3.47)`);
  await page.close();
}

// 15. Exam countdown: a blank hours field must not quietly count as half an hour a day.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/exam-countdown/`, { waitUntil: 'networkidle0' });
  const res = await page.evaluate((exam) => {
    const set = (id, v) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('change', { bubbles: true })); };
    set('examDate', exam); set('daysPerWeek', '7'); set('hoursPerDay', '3');
    const full = [document.getElementById('r-days').textContent, document.getElementById('r-hours').textContent];
    set('hoursPerDay', '');
    return { full, hidden: document.getElementById('countdown-result').hidden, hours: document.getElementById('r-hours').textContent };
  }, dateIn(28));
  check(res.full[0] === '28' && res.full[1] === '84', `countdown 28 days x 3 h: ${res.full.join(' days, ')} hours (want 28, 84)`);
  check(res.hidden, `countdown with blank hours shows no total (showed ${res.hours} h)`);
  await page.close();
}

{
  const page = await newPage();
  await page.goto(`${BASE}/tools/study-schedule-maker/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const res = await page.evaluate(async (d) => {
    const [n, dt] = document.querySelector('.ss-row').querySelectorAll('input'); n.value = 'Bio'; dt.value = d;
    document.getElementById('ssHours').value = '';
    document.getElementById('ss-form').requestSubmit();
    await new Promise((r) => setTimeout(r, 200));
    return { hidden: document.getElementById('ss-result').hidden, err: document.getElementById('ss-error').textContent };
  }, dateIn(14));
  check(res.hidden && res.err, `schedule maker with blank hours shows no schedule ("${res.err}")`);
  await page.close();
}

// 16. Plan generator edges: exam today/past rejected, 3 days accepted, leap day, max range, total hours match the weeks.
{
  const page = await newPage({ tz: 'America/New_York', fixed: Date.UTC(2028, 1, 1, 17) });
  const ics = await icsOf(page, '2028-02-29', '1.5', '7');
  const starts = [...ics.matchAll(/DTSTART:(\d{8})T/g)].map((m) => m[1]);
  check(starts.length === 28 && starts[27] === '20280228' && /DTSTART;VALUE=DATE:20280229\r\nDTEND;VALUE=DATE:20280301/.test(ics), `plan to leap day 29 Feb 2028: ${starts.length} sessions, last ${starts[starts.length - 1]}, exam event 29 Feb to 1 Mar`);
  await page.close();
}
for (const [days, hours, perWeek, ok] of [[0, '2', '5', false], [-3, '2', '5', false], [2, '2', '5', false], [3, '2', '5', true], [3, '14', '7', true], [180, '0.5', '3', true], [181, '2', '5', false], [30, '2', '1', false], [30, '', '5', false]]) {
  const page = await newPage();
  await page.goto(`${BASE}/study-plan/nclex/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  const res = await page.evaluate((exam, hours, perWeek) => {
    const set = (id, v) => { document.getElementById(id).value = v; };
    set('examDate', exam); set('hoursPerDay', hours); set('daysPerWeek', perWeek);
    document.querySelector('form').requestSubmit();
    const weeks = [...document.querySelectorAll('.week')].map((w) => parseFloat(w.querySelector('.week-when span:last-child').textContent));
    const planned = document.querySelector('.totals div:nth-child(3) dd');
    const daysLeft = document.querySelector('.totals div:nth-child(1) dd');
    return { err: document.getElementById('form-error').textContent, weeks, planned: planned ? Number(planned.textContent) : null, daysLeft: daysLeft ? Number(daysLeft.textContent) : null, html: document.getElementById('plan').innerHTML };
  }, dateIn(days), hours, perWeek);
  const sum = res.weeks.reduce((a, b) => a + b, 0);
  const good = ok
    ? !res.err && res.daysLeft === days && res.weeks.length === Math.ceil(days / 7) && res.weeks.every((h) => h > 0) && Math.abs(res.planned - sum) <= 0.5 && !/NaN|undefined|Infinity/.test(res.html)
    : !!res.err && !res.weeks.length;
  check(good, `plan NCLEX exam in ${days} days, ${hours} h x ${perWeek}: ${ok ? `${res.weeks.length} weeks, planned ${res.planned} h vs weeks ${sum} h` : `rejected: "${res.err.slice(0, 60)}"`}`);
  await page.close();
}

// 17. Home focus day: a block that ended while away is counted once, and the streak follows calendar days.
for (const [lastAgo, nBefore, want] of [[1, 3, 4], [2, 3, 1], [0, 5, 5]]) {
  const page = await newPage();
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle0' });
  const res = await page.evaluate(async (lastAgo, nBefore) => {
    const ld = (k) => { const d = new Date(); d.setDate(d.getDate() - k); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
    localStorage.setItem('ffl-home-focus', JSON.stringify({ subject: '', len: 25, day: ld(0), focus: [lastAgo === 0, false, false, false], tested: [false, false, false, false], run: { endAt: Date.now() - 5000 }, streak: { last: ld(lastAgo), n: nBefore } }));
    return 0;
  }, lastAgo, nBefore);
  await page.reload({ waitUntil: 'networkidle0' });
  const s = await page.evaluate(() => JSON.parse(localStorage.getItem('ffl-home-focus')));
  const doneBlocks = s.focus.filter(Boolean).length;
  check(s.streak.n === want && doneBlocks === (lastAgo === 0 ? 2 : 1) && !s.run, `home focus: last streak day ${lastAgo} day(s) ago, ${nBefore} days -> streak ${s.streak.n} (want ${want}), blocks done ${doneBlocks}`);
  await page.close();
}

// 18. Topic names in the tracker / error log match each plan page, so "Mark them as shaky" finds them.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/practice-score-tracker/`, { waitUntil: 'networkidle0' });
  const topics = await page.evaluate(() => window.EXAM_TOPICS);
  await page.close();
  for (const [slug, e] of Object.entries(topics)) {
    const p = await newPage();
    const r = await p.goto(`${BASE}/study-plan/${slug}/`, { waitUntil: 'domcontentloaded' });
    const names = r && r.status() < 400 ? await p.evaluate(() => (window.EXAM_CONFIG ? window.EXAM_CONFIG.topics.map((t) => t.name) : null)) : null;
    const wsum = e.topics.reduce((a, t) => a + t[1], 0);
    check(names && JSON.stringify(names) === JSON.stringify(e.topics.map((t) => t[0])) && wsum > 0, `exam topics ${slug}: ${names ? names.length : 'no plan page'} topics match the plan page`);
    await p.close();
  }
}

// 19. Embed pages load without script errors and still calculate.
for (const [slug, setup, out] of [
  ['final-grade-calculator', { current: '78', weight: '40', target: '80' }, ['r-need', '83%']],
  ['test-time-calculator', { totalMin: '120', questions: '60', reviewPct: '0' }, ['r-sec', '120 sec']],
  ['gpa-calculator', {}, ['r-term', '3.39']],
  ['weighted-grade-calculator', {}, ['r-weight', '100%']],
  ['exam-countdown', { examDate: dateIn(10), hoursPerDay: '2', daysPerWeek: '7' }, ['r-hours', '20']],
  ['reading-planner', { totalPages: '100', pagesRead: '0', deadline: dateIn(10), readDays: '7' }, ['r-left', '100']],
]) {
  const page = await newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(`${BASE}/embed/${slug}/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const got = await page.evaluate((setup, id) => {
    Object.entries(setup).forEach(([k, v]) => { const e = document.getElementById(k); e.value = v; });
    const f = document.querySelector('form'); f.dispatchEvent(new Event('input', { bubbles: true })); f.dispatchEvent(new Event('change', { bubbles: true })); f.requestSubmit();
    return document.getElementById(id).textContent.trim();
  }, setup, out[0]);
  check(!errors.length && got === out[1], `embed ${slug}: ${out[0]} = ${got} (want ${out[1]})${errors.length ? ' errors: ' + errors.join('; ') : ''}`);
  await page.close();
}

// 20. Downloads: score tracker CSV quotes commas and quotes; flashcards export/import round trip.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/practice-score-tracker/`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.setItem('ffl-scores', JSON.stringify({ exam: 'nclex', target: 75, hours: 10, entries: [] })));
  await page.reload({ waitUntil: 'networkidle0' });
  await page.evaluate(() => { window.__blobs = []; const real = URL.createObjectURL.bind(URL); URL.createObjectURL = (b) => { window.__blobs.push(b); return real(b); }; HTMLAnchorElement.prototype.click = function () {}; });
  const csv = await page.evaluate(async () => {
    const set = (id, v) => { document.getElementById(id).value = v; };
    set('sc-right', '7'); set('sc-total', '10'); set('sc-note', 'Kaplan, set "B"');
    document.getElementById('sc-form').requestSubmit();
    document.getElementById('sc-csv').click();
    return window.__blobs[0] ? await window.__blobs[0].text() : '';
  });
  check(csv.split('\r\n').length === 2 && csv.includes('"7","10","Kaplan, set ""B"""'), `score tracker CSV: ${JSON.stringify(csv.split('\r\n')[1])}`);
  await page.close();

  const p2 = await newPage();
  await p2.goto(`${BASE}/tools/flashcards/`, { waitUntil: 'networkidle0' });
  await p2.evaluate(() => localStorage.setItem('ffl-flashcards', JSON.stringify([{ front: 'Q, "1"', back: 'A <b>', step: 3, due: '2030-01-02' }])));
  await p2.reload({ waitUntil: 'networkidle0' });
  await p2.evaluate(() => { window.__blobs = []; const real = URL.createObjectURL.bind(URL); URL.createObjectURL = (b) => { window.__blobs.push(b); return real(b); }; HTMLAnchorElement.prototype.click = function () {}; });
  const json = await p2.evaluate(async () => { document.getElementById('fc-export').click(); return window.__blobs[0].text(); });
  await p2.evaluate(() => localStorage.setItem('ffl-flashcards', '[]'));
  await p2.reload({ waitUntil: 'networkidle0' });
  const input = await p2.$('#fc-import');
  const fs = await import('fs'); const os = await import('os'); const path = await import('path');
  const tmp = path.join(os.tmpdir(), 'ffl-cards.json'); fs.writeFileSync(tmp, json);
  await input.uploadFile(tmp);
  await wait(400);
  const cards = await p2.evaluate(() => JSON.parse(localStorage.getItem('ffl-flashcards')));
  check(cards.length === 1 && cards[0].front === 'Q, "1"' && cards[0].back === 'A <b>' && cards[0].step === 3 && cards[0].due === '2030-01-02', `flashcards export then import keeps the card: ${JSON.stringify(cards)}`);
  await p2.close();
}

await browser.close();
console.log(failed ? `\n${failed} FAILED` : '\nALL PASSED');
process.exit(failed ? 1 : 0);
