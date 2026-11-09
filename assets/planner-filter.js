// Planner hub: filter cards by area chip and by typed exam name.
(function () {
  var q = document.getElementById('planner-q'), grid = document.getElementById('pc-grid');
  if (!q || !grid) return;
  var cards = [].slice.call(grid.children), chips = [].slice.call(document.querySelectorAll('.chip'));
  var count = document.getElementById('finder-count'), empty = document.getElementById('finder-empty'), group = '';
  function run() {
    var t = q.value.trim().toLowerCase(), n = 0;
    cards.forEach(function (c) {
      var ok = (!group || c.dataset.group === group) && (!t || c.dataset.name.indexOf(t) > -1);
      c.hidden = !ok; if (ok) n++;
    });
    empty.hidden = n > 0;
    count.textContent = (group || t) ? n + (n === 1 ? ' planner' : ' planners') : '';
  }
  q.addEventListener('input', run);
  chips.forEach(function (b) {
    b.addEventListener('click', function () {
      group = b.dataset.filter;
      chips.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      run();
    });
  });
})();
