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
 * Frames are decoded a keyframe group (12 frames) at a time, and only the
 * group under the playhead plus its two neighbours are kept as bitmaps: all
 * 192 frames at 1600px would be over a gigabyte of memory. The index next to
 * each MP4 (built by _build/fly/build_fly.py) holds the decoder config and the
 * byte range of every frame.
 *
 * FALLBACKS
 * No WebCodecs, an unsupported codec or a decoder error: the same MP4 goes into
 * the <video> and is seeked the old way. Reduced motion, Save-Data or no JS:
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
    const goal = now - lastMove > 140 ? Math.round(exact) : exact;
    /* the same glide at 60 Hz and 120 Hz */
    shown += (goal - shown) * (1 - Math.pow(0.78, dt / 16.7));
    if (Math.abs(goal - shown) < 0.003) shown = goal;

    if (engine) engine.show(shown, dir);
    paintBeats(p);
    if (bar) bar.style.transform = `scaleX(${p.toFixed(4)})`;
    if (cue) cue.classList.toggle('is-gone', p > 0.02);

    if (running) requestAnimationFrame(frame);
  }

  /* --- canvas size follows the stage, at up to 2x device pixels ---------- */
  function fit() {
    const r = media.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(1, Math.round(r.width * dpr));
    const h = Math.max(1, Math.round(r.height * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      if (engine) engine.resize();
    }
  }

  /* --- the WebCodecs engine ---------------------------------------------- */
  async function canvasEngine() {
    if (!('VideoDecoder' in window) || !('EncodedVideoChunk' in window)) {
      throw new Error('no WebCodecs');
    }
    const ok = r => { if (!r.ok) throw new Error(`${r.url} ${r.status}`); return r; };
    const [meta, buf] = await Promise.all([
      fetch(SRC.json).then(ok).then(r => r.json()),
      fetch(SRC.mp4).then(ok).then(r => r.arrayBuffer()),
    ]);

    const description = Uint8Array.from(atob(meta.description), c => c.charCodeAt(0));
    const config = {
      codec: meta.codec, codedWidth: meta.width, codedHeight: meta.height,
      description, optimizeForLatency: true,
    };
    const support = await VideoDecoder.isConfigSupported(config);
    if (!support.supported) throw new Error(`${meta.codec} not supported`);

    const index = meta.frames;               // [byte offset, byte length, keyframe]
    const n = index.length;
    const usec = 1e6 / meta.fps;
    const keys = [];
    index.forEach((f, i) => { if (f[2]) keys.push(i); });
    const groupOf = i => {
      let lo = 0, hi = keys.length - 1;
      while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (keys[mid] <= i) lo = mid; else hi = mid - 1; }
      return lo;
    };
    const groupRange = g => [keys[g], g + 1 < keys.length ? keys[g + 1] : n];

    const ctx = canvas.getContext('2d', { alpha: false });
    const cache = new Map();                 // frame -> ImageBitmap
    const ready = new Set();                 // groups fully decoded into cache
    let pending = [];                        // bitmaps still being made
    let want = 0, wantDir = 1, busy = false, broken = null;
    let dirty = true, lastPos = -1, revealed = false;

    const decoder = new VideoDecoder({
      output: vf => {
        const i = Math.round(vf.timestamp / usec);
        pending.push(createImageBitmap(vf).then(bmp => {
          vf.close();
          const old = cache.get(i);
          if (old) old.close();
          cache.set(i, bmp);
          dirty = true;
        }, err => { vf.close(); throw err; }));
      },
      error: err => { broken = err; },
    });
    decoder.configure(config);

    async function decodeGroup(g) {
      const [a, b] = groupRange(g);
      pending = [];
      for (let i = a; i < b; i++) {
        const [pos, len, key] = index[i];
        decoder.decode(new EncodedVideoChunk({
          type: key ? 'key' : 'delta',
          timestamp: Math.round(i * usec),
          duration: Math.round(usec),
          data: new Uint8Array(buf, pos, len),
        }));
      }
      await decoder.flush();
      await Promise.all(pending);
      if (broken) throw broken;
      ready.add(g);
    }

    function drop(g) {
      const [a, b] = groupRange(g);
      for (let i = a; i < b; i++) {
        const bmp = cache.get(i);
        if (bmp) { bmp.close(); cache.delete(i); }
      }
      ready.delete(g);
    }

    /* the group under the playhead first, then the one it is heading into,
       then the one behind; everything else is let go before decoding more */
    async function pump() {
      if (busy || broken) return;
      busy = true;
      try {
        for (;;) {
          const keep = [want, want + wantDir, want - wantDir].filter(g => g >= 0 && g < keys.length);
          for (const g of [...ready]) if (!keep.includes(g)) drop(g);
          const next = keep.find(g => !ready.has(g));
          if (next === undefined) break;
          await decodeGroup(next);
        }
      } catch (err) {
        broken = broken || err;
      }
      busy = false;
      if (broken) fail(broken);
    }

    function nearest(i) {
      for (let d = 1; d < 24; d++) {
        if (cache.has(i - d)) return cache.get(i - d);
        if (cache.has(i + d)) return cache.get(i + d);
      }
      return null;
    }

    function cover(bmp, alpha) {
      const cw = canvas.width, ch = canvas.height;
      const s = Math.max(cw / bmp.width, ch / bmp.height);
      const dw = bmp.width * s, dh = bmp.height * s;
      ctx.globalAlpha = alpha;
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      ctx.drawImage(bmp, (cw - dw) * 0.5, (ch - dh) * FOCUS_Y, dw, dh);
    }

    /* the first group has to decode before this engine takes over, with a time
       limit: a decoder that never answers must not leave the hero frozen */
    const first = decodeGroup(0);
    first.catch(() => {});                   // the race below reports it
    await Promise.race([
      first,
      new Promise((_, reject) => setTimeout(() => reject(new Error('decoder timed out')), 8000)),
    ]).catch(err => { try { decoder.close(); } catch (e) { /* already closed */ } throw err; });

    return {
      frames: n,
      show(pos, heading) {
        const i0 = Math.max(0, Math.min(n - 1, Math.floor(pos)));
        const t = pos - i0;
        const i1 = Math.min(n - 1, i0 + 1);
        /* a blend partner across a group boundary is covered: the neighbours
           either side of the playhead's group are always kept */
        const g = groupOf(i0);
        if (g !== want || heading !== wantDir) { want = g; wantDir = heading; }
        if (!busy) pump();

        if (!dirty && Math.abs(pos - lastPos) < 0.0005) return;
        const b0 = cache.get(i0);
        const b1 = t > 0.004 ? cache.get(i1) : null;
        const baseBmp = b0 || nearest(i0);
        if (!baseBmp) return;
        cover(baseBmp, 1);
        if (b0 && b1) cover(b1, t);
        ctx.globalAlpha = 1;
        dirty = !b0 || (t > 0.004 && !b1);
        lastPos = pos;
        canvas.dataset.frame = b0 ? pos.toFixed(3) : `~${i0}`;
        if (!revealed) { revealed = true; root.classList.add('is-ready'); }
      },
      resize() { dirty = true; },
      /* off screen: hand back all but the group under the playhead */
      rest() { for (const g of [...ready]) if (g !== want) drop(g); },
      destroy() {
        try { decoder.close(); } catch (e) { /* already closed */ }
        cache.forEach(b => b.close());
        cache.clear();
        ready.clear();
      },
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
      destroy() {},
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
    .then(e => { engine = e; frames = e.frames; })
    .catch(fail);
}

document.addEventListener('DOMContentLoaded', initFly);
