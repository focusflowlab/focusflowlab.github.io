// Layout fault scan: every page, three widths, after filling and submitting forms (plans, tools, focus day). Flags clipped inputs, wrapped short labels/buttons, overflow, horizontal scroll, touching blocks, clipped scroll boxes and tiny tap targets.
// elements wider than their container, horizontal scroll, touching blocks and tiny tap targets.
import puppeteer from 'puppeteer-core';
import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join } from 'path';
const root = 'F:/Personal Projects/focusflowlab.github.io';
const pages = [];
const walk = (dir, rel) => { for (const n of readdirSync(dir)) { if (n.startsWith('_') || n.startsWith('.') || n === 'node_modules' || n === 'embed') continue; const p = join(dir, n); if (statSync(p).isDirectory()) walk(p, rel + n + '/'); else if (n === 'index.html') pages.push('/' + rel); else if (n.endsWith('.html') && rel === '') pages.push('/' + n); } };
walk(root, '');
const exe = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const browser = await puppeteer.launch({ executablePath: exe, headless: 'new' });
const out = [];
for (const width of [375, 768, 1280]) {
  for (const path of pages) {
    const p = await browser.newPage();
    await p.setViewport({ width, height: 900 });
    await p.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
    await p.goto('http://localhost:8765' + path, { waitUntil: 'networkidle2', timeout: 30000 }).catch(() => {});
    // fill sample values so clipping of typed values shows up
    await p.evaluate(() => {
      document.querySelectorAll('input[type=date]').forEach((i) => { if (!i.value) i.value = '2026-11-17'; });
      document.querySelectorAll('input[type=number]').forEach((i) => { if (!i.value) i.value = i.placeholder || '100'; });
    });
    await p.evaluate(async () => {
      const plus = (n) => { const d = new Date(Date.now() + n * 864e5); return d.toISOString().slice(0, 10); };
      document.querySelectorAll('main input[type=date]').forEach((i) => { i.value = plus(40); });
      const f = document.getElementById('plan-form') || document.querySelector('main form');
      if (f && !f.classList.contains('kit-form')) { try { f.requestSubmit(); } catch {} }
      const go = document.getElementById('fd-go'); if (go) go.click();
      if (document.getElementById('sc-form')) { const t = document.getElementById('sc-total'); const r = document.getElementById('sc-right'); t.value = 40; r.value = 30; document.getElementById('sc-form').requestSubmit(); }
      if (document.getElementById('el-form')) { document.getElementById('el-what').value = 'Heparin antidote'; document.getElementById('el-form').requestSubmit(); }
      await new Promise((r) => setTimeout(r, 700));
    });
    const issues = await p.evaluate((width) => {
      const res = [];
      const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('[hidden], .kit-trap, .visually-hidden, .skip'); };
      const name = (e) => (e.id ? '#' + e.id : e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/)[0] : '')) + ' "' + (e.textContent || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 30) + '"';
      if (document.documentElement.scrollWidth > innerWidth + 1) res.push(`H-SCROLL page ${document.documentElement.scrollWidth}px`);
      // inputs whose content is clipped
      document.querySelectorAll('input[type=date], input[type=number], select').forEach((e) => {
        if (!vis(e)) return;
        const r = e.getBoundingClientRect();
        if (e.type === 'date' && r.width < 150) res.push(`NARROW-DATE ${name(e)} ${Math.round(r.width)}px`);
        if (e.tagName === 'SELECT') { const t = e.options[e.selectedIndex]?.text || ''; const c = document.createElement('canvas').getContext('2d'); c.font = getComputedStyle(e).font; if (c.measureText(t).width + parseFloat(getComputedStyle(e).paddingLeft) + parseFloat(getComputedStyle(e).paddingRight) + 4 > r.width) res.push(`CLIPPED-SELECT ${name(e)} "${t}" in ${Math.round(r.width)}px`); }
      });
      // short labels / buttons / check labels that wrap
      document.querySelectorAll('label, .btn, button, .card-tag, .nav-trigger, .nav-link, th').forEach((e) => {
        if (!vis(e)) return;
        const txt = (e.textContent || '').trim();
        if (!txt || txt.length > 40) return;
        if (e.tagName === 'TH') return;
        const tops = []; const tw = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); let tn;
        while ((tn = tw.nextNode())) { if (!tn.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(tn); [...rg.getClientRects()].filter((r) => r.width > 1).forEach((r) => { if (!tops.some((t) => Math.abs(t - r.top) < r.height * 0.6)) tops.push(r.top); }); }
        if (tops.length > 1) {
          const words = txt.split(/\s+/).length;
          res.push(`WRAPPED ${name(e)} (${tops.length} lines, ${words} words, box ${Math.round(e.getBoundingClientRect().width)}px)`);
        }
      });
      // children wider than their parent (overflow), excluding scroll containers
      document.querySelectorAll('main *').forEach((e) => {
        if (!vis(e) || e.closest('.table-scroll, pre, .toc, svg')) return;
        const pr = e.parentElement; if (!pr) return;
        const ps = getComputedStyle(pr); if (/auto|scroll|hidden/.test(ps.overflowX)) return;
        const r = e.getBoundingClientRect(), q = pr.getBoundingClientRect();
        if (r.right > q.right + 2 && r.width > 20 && q.width > 0) res.push(`OVERFLOW ${name(e)} sticks out ${Math.round(r.right - q.right)}px`);
      });
      // touching blocks: consecutive block siblings in the same column with no gap
      document.querySelectorAll('main p, main ul, main ol, main div, main section, main form, main table, main .btn, main h2, main h3, main aside, main details, main dl, main figure').forEach((e) => {
        if (!vis(e) || e.closest('svg, .table-scroll, .alloc, .totals, .mega, .cards, .toc')) return;
        const nx = e.nextElementSibling; if (!nx || !vis(nx)) return;
        const se = getComputedStyle(e), sn = getComputedStyle(nx);
        if (se.display.includes('inline') || sn.display.includes('inline') || sn.position === 'absolute' || sn.position === 'fixed') return;
        if (se.display === 'flex' && se.flexDirection === 'row' && e.parentElement && getComputedStyle(e.parentElement).display.includes('flex')) return;
        const px = (v) => parseFloat(v) || 0;
        const solid = (st) => st.backgroundColor !== 'rgba(0, 0, 0, 0)' && st.backgroundColor !== 'transparent';
        if (px(se.paddingBottom) >= 8 || px(sn.paddingTop) >= 8 || px(se.borderBottomWidth) > 0 || px(sn.borderTopWidth) > 0 || solid(se) || solid(sn) || e.tagName === 'DETAILS') return;
        const a = e.getBoundingClientRect(), b = nx.getBoundingClientRect();
        const ov = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        if (ov < Math.min(a.width, b.width) * 0.5) return;
        const gap = b.top - a.bottom;
        if (gap >= 0 && gap < 4 && (nx.textContent || '').trim() && (e.textContent || '').trim()) res.push(`TOUCHING ${name(e)} -> ${name(nx)} gap ${Math.round(gap)}px`);
      });
      document.querySelectorAll('.table-scroll, .mega, .sc-list, pre').forEach((e) => { if (e.classList.contains('mega')) return; if (e.scrollHeight > e.clientHeight + 2 && getComputedStyle(e).overflowY !== 'visible') res.push(`V-CLIPPED ${name(e)} ${e.clientHeight}px of ${e.scrollHeight}px`); });
      // small tap targets on phones
      if (width <= 400) document.querySelectorAll('main button, main .btn, main select, main input:not([type=checkbox]):not([type=radio]):not([type=hidden])').forEach((e) => {
        if (!vis(e)) return; const r = e.getBoundingClientRect(); if (r.height < 36) res.push(`SMALL-TAP ${name(e)} ${Math.round(r.height)}px`);
      });
      return [...new Set(res)];
    }, width);
    if (issues.length) out.push(`\n[${width}] ${path}\n  ` + issues.slice(0, 12).join('\n  '));
    await p.close();
  }
}
await browser.close();
console.log(pages.length + ' pages scanned at 375/768/1280' + (out.length ? out.join('') : '\nNO ISSUES'));
