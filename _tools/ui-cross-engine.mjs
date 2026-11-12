// Cross-engine UI tests (Playwright): the same real typing/clicking checks in Chromium (control), Firefox and WebKit
// (Safari's engine). Meant for the live site:  BASE=https://thefocusflowlab.com node ui-cross-engine.mjs
// Setup in $TEMP/hmtools:  npm i --no-save playwright-core@1.48.2 && npx playwright-core install firefox webkit
// ENGINES=firefox,webkit and ONLY=numbers,loggers,... narrow a run. Exit 1 on any FAIL.
// MailerLite is always intercepted and answered locally: nothing is ever sent.
import { chromium, firefox, webkit } from 'playwright-core';
import { existsSync, mkdtempSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const BASE = process.env.BASE || 'http://localhost:8765';
const ONLY = process.env.ONLY ? process.env.ONLY.split(',') : null;
const chrome = ['C:/Program Files/Google/Chrome/Application/chrome.exe'].find(existsSync);
const LAUNCH = { chromium: () => chromium.launch({ executablePath: chrome }), firefox: () => firefox.launch(), webkit: () => webkit.launch() };
const ENGINES = process.env.ENGINES ? process.env.ENGINES.split(',') : Object.keys(LAUNCH);
let failed = 0;
const tally = {};
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const iso = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
const dateIn = (n) => { const t = new Date(); return iso(new Date(t.getFullYear(), t.getMonth(), t.getDate() + n)); };
const run = (n) => !ONLY || ONLY.includes(n);

for (const engine of ENGINES) {
  const browser = await LAUNCH[engine]();
  tally[engine] = { pass: 0, fail: 0 };
  const check = (ok, msg) => { console.log((ok ? 'PASS ' : 'FAIL ') + `[${engine}] ` + msg); tally[engine][ok ? 'pass' : 'fail']++; if (!ok) failed++; };
  async function open(path, { touch, width = 1280, init, storage } = {}) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, hasTouch: !!touch, locale: 'en-US' });
    await ctx.route(/mailerlite\.com/, (r) => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'Access-Control-Allow-Origin': '*' }, body: '{"success":true}' }));
    await ctx.route(/cloudflareinsights|youtube|ytimg/, (r) => r.fulfill({ status: 204, body: '' }));
    if (storage) await ctx.addInitScript(storage);
    if (init) await ctx.addInitScript(init);
    const page = await ctx.newPage(); const errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    page.on('dialog', (d) => { errs.push('dialog ' + d.message()); d.dismiss(); });
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    if (!storage) { await page.evaluate(() => localStorage.clear()); await page.reload({ waitUntil: 'networkidle' }); }
    return { page, errs, close: () => ctx.close() };
  }
  const typeInto = async (page, sel, v, paste) => {
    const h = typeof sel === 'string' ? page.locator(sel).first() : sel;
    await h.click(); await page.keyboard.press('ControlOrMeta+a'); await page.keyboard.press('Backspace');
    if (v) paste ? await page.keyboard.insertText(v) : await page.keyboard.type(v);
  };
  const look = (page) => page.evaluate(() => {
    const m = document.querySelector('main'), keep = (e) => !e.closest('.kit-form, .tracker-offer, .kit') && e.offsetParent !== null;
    const result = [...m.querySelectorAll('[aria-live], output, [id^="r-"], #plan')].filter(keep).map((e) => e.innerText.trim()).join('|');
    const error = [...m.querySelectorAll('.error, [role=alert]')].filter(keep).map((e) => e.innerText.trim()).join(' ').trim();
    return { result, error, bad: (m.innerText.match(/NaN|undefined|Infinity|Invalid Date|\de\+\d/g) || []).join(',') };
  });
  const press = async (page, enter) => {
    const s = page.locator('main form:not(.kit-form) button[type=submit]').first();
    const has = await s.count();
    if (enter) await page.keyboard.press('Enter'); else if (has) await s.click();
    if (!has) await page.locator('main h1').click();
    await wait(200);
  };

  // Number boxes: odd values typed or pasted, Enter then click, then the box fixed.
  if (run('numbers')) {
    const ODD = [['99999999'], ['-5'], ['2.5'], [''], ['1e3'], ['0'], [' 42 ', true], ['12abc', true], ['1e']];
    const T = [
      ['/tools/test-time-calculator/', { '#totalMin': '90', '#questions': '60' }],
      ['/tools/final-grade-calculator/', { '#current': '82', '#weight': '30', '#target': '85' }],
      ['/tools/reading-planner/', { '#totalPages': '420', '#pagesRead': '60' }, ['deadline', 16]],
      ['/tools/gpa-calculator/', { '#prevGpa': '3.2', '#prevCredits': '45', '#targetGpa': '3.5', '#nextCredits': '15' }],
      ['/tools/weighted-grade-calculator/', { '.wg-row:nth-child(1) input:nth-of-type(2)': '40', '.wg-row:nth-child(1) input:nth-of-type(3)': '80' }],
      ['/tools/exam-countdown/', { '#hoursPerDay': '3' }, ['examDate', 30]],
      ['/tools/practice-score-tracker/', { '#sc-target': '75', '#sc-hours': '20' }],
    ];
    for (const [path, good, date] of T) {
      const fill = async (page) => {
        for (const [s, v] of Object.entries(good)) await typeInto(page, s, v);
        if (date) await page.evaluate(([id, d]) => { const e = document.getElementById(id); e.value = d; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); }, [date[0], dateIn(date[1])]);
      };
      const clean = await open(path); await fill(clean.page); await press(clean.page);
      const want = await look(clean.page); await clean.close();
      const misses = [];
      for (const sel of Object.keys(good)) for (const [v, paste] of ODD) {
        const { page, errs, close } = await open(path); await fill(page);
        await typeInto(page, sel, v, paste); await press(page, true); await press(page);
        const st = await page.locator(sel).first().evaluate((e) => ({ v: e.value.trim(), bad: !!(e.validity && e.validity.badInput), min: e.min, max: e.max, step: e.step }));
        const n = Number(st.v), whole = st.step !== '' && Number(st.step) >= 1;
        const outside = st.bad || (st.v !== '' && (!Number.isFinite(n) || (st.min !== '' && n < Number(st.min)) || (st.max !== '' && n > Number(st.max)) || (whole && !Number.isInteger(n))));
        const got = await look(page);
        await typeInto(page, sel, good[sel]); await press(page);
        const after = await look(page);
        const problems = [];
        if (errs.length || got.bad || after.bad) problems.push('error/NaN ' + (errs[0] || got.bad || after.bad));
        if (outside && !got.error) problems.push(`no message (box "${st.v}"${st.bad ? ', unreadable' : ''})`);
        if (after.result !== want.result || after.error !== want.error) problems.push(`after fix ${after.error || after.result.slice(0, 50)}`);
        if (problems.length) misses.push(`${sel}=${JSON.stringify(v)}: ${problems.join('; ')}`);
        await close();
      }
      check(!misses.length, `numbers ${path}: ${Object.keys(good).length} boxes x ${ODD.length} odd values${misses.length ? ' FAILED ' + misses.join(' | ') : ''}`);
    }
  }

  // Loggers: the owner's case, blank entries, two entries, delete, reload.
  if (run('loggers')) {
    {
      const { page, errs, close } = await open('/tools/practice-score-tracker/');
      const count = () => page.evaluate(() => JSON.parse(localStorage.getItem('ffl-scores') || '{"entries":[]}').entries.length);
      await typeInto(page, '#sc-right', '30'); await typeInto(page, '#sc-total', '4566505'); await press(page, true);
      const e1 = (await look(page)).error, c1 = await count();
      await typeInto(page, '#sc-total', '40'); await press(page, true);
      const s2 = await page.evaluate(() => [document.getElementById('sc-count').textContent, document.getElementById('sc-overall').textContent]);
      await press(page); const c3 = await count();
      await page.locator('#sc-list button').first().click(); await wait(150);
      await page.reload({ waitUntil: 'networkidle' }); const c4 = await count();
      check(e1.includes('5,000') && c1 === 0 && s2[0] === '40' && s2[1] === '75%' && c3 === 1 && c4 === 0 && !errs.length, `loggers score tracker: huge refused, fixed logged (${s2}), empty resubmit ignored, Remove + reload (${c4})${errs[0] ? ' ERR ' + errs[0] : ''}`);
      await close();
    }
    for (const [path, key, fill, list] of [['/tools/error-log/', 'ffl-errorlog', ['#el-what'], (s) => s.items.length], ['/tools/spaced-review/', 'ffl-spaced-review', ['#topic'], (s) => s.length], ['/tools/flashcards/', 'ffl-flashcards', ['#fcFront', '#fcBack'], (s) => s.length]]) {
      const { page, errs, close } = await open(path);
      const n = async () => { const v = await page.evaluate((k) => localStorage.getItem(k), key); return v ? list(JSON.parse(v)) : 0; };
      const put = async (v, paste) => { for (const s of fill) await typeInto(page, s, v, paste); await press(page); };
      await put(''); const blank = [await n(), (await look(page)).error];
      await put('    ', true); const spaces = await n();
      await put('Beta blockers'); await put('Beta blockers'); const two = await n();
      await page.reload({ waitUntil: 'networkidle' }); const kept = await n();
      await page.locator('main button', { hasText: /^(Delete|Remove)$/ }).first().click(); await wait(150);
      const del = await n();
      check(blank[0] === 0 && blank[1] && spaces === 0 && two === 2 && kept === 2 && del === 1 && !errs.length, `loggers ${path}: blank/spaces refused, 2 saved, reload keeps 2, Delete leaves ${del}${errs[0] ? ' ERR ' + errs[0] : ''}`);
      await close();
    }
  }

  // Dates typed into the date boxes (segment order found by trial), plus impossible 30 Feb.
  if (run('dates')) {
    const year = new Date().getFullYear(); const leap = [1, 2, 3, 4].map((k) => year + k).find((y) => new Date(y, 1, 29).getDate() === 29);
    for (const [name, path, sel, prep] of [['countdown', '/tools/exam-countdown/', '#examDate', async (p) => typeInto(p, '#hoursPerDay', '3')], ['reading', '/tools/reading-planner/', '#deadline', async (p) => typeInto(p, '#totalPages', '300')], ['GRE plan', '/study-plan/gre/', '#examDate', null]]) {
      const res = [];
      let order = null;
      for (const [label, value, want] of [['in 30 days', dateIn(30), 'ok'], ['today', dateIn(0), 'msg'], ['yesterday', dateIn(-1), 'msg'], ['leap day', `${leap}-02-29`, 'any'], ['30 Feb', `${leap + 1}-02-30`, 'msg']]) {
        const typeParts = async (pg, o, [y, m, d]) => { await pg.locator(sel).click({ position: { x: 6, y: 10 } }); for (const part of o) await pg.keyboard.type({ year: y, month: m, day: d }[part]); };
        if (!order && order !== false) { // find the box's key order once, on a throwaway page
          const t = await open(path); order = false;
          for (const o of [['month', 'day', 'year'], ['day', 'month', 'year'], ['year', 'month', 'day']]) {
            await t.page.reload({ waitUntil: 'networkidle' }); await typeParts(t.page, o, ['2027', '01', '31']);
            if (await t.page.locator(sel).inputValue() === '2027-01-31') { order = o; break; }
          }
          await t.close();
        }
        const { page, errs, close } = await open(path);
        if (prep) await prep(page);
        const box = page.locator(sel);
        const typeParts2 = (o, parts) => typeParts(page, o, parts);
        let typed = '', how = 'typed';
        if (order) { await typeParts2(order, value.split('-')); typed = await box.inputValue(); }
        else { how = 'fill'; try { await box.fill(value); } catch { /* impossible date */ } typed = await box.inputValue(); }
        await box.dispatchEvent('change');
        await press(page); await press(page);
        const g = await look(page);
        const ok = want === 'ok' ? g.result && !g.error : want === 'msg' ? !!g.error : (g.result || g.error);
        // A real date box empties itself on 30 Feb; a plain-text one (WebKit on Windows, older Safari) keeps it and the tool must refuse it.
        const boxOk = label === '30 Feb' ? typed === '' || !!g.error : typed === value;
        if (!(ok && boxOk && !g.bad && !errs.length)) res.push(`${label}: box "${typed}" (${how}), ${g.error || (g.result ? 'result' : 'nothing')}${errs[0] ? ' ERR ' + errs[0] : ''}`);
        await close();
      }
      check(!res.length, `dates ${name}: future, today, yesterday, leap day, 30 Feb typed (order ${order ? order.join('/') : 'none: box takes no typing, used fill'})${res.length ? ' FAILED ' + res.join(' | ') : ''}`);
    }
  }

  // Flashcard import files.
  if (run('import')) {
    const dir = mkdtempSync(join(tmpdir(), 'ffl-x-'));
    const card = (i) => ({ front: `Q${i} "quoted", line\nbreak`, back: `A${i} <img src=x onerror="window.__xss=1">` });
    const files = { 'empty.json': '', 'text.txt': 'hello', 'mixed.json': JSON.stringify([card(1), { front: 'x' }, null, card(2)]), 'bom.json': '\ufeff' + JSON.stringify([card(3)]), 'big.json': JSON.stringify(Array.from({ length: 3000 }, (_, i) => card(10 + i))) };
    for (const [n, c] of Object.entries(files)) writeFileSync(join(dir, n), c);
    const { page, errs, close } = await open('/tools/flashcards/');
    const res = [];
    for (const [name, re, count] of [['empty.json', /isn’t a FocusFlow/, '0'], ['text.txt', /isn’t a FocusFlow/, '0'], ['mixed.json', /^2 cards imported\.$/, '2'], ['mixed.json', /already in your deck/, '2'], ['bom.json', /1 card imported/, '3'], ['big.json', /3000 cards imported/, '3003']]) {
      await page.setInputFiles('#fc-import', join(dir, name)); await wait(800);
      const msg = await page.locator('#fc-error').textContent(), c = await page.locator('#fc-count').textContent();
      if (!re.test(msg) || c !== count) res.push(`${name}: "${msg}" deck ${c}`);
    }
    const xss = await page.evaluate(() => [document.querySelector('#fc-list li')?.innerHTML.includes('&lt;img') ?? false, window.__xss ?? 0]);
    check(!res.length && xss[0] && !xss[1] && !errs.length, `import: empty, text, mixed, duplicate, BOM, 3,000 cards; HTML shown as text${res.length ? ' FAILED ' + res.join(' | ') : ''}${errs[0] ? ' ERR ' + errs[0] : ''}`);
    await close();
  }

  // Focus timer: reload mid-block, block ended while closed.
  if (run('timer')) {
    const shift = () => { const Real = Date, s = () => Number(sessionStorage.getItem('shift') || 0); class F extends Real { constructor(...a) { if (a.length === 0) super(Real.now() + s()); else super(...a); } static now() { return Real.now() + s(); } } window.Date = F; };
    const { page, errs, close } = await open('/tools/focus-timer/', { init: shift });
    await page.click('#start'); await wait(300);
    await page.evaluate(() => sessionStorage.setItem('shift', String(5 * 60000))); await page.reload({ waitUntil: 'networkidle' }); await wait(400);
    const mid = [await page.locator('#time').textContent(), await page.locator('#start').textContent()];
    await page.evaluate(() => sessionStorage.setItem('shift', String(31 * 60000))); await page.reload({ waitUntil: 'networkidle' }); await wait(400);
    const k = 'ffl-timer-' + dateIn(0);
    const done1 = await page.evaluate((key) => localStorage.getItem(key), k);
    await page.reload({ waitUntil: 'networkidle' }); const done2 = await page.evaluate((key) => localStorage.getItem(key), k);
    check(/^(19|20):\d\d$/.test(mid[0]) && mid[1] === 'Pause' && done1 === '1' && done2 === '1' && !errs.length, `timer: reload mid-block carries on (${mid}), block ended while closed counted once (${done1}/${done2})`);
    await close();
  }

  // Signup: bad emails refused with nothing sent; a good one sent once.
  if (run('signup')) for (const path of ['/', '/study-plan/gre/']) {
    const { page, errs, close } = await open(path); const sent = [];
    page.on('request', (r) => { if (r.url().includes('mailerlite.com')) sent.push(r.postData() || ''); });
    const msgs = [];
    for (const [v, paste] of [[''], ['abc'], ['a@b'], ['  x @y.com', true]]) { await typeInto(page, '#kit-email', v, paste); await page.keyboard.press('Enter'); await wait(150); msgs.push(await page.locator('#kit-status').textContent()); }
    const none = sent.length;
    await typeInto(page, '#kit-email', '  test+ui@example.com ', true); await page.locator('#kit-form button[type=submit]').dblclick(); await wait(600);
    const ok = await page.locator('#kit-status').textContent();
    check(none === 0 && msgs.every((m) => /valid email/.test(m)) && sent.length === 1 && /Check your inbox/.test(ok) && !errs.length, `signup ${path}: 4 bad emails refused (${none} sent), good email double-clicked sent ${sent.length}x${/Check your inbox/.test(ok) ? '' : ' MSG "' + ok.slice(0, 70) + '"'}${msgs.every((m) => /valid email/.test(m)) ? '' : ' BAD-MSGS ' + JSON.stringify(msgs)}${errs[0] ? ' ERR ' + errs[0] : ''}`);
    await close();
  }

  // Phone width with touch: menus, theme toggle, a form by tapping.
  if (run('mobile')) {
    const { page, errs, close } = await open('/', { touch: true, width: 375 });
    const vis = (id) => page.locator('#' + id).isVisible();
    const r = [];
    for (const id of ['menu-plans', 'menu-tools', 'menu-guides', 'menu-planners']) {
      await page.locator(`[aria-controls="${id}"]`).tap(); await wait(200); const o = await vis(id);
      await page.keyboard.press('Escape'); await wait(150); r.push(o && !(await vis(id)));
    }
    const th0 = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    await page.locator('.theme-toggle').tap(); await wait(100);
    const th1 = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    await page.goto(BASE + '/tools/test-time-calculator/', { waitUntil: 'networkidle' });
    await page.locator('#totalMin').tap(); await typeInto(page, '#totalMin', '90'); await page.locator('#questions').tap(); await typeInto(page, '#questions', '60');
    await page.locator('main form button[type=submit]').tap(); await wait(250);
    const g = await look(page);
    check(r.every(Boolean) && th1 && th1 !== th0 && g.result && !g.error && !errs.length, `mobile 375 touch: menus ${r}, theme ${th0}→${th1}, form by tapping ${g.error || 'ok'}`);
    await close();
  }

  // Storage blocked: tools work, loggers say entries are not saved.
  if (run('storage')) {
    const BLOCK = () => { try { Object.defineProperty(window, 'localStorage', { configurable: true, get() { throw new DOMException('blocked', 'SecurityError'); } }); } catch {} };
    const res = [];
    for (const [path, fill, logger] of [['/tools/practice-score-tracker/', [['#sc-right', '7'], ['#sc-total', '10']], true], ['/tools/error-log/', [['#el-what', 'Beta']], true], ['/tools/test-time-calculator/', [['#totalMin', '90'], ['#questions', '60']], false], ['/tools/gpa-calculator/', [], false], ['/', [], false]]) {
      const { page, errs, close } = await open(path, { storage: BLOCK });
      for (const [s, v] of fill) await typeInto(page, s, v);
      if (fill.length) await press(page);
      const g = await look(page), note = await page.locator('#ff-store-note').count();
      if (errs.length || g.bad || (logger && !note) || (fill.length && !logger && !g.result)) res.push(`${path}: ${errs[0] || g.bad || (logger && !note ? 'no notice' : 'no result')}`);
      await close();
    }
    check(!res.length, `storage blocked: 5 pages work, loggers show the notice${res.length ? ' FAILED ' + res.join(' | ') : ''}`);
  }

  // Layout: every sitemap page at 375/768/1280: no sideways scroll, no script errors.
  if (run('layout')) {
    const xml = await (await fetch(BASE + '/sitemap.xml')).text();
    const urls = [...xml.matchAll(/<loc>https:\/\/thefocusflowlab\.com([^<]*)<\/loc>/g)].map((m) => m[1]);
    for (const width of [375, 768, 1280]) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 } });
      await ctx.route(/cloudflareinsights|youtube|ytimg/, (r) => r.fulfill({ status: 204, body: '' }));
      const page = await ctx.newPage(); const bad = [];
      for (const u of urls) {
        const errs = []; const on = (e) => errs.push(e.message); page.on('pageerror', on);
        await page.goto(BASE + u, { waitUntil: 'load' }).catch((e) => errs.push(e.message)); await wait(150);
        const over = await page.evaluate(() => {
          const w = document.documentElement.clientWidth; const wide = [...document.querySelectorAll('main *, header *')].filter((e) => { const r = e.getBoundingClientRect(); return r.width && r.right > w + 1 && getComputedStyle(e).position !== 'fixed' && !e.closest('[hidden], .table-wrap, .scroll, pre, table, .mega, .nav-panel'); }).slice(0, 2).map((e) => e.tagName + '.' + (e.className || '').toString().split(' ')[0]);
          return { scroll: document.documentElement.scrollWidth - w, wide };
        });
        page.off('pageerror', on);
        if (over.scroll > 0 || errs.length) bad.push(`${u} (+${over.scroll}px ${over.wide.join(',')}${errs[0] ? ' ERR ' + errs[0] : ''})`);
      }
      check(!bad.length, `layout ${width}px: ${urls.length} pages, no sideways scroll or script error${bad.length ? ' FAILED ' + bad.slice(0, 8).join(' | ') : ''}`);
      await ctx.close();
    }
  }
  await browser.close();
}

console.log('\n' + Object.entries(tally).map(([e, t]) => `${e}: ${t.pass} pass, ${t.fail} fail`).join('\n'));
console.log(failed ? `${failed} FAILED` : 'ALL PASSED');
process.exit(failed ? 1 : 0);
