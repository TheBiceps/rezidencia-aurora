/* ---------------------------------------------------------------------------
 * P6 — apartment list
 * Cards only (the brief replaces the typology table with cards). Filters per
 * the brief: rooms, floor, area, terrace/balcony, orientation, availability.
 * Needs plan.js for the floor-plan thumbnails.
 * ------------------------------------------------------------------------ */

function unitCardHTML(a, opts) {
  const o = opts || {};
  const href = a.status === 'predany' ? null : 'byt.html?id=' + encodeURIComponent(a.id);
  const tag = href ? 'a' : 'div';
  return `<${tag} class="ucard" data-status="${a.status}" ${href ? `href="${href}"` : ''}>
    <div class="ucard__plan" aria-hidden="true">${planSVG(a, { compact: true })}</div>
    <div class="ucard__body">
      <div class="ucard__top">
        <div>
          <div class="ucard__id">${a.id}</div>
          <div class="ucard__type">${a.type} · ${a.floor}. NP</div>
        </div>
        <span class="pill pill--${a.status}">${STATUS_LABEL[a.status]}</span>
      </div>
      <dl class="ucard__rows">
        <div><dt>Izby</dt><dd>${a.rooms}</dd></div>
        <div><dt>Interiér</dt><dd>${fmtArea(a.area)} m²</dd></div>
        <div><dt>${a.extKind}</dt><dd>${fmtArea(a.ext)} m²</dd></div>
        <div><dt>Orientácia</dt><dd>${a.orientation}</dd></div>
      </dl>
      <div class="ucard__foot">
        <span class="ucard__price">${fmtPrice(a.price, a.status)}</span>
        ${href && !o.noArrow ? `<span class="ucard__go">${icon.arrow}</span>` : ''}
      </div>
    </div>
  </${tag}>`;
}

function initList() {
  const root = document.querySelector('[data-list]');
  if (!root) return;

  const cards = root.querySelector('[data-cards]');
  const empty = root.querySelector('[data-empty]');
  const counts = root.querySelectorAll('[data-count]');
  const phone = window.matchMedia('(max-width: 759px)');

  const f = {
    rooms:  root.querySelector('#f-rooms'),
    floor:  root.querySelector('#f-floor'),
    area:   root.querySelector('#f-area'),
    ext:    root.querySelector('#f-ext'),
    orient: root.querySelector('#f-orient'),
    status: root.querySelector('#f-status'),
  };

  /* prefill from the URL — hero floor chips link in with ?floor=4 */
  const params = new URLSearchParams(location.search);
  Object.keys(f).forEach(k => {
    const v = params.get(k);
    if (v && f[k] && [...f[k].options].some(op => op.value === v)) f[k].value = v;
  });

  function matches(a) {
    if (f.status.value && a.status !== f.status.value) return false;
    if (f.rooms.value && String(a.rooms >= 5 ? 5 : a.rooms) !== f.rooms.value) return false;
    if (f.floor.value && String(a.floor) !== f.floor.value) return false;
    if (f.area.value && a.area < Number(f.area.value)) return false;
    if (f.ext.value && a.extKind !== f.ext.value) return false;
    if (f.orient.value && !a.orientation.includes(f.orient.value)) return false;
    return true;
  }

  const order = (a, b) => a.floor - b.floor || Number(a.id.split('.')[1]) - Number(b.id.split('.')[1]);

  function render() {
    const rows = APARTMENTS.filter(matches).sort(order);
    cards.innerHTML = rows.map(a => unitCardHTML(a)).join('');
    const label = `${rows.length} ${plural(rows.length, 'byt', 'byty', 'bytov')}`;
    counts.forEach(el => { el.textContent = label; });
    empty.hidden = rows.length > 0;
    cards.hidden = rows.length === 0;
  }

  /* --- mobile filter sheet ---------------------------------------------- */
  const bar = root.querySelector('.filters');
  const fToggle = root.querySelector('[data-filter-toggle]');
  const badge = root.querySelector('[data-filter-badge]');
  const scrim = root.querySelector('[data-filter-scrim]');

  const activeCount = () => Object.values(f).filter(el => el && el.value).length;
  function syncBadge() {
    if (!badge) return;
    const n = activeCount();
    badge.textContent = n;
    badge.hidden = n === 0;
  }
  function setSheet(open) {
    if (!bar) return;
    bar.dataset.open = String(open);
    if (fToggle) fToggle.setAttribute('aria-expanded', String(open));
    if (scrim) scrim.hidden = !open;
    if (phone.matches) document.body.dataset.locked = String(open);
  }
  if (fToggle && bar) {
    fToggle.addEventListener('click', () => setSheet(bar.dataset.open !== 'true'));
    root.querySelectorAll('[data-filter-close]').forEach(b => b.addEventListener('click', () => setSheet(false)));
    if (scrim) scrim.addEventListener('click', () => setSheet(false));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && bar.dataset.open === 'true') setSheet(false); });
  }

  Object.values(f).forEach(el => el && el.addEventListener('change', () => { syncBadge(); render(); }));
  const reset = root.querySelector('[data-reset]');
  reset && reset.addEventListener('click', () => {
    Object.values(f).forEach(el => { if (el) el.value = ''; });
    history.replaceState(null, '', location.pathname);
    syncBadge();
    render();
  });
  const onBreak = () => { if (!phone.matches) setSheet(false); };
  phone.addEventListener ? phone.addEventListener('change', onBreak) : phone.addListener(onBreak);

  syncBadge();
  render();
}
