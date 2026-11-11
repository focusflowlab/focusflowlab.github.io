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

await browser.close();
console.log(failed ? `\n${failed} FAILED` : '\nALL PASSED');
process.exit(failed ? 1 : 0);
