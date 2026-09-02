/* ---------------------------------------------------------------------------
 * P6 — the building, drawn once and reused everywhere (placeholder facade)
 *
 * The facade is generated from the SAME geometry that produces the clickable
 * hotspots, so the drawing and the hit areas can never drift apart.
 *
 * Exports used elsewhere:
 *   ART, unitBox(a)          geometry
 *   mountFacade(svg)         paint the building into an <svg>
 *   mountHotspots(svg)       paint the clickable overlay
 *   mountFloorBands(svg)     paint whole-storey highlight bands (scrollytelling)
 *   schematicSVG(activeId)   small abstract elevation for the detail page
 *   frameViewBox(el, w, h)   keep the mass framed at any aspect ratio
 *   setSkyTime(root, t)      0 = dawn … 1 = dusk
 *   initPicker(root)         wire up the hero selector
 *
 * ➜ WHEN THE REAL RENDER ARRIVES
 *   Put it behind `.hero__vis` and keep this file for the hotspot layer only.
 *   Adjust the ART constants until the rects sit on the real windows.
 * ------------------------------------------------------------------------ */

const ART = {
  cx: 800,          // horizontal centre of the apartment bays
  ground: 880,      // ground line
  floorH: 88,       // height of one storey
  bayW: 150,        // width of one bay
  bays: 7,          // bays across the widest floor
  glassTop: 11,     // inset of the glazing from the top of the storey
  glassH: 55,       // height of the glazing
  railH: 15,        // height of the balcony balustrade
};

ART.left = ART.cx - (ART.bays * ART.bayW) / 2;   // 275
ART.right = ART.left + ART.bays * ART.bayW;      // 1325
ART.top = ART.ground - 8 * ART.floorH;           // 176
ART.coreW = 100;                                 // stair / lift core + entrance
ART.coreX = ART.left - ART.coreW;                // 175
ART.coreTop = ART.top - 32;
ART.midX = (ART.coreX + ART.right) / 2;

/** Bounding box of one apartment's slice of the facade, in artwork units. */
function unitBox(a) {
  return {
    x: ART.left + a.bay * ART.bayW,
    y: ART.ground - a.floor * ART.floorH,
    w: ART.bayW,
    h: ART.floorH,
  };
}

/** Extent of one whole storey. */
function floorBox(f) {
  const row = APARTMENTS.filter(u => u.floor === f);
  if (!row.length) return null;
  return {
    x: ART.left + row[0].bayOffset * ART.bayW,
    y: ART.ground - f * ART.floorH,
    w: row[0].bays * ART.bayW,
    h: ART.floorH,
  };
}

/** Deterministic 0–99 value per unit id, so nothing flickers between renders. */
function seed(id) {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) % 9973;
  return h % 100;
}

/* --- palette ------------------------------------------------------------- */

const P = {
  wall:   '#D5CAB7',   // warm limestone
  wallHi: '#E6DDCC',   // slab faces / piers catching light
  wallLo: '#BEB19B',   // shaded returns
  recess: '#AC9F89',   // loggia soffit
  deck:   '#DFD5C4',
  rail:   '#9A8F7E',
  ground: '#C7BEAF',
  paving: '#CFC7B9',
  shade:  '#ABA292',
  green:  '#6E7C63',
  trunk:  '#7B6B55',
};

/** Sky palettes the scrollytelling section interpolates between. */
const SKY_KEYS = [
  { at: 0.00, stops: ['#3E4C63', '#77788C', '#C2967C', '#E6C6A2'], haze: '#FFD2A4', hazeO: 0.75, night: 0.55 },
  { at: 0.38, stops: ['#7E9BB4', '#AEC3D2', '#D8DFDF', '#EFE7D8'], haze: '#FFF4DE', hazeO: 0.85, night: 0.00 },
  { at: 0.72, stops: ['#5C7C9E', '#9DAFC0', '#E2C69A', '#F4D4A6'], haze: '#FFDCA6', hazeO: 0.95, night: 0.18 },
  { at: 1.00, stops: ['#232A3E', '#454759', '#89685A', '#BE8659'], haze: '#FFB877', hazeO: 0.70, night: 1.00 },
];

const DEFS = `<defs>
   <linearGradient id="sky%NS%" gradientUnits="userSpaceOnUse" x1="0" y1="-150" x2="0" y2="890">
     <stop data-sky="0" offset="0%" stop-color="#7E9BB4"/>
     <stop data-sky="1" offset="42%" stop-color="#AEC3D2"/>
     <stop data-sky="2" offset="78%" stop-color="#D8DFDF"/>
     <stop data-sky="3" offset="100%" stop-color="#EFE7D8"/>
   </linearGradient>
   <radialGradient id="haze%NS%" cx="50%" cy="50%">
     <stop data-haze offset="0%" stop-color="#FFF4DE" stop-opacity=".85"/>
     <stop data-haze offset="100%" stop-color="#FFF4DE" stop-opacity="0"/>
   </radialGradient>
   <linearGradient id="glass%NS%" x1="0" y1="0" x2="0.55" y2="1">
     <stop offset="0%" stop-color="#5C6A75"/>
     <stop offset="52%" stop-color="#3B4650"/>
     <stop offset="100%" stop-color="#2C353D"/>
   </linearGradient>
   <linearGradient id="sheen%NS%" x1="0" y1="0" x2="1" y2="0.75">
     <stop offset="0%" stop-color="#FFFFFF" stop-opacity=".30"/>
     <stop offset="38%" stop-color="#FFFFFF" stop-opacity=".04"/>
     <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
   </linearGradient>
   <linearGradient id="lit%NS%" x1="0" y1="0" x2="0.3" y2="1">
     <stop offset="0%" stop-color="#F3D6A2"/>
     <stop offset="100%" stop-color="#C9975A"/>
   </linearGradient>
   <linearGradient id="entry%NS%" x1="0" y1="0" x2="0" y2="1">
     <stop offset="0%" stop-color="#4A555F"/>
     <stop offset="100%" stop-color="#6E7A84"/>
   </linearGradient>
 </defs>`;

/* --- the facade, split into parallax layers ------------------------------ */

function facadeLayers(units) {
  const g = ART;
  let sky = '', mass = '', fore = '';

  /* ---- sky ------------------------------------------------------------- */
  sky += `<rect x="-1800" y="-2400" width="5200" height="5400" fill="url(#sky%NS%)"/>`;
  sky += `<ellipse cx="1560" cy="200" rx="700" ry="470" fill="url(#haze%NS%)"/>`;
  sky += `<g class="clouds" fill="#FFFFFF" opacity=".40">
            <ellipse cx="330" cy="238" rx="196" ry="34"/><ellipse cx="432" cy="216" rx="122" ry="27"/>
            <ellipse cx="1250" cy="112" rx="238" ry="30"/><ellipse cx="1136" cy="96" rx="132" ry="23"/>
          </g>`;
  sky += `<g fill="#B4C1CD" opacity=".55">`;
  [[-420,140],[-250,210],[-70,168],[70,246],[1400,196],[1512,132],[1636,224],[1782,158],[1922,238],[2110,150]]
    .forEach(([x, h]) => { sky += `<rect x="${x}" y="${g.ground - h}" width="118" height="${h}"/>`; });
  sky += `</g>`;

  /* ---- ground ---------------------------------------------------------- */
  mass += `<rect x="-1800" y="${g.ground}" width="5200" height="2800" fill="${P.ground}"/>`;
  mass += `<rect x="-1800" y="${g.ground}" width="5200" height="150" fill="${P.paving}"/>`;
  for (let i = 0; i < 11; i++) {
    mass += `<rect x="${-600 + i * 260}" y="${g.ground + 8}" width="2" height="142" fill="${P.shade}" opacity=".35"/>`;
  }
  mass += `<ellipse cx="${g.midX + 130}" cy="${g.ground + 32}" rx="${(g.right - g.coreX) / 2 + 160}" ry="38" fill="${P.shade}" opacity=".6"/>`;

  /* ---- entrance / circulation core -------------------------------------- */
  mass += `<rect x="${g.coreX}" y="${g.coreTop}" width="${g.coreW}" height="${g.ground - g.coreTop}" fill="${P.wallLo}"/>`;
  mass += `<rect x="${g.coreX}" y="${g.coreTop}" width="14" height="${g.ground - g.coreTop}" fill="${P.wallHi}" opacity=".5"/>`;
  mass += `<rect x="${g.coreX + 26}" y="${g.coreTop + 26}" width="${g.coreW - 52}" height="${g.ground - g.coreTop - 130}" fill="url(#glass%NS%)"/>`;
  mass += `<rect class="win-lit" data-lit=".05" x="${g.coreX + 26}" y="${g.coreTop + 26}" width="${g.coreW - 52}" height="${g.ground - g.coreTop - 130}" fill="url(#lit%NS%)" opacity="0"/>`;
  for (let f = 1; f <= 8; f++) {
    const y = g.ground - f * g.floorH;
    if (y < g.coreTop + 30) continue;
    mass += `<rect x="${g.coreX + 26}" y="${y - 3}" width="${g.coreW - 52}" height="5" fill="${P.wallHi}" opacity=".85"/>`;
  }
  mass += `<rect x="${g.coreX + 14}" y="${g.ground - 100}" width="${g.coreW - 28}" height="100" fill="url(#entry%NS%)"/>`;
  mass += `<rect class="win-lit" data-lit=".02" x="${g.coreX + 14}" y="${g.ground - 100}" width="${g.coreW - 28}" height="100" fill="url(#lit%NS%)" opacity="0"/>`;
  mass += `<rect x="${g.coreX + g.coreW / 2 - 1}" y="${g.ground - 100}" width="2" height="100" fill="${P.wallLo}"/>`;
  mass += `<rect x="${g.coreX - 30}" y="${g.ground - 112}" width="${g.coreW + 80}" height="12" fill="${P.wallHi}"/>`;
  mass += `<rect x="${g.coreX - 30}" y="${g.ground - 100}" width="${g.coreW + 80}" height="7" fill="${P.shade}" opacity=".45"/>`;

  /* ---- storeys ---------------------------------------------------------- */
  for (let f = 1; f <= 8; f++) {
    const row = units.filter(u => u.floor === f);
    if (!row.length) continue;
    const off = row[0].bayOffset, n = row[0].bays;
    const x = g.left + off * g.bayW, w = n * g.bayW;
    const y = g.ground - f * g.floorH;

    mass += `<g class="storey" data-floor="${f}">`;
    mass += `<rect x="${x}" y="${y}" width="${w}" height="${g.floorH}" fill="${P.wall}"/>`;
    mass += `<rect x="${x}" y="${y + 5}" width="${w}" height="${g.floorH - 13}" fill="${P.recess}"/>`;

    for (let i = 0; i <= n; i++) {
      const px = x + i * g.bayW - (i === 0 ? 0 : 6);
      mass += `<rect x="${px}" y="${y}" width="12" height="${g.floorH}" fill="${P.wallHi}"/>`;
      mass += `<rect x="${px + 12}" y="${y + 5}" width="4" height="${g.floorH - 13}" fill="${P.shade}" opacity=".5"/>`;
    }

    mass += `<rect x="${x - 10}" y="${y + g.floorH - 8}" width="${w + 20}" height="10" fill="${P.wallHi}"/>`;
    mass += `<rect x="${x - 10}" y="${y + g.floorH - 12}" width="${w + 20}" height="5" fill="${P.shade}" opacity=".4"/>`;

    /* the storey below is wider → its roof is a terrace */
    const below = units.filter(u => u.floor === f - 1);
    if (below.length && below[0].bays > n) {
      const bx = g.left + below[0].bayOffset * g.bayW, bw = below[0].bays * g.bayW;
      mass += `<rect x="${bx - 10}" y="${y + g.floorH - 8}" width="${bw + 20}" height="10" fill="${P.wallHi}"/>`;
      mass += `<rect x="${bx}" y="${y + g.floorH - 20}" width="${bw}" height="12" fill="${P.deck}"/>`;
      [[bx, x - bx], [x + w, bx + bw - x - w]].forEach(([tx, tw]) => {
        if (tw <= 2) return;
        mass += `<rect x="${tx}" y="${y + g.floorH - 54}" width="${tw}" height="34" fill="#FFFFFF" opacity=".32"/>`;
        mass += `<rect x="${tx}" y="${y + g.floorH - 56}" width="${tw}" height="3" fill="${P.rail}"/>`;
      });
    }

    /* glazing + balustrades for this storey */
    row.forEach(u => {
      const b = unitBox(u);
      const gx = b.x + 16, gw = b.w - 32;
      const gy = b.y + g.glassTop, gh = g.glassH;
      const sd = seed(u.id) / 100;

      mass += `<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" fill="url(#glass%NS%)"/>`;
      mass += `<rect class="win-lit" data-lit="${sd.toFixed(2)}" x="${gx}" y="${gy}" width="${gw}" height="${gh}" fill="url(#lit%NS%)" opacity="0"/>`;
      for (let m = 1; m <= 2; m++) {
        mass += `<rect x="${gx + (gw / 3) * m - 1.5}" y="${gy}" width="3" height="${gh}" fill="${P.wallHi}" opacity=".8"/>`;
      }
      mass += `<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" fill="url(#sheen%NS%)"/>`;
      mass += `<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" fill="none" stroke="#3A444E" stroke-width="2.5"/>`;

      const ry = gy + gh + 3;
      mass += `<rect x="${b.x + 12}" y="${ry}" width="${b.w - 24}" height="${g.railH}" fill="#FFFFFF" opacity=".38"/>`;
      mass += `<rect x="${b.x + 12}" y="${ry}" width="${b.w - 24}" height="2.5" fill="${P.rail}"/>`;
    });
    mass += `</g>`;
  }

  /* ---- roof ------------------------------------------------------------- */
  const topRow = units.filter(u => u.floor === 8)[0];
  const tx = g.left + topRow.bayOffset * g.bayW, tw = topRow.bays * g.bayW;
  mass += `<rect x="${tx - 12}" y="${g.top - 14}" width="${tw + 24}" height="16" fill="${P.wallHi}"/>`;
  mass += `<rect x="${tx - 12}" y="${g.top + 1}" width="${tw + 24}" height="5" fill="${P.shade}" opacity=".45"/>`;
  mass += `<rect x="${g.coreX - 6}" y="${g.coreTop - 12}" width="${g.coreW + 12}" height="14" fill="${P.wallHi}"/>`;

  /* ---- landscaping ------------------------------------------------------ */
  fore += `<rect x="${g.left - 6}" y="${g.ground - 32}" width="${g.right - g.left + 12}" height="32" rx="9" fill="${P.green}" opacity=".92"/>`;
  fore += `<rect x="${g.left - 6}" y="${g.ground - 32}" width="${g.right - g.left + 12}" height="8" rx="4" fill="#8A9779" opacity=".75"/>`;
  [[g.coreX - 158, 1.05], [g.coreX - 66, .8], [g.right + 66, .92], [g.right + 176, 1.12], [g.right + 280, .74]]
    .forEach(([x, k]) => {
      const h = 190 * k;
      fore += `<ellipse cx="${x + 14}" cy="${g.ground + 12}" rx="${44 * k}" ry="11" fill="${P.shade}" opacity=".5"/>`;
      fore += `<rect x="${x - 3}" y="${g.ground - h * .5}" width="6" height="${h * .5}" fill="${P.trunk}"/>`;
      fore += `<ellipse cx="${x}" cy="${g.ground - h * .72}" rx="${40 * k}" ry="${52 * k}" fill="${P.green}"/>`;
      fore += `<ellipse cx="${x - 12 * k}" cy="${g.ground - h * .82}" rx="${25 * k}" ry="${30 * k}" fill="#7E8C71" opacity=".85"/>`;
    });

  /* dusk warms the whole mass */
  const warm = `<rect class="warm-wash" x="-1800" y="-2400" width="5200" height="5400" fill="#8A5A2E" opacity="0" style="mix-blend-mode:multiply"/>`;

  return { sky, mass, fore, warm };
}

let nsCount = 0;

/** Paint the building into an <svg>, in parallax-ready layers.
 *  Gradient ids are namespaced per mount so two facades can coexist on a page
 *  (a shared id would make both read the first one's gradients). */
function mountFacade(svgEl, opts) {
  const o = opts || {};
  const ns = '-' + (o.ns || 'f' + (++nsCount));
  const L = facadeLayers(APARTMENTS);
  svgEl.innerHTML = (DEFS +
    `<g class="pl" data-depth="0.10">${L.sky}</g>` +
    `<g class="pl" data-depth="0.26">${L.mass}</g>` +
    `<g class="pl" data-depth="0.52">${L.fore}</g>` +
    (o.warm === false ? '' : L.warm)).replace(/%NS%/g, ns);
}

/* --- clickable overlay --------------------------------------------------- */

function mountHotspots(svgEl) {
  let s = '';
  APARTMENTS.forEach(u => {
    const b = unitBox(u);
    /* intro sweep runs bottom-up, left-to-right */
    const delay = (u.floor - 1) * 70 + u.bay * 26;
    s += `<rect class="unit" data-id="${u.id}" data-status="${u.status}" data-floor="${u.floor}"` +
         ` style="--d:${delay}ms"` +
         ` x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}"` +
         ` tabindex="0" role="link"` +
         ` aria-label="Byt ${u.id}, ${u.type}, ${fmtArea(u.area)} m², ${STATUS_LABEL[u.status]}"></rect>`;
  });
  for (let f = 1; f <= 8; f++) {
    s += `<text class="picker__floorlabel" data-floor="${f}" x="${ART.right + 30}"` +
         ` y="${ART.ground - f * ART.floorH + ART.floorH / 2 + 6}">${f}. podlažie</text>`;
  }
  svgEl.innerHTML = s;
}

/** Whole-storey highlight bands, used by the scrollytelling section. */
function mountFloorBands(svgEl) {
  let s = '';
  for (let f = 1; f <= 8; f++) {
    const b = floorBox(f);
    if (!b) continue;
    s += `<rect class="fband" data-floor="${f}" x="${b.x - 12}" y="${b.y - 2}" width="${b.w + 24}" height="${b.h + 2}"/>`;
  }
  /* the entrance level reads as "floor 0" */
  s += `<rect class="fband" data-floor="0" x="${ART.coreX - 34}" y="${ART.ground - 116}" width="${ART.coreW + 88}" height="116"/>`;
  svgEl.innerHTML = s;
}

/* --- time of day --------------------------------------------------------- */

const hex2rgb = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const rgb2hex = c => '#' + c.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
const mixHex = (a, b, t) => rgb2hex(hex2rgb(a).map((v, i) => v + (hex2rgb(b)[i] - v) * t));

/** t: 0 = dawn, ~0.38 = midday, ~0.72 = golden hour, 1 = dusk. */
function setSkyTime(root, t) {
  t = Math.min(1, Math.max(0, t));
  let a = SKY_KEYS[0], b = SKY_KEYS[SKY_KEYS.length - 1];
  for (let i = 0; i < SKY_KEYS.length - 1; i++) {
    if (t >= SKY_KEYS[i].at && t <= SKY_KEYS[i + 1].at) { a = SKY_KEYS[i]; b = SKY_KEYS[i + 1]; break; }
  }
  const k = b.at === a.at ? 0 : (t - a.at) / (b.at - a.at);

  root.querySelectorAll('[data-sky]').forEach(stop => {
    const i = +stop.dataset.sky;
    stop.setAttribute('stop-color', mixHex(a.stops[i], b.stops[i], k));
  });
  const haze = mixHex(a.haze, b.haze, k);
  const hazeO = a.hazeO + (b.hazeO - a.hazeO) * k;
  root.querySelectorAll('[data-haze]').forEach((stop, i) => {
    stop.setAttribute('stop-color', haze);
    if (i === 0) stop.setAttribute('stop-opacity', hazeO.toFixed(2));
  });

  const night = a.night + (b.night - a.night) * k;
  root.querySelectorAll('.win-lit').forEach(w => {
    const th = +w.dataset.lit;
    w.setAttribute('opacity', Math.min(1, Math.max(0, (night - th * 0.9) * 2.4)).toFixed(2));
  });
  const wash = root.querySelector('.warm-wash');
  if (wash) wash.setAttribute('opacity', (night * 0.16).toFixed(3));
  const clouds = root.querySelector('.clouds');
  if (clouds) clouds.setAttribute('opacity', (0.40 - night * 0.28).toFixed(2));
}

/* --- abstract elevation for the apartment detail page -------------------- */

function schematicSVG(activeId) {
  const g = ART, pad = 3;
  const x0 = g.left - 40, x1 = g.right + 40;
  const y0 = g.top - 30, y1 = g.ground + 44;
  let s = '';

  s += `<rect x="${g.coreX - 4}" y="${g.coreTop}" width="${g.coreW + 4}" height="${g.ground - g.coreTop}" rx="4" fill="#E3DCD1"/>`;
  s += `<text x="${g.coreX + g.coreW / 2}" y="${g.ground - 40}" text-anchor="middle" font-family="Inter,sans-serif" font-size="26" fill="#8A8079">vstup</text>`;

  APARTMENTS.forEach(u => {
    const b = unitBox(u);
    const on = u.id === activeId;
    s += `<a href="byt.html?id=${encodeURIComponent(u.id)}" class="mini__cell${on ? ' is-active' : ''}" data-status="${u.status}" aria-label="Byt ${u.id}, ${STATUS_LABEL[u.status]}">
            <rect x="${b.x + pad}" y="${b.y + pad}" width="${b.w - pad * 2}" height="${b.h - pad * 2}" rx="3"/>
            ${on ? `<text x="${b.x + b.w / 2}" y="${b.y + b.h / 2 + 11}" text-anchor="middle" font-family="Inter,sans-serif" font-weight="600" font-size="30">${u.id}</text>` : ''}
          </a>`;
  });

  for (let f = 1; f <= 8; f++) {
    s += `<text class="mini__floor" x="${g.right + 16}" y="${g.ground - f * g.floorH + g.floorH / 2 + 10}"
             font-family="Inter,sans-serif" font-size="26" fill="#8A8079">${f}</text>`;
  }
  s += `<rect x="${g.left - 20}" y="${g.ground}" width="${g.right - g.left + 40}" height="6" rx="3" fill="#C9C1B5"/>`;

  return `<svg viewBox="${x0} ${y0} ${x1 - x0} ${y1 - y0}" role="img"
            aria-label="Poloha bytu ${activeId} v dome">${s}</svg>`;
}

/* --- framing ------------------------------------------------------------- */

function frameViewBox(el, w, h, opts) {
  if (!w || !h) return;
  const o = opts || {};
  const r = w / h;
  const bw = ART.right - ART.coreX;
  const bh = ART.ground - ART.coreTop;

  /* Wide viewports: the mass sits right of centre so the headline gets clear
     sky on the left. Narrow viewports: centre it and zoom in as far as the
     width allows, so the storeys stay tappable. */
  const wide = o.centred ? false : w >= 900;
  const fill = o.fill || (wide ? 0.55 : 0.94);
  const vfill = o.vfill || (wide ? 0.62 : 0.70);

  const H = Math.max(bh / vfill, (bw / fill) / r);
  const W = H * r;
  const leftFrac = wide ? 0.38 : (1 - bw / W) / 2;
  const x = ART.coreX - leftFrac * W;
  const y = ART.ground + (o.base != null ? o.base : (wide ? 0.26 : 0.02)) * H - H;
  el.setAttribute('viewBox', `${x.toFixed(1)} ${y.toFixed(1)} ${W.toFixed(1)} ${H.toFixed(1)}`);
}

/* --- the hero selector --------------------------------------------------- */

function initPicker(root) {
  const visEl = root.querySelector('[data-facade]');
  const hotEl = root.querySelector('[data-hotspots]');
  const tip = root.querySelector('[data-tip]');
  if (!visEl || !hotEl) return;

  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  mountFacade(visEl);
  mountHotspots(hotEl);

  const size = () => {
    const r = root.getBoundingClientRect();
    frameViewBox(visEl, r.width, r.height);
    frameViewBox(hotEl, r.width, r.height);
  };
  size();
  if (window.ResizeObserver) new ResizeObserver(size).observe(root);
  else window.addEventListener('resize', size);

  const rects = [...hotEl.querySelectorAll('.unit')];
  const labels = [...hotEl.querySelectorAll('.picker__floorlabel')];
  const byId = Object.fromEntries(APARTMENTS.map(a => [a.id, a]));
  const isTouch = window.matchMedia('(hover: none)').matches;
  const sheet = window.matchMedia('(max-width: 899px)');

  /* one-off intro sweep so the affordance is obvious without instructions */
  if (!calm) {
    root.classList.add('is-intro');
    setTimeout(() => root.classList.remove('is-intro'), 3400);
  }

  function clear() {
    rects.forEach(r => r.classList.remove('is-hot', 'is-dim'));
    labels.forEach(l => l.classList.remove('is-on'));
    if (tip) tip.dataset.show = 'false';
    root.classList.remove('is-picking', 'is-legend');
  }

  function show(rect) {
    const a = byId[rect.dataset.id];
    if (!a) return;
    root.classList.remove('is-intro', 'is-legend');
    root.classList.add('is-picking');
    rects.forEach(r => {
      r.classList.toggle('is-hot', r === rect);
      r.classList.toggle('is-dim', r !== rect && r.dataset.floor !== rect.dataset.floor);
    });
    labels.forEach(l => l.classList.toggle('is-on', l.dataset.floor === rect.dataset.floor));
    if (!tip) return;

    tip.innerHTML =
      `<div class="tip__head">
         <span class="tip__id">${a.id}</span>
         <span class="pill pill--${a.status}">${STATUS_LABEL[a.status]}</span>
       </div>
       <div class="tip__type">${a.type} · ${a.floor}. nadzemné podlažie</div>
       <dl class="tip__rows">
         <div class="tip__row"><dt>Interiér</dt><dd>${fmtArea(a.area)} m²</dd></div>
         <div class="tip__row"><dt>${a.extKind}</dt><dd>${fmtArea(a.ext)} m²</dd></div>
         <div class="tip__row"><dt>Orientácia</dt><dd>${a.orientation}</dd></div>
         <div class="tip__row"><dt>Cena</dt><dd>${fmtPrice(a.price, a.status)}</dd></div>
       </dl>
       <div class="tip__cta">${a.status === 'predany' ? 'Predané' : 'Kliknite pre detail bytu'}</div>
       <div class="tip__actions">
         ${a.status === 'predany'
           ? `<span class="btn btn--ghost" aria-disabled="true">Predané</span>`
           : `<a class="btn btn--primary" href="byt.html?id=${encodeURIComponent(a.id)}">Zobraziť detail</a>`}
         <button type="button" class="tip__close" data-tip-close aria-label="Zavrieť">
           <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
         </button>
       </div>`;

    const closeBtn = tip.querySelector('[data-tip-close]');
    if (closeBtn) closeBtn.addEventListener('click', clear);

    tip.dataset.show = 'true';
    if (sheet.matches) return;   // docked sheet: CSS handles placement

    const rb = rect.getBoundingClientRect();
    const rootB = root.getBoundingClientRect();
    const w = 268;
    let left = rb.left - rootB.left + rb.width / 2;
    left = Math.min(Math.max(left, w / 2 + 12), rootB.width - w / 2 - 12);
    tip.style.left = left + 'px';

    const h = tip.offsetHeight;
    const above = rb.top - rootB.top - 14;
    const below = above + rb.height + 28;
    tip.dataset.flip = String(above < h);
    tip.style.top = (above < h ? below : above - h) + 'px';
  }

  function open(rect) {
    const a = byId[rect.dataset.id];
    if (!a || a.status === 'predany') return;
    window.location.href = 'byt.html?id=' + encodeURIComponent(a.id);
  }

  rects.forEach(rect => {
    rect.addEventListener('mouseenter', () => { if (!isTouch) show(rect); });
    rect.addEventListener('focus', () => show(rect));
    rect.addEventListener('blur', clear);
    rect.addEventListener('click', e => {
      e.preventDefault();
      /* touch: show the sheet and let its button do the navigating, so a
         mis-tap on a ~28px hotspot costs one tap instead of a wrong page */
      if (isTouch) { show(rect); return; }
      open(rect);
    });
    rect.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(rect); }
    });
  });

  hotEl.addEventListener('mouseleave', () => { if (!isTouch) clear(); });
  document.addEventListener('click', e => {
    if (isTouch && !hotEl.contains(e.target) && !(tip && tip.contains(e.target))) clear();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') clear(); });

  /* hovering a legend entry lights up every unit with that status */
  document.querySelectorAll('[data-legend]').forEach(item => {
    const status = item.dataset.legend;
    const on = () => {
      root.classList.remove('is-intro');
      root.classList.add('is-picking', 'is-legend');
      rects.forEach(r => {
        r.classList.toggle('is-hot', r.dataset.status === status);
        r.classList.toggle('is-dim', r.dataset.status !== status);
      });
    };
    item.addEventListener('mouseenter', () => { if (!isTouch) on(); });
    item.addEventListener('focus', on);
    item.addEventListener('mouseleave', () => { if (!isTouch) clear(); });
    item.addEventListener('blur', () => { if (!isTouch) clear(); });
    /* hover does nothing on a phone, so make the legend a tap filter */
    item.addEventListener('click', () => {
      const already = root.classList.contains('is-legend') && item.dataset.on === 'true';
      document.querySelectorAll('[data-legend]').forEach(o => { o.dataset.on = 'false'; });
      if (already) { clear(); return; }
      on();
      item.dataset.on = 'true';
    });
  });

  /* No pointer parallax here on purpose — drifting the building under the
     cursor read as wobble rather than depth. The `.pl` layer groups are still
     emitted by mountFacade() if it is ever wanted back. */

  /* floor strip — the dependable way in on small screens */
  const strip = root.parentElement.querySelector('[data-floorstrip]');
  if (strip) {
    strip.innerHTML = [8, 7, 6, 5, 4, 3, 2, 1].map(f => {
      const free = APARTMENTS.filter(a => a.floor === f && a.status === 'dostupny').length;
      return `<a class="floorstrip__row" href="byty.html?floor=${f}">
                <span class="floorstrip__no">${f}. NP</span>
                <span class="floorstrip__free">${free} ${plural(free, 'voľný', 'voľné', 'voľných')}</span>
              </a>`;
    }).join('');
  }
}
