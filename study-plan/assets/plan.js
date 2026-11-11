/*
 * FocusFlow Lab study plan generator.
 * Each exam page sets window.EXAM_CONFIG before this file loads.
 * Everything runs in the browser; nothing is sent anywhere.
 */
(function () {
  'use strict';

  const config = window.EXAM_CONFIG;
  const storageKey = 'ffl-plan-' + config.id;
  const MS_PER_DAY = 24 * 60 * 60 * 1000;
  const TOPICS_SHOWN = 4;
  // Calendar-day arithmetic. Adding n x 24 h lands on 11 pm the day before after the autumn clock change.
  const addDays = (date, n) => new Date(date.getFullYear(), date.getMonth(), date.getDate() + n);

  const form = document.getElementById('plan-form');
  const output = document.getElementById('plan');
  const errorBox = document.getElementById('form-error');

  const PHASES = {
    review: { label: 'Content review', color: 'var(--color-phase-review)' },
    practice: { label: 'Practice and review', color: 'var(--color-phase-practice)' },
    final: { label: 'Final week', color: 'var(--color-phase-final)' },
  };

  /** Build the weak-area checkboxes from the exam's topic list. */
  function renderTopicChoices() {
    document.getElementById('weak-areas').innerHTML = config.topics
      .map((topic, index) =>
        `<label class="topic"><input type="checkbox" name="weak" value="${index}">${topic.name}</label>`)
      .join('');
  }

  /** Read the form into a plain object. */
  function readInputs() {
    return {
      examDate: form.examDate.value,
      hoursPerDay: parseFloat(form.hoursPerDay.value),
      daysPerWeek: parseInt(form.daysPerWeek.value, 10),
      weak: [...form.querySelectorAll('input[name="weak"]:checked')].map((box) => parseInt(box.value, 10)),
    };
  }

  /** Put saved inputs back into the form. */
  function fillInputs(saved) {
    form.examDate.value = saved.examDate || '';
    if (saved.hoursPerDay) form.hoursPerDay.value = saved.hoursPerDay;
    if (saved.daysPerWeek) form.daysPerWeek.value = saved.daysPerWeek;
    (saved.weak || []).forEach((index) => {
      const box = form.querySelector(`input[name="weak"][value="${index}"]`);
      if (box) box.checked = true;
    });
  }

  /** Return a friendly error message, or '' when the inputs are fine. */
  function validate(inputs, daysLeft) {
    if (!inputs.examDate) return 'Pick your exam date first.';
    if (!(daysLeft >= 3)) return "Your exam is less than 3 days away. Rest, skim your notes, and trust the work you've done.";
    if (daysLeft > config.maxDays) return `That's more than ${Math.round(config.maxDays / 30)} months away. Come back nearer the date for a tighter plan.`;
    if (!(inputs.hoursPerDay >= 0.5 && inputs.hoursPerDay <= 14)) return 'Hours per day should be somewhere between 0.5 and 14.';
    if (!(inputs.daysPerWeek >= 1 && inputs.daysPerWeek <= 7)) return 'Pick how many days a week you can study.';
    return '';
  }

  /** Split hours across topics by exam weight, giving weak areas 50% more. Half-hour blocks shared by largest
   *  remainder, so the topic hours always add up to the week's hours as shown (rounding each topic alone did not). */
  function splitTopicHours(hours, weak) {
    const weights = config.topics.map((topic, index) => topic.weight * (weak.includes(index) ? 1.5 : 1));
    const total = weights.reduce((sum, weight) => sum + weight, 0);
    const blocks = Math.round(hours * 2);
    const raw = weights.map((w) => (blocks * w) / total);
    const counts = raw.map(Math.floor);
    let spare = blocks - counts.reduce((a, b) => a + b, 0);
    raw.map((v, i) => [v - counts[i], weights[i], i]).sort((a, b) => b[0] - a[0] || b[1] - a[1]).forEach(([, , i]) => { if (spare > 0) { counts[i]++; spare--; } });
    return config.topics
      .map((topic, index) => ({ name: topic.name, hours: counts[index] / 2 }))
      .sort((a, b) => b.hours - a.hours);
  }

  /** Pick the phase for a week from how far through the plan it is. */
  function phaseForWeek(weekIndex, totalWeeks) {
    if (weekIndex === totalWeeks - 1) return 'final';
    return (weekIndex + 1) / totalWeeks <= config.reviewShare ? 'review' : 'practice';
  }

  /** Build the whole plan as data. */
  function buildPlan(inputs) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const exam = new Date(inputs.examDate + 'T00:00:00');
    const daysLeft = Math.round((exam - today) / MS_PER_DAY);
    const message = validate(inputs, daysLeft);
    if (message) return { error: message };

    const totalWeeks = Math.max(1, Math.ceil(daysLeft / 7));
    const weeks = [];
    let totalHours = 0;

    for (let weekIndex = 0; weekIndex < totalWeeks; weekIndex++) {
      const start = addDays(today, weekIndex * 7);
      const daysInWeek = Math.min(7, daysLeft - weekIndex * 7);
      const studyDays = Math.max(1, Math.round((daysInWeek * inputs.daysPerWeek) / 7));
      const phase = totalWeeks === 1 ? 'final' : phaseForWeek(weekIndex, totalWeeks);
      // The final week eases off so you walk in rested.
      const hours = studyDays * inputs.hoursPerDay * (phase === 'final' ? 0.6 : 1);
      totalHours += hours;
      weeks.push({
        number: weekIndex + 1,
        start,
        phase,
        hours,
        studyDays,
        daysInWeek,
        topics: splitTopicHours(hours, inputs.weak),
        tasks: config.tasks[phase](studyDays, weekIndex, totalWeeks),
      });
    }

    return { daysLeft, totalWeeks, totalHours, weeks, exam, inputs };
  }

  /** Daily pages for the first week: your dates, your topics, four focus blocks with a self-test. Printed from a hidden block. */
  function buildDailyPages(plan, noCover) {
    const week = plan.weeks[0];
    const n = week.studyDays;
    const slots = n * 4;
    // Share the block slots between topics by hours (largest remainder), then deal them out round-robin so a day mixes topics.
    const total = week.topics.reduce((s, t) => s + t.hours, 0) || 1;
    const raw = week.topics.map((t) => (t.hours / total) * slots);
    const counts = raw.map(Math.floor);
    let spare = slots - counts.reduce((a, b) => a + b, 0);
    raw.map((v, i) => [v - Math.floor(v), i]).sort((a, b) => b[0] - a[0]).forEach(([, i]) => { if (spare > 0) { counts[i]++; spare--; } });
    const queue = [];
    while (queue.length < slots) {
      let added = false;
      counts.forEach((c, i) => { if (c > 0 && queue.length < slots) { queue.push(week.topics[i].name); counts[i]--; added = true; } });
      if (!added) break;
    }
    const minutes = Math.max(15, Math.round((plan.inputs.hoursPerDay * 60) / 4 / 5) * 5);
    const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const fmtLong = (d) => d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    const top = week.topics.slice(0, 5);
    const cover = `<section class="day-page">
        <p class="dp-kicker">My ${esc(config.shortName)} plan</p>
        <h2>${esc(config.shortName)} on ${esc(plan.exam.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }))}</h2>
        <p class="dp-lead">${plan.daysLeft} days to go. ${plan.inputs.hoursPerDay} hours a day, ${plan.inputs.daysPerWeek} days a week, about ${Math.round(plan.totalHours)} hours in total.</p>
        <h3>Where week 1 goes</h3>
        <ul class="dp-list">${top.map((t) => `<li><span>${esc(t.name)}</span><strong>${roundHalf(t.hours)} h</strong></li>`).join('')}</ul>
        <h3>How each day works</h3>
        <ol class="dp-steps"><li>Four focus blocks of about ${minutes} minutes, phone in another room.</li><li>After each block, close your notes and write what you remember. Tick the self-test.</li><li>Write every miss in the error log at the bottom of the page.</li><li>Tomorrow, start with five minutes of recall from today.</li></ol>
        <p class="dp-foot">Made with the free plan generator at thefocusflowlab.com. The full ${plan.totalWeeks}-week schedule is in your plan on screen. Want every week on paper, with an exam map and a test log? See the printable planners at thefocusflowlab.com/planners.</p>
      </section>`;
    const days = [];
    for (let i = 0; i < n; i++) {
      const day = addDays(week.start, Math.floor((i * week.daysInWeek) / n));
      const blocks = [0, 1, 2, 3].map((b) => `<li><span class="dp-n">${b + 1}</span><div><strong>${esc(queue[i * 4 + b] || week.topics[0].name)}</strong><span class="dp-sub">${minutes} minutes</span></div><span class="dp-box" aria-hidden="true"></span><span class="dp-lbl">Self-test done</span></li>`).join('');
      days.push(`<section class="day-page">
        <p class="dp-kicker">${esc(config.shortName)} · day ${i + 1} of ${n} this week · ${Math.max(0, Math.round((plan.exam - day) / MS_PER_DAY))} days to the exam</p>
        <h2>${esc(fmtLong(day))}</h2>
        <ol class="dp-blocks">${blocks}</ol>
        <h3>What I remember from block 4, without notes</h3>
        <div class="dp-lines"><i></i><i></i><i></i><i></i></div>
        <h3>Error log: what I missed, and why</h3>
        <div class="dp-lines"><i></i><i></i><i></i></div>
        <p class="dp-foot">Start tomorrow with five minutes of recall from today. Plan from thefocusflowlab.com</p>
      </section>`);
    }
    return (noCover ? '' : cover) + days.join('');
  }

  /** The whole plan as printable pages: cover, overview, a page per week, the first week day by day, error logs and a checklist. */
  function buildFullPack(plan) {
    const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const long = (d) => d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    const short = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const blank = (n) => Array.from({ length: n }, () => '<i></i>').join('');
    const cover = `<section class="day-page pack-cover">
        <p class="dp-kicker">My ${esc(config.shortName)} plan</p>
        <h2>${esc(config.shortName)}<br>${plan.totalWeeks}-week plan</h2>
        <p class="dp-lead">Exam day: ${esc(long(plan.exam))}. ${plan.daysLeft} days to go.</p>
        <ul class="dp-list">
          <li><span>Study time</span><strong>${plan.inputs.hoursPerDay} hours a day, ${plan.inputs.daysPerWeek} days a week</strong></li>
          <li><span>Hours planned</span><strong>about ${Math.round(plan.totalHours)}</strong></li>
          <li><span>Starts</span><strong>${esc(long(plan.weeks[0].start))}</strong></li>
        </ul>
        <div class="dp-fields"><div><span>Name</span><i></i></div><div><span>Target score or result</span><i></i></div></div>
        <h3>What is inside</h3>
        <ol class="dp-steps"><li>The plan at a glance, week by week.</li><li>One page for each week: tasks, hours per topic, days studied and a practice score.</li><li>Your first week, day by day, with four focus blocks and a self-test after each.</li><li>Error log pages and a final-week checklist.</li></ol>
        <p class="dp-foot">Made with the free plan generator at thefocusflowlab.com. ${esc(config.shortName)} topic shares are rough planning figures, not official numbers.</p>
      </section>`;
    const rows = plan.weeks.map((w) => `<tr><td>${w.number}</td><td>${esc(short(w.start))}</td><td>${esc(PHASES[w.phase].label)}</td><td>${roundHalf(w.hours)} h</td><td>${esc(w.topics.slice(0, 2).map((t) => t.name).join(', '))}</td><td class="c"><span class="dp-box"></span></td></tr>`).join('');
    const overview = `<section class="day-page">
        <p class="dp-kicker">${esc(config.shortName)} plan</p>
        <h2>The plan at a glance</h2>
        <table class="dp-table"><thead><tr><th>Wk</th><th>From</th><th>Phase</th><th>Hours</th><th>Most time on</th><th class="c">Done</th></tr></thead><tbody>${rows}</tbody></table>
        <p class="dp-foot">Content review first, practice and review in the middle, an easier final week so you arrive rested.</p>
      </section>`;
    const compact = plan.totalWeeks > 16;
    const weekHtml = (w) => `<div class="wk${compact ? ' wk-compact' : ''}">
        <p class="dp-kicker">Week ${w.number} of ${plan.totalWeeks} · from ${esc(long(w.start))} · ${esc(PHASES[w.phase].label)} · ${roundHalf(w.hours)} hours</p>
        <h3>This week</h3>
        <ul class="dp-checks">${w.tasks.map((t) => `<li><span class="dp-box"></span><span>${esc(t)}</span></li>`).join('')}</ul>
        <h3>Where the hours go</h3>
        <ul class="dp-list">${w.topics.slice(0, compact ? 4 : 6).map((t) => `<li><span>${esc(t.name)}</span><strong>${roundHalf(t.hours)} h</strong></li>`).join('')}</ul>
        <div class="dp-days">${['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((d) => `<div><b>${d}</b><span class="dp-box"></span></div>`).join('')}</div>
        <div class="dp-fields"><div><span>Practice score this week</span><i></i></div><div><span>Biggest gap</span><i></i></div></div>
        ${compact ? '' : '<h3>Notes</h3><div class="dp-lines">' + blank(4) + '</div>'}
      </div>`;
    let weeks = '';
    if (compact) {
      for (let i = 0; i < plan.weeks.length; i += 2) weeks += `<section class="day-page">${weekHtml(plan.weeks[i])}${plan.weeks[i + 1] ? weekHtml(plan.weeks[i + 1]) : ''}</section>`;
    } else {
      weeks = plan.weeks.map((w) => `<section class="day-page">${weekHtml(w)}</section>`).join('');
    }
    const errRows = Array.from({ length: 14 }, () => '<tr><td></td><td></td><td></td></tr>').join('');
    const errLog = (k) => `<section class="day-page">
        <p class="dp-kicker">${esc(config.shortName)} plan</p>
        <h2>Error log ${k} of 2</h2>
        <p class="dp-lead">Write the concept, not the question. Was it a gap, a misread, a slip or timing? Review this log instead of re-reading notes.</p>
        <table class="dp-table dp-err"><thead><tr><th>Concept I missed</th><th>Why</th><th>What I will do</th></tr></thead><tbody>${errRows}</tbody></table>
      </section>`;
    const checklist = ['Take your last full practice test early in the week', 'Review your error log, not new content', 'Do a short mixed question set each day', 'Confirm your test date, location and what to bring', 'Prepare your ID and anything the test centre requires', 'No new content in the last two days', 'Light review only the day before, then rest', 'Sleep at your normal time the night before', 'Arrive early and settle in'];
    const finalPage = `<section class="day-page">
        <p class="dp-kicker">${esc(config.shortName)} plan</p>
        <h2>Final-week checklist</h2>
        <ul class="dp-checks big">${checklist.map((t) => `<li><span class="dp-box"></span><span>${esc(t)}</span></li>`).join('')}</ul>
        <p class="dp-foot">You have done the work. Good luck. Plan from thefocusflowlab.com</p>
      </section>`;
    return cover + overview + weeks + buildDailyPages(plan, true) + errLog(1) + errLog(2) + finalPage;
  }

  function printPack(html) {
    let root = document.getElementById('daily-print');
    if (!root) { root = document.createElement('div'); root.id = 'daily-print'; root.className = 'daily-print'; document.body.appendChild(root); }
    root.innerHTML = html;
    document.body.classList.add('print-days');
    const done = () => { document.body.classList.remove('print-days'); window.removeEventListener('afterprint', done); };
    window.addEventListener('afterprint', done);
    window.print();
  }

  function printDailyPages(plan) { printPack(buildDailyPages(plan)); }
  function printFullPack(plan) { printPack(buildFullPack(plan)); }

  /** One calendar event per study session (no repeats), so any session can be moved or deleted. Times are local ("floating"). */
  function buildIcs(plan) {
    const pad = (n) => String(n).padStart(2, '0');
    const ymd = (d) => d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate());
    const stamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z';
    const esc = (t) => String(t).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//FocusFlow Lab//Study plan//EN', 'CALSCALE:GREGORIAN', 'X-WR-CALNAME:' + esc(config.shortName + ' study plan')];
    let uid = 0;
    const add = (ev) => { lines.push('BEGIN:VEVENT', 'UID:ffl-' + stamp + '-' + (uid++) + '@thefocusflowlab.com', 'DTSTAMP:' + stamp, ...ev, 'END:VEVENT'); };
    plan.weeks.forEach((week) => {
      const perDay = week.hours / week.studyDays;
      const top = week.topics.slice(0, 2).map((t) => t.name).join(' and ');
      const desc = 'Week ' + week.number + ', ' + PHASES[week.phase].label + '. Most time this week: ' + top + '. ' + week.tasks.join(' ') + ' Free plan from thefocusflowlab.com';
      for (let i = 0; i < week.studyDays; i++) {
        const day = addDays(week.start, Math.floor((i * week.daysInWeek) / week.studyDays));
        // Start at 6 PM; a long day ends at midnight instead, so the event starts earlier rather than running past midnight.
        const length = Math.max(15, Math.round(perDay * 60));
        const endMin = Math.min(18 * 60 + length, 24 * 60);
        const startMin = endMin - length;
        // new Date() rolls minutes past 1440 into the next day, so an end of exactly midnight gets tomorrow's date.
        const at = (m) => { const t = new Date(day.getFullYear(), day.getMonth(), day.getDate(), 0, m); return ymd(t) + 'T' + pad(t.getHours()) + pad(t.getMinutes()) + '00'; };
        add(['DTSTART:' + at(startMin), 'DTEND:' + at(endMin), 'SUMMARY:' + esc(config.shortName + ': ' + top), 'DESCRIPTION:' + esc(desc)]);
      }
    });
    const next = addDays(plan.exam, 1);
    add(['DTSTART;VALUE=DATE:' + ymd(plan.exam), 'DTEND;VALUE=DATE:' + ymd(next), 'SUMMARY:' + esc(config.shortName + ' exam day'), 'DESCRIPTION:' + esc('Good luck. Plan made with thefocusflowlab.com')]);
    lines.push('END:VCALENDAR');
    // Fold long lines (RFC 5545): continuation lines start with a space. 60 characters keeps multi-byte text under 75 bytes.
    const fold = (l) => { const out = []; for (let i = 0; i < l.length; i += 60) out.push((i ? ' ' : '') + l.slice(i, i + 60)); return out.join('\r\n'); };
    return lines.map(fold).join('\r\n') + '\r\n';
  }

  function downloadIcs(plan) {
    const blob = new Blob([buildIcs(plan)], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = config.shortName.toLowerCase().replace(/[^a-z0-9]+/g, '-') + '-study-plan.ics';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const formatDate = (date) => date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const roundHalf = (value) => Math.round(value * 2) / 2;

  /** The small per-topic bar chart for one week. */
  function renderAllocation(week) {
    const shown = week.topics.slice(0, TOPICS_SHOWN);
    const largest = shown[0].hours || 1;
    const rest = week.topics.slice(TOPICS_SHOWN).reduce((sum, topic) => sum + topic.hours, 0);
    const rows = shown.map((topic) => `
      <div class="alloc-row"><dt>${topic.name}</dt><dd>${roundHalf(topic.hours)} h</dd>
        <div class="bar" aria-hidden="true"><i style="width:${Math.round((topic.hours / largest) * 100)}%"></i></div></div>`).join('');
    const restRow = rest > 0 ? `<div class="alloc-row"><dt>Everything else</dt><dd>${roundHalf(rest)} h</dd></div>` : '';
    return `<dl class="alloc" aria-label="Topic hours for week ${week.number}">${rows}${restRow}</dl>`;
  }

  /** Turn plan data into the timetable. */
  function renderPlan(plan) {
    const recommended = config.recommendedHours;
    const hoursPlanned = Math.round(plan.totalHours);
    const warning = hoursPlanned < recommended.min
      ? `<p class="warning">Most people put in around ${recommended.min} to ${recommended.max} hours for the ${config.shortName}. This plan has ${hoursPlanned}. If you can, add time per day or move your date back.</p>`
      : '';
    const legend = Object.values(PHASES)
      .map((phase) => `<li><span class="swatch" style="background:${phase.color}"></span>${phase.label}</li>`).join('');

    const weeks = plan.weeks.map((week) => `
      <article class="week" data-phase="${week.phase}">
        <div class="week-when"><strong>Week ${week.number}</strong><span>from ${formatDate(week.start)}</span><span>${roundHalf(week.hours)} hours</span></div>
        <div>
          <h3 class="week-phase">${PHASES[week.phase].label}</h3>
          <ul>${week.tasks.map((task) => `<li>${task}</li>`).join('')}</ul>
        </div>
        ${renderAllocation(week)}
      </article>`).join('');

    output.innerHTML = `
      <div class="plan-head">
        <h2>Your ${config.shortName} plan</h2>
        <dl class="totals">
          <div><dt>Days left</dt><dd>${plan.daysLeft}</dd></div>
          <div><dt>Weeks</dt><dd>${plan.totalWeeks}</dd></div>
          <div><dt>Hours planned</dt><dd>${hoursPlanned}</dd></div>
        </dl>
      </div>
      <ul class="legend">${legend}</ul>
      ${warning}
      ${weeks}
      <div class="plan-actions">
        <button class="btn" type="button" id="print-plan">Print or save as PDF</button>
        <button class="btn btn-soft" type="button" id="print-pack">Print my full plan pack</button>
        <button class="btn btn-soft" type="button" id="print-days">Print my first week, day by day</button>
        <button class="btn btn-soft" type="button" id="add-cal">Add to my calendar (.ics)</button>
        <a class="btn btn-quiet" href="#plan-form">Change my answers</a>
      </div>
      <p class="muted cal-note">The calendar file has one event per study session, starting at 6 pm (earlier on very long days, so it ends by midnight), and your exam day. Move any session after you import it into Google Calendar, Apple Calendar or Outlook.</p>`;
    document.getElementById('print-plan').addEventListener('click', () => window.print());
    document.getElementById('add-cal').addEventListener('click', () => downloadIcs(plan));
    document.getElementById('print-days').addEventListener('click', () => printDailyPages(plan));
    document.getElementById('print-pack').addEventListener('click', () => printFullPack(plan));
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    output.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    const heading = output.querySelector('h2');
    heading.setAttribute('tabindex', '-1');
    heading.focus({ preventScroll: true });
  }

  /** Handle "Build my plan". */
  function onSubmit(event) {
    event.preventDefault();
    const inputs = readInputs();
    const plan = buildPlan(inputs);
    if (plan.error) {
      errorBox.textContent = plan.error;
      output.innerHTML = '';
      return;
    }
    errorBox.textContent = '';
    try { localStorage.setItem(storageKey, JSON.stringify(inputs)); } catch (ignored) { /* private mode */ }
    renderPlan(plan);
  }

  /** If the practice score tracker has scores for this exam, offer to mark the topics below target as shaky. */
  function offerTrackerTopics() {
    try {
      const slug = location.pathname.split('/').filter(Boolean)[1];
      const data = JSON.parse(localStorage.getItem('ffl-scores') || 'null');
      if (!data || !Array.isArray(data.entries)) return;
      const target = Number(data.target) || 75;
      const totals = {};
      data.entries.filter((e) => e.exam === slug).forEach((e) => {
        const t = totals[e.topic] || (totals[e.topic] = { right: 0, total: 0 });
        t.right += e.right; t.total += e.total;
      });
      const weak = [];
      config.topics.forEach((topic, index) => {
        const t = totals[topic.name];
        if (t && t.total >= 10 && (t.right / t.total) * 100 < target) weak.push(index);
      });
      if (!weak.length) return;
      const names = weak.map((i) => config.topics[i].name);
      const note = document.createElement('p');
      note.className = 'tracker-note';
      note.innerHTML = 'Your <a href="/tools/practice-score-tracker/">score tracker</a> shows ' + (weak.length === 1 ? 'one topic' : weak.length + ' topics') + ' below your ' + target + '% target: <strong></strong>. ';
      note.querySelector('strong').textContent = names.join(', ');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-soft';
      btn.textContent = 'Mark them as shaky';
      btn.addEventListener('click', () => {
        weak.forEach((i) => { const box = form.querySelector('input[name="weak"][value="' + i + '"]'); if (box) box.checked = true; });
        btn.textContent = 'Marked';
        btn.disabled = true;
      });
      note.appendChild(btn);
      document.getElementById('weak-areas').insertAdjacentElement('beforebegin', note);
    } catch (ignored) { /* no tracker data */ }
  }

  renderTopicChoices();
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
    if (saved) fillInputs(saved);
  } catch (ignored) { /* storage blocked: start fresh */ }
  offerTrackerTopics();
  form.addEventListener('submit', onSubmit);
})();
