/* ---------------------------------------------------------------------------
 * P6 — "Poloha v dome"
 *
 * The architect's rendered floor plan for the storey the apartment sits on,
 * with every apartment on that storey as a hit region: the one you are looking
 * at is highlighted, the others light up on hover and link to their own page.
 *
 * WHERE THE GEOMETRY COMES FROM
 * The outlines below are traced on the party walls, facade lines and balcony
 * bands detected in the source renders, and each is tied to a letter by the
 * apartment labels printed in the architect's PDFs (_build/plans/src/*.pdf) —
 * not by eye. E, F and G are near-identical one-room flats that no amount of
 * looking will tell apart; the PDF labels are what settle them. Left to right
 * along the courtyard side they run G, F, E.
 *
 * Coordinates are percentages of the cropped plan image, so they survive any
 * re-export at a different resolution — but NOT a different crop. The crop is
 * pinned in _build/plans/import_renders.py (FLOOR_CROP) for exactly that
 * reason; change it there and these numbers have to move with it.
 * ------------------------------------------------------------------------ */

/* 1.NP has no I — that corner of the building is the entrance lobby. */
const FLOOR_SHAPES = {
  '25': {
    A: '43.90,3.11 63.27,3.11 63.27,46.89 43.90,46.89',
    B: '63.27,3.11 83.14,3.11 83.14,46.89 63.27,46.89',
    C: '83.14,3.11 98.85,3.11 98.85,57.38 78.05,57.38 78.05,46.39 83.14,46.39',
    D: '69.94,57.38 98.85,57.38 98.85,96.89 69.94,96.89',
    E: '56.60,50.16 69.94,50.16 69.94,96.89 56.60,96.89',
    F: '43.19,50.16 56.60,50.16 56.60,96.89 43.19,96.89',
    G: '30.34,50.16 43.19,50.16 43.19,96.89 30.34,96.89',
    H: '1.08,50.16 30.34,50.16 30.34,96.89 1.08,96.89',
    I: '1.08,3.11 30.63,3.11 30.63,50.16 1.08,50.16',
  },
  '1': {
    A: '43.48,2.92 63.39,2.92 63.39,46.48 43.48,46.48',
    B: '63.39,2.92 83.43,2.92 83.43,46.48 63.39,46.48',
    C: '83.43,2.92 98.87,2.92 98.87,58.15 77.12,58.15 77.12,45.45 83.43,45.45',
    D: '70.04,58.15 98.58,58.15 98.58,96.74 70.04,96.74',
    E: '56.59,54.37 70.04,54.37 70.04,96.74 56.59,96.74',
    F: '43.20,54.37 56.59,54.37 56.59,96.74 43.20,96.74',
    G: '29.53,54.37 43.20,54.37 43.20,96.74 29.53,96.74',
    H: '0.99,2.92 30.31,2.92 30.31,58.15 0.99,58.15',
  },
};

/* the two plans are cropped to different boxes, so each carries its own ratio */
const FLOOR_IMG = {
  '1':  { src: 'assets/plans/floor-1np.webp',  w: 1412, h: 583,
          label: '1. nadzemné podlažie' },
  '25': { src: 'assets/plans/floor-25np.webp', w: 1394, h: 610,
          label: '2.–5. nadzemné podlažie' },
};

const floorKey = floor => (floor === 1 ? '1' : '25');

/* --- centroid, so the badge sits inside its own outline ------------------- */
function polyCentre(pts) {
  const p = pts.trim().split(/\s+/).map(s => s.split(',').map(Number));
  let a = 0, cx = 0, cy = 0;
  for (let i = 0; i < p.length; i++) {
    const [x0, y0] = p[i], [x1, y1] = p[(i + 1) % p.length];
    const f = x0 * y1 - x1 * y0;
    a += f; cx += (x0 + x1) * f; cy += (y0 + y1) * f;
  }
  /* a degenerate outline would divide by zero — fall back to the mean */
  if (Math.abs(a) < 1e-6) {
    return [p.reduce((s, q) => s + q[0], 0) / p.length,
            p.reduce((s, q) => s + q[1], 0) / p.length];
  }
  return [cx / (3 * a), cy / (3 * a)];
}

/**
 * Render the storey plan into `host` with `active` (an apartment id like "3.H")
 * highlighted. Every other apartment on the same storey becomes a link.
 */
function mountFloorPlan(host, active) {
  if (!host) return;
  const a = APARTMENTS.find(u => u.id === active);
  if (!a) return;

  const key = floorKey(a.floor);
  const img = FLOOR_IMG[key];
  const shapes = FLOOR_SHAPES[key];
  if (!img || !shapes) return;

  const onFloor = APARTMENTS.filter(u => u.floor === a.floor);

  const cell = u => {
    const pts = shapes[u.letter];
    if (!pts) return '';
    const on = u.id === a.id;
    const [cx, cy] = polyCentre(pts);
    const title = `Byt ${u.id} · ${u.type} · ${fmtArea(u.area)} m²`
                + (on ? ' · tento byt' : ` · ${STATUS_LABEL[u.status]}`);
    /* the active flat is not a link — you are already on its page */
    const tag = on ? 'g' : 'a';
    const href = on ? '' : ` href="byt.html?id=${encodeURIComponent(u.id)}"`;
    return `<${tag}${href} class="fplan__unit${on ? ' is-active' : ''}"
              data-status="${u.status}" data-id="${u.id}"
              ${on ? 'aria-current="page"' : ''} aria-label="${title}">
              <title>${title}</title>
              <polygon points="${pts}"/>
              <g class="fplan__tag" transform="translate(${cx} ${cy})">
                <rect x="-7.2" y="-4.4" width="14.4" height="8.8" rx="4.4"/>
                <text y="2.1">${u.letter}</text>
              </g>
            </${tag}>`;
  };

  /* the overlay is positioned against __frame, not against the figure: the
     figure also holds the caption, and stretching the map over that would
     shear every outline downwards */
  host.innerHTML = `
    <figure class="fplan">
      <div class="fplan__scroll">
       <div class="fplan__frame">
        <img class="fplan__img" src="${img.src}" width="${img.w}" height="${img.h}"
             alt="Pôdorys ${a.floor}. nadzemného podlažia, byt ${a.id} je zvýraznený"
             loading="lazy" decoding="async">
        <svg class="fplan__map" viewBox="0 0 100 100" preserveAspectRatio="none"
             role="group" aria-label="Byty na ${a.floor}. nadzemnom podlaží">
          ${onFloor.map(cell).join('')}
        </svg>
       </div>
      </div>
      <figcaption class="fplan__cap">${img.label}${a.floor === 1
        ? '' : ' · pôdorys je zhodný pre 2.–5. NP'}</figcaption>
    </figure>`;
}
