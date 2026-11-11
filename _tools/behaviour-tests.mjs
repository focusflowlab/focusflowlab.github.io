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
// local calendar date (toISOString gave the UTC date, a day early from 00:00 to 05:00 in Karachi)
const dateIn = (days) => { const t = new Date(); const d = new Date(t.getFullYear(), t.getMonth(), t.getDate() + days); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };

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
for (const [total, done, days, per] of [['10', '0', 6, '7'], ['100', '0', 6, '7'], ['50', '', 4, '7'], ['301', '17', 30, '5']]) {
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

// 19b. Score tracker: a total over 5,000 is refused; an old saved one stays listed (removable) but is left out of every figure.
{
  const page = await newPage();
  await page.goto(`${BASE}/tools/practice-score-tracker/`, { waitUntil: 'networkidle0' });
  const t = 'Management of Care';
  await page.evaluate((t) => localStorage.setItem('ffl-scores', JSON.stringify({ exam: 'nclex', target: 75, hours: 10, entries: [
    { id: 1, exam: 'nclex', topic: t, date: '2026-11-01', right: 30, total: 4566505, note: '' },
    { id: 2, exam: 'nclex', topic: t, date: '2026-11-02', right: 8, total: 10, note: '' }] })), t);
  await page.reload({ waitUntil: 'networkidle0' });
  const r = await page.evaluate((t) => {
    const $ = (id) => document.getElementById(id);
    const row = [...$('sc-table').rows].find((tr) => tr.cells[0].textContent === t);
    const out = { count: $('sc-count').textContent, overall: $('sc-overall').textContent, row: row ? row.cells[1].textContent : '', items: $('sc-list').children.length,
      flagged: $('sc-list').textContent.includes('not counted') };
    $('sc-right').value = '30'; $('sc-total').value = '4566505'; $('sc-form').requestSubmit();
    out.err = $('sc-error').textContent; out.saved = JSON.parse(localStorage.getItem('ffl-scores')).entries.length;
    $('sc-right').value = '30'; $('sc-total').value = '5000'; $('sc-form').requestSubmit();
    out.okErr = $('sc-error').textContent; out.count2 = $('sc-count').textContent;
    [...$('sc-list').querySelectorAll('button')].find((b) => b.getAttribute('aria-label').includes('2026-11-01')).click();
    out.after = JSON.parse(localStorage.getItem('ffl-scores')).entries.map((e) => e.total).sort((a, b) => a - b).join(',');
    return out;
  }, t);
  check(r.count === '10' && r.overall === '80%' && r.row === '80% (8/10)' && r.items === 2 && r.flagged, `score tracker old 4,566,505 entry left out: count ${r.count}, overall ${r.overall}, row ${r.row}, listed ${r.items}, flagged ${r.flagged}`);
  check(r.err.includes('at most 5,000') && r.saved === 2, `score tracker refuses total 4,566,505: "${r.err}", saved ${r.saved}`);
  check(r.okErr === '' && r.count2 === '5010' && r.after === '10,5000', `score tracker accepts 5,000 and removes the bad row: count ${r.count2}, left ${r.after}`);
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

// 21. Corrupt or old saved data never breaks a tool: no script error, no "NaN" or "undefined" on the page.
{
  const junk = ['{', '"text"', '123', 'null', '[]', '{}', '[1,"x",null]',
    '{"rows":"abc","entries":"abc","items":"abc","focus":"abc","weak":"abc","hours":"x","target":"x"}',
    '{"exam":"zzz","entries":[{"exam":"nclex","topic":5,"right":"x","total":null,"date":3}],"items":[{"exam":"nclex","reason":"zzz","review":5,"what":null}],"focus":[1,2],"tested":"x","streak":null,"len":"25","run":{"endAt":"x"},"subject":5,"rows":[{"name":{},"credits":"x","grade":"Z","level":"q","date":"bad","priority":"9","weight":"x","score":"y"}]}',
    '[{"front":1},{"front":"Q","back":"A","step":"x","due":5},{"name":null,"date":"bad"},{"name":"T","date":"2026-13-45"}]',
    '{"exam":"nclex","target":"x","hours":"y","entries":[{"exam":"nclex","topic":"Pharmacological and Parenteral Therapies","right":"x","total":null},{"exam":"nclex","topic":5,"right":20,"total":10}],"items":[{"exam":"nclex","topic":"x","what":"q","reason":"zzz","review":"2026-01-01"},{"exam":"nclex","what":5,"reason":"gap"}]}'];
  const day = (() => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); })();
  const pages = [['ffl-final-grade', '/tools/final-grade-calculator/'], ['ffl-weighted-grade', '/tools/weighted-grade-calculator/'], ['ffl-gpa', '/tools/gpa-calculator/'],
    ['ffl-pace', '/tools/test-time-calculator/'], ['ffl-reading', '/tools/reading-planner/'], ['ffl-countdown', '/tools/exam-countdown/'], ['ffl-study-schedule', '/tools/study-schedule-maker/'],
    ['ffl-scores', '/tools/practice-score-tracker/'], ['ffl-errorlog', '/tools/error-log/'], ['ffl-spaced-review', '/tools/spaced-review/'], ['ffl-flashcards', '/tools/flashcards/'],
    ['ffl-home-focus', '/'], ['ffl-timer-' + day, '/tools/focus-timer/'], ['ffl-plan-gre', '/study-plan/gre/'], ['ffl-scores', '/study-plan/nclex/']];
  for (const [key, url] of pages) {
    const page = await newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await page.goto(`${BASE}${url}`, { waitUntil: 'networkidle0' });
    const bad = [];
    for (const v of junk) {
      errors.length = 0;
      await page.evaluate((k, v) => { localStorage.clear(); localStorage.setItem(k, v); }, key, v);
      await page.reload({ waitUntil: 'networkidle0' });
      const text = await page.evaluate(() => document.body.innerText);
      const m = text.match(/.{0,30}\b(NaN|undefined|Infinity)\b.{0,30}/);
      if (errors.length || m) bad.push(v.slice(0, 30) + ' -> ' + (errors[0] || m[0]).slice(0, 90));
    }
    check(!bad.length, `corrupt saved data on ${url} (${key}): ${bad.length ? bad.join(' || ') : 'all ' + junk.length + ' cases load cleanly'}`);
    await page.close();
  }
}

// 21b. Good saved data still loads after the clean-up above (the filters must not drop real entries).
{
  const d = dateIn(0), later = dateIn(3);
  const cases = [
    ['/tools/practice-score-tracker/', 'ffl-scores', { exam: 'nclex', target: 80, hours: 10, entries: [{ id: 1, exam: 'nclex', topic: 'Pharmacological and Parenteral Therapies', date: d, right: 7, total: 10, note: 'x' }] }, () => document.getElementById('sc-count').textContent + '|' + document.getElementById('sc-target').value, '10|80'],
    ['/tools/error-log/', 'ffl-errorlog', { exam: 'nclex', items: [{ id: 1, exam: 'nclex', topic: 'Pharmacological and Parenteral Therapies', what: 'q', reason: 'gap', fix: '', added: d, review: later, fixed: false }] }, () => document.getElementById('el-total').textContent, '1'],
    ['/tools/spaced-review/', 'ffl-spaced-review', [{ name: 'Topic', date: d }], () => String(document.querySelectorAll('.review-topic').length), '1'],
    ['/tools/gpa-calculator/', 'ffl-gpa', { rows: [{ name: 'Bio', credits: 4, grade: 'B+', level: 'honors' }], prevGpa: '', prevCredits: '', targetGpa: '', nextCredits: '' }, () => document.getElementById('r-term').textContent + '|' + document.getElementById('r-weighted').textContent, '3.30|3.80'],
    ['/tools/weighted-grade-calculator/', 'ffl-weighted-grade', [{ name: 'Exams', weight: '60', score: '90' }, { name: 'HW', weight: '40', score: '80' }], () => document.getElementById('r-grade').textContent, '86.0%'],
    ['/tools/study-schedule-maker/', 'ffl-study-schedule', { rows: [{ name: 'Bio', date: dateIn(10), priority: '3' }], hours: '2', days: '7' }, () => document.querySelector('.ss-row input').value + '|' + document.querySelector('.ss-row select').value + '|' + document.getElementById('ssDays').value, 'Bio|3|7'],
    ['/', 'ffl-home-focus', { subject: 'Chem', len: 45, day: d, focus: [true, false, false, false], tested: [true, false, false, false], run: null, streak: { last: d, n: 3 } }, () => document.getElementById('fd-subject').value + '|' + document.getElementById('fd-count').textContent + '|' + document.getElementById('fd-streak').textContent, 'Chem|1 of 4 blocks|3-day streak'],
  ];
  for (const [url, key, value, read, want] of cases) {
    const page = await newPage();
    await page.goto(`${BASE}${url}`, { waitUntil: 'networkidle0' });
    await page.evaluate((k, v) => { localStorage.clear(); localStorage.setItem(k, v); }, key, JSON.stringify(value));
    await page.reload({ waitUntil: 'networkidle0' });
    const got = await page.evaluate(read);
    check(got === want, `saved data reloads on ${url}: ${got} (want ${want})`);
    await page.close();
  }
}

// 22. Every plan generator, extreme inputs, several time zones: plan, topic hours, calendar file (read by a real parser) and print pack agree.
{
  const ICAL = (await import('ical.js')).default;
  const slugs = Object.keys(await (async () => { const p = await newPage(); await p.goto(`${BASE}/tools/practice-score-tracker/`, { waitUntil: 'networkidle0' }); const t = await p.evaluate(() => window.EXAM_TOPICS); await p.close(); return t; })());
  const zones = [['Asia/Karachi', Date.UTC(2026, 10, 11, 20)], ['America/Los_Angeles', Date.UTC(2027, 2, 1, 7)], ['Pacific/Auckland', Date.UTC(2027, 2, 20, 11)], ['Europe/London', Date.UTC(2027, 9, 20, 23, 30)], ['Australia/Lord_Howe', Date.UTC(2026, 9, 1, 13)]];
  const ymd = (d) => d.getUTCFullYear() + String(d.getUTCMonth() + 1).padStart(2, '0') + String(d.getUTCDate()).padStart(2, '0');
  for (const slug of slugs) {
    for (const [tz, fixed] of zones) {
      if (slug !== 'mcat' && slug !== 'teas' && tz !== 'Asia/Karachi') continue; // every exam in one zone, two exams in every zone
      const page = await newPage({ tz, fixed });
      const errors = [];
      page.on('pageerror', (e) => errors.push(e.message));
      await page.goto(`${BASE}/study-plan/${slug}/`, { waitUntil: 'networkidle0' });
      await page.evaluate(() => { localStorage.clear(); window.__blobs = []; const real = URL.createObjectURL.bind(URL); URL.createObjectURL = (b) => { window.__blobs.push(b); return real(b); }; HTMLAnchorElement.prototype.click = function () {}; window.print = () => {}; });
      const maxDays = await page.evaluate(() => window.EXAM_CONFIG.maxDays);
      // local "today" in that zone at the frozen instant
      const local = await page.evaluate(() => { const d = new Date(); return [d.getFullYear(), d.getMonth(), d.getDate()]; });
      const dayStr = (n) => { const d = new Date(Date.UTC(local[0], local[1], local[2] + n)); return d.toISOString().slice(0, 10); };
      const problems = [];
      const cases = [[0, '2', '5', false], [-1, '2', '5', false], [2, '2', '5', false], [maxDays + 1, '2', '5', false], [20, '0', '5', false], [20, '24', '5', false], [20, '', '5', false], [20, 'abc', '5', false],
        [3, '0.5', '3', true], [7, '14', '7', true], [8, '1.5', '4', true], [45, '3', '6', true], [maxDays, '0.5', '3', true], [maxDays, '14', '7', true]];
      for (const [days, hours, per, ok] of cases) {
        const exam = dayStr(days);
        const r = await page.evaluate(async (exam, hours, per) => {
          window.__blobs = [];
          document.getElementById('plan').innerHTML = '';
          const f = document.querySelector('form');
          f.examDate.value = exam; f.hoursPerDay.value = hours; f.daysPerWeek.value = per;
          // submit the way the button does, but without the browser's own field validation, so the script's checks are tested
          f.dispatchEvent(new Event('submit', { cancelable: true }));
          const plan = document.getElementById('plan');
          const weeks = [...plan.querySelectorAll('.week')].map((w) => ({ h: parseFloat(w.querySelector('.week-when span:last-child').textContent), parts: [...w.querySelectorAll('.alloc dd')].map((d) => parseFloat(d.textContent)) }));
          const out = { err: document.getElementById('form-error').textContent, weeks, text: plan.innerText, days: plan.querySelector('.totals dd') ? Number(plan.querySelector('.totals dd').textContent) : null };
          if (!weeks.length) return out;
          document.getElementById('add-cal').click();
          out.ics = window.__blobs[0] ? await window.__blobs[0].text() : '';
          document.getElementById('print-pack').click();
          const pack = document.getElementById('daily-print');
          out.packPages = pack.querySelectorAll(':scope > .day-page').length; out.packText = pack.innerText;
          out.dayDates = [...pack.querySelectorAll('.day-page h2')].map((h) => h.textContent);
          out.compact = !!pack.querySelector('.wk-compact');
          return out;
        }, exam, hours, per);
        const tag = `${days}d ${hours || 'blank'}h x${per}`;
        if (!ok) { if (!r.err || r.weeks.length) problems.push(`${tag}: not rejected`); continue; }
        if (r.err) { problems.push(`${tag}: rejected "${r.err}"`); continue; }
        if (/\b(NaN|undefined|Infinity)\b/.test(r.text + r.packText)) problems.push(`${tag}: NaN/undefined in output`);
        if (r.days !== days) problems.push(`${tag}: days left ${r.days}`);
        if (r.weeks.length !== Math.ceil(days / 7)) problems.push(`${tag}: ${r.weeks.length} weeks`);
        r.weeks.forEach((w, i) => { const s = w.parts.reduce((a, b) => a + b, 0); if (!(w.h > 0) || Math.abs(s - w.h) > 1e-9) problems.push(`${tag}: week ${i + 1} ${w.h} h vs topics ${s} h`); });
        // calendar: parse with ical.js
        let comp; try { comp = new ICAL.Component(ICAL.parse(r.ics)); } catch (e) { problems.push(`${tag}: ics does not parse: ${e.message}`); continue; }
        const evs = comp.getAllSubcomponents('vevent').map((v) => new ICAL.Event(v));
        const uids = new Set(evs.map((e) => e.uid));
        if (uids.size !== evs.length) problems.push(`${tag}: duplicate UIDs`);
        const examEv = evs.filter((e) => e.startDate.isDate);
        const sess = evs.filter((e) => !e.startDate.isDate);
        if (examEv.length !== 1 || examEv[0].startDate.toString() !== exam || examEv[0].endDate.toString() !== dayStr(days + 1)) problems.push(`${tag}: exam event ${examEv.map((e) => e.startDate + '..' + e.endDate)}`);
        const first = dayStr(0).replace(/-/g, ''), last = dayStr(days - 1).replace(/-/g, '');
        const sessDays = sess.map((e) => e.startDate.toString().slice(0, 10).replace(/-/g, ''));
        if (new Set(sessDays).size !== sessDays.length) problems.push(`${tag}: two sessions on one day`);
        if (sessDays.some((d) => d < first || d > last)) problems.push(`${tag}: session outside ${first}-${last}: ${sessDays.filter((d) => d < first || d > last)[0]}`);
        sess.forEach((e) => { const s = e.startDate.toJSDate(), en = e.endDate.toJSDate(); if (!(en > s) || e.endDate.toString().slice(0, 10) !== e.startDate.toString().slice(0, 10) && !e.endDate.toString().endsWith('T00:00:00')) problems.push(`${tag}: bad session ${e.startDate}..${e.endDate}`); });
        const studyDays = r.weeks.length; // sanity: sessions >= weeks
        if (sess.length < studyDays) problems.push(`${tag}: ${sess.length} sessions for ${studyDays} weeks`);
        // print pack: cover + overview + week pages + first-week days + 2 error logs + checklist
        const weekPages = r.compact ? Math.ceil(r.weeks.length / 2) : r.weeks.length;
        const week1Sessions = sess.filter((e) => e.description && /Week 1,/.test(e.description)).length;
        if (r.packPages !== 1 + 1 + weekPages + week1Sessions + 3) problems.push(`${tag}: pack ${r.packPages} pages, want ${1 + 1 + weekPages + week1Sessions + 3}`);
      }
      if (errors.length) problems.push('script error: ' + errors[0]);
      check(!problems.length, `plan ${slug} in ${tz}: ${problems.length ? problems.slice(0, 4).join(' | ') : cases.length + ' cases clean (ics parsed, pack counted)'}`);
      await page.close();
    }
  }
}

// 23. Real keyboard input (the sections above mostly set .value in page script). Each odd value is typed or pasted into
// one box, the button is pressed twice, then the box is retyped with a good value and pressed again.
// Checks: no script error or NaN/Infinity/undefined/1e+ on the page; a value outside the box's own min/max (or a
// decimal in a whole-number box) gets a visible message; after the fix the result is exactly the result of a clean
// page with the good values (so a bad entry never blocks or skews the next one).
// Date boxes are set in script: typing a date depends on the browser's locale.
{
  const ODD = ['99999999', '-5', '2.5', '', '1e3', '0', 'PASTE: 42 ', 'PASTE:12abc'];
  const typeInto = async (page, h, v) => {
    await h.focus(); await page.keyboard.down('Control'); await page.keyboard.press('KeyA'); await page.keyboard.up('Control'); await page.keyboard.press('Backspace');
    if (v.startsWith('PASTE:')) await page.keyboard.sendCharacter(v.slice(6)); else if (v) await page.keyboard.type(v);
  };
  // First press with the Enter key (still in the box), later presses with a mouse click on the button.
  const press = async (page, enter) => {
    const s = await page.$('main form:not(.kit-form) button[type=submit]');
    if (enter) await page.keyboard.press('Enter');
    if (!enter && s) await s.click();
    if (!s) await page.click('main h1'); // live forms with no button: leave the box
    await wait(150);
  };
  const look = (page) => page.evaluate(() => {
    const m = document.querySelector('main'), keep = (e) => !e.closest('.kit-form, .tracker-offer, .kit') && e.offsetParent !== null;
    const result = [...m.querySelectorAll('[aria-live], output, [id^="r-"]')].filter(keep).map((e) => e.innerText.trim()).join('|');
    const error = [...m.querySelectorAll('.error, [role=alert]')].filter(keep).map((e) => e.innerText.trim()).join(' ');
    return { result, error, bad: (m.innerText.match(/NaN|undefined|Infinity|\de\+\d/g) || []).join(',') };
  });
  const T = [
    ['test-time-calculator', { '#totalMin': '90', '#questions': '60' }, ['#totalMin', '#questions']],
    ['final-grade-calculator', { '#current': '82', '#weight': '30', '#target': '85' }, ['#current', '#weight', '#target']],
    ['exam-countdown', { '#hoursPerDay': '3', $date: ['examDate', 30] }, ['#hoursPerDay']],
    ['reading-planner', { '#totalPages': '420', '#pagesRead': '60', $date: ['deadline', 16] }, ['#totalPages', '#pagesRead']],
    ['gpa-calculator', { '#prevGpa': '3.2', '#prevCredits': '45', '#targetGpa': '3.5', '#nextCredits': '15' }, ['.gpa-row input[type=number]', '#prevGpa', '#prevCredits', '#targetGpa', '#nextCredits']],
    ['weighted-grade-calculator', { '.wg-row:nth-child(1) input:nth-of-type(2)': '40', '.wg-row:nth-child(1) input:nth-of-type(3)': '80' }, ['.wg-row:nth-child(1) input:nth-of-type(2)', '.wg-row:nth-child(1) input:nth-of-type(3)']],
    ['study-schedule-maker', { '#ssHours': '3', $subjects: [['Math', 20], ['Biology', 25]] }, ['#ssHours']],
    ['/study-plan/gre/', { '#hoursPerDay': '2', $date: ['examDate', 60] }, ['#hoursPerDay']],
    ['/study-plan/nclex/', { '#hoursPerDay': '3', $date: ['examDate', 40] }, ['#hoursPerDay']],
  ];
  const fresh = async (path, good) => {
    const page = await newPage(); const errs = []; page.on('pageerror', (e) => errs.push(e.message));
    await page.goto(BASE + (path.startsWith('/') ? path : `/tools/${path}/`), { waitUntil: 'networkidle0' }); await page.evaluate(() => localStorage.clear()); await page.reload({ waitUntil: 'networkidle0' });
    for (const [sel, v] of Object.entries(good)) {
      if (sel === '$date') await page.evaluate((id, iso) => { const e = document.getElementById(id); e.value = iso; e.dispatchEvent(new Event('input', { bubbles: true })); }, v[0], dateIn(v[1]));
      else if (sel === '$subjects') await page.evaluate((rows) => rows.forEach(([n, iso], i) => { const li = document.querySelectorAll('#ss-form li')[i]; li.querySelector('input[type=text]').value = n; li.querySelector('input[type=date]').value = iso; }), v.map(([n, d]) => [n, dateIn(d)]));
      else await typeInto(page, await page.$(sel), v);
    }
    return { page, errs };
  };
  for (const [path, good, fields] of T) {
    const clean = await fresh(path, good); await press(clean.page);
    const want = await look(clean.page); await clean.page.close();
    check(want.result && !want.error && !want.bad, `keyboard ${path}: good values give a result (${want.result.slice(0, 60)}..)`);
    for (const sel of fields) for (const v of ODD) {
      const { page, errs } = await fresh(path, good);
      const h = await page.$(sel);
      const [min, max, step] = await h.evaluate((e) => [e.min, e.max, e.step]);
      await typeInto(page, h, v); await press(page, true); await press(page);
      // Judge what the box holds: the browser drops letters from a paste ("12abc" becomes 12).
      const got = await look(page), typed = (await h.evaluate((e) => e.value)).trim();
      const n = Number(typed), stepWhole = step !== '' && Number(step) >= 1;
      const outside = typed !== '' && (!Number.isFinite(n) || (min !== '' && n < Number(min)) || (max !== '' && n > Number(max)) || (stepWhole && !Number.isInteger(n)));
      await typeInto(page, h, good[sel] ?? (sel.includes('gpa-row') ? '3' : '')); await press(page);
      const after = await look(page);
      const label = `keyboard ${path} ${sel.replace(/^#/, '')}=${JSON.stringify(v)}`;
      check(!errs.length && !got.bad && !after.bad, `${label}: no script error or NaN (${errs[0] || got.bad || after.bad || 'ok'})`);
      if (outside) check(got.error !== '', `${label}: outside ${min}..${max}${stepWhole ? ' whole' : ''}, message shown ("${got.error.slice(0, 70)}")`);
      check(after.result === want.result && after.error === want.error, `${label}: fixed box gives the clean result${after.result === want.result ? '' : ` (got ${after.result.slice(0, 80)} | ${after.error})`}`);
      await page.close();
    }
  }

  // Loggers: the owner's case (a huge total, then a fixed one), blank and whitespace-only entries, the same entry twice, a long paste.
  {
    const { page } = await fresh('practice-score-tracker', {});
    const count = () => page.evaluate(() => JSON.parse(localStorage.getItem('ffl-scores') || '{"entries":[]}').entries.length);
    await typeInto(page, await page.$('#sc-right'), '30'); await typeInto(page, await page.$('#sc-total'), '4566505'); await press(page);
    const e1 = (await look(page)).error, c1 = await count();
    await typeInto(page, await page.$('#sc-total'), '40'); await press(page);
    const s2 = await page.evaluate(() => [document.getElementById('sc-count').textContent, document.getElementById('sc-overall').textContent]);
    await press(page); const c3 = await count();
    for (const [r, t] of [['7', '10'], ['7', '10']]) { await typeInto(page, await page.$('#sc-right'), r); await typeInto(page, await page.$('#sc-total'), t); await press(page); }
    const s4 = await page.evaluate(() => document.getElementById('sc-count').textContent);
    check(e1.includes('5,000') && c1 === 0 && s2[0] === '40' && s2[1] === '75%' && c3 === 1 && s4 === '60', `keyboard score tracker: huge total refused (${c1} saved), fixed total logged (${s2}), empty resubmit adds nothing (${c3}), same set twice counted twice (${s4})`);
    await page.close();
  }
  for (const [path, key, fill, list] of [
    ['error-log', 'ffl-errorlog', ['#el-what'], (s) => s.items.length],
    ['spaced-review', 'ffl-spaced-review', ['#topic'], (s) => s.length],
    ['flashcards', 'ffl-flashcards', ['#fcFront', '#fcBack'], (s) => s.length],
  ]) {
    const { page, errs } = await fresh(path, {});
    const n = () => page.evaluate((k) => localStorage.getItem(k), key).then((v) => (v ? list(JSON.parse(v)) : 0));
    const put = async (v) => { for (const sel of fill) await typeInto(page, await page.$(sel), v); await press(page); };
    await put(''); const blank = [await n(), (await look(page)).error];
    await put('PASTE:    '); const spaces = await n();
    await put('Beta blockers'); await put('Beta blockers'); const two = await n();
    await put('PASTE:' + 'x'.repeat(5000)); const long = await n();
    const bad = (await look(page)).bad;
    check(blank[0] === 0 && blank[1] !== '' && spaces === 0 && two === 2 && long === 3 && !errs.length && !bad, `keyboard ${path}: blank refused with a message, spaces refused, two entries saved, long paste saved (${blank[0]}/${spaces}/${two}/${long}${errs[0] ? ', ' + errs[0] : ''})`);
    // Double-click the button on a filled form: one entry, not two (the form clears after the first).
    for (const sel of fill) await typeInto(page, await page.$(sel), 'Renal dosing');
    await (await page.$('main form button[type=submit]')).click({ count: 2 }); await wait(200);
    const dbl = await n();
    // Reload: entries persist. Then delete one with a real click.
    await page.reload({ waitUntil: 'networkidle0' });
    const kept = await n();
    const del = await page.evaluateHandle(() => [...document.querySelectorAll('main button')].find((b) => /^(Delete|Remove)$/.test(b.textContent.trim())));
    await del.click(); await wait(150);
    const afterDel = await n();
    check(dbl === 4 && kept === 4 && afterDel === 3 && !errs.length, `click ${path}: double-click adds one (${dbl}), reload keeps all (${kept}), Delete removes one (${afterDel})`);
    await page.close();
  }

  // Score tracker: double-click logs once; Remove by click; reload keeps the rest; target/hours boxes refuse odd values.
  {
    const { page, errs } = await fresh('practice-score-tracker', {});
    const count = () => page.evaluate(() => JSON.parse(localStorage.getItem('ffl-scores') || '{"entries":[]}').entries.length);
    for (const t of ['10', '20']) { await typeInto(page, await page.$('#sc-right'), '5'); await typeInto(page, await page.$('#sc-total'), t); await (await page.$('#sc-form button[type=submit]')).click({ count: 2 }); await wait(150); }
    const two = await count();
    await page.click('#sc-list button'); await wait(150);
    await page.reload({ waitUntil: 'networkidle0' });
    const one = await count(), shown = await page.evaluate(() => document.getElementById('sc-count').textContent);
    await typeInto(page, await page.$('#sc-hours'), '99999999'); await page.click('main h1'); await wait(150);
    const hoursMsg = (await look(page)).error, hoursBox = await page.$eval('#sc-hours', (e) => e.value);
    await typeInto(page, await page.$('#sc-target'), '2.5'); await page.click('main h1'); await wait(150);
    const targetMsg = (await look(page)).error;
    check(two === 2 && one === 1 && shown === '10' && hoursMsg.includes('0 to 100') && hoursBox === '20' && targetMsg.includes('1 to 100') && !errs.length,
      `click score tracker: double-clicks log ${two}, Remove + reload leave ${one} (${shown} questions), 99999999 h refused (box back to ${hoursBox}), target 2.5 refused`);
    await page.close();
  }

  // Error log "Fixed it" (edit) by click survives a reload.
  {
    const { page, errs } = await fresh('error-log', {});
    await typeInto(page, await page.$('#el-what'), 'Loop diuretics'); await press(page, true);
    const fix = await page.evaluateHandle(() => [...document.querySelectorAll('main button')].find((b) => b.textContent.trim() === 'Fixed it'));
    await fix.click(); await wait(150); await page.reload({ waitUntil: 'networkidle0' });
    const st = await page.evaluate(() => JSON.parse(localStorage.getItem('ffl-errorlog')).items.map((i) => Object.keys(i).filter((k) => /fix|done|status/i.test(k)).map((k) => k + '=' + i[k]).join(',')));
    check(st.length === 1 && /true|done|fixed|\d{4}-/.test(st[0]) && !errs.length, `click error log: "Fixed it" saved and kept after reload (${st})`);
    await page.close();
  }

  // Signup forms (home kit, plan-page tracker): the MailerLite request is intercepted and answered here, never sent.
  for (const path of ['/', '/study-plan/gre/']) {
    const page = await newPage(); const errs = []; page.on('pageerror', (e) => errs.push(e.message));
    const sent = [];
    await page.setRequestInterception(true);
    page.on('request', (r) => { if (r.url().includes('mailerlite.com')) { sent.push(r.postData() || ''); r.respond({ status: 200, contentType: 'application/json', headers: { 'Access-Control-Allow-Origin': '*' }, body: '{"success":true}' }); } else r.continue(); });
    await page.goto(BASE + path, { waitUntil: 'networkidle0' });
    const box = await page.$('#kit-email'), btn = await page.$('#kit-form button[type=submit]');
    const tries = [];
    for (const v of ['', 'abc', 'a@b', 'PASTE:  x @y.com', 'PASTE:' + 'x'.repeat(300)]) { await typeInto(page, box, v); await page.keyboard.press('Enter'); await wait(100); tries.push(await page.$eval('#kit-status', (e) => e.textContent)); }
    const refused = sent.length === 0 && tries.every((t) => t.includes('valid email'));
    await typeInto(page, box, 'PASTE:  test+ui@example.com '); await btn.click({ count: 2 }); await wait(400);
    const ok = await page.$eval('#kit-status', (e) => e.textContent);
    const examField = (sent[0] || '').includes('fields[exam]');
    check(refused && sent.length === 1 && ok.includes('Check your inbox') && (path === '/' || examField) && !errs.length,
      `signup ${path}: 5 bad emails refused, nothing sent; good email (pasted with spaces, double-clicked) sent once (${sent.length})${path === '/' ? '' : ', exam field included ' + examField}`);
    await page.close();
  }

  // Focus timer: Start runs, a second click pauses, Reset goes back; Enter on the focused button starts it.
  {
    const { page, errs } = await fresh('focus-timer', {});
    const clock = () => page.$eval('#time', (e) => e.textContent.trim());
    const start = await page.evaluateHandle(() => [...document.querySelectorAll('main button')].find((b) => /Start/.test(b.textContent)));
    const c0 = await clock(); await start.click(); await wait(1600); const c1 = await clock();
    await start.click(); await wait(1200); const c2 = await clock(); await wait(1200); const c3 = await clock();
    const reset = await page.evaluateHandle(() => [...document.querySelectorAll('main button')].find((b) => /Reset/.test(b.textContent)));
    await reset.click(); await wait(300); const c4 = await clock();
    await start.focus(); await page.keyboard.press('Enter'); await wait(1600); const c5 = await clock();
    check(c0 && c1 !== c0 && c2 === c3 && c4 === c0 && c5 !== c0 && !errs.length, `click focus timer: runs (${c0} -> ${c1}), pause holds (${c2} = ${c3}), reset (${c4}), Enter starts (${c5})`);
    await page.close();
  }
}

await browser.close();
console.log(failed ? `\n${failed} FAILED` : '\nALL PASSED');
process.exit(failed ? 1 : 0);
