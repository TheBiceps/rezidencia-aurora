/* ---------------------------------------------------------------------------
 * P6 — "Vyberte si byt priamo v dome"
 *
 * The investor's exterior visualisation of P6 with every apartment storey as a
 * hit band. Hovering a storey paints it in brand copper and shows how many flats
 * it holds and how many are free, reserved and sold; clicking lists them.
 *
 * WHERE THE BANDS COME FROM
 * Measured on the 2560x1440 image (assets/img/p6-dom-2560.webp) against the
 * bottom edge of each balcony slab, which is where one storey visibly ends and
 * the next begins. The top storey runs up to the roof edge; the roof terrace
 * above it is not a storey with flats. Ground floor = 1. NP, so the picture has
 * exactly the five storeys BUILDING.floors says.
 *
 * The coordinates are in image pixels and the image sits inside the same SVG
 * as the bands, so any crop of the viewBox moves both together. A new picture
 * means re-measuring these numbers.
 *
 * Counts are read from APARTMENTS at load: change a status in data.js and the
 * card follows.
 * ------------------------------------------------------------------------ */

const DOM_IMG = { w: 2560, h: 1440 };
const DOM_X = [546, 2110];                  // facade, left and right edge
const DOM_FLOORS = {                         // storey -> [top, bottom]
  5: [184, 362],
  4: [362, 508],
  3: [508, 658],
  2: [658, 808],
  1: [808, 988],
};
/* phones: frame the building rather than the street, so a storey is a
   thumb-sized band instead of a 20px sliver */
const DOM_VIEW = { wide: `0 0 ${DOM_IMG.w} ${DOM_IMG.h}`, narrow: '500 130 1660 900' };

function floorCounts(f) {
  const on = APARTMENTS.filter(a => a.floor === f);
  const n = s => on.filter(a => a.status === s).length;
  return { total: on.length, free: n('dostupny'), reserved: n('rezervovany'), sold: n('predany') };
}

function initFloors() {
  const root = document.querySelector('[data-bldg]');
  if (!root) return;
  const svg = root.querySelector('svg');
  const img = root.querySelector('[data-bldg-img]');
  const layer = root.querySelector('[data-floors]');
  const tip = root.querySelector('[data-tip]');
  if (!svg || !layer) return;

  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouch = window.matchMedia('(hover: none)').matches;
  const narrow = window.matchMedia('(max-width: 899px)');

  /* --- storeys --------------------------------------------------------- */
  const [x0, x1] = DOM_X;
  layer.innerHTML = Object.entries(DOM_FLOORS).map(([f, [top, bottom]]) => {
    const c = floorCounts(Number(f));
    const label = `${f}. nadzemné podlažie: ${c.total} ${plural(c.total, 'byt', 'byty', 'bytov')}, `
      + `voľné ${c.free}, rezervované ${c.reserved}, predané ${c.sold}`;
    return `<a class="bldg__floor" href="byty.html?floor=${f}" data-floor="${f}" aria-label="${label}">
              <rect x="${x0}" y="${top}" width="${x1 - x0}" height="${bottom - top}"/>
              <g class="bldg__tag" transform="translate(${x1 - 18} ${(top + bottom) / 2})">
                <rect x="-108" y="-27" width="108" height="54" rx="4"/>
                <text x="-54" y="10">${f}. NP</text>
              </g>
            </a>`;
  }).join('');
  const floors = [...layer.querySelectorAll('.bldg__floor')];

  /* --- framing ---------------------------------------------------------- */
  const frame = () => svg.setAttribute('viewBox', narrow.matches ? DOM_VIEW.narrow : DOM_VIEW.wide);
  frame();
  if (narrow.addEventListener) narrow.addEventListener('change', frame);

  /* --- picture: the smallest file that is still sharp, fetched on approach */
  if (img) {
    const load = () => {
      const r = root.getBoundingClientRect();
      /* on phones the building is cropped in, so it is drawn larger than the
         box width suggests */
      const zoom = narrow.matches ? DOM_IMG.w / 1660 : 1;
      const need = r.width * zoom * Math.min(window.devicePixelRatio || 1, 2);
      const src = need > 1920 ? img.dataset.srcLg : need > 1280 ? img.dataset.srcMd : img.dataset.srcSm;
      /* decode first, then swap in: the SVG <image> then paints complete and
         the fade never starts on a half-loaded picture */
      const pre = new Image();
      pre.src = src;
      const ready = () => { img.setAttribute('href', src); root.classList.add('is-loaded'); };
      (pre.decode ? pre.decode() : Promise.reject()).then(ready, () => {
        pre.onload = ready;
        if (pre.complete) ready();
      });
    };
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(([e]) => {
        if (e.isIntersecting) { io.disconnect(); load(); }
      }, { rootMargin: '900px 0px' });
      io.observe(root);
    } else load();
  }

  /* --- card ------------------------------------------------------------- */
  /* touch: the storey the first tap opened. Kept apart from .is-hot, because a
     tap focuses the link before it clicks, and focus alone lights the storey */
  let armed = null;

  function clear() {
    armed = null;
    floors.forEach(el => el.classList.remove('is-hot'));
    root.classList.remove('is-picking');
    if (tip) tip.dataset.show = 'false';
  }

  function show(el, pointerX) {
    const f = Number(el.dataset.floor);
    const c = floorCounts(f);
    root.classList.remove('is-intro');
    root.classList.add('is-picking');
    floors.forEach(o => o.classList.toggle('is-hot', o === el));
    if (!tip) return;

    const pct = n => (c.total ? (n / c.total) * 100 : 0).toFixed(2);
    tip.innerHTML = `
      <div class="tip__head">
        <span class="tip__id">${f}. NP</span>
        <span class="tip__type">nadzemné podlažie</span>
      </div>
      <dl class="tip__rows">
        <div class="tip__row tip__row--total"><dt>Bytov na podlaží</dt><dd>${c.total}</dd></div>
        <div class="tip__bar" aria-hidden="true">
          <span class="tip__bar--ok" style="width:${pct(c.free)}%"></span>
          <span class="tip__bar--warn" style="width:${pct(c.reserved)}%"></span>
          <span class="tip__bar--off" style="width:${pct(c.sold)}%"></span>
        </div>
        <div class="tip__row"><dt><i class="legend__dot legend__dot--ok"></i>Voľné</dt><dd>${c.free}</dd></div>
        <div class="tip__row"><dt><i class="legend__dot legend__dot--warn"></i>Rezervované</dt><dd>${c.reserved}</dd></div>
        <div class="tip__row"><dt><i class="legend__dot legend__dot--off"></i>Predané</dt><dd>${c.sold}</dd></div>
      </dl>
      <div class="tip__cta">Kliknite a zobrazte byty</div>
      <div class="tip__actions">
        <a class="btn btn--primary" href="byty.html?floor=${f}">Zobraziť byty na ${f}. NP</a>
        <button type="button" class="tip__close" data-tip-close aria-label="Zavrieť">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </div>`;
    const close = tip.querySelector('[data-tip-close]');
    if (close) close.addEventListener('click', clear);
    tip.dataset.show = 'true';
    if (narrow.matches) return;               // docked bottom sheet: CSS places it

    /* beside the building if the street leaves room, over it if not; level
       with the storey either way */
    const rb = el.querySelector('rect').getBoundingClientRect();
    const box = root.getBoundingClientRect();
    const w = tip.offsetWidth, h = tip.offsetHeight, gap = 12;
    const leftRoom = rb.left - box.left;
    let x;
    if (leftRoom >= w + gap * 2) x = leftRoom - gap - w;
    else {
      const px = pointerX != null ? pointerX - box.left : rb.left - box.left + rb.width / 2;
      x = px - w / 2;
    }
    x = Math.min(Math.max(x, 12), box.width - w - 12);
    let y = rb.top - box.top + rb.height / 2 - h / 2;
    y = Math.min(Math.max(y, 12), box.height - h - 12);
    tip.style.left = `${x}px`;
    tip.style.top = `${y}px`;
  }

  floors.forEach(el => {
    el.addEventListener('mouseenter', e => { if (!isTouch) show(el, e.clientX); });
    el.addEventListener('focus', () => show(el));
    el.addEventListener('blur', () => { if (!isTouch) clear(); });
    el.addEventListener('click', e => {
      /* touch: the first tap shows the card, a second tap or its button goes on */
      if (isTouch && armed !== el) { e.preventDefault(); show(el); armed = el; }
    });
  });
  svg.addEventListener('mouseleave', () => { if (!isTouch) clear(); });
  document.addEventListener('click', e => {
    if (isTouch && !layer.contains(e.target) && !(tip && tip.contains(e.target))) clear();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') clear(); });

  /* --- one sweep up the building the first time it is seen, so nobody has to
     be told the storeys are live ----------------------------------------- */
  if (!calm && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      root.classList.add('is-intro');
      setTimeout(() => root.classList.remove('is-intro'), 2600);
    }, { threshold: 0.5 });
    io.observe(root);
  }

  /* --- floor chips: the dependable way in on small screens ---------------- */
  const strip = document.querySelector('[data-floorstrip]');
  if (strip) {
    strip.innerHTML = Object.keys(DOM_FLOORS).map(Number).sort((a, b) => b - a).map(f => {
      const { free } = floorCounts(f);
      return `<a class="floorstrip__row" href="byty.html?floor=${f}">
                <span class="floorstrip__no">${f}. NP</span>
                <span class="floorstrip__free">${free} ${plural(free, 'voľný', 'voľné', 'voľných')}</span>
              </a>`;
    }).join('');
  }
}

document.addEventListener('DOMContentLoaded', initFloors);
