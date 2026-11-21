(function () {
  var list = document.getElementById('poll'), status = document.getElementById('poll-status');
  if (!list) return;
  var buttons = [].slice.call(list.querySelectorAll('.opt'));
  var voter, mine;
  try {
    voter = localStorage.getItem('llc-voter');
    if (!voter) { voter = crypto.randomUUID(); localStorage.setItem('llc-voter', voter); }
    mine = localStorage.getItem('llc-vote-next-up-1');
  } catch (e) { voter = crypto.randomUUID ? crypto.randomUUID() : null; }

  function render(counts) {
    var total = 0, k;
    for (k in counts) total += counts[k];
    buttons.forEach(function (b) {
      var n = counts[b.dataset.choice] || 0, pct = total ? Math.round(n / total * 100) : 0;
      b.querySelector('.opt-bar').style.width = pct + '%';
      b.querySelector('.opt-count').textContent = n ? pct + '% (' + n + ')' : '';
      b.setAttribute('aria-pressed', b.dataset.choice === mine ? 'true' : 'false');
    });
    status.textContent = total === 0 ? 'No votes yet. Be the first.'
      : total + (total === 1 ? ' vote' : ' votes') + ' so far.' + (mine ? ' Your vote is in.' : '');
  }
  function fail() { status.textContent = "The votes didn't load. Refresh the page to try again."; }
  function call(body) {
    return fetch('/api/vote', body ? { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) } : undefined)
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { render(d.counts); });
  }
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      if (!voter) return fail();
      var prev = mine; mine = b.dataset.choice;
      buttons.forEach(function (x) { x.disabled = true; });
      call({ choice: mine, voter: voter }).then(function () {
        try { localStorage.setItem('llc-vote-next-up-1', mine); } catch (e) {}
      }).catch(function () { mine = prev; fail(); })
        .then(function () { buttons.forEach(function (x) { x.disabled = false; }); });
    });
  });
  call().catch(fail);
})();
