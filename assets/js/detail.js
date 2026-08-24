/* ---------------------------------------------------------------------------
 * REZIDENCIA AURORA — single apartment page
 * Reads ?id=4.03 and renders from APARTMENTS.
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
function planSVG(a) {
  const W = 620, H = 430, pad = 7;
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
    const showArea = h >= 46;
    return `<g class="plan__room" data-room="${room.key}" tabindex="0" role="img"
              aria-label="${room.name}, ${room.area.toFixed(1)} m²"><title>${room.name} — ${room.area.toFixed(1)} m²</title>
      <rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${Math.max(w, 1).toFixed(1)}" height="${Math.max(h, 1).toFixed(1)}" rx="2" fill="#F7F4EF" stroke="#14120F" stroke-width="2"/>
      <text x="${(x + 12).toFixed(1)}" y="${(y + 24).toFixed(1)}" font-family="Inter, sans-serif" font-size="${size}" font-weight="500" fill="#14120F">${clip(room.name, w, size)}</text>
      ${showArea ? `<text x="${(x + 12).toFixed(1)}" y="${(y + 26 + size + 4).toFixed(1)}" font-family="Inter, sans-serif" font-size="${size - 1.5}" fill="#5C544A">${room.area.toFixed(1)} m²</text>` : ''}
    </g>`;
  }).join('');

  return `<svg viewBox="-6 -6 ${W + 12} ${H + 12}" role="img" aria-label="Orientačná schéma dispozície bytu ${a.id}">${body}</svg>`;
}

/* --- orientation compass -------------------------------------------------- */

const BEARING = {
  'Sever': 0, 'Severovýchod': 45, 'Východ': 90, 'Juhovýchod': 135,
  'Juh': 180, 'Juhozápad': 225, 'Západ': 270, 'Severozápad': 315,
};

function compassSVG(orientation) {
  const dirs = orientation.split('/').map(t => t.trim()).filter(t => t in BEARING);
  const R = 42;
  const needles = dirs.map(d => {
    const rad = ((BEARING[d] - 90) * Math.PI) / 180;
    return `<g transform="rotate(${BEARING[d]} 60 60)">
              <path d="M60 60 L53 30 L60 20 L67 30 Z" fill="#A98C64"/>
            </g>`;
  }).join('');
  const ticks = [0, 45, 90, 135, 180, 225, 270, 315].map(deg => {
    const major = deg % 90 === 0;
    return `<line x1="60" y1="${60 - R}" x2="60" y2="${60 - R + (major ? 7 : 4)}"
              transform="rotate(${deg} 60 60)" stroke="#C9C1B5" stroke-width="${major ? 2 : 1}"/>`;
  }).join('');
  const letters = [['S', 0], ['V', 90], ['J', 180], ['Z', 270]].map(([ch, deg]) => {
    const rad = ((deg - 90) * Math.PI) / 180;
    const r = R + 13;
    return `<text x="${(60 + Math.cos(rad) * r).toFixed(1)}" y="${(60 + Math.sin(rad) * r + 4).toFixed(1)}"
              text-anchor="middle" font-family="Inter,sans-serif" font-size="11" font-weight="600"
              fill="${dirs.some(d => BEARING[d] === deg) ? '#A98C64' : '#8A8079'}">${ch}</text>`;
  }).join('');
  return `<svg viewBox="0 0 120 120" role="img" aria-label="Orientácia bytu: ${orientation}">
    <circle cx="60" cy="60" r="${R}" fill="none" stroke="#E3DCD1" stroke-width="1.5"/>
    ${ticks}${needles}${letters}
    <circle cx="60" cy="60" r="3.5" fill="#14120F"/>
  </svg>`;
}

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

  document.title = `Byt ${a.id} — ${a.type}, ${fmtArea(a.area)} m² | Rezidencia Aurora`;
  const meta = document.querySelector('meta[name="description"]');
  if (meta) meta.setAttribute('content',
    `${a.type} č. ${a.id} na ${a.floor}. nadzemnom podlaží. Interiér ${fmtArea(a.area)} m², ${a.extKind.toLowerCase()} ${fmtArea(a.ext)} m², orientácia ${a.orientation}.`);

  root.querySelectorAll('[data-crumb]').forEach(el => { el.textContent = 'Byt ' + a.id; });

  root.querySelector('[data-head]').innerHTML = `
    <p class="eyebrow">Rezidencia Aurora · ${a.floor}. nadzemné podlažie</p>
    <div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:12px 22px">
      <h1 style="font-size:clamp(2.8rem,6.5vw,5rem)">Byt ${a.id}</h1>
      <span class="pill pill--${a.status}">${STATUS_LABEL[a.status]}</span>
    </div>
    <p class="lede" style="margin-top:14px">${a.type} · typológia ${a.layout} · orientácia ${a.orientation}</p>`;

  root.querySelector('[data-spec]').innerHTML = [
    ['Interiér', fmtArea(a.area), 'm²'],
    [a.extKind, fmtArea(a.ext), 'm²'],
    ['Celková plocha', fmtArea(a.total), 'm²'],
    ['Izby', a.rooms, ''],
    ['Podlažie', a.floor + '. NP', ''],
  ].map(([k, v, u]) =>
    `<div class="spec__item"><dt>${k}</dt><dd>${v}${u ? ` <small>${u}</small>` : ''}</dd></div>`).join('');

  root.querySelector('[data-plan]').innerHTML = planSVG(a);

  const rt = root.querySelector('[data-rooms]');
  rt.querySelector('tbody').innerHTML = a.roomList
    .map((r, i) => `<tr data-room="${i}" tabindex="0"><td>${r.name}</td><td>${r.area.toFixed(1)} m²</td></tr>`).join('');
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

  const comp = root.querySelector('[data-compass]');
  if (comp) comp.innerHTML = compassSVG(a.orientation);
  const ori = root.querySelector('[data-orientation]');
  if (ori) ori.textContent = a.orientation;

  /* hovering a room in the plan highlights its row in the table, and back */
  const planEl = root.querySelector('[data-plan]');
  const roomsBody = rt.querySelector('tbody');
  const mark = (key, on) => {
    root.querySelectorAll(`[data-room="${key}"]`).forEach(el => el.classList.toggle('is-on', on));
  };
  [planEl, roomsBody].forEach(scope => {
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

  /* ← / → walk through the building */
  document.addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
    if (e.key === 'ArrowLeft') location.href = 'byt.html?id=' + encodeURIComponent(prev.id);
    if (e.key === 'ArrowRight') location.href = 'byt.html?id=' + encodeURIComponent(next.id);
  });

  /* same layout type, still available */
  const similar = APARTMENTS.filter(x => x.layout === a.layout && x.id !== a.id && x.status === 'dostupny').slice(0, 4);
  const simWrap = root.querySelector('[data-similar]');
  if (similar.length) {
    simWrap.querySelector('[data-similar-cards]').innerHTML = similar.map(x => `
      <a class="card" href="byt.html?id=${encodeURIComponent(x.id)}" data-status="${x.status}">
        <div class="card__top">
          <div><div class="card__id">${x.id}</div><div class="card__type">${x.type} · ${x.floor}. NP</div></div>
          <span class="pill pill--${x.status}">${STATUS_LABEL[x.status]}</span>
        </div>
        <dl class="card__rows">
          <div class="card__row"><dt>Interiér</dt><dd>${fmtArea(x.area)} m²</dd></div>
          <div class="card__row"><dt>Cena</dt><dd class="card__price">${fmtPrice(x.price, x.status)}</dd></div>
        </dl>
      </a>`).join('');
  } else {
    simWrap.hidden = true;
  }
}
