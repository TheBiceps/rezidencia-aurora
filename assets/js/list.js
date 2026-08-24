/* ---------------------------------------------------------------------------
 * REZIDENCIA AURORA — apartment list: filtering, sorting, table/card views
 * ------------------------------------------------------------------------ */

function initList() {
  const root = document.querySelector('[data-list]');
  if (!root) return;

  const tbody = root.querySelector('[data-rows]');
  const cards = root.querySelector('[data-cards]');
  const empty = root.querySelector('[data-empty]');
  const counts = root.querySelectorAll('[data-count]');
  const tableWrap = root.querySelector('[data-table]');

  const f = {
    status: root.querySelector('#f-status'),
    rooms: root.querySelector('#f-rooms'),
    floor: root.querySelector('#f-floor'),
    area: root.querySelector('#f-area'),
    price: root.querySelector('#f-price'),
  };

  const phone = window.matchMedia('(max-width: 759px)');

  let sort = { key: 'id', dir: 'asc' };
  /* a 940px-wide table is unusable on a phone, so cards are forced there
     regardless of the remembered preference */
  let stored = localStorage.getItem('aurora-view') || 'table';
  let view = phone.matches ? 'cards' : stored;

  /* prefill from the URL — the hero floor strip links in with ?floor=4 */
  const params = new URLSearchParams(location.search);
  ['status', 'rooms', 'floor'].forEach(k => {
    const v = params.get(k);
    if (v && f[k] && [...f[k].options].some(o => o.value === v)) f[k].value = v;
  });

  function matches(a) {
    if (f.status.value && a.status !== f.status.value) return false;
    if (f.rooms.value && String(a.rooms >= 5 ? 5 : a.rooms) !== f.rooms.value) return false;
    if (f.floor.value && String(a.floor) !== f.floor.value) return false;
    if (f.area.value && a.area < Number(f.area.value)) return false;
    if (f.price.value && a.price != null && a.price > Number(f.price.value)) return false;
    return true;
  }

  function compare(a, b) {
    const k = sort.key;
    let x, y;
    if (k === 'id') { x = a.floor * 100 + Number(a.id.split('.')[1]); y = b.floor * 100 + Number(b.id.split('.')[1]); }
    else if (k === 'status') { x = ['dostupny', 'rezervovany', 'predany'].indexOf(a.status); y = ['dostupny', 'rezervovany', 'predany'].indexOf(b.status); }
    else { x = a[k]; y = b[k]; }
    const d = x < y ? -1 : x > y ? 1 : 0;
    return sort.dir === 'asc' ? d : -d;
  }

  function rowHTML(a) {
    const href = a.status === 'predany' ? null : 'byt.html?id=' + encodeURIComponent(a.id);
    return `<tr data-status="${a.status}" ${href ? `data-href="${href}"` : ''}>
      <td class="cell-id">${href ? `<a href="${href}">${a.id}</a>` : a.id}</td>
      <td>${a.type}</td>
      <td class="num">${a.floor}. NP</td>
      <td class="num">${fmtArea(a.area)}</td>
      <td class="num">${fmtArea(a.ext)} <span style="color:var(--text-muted)">${a.extKind.toLowerCase()}</span></td>
      <td class="num">${fmtArea(a.total)}</td>
      <td>${a.orientation}</td>
      <td><span class="pill pill--${a.status}">${STATUS_LABEL[a.status]}</span></td>
      <td class="num">${fmtPrice(a.price, a.status)}</td>
      <td class="cell-go">${href ? icon.arrow : ''}</td>
    </tr>`;
  }

  function cardHTML(a) {
    const href = a.status === 'predany' ? null : 'byt.html?id=' + encodeURIComponent(a.id);
    const tag = href ? 'a' : 'div';
    return `<${tag} class="card" data-status="${a.status}" ${href ? `href="${href}"` : ''}>
      <div class="card__top">
        <div>
          <div class="card__id">${a.id}</div>
          <div class="card__type">${a.type} · ${a.floor}. NP</div>
        </div>
        <span class="pill pill--${a.status}">${STATUS_LABEL[a.status]}</span>
      </div>
      <dl class="card__rows">
        <div class="card__row"><dt>Interiér</dt><dd>${fmtArea(a.area)} m²</dd></div>
        <div class="card__row"><dt>${a.extKind}</dt><dd>${fmtArea(a.ext)} m²</dd></div>
        <div class="card__row"><dt>Orientácia</dt><dd>${a.orientation}</dd></div>
        <div class="card__row"><dt>Cena</dt><dd class="card__price">${fmtPrice(a.price, a.status)}</dd></div>
      </dl>
    </${tag}>`;
  }

  function render() {
    const rows = APARTMENTS.filter(matches).sort(compare);

    tbody.innerHTML = rows.map(rowHTML).join('');
    cards.innerHTML = rows.map(cardHTML).join('');
    const label = `${rows.length} ${plural(rows.length, 'byt', 'byty', 'bytov')}`;
    counts.forEach(el => { el.textContent = label; });
    empty.hidden = rows.length > 0;
    const v = phone.matches ? 'cards' : view;
    tableWrap.hidden = v !== 'table' || !rows.length;
    cards.hidden = v !== 'cards' || !rows.length;

    tbody.querySelectorAll('tr[data-href]').forEach(tr => {
      tr.addEventListener('click', e => {
        if (e.target.closest('a')) return;
        location.href = tr.dataset.href;
      });
    });
  }

  /* sorting */
  root.querySelectorAll('th button[data-sort]').forEach(btn => {
    btn.insertAdjacentHTML('beforeend', icon.sort);
    btn.addEventListener('click', () => {
      const key = btn.dataset.sort;
      sort = { key, dir: sort.key === key && sort.dir === 'asc' ? 'desc' : 'asc' };
      root.querySelectorAll('th button[data-sort]').forEach(b => {
        b.removeAttribute('data-dir');
        b.closest('th').removeAttribute('aria-sort');
      });
      btn.dataset.dir = sort.dir;
      btn.closest('th').setAttribute('aria-sort', sort.dir === 'asc' ? 'ascending' : 'descending');
      render();
    });
  });

  /* view toggle */
  root.querySelectorAll('[data-view]').forEach(btn => {
    btn.addEventListener('click', () => {
      view = btn.dataset.view;
      stored = view;
      localStorage.setItem('aurora-view', view);
      root.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      render();
    });
    btn.setAttribute('aria-pressed', String(btn.dataset.view === view));
  });

  /* --- mobile filter drawer --------------------------------------------- */
  const bar = root.querySelector('.filters');
  const fToggle = root.querySelector('[data-filter-toggle]');
  const badge = root.querySelector('[data-filter-badge]');

  const activeCount = () => Object.values(f).filter(el => el && el.value).length;

  function syncBadge() {
    if (!badge) return;
    const n = activeCount();
    badge.textContent = n;
    badge.hidden = n === 0;
  }

  const scrim = root.querySelector('[data-filter-scrim]');

  function setSheet(open) {
    bar.dataset.open = String(open);
    if (fToggle) fToggle.setAttribute('aria-expanded', String(open));
    if (scrim) scrim.hidden = !open;
    if (phone.matches) document.body.dataset.locked = String(open);
  }

  if (fToggle && bar) {
    fToggle.addEventListener('click', () => setSheet(bar.dataset.open !== 'true'));
    root.querySelectorAll('[data-filter-close]').forEach(b =>
      b.addEventListener('click', () => setSheet(false)));
    if (scrim) scrim.addEventListener('click', () => setSheet(false));
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && bar.dataset.open === 'true') setSheet(false);
    });
  }

  Object.values(f).forEach(el => el && el.addEventListener('change', () => { syncBadge(); render(); }));
  const reset = root.querySelector('[data-reset]');
  reset && reset.addEventListener('click', () => {
    Object.values(f).forEach(el => { if (el) el.value = ''; });
    history.replaceState(null, '', location.pathname);
    syncBadge();
    render();
  });

  /* crossing the breakpoint swaps the view without a reload */
  const onBreak = () => {
    if (!phone.matches) { view = stored; setSheet(false); }
    render();
  };
  phone.addEventListener ? phone.addEventListener('change', onBreak) : phone.addListener(onBreak);

  syncBadge();

  render();
}
