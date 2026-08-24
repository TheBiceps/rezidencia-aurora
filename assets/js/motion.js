/* ---------------------------------------------------------------------------
 * REZIDENCIA AURORA — motion layer
 *
 * Everything here is progressive enhancement: with JS off, or with
 * `prefers-reduced-motion: reduce`, the page is fully readable and every
 * revealed element is simply shown.
 * ------------------------------------------------------------------------ */

const CALM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp01 = v => Math.min(1, Math.max(0, v));
const easeOut = t => 1 - Math.pow(1 - t, 3);

/** One shared scroll loop — cheaper and jank-free versus a listener per effect. */
const onFrame = (() => {
  const jobs = [];
  let queued = false;
  const run = () => { queued = false; jobs.forEach(fn => fn()); };
  const kick = () => { if (!queued) { queued = true; requestAnimationFrame(run); } };
  window.addEventListener('scroll', kick, { passive: true });
  window.addEventListener('resize', kick, { passive: true });
  return fn => { jobs.push(fn); kick(); };
})();

/* --- reveal on enter ----------------------------------------------------- */

function initReveal() {
  const items = document.querySelectorAll('.reveal');
  if (!items.length) return;
  if (CALM || !('IntersectionObserver' in window)) {
    items.forEach(i => i.classList.add('is-in'));
    return;
  }
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const sibs = [...e.target.parentElement.children].filter(c => c.classList.contains('reveal'));
      e.target.style.transitionDelay = Math.min(sibs.indexOf(e.target), 6) * 80 + 'ms';
      e.target.classList.add('is-in');
      io.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -12% 0px' });
  items.forEach(i => io.observe(i));
}

/* --- numbers that count up when they scroll into view -------------------- */

function initCountUp() {
  const els = document.querySelectorAll('[data-countup]');
  if (!els.length) return;
  const paint = (el, v) => { el.textContent = new Intl.NumberFormat('sk-SK').format(Math.round(v)); };

  if (CALM || !('IntersectionObserver' in window)) {
    els.forEach(el => paint(el, +el.dataset.countup));
    return;
  }
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      const el = e.target, to = +el.dataset.countup, t0 = performance.now(), ms = 1100;
      const tick = now => {
        const p = clamp01((now - t0) / ms);
        paint(el, to * easeOut(p));
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      /* rAF is paused in background tabs — make sure the real number lands */
      setTimeout(() => paint(el, to), ms + 300);
    });
  }, { rootMargin: '0px' });
  els.forEach(el => { el.textContent = '0'; io.observe(el); });
}

/* --- hero: content lifts away, the building settles ---------------------- */

function initHeroScroll() {
  const hero = document.querySelector('.hero');
  if (!hero || CALM) return;
  const content = hero.querySelector('.hero__content');
  const vis = hero.querySelector('.hero__vis');
  if (!content || !vis) return;

  /* keep the scroll cue clear of the stats strip */
  const stats = hero.querySelector('.hero__stats');
  if (stats) {
    const setH = () => hero.style.setProperty('--stats-h', stats.offsetHeight + 'px');
    setH();
    if (window.ResizeObserver) new ResizeObserver(setH).observe(stats);
  }

  /* A transform on .hero__vis would make it the containing block for the
     unit sheet, which is position:fixed on phones. Desktop only. */
  const wide = window.matchMedia('(min-width: 900px)');

  onFrame(() => {
    const h = hero.offsetHeight;
    const p = clamp01(window.scrollY / Math.max(h * 0.85, 1));
    content.style.transform = `translate3d(0, ${(p * -54).toFixed(1)}px, 0)`;
    content.style.opacity = (1 - p * 1.25).toFixed(3);
    if (wide.matches) {
      vis.style.transform = `translate3d(0, ${(p * 40).toFixed(1)}px, 0) scale(${(1 + p * 0.05).toFixed(4)})`;
    } else if (vis.style.transform) {
      vis.style.transform = '';
    }
  });
}

/* --- cursor spotlight on tiles ------------------------------------------- */

function initSpotlight() {
  if (CALM || window.matchMedia('(hover: none)').matches) return;
  let el = null, x = 0, y = 0, raf = 0;
  const apply = () => {
    raf = 0;
    if (!el) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty('--mx', (((x - r.left) / r.width) * 100).toFixed(1) + '%');
    el.style.setProperty('--my', (((y - r.top) / r.height) * 100).toFixed(1) + '%');
  };
  document.addEventListener('pointermove', e => {
    const t = e.target.closest && e.target.closest('.card, .feature, .aside__box, .ph');
    if (!t) { el = null; return; }
    el = t; x = e.clientX; y = e.clientY;
    if (!raf) raf = requestAnimationFrame(apply);
  }, { passive: true });
}

/* --- FAQ: animate the disclosure height ---------------------------------- */

function initFaq() {
  document.querySelectorAll('.faq details').forEach(d => {
    const body = d.querySelector('.faq__body');
    if (!body) return;
    d.addEventListener('toggle', () => {
      /* close the siblings so only one answer is open at a time */
      if (!d.open) return;
      d.parentElement.querySelectorAll('details[open]').forEach(o => { if (o !== d) o.open = false; });
    });
  });
}

/* --- scrollytelling ------------------------------------------------------ */

function initScrolly() {
  document.querySelectorAll('[data-scrolly]').forEach(section => {
    const stage = section.querySelector('[data-stage]');
    const facade = section.querySelector('[data-scrolly-facade]');
    const bands = section.querySelector('[data-scrolly-bands]');
    const steps = [...section.querySelectorAll('[data-step]')];
    const timeEl = section.querySelector('[data-timelabel]');
    const progEl = section.querySelector('[data-progress]');
    const idxEl = section.querySelector('[data-stepno]');
    if (!facade || !steps.length) return;

    mountFacade(facade, { ns: 'scrolly' });
    mountFloorBands(bands);

    /* measure the graphic itself — the stage is taller than the picture */
    const graphic = section.querySelector('.scrolly__graphic');
    const frame = () => {
      const r = graphic.getBoundingClientRect();
      const o = { centred: true, fill: 0.90, vfill: 0.80, base: 0.10 };
      frameViewBox(facade, r.width, r.height, o);
      frameViewBox(bands, r.width, r.height, o);
    };
    frame();
    if (window.ResizeObserver) new ResizeObserver(frame).observe(graphic);

    const bandEls = [...bands.querySelectorAll('.fband')];
    const TIMES = ['Dopoludnia', 'Popoludní', 'Podvečer', 'Súmrak'];
    let active = -1;

    const setStep = i => {
      if (i === active) return;
      active = i;
      steps.forEach((s, n) => s.classList.toggle('is-on', n === i));
      const want = (steps[i].dataset.floors || '').split(',').map(v => v.trim()).filter(Boolean);
      const all = want.includes('all');
      bandEls.forEach(b => b.classList.toggle('is-on', all || want.includes(b.dataset.floor)));
      if (stage) stage.style.setProperty('--zoom', steps[i].dataset.zoom || '1');
      if (idxEl) idxEl.textContent = String(i + 1).padStart(2, '0');
    };

    const update = () => {
      const r = section.getBoundingClientRect();
      const span = Math.max(section.offsetHeight - window.innerHeight, 1);
      const p = clamp01(-r.top / span);

      if (!CALM) setSkyTime(facade, 0.20 + p * 0.80);
      if (progEl) progEl.style.transform = `scaleX(${p.toFixed(4)})`;
      if (timeEl) timeEl.textContent = TIMES[Math.min(TIMES.length - 1, Math.floor(p * TIMES.length))];

      const line = window.innerHeight * 0.58;
      let i = 0;
      steps.forEach((s, n) => { if (s.getBoundingClientRect().top < line) i = n; });
      setStep(i);
    };

    onFrame(update);
    update();
  });
}

/* --- section progress rail ----------------------------------------------- */

function initReadingBar() {
  const bar = document.querySelector('[data-readbar]');
  if (!bar) return;
  onFrame(() => {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.transform = `scaleX(${clamp01(window.scrollY / Math.max(h, 1)).toFixed(4)})`;
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initReveal();
  initCountUp();
  initHeroScroll();
  initSpotlight();
  initFaq();
  initScrolly();
  initReadingBar();
});
