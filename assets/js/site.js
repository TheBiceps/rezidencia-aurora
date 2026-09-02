/* ---------------------------------------------------------------------------
 * P6 — shared helpers, navigation, page chrome
 * Load order:  data.js → site.js → motion.js → plan.js → (map.js | building.js | list.js | detail.js)
 * ------------------------------------------------------------------------ */

const STATUS_LABEL = {
  dostupny: 'Voľný',
  rezervovany: 'Rezervovaný',
  predany: 'Predaný',
};

const nfArea = new Intl.NumberFormat('sk-SK', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const nfPrice = new Intl.NumberFormat('sk-SK', { maximumFractionDigits: 0 });

const fmtArea = v => nfArea.format(v);

function fmtPrice(price, status) {
  if (status === 'predany') return '—';
  if (!SHOW_PRICES || price == null) return 'Na vyžiadanie';
  return nfPrice.format(price) + ' €';
}

/** Slovak 1 / 2-4 / 5+ plural. */
function plural(n, one, few, many) {
  if (n === 1) return one;
  if (n >= 2 && n <= 4) return few;
  return many;
}

const roomsLabel = n => n >= 5 ? 'Penthouse' : `${n}-izbový`;

const icon = {
  arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
  sort: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 15 6 6 6-6"/></svg>',
};

/* --- navigation ---------------------------------------------------------- */

function initNav() {
  const nav = document.querySelector('[data-nav]');
  if (!nav) return;
  const overHero = nav.dataset.nav === 'over';
  const sentinel = document.querySelector('[data-nav-sentinel]');

  const setState = solid => {
    nav.classList.toggle('nav--solid', solid);
    nav.classList.toggle('nav--over', overHero && !solid);
  };
  setState(!overHero);

  if (overHero && sentinel && 'IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => setState(!e.isIntersecting), { threshold: 0 }).observe(sentinel);
  } else if (overHero) {
    const onScroll = () => setState(window.scrollY > 80);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* mobile drawer */
  const drawer = document.querySelector('[data-drawer]');
  const openBtn = nav.querySelector('[data-drawer-open]');
  const closeBtn = drawer && drawer.querySelector('[data-drawer-close]');
  if (!drawer || !openBtn) return;

  const toggle = open => {
    drawer.dataset.open = String(open);
    drawer.setAttribute('aria-hidden', String(!open));
    openBtn.setAttribute('aria-expanded', String(open));
    document.body.dataset.locked = String(open);
    if (open) (drawer.querySelector('a, button') || drawer).focus();
    else openBtn.focus();
  };
  openBtn.addEventListener('click', () => toggle(true));
  closeBtn && closeBtn.addEventListener('click', () => toggle(false));
  drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => toggle(false)));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && drawer.dataset.open === 'true') toggle(false);
  });
}

/* --- contact / interest forms (front-end only for now) ------------------- */

function initForms() {
  document.querySelectorAll('[data-form]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      /* TODO: point this at the real endpoint (Formspree / API / CRM webhook). */
      const ok = form.querySelector('[data-form-ok]');
      form.querySelectorAll('input, textarea, select, button').forEach(el => { el.disabled = true; });
      if (ok) { ok.dataset.show = 'true'; ok.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
    });
  });
}

/* --- footer year --------------------------------------------------------- */

function initChrome() {
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
  const free = APARTMENTS.filter(a => a.status === 'dostupny').length;
  document.querySelectorAll('[data-count-free]').forEach(el => {
    el.textContent = free;
    el.dataset.countup = free;   // motion.js animates it into view
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initForms();
  initChrome();
  const picker = document.querySelector('[data-picker]');
  if (picker && typeof initPicker === 'function') initPicker(picker);
  if (typeof initList === 'function') initList();
  if (typeof initDetail === 'function') initDetail();
});
