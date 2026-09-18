/* ---------------------------------------------------------------------------
 * P6 — hero fly-by, driven by scroll
 *
 * The footage starts on the architect's own visualisation of P6 and pushes in
 * toward the planted balconies. Scrolling moves the camera; three short beats
 * of copy come and go over the top.
 *
 * WHY NOT JUST SEEK A <video>
 * That was the first version and it did not feel like scrolling the camera.
 * A seek is asynchronous and each one has to land before the next, so the
 * picture changed in visible steps and trailed the page. Measured on a real
 * scroll gesture it updated 25-37 times a second at best, from a clip that
 * only had 96 distinct frames to show.
 *
 * WHAT IT DOES INSTEAD
 * It fetches the MP4 whole and decodes the frames itself with WebCodecs, then
 * paints them into a canvas on every display refresh. Between two frames it
 * blends the pair by the exact scroll position, so the camera moves
 * continuously however slowly you scroll, and when the page comes to rest it
 * eases onto a real frame so a still never shows two frames at once.
 *
 * Decoding and painting run in a worker (fly-worker.js) on the canvas handed
 * over as an OffscreenCanvas; this thread only works out where the playhead
 * should be and posts it. On the main thread a keyframe group decoding
 * mid-scroll stalled the page for up to 250 ms, right under the reader's hand.
 *
 * Frames are decoded a keyframe group (12 frames) at a time, and only the
 * group under the playhead plus its two neighbours are kept as bitmaps: all
 * 192 frames at 1600px would be over a gigabyte of memory. The index next to
 * each MP4 (built by _build/fly/build_fly.py) holds the decoder config and the
 * byte range of every frame.
 *
 * FALLBACKS
 * No WebCodecs or OffscreenCanvas, an unsupported codec or a decoder error:
 * the same MP4 goes into the <video> and is seeked the old way. Reduced motion, Save-Data or no JS:
 * the section stays a normal one-screen hero on the render itself and the
 * footage is never requested.
 * ------------------------------------------------------------------------ */

function initFly() {
  const root = document.querySelector('[data-fly]');
  if (!root) return;

  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  if (calm || saveData) return;

  const media = root.querySelector('.fly__media');
  const canvas = root.querySelector('[data-fly-canvas]');
  const video = root.querySelector('[data-fly-video]');
  const beats = [...root.querySelectorAll('[data-beat]')];
  const bar = root.querySelector('[data-fly-bar]');
  const cue = root.querySelector('.fly__cue');
  if (!media || !canvas) return;

  /* phones get a 4:5 crop of the flight: their stage is roughly that shape,
     and a 16:9 frame would be two-thirds cropped away anyway */
  const box = media.getBoundingClientRect();
  const tall = box.width / Math.max(1, box.height) < 1.1;
  const base = tall ? root.dataset.flyTall : root.dataset.flyWide;
  const ver = root.dataset.flyV ? `?v=${root.dataset.flyV}` : '';
  const SRC = { mp4: `${base}.mp4${ver}`, json: `${base}.json${ver}` };
  const FOCUS_Y = tall ? 0.48 : 0.42;       // matches the poster's object-position
  const FPS = 24;

  root.classList.add('is-live');

  /* beat windows as fractions of the scroll: [fade in start, fully in, start
     out, fully out]. The last beat never leaves: the section ends on it. */
  const WINDOWS = [
    [-1, 0, 0.20, 0.30],
    [0.34, 0.42, 0.58, 0.66],
    [0.72, 0.80, 2, 3],
  ];

  /* How long the camera takes to catch up with the scroll, in milliseconds.
     A wheel mouse moves the page in one jump per notch — about 114px, which is
     some 8 frames of footage — and without this the picture steps through them
     one frame at a time. Gliding turns each notch into a short camera move.
     Higher is smoother and lazier; lower is tighter and starts to step again.
     A trackpad never notices: its deltas are already smaller than the glide. */
  const GLIDE_MS = 95;

  let frames = 192;      // replaced by the index once it loads
  let shown = 0;         // displayed playhead, in frames, fractional
  let lastP = -1;
  let lastMove = -1e9;
  let lastNow = 0;
  let dir = 1;
  let running = false;
  let engine = null;

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

  function frame(now) {
    const dt = lastNow ? Math.min(64, now - lastNow) : 16.7;
    lastNow = now;

    const p = progress();
    if (p !== lastP) {
      if (lastP >= 0) { lastMove = now; dir = p > lastP ? 1 : -1; }
      lastP = p;
    }
    const exact = p * (frames - 1);
    /* while the page moves, follow it through the in-between positions; once
       it rests, settle on a whole frame */
    const settling = now - lastMove > 140;
    const goal = settling ? Math.round(exact) : exact;

    /* Frame-rate independent glide: the same feel at 60, 90 and 120 Hz. */
    shown += (goal - shown) * (1 - Math.exp(-dt / GLIDE_MS));
    if (Math.abs(goal - shown) < 0.003) shown = goal;

    /* the copy and the bar ride the same glide as the camera, or a wheel notch
       would step them while the picture moves smoothly behind */
    const smooth = frames > 1 ? clamp01(shown / (frames - 1)) : p;

    if (engine) engine.show(shown, dir);
    paintBeats(smooth);
    if (bar) bar.style.transform = `scaleX(${smooth.toFixed(4)})`;
    if (cue) cue.classList.toggle('is-gone', smooth > 0.02);

    if (running) requestAnimationFrame(frame);
  }

  /* --- canvas size follows the stage, at up to 2x device pixels ----------
     The canvas is handed to the worker, so its size is a message, not a
     property; this thread keeps the last size for whenever the engine lands. */
  let size = { width: 0, height: 0 };
  function fit() {
    const r = media.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(r.width * dpr));
    const height = Math.max(1, Math.round(r.height * dpr));
    if (width === size.width && height === size.height) return;
    size = { width, height };
    if (engine) engine.resize(size);
  }

  /* --- the WebCodecs engine, in a worker ---------------------------------- */
  async function canvasEngine() {
    if (!('VideoDecoder' in window) || !('EncodedVideoChunk' in window)) {
      throw new Error('no WebCodecs');
    }
    if (typeof Worker !== 'function' || !canvas.transferControlToOffscreen) {
      throw new Error('no OffscreenCanvas worker');
    }
    const ok = r => { if (!r.ok) throw new Error(`${r.url} ${r.status}`); return r; };
    const [meta, buf] = await Promise.all([
      fetch(SRC.json).then(ok).then(r => r.json()),
      fetch(SRC.mp4).then(ok).then(r => r.arrayBuffer()),
    ]);
    const description = Uint8Array.from(atob(meta.description), c => c.charCodeAt(0));

    const worker = new Worker(`assets/js/fly-worker.js${ver}`);
    const off = canvas.transferControlToOffscreen();
    let live = true;
    const stop = () => { if (live) { live = false; worker.postMessage({ type: 'close' }); worker.terminate(); } };

    const started = new Promise((resolve, reject) => {
      worker.addEventListener('message', e => {
        if (e.data.type === 'ready') resolve(e.data.frames);
        else if (e.data.type === 'error') reject(new Error(e.data.message));
      });
      worker.addEventListener('error', e => reject(new Error(e.message || 'worker failed')));
      setTimeout(() => reject(new Error('decoder timed out')), 8000);
    });

    fit();
    worker.postMessage({ type: 'init', meta, description, buf, canvas: off, focusY: FOCUS_Y, ...size }, [buf, off]);

    let n;
    try { n = await started; } catch (err) { stop(); throw err; }

    worker.addEventListener('message', e => {
      /* a decoder that dies later must not leave a frozen picture */
      if (e.data.type === 'error' && live) fail(new Error(e.data.message));
      /* the frame on screen, for anything watching from the outside */
      else if (e.data.type === 'drew') canvas.dataset.frame = e.data.pos.toFixed(3);
    });

    root.classList.add('is-ready');
    return {
      frames: n,
      show(pos, dir) { if (live) worker.postMessage({ type: 'show', pos, dir }); },
      resize(next) { if (live) worker.postMessage({ type: 'resize', ...next }); },
      rest() { if (live) worker.postMessage({ type: 'rest' }); },
      destroy() { stop(); },
    };
  }

  /* --- the fallback: seek the same MP4 in a <video> ---------------------- */
  function videoEngine() {
    if (!video) return null;
    let ok = false;
    root.classList.add('is-video');
    video.src = SRC.mp4;
    video.preload = 'auto';
    video.addEventListener('loadeddata', () => { ok = true; root.classList.add('is-ready'); }, { once: true });
    /* iOS Safari will not paint seeked frames until the element has played once.
       It is muted and inline, so this is allowed; pause straight away. */
    video.addEventListener('loadedmetadata', () => {
      const go = video.play();
      if (go && go.then) go.then(() => video.pause()).catch(() => {});
    }, { once: true });
    video.load();
    return {
      frames: 192,
      show(pos) {
        if (!ok || video.seeking) return;
        const t = Math.min(pos / FPS, (video.duration || 8) - 0.02);
        if (Math.abs(video.currentTime - t) > 0.02) video.currentTime = t;
      },
      resize() {},
      rest() {},
      destroy() {},   // the <video> keeps whatever it has buffered
    };
  }

  function fail(err) {
    if (root.classList.contains('is-video')) return;
    console.warn('[fly] falling back to <video>:', err && err.message ? err.message : err);
    if (engine) engine.destroy();
    root.classList.remove('is-ready');
    engine = videoEngine();
  }

  /* only spend frames while the section is actually on screen */
  let restTimer = 0;
  const io = new IntersectionObserver(([e]) => {
    if (e.isIntersecting) {
      clearTimeout(restTimer);
      if (!running) { running = true; lastNow = 0; requestAnimationFrame(frame); }
    } else {
      running = false;
      restTimer = setTimeout(() => engine && engine.rest(), 2000);
    }
  }, { rootMargin: '100px 0px' });
  io.observe(root);

  fit();
  if ('ResizeObserver' in window) new ResizeObserver(fit).observe(media);
  else window.addEventListener('resize', fit);

  paintBeats(progress());

  canvasEngine()
    .then(e => { engine = e; frames = e.frames; e.resize(size); })
    .catch(fail);
}

document.addEventListener('DOMContentLoaded', initFly);
