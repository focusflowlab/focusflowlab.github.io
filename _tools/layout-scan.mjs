// Layout fault scan: every page, three widths. Flags clipped inputs, wrapped short labels/buttons,
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
      // touching blocks: consecutive block siblings with no gap (text/button groups)
      document.querySelectorAll('main p, main ul, main ol, main .sheet-actions, main .fields, main form, main table, main .btn').forEach((e) => {
        if (!vis(e)) return;
        const nx = e.nextElementSibling; if (!nx || !vis(nx)) return;
        if (getComputedStyle(nx).display.includes('inline') || getComputedStyle(e).display.includes('inline')) return;
        const gap = nx.getBoundingClientRect().top - e.getBoundingClientRect().bottom;
        if (gap >= 0 && gap < 4 && (nx.textContent || '').trim()) res.push(`TOUCHING ${name(e)} -> ${name(nx)} gap ${Math.round(gap)}px`);
      });
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
