// Shared number-box reader for every tool. The forms are novalidate (so the browser shows our messages, not its own),
// which also means the browser never enforces min/max/step. This applies the box's own limits:
//   ffField(el) -> { v, ok }   v: the number, null when the box is blank, NaN when it holds text that is not a number
//                              ok: false when the value is outside min/max, or not whole in a box with step 1 or more
// Number(), not parseInt/parseFloat: those read "1e3" as 1 and "12abc" as 12.
window.ffField = (el) => {
  const raw = el.value.trim();
  // Text the browser could not read as a number ("12abc" in Firefox, "1e" in Chrome) reads as "" but is not blank.
  if (raw === '' && el.validity && el.validity.badInput) return { v: NaN, ok: false };
  if (raw === '') return { v: null, ok: true };
  const v = Number(raw);
  const min = el.min === '' ? -Infinity : Number(el.min), max = el.max === '' ? Infinity : Number(el.max);
  const whole = el.step !== '' && el.step !== 'any' && Number(el.step) >= 1;
  return { v, ok: Number.isFinite(v) && v >= min && v <= max && (!whole || Number.isInteger(v)) };
};
// A real calendar date "YYYY-MM-DD"? Date boxes that are plain text (older Safari) can hold "2029-02-30" or "soon".
window.ffDate = (s) => {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '');
  if (!m) return false;
  const d = new Date(+m[1], m[2] - 1, +m[3]);
  return d.getFullYear() === +m[1] && d.getMonth() === m[2] - 1 && d.getDate() === +m[3];
};
// Save to this browser. When storage is blocked or full (private windows, strict settings), say so once on the page
// instead of losing entries silently. Returns true when saved.
window.ffSave = (key, value) => {
  try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch {
    if (!document.getElementById('ff-store-note')) {
      const p = document.createElement('p');
      p.id = 'ff-store-note'; p.className = 'error'; p.setAttribute('role', 'status');
      p.textContent = 'This browser isn’t saving your entries (private window, or storage blocked or full). They stay until you close this page, so download them first if you need them.';
      (document.querySelector('main form') || document.querySelector('main')).before(p);
    }
    return false;
  }
};
// "1 to 1,000" style text for messages, from the same attributes.
window.ffRange = (el) => (el.min !== '' ? Number(el.min).toLocaleString('en-US') : '0') + ' to ' + (el.max !== '' ? Number(el.max).toLocaleString('en-US') : 'any');
