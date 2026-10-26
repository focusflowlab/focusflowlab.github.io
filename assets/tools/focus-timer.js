// Focus timer: focus blocks with a break and a self-test prompt.
// Timing uses timestamps, so it stays right when the tab sleeps.
(() => {
  const $ = (id) => document.getElementById(id);
  const display = $('time');
  const phaseLabel = $('phase');
  const startBtn = $('start');
  const resetBtn = $('reset');
  const prompt = $('selftest');
  const doneCount = $('done-count');
  const todayKey = 'ffl-timer-' + new Date().toISOString().slice(0, 10);

  let phase = 'focus';      // 'focus' or 'break'
  let endsAt = 0;           // timestamp when the running phase ends
  let remaining = minutes('focus') * 60_000;
  let tick = null;
  const baseTitle = document.title;

  function minutes(which) {
    const el = document.querySelector(`input[name="${which}"]:checked`);
    return Number(el ? el.value : (which === 'focus' ? 25 : 5));
  }
  function fmt(ms) {
    const total = Math.max(0, Math.ceil(ms / 1000));
    const m = Math.floor(total / 60), s = total % 60;
    return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
  }
  function render() {
    display.textContent = fmt(remaining);
    phaseLabel.textContent = phase === 'focus' ? 'Focus block' : 'Break';
    document.title = tick ? fmt(remaining) + ' · ' + baseTitle : baseTitle;
    startBtn.textContent = tick ? 'Pause' : (remaining < minutes(phase) * 60_000 ? 'Resume' : 'Start');
  }
  function readDone() { try { return Number(localStorage.getItem(todayKey) || 0); } catch { return 0; } }
  function writeDone(n) { try { localStorage.setItem(todayKey, String(n)); } catch {} }
  function showDone() { const n = readDone(); doneCount.textContent = n === 1 ? '1 focus block done today' : n + ' focus blocks done today'; }

  function chime() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [0, 0.25].forEach((t) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.frequency.value = 660; o.connect(g); g.connect(ctx.destination);
        g.gain.setValueAtTime(0.0001, ctx.currentTime + t);
        g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + t + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + t + 0.4);
        o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.45);
      });
    } catch {}
  }

  function stop() { clearInterval(tick); tick = null; }
  function run() {
    endsAt = Date.now() + remaining;
    tick = setInterval(() => {
      remaining = endsAt - Date.now();
      if (remaining <= 0) finish();
      render();
    }, 250);
    render();
  }
  function finish() {
    stop();
    if ($('sound').checked) chime();
    if (phase === 'focus') {
      writeDone(readDone() + 1); showDone();
      prompt.hidden = false;
      phase = 'break';
    } else {
      prompt.hidden = true;
      phase = 'focus';
    }
    remaining = minutes(phase) * 60_000;
    render();
  }

  startBtn.addEventListener('click', () => {
    if (tick) { stop(); render(); return; }
    if (phase === 'focus') prompt.hidden = true;
    run();
  });
  resetBtn.addEventListener('click', () => {
    stop(); phase = 'focus'; prompt.hidden = true;
    remaining = minutes('focus') * 60_000; render();
  });
  document.querySelectorAll('input[name="focus"], input[name="break"]').forEach((el) => el.addEventListener('change', () => {
    if (!tick) { remaining = minutes(phase) * 60_000; render(); }
  }));

  showDone();
  render();
})();
