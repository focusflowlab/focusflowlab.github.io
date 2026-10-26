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

  function calc() {
    const value = $('examDate').value;
    if (!value) { out.hidden = true; return; }
    const exam = startOfDay(value + 'T00:00:00');
    const today = startOfDay(new Date());
    const days = Math.round((exam - today) / 86400000);
    const err = $('countdown-error');
    if (days < 1) { err.textContent = 'Pick a date after today.'; out.hidden = true; return; }
    err.textContent = '';
    const hours = Math.min(14, Math.max(0.5, Number($('hoursPerDay').value) || 0));
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

  form.addEventListener('submit', (e) => { e.preventDefault(); calc(); });
  form.addEventListener('change', calc);
  calc();
})();
