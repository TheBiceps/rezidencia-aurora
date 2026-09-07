/* ---------------------------------------------------------------------------
 * P6 — real map + "päťminútové mesto"
 *
 * Leaflet over CARTO basemaps. Every distance and time below is a REAL routed
 * value from P6 (Prievozská 6), measured on the OSM road/path network with
 * OSRM — walking and cycling profiles, car for the airports. They are not
 * straight-line estimates. Re-measure with _build/geo/ if a POI moves.
 *
 * Car times are free-flow: no traffic. Treat them as a floor, not a promise.
 * ------------------------------------------------------------------------ */

const P6 = { lat: 48.146834, lng: 17.141030, label: 'P6 · Prievozská 6' };

/* m = routed metres on foot; walk/bike/car = minutes */
const POIS = [
  { id: 'apollo', dir: 'bottom',      name: 'Apollo Business Center II',        short: 'Apollo',      lat: 48.146692, lng: 17.140077, m:   75, walk:  1, bike:  1, car:  2, cats: ['praca'] },
  { id: 'novohradska', dir: 'bottom', name: 'Spojená škola Novohradská',        short: 'Škola',       lat: 48.145905, lng: 17.134489, m:  547, walk:  7, bike:  4, car:  2, cats: ['skola'], key: true },
  { id: 'd1', dir: 'right',          name: 'Nájazd na D1',                     short: 'D1',          lat: 48.148705, lng: 17.147446, m:  550, walk:  7, bike:  4, car:  3, cats: ['doprava'] },
  { id: 'nivytower', dir: 'left',   name: 'Nivy Tower',                       short: 'Nivy Tower',  lat: 48.146215, lng: 17.130031, m:  883, walk: 12, bike:  5, car:  3, cats: ['praca'] },
  { id: 'mileticka', dir: 'top',   name: 'Trhovisko Miletičova',             short: 'Miletička',   lat: 48.153787, lng: 17.136708, m:  936, walk: 13, bike:  7, car:  3, cats: ['nakupy', 'gastro'], key: true },
  { id: 'nivy', dir: 'left',        name: 'Nivy — centrum a autobusová stanica', short: 'Nivy',    lat: 48.146842, lng: 17.128698, m: 1042, walk: 14, bike:  8, car:  4, cats: ['doprava', 'nakupy', 'gastro'], key: true },
  { id: 'twincity', dir: 'bottom',    name: 'Twin City',                        short: 'Twin City',   lat: 48.145467, lng: 17.124946, m: 1369, walk: 18, bike:  8, car:  4, cats: ['praca'] },
  { id: 'skypark', dir: 'left',     name: 'Sky Park',                         short: 'Sky Park',    lat: 48.144013, lng: 17.125541, m: 1451, walk: 19, bike:  9, car:  4, cats: ['praca', 'gastro', 'volnycas'], key: true },
  { id: 'cbc', dir: 'top',         name: 'CBC',                              short: 'CBC',         lat: 48.148714, lng: 17.125524, m: 1492, walk: 20, bike:  8, car:  5, cats: ['praca'] },
  { id: 'zimny', dir: 'top',       name: 'Zimný štadión Ondreja Nepelu',     short: 'Zimný štadión', lat: 48.160214, lng: 17.136223, m: 1853, walk: 25, bike: 11, car:  4, cats: ['sport'], key: true },
  { id: 'eurovea', dir: 'left',     name: 'Eurovea',                          short: 'Eurovea',     lat: 48.140359, lng: 17.121856, m: 1999, walk: 27, bike: 12, car:  5, cats: ['nakupy', 'gastro', 'volnycas'], key: true },
  { id: 'strkovec', dir: 'right',    name: 'Štrkovecké jazero',                short: 'Štrkovec',    lat: 48.157959, lng: 17.147301, m: 2161, walk: 29, bike: 12, car:  4, cats: ['sport', 'volnycas'] },
  { id: 'nfs', dir: 'top',         name: 'Národný futbalový štadión',        short: 'Futbalový štadión', lat: 48.163491, lng: 17.136794, m: 2453, walk: 33, bike: 14, car:  5, cats: ['sport'] },
  { id: 'promenada', dir: 'bottom',   name: 'Dunajská promenáda',               short: 'Dunaj',       lat: 48.136376, lng: 17.113283, m: 3120, walk: 42, bike: 16, car:  6, cats: ['sport', 'volnycas'], key: true },
  { id: 'letisko', dir: 'left',     name: 'Letisko M. R. Štefánika',          short: 'Letisko',     lat: 48.170844, lng: 17.210040, m: 8328, walk: null, bike: 34, car: 16, cats: ['doprava'], far: true },
];

const CATS = { praca: 'Práca', skola: 'Škola', doprava: 'Doprava', nakupy: 'Nákupy',
               sport: 'Šport', gastro: 'Gastronómia', volnycas: 'Voľný čas' };
const MODES = { pesi: { label: 'Pešo', k: 'walk' }, bicykel: { label: 'Bicyklom', k: 'bike' },
                auto: { label: 'Autom', k: 'car' } };

const fmtM  = m => m < 1000 ? `${m} m` : `${(m / 1000).toFixed(1).replace('.', ',')} km`;
const fmtT  = v => v == null ? '—' : `${v} min`;
const tier  = v => v == null ? 'far' : v <= 5 ? 'near' : v <= 15 ? 'mid' : 'far';

/* --- Leaflet, loaded once and only when a map is actually needed ---------- */
const LEAFLET_CSS = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
const LEAFLET_JS  = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js';
let leafletReady;
function loadLeaflet() {
  if (leafletReady) return leafletReady;
  leafletReady = new Promise((resolve, reject) => {
    if (window.L) return resolve(window.L);
    const css = document.createElement('link');
    css.rel = 'stylesheet'; css.href = LEAFLET_CSS;
    css.integrity = 'sha512-h9FcoyWjHcOcmEVkxOfTLnmZFWIH0iZhZT1H2TbOq55xssQGEJHEaIm+PgoUaZbRvQTNTluNOEfb1ZRy6D3BOw==';
    css.crossOrigin = 'anonymous';
    document.head.appendChild(css);
    const s = document.createElement('script');
    s.src = LEAFLET_JS;
    s.integrity = 'sha512-puJW3E/qXDqYp9IfhAI54BJEaWIfloJ7JWs7OeD5i6ruC9JZL1gERT1wjtwXFlh7CjE7ZJ+/vcRZRkIYIb6p4g==';
    s.crossOrigin = 'anonymous';
    s.onload = () => resolve(window.L);
    s.onerror = () => reject(new Error('Leaflet failed to load'));
    document.head.appendChild(s);
  });
  return leafletReady;
}

/* --- markers -------------------------------------------------------------- */
function poiIcon(L, p, extra) {
  return L.divIcon({
    className: '', iconSize: [12, 12], iconAnchor: [6, 6],
    html: `<span class="pin ${extra || ''}" data-id="${p.id}"></span>`,
  });
}
function selfIcon(L) {
  return L.divIcon({
    className: '', iconSize: [22, 22], iconAnchor: [11, 11],
    html: '<span class="pin pin--self"><i></i></span>',
  });
}

function mountMap(el, opts) {
  const o = Object.assign({ mode: 'static', theme: 'light' }, opts || {});
  const host = el.querySelector('[data-map-stage]') || el;
  const dark = o.theme === 'dark';

  const start = () => loadLeaflet().then(L => {
    const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const map = L.map(host, {
      zoomControl: true, scrollWheelZoom: false, attributionControl: true,
      /* Leaflet fades tiles in from opacity 0; if the tab is throttled that
         fade can stall and leave the map blank. Paint them straight away. */
      fadeAnimation: false,
      zoomAnimation: !calm, markerZoomAnimation: !calm,
    });
    /* Esri Gray Canvas: keyless, and the muted grey suits the palette.
       CARTO now stamps "API KEY REQUIRED" across its free basemap tiles.
       Base carries no labels, so the Reference layer goes on top of the pins. */
    const esri = n => `https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/${n}/MapServer/tile/{z}/{y}/{x}`;
    const tone = dark ? 'Dark' : 'Light';
    const ATTR = 'Tiles &copy; <a href="https://www.esri.com/">Esri</a> — Esri, HERE, Garmin, ' +
                 '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
    L.tileLayer(esri(`World_${tone}_Gray_Base`), { maxZoom: 18, attribution: ATTR }).addTo(map);
    L.tileLayer(esri(`World_${tone}_Gray_Reference`), { maxZoom: 18, pane: 'shadowPane', opacity: .9 }).addTo(map);

    /* wheel zoom only once the user has actually engaged with the map */
    map.on('click focus', () => map.scrollWheelZoom.enable());
    map.on('mouseout blur', () => map.scrollWheelZoom.disable());

    const shown = o.mode === 'interactive' ? POIS : POIS.filter(p => p.key);
    const marks = {};
    shown.forEach(p => {
      const mk = L.marker([p.lat, p.lng], { icon: poiIcon(L, p), keyboard: true,
                                            title: `${p.name} — ${fmtM(p.m)}` }).addTo(map);
      const dir = p.dir || 'right';
      const off = { right: [8, 0], left: [-8, 0], top: [0, -8], bottom: [0, 8] }[dir];
      mk.bindTooltip(`<b>${p.short}</b><span class="t-time"></span>`,
        { permanent: true, direction: dir, offset: off, className: 'poi-tip' });
      mk.bindPopup(
        `<b>${p.name}</b><br><span class="pop-m">${fmtM(p.m)} z P6</span>` +
        `<br>Pešo ${fmtT(p.walk)} · Bicyklom ${fmtT(p.bike)} · Autom ${fmtT(p.car)}`);
      marks[p.id] = mk;
    });

    L.marker([P6.lat, P6.lng], { icon: selfIcon(L), zIndexOffset: 1000, title: P6.label })
      .addTo(map)
      .bindTooltip('<b>P6</b><span class="t-sub">Prievozská 6</span>',
                   { permanent: true, direction: 'right', offset: [12, 0], className: 'poi-tip poi-tip--self' });

    const near = POIS.filter(p => !p.far);
    map.fitBounds(L.latLngBounds([[P6.lat, P6.lng], ...near.map(p => [p.lat, p.lng])]),
                  { padding: [46, 46] });

    el.classList.add('is-ready');
    if (o.mode === 'interactive') wire(el, map, marks, L);
    setTimeout(() => map.invalidateSize(), 60);
  }).catch(() => { el.classList.add('is-failed'); });

  /* only pull tiles once the section is actually approached */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(e => {
      if (e[0].isIntersecting) { io.disconnect(); start(); }
    }, { rootMargin: '400px' });
    io.observe(el);
  } else start();
}

function wire(el, map, marks, L) {
  const modeBtns = [...el.querySelectorAll('[data-mode]')];
  const catBtns = [...el.querySelectorAll('[data-cat]')];
  const list = el.querySelector('[data-reach-list]');
  const summary = el.querySelector('[data-reach-summary]');
  let mode = 'pesi', cat = 'all';

  function render() {
    const key = MODES[mode].k;
    const rows = POIS.filter(p => cat === 'all' || p.cats.includes(cat))
                     .slice().sort((a, b) => (a[key] ?? 1e9) - (b[key] ?? 1e9));
    POIS.forEach(p => {
      const mk = marks[p.id]; if (!mk) return;
      const on = cat === 'all' || p.cats.includes(cat);
      const t = p[key];
      const pin = mk.getElement() && mk.getElement().querySelector('.pin');
      if (pin) { pin.dataset.tier = tier(t); pin.classList.toggle('is-off', !on); }
      const tip = mk.getTooltip();
      if (tip) {
        const node = tip.getElement();
        if (node) {
          const slot = node.querySelector('.t-time');
          if (slot) slot.textContent = on ? ` ${fmtT(t)}` : '';
          node.classList.toggle('is-off', !on);
        }
      }
    });
    if (list) list.innerHTML = rows.map(p => `
      <li class="reach__row" data-id="${p.id}" data-tier="${tier(p[key])}">
        <span class="reach__name">${p.name}</span>
        <span class="reach__cats">${p.cats.map(c => CATS[c]).join(' · ')} · ${fmtM(p.m)}</span>
        <span class="reach__time">${fmtT(p[key])}</span>
      </li>`).join('');
    if (summary) {
      const n5 = rows.filter(p => p[key] != null && p[key] <= 5).length;
      const n15 = rows.filter(p => p[key] != null && p[key] <= 15).length;
      summary.innerHTML = `<b>${n5}</b> ${plural(n5, 'miesto', 'miesta', 'miest')} do 5 minút · <b>${n15}</b> do 15 minút — ${MODES[mode].label.toLowerCase()}`;
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
  if (list) {
    const hot = (id, on) => {
      const mk = marks[id]; if (!mk) return;
      const pin = mk.getElement() && mk.getElement().querySelector('.pin');
      if (pin) pin.classList.toggle('is-hot', on);
    };
    list.addEventListener('mouseover', e => { const r = e.target.closest('.reach__row'); if (r) hot(r.dataset.id, true); });
    list.addEventListener('mouseout',  e => { const r = e.target.closest('.reach__row'); if (r) hot(r.dataset.id, false); });
    list.addEventListener('click', e => {
      const r = e.target.closest('.reach__row'); if (!r) return;
      const p = POIS.find(x => x.id === r.dataset.id);
      if (p) { map.setView([p.lat, p.lng], 16, { animate: true }); marks[p.id].openPopup(); }
    });
  }
  render();
}

/* --- §5 business-zone route, real routed figures -------------------------- */
function routeStops() {
  const ids = ['apollo', 'nivy', 'twincity', 'skypark', 'eurovea'];
  return [{ self: true, short: 'P6' }].concat(ids.map(id => POIS.find(p => p.id === id)));
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-citymap]').forEach(el =>
    mountMap(el, { mode: el.dataset.citymap, theme: el.dataset.theme || 'light' }));

  const route = document.querySelector('[data-route]');
  if (route) {
    route.innerHTML = routeStops().map((p, i) => i === 0 ? `
      <li class="route__stop route__stop--self">
        <span class="route__dot"></span>
        <span class="route__name">P6</span>
        <span class="route__meta">štart</span>
      </li>` : `
      <li class="route__stop">
        <span class="route__dot"></span>
        <span class="route__name">${p.short}</span>
        <span class="route__meta"><b>${fmtM(p.m)}</b><br>${p.walk}&nbsp;min&nbsp;pešo · ${p.bike}&nbsp;min&nbsp;bicyklom</span>
      </li>`).join('');
  }
});
