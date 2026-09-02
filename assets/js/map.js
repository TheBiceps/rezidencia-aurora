/* ---------------------------------------------------------------------------
 * P6 — schematic city map + "päťminútové mesto"
 *
 * One component, two modes:
 *   mountCityMap(el, { mode: 'static' })       wide minimal map, key places only
 *   mountCityMap(el, { mode: 'interactive' })  travel-mode toggle, category chips,
 *                                              reachable places list
 *
 * ⚠️  Positions are SCHEMATIC (north up, not to scale) and distances are
 *     estimates from Prievozská 6 along real streets. Verify the km column
 *     before launch — every time on the page derives from it.
 * ------------------------------------------------------------------------ */

const CATS = {
  praca:    'Práca',
  skola:    'Škola',
  doprava:  'Doprava',
  nakupy:   'Nákupy',
  sport:    'Šport',
  gastro:   'Gastronómia',
  volnycas: 'Voľný čas',
};

/* x/y in a 1200×640 frame, P6 at centre-right. `key` = shown on the static map. */
const POIS = [
  { id: 'p6',          name: 'P6 · Prievozská 6',                 x: 600, y: 330, km: 0,    cats: [],                        self: true },
  { id: 'apollo', anchor: 'start',      name: 'Apollo Business Center II',         x: 546, y: 356, km: 0.15, cats: ['praca'],                 key: true },
  { id: 'mhd', anchor: 'start',         name: 'Zastávka MHD Miletičova',           x: 522, y: 298, km: 0.25, cats: ['doprava'] },
  { id: 'gastro', anchor: 'start',      name: 'Kaviarne a reštaurácie Miletičova', x: 508, y: 262, km: 0.4,  cats: ['gastro'] },
  { id: 'fitness', anchor: 'start',     name: 'Fitness centrá v okolí',            x: 660, y: 396, km: 0.5,  cats: ['sport'] },
  { id: 'novohradska', anchor: 'start', name: 'Spojená škola Novohradská',         x: 724, y: 230, km: 0.6,  cats: ['skola'],                 key: true },
  { id: 'mileticka', anchor: 'end',   name: 'Trhovisko Miletičova',              x: 466, y: 236, km: 0.7,  cats: ['nakupy', 'gastro'],      key: true },
  { id: 'nivy', anchor: 'start',        name: 'Nivy · autobusová stanica a centrum', x: 428, y: 414, km: 1.1, cats: ['doprava', 'nakupy', 'gastro'], key: true, label: 'Nivy' },
  { id: 'cbc', anchor: 'end',         name: 'CBC',                               x: 372, y: 350, km: 1.2,  cats: ['praca'] },
  { id: 'nivytower', anchor: 'end',   name: 'Nivy Tower',                        x: 366, y: 398, km: 1.4,  cats: ['praca'] },
  { id: 'd1', anchor: 'end',          name: 'Nájazd na D1',                      x: 986, y: 470, km: 1.5,  cats: ['doprava'] },
  { id: 'zimny', anchor: 'start',       name: 'Zimný štadión Ondreja Nepelu',      x: 596, y: 110, km: 1.6,  cats: ['sport'],                 key: true },
  { id: 'twincity', anchor: 'end',    name: 'Twin City',                         x: 318, y: 418, km: 1.6,  cats: ['praca'] },
  { id: 'strkovec', anchor: 'end',    name: 'Štrkovecké jazero',                 x: 902, y: 244, km: 1.8,  cats: ['sport', 'volnycas'] },
  { id: 'skypark', anchor: 'end',     name: 'Sky Park',                          x: 284, y: 456, km: 1.9,  cats: ['praca', 'gastro', 'volnycas'], key: true },
  { id: 'nfs', anchor: 'start',         name: 'Národný futbalový štadión',         x: 650, y: 64,  km: 1.9,  cats: ['sport'] },
  { id: 'promenada', anchor: 'start',   name: 'Dunajská promenáda',                x: 340, y: 556, km: 2.3,  cats: ['sport', 'volnycas'] },
  { id: 'eurovea', anchor: 'end',     name: 'Eurovea',                           x: 234, y: 526, km: 2.4,  cats: ['nakupy', 'gastro', 'volnycas'], key: true },
  { id: 'downtown', anchor: 'start',    name: 'Downtown · Staré Mesto',            x: 128, y: 326, km: 3.2,  cats: ['gastro', 'volnycas'],    label: 'Downtown' },
  { id: 'letisko', anchor: 'end',     name: 'Letisko Bratislava',                x: 1150, y: 302, km: 8.5, cats: ['doprava'],               car: '10–15 min', edge: true },
];

/* minutes per km — deliberately conservative city-pace figures */
const MODES = {
  pesi:      { label: 'Pešo',       perKm: 12,  fixed: 0 },
  bicykel:   { label: 'Bicyklom',   perKm: 4,   fixed: 1 },
  kolobezka: { label: 'Kolobežkou', perKm: 3.4, fixed: 1 },
  auto:      { label: 'Autom',      perKm: 2.2, fixed: 3 },
};

function travelMinutes(poi, modeKey) {
  if (poi.self) return 0;
  if (modeKey === 'auto' && poi.car) return poi.car;
  if (modeKey !== 'auto' && poi.km > 6) return null;   // not a realistic walk / ride
  const m = MODES[modeKey];
  return Math.max(1, Math.round(poi.km * m.perKm + m.fixed));
}

const fmtMin = v => v === null ? '—' : (typeof v === 'string' ? v : `≈ ${v} min`);
const tierOf = v => v === null ? 'far' : (typeof v === 'string' ? 'mid' : (v <= 5 ? 'near' : v <= 15 ? 'mid' : 'far'));

/* --- drawing ------------------------------------------------------------- */

function cityMapSVG(opts) {
  const o = opts || {};
  const dark = o.theme === 'dark';
  const show = o.mode === 'static' ? POIS.filter(p => p.self || p.key) : POIS;

  const c = dark
    ? { bg: '#14120F', water: '#1E2A33', waterLine: '#3A5566', street: 'rgba(247,244,239,.10)', area: 'rgba(247,244,239,.05)',
        label: 'rgba(247,244,239,.78)', faint: 'rgba(247,244,239,.38)', dot: '#C4AB89', dotLine: '#14120F' }
    : { bg: '#EFEAE2', water: '#D6DEE3', waterLine: '#B7C7D1', street: 'rgba(20,18,15,.10)', area: 'rgba(20,18,15,.045)',
        label: '#2E2924', faint: '#7A7167', dot: '#14120F', dotLine: '#EFEAE2' };

  let s = `<rect x="0" y="0" width="1200" height="640" fill="${c.bg}"/>`;

  /* the Danube — the one landmark everyone reads instantly */
  s += `<path d="M -20 400 C 110 450, 180 540, 300 580 S 640 630, 1220 596 L 1220 660 L -20 660 Z" fill="${c.water}"/>`;
  s += `<path d="M -20 400 C 110 450, 180 540, 300 580 S 640 630, 1220 596" fill="none" stroke="${c.waterLine}" stroke-width="2"/>`;
  s += `<text x="1040" y="622" font-family="Inter,sans-serif" font-size="13" letter-spacing="3" fill="${c.faint}">DUNAJ</text>`;

  /* old town as a soft area, Ružinov as a label */
  s += `<ellipse cx="120" cy="330" rx="150" ry="120" fill="${c.area}"/>`;
  s += `<text x="1010" y="150" font-family="Inter,sans-serif" font-size="13" letter-spacing="3" fill="${c.faint}">RUŽINOV</text>`;

  /* a handful of orienting streets, unlabelled */
  const st = `stroke="${c.street}" stroke-width="3" stroke-linecap="round" fill="none"`;
  s += `<path d="M 430 340 L 960 336" ${st}/>`;                 /* Prievozská */
  s += `<path d="M 484 190 L 476 460" ${st}/>`;                 /* Miletičova */
  s += `<path d="M 250 470 C 400 420, 520 380, 660 372" ${st}/>`; /* Mlynské nivy */
  s += `<path d="M 742 40 L 748 520" ${st}/>`;                  /* Bajkalská */
  s += `<path d="M 470 214 L 1130 206" ${st}/>`;                /* Trnavská */
  s += `<path d="M 60 470 C 160 500, 260 540, 330 560" ${st}/>`;/* nábrežie */

  /* reach rings around P6 — the "five minute" idea made visible */
  if (o.mode === 'interactive') {
    s += `<g class="citymap__rings">
            <circle cx="600" cy="330" r="118" fill="none" stroke="${c.faint}" stroke-width="1" stroke-dasharray="4 7" opacity=".55"/>
            <circle cx="600" cy="330" r="290" fill="none" stroke="${c.faint}" stroke-width="1" stroke-dasharray="4 7" opacity=".3"/>
          </g>`;
  }

  show.forEach(p => {
    if (p.self) return;
    const lbl = p.label || p.name;
    const anchorRight = p.anchor ? p.anchor === 'end' : p.x > 640;
    s += `<g class="poi" data-id="${p.id}" data-cats="${p.cats.join(' ')}" tabindex="0" role="img" aria-label="${p.name}">
            <circle class="poi__halo" cx="${p.x}" cy="${p.y}" r="16"/>
            <circle class="poi__dot" cx="${p.x}" cy="${p.y}" r="5.5" fill="${c.dot}" stroke="${c.dotLine}" stroke-width="2"/>
            <text class="poi__label" x="${p.x + (anchorRight ? -14 : 14)}" y="${p.y + 4.5}"
                  text-anchor="${anchorRight ? 'end' : 'start'}" font-family="Inter,sans-serif" font-size="14" fill="${c.label}">${lbl}</text>
            <text class="poi__time" x="${p.x + (anchorRight ? -14 : 14)}" y="${p.y + 22}"
                  text-anchor="${anchorRight ? 'end' : 'start'}" font-family="Inter,sans-serif" font-size="12" font-weight="600" fill="#B87333"></text>
          </g>`;
  });

  /* P6 — copper, on top of everything */
  s += `<g class="poi poi--self" aria-label="P6, Prievozská 6">
          <circle class="poi__pulse" cx="600" cy="330" r="12" fill="none" stroke="#B87333" stroke-width="2"/>
          <circle cx="600" cy="330" r="9" fill="#B87333" stroke="${c.bg}" stroke-width="3"/>
          <text x="618" y="322" font-family="Inter,sans-serif" font-size="15" font-weight="600" letter-spacing="1" fill="${dark ? '#F7F4EF' : '#14120F'}">P6</text>
          <text x="618" y="340" font-family="Inter,sans-serif" font-size="12" fill="${c.faint}">Prievozská 6</text>
        </g>`;

  return `<svg class="citymap__svg" viewBox="0 0 1200 640" role="img"
            aria-label="Schematická mapa Bratislavy s polohou P6 a okolitých miest">${s}</svg>`;
}

/* --- mount ---------------------------------------------------------------- */

function mountCityMap(el, opts) {
  const o = Object.assign({ mode: 'static', theme: 'light' }, opts || {});
  const stage = el.querySelector('[data-map-stage]') || el;
  stage.innerHTML = cityMapSVG(o);

  /* phones: the map scrolls sideways; open it centred on P6 */
  const scroller = el.querySelector('[data-map-scroll]');
  if (scroller) {
    const centre = () => {
      const w = scroller.scrollWidth, v = scroller.clientWidth;
      if (w > v) scroller.scrollLeft = (w * 0.5) - v * 0.5;
    };
    centre();
    window.addEventListener('resize', centre, { passive: true });
  }

  if (o.mode !== 'interactive') return;

  const modeBtns = [...el.querySelectorAll('[data-mode]')];
  const catBtns = [...el.querySelectorAll('[data-cat]')];
  const list = el.querySelector('[data-reach-list]');
  const summary = el.querySelector('[data-reach-summary]');
  const pois = [...stage.querySelectorAll('.poi[data-id]')];

  let mode = 'pesi';
  let cat = 'all';

  function render() {
    const rows = [];
    pois.forEach(node => {
      const p = POIS.find(x => x.id === node.dataset.id);
      const inCat = cat === 'all' || p.cats.includes(cat);
      const t = travelMinutes(p, mode);
      const tier = tierOf(t);
      node.dataset.tier = tier;
      node.classList.toggle('is-off', !inCat);
      node.querySelector('.poi__time').textContent = inCat ? fmtMin(t) : '';
      if (inCat) rows.push({ p, t, tier });
    });

    rows.sort((a, b) => {
      const av = typeof a.t === 'number' ? a.t : 999, bv = typeof b.t === 'number' ? b.t : 999;
      return av - bv;
    });

    if (list) {
      list.innerHTML = rows.map(({ p, t, tier }) => `
        <li class="reach__row" data-tier="${tier}">
          <span class="reach__name">${p.name}</span>
          <span class="reach__cats">${p.cats.map(k => CATS[k]).join(' · ')}</span>
          <span class="reach__time">${fmtMin(t)}</span>
        </li>`).join('');
    }
    if (summary) {
      const near = rows.filter(r => typeof r.t === 'number' && r.t <= 5).length;
      const mid = rows.filter(r => typeof r.t === 'number' && r.t <= 15).length;
      summary.innerHTML = `<b>${near}</b> ${plural(near, 'miesto', 'miesta', 'miest')} do 5 minút · <b>${mid}</b> do 15 minút — ${MODES[mode].label.toLowerCase()}`;
    }
  }

  modeBtns.forEach(b => b.addEventListener('click', () => {
    mode = b.dataset.mode;
    modeBtns.forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    render();
  }));
  catBtns.forEach(b => b.addEventListener('click', () => {
    cat = b.dataset.cat;
    catBtns.forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    render();
  }));

  /* hovering a list row lights its dot, and back */
  const link = (id, on) => {
    el.querySelectorAll(`[data-id="${id}"]`).forEach(n => n.classList.toggle('is-hot', on));
  };
  if (list) {
    list.addEventListener('mouseover', e => { const r = e.target.closest('.reach__row'); if (r) link(POIS.find(p => p.name === r.querySelector('.reach__name').textContent).id, true); });
    list.addEventListener('mouseout',  e => { const r = e.target.closest('.reach__row'); if (r) link(POIS.find(p => p.name === r.querySelector('.reach__name').textContent).id, false); });
  }

  render();
}

/* --- the business-zone route (section 5) ---------------------------------- */

function routeTimes() {
  const stops = ['p6', 'apollo', 'nivy', 'twincity', 'skypark', 'eurovea'];
  return stops.map(id => {
    const p = POIS.find(x => x.id === id);
    return { id, name: p.label || p.name.split(' ·')[0], bike: travelMinutes(p, 'bicykel'), scooter: travelMinutes(p, 'kolobezka'), walk: travelMinutes(p, 'pesi') };
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-citymap]').forEach(el => {
    mountCityMap(el, { mode: el.dataset.citymap, theme: el.dataset.theme || 'light' });
  });
  const route = document.querySelector('[data-route]');
  if (route) {
    route.innerHTML = routeTimes().map((r, i) => `
      <li class="route__stop${i === 0 ? ' route__stop--self' : ''}">
        <span class="route__dot"></span>
        <span class="route__name">${r.name}</span>
        ${i === 0 ? `<span class="route__meta">štart</span>`
                  : `<span class="route__meta"><b>${r.bike}</b> min bicyklom · <b>${r.scooter}</b> min kolobežkou</span>`}
      </li>`).join('');
  }
});
