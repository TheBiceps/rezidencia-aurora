/* ---------------------------------------------------------------------------
 * P6 — schematic floor plans
 * Shared by the unit list (thumbnails), the landing page and the detail page.
 * Placeholder until the real floor-plan drawings are delivered.
 * ------------------------------------------------------------------------ */

/** Squarified treemap — keeps every room close to square instead of
 *  degenerating into slivers. Bruls, Huizing & van Wijk, 2000. */
function squarify(values, x0, y0, w0, h0) {
  const out = [];
  let x = x0, y = y0, w = w0, h = h0;
  const total = values.reduce((a, b) => a + b, 0);
  const scale = (w * h) / total;

  const worst = (row, len) => {
    const sum = row.reduce((a, b) => a + b, 0) * scale;
    const mx = Math.max.apply(null, row) * scale;
    const mn = Math.min.apply(null, row) * scale;
    return Math.max((len * len * mx) / (sum * sum), (sum * sum) / (len * len * mn));
  };

  const place = (row, len, horiz) => {
    const thick = (row.reduce((a, b) => a + b, 0) * scale) / len;
    let off = 0;
    row.forEach(v => {
      const side = (v * scale) / thick;
      out.push(horiz ? { x: x + off, y, w: side, h: thick }
                     : { x, y: y + off, w: thick, h: side });
      off += side;
    });
    if (horiz) { y += thick; h -= thick; } else { x += thick; w -= thick; }
  };

  const rest = values.slice();
  let row = [];
  while (rest.length) {
    const horiz = w >= h;
    const len = horiz ? w : h;
    if (!row.length || worst(row.concat(rest[0]), len) <= worst(row, len)) {
      row.push(rest.shift());
    } else {
      place(row, len, horiz);
      row = [];
    }
  }
  if (row.length) place(row, w >= h ? w : h, w >= h);
  return out;
}

/** Schematic plan of one apartment — placeholder until the real
 *  floor-plan drawings are delivered. */
function planSVG(a, opts) {
  const o = opts || {};
  /* On a phone the plan is only ~300px wide, so a 620x430 landscape box
     shrinks the labels to ~7px. A taller, narrower box keeps them readable.
     `compact` draws an unlabelled thumbnail for listing cards. */
  const narrow = !o.compact && window.matchMedia('(max-width: 899px)').matches;
  const W = o.compact ? 320 : (narrow ? 420 : 620);
  const H = o.compact ? 200 : (narrow ? 520 : 430);
  const pad = o.compact ? 5 : 7;
  const rooms = a.roomList.map((r, i) => ({ ...r, key: i }))
    .sort((r1, r2) => r2.area - r1.area);
  const cells = squarify(rooms.map(r => r.area), 0, 0, W, H);

  const clip = (text, width, size) => {
    const max = Math.max(3, Math.floor((width - 20) / (size * 0.55)));
    return text.length > max ? text.slice(0, max - 1).trim() + '…' : text;
  };

  const body = cells.map((c, i) => {
    const room = rooms[i];
    const x = c.x + pad / 2, y = c.y + pad / 2, w = c.w - pad, h = c.h - pad;
    const size = (h < 56 || w < 96) ? 13 : 15.5;
    /* a sliver of a room has no space for the m² line — the name is enough */
    const showArea = h >= 46 && w >= 72;
    if (o.compact) {
      return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${Math.max(w, 1).toFixed(1)}" height="${Math.max(h, 1).toFixed(1)}" rx="1.5" fill="#F7F4EF" stroke="#14120F" stroke-width="1.6"/>`;
    }
    return `<g class="plan__room" data-room="${room.key}" tabindex="0" role="img"
              aria-label="${room.name}, ${room.area.toFixed(1)} m²"><title>${room.name} — ${room.area.toFixed(1)} m²</title>
      <rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${Math.max(w, 1).toFixed(1)}" height="${Math.max(h, 1).toFixed(1)}" rx="2" fill="#F7F4EF" stroke="#14120F" stroke-width="2"/>
      <text x="${(x + 12).toFixed(1)}" y="${(y + 24).toFixed(1)}" font-family="Inter, sans-serif" font-size="${size}" font-weight="500" fill="#14120F">${clip(room.name, w, size)}</text>
      ${showArea ? `<text x="${(x + 12).toFixed(1)}" y="${(y + 26 + size + 4).toFixed(1)}" font-family="Inter, sans-serif" font-size="${size - 1.5}" fill="#5C544A">${room.area.toFixed(1)} m²</text>` : ''}
    </g>`;
  }).join('');

  return `<svg viewBox="-4 -4 ${W + 8} ${H + 8}" role="img" aria-label="Orientačná schéma dispozície bytu ${a.id}">${body}</svg>`;
}
