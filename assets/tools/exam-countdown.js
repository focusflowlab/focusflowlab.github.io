// Exam countdown: days and real study hours left.
(() => {
  const $ = (id) => document.getElementById(id);
  const form = $('countdown-form');
  const out = $('countdown-result');
  const key = 'ffl-countdown';

  try {
    const saved = JSON.parse(localStorage.getItem(key) || 'null');
    if (saved) { $('examDate').value = saved.examDate; $('hoursPerDay').value = saved.hoursPerDay; $('daysPerWeek').value = saved.daysPerWeek; }
  } catch {}

  function startOfDay(d) { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; }

  function calc(submitted) {
    const value = ffDate($('examDate').value) ? $('examDate').value : ''; // an impossible date counts as none
    // A blank or impossible date (e.g. 30 Feb, which the box empties) only gets a message when the button is pressed.
    if (!value) { out.hidden = true; $('countdown-error').textContent = submitted === true ? 'Pick your exam date.' : ''; return; }
    const exam = startOfDay(value + 'T00:00:00');
    const today = startOfDay(new Date());
    const days = Math.round((exam - today) / 86400000);
    const err = $('countdown-error');
    if (days < 1) { err.textContent = 'Pick a date after today.'; out.hidden = true; return; }
    // A blank or out-of-range field used to count silently as 0.5 h (or 14 h) a day.
    const H = ffField($('hoursPerDay')), hours = H.v;
    if (hours === null || !H.ok) { err.textContent = 'Enter your study hours per day, between 0.5 and 14.'; out.hidden = true; return; }
    err.textContent = '';
    const perWeek = Number($('daysPerWeek').value);
    const studyDays = Math.round(days * perWeek / 7);
    const total = Math.round(studyDays * hours);
    const weeks = Math.floor(days / 7);

    $('r-days').textContent = days;
    $('r-weeks').textContent = weeks + (days % 7 ? ' and ' + (days % 7) + (days % 7 === 1 ? ' day' : ' days') : '');
    $('r-study').textContent = studyDays;
    $('r-hours').textContent = total;
    const extra = Math.round(studyDays * 1);
    $('r-tip').textContent = 'One more hour a day would add about ' + extra + ' hours before the exam.';
    out.hidden = false;
    try { localStorage.setItem(key, JSON.stringify({ examDate: value, hoursPerDay: $('hoursPerDay').value, daysPerWeek: $('daysPerWeek').value })); } catch {}
  }

  form.addEventListener('submit', (e) => { e.preventDefault(); calc(true); });
  form.addEventListener('change', () => calc());
  calc();
})();
