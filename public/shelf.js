(function () {
  var list = document.getElementById('shelf');
  if (!list) return;
  var items = [].slice.call(list.children);
  var chips = [].slice.call(document.querySelectorAll('.chip'));
  var q = document.getElementById('shelf-q');
  var count = document.getElementById('shelf-count');
  var genre = 'all';
  function apply() {
    var term = q.value.trim().toLowerCase(), shown = 0;
    items.forEach(function (li) {
      var ok = (genre === 'all' || li.dataset.genre === genre) &&
        (!term || li.textContent.toLowerCase().indexOf(term) !== -1);
      li.hidden = !ok;
      if (ok) shown++;
    });
    count.textContent = shown === items.length ? '' :
      shown === 0 ? 'Nothing on the shelf matches that. Try another title or author.' :
      'Showing ' + shown + ' of ' + items.length + ' series.';
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      genre = c.dataset.filter;
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
      apply();
    });
  });
  q.addEventListener('input', apply);
})();
