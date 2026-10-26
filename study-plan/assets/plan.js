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

  const form = document.getElementById('plan-form');
  const output = document.getElementById('plan');
  const errorBox = document.getElementById('form-error');

  const PHASES = {
    review: { label: 'Content review', color: 'var(--phase-review)' },
    practice: { label: 'Practice and review', color: 'var(--phase-practice)' },
    final: { label: 'Final week', color: 'var(--phase-final)' },
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
    if (daysLeft < 3) return "Your exam is less than 3 days away. Rest, skim your notes, and trust the work you've done.";
    if (daysLeft > config.maxDays) return `That's more than ${Math.round(config.maxDays / 30)} months away. Come back nearer the date for a tighter plan.`;
    if (!(inputs.hoursPerDay >= 0.5 && inputs.hoursPerDay <= 14)) return 'Hours per day should be somewhere between 0.5 and 14.';
    return '';
  }

  /** Split hours across topics by exam weight, giving weak areas 50% more. */
  function splitTopicHours(hours, weak) {
    const weights = config.topics.map((topic, index) => topic.weight * (weak.includes(index) ? 1.5 : 1));
    const total = weights.reduce((sum, weight) => sum + weight, 0);
    return config.topics
      .map((topic, index) => ({ name: topic.name, hours: (hours * weights[index]) / total }))
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
      const start = new Date(today.getTime() + weekIndex * 7 * MS_PER_DAY);
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
        topics: splitTopicHours(hours, inputs.weak),
        tasks: config.tasks[phase](studyDays, weekIndex, totalWeeks),
      });
    }

    return { daysLeft, totalWeeks, totalHours, weeks };
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
        <a class="btn btn-quiet" href="#plan-form">Change my answers</a>
      </div>`;
    document.getElementById('print-plan').addEventListener('click', () => window.print());
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    output.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
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

  renderTopicChoices();
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
    if (saved) fillInputs(saved);
  } catch (ignored) { /* storage blocked: start fresh */ }
  form.addEventListener('submit', onSubmit);
})();
