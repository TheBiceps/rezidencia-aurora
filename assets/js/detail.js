/* ---------------------------------------------------------------------------
 * P6 — single apartment page
 * Reads ?id=4.03 and renders from APARTMENTS.
 * The plan is the architect's own drawing, cut per apartment (a.plan).
 * ------------------------------------------------------------------------ */

function initDetail() {
  const root = document.querySelector('[data-detail]');
  if (!root) return;

  const id = new URLSearchParams(location.search).get('id');
  const order = APARTMENTS.slice().sort((a, b) =>
    a.floor - b.floor || Number(a.id.split('.')[1]) - Number(b.id.split('.')[1]));
  const idx = order.findIndex(a => a.id === id);

  if (idx === -1) {
    root.innerHTML = `<div class="empty">
      <h3>Byt sa nenašiel</h3>
      <p class="lede" style="margin-inline:auto">Skontrolujte prosím odkaz alebo si vyberte byt z celkovej ponuky.</p>
      <p><a class="btn btn--primary" href="byty.html">Zobraziť všetky byty</a></p>
    </div>`;
    return;
  }

  const a = order[idx];
  const prev = order[(idx - 1 + order.length) % order.length];
  const next = order[(idx + 1) % order.length];
  const ppm = a.price != null ? Math.round(a.price / a.area) : null;

  document.title = `Byt ${a.id} — ${a.type}, ${fmtArea(a.area)} m² | P6`;
  const meta = document.querySelector('meta[name="description"]');
  if (meta) meta.setAttribute('content',
    `${a.type} ${a.id} na ${a.floor}. nadzemnom podlaží. Interiér ${fmtArea(a.area)} m², balkón ${fmtArea(a.ext)} m². Pôdorys a výmery miestností.`);

  root.querySelectorAll('[data-crumb]').forEach(el => { el.textContent = 'Byt ' + a.id; });

  root.querySelector('[data-head]').innerHTML = `
    <p class="eyebrow">P6 · Prievozská 6 · ${a.floor}. nadzemné podlažie</p>
    <div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:12px 22px">
      <h1 style="font-size:clamp(2.8rem,6.5vw,5rem)">Byt ${a.id}</h1>
      <span class="pill pill--${a.status}">${STATUS_LABEL[a.status]}</span>
    </div>
    <p class="lede" style="margin-top:14px">${a.type} · ${a.floor}. nadzemné podlažie · byt ${a.letter}</p>`;

  root.querySelector('[data-spec]').innerHTML = [
    ['Interiér', fmtArea(a.area), 'm²'],
    ['Balkón', fmtArea(a.ext), 'm²'],
    ['Spolu', fmtArea(a.total), 'm²'],
    ['Izby', a.rooms, ''],
    ['Podlažie', a.floor + '. NP', ''],
  ].map(([k, v, u]) =>
    `<div class="spec__item"><dt>${k}</dt><dd>${v}${u ? ` <small>${u}</small>` : ''}</dd></div>`).join('');

  const planHost = root.querySelector('[data-plan]');
  planHost.innerHTML =
    `<img class="plan__img" src="${a.plan}" loading="lazy" decoding="async"
          alt="Pôdorys bytu ${a.id} — ${a.type}, interiér ${fmtArea(a.area)} m²">`;
  const dl = root.querySelector('[data-plan-download]');
  if (dl) dl.href = a.plan;

  const rt = root.querySelector('[data-rooms]');
  rt.querySelector('tbody').innerHTML = a.roomList
    .map((r, i) => `<tr data-room="${i}"><td>${r.name}</td><td>${fmtArea1(r.area)} m²</td></tr>`).join('');
  rt.querySelector('tfoot td:last-child').textContent = fmtArea(a.area) + ' m²';

  root.querySelector('[data-aside]').innerHTML = `
    <div class="aside__box">
      <p class="eyebrow" style="margin-bottom:4px">${a.status === 'predany' ? 'Stav bytu' : 'Cena vrátane DPH'}</p>
      <div class="aside__price">${a.status === 'predany' ? 'Predané' : fmtPrice(a.price, a.status)}</div>
      ${ppm && a.status !== 'predany' && SHOW_PRICES
        ? `<div class="aside__ppm">${nfPrice.format(ppm)} € / m² interiéru</div>` : ''}
      <div class="aside__actions">
        ${a.status === 'predany'
          ? `<a class="btn btn--primary" href="byty.html?status=dostupny">Zobraziť voľné byty ${icon.arrow}</a>
             <a class="btn btn--ghost" href="kontakt.html">Napísať nám</a>`
          : `<a class="btn btn--primary" href="kontakt.html?byt=${encodeURIComponent(a.id)}">
               ${a.status === 'rezervovany' ? 'Zapísať sa ako náhradník' : 'Mám záujem o tento byt'} ${icon.arrow}</a>
             <a class="btn btn--ghost" href="byty.html">Späť na ponuku</a>`}
      </div>
      <p class="form__note" style="margin:18px 0 0">
        Parkovacie státie a pivničná kobka sa predávajú samostatne.
        Uvedené výmery sú projektové a môžu sa mierne líšiť od skutočného vyhotovenia.
      </p>
    </div>`;

  root.querySelector('[data-detailnav]').innerHTML = `
    <a class="link-arrow" href="byt.html?id=${encodeURIComponent(prev.id)}" style="flex-direction:row-reverse">
      <span style="transform:rotate(180deg);display:inline-flex">${icon.arrow}</span> Byt ${prev.id}</a>
    <a class="link-arrow" href="byt.html?id=${encodeURIComponent(next.id)}">Byt ${next.id} ${icon.arrow}</a>`;

  /* position in the building — clickable, so browsing neighbours is one hop */
  const mini = root.querySelector('[data-mini]');
  if (mini) mini.innerHTML = schematicSVG(a.id);


  /* hovering a room in the plan highlights its row in the table, and back.
     Delegated from stable parents so a plan redraw does not unbind it. */
  const roomsBody = rt.querySelector('tbody');
  const mark = (key, on) => {
    root.querySelectorAll(`[data-room="${key}"]`).forEach(el => el.classList.toggle('is-on', on));
  };
  [planHost, roomsBody].forEach(scope => {
    if (!scope) return;
    ['mouseover', 'focusin'].forEach(ev => scope.addEventListener(ev, e => {
      const t = e.target.closest('[data-room]');
      if (t) mark(t.dataset.room, true);
    }));
    ['mouseout', 'focusout'].forEach(ev => scope.addEventListener(ev, e => {
      const t = e.target.closest('[data-room]');
      if (t) mark(t.dataset.room, false);
    }));
  });

  /* persistent CTA on phones — the price and the enquiry button stay in
     reach instead of living 2,000px up the page */
  const bar = document.querySelector('[data-sticky-cta]');
  if (bar) {
    const sold = a.status === 'predany';
    bar.innerHTML = `
      <div class="sticky-cta__price">
        <span class="sticky-cta__label">${sold ? 'Byt ' + a.id : 'Cena vrátane DPH'}</span>
        <span class="sticky-cta__value">${sold ? 'Predané' : fmtPrice(a.price, a.status)}</span>
      </div>
      ${sold
        ? `<a class="btn btn--primary" href="byty.html?status=dostupny">Voľné byty</a>`
        : `<a class="btn btn--primary" href="kontakt.html?byt=${encodeURIComponent(a.id)}">Mám záujem</a>`}`;
    bar.hidden = false;
    document.body.classList.add('has-sticky-cta');
  }

  /* ← / → walk through the building */
  document.addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
    if (e.key === 'ArrowLeft') location.href = 'byt.html?id=' + encodeURIComponent(prev.id);
    if (e.key === 'ArrowRight') location.href = 'byt.html?id=' + encodeURIComponent(next.id);
  });

  /* same layout type, still available */
  const similar = APARTMENTS.filter(x => x.letter === a.letter && x.id !== a.id && x.status === 'dostupny').slice(0, 6);
  const simWrap = root.querySelector('[data-similar]');
  if (similar.length) {
    simWrap.querySelector('[data-similar-cards]').innerHTML = similar.map(x => unitCardHTML(x)).join('');
  } else {
    simWrap.hidden = true;
  }
}
