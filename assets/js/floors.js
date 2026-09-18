/* ---------------------------------------------------------------------------
 * P6 — "Vyberte si byt priamo v dome"
 *
 * The investor's exterior visualisation of P6 with every apartment storey as a
 * hit band. Hovering a storey paints it in brand copper and shows how many flats
 * it holds and how many are free, reserved and sold.
 *
 * Clicking a storey dives into it: the camera pushes in on that band while the
 * architect's plan of the storey opens out of it, filling the stage. There every
 * flat lights up under the pointer with a card, and a click opens its page.
 * The plan and its outlines are the ones "Poloha v dome" uses (floorplan.js).
 * The floor view has its own history entry (#podlazie-3), so the browser's
 * back button returns to the building, and that address opens it directly.
 *
 * TWO SIDES
 * The house can be turned: the street facade (Prievozská, the north side) and
 * the courtyard facade behind it. One click turns it, and the storeys stay
 * live on whichever side is showing. Each side carries its own picture AND its
 * own band geometry, because the bands are measured in the pixels of that
 * picture; VIEWS below holds both. A side with no picture configured simply
 * does not exist and the turn button hides itself, which is what happens until
 * the investor's render of the second facade is in `assets/img/`.
 *
 * WHERE THE BANDS COME FROM
 * Measured on the picture itself (2560x1440) against the bottom edge of each
 * balcony slab, which is where one storey visibly ends and the next begins.
 * The top storey runs up to the roof edge; the roof terrace above it is not a
 * storey with flats. Ground floor = 1. NP, so the picture has exactly the five
 * storeys BUILDING.floors says.
 *
 * The coordinates are in image pixels and the image sits inside the same SVG
 * as the bands, so any crop of the viewBox moves both together. A NEW PICTURE
 * MEANS RE-MEASURING these numbers for that side.
 *
 * Counts are read from APARTMENTS at load: change a status in data.js and the
 * card follows.
 * ------------------------------------------------------------------------ */

const DOM_IMG = { w: 2560, h: 1440 };

/* Each side: the facade's left and right edge in image pixels, every storey as
   [top, bottom], and how the phone crop frames it (a storey has to stay a
   thumb-sized band rather than a 20px sliver). `slug` is the file stem in
   assets/img/, expected at 1280 / 1920 / 2560 px wide. */
const VIEWS = {
  front: {
    slug: 'p6-dom',
    label: 'Pohľad z Prievozskej',
    side: 'Uličná strana, sever',
    x: [546, 2110],
    floors: { 5: [184, 362], 4: [362, 508], 3: [508, 658], 2: [658, 808], 1: [808, 988] },
    narrow: '500 130 1660 900',
  },
  /* The courtyard render is not in yet. Fill in `slug` once the file is in
     assets/img/ AND re-measure x / floors on that picture: the camera sits
     somewhere else, so the old numbers do not carry over. */
  back: {
    slug: null,
    label: 'Pohľad z dvora',
    side: 'Dvorová strana, juh',
    x: [546, 2110],
    floors: { 5: [184, 362], 4: [362, 508], 3: [508, 658], 2: [658, 808], 1: [808, 988] },
    narrow: '500 130 1660 900',
  },
};
const VIEW_ORDER = ['front', 'back'];
/* the same five storeys whichever side is showing */
const STOREYS = Object.keys(VIEWS.front.floors).map(Number).sort((a, b) => a - b);

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

  /* --- the two sides ---------------------------------------------------- */
  const sides = VIEW_ORDER.filter(k => VIEWS[k].slug);
  let sideKey = sides[0] || 'front';
  const sideView = () => VIEWS[sideKey];
  const ver = root.dataset.bldgV ? `?v=${root.dataset.bldgV}` : '';
  const rotateBtn = root.querySelector('[data-bldg-rotate]');
  const sideLabel = root.querySelector('[data-bldg-side]');

  /* the file that is sharp enough for the box the picture is drawn in */
  function pickSrc(view) {
    const r = root.getBoundingClientRect();
    /* on phones the building is cropped in, so it is drawn larger than the
       box width suggests */
    const zoom = narrow.matches ? DOM_IMG.w / Number(view.narrow.split(' ')[2]) : 1;
    const need = r.width * zoom * Math.min(window.devicePixelRatio || 1, 2);
    const w = need > 1920 ? 2560 : need > 1280 ? 1920 : 1280;
    return `assets/img/${view.slug}-${w}.webp${ver}`;
  }

  /* --- storeys, rebuilt for whichever side is showing -------------------- */
  let floors = [];
  function buildBands() {
    const view = sideView();
    const [x0, x1] = view.x;
    layer.innerHTML = Object.entries(view.floors).map(([f, [top, bottom]]) => {
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
    floors = [...layer.querySelectorAll('.bldg__floor')];
    wireFloors();
  }

  /* --- framing ---------------------------------------------------------- */
  const frame = () => svg.setAttribute('viewBox',
    narrow.matches ? sideView().narrow : `0 0 ${DOM_IMG.w} ${DOM_IMG.h}`);
  if (narrow.addEventListener) narrow.addEventListener('change', () => { frame(); paint(); });

  /* --- picture: fetched on approach, decoded before it is shown ---------- */
  const loaded = new Set();
  function showPicture(view) {
    const src = pickSrc(view);
    if (loaded.has(src)) { img.setAttribute('href', src); root.classList.add('is-loaded'); return Promise.resolve(); }
    const pre = new Image();
    pre.src = src;
    const ready = () => { loaded.add(src); img.setAttribute('href', src); root.classList.add('is-loaded'); };
    return (pre.decode ? pre.decode() : Promise.reject())
      .then(ready, () => new Promise(res => {
        pre.onload = () => { ready(); res(); };
        pre.onerror = res;
        if (pre.complete) { ready(); res(); }
      }));
  }

  function paint() {
    frame();
    buildBands();
    if (sideLabel) sideLabel.textContent = sideView().side;
    if (rotateBtn) {
      const other = VIEWS[sides[(sides.indexOf(sideKey) + 1) % sides.length]];
      rotateBtn.hidden = sides.length < 2;
      if (other) rotateBtn.setAttribute('aria-label', `Otočiť dom: ${other.label}`);
    }
    return img ? showPicture(sideView()) : Promise.resolve();
  }

  if (img) {
    const start = () => paint();
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(([e]) => {
        if (e.isIntersecting) { io.disconnect(); start(); }
      }, { rootMargin: '900px 0px' });
      io.observe(root);
    } else start();
  } else paint();

  /* --- turning the house ------------------------------------------------ */
  let turning = false;
  async function rotate() {
    if (turning || sides.length < 2) return;
    turning = true;
    clear();
    const next = sides[(sides.indexOf(sideKey) + 1) % sides.length];
    /* have the other picture decoded before the turn starts, or the house
       comes back blank halfway through */
    const pre = new Image();
    pre.src = pickSrc(VIEWS[next]);
    await (pre.decode ? pre.decode().catch(() => {}) : Promise.resolve());

    const stage = svg;
    if (calm || !stage.animate) {
      sideKey = next; await paint(); turning = false; return;
    }
    root.classList.add('is-turning');
    const half = { duration: 320, easing: 'cubic-bezier(.45, 0, .55, 1)', fill: 'both' };
    await stage.animate([{ transform: 'perspective(1400px) rotateY(0deg)', opacity: 1 },
                         { transform: 'perspective(1400px) rotateY(-84deg)', opacity: .25 }], half).finished.catch(() => {});
    sideKey = next;
    await paint();
    stage.getAnimations().forEach(an => an.cancel());
    await stage.animate([{ transform: 'perspective(1400px) rotateY(84deg)', opacity: .25 },
                         { transform: 'perspective(1400px) rotateY(0deg)', opacity: 1 }],
                        { ...half, duration: 380 }).finished.catch(() => {});
    stage.getAnimations().forEach(an => an.cancel());
    root.classList.remove('is-turning');
    turning = false;
  }
  if (rotateBtn) rotateBtn.addEventListener('click', rotate);

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

  function showFloor(el, pointerX) {
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
      <div class="tip__cta">Kliknite a zobrazte pôdorys</div>
      <div class="tip__actions">
        <button type="button" class="btn btn--primary" data-open-floor="${f}">Pôdorys ${f}. NP</button>
        <button type="button" class="tip__close" data-tip-close aria-label="Zavrieť">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </div>`;
    const close = tip.querySelector('[data-tip-close]');
    if (close) close.addEventListener('click', clear);
    const go = tip.querySelector('[data-open-floor]');
    if (go) go.addEventListener('click', () => openFloor(f));
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

  function wireFloors() {
    floors.forEach(el => {
      el.addEventListener('mouseenter', e => { if (!isTouch) showFloor(el, e.clientX); });
      el.addEventListener('focus', () => showFloor(el));
      el.addEventListener('blur', () => { if (!isTouch) clear(); });
      el.addEventListener('click', e => {
        /* a new-tab click still gets the apartment list the link points at */
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        e.preventDefault();
        /* touch: the first tap shows the card, a second tap or its button goes on */
        if (isTouch && armed !== el) { showFloor(el); armed = el; return; }
        openFloor(Number(el.dataset.floor));
      });
    });
  }
  svg.addEventListener('mouseleave', () => { if (!isTouch) clear(); });
  document.addEventListener('click', e => {
    if (!isTouch) return;
    if (!layer.contains(e.target) && !(tip && tip.contains(e.target))) clear();
    if (current != null && !stage.contains(e.target) && !unitTip.contains(e.target)) hideUnit();
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (current == null) { clear(); return; }
    if (unitTip.dataset.show === 'true') hideUnit(); else closeFloor();
  });

  /* =======================================================================
     THE FLOOR VIEW
     ======================================================================= */
  const ease = 'cubic-bezier(.7, 0, .25, 1)';
  const settle = 'cubic-bezier(.2, .8, .2, 1)';
  const back = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>';
  const storeys = STOREYS;

  const view = document.createElement('div');
  view.className = 'fview';
  view.hidden = true;
  view.setAttribute('role', 'region');
  view.setAttribute('aria-label', 'Pôdorys podlažia');
  view.innerHTML = `
    <div class="fview__bar">
      <button type="button" class="fview__back" data-fview-back>${back}<span>Späť na dom</span></button>
      <div class="fview__title" aria-live="polite">
        <span class="fview__no" data-fview-no></span>
        <span class="fview__meta" data-fview-meta></span>
      </div>
      <div class="fview__floors" role="group" aria-label="Prepnúť podlažie">
        ${storeys.map(f => `<button type="button" class="fview__chip" data-fview-floor="${f}">${f}. NP</button>`).join('')}
      </div>
    </div>
    <div class="fview__stage" data-fview-stage></div>
    <div class="tip tip--unit" data-unit-tip data-show="false" role="status" aria-live="polite"></div>`;
  root.appendChild(view);

  const stage = view.querySelector('[data-fview-stage]');
  const unitTip = view.querySelector('[data-unit-tip]');
  const chips = [...view.querySelectorAll('[data-fview-floor]')];
  let current = null;        // storey on show, or null on the building
  let busy = false;          // a transition is running
  let pushed = false;        // this page added the #podlazie history entry

  const bandOf = f => layer.querySelector(`.bldg__floor[data-floor="${f}"]`);
  const hint = document.querySelector('[data-bldg-hint]');
  const hintText = on => { if (hint) hint.textContent = on ? 'Vyberte byt priamo v pôdoryse' : 'Vyberte podlažie priamo na dome'; };

  /* keyboard users get focus handed back to the storey they came from; for a
     pointer that would pop the storey's card up again the moment they return */
  let viaKeyboard = false;
  document.addEventListener('keydown', () => { viaKeyboard = true; }, true);
  document.addEventListener('pointerdown', () => { viaKeyboard = false; }, true);

  function renderFloor(f) {
    const c = floorCounts(f);
    view.querySelector('[data-fview-no]').textContent = `${f}. NP`;
    view.querySelector('[data-fview-meta]').textContent =
      `${c.total} ${plural(c.total, 'byt', 'byty', 'bytov')} · ${c.free} ${plural(c.free, 'voľný', 'voľné', 'voľných')}`;
    chips.forEach(ch => {
      const on = Number(ch.dataset.fviewFloor) === f;
      ch.classList.toggle('is-on', on);
      ch.setAttribute('aria-pressed', String(on));
    });
    hideUnit();
    stage.innerHTML = floorPlanHTML(f, { titles: false });
  }

  /* The camera pushes in on the storey until its band nearly spans the stage;
     the plan then opens out of the band at that zoomed size. Returns the zoom,
     its origin (the band's centre) and the zoomed band as a clip-path inset. */
  function bandInset(f) {
    const box = root.getBoundingClientRect();
    const r = bandOf(f).querySelector('rect').getBoundingClientRect();
    const zoom = Math.min(3, (box.width * 0.96) / r.width);
    const cx = r.left - box.left + r.width / 2;
    const cy = r.top - box.top + r.height / 2;
    const w = r.width * zoom, h = r.height * zoom;
    const t = Math.max(0, cy - h / 2), b = Math.max(0, box.height - (cy + h / 2));
    const l = Math.max(0, cx - w / 2), rr = Math.max(0, box.width - (cx + w / 2));
    return {
      zoom,
      origin: `${cx}px ${cy}px`,
      clip: `inset(${t}px ${rr}px ${b}px ${l}px round 4px)`,
    };
  }

  const done = anims => Promise.all(anims.map(an => an.finished)).catch(() => {});
  const drop = el => el.getAnimations().forEach(an => an.cancel());

  async function openFloor(f, { animate = true, push = true } = {}) {
    if (busy || !STOREYS.includes(Number(f))) return;
    clear();

    if (current != null) {                   // already inside: swap storeys
      if (f === current) return;
      current = f;
      if (history.replaceState) history.replaceState({ p6floor: f }, '', `#podlazie-${f}`);
      if (calm || !stage.animate) { renderFloor(f); return; }
      busy = true;
      await done([stage.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 150, fill: 'forwards' })]);
      renderFloor(f);
      drop(stage);
      await done([stage.animate([{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }],
                                { duration: 320, easing: settle })]);
      busy = false;
      return;
    }

    current = f;
    renderFloor(f);
    hintText(true);
    if (push && history.pushState) { history.pushState({ p6floor: f }, '', `#podlazie-${f}`); pushed = true; }
    floors.forEach(o => o.classList.toggle('is-hot', o === bandOf(f)));

    const motion = animate && !calm && !!view.animate;
    if (!motion) {
      root.classList.add('is-floor');
      view.hidden = false;
      view.querySelector('[data-fview-back]').focus({ preventScroll: true });
      return;
    }

    busy = true;
    const g = bandInset(f);
    svg.style.transformOrigin = g.origin;

    if (narrow.matches) {
      /* phones: the plan needs more height than the picture has, so push in on
         the storey first, then let the plan take the page */
      await done([svg.animate([{ transform: 'scale(1)', opacity: 1 }, { transform: `scale(${g.zoom})`, opacity: 0 }],
                              { duration: 560, easing: ease, fill: 'forwards' })]);
      root.classList.add('is-floor');
      view.hidden = false;
      drop(svg);
      await done([view.animate([{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }],
                               { duration: 420, easing: settle })]);
      const top = root.getBoundingClientRect().top;
      const bar = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 64;
      if (top < bar || top > window.innerHeight * 0.35) window.scrollBy({ top: top - bar - 12, behavior: 'smooth' });
    } else {
      /* desktop, in two beats: the camera pushes in on the copper storey, then
         that storey opens out into its plan and fills the stage */
      root.classList.add('is-floor');
      view.hidden = false;
      const bar = view.querySelector('.fview__bar');
      await done([
        svg.animate([
          { transform: 'scale(1)', opacity: 1 },
          { transform: `scale(${g.zoom})`, opacity: 1, offset: .62 },
          { transform: `scale(${g.zoom * 1.06})`, opacity: 0 },
        ], { duration: 1150, easing: 'cubic-bezier(.45, 0, .2, 1)', fill: 'forwards' }),
        /* invisible while the camera is still moving: a delayed animation holds
           its first frame, and a visible band here reads as a hole in the house */
        view.animate([
          { clipPath: g.clip, opacity: 0 },
          { clipPath: g.clip, opacity: 1, offset: .14 },
          { clipPath: 'inset(0px 0px 0px 0px round 0px)', opacity: 1 },
        ], { duration: 820, delay: 560, easing: ease, fill: 'both' }),
        stage.animate([{ opacity: 0, transform: 'scale(1.04)' }, { opacity: 1, transform: 'none' }],
                      { duration: 620, delay: 600, easing: settle, fill: 'both' }),
        bar.animate([{ opacity: 0, transform: 'translateY(-10px)' }, { opacity: 1, transform: 'none' }],
                    { duration: 420, delay: 1050, easing: settle, fill: 'both' }),
      ]);
      /* clip-path left on the view would clip the fixed-position card too */
      drop(view); drop(stage); drop(bar);
      svg.style.visibility = 'hidden';
      drop(svg);
    }
    busy = false;
    view.querySelector('[data-fview-back]').focus({ preventScroll: true });
  }

  async function closeFloor({ animate = true, fromHistory = false } = {}) {
    if (current == null || busy) return;
    /* our own history entry: step back through it, and popstate lands here */
    if (!fromHistory && pushed && history.state && history.state.p6floor) { history.back(); return; }
    if (!fromHistory && location.hash.startsWith('#podlazie-') && history.replaceState) {
      history.replaceState(null, '', location.pathname + location.search + '#vyber-bytu');
    }

    const f = current;
    current = null;
    pushed = false;
    hideUnit();
    hintText(false);
    const motion = animate && !calm && !!view.animate;
    const finish = () => {
      view.hidden = true;
      root.classList.remove('is-floor');
      svg.style.visibility = '';
      [view, stage, svg].forEach(drop);
      clear();
      const band = bandOf(f);
      if (band && viaKeyboard) band.focus({ preventScroll: true });
    };
    if (!motion) { finish(); return; }

    busy = true;
    if (narrow.matches) {
      await done([view.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 220, fill: 'forwards' })]);
      view.hidden = true;
      root.classList.remove('is-floor');
      const g = bandInset(f);
      svg.style.transformOrigin = g.origin;
      drop(view);
      await done([svg.animate([{ transform: `scale(${g.zoom})`, opacity: 0 }, { transform: 'scale(1)', opacity: 1 }],
                              { duration: 520, easing: ease })]);
    } else {
      /* the plan folds back into its storey, then the camera pulls out */
      const g = bandInset(f);
      svg.style.transformOrigin = g.origin;
      svg.style.visibility = '';
      await done([
        stage.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 380, easing: 'ease-in', fill: 'both' }),
        view.animate([
          { clipPath: 'inset(0px 0px 0px 0px round 0px)', opacity: 1 },
          { clipPath: g.clip, opacity: 1, offset: .8 },
          { clipPath: g.clip, opacity: 0 },
        ], { duration: 700, easing: ease, fill: 'both' }),
        svg.animate([
          { transform: `scale(${g.zoom})`, opacity: 0 },
          { transform: `scale(${g.zoom})`, opacity: 1, offset: .3 },
          { transform: 'scale(1)', opacity: 1 },
        ], { duration: 1150, delay: 240, easing: 'cubic-bezier(.45, 0, .2, 1)', fill: 'both' }),
      ]);
    }
    busy = false;
    finish();
  }

  view.querySelector('[data-fview-back]').addEventListener('click', () => closeFloor());
  chips.forEach(ch => ch.addEventListener('click', () => openFloor(Number(ch.dataset.fviewFloor))));

  /* a typed or linked #podlazie-3 arrives as a fragment navigation with no state */
  const hashFloor = () => { const m = /^#podlazie-(\d)$/.exec(location.hash); return m && STOREYS.includes(Number(m[1])) ? Number(m[1]) : null; };
  window.addEventListener('popstate', e => {
    const f = (e.state && e.state.p6floor) || hashFloor();
    if (f) openFloor(f, { push: false });
    else if (current != null) closeFloor({ fromHistory: true });
  });

  /* --- flats on the plan ------------------------------------------------ */
  let hotUnit = null;
  let armedUnit = null;      // touch: the flat the first tap opened

  function hideUnit() {
    hotUnit = null;
    armedUnit = null;
    stage.querySelectorAll('.fplan__unit.is-hot').forEach(u => u.classList.remove('is-hot'));
    unitTip.dataset.show = 'false';
  }

  function showUnit(u) {
    if (u === hotUnit) return;
    const a = APARTMENTS.find(x => x.id === u.dataset.id);
    if (!a) return;
    hotUnit = u;
    stage.querySelectorAll('.fplan__unit').forEach(x => x.classList.toggle('is-hot', x === u));
    const href = `byt.html?id=${encodeURIComponent(a.id)}`;
    unitTip.innerHTML = `
      <div class="tip__head">
        <span class="tip__id">${a.id}</span>
        <span class="pill pill--${a.status}">${STATUS_LABEL[a.status]}</span>
      </div>
      <div class="tip__type">${a.type} · ${a.floor}. nadzemné podlažie</div>
      <dl class="tip__rows">
        <div class="tip__row"><dt>Interiér</dt><dd>${fmtArea(a.area)} m²</dd></div>
        <div class="tip__row"><dt>${a.extKind}</dt><dd>${fmtArea(a.ext)} m²</dd></div>
        <div class="tip__row tip__row--total"><dt>Spolu</dt><dd>${fmtArea(a.total)} m²</dd></div>
        <div class="tip__row"><dt>Cena</dt><dd>${a.status === 'predany' ? 'Predané' : fmtPrice(a.price, a.status)}</dd></div>
      </dl>
      <div class="tip__cta">Kliknite pre detail bytu</div>
      <div class="tip__actions">
        <a class="btn btn--primary" href="${href}">Detail bytu ${a.id}</a>
        <button type="button" class="tip__close" data-tip-close aria-label="Zavrieť">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </div>`;
    unitTip.querySelector('[data-tip-close]').addEventListener('click', hideUnit);
    unitTip.dataset.show = 'true';
    if (narrow.matches) return;

    /* above the flat, or below it when the plan's top edge is too close */
    const pr = u.querySelector('polygon').getBoundingClientRect();
    const box = root.getBoundingClientRect();
    const w = unitTip.offsetWidth, h = unitTip.offsetHeight, gap = 12;
    let x = pr.left - box.left + pr.width / 2 - w / 2;
    x = Math.min(Math.max(x, 12), box.width - w - 12);
    let y = pr.top - box.top - h - gap;
    if (y < 12) y = pr.bottom - box.top + gap;
    y = Math.min(Math.max(y, 12), box.height - h - 12);
    unitTip.style.left = `${x}px`;
    unitTip.style.top = `${y}px`;
  }

  stage.addEventListener('mouseover', e => {
    if (isTouch) return;
    const u = e.target.closest('.fplan__unit');
    if (u) showUnit(u); else hideUnit();
  });
  stage.addEventListener('mouseleave', () => { if (!isTouch) hideUnit(); });
  stage.addEventListener('focusin', e => { const u = e.target.closest('.fplan__unit'); if (u) showUnit(u); });
  stage.addEventListener('focusout', e => {
    if (!isTouch && !(e.relatedTarget && stage.contains(e.relatedTarget))) hideUnit();
  });
  stage.addEventListener('click', e => {
    const u = e.target.closest('.fplan__unit');
    if (!u) return;
    if (isTouch && armedUnit !== u) { e.preventDefault(); hotUnit = null; showUnit(u); armedUnit = u; }
  });

  /* arriving on #podlazie-3 opens that storey straight away */
  const deep = /^#podlazie-(\d)$/.exec(location.hash);
  if (deep && STOREYS.includes(Number(deep[1]))) {
    const f = Number(deep[1]);
    if (history.replaceState) history.replaceState({ p6floor: f }, '', location.hash);
    openFloor(f, { animate: false, push: false });
    /* once more after load: the hero's pictures and fonts move the section */
    const place = () => root.scrollIntoView({ block: 'center' });
    place();
    if (document.readyState !== 'complete') window.addEventListener('load', place, { once: true });
  }

  /* --- one sweep up the building the first time it is seen, so nobody has to
     be told the storeys are live ----------------------------------------- */
  if (!calm && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      if (current != null) return;
      root.classList.add('is-intro');
      setTimeout(() => root.classList.remove('is-intro'), 2600);
    }, { threshold: 0.5 });
    io.observe(root);
  }

  /* --- floor chips: the dependable way in on small screens ---------------- */
  const strip = document.querySelector('[data-floorstrip]');
  if (strip) {
    strip.innerHTML = STOREYS.slice().sort((a, b) => b - a).map(f => {
      const { free } = floorCounts(f);
      return `<a class="floorstrip__row" href="byty.html?floor=${f}">
                <span class="floorstrip__no">${f}. NP</span>
                <span class="floorstrip__free">${free} ${plural(free, 'voľný', 'voľné', 'voľných')}</span>
              </a>`;
    }).join('');
  }
}

document.addEventListener('DOMContentLoaded', initFloors);
