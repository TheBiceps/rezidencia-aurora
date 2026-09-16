/* ---------------------------------------------------------------------------
 * P6 — hero fly-by, driven by scroll
 *
 * The footage starts on the architect's own visualisation of P6 and pushes in
 * toward the planted balconies. Scrolling scrubs through it while three short
 * beats of copy come and go over the top.
 *
 * WHY A VIDEO AND NOT A FRAME SEQUENCE
 * 96 frames as individual WebPs came to 7-12 MB, because every frame is
 * compressed on its own and moving foliage does not shrink. The same frames as
 * H.264 with a keyframe every 6 frames are 4.1 MB (1600px) and 1.6 MB (960px),
 * and the short keyframe interval keeps a seek to any point down to decoding
 * five frames at most.
 *
 * HOW THE SCRUB STAYS SMOOTH
 * The target time follows the scroll position, the displayed time eases toward
 * it, and a new seek is only issued once the previous one has landed. Setting
 * currentTime on every frame regardless makes seeks queue up and the picture
 * lag far behind the scroll.
 *
 * WHEN IT DOES NOT RUN
 * Reduced motion, Save-Data, or no JS: the section stays a normal one-screen
 * hero on the first frame, which is the render itself. The video is never
 * requested.
 * ------------------------------------------------------------------------ */

function initFly() {
  const root = document.querySelector('[data-fly]');
  if (!root) return;

  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  if (calm || saveData) return;

  const video = root.querySelector('[data-fly-video]');
  const beats = [...root.querySelectorAll('[data-beat]')];
  const bar = root.querySelector('[data-fly-bar]');
  const cue = root.querySelector('.fly__cue');
  if (!video) return;

  /* phones and small windows get the 960px encode: a 1600px frame is wasted on
     a 390px-wide stage, and it is two and a half times the download */
  const wantLg = window.innerWidth * Math.min(window.devicePixelRatio || 1, 2) > 1100;
  video.src = wantLg ? video.dataset.srcLg : video.dataset.srcSm;
  video.preload = 'auto';

  root.classList.add('is-live');

  /* beat windows as fractions of the scroll: [fade in start, fully in, start
     out, fully out]. The last beat never leaves: the section ends on it. */
  const WINDOWS = [
    [-1, 0, 0.20, 0.30],
    [0.34, 0.42, 0.58, 0.66],
    [0.72, 0.80, 2, 3],
  ];

  let duration = 8;
  let ready = false;
  let target = 0;        // where the scroll says we should be, in seconds
  let shown = 0;         // where the eased playhead is
  let running = false;

  const clamp01 = v => Math.max(0, Math.min(1, v));

  function progress() {
    const r = root.getBoundingClientRect();
    const travel = root.offsetHeight - window.innerHeight;
    return travel > 0 ? clamp01(-r.top / travel) : 0;
  }

  function paintBeats(p) {
    beats.forEach((b, i) => {
      const [a, b1, c, d] = WINDOWS[i] || WINDOWS[WINDOWS.length - 1];
      let o;
      if (p <= a) o = 0;
      else if (p < b1) o = (p - a) / (b1 - a);
      else if (p <= c) o = 1;
      else if (p < d) o = 1 - (p - c) / (d - c);
      else o = 0;
      /* ease, and a small rise as a beat arrives or leaves */
      const e = o * o * (3 - 2 * o);
      b.style.opacity = e.toFixed(3);
      b.style.transform = `translate3d(0, ${((1 - e) * 22).toFixed(1)}px, 0)`;
      /* an invisible beat must not keep its buttons in the tab order */
      const off = e < 0.02;
      if (b.classList.contains('is-on') === off) {
        b.classList.toggle('is-on', !off);
        if (off) b.setAttribute('aria-hidden', 'true'); else b.removeAttribute('aria-hidden');
      }
    });
  }

  function frame() {
    const p = progress();
    target = p * duration;
    shown += (target - shown) * 0.2;
    if (Math.abs(target - shown) < 0.004) shown = target;

    if (ready && !video.seeking && Math.abs(video.currentTime - shown) > 0.03) {
      video.currentTime = Math.min(shown, duration - 0.05);
    }
    paintBeats(p);
    if (bar) bar.style.transform = `scaleX(${p.toFixed(4)})`;
    if (cue) cue.classList.toggle('is-gone', p > 0.02);

    if (running) requestAnimationFrame(frame);
  }

  /* only spend frames while the section is actually on screen */
  const io = new IntersectionObserver(([e]) => {
    if (e.isIntersecting && !running) { running = true; requestAnimationFrame(frame); }
    else if (!e.isIntersecting) running = false;
  }, { rootMargin: '100px 0px' });
  io.observe(root);

  function markReady() {
    if (ready) return;
    ready = true;
    duration = Number.isFinite(video.duration) && video.duration > 0 ? video.duration : duration;
    video.currentTime = Math.min(shown, duration - 0.05);
    root.classList.add('is-ready');       // cross-fades the video over the poster
  }

  video.addEventListener('loadeddata', markReady, { once: true });
  video.addEventListener('error', () => {
    /* keep the poster and the beats; the scroll story still reads without motion */
    root.classList.remove('is-ready');
  });

  /* iOS Safari will not paint seeked frames until the element has played once.
     It is muted and inline, so this is allowed; pause straight away. */
  video.addEventListener('loadedmetadata', () => {
    const go = video.play();
    if (go && go.then) go.then(() => video.pause()).catch(() => {});
  }, { once: true });

  video.load();
  paintBeats(progress());
}

document.addEventListener('DOMContentLoaded', initFly);
