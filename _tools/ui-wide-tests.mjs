// Wide UI tests in a real browser, meant for the live site (BASE=https://thefocusflowlab.com) or the preview server.
// Covers what behaviour-tests.mjs does not: typed dates in three locales, flashcard files, all 14 plan generators by
// typing, downloads, focus timer across reload/midnight, embeds in an iframe, phone width with touch, keyboard-only
// use, blocked/full storage, slow and offline network, and console errors / failed requests on every sitemap page.
// Run: copy to $TEMP/hmtools (puppeteer-core, ical.js), then  node ui-wide-tests.mjs   (exit 1 on any FAIL)
// The MailerLite signup request is always intercepted and answered locally: nothing is ever sent.
import puppeteer from 'puppeteer-core';
import { existsSync, mkdtempSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { execFileSync } from 'child_process';

const BASE = process.env.BASE || 'http://localhost:8765';
const ONLY = process.env.ONLY ? process.env.ONLY.split(',') : null;
const exe = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
let failed = 0;
const check = (ok, msg) => { console.log((ok ? 'PASS ' : 'FAIL ') + msg); if (!ok) failed++; };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const iso = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
const dateIn = (n) => { const t = new Date(); return iso(new Date(t.getFullYear(), t.getMonth(), t.getDate() + n)); };
const run = (name) => !ONLY || ONLY.includes(name);
const browsers = {};
const launch = async (lang = 'en-US') => (browsers[lang] ||= await puppeteer.launch({ executablePath: exe, headless: 'new', args: [`--lang=${lang}`], env: { ...process.env, LANG: lang } }));
async function open(path, { lang, setup, block } = {}) {
  const page = await (await launch(lang)).newPage();
  await page.setViewport({ width: 1280, height: 900 });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  page.on('dialog', (d) => { errs.push('dialog: ' + d.message()); d.dismiss(); });
  await page.setRequestInterception(true);
  page.on('request', (r) => {
    if (r.url().includes('mailerlite.com')) return r.respond({ status: 200, contentType: 'application/json', headers: { 'Access-Control-Allow-Origin': '*' }, body: '{"success":true}' });
    if (r.url().includes('cloudflareinsights') || r.url().includes('youtube')) return r.respond({ status: 204, body: '' });
    r.continue();
  });
  if (block) await page.evaluateOnNewDocument(block);
  if (setup) await page.evaluateOnNewDocument(setup);
  await page.goto(BASE + path, { waitUntil: 'networkidle0' });
  return { page, errs };
}
const clear = async (page) => { await page.evaluate(() => { try { localStorage.clear(); } catch {} }); await page.reload({ waitUntil: 'networkidle0' }); };
const typeInto = async (page, sel, v) => {
  const h = typeof sel === 'string' ? await page.$(sel) : sel;
  await h.focus(); await page.keyboard.down('Control'); await page.keyboard.press('KeyA'); await page.keyboard.up('Control'); await page.keyboard.press('Backspace');
  if (v) await page.keyboard.type(v);
};
// Type a date the way a person does in this browser's locale (segment order from Intl).
// The box's own segment order is found by trial (it need not follow navigator.language in headless Chrome).
const orders = {};
async function emptyDate(page, h) {
  await h.focus();
  for (let i = 0; i < 3; i++) { await page.keyboard.press('Backspace'); await page.keyboard.press('ArrowRight'); }
  for (let i = 0; i < 3; i++) await page.keyboard.press('ArrowLeft');
}
async function typeDate(page, sel, isoDate) {
  const h = await page.$(sel);
  const lang = await page.evaluate(() => navigator.language);
  if (!orders[lang]) {
    for (const o of [['month', 'day', 'year'], ['day', 'month', 'year'], ['year', 'month', 'day']]) {
      await emptyDate(page, h);
      for (const part of o) await page.keyboard.type({ year: '2027', month: '01', day: '31' }[part]);
      if (await h.evaluate((e) => e.value) === '2027-01-31') { orders[lang] = o; break; }
    }
    orders[lang] ||= ['month', 'day', 'year'];
  }
  const [y, m, d] = isoDate.split('-');
  await emptyDate(page, h);
  for (const part of orders[lang]) await page.keyboard.type({ year: y, month: m, day: d }[part]);
  await h.evaluate((e) => e.dispatchEvent(new Event('change', { bubbles: true })));
  return h.evaluate((e) => e.value);
}
const look = (page) => page.evaluate(() => {
  const m = document.querySelector('main'), keep = (e) => !e.closest('.kit-form, .tracker-offer, .kit') && e.offsetParent !== null;
  const result = [...m.querySelectorAll('[aria-live], output, [id^="r-"], #plan')].filter(keep).map((e) => e.innerText.trim()).join('|').replace(/\|+/g, '|').replace(/^\||\|$/g, '');
  const error = [...m.querySelectorAll('.error, [role=alert]')].filter(keep).map((e) => e.innerText.trim()).join(' ').trim();
  return { result, error, bad: (m.innerText.match(/NaN|undefined|Infinity|Invalid Date|\de\+\d/g) || []).join(',') };
});
const submit = async (page) => { const s = await page.$('main form:not(.kit-form) button[type=submit]'); if (s) await s.click(); await wait(200); };

// a. Dates typed in en-US, en-GB and German order: future, leap day, today, past, impossible (30 Feb).
if (run('dates')) {
  const year = new Date().getFullYear(); const leap = [year + 1, year + 2, year + 3, year + 4].find((y) => new Date(y, 1, 29).getDate() === 29);
  const CASES = [['in 30 days', dateIn(30), 'ok'], ['leap day', `${leap}-02-29`, 'far'], ['today', dateIn(0), 'msg'], ['yesterday', dateIn(-1), 'msg'], ['30 Feb', `${leap + 1}-02-30`, 'msg']];
  const TOOLS = [
    ['countdown', '/tools/exam-countdown/', '#examDate', async (p) => typeInto(p, '#hoursPerDay', '3')],
    ['reading', '/tools/reading-planner/', '#deadline', async (p) => typeInto(p, '#totalPages', '300')],
    ['GRE plan', '/study-plan/gre/', '#examDate', null],
    ['schedule', '/tools/study-schedule-maker/', '#ss-form li:first-child input[type=date]', async (p) => { await typeInto(p, '#ss-form li:first-child input[type=text]', 'Math'); await typeInto(p, '#ssHours', '3'); }],
  ];
  for (const lang of ['en-US', 'en-GB', 'de']) for (const [name, path, sel, prep] of TOOLS) for (const [label, value, want] of CASES) {
    const { page, errs } = await open(path, { lang }); await clear(page);
    if (prep) await prep(page);
    const typed = await typeDate(page, sel, value); await submit(page); await submit(page);
    const got = await look(page);
    const impossible = label === '30 Feb';
    const typedOk = impossible ? typed === '' : typed === value;
    // 'far': a date over the tool's range must give either a result or a clear message, never nothing.
    const ok = want === 'ok' ? got.result && !got.error : want === 'msg' ? got.error !== '' : (got.result || got.error);
    check(typedOk && ok && !got.bad && !errs.length, `date ${lang} ${name} ${label} (${value}): box holds "${typed}", ${want === 'msg' ? 'message "' + got.error.slice(0, 60) + '"' : got.error ? 'message "' + got.error.slice(0, 60) + '"' : 'result shown'}${errs[0] ? ' ERR ' + errs[0] : ''}`);
    await page.close();
  }
  // Spaced review: the day you studied can be today or past, not the future.
  for (const [label, value, want] of [['today', dateIn(0), 'ok'], ['last week', dateIn(-7), 'ok'], ['tomorrow', dateIn(1), 'msg'], ['30 Feb', `${leap + 1}-02-30`, 'ok']]) {
    const { page, errs } = await open('/tools/spaced-review/'); await clear(page);
    await typeInto(page, '#topic', 'Cell biology'); const typed = await typeDate(page, '#studied', value); await submit(page);
    const n = await page.evaluate(() => JSON.parse(localStorage.getItem('ffl-spaced-review') || '[]').length), got = await look(page);
    check((want === 'ok' ? n === 1 : n === 0 && got.error) && !got.bad && !errs.length, `date spaced review studied ${label}: box "${typed}", ${n} topic saved ${got.error ? '(' + got.error.slice(0, 50) + ')' : ''}`);
    await page.close();
  }
}

// b. Flashcard import: odd files, duplicates, HTML in cards, a file too big for browser storage.
if (run('import')) {
  const dir = mkdtempSync(join(tmpdir(), 'ffl-import-'));
  const card = (i) => ({ front: `Q${i} "quoted", with comma\nand newline`, back: `A${i} <img src=x onerror="window.__xss=1">`, step: 0, due: '2026-01-01' });
  const files = {
    'empty.json': '', 'text.txt': 'hello', 'object.json': '{"front":"a","back":"b"}', 'wrong-shape.json': '[{"q":1},{"front":2,"back":3}]',
    'mixed.json': JSON.stringify([card(1), { front: 'only front' }, null, 7, card(2)]),
    'utf16.json': Buffer.concat([Buffer.from([0xff, 0xfe]), Buffer.from(JSON.stringify([card(3)]), 'utf16le')]),
    'bom-utf8.json': Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(JSON.stringify([card(4)]))]),
    'big.json': JSON.stringify(Array.from({ length: 5000 }, (_, i) => card(100 + i))),
    'huge.json': JSON.stringify(Array.from({ length: 60000 }, (_, i) => ({ front: 'F'.repeat(80) + i, back: 'B'.repeat(80) + i }))),
  };
  for (const [n, c] of Object.entries(files)) writeFileSync(join(dir, n), c);
  const { page, errs } = await open('/tools/flashcards/'); await clear(page);
  const load = async (name) => {
    const [chooser] = await Promise.all([page.waitForFileChooser(), page.evaluate(() => document.getElementById('fc-import').click())]);
    await chooser.accept([join(dir, name)]); await wait(700);
    return [await page.$eval('#fc-error', (e) => e.textContent), await page.$eval('#fc-count', (e) => e.textContent)];
  };
  const expect = [
    ['empty.json', /isn’t a FocusFlow/, '0'], ['text.txt', /isn’t a FocusFlow/, '0'], ['object.json', /isn’t a FocusFlow/, '0'], ['wrong-shape.json', /isn’t a FocusFlow/, '0'],
    ['mixed.json', /^2 cards imported\.$/, '2'], ['mixed.json', /^0 cards imported, 2 already in your deck\.$/, '2'],
    ['utf16.json', /isn’t a FocusFlow|1 card imported/, null], ['bom-utf8.json', /1 card imported/, null], ['big.json', /5000 cards imported/, null],
  ];
  for (const [name, re, count] of expect) {
    const [msg, c] = await load(name);
    check(re.test(msg) && (count === null || c === count), `import ${name}: "${msg}" (deck ${c})`);
  }
  const shown = await page.evaluate(() => [document.querySelector('#fc-list li')?.innerHTML.includes('&lt;img') ?? false, window.__xss ?? 0]);
  check(shown[0] && !shown[1], `import: HTML in a card is shown as text, never run (${shown})`);
  const [hugeMsg] = await load('huge.json');
  const note = await page.$eval('#ff-store-note', (e) => e.textContent).catch(() => '');
  check(/for this visit only/.test(hugeMsg) && note.includes('isn’t saving'), `import huge.json (about 10 MB, over browser storage): "${hugeMsg.slice(0, 60)}", page notice shown`);
  check(!errs.length, `import: no script errors (${errs[0] || 'ok'})`);
  await page.close();
}

// c. All 14 plan generators by typing: good plan, odd hours, near/past/far dates, print buttons, calendar file.
if (run('plans')) {
  const { page: p0 } = await open('/tools/practice-score-tracker/');
  const slugs = Object.keys(await p0.evaluate(() => window.EXAM_TOPICS)); await p0.close();
  let ICAL = null; try { ICAL = (await import('ical.js')).default; } catch {}
  for (const slug of slugs) {
    const { page, errs } = await open(`/study-plan/${slug}/`, { setup: () => { window.__prints = 0; window.print = () => { window.__prints++; }; const real = URL.createObjectURL.bind(URL); window.__blobs = []; URL.createObjectURL = (b) => { window.__blobs.push(b); return real(b); }; HTMLAnchorElement.prototype.click = function () {}; } });
    await clear(page);
    const cases = [];
    for (const [h, d, want] of [['2.5', 60, 'ok'], ['99999999', 60, 'msg'], ['', 60, 'msg'], ['0', 60, 'msg'], ['-1', 60, 'msg'], ['14', 60, 'ok'], ['3', 0, 'msg'], ['3', -10, 'msg'], ['3', 2, 'msg'], ['3', 3, 'ok'], ['3', 900, 'msg']]) {
      await typeInto(page, '#hoursPerDay', h); await typeDate(page, '#examDate', dateIn(d)); await page.keyboard.press('Enter'); await wait(250);
      const g = await look(page);
      const pass = (want === 'ok' ? g.result && !g.error : g.error) && !g.bad;
      if (!pass) cases.push(`${h}h/${d}d: ${g.error || g.result.slice(0, 40)}`);
    }
    await typeInto(page, '#hoursPerDay', '3'); await typeDate(page, '#examDate', dateIn(45)); await page.keyboard.press('Enter'); await wait(300);
    for (const id of ['print-plan', 'print-days', 'print-pack']) { await page.click('#' + id); await wait(300); }
    await page.click('#add-cal'); await wait(300);
    const out = await page.evaluate(async () => [window.__prints, window.__blobs.length ? await window.__blobs[window.__blobs.length - 1].text() : '']);
    let events = (out[1].match(/BEGIN:VEVENT/g) || []).length, parsed = 'not parsed';
    if (ICAL && out[1]) { try { parsed = new ICAL.Component(ICAL.parse(out[1])).getAllSubcomponents('vevent').length + ' events parsed'; } catch (e) { parsed = 'PARSE ERROR ' + e.message; } }
    check(!cases.length && out[0] === 3 && events > 5 && !/ERROR/.test(parsed) && !errs.length, `plan ${slug}: 11 typed cases ${cases.length ? 'FAILED ' + cases.join('; ') : 'ok'}, 3 print buttons, calendar ${events} events (${parsed})${errs[0] ? ' ERR ' + errs[0] : ''}`);
    await page.close();
  }
}

// d. Downloads: templates open with the right sheets/headers; tool CSV/JSON/ICS exports are well formed.
if (run('downloads')) {
  const dir = mkdtempSync(join(tmpdir(), 'ffl-dl-'));
  for (const f of ['final-grade-template.xlsx', 'mcat-error-log-template.xlsx', 'practice-score-log.xlsx', 'study-schedule-template.xlsx', 'mcat-error-log-template.csv']) {
    const res = await fetch(`${BASE}/assets/templates/${f}`);
    const buf = Buffer.from(await res.arrayBuffer()); writeFileSync(join(dir, f), buf);
    let info = '';
    try {
      info = execFileSync('python', ['-I', '-c', `import sys,csv,openpyxl
p=sys.argv[1]
if p.endswith('.csv'):
  rows=list(csv.reader(open(p,encoding='utf-8-sig'))); print(len(rows),'rows;',rows[0][:4])
else:
  wb=openpyxl.load_workbook(p); ws=wb.worksheets[0]; print(wb.sheetnames, [c.value for c in ws[1]][:4], ws.max_row,'rows')`, join(dir, f)], { encoding: 'utf8' }).trim();
    } catch (e) { info = 'ERROR ' + (e.stderr || e.message).toString().split('\n').slice(-2).join(' '); }
    check(res.status === 200 && buf.length > 200 && !info.startsWith('ERROR'), `download ${f}: ${res.status}, ${buf.length} bytes, opens: ${info.slice(0, 120)}`);
  }
  const grab = { setup: () => { const real = URL.createObjectURL.bind(URL); window.__blobs = []; URL.createObjectURL = (b) => { window.__blobs.push(b); return real(b); }; HTMLAnchorElement.prototype.click = function () {}; } };
  {
    const { page } = await open('/tools/error-log/', grab); await clear(page);
    await typeInto(page, '#el-what', 'Mixed up "beta-1" vs beta-2, again'); await typeInto(page, '#el-fix', 'Card: B1 = heart; B2 = lungs'); await submit(page);
    await page.click('#el-csv'); await wait(300);
    const csv = await page.evaluate(async () => window.__blobs.length ? await window.__blobs[0].text() : '');
    check(csv.split(/\r?\n/).filter(Boolean).length === 2 && csv.includes('"Mixed up ""beta-1"" vs beta-2, again"'), `download error log CSV: header + 1 row, quotes doubled (${JSON.stringify(csv.split(/\r?\n/)[1]?.slice(0, 80))})`);
    await page.close();
  }
  {
    const { page } = await open('/tools/spaced-review/', grab); await clear(page);
    await typeInto(page, '#topic', 'Renal; "acid-base", part 2'); await submit(page);
    await page.click('#download-ics'); await wait(300);
    const ics = await page.evaluate(async () => window.__blobs.length ? await window.__blobs[0].text() : '');
    let parsed = 'not parsed'; try { const ICAL = (await import('ical.js')).default; parsed = new ICAL.Component(ICAL.parse(ics)).getAllSubcomponents('vevent').length + ' events'; } catch (e) { parsed = 'PARSE ERROR ' + e.message; }
    check(ics.startsWith('BEGIN:VCALENDAR') && !/ERROR/.test(parsed) && /SUMMARY:.*Renal\\; "acid-base"\\, part 2/.test(ics), `download spaced review ICS: ${parsed}, ; and , escaped in the summary`);
    await page.close();
  }
}

// e. Focus timer: reload mid-block, block ending while the tab was closed, a block across midnight, hidden tab.
if (run('timer')) {
  const clockShift = () => {
    const Real = Date; const shift = () => Number(sessionStorage.getItem('shift') || 0);
    class Fake extends Real { constructor(...a) { if (a.length === 0) super(Real.now() + shift()); else super(...a); } static now() { return Real.now() + shift(); } }
    window.Date = Fake;
  };
  const { page, errs } = await open('/tools/focus-timer/', { setup: clockShift }); await clear(page);
  const t = () => page.$eval('#time', (e) => e.textContent.trim());
  const label = () => page.$eval('#start', (e) => e.textContent.trim());
  const shiftTo = (ms) => page.evaluate((v) => sessionStorage.setItem('shift', String(v)), ms);
  const doneOn = (d) => page.evaluate((k) => localStorage.getItem(k), 'ffl-timer-' + d);
  await page.click('#start'); await wait(300);
  await shiftTo(5 * 60_000); await page.reload({ waitUntil: 'networkidle0' }); await wait(400);
  const mid = [await t(), await label()];
  await shiftTo(31 * 60_000); await page.reload({ waitUntil: 'networkidle0' }); await wait(400);
  const ended = [await t(), await page.$eval('#phase', (e) => e.textContent), await doneOn(dateIn(0))];
  await page.reload({ waitUntil: 'networkidle0' }); await wait(300);
  const again = await doneOn(dateIn(0));
  check(/^(19|20):\d\d$/.test(mid[0]) && mid[1] === 'Pause', `timer reload mid-block: carries on (${mid})`);
  check(ended[1] === 'Break' && ended[2] === '1' && again === '1', `timer block ended while closed: counted once (${ended}, after another reload ${again})`);
  // Midnight: start at 23:50 local, finish at 00:15 the next day: counts for the new day.
  await page.click('#reset'); await page.evaluate(() => { localStorage.clear(); });
  const now = new Date(), toMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1) - now;
  await shiftTo(toMidnight - 10 * 60_000); await page.reload({ waitUntil: 'networkidle0' });
  await page.click('#start'); await wait(300);
  await shiftTo(toMidnight + 16 * 60_000); await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange'))); await wait(600);
  check(await doneOn(dateIn(1)) === '1' && !(await doneOn(dateIn(0))), `timer block across midnight: counted for the new day (${dateIn(1)})`);
  check(!errs.length, `timer: no script errors (${errs[0] || 'ok'})`);
  await page.close();
}

// f. Embeds inside an iframe on another page: loads, works at 320 px and 600 px, dark theme, credit link.
if (run('embeds')) {
  for (const slug of ['exam-countdown', 'final-grade-calculator', 'gpa-calculator', 'reading-planner', 'test-time-calculator', 'weighted-grade-calculator']) {
    for (const [w, scheme] of [[320, 'light'], [600, 'dark']]) {
      const page = await (await launch()).newPage(); const errs = []; page.on('pageerror', (e) => errs.push(e.message));
      await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
      await page.setContent(`<html><body style="margin:0"><iframe id="f" src="${BASE}/embed/${slug}/" style="width:${w}px;height:900px;border:0"></iframe></body></html>`, { waitUntil: 'networkidle0' });
      const frame = page.frames().find((f) => f.url().includes('/embed/'));
      const info = await frame.evaluate(() => {
        const a = document.querySelector('.embed-credit a');
        return { over: document.documentElement.scrollWidth - document.documentElement.clientWidth, href: a?.getAttribute('href'), target: a?.target, bg: getComputedStyle(document.body).backgroundColor, inputs: document.querySelectorAll('input,select').length };
      });
      check(info.over <= 0 && info.href?.includes(`/tools/${slug}/`) && info.target === '_blank' && info.inputs > 0 && !errs.length, `embed ${slug} in iframe ${w}px ${scheme}: no sideways scroll (${info.over}), credit link to the tool in a new tab, background ${info.bg}`);
      await page.close();
    }
  }
}

// g. Phone (375 px, touch): menus open/close by tap and Escape, theme toggle, a form used by tapping.
if (run('mobile')) {
  const page = await (await launch()).newPage(); const errs = []; page.on('pageerror', (e) => errs.push(e.message));
  await page.setViewport({ width: 375, height: 812, isMobile: true, hasTouch: true });
  await page.goto(BASE + '/', { waitUntil: 'networkidle0' });
  const vis = (id) => page.$eval(id, (e) => e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden');
  const res = [];
  for (const id of ['menu-plans', 'menu-tools', 'menu-guides', 'menu-planners']) {
    await page.tap(`[aria-controls="${id}"]`); await wait(200); const opened = await vis('#' + id);
    const over = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    await page.keyboard.press('Escape'); await wait(150); const closed = !(await vis('#' + id));
    res.push(opened && closed && over <= 0);
  }
  await page.tap('[aria-controls="menu-tools"]'); await wait(150);
  // Tap a plain spot outside the open panel (the panel covers part of the page on a phone; a link under the finger would navigate).
  const spot = await page.evaluate(() => {
    for (let y = innerHeight - 10; y > 60; y -= 20) for (const x of [10, innerWidth / 2, innerWidth - 10]) {
      const e = document.elementFromPoint(x, y);
      if (e && !e.closest('a, button, input, select, textarea, label, .nav-item, [role=button]')) return [x, y];
    }
    return null;
  });
  if (spot) await page.touchscreen.tap(spot[0], spot[1]); await wait(150);
  const tapOut = !(await vis('#menu-tools'));
  const th0 = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  await page.tap('.theme-toggle'); await wait(100); const th1 = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  check(res.every(Boolean) && tapOut && th1 && th1 !== th0 && !errs.length, `phone 375px: 4 menus open by tap and close by Escape (${res}), tap outside closes (${tapOut}), theme toggle ${th0}→${th1}`);
  for (const [path, fill] of [['/tools/test-time-calculator/', [['#totalMin', '90'], ['#questions', '60']]], ['/tools/practice-score-tracker/', [['#sc-right', '7'], ['#sc-total', '10']]], ['/study-plan/mcat/', []]]) {
    await page.goto(BASE + path, { waitUntil: 'networkidle0' }); await page.evaluate(() => localStorage.clear());
    for (const [s, v] of fill) { await page.tap(s); await typeInto(page, s, v); } // tap, then clear and type (boxes may hold sample values)
    if (path.includes('study-plan')) await page.evaluate((d) => { document.getElementById('examDate').value = d; }, dateIn(60));
    await page.tap('main form:not(.kit-form) button[type=submit]'); await wait(300);
    const g = await look(page), over = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(g.result && !g.error && over <= 0, `phone 375px ${path}: filled and submitted by tapping, result shown, no sideways scroll (${over})${g.error ? ' ERROR "' + g.error.slice(0, 80) + '"' : ''}${g.result ? '' : ' NO RESULT'}`);
  }
  await page.close();
}

// h. Keyboard only: every Tab stop shows a visible focus mark; Enter/Space work on buttons and menus.
if (run('keyboard')) {
  const pages = ['/', '/tools/', '/study-plan/gre/', '/guides/how-to-create-a-study-schedule/', '/planners/gre-8-week-planner/', '/exam-facts/',
    ...['test-time-calculator', 'final-grade-calculator', 'gpa-calculator', 'weighted-grade-calculator', 'exam-countdown', 'reading-planner', 'study-schedule-maker', 'practice-score-tracker', 'error-log', 'spaced-review', 'flashcards', 'focus-timer'].map((s) => `/tools/${s}/`)];
  for (const path of pages) {
    const { page, errs } = await open(path);
    const misses = [], seen = new Set();
    for (let i = 0; i < 120; i++) {
      await page.keyboard.press('Tab');
      const f = await page.evaluate(() => {
        const e = document.activeElement; if (!e || e === document.body) return null;
        const s = getComputedStyle(e), r = e.getBoundingClientRect();
        const mark = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== 'none';
        return { id: e.tagName + (e.id ? '#' + e.id : '') + ':' + (e.textContent || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 25), mark, size: r.width > 0 && r.height > 0 };
      });
      if (!f) break;
      if (seen.has(f.id)) { if (seen.size > 5) break; continue; }
      seen.add(f.id);
      if (!f.mark || !f.size) misses.push(f.id + (f.mark ? '' : ' (no focus mark)') + (f.size ? '' : ' (zero size)'));
    }
    check(!misses.length && seen.size > 3 && !errs.length, `keyboard ${path}: ${seen.size} tab stops, all with a visible focus mark${misses.length ? ' MISSING: ' + misses.slice(0, 5).join('; ') : ''}`);
    await page.close();
  }
  const { page, errs } = await open('/tools/focus-timer/');
  await page.focus('#start'); await page.keyboard.press('Space'); await wait(1300); const run1 = await page.$eval('#start', (e) => e.textContent);
  await page.keyboard.press('Space'); await wait(200); const run2 = await page.$eval('#start', (e) => e.textContent);
  await page.goto(BASE + '/', { waitUntil: 'networkidle0' });
  await page.focus('[aria-controls="menu-tools"]'); await page.keyboard.press('Enter'); await wait(150);
  const open1 = await page.$eval('[aria-controls="menu-tools"]', (e) => e.getAttribute('aria-expanded'));
  await page.keyboard.press('Escape'); await wait(150);
  const back = await page.evaluate(() => [document.activeElement.getAttribute('aria-controls'), document.querySelector('[aria-controls="menu-tools"]').getAttribute('aria-expanded')]);
  await page.focus('.theme-toggle'); const th0 = await page.evaluate(() => document.documentElement.getAttribute('data-theme')); await page.keyboard.press('Space'); await wait(100);
  const th1 = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  check(run1 === 'Pause' && run2 === 'Resume' && open1 === 'true' && back[0] === 'menu-tools' && back[1] === 'false' && th1 !== th0 && !errs.length, `keyboard: Space starts/pauses the timer (${run1}/${run2}), Enter opens the menu, Escape closes it and returns focus, Space switches theme`);
  await page.close();
}

// i. Storage blocked (some private windows) or full: every tool still works and says entries are not being saved.
if (run('storage')) {
  const BLOCKED = () => { Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('blocked', 'SecurityError'); } }); };
  const FULL = () => { Storage.prototype.setItem = function () { throw new DOMException('full', 'QuotaExceededError'); }; };
  const tools = [['/tools/test-time-calculator/', [['#totalMin', '90'], ['#questions', '60']], false], ['/tools/final-grade-calculator/', [['#current', '82'], ['#weight', '30'], ['#target', '85']], false],
    ['/tools/practice-score-tracker/', [['#sc-right', '7'], ['#sc-total', '10']], true], ['/tools/error-log/', [['#el-what', 'Beta blockers']], true], ['/tools/spaced-review/', [['#topic', 'Cells']], true],
    ['/tools/flashcards/', [['#fcFront', 'Q'], ['#fcBack', 'A']], true], ['/tools/gpa-calculator/', [], false], ['/tools/focus-timer/', [], false], ['/', [], false], ['/study-plan/gre/', [], false]];
  for (const [mode, fn] of [['blocked', BLOCKED], ['full', FULL]]) for (const [path, fill, logger] of tools) {
    const { page, errs } = await open(path, { block: fn });
    for (const [s, v] of fill) await typeInto(page, s, v);
    if (path.includes('study-plan')) { await typeDate(page, '#examDate', dateIn(60)); }
    if (path.includes('focus-timer')) { await page.click('#start'); await wait(300); await page.click('#start'); }
    if (fill.length || path.includes('study-plan')) await submit(page);
    const g = await look(page), note = await page.$('#ff-store-note');
    const shows = logger ? (await page.evaluate(() => document.querySelector('main').innerText)).includes('Cells') || g.result || (await page.$$eval('#fc-list li, #el-list li, #sc-list li', (l) => l.length)) > 0 : true;
    check(!errs.length && !g.bad && shows && (!logger || note), `storage ${mode} ${path}: works${logger ? ', entry shown, "not saving" notice' + (note ? '' : ' MISSING') : ''}${errs[0] ? ' ERR ' + errs[0] : ''}`);
    await page.close();
  }
}

// j. Slow 3G and offline: tools load and calculate; signup offline says it could not reach the service.
if (run('network')) {
  const { page, errs } = await open('/');
  const cdp = await page.createCDPSession();
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 400, downloadThroughput: 50_000, uploadThroughput: 20_000 });
  const t0 = Date.now(); await page.goto(BASE + '/tools/gpa-calculator/', { waitUntil: 'load', timeout: 120_000 }); const slow = Date.now() - t0;
  const gpa = await page.$eval('#r-term', (e) => e.textContent);
  await cdp.send('Network.emulateNetworkConditions', { offline: true, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  await typeInto(page, '.gpa-row input[type=number]', '4'); await page.click('main h1'); await wait(200);
  const gpa2 = await page.$eval('#r-term', (e) => e.textContent);
  check(/^\d\.\d\d$/.test(gpa) && gpa2 !== gpa && !errs.length, `network slow 3G: GPA page loaded in ${(slow / 1000).toFixed(1)} s and works (${gpa}); offline after load still calculates (${gpa2})`);
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  await page.close();
  const p2 = await (await launch()).newPage(); const e2 = []; p2.on('pageerror', (e) => e2.push(e.message));
  await p2.goto(BASE + '/study-plan/gre/', { waitUntil: 'networkidle0' });
  await p2.setOfflineMode(true);
  await typeInto(p2, '#kit-email', 'test+offline@example.com'); await p2.keyboard.press('Enter'); await wait(800);
  const msg = await p2.$eval('#kit-status', (e) => e.textContent), btn = await p2.$eval('#kit-form button[type=submit]', (b) => b.disabled);
  check(/couldn’t reach/.test(msg) && !btn && !e2.length, `network offline signup: "${msg.slice(0, 60)}", button usable again`);
  await p2.close();
}

// k. Every sitemap page: no console errors or warnings, no failed or 4xx/5xx requests (analytics/video excluded).
if (run('console')) {
  const xml = await (await fetch(BASE + '/sitemap.xml')).text();
  const urls = [...xml.matchAll(/<loc>https:\/\/thefocusflowlab\.com([^<]*)<\/loc>/g)].map((m) => m[1]);
  const b = await launch();
  for (const path of urls) {
    const page = await b.newPage(); const issues = [];
    page.on('console', (m) => { if (['error', 'warning', 'warn'].includes(m.type())) issues.push(m.type() + ': ' + m.text().slice(0, 100)); });
    page.on('pageerror', (e) => issues.push('pageerror: ' + e.message));
    page.on('requestfailed', (r) => { if (!/cloudflareinsights|youtube|ytimg|googlevideo|doubleclick|google\.com/.test(r.url())) issues.push('failed: ' + r.url().slice(0, 90) + ' ' + r.failure()?.errorText); });
    page.on('response', (r) => { if (r.status() >= 400 && !/cloudflareinsights|youtube|ytimg|googlevideo/.test(r.url())) issues.push(r.status() + ': ' + r.url().slice(0, 90)); });
    await page.goto(BASE + path, { waitUntil: 'networkidle0', timeout: 60_000 }).catch((e) => issues.push('load: ' + e.message));
    check(!issues.length, `console ${path}: ${issues.length ? issues.slice(0, 3).join(' | ') : 'clean'}`);
    await page.close();
  }
}

for (const b of Object.values(browsers)) await b.close();
console.log(failed ? `\n${failed} FAILED` : '\nALL PASSED');
process.exit(failed ? 1 : 0);
