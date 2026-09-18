/* ---------------------------------------------------------------------------
 * P6 — hero fly-by: the decoder, off the main thread
 *
 * fly.js hands this worker the MP4, its frame index and the hero's canvas
 * (transferred as an OffscreenCanvas), then posts the playhead once per display
 * refresh. Everything expensive — decoding H.264, turning frames into bitmaps,
 * painting them — happens here, so none of it can hold up scrolling.
 *
 * That is the whole point of the worker: on the main thread a keyframe group
 * decoding mid-scroll stalled the page for up to 250 ms, which is exactly the
 * moment the reader is dragging the wheel.
 *
 * Messages in:  init | show | resize | rest | close
 * Messages out: ready | error
 * ------------------------------------------------------------------------ */

let canvas = null;
let ctx = null;
let focusY = 0.42;

let index = [];          // [byte offset, byte length, keyframe] per frame
let keys = [];           // frame numbers that are keyframes
let bytes = null;
let usec = 1e6 / 24;
let count = 0;

let decoder = null;
const cache = new Map(); // frame -> ImageBitmap
const ready = new Set(); // groups fully decoded into cache
let pending = [];
let want = 0, wantDir = 1, busy = false, broken = null;
let lastPos = -1, dirty = true;
let told = 0;            // last time the painted frame was reported back

const groupOf = i => {
  let lo = 0, hi = keys.length - 1;
  while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (keys[mid] <= i) lo = mid; else hi = mid - 1; }
  return lo;
};
const groupRange = g => [keys[g], g + 1 < keys.length ? keys[g + 1] : count];

function drop(g) {
  const [a, b] = groupRange(g);
  for (let i = a; i < b; i++) {
    const bmp = cache.get(i);
    if (bmp) { bmp.close(); cache.delete(i); }
  }
  ready.delete(g);
}

async function decodeGroup(g) {
  const [a, b] = groupRange(g);
  pending = [];
  for (let i = a; i < b; i++) {
    const [pos, len, key] = index[i];
    decoder.decode(new EncodedVideoChunk({
      type: key ? 'key' : 'delta',
      timestamp: Math.round(i * usec),
      duration: Math.round(usec),
      data: new Uint8Array(bytes, pos, len),
    }));
  }
  await decoder.flush();
  await Promise.all(pending);
  if (broken) throw broken;
  ready.add(g);
}

/* the group under the playhead first, then the one it is heading into, then
   the one behind; everything else is let go before more is decoded */
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
      if (dirty) draw(lastPos);
    }
  } catch (err) {
    broken = broken || err;
    self.postMessage({ type: 'error', message: String(broken && broken.message || broken) });
  }
  busy = false;
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
  ctx.drawImage(bmp, (cw - dw) * 0.5, (ch - dh) * focusY, dw, dh);
}

/* the frame either side of the exact playhead, blended by what is between them,
   so the camera keeps moving between two frames of footage */
function draw(pos) {
  if (pos < 0 || !ctx) return false;
  const i0 = Math.max(0, Math.min(count - 1, Math.floor(pos)));
  const t = pos - i0;
  const i1 = Math.min(count - 1, i0 + 1);
  const b0 = cache.get(i0);
  const b1 = t > 0.004 ? cache.get(i1) : null;
  const base = b0 || nearest(i0);
  if (!base) return false;
  ctx.globalAlpha = 1;
  cover(base, 1);
  if (b0 && b1) cover(b1, t);
  ctx.globalAlpha = 1;
  dirty = !b0 || (t > 0.004 && !b1);
  lastPos = pos;
  /* what is actually on screen, a few times a second — fly.js mirrors it onto
     the canvas element so the scroll-smoothness tests can measure the truth */
  const now = Date.now();
  if (now - told > 16) { told = now; self.postMessage({ type: 'drew', pos: b0 ? pos : i0, exact: !!b0 }); }
  return true;
}

function show(pos, dir) {
  const g = groupOf(Math.max(0, Math.min(count - 1, Math.floor(pos))));
  if (g !== want || dir !== wantDir) { want = g; wantDir = dir; }
  if (!busy) pump();
  if (!dirty && Math.abs(pos - lastPos) < 0.0005) return;
  draw(pos);
}

async function init(m) {
  canvas = m.canvas;
  ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
  focusY = m.focusY;
  if (m.width && m.height) { canvas.width = m.width; canvas.height = m.height; }

  bytes = m.buf;
  index = m.meta.frames;
  count = index.length;
  usec = 1e6 / m.meta.fps;
  keys = [];
  index.forEach((f, i) => { if (f[2]) keys.push(i); });

  const config = {
    codec: m.meta.codec,
    codedWidth: m.meta.width,
    codedHeight: m.meta.height,
    description: m.description,
    optimizeForLatency: true,
  };
  const support = await VideoDecoder.isConfigSupported(config);
  if (!support.supported) throw new Error(`${m.meta.codec} not supported`);

  decoder = new VideoDecoder({
    output: frame => {
      const i = Math.round(frame.timestamp / usec);
      pending.push(createImageBitmap(frame).then(bmp => {
        frame.close();
        const old = cache.get(i);
        if (old) old.close();
        cache.set(i, bmp);
        dirty = true;
      }, err => { frame.close(); throw err; }));
    },
    error: err => { broken = err; },
  });
  decoder.configure(config);

  await decodeGroup(0);
  draw(0);
  self.postMessage({ type: 'ready', frames: count });
}

self.onmessage = e => {
  const m = e.data;
  if (m.type === 'init') {
    init(m).catch(err => self.postMessage({ type: 'error', message: String(err && err.message || err) }));
  } else if (m.type === 'show') {
    if (ctx) show(m.pos, m.dir);
  } else if (m.type === 'resize') {
    if (!canvas) return;
    canvas.width = m.width;
    canvas.height = m.height;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    dirty = true;
    draw(lastPos);
  } else if (m.type === 'rest') {
    /* off screen: hand back all but the group under the playhead */
    for (const g of [...ready]) if (g !== want) drop(g);
  } else if (m.type === 'close') {
    try { decoder && decoder.close(); } catch (err) { /* already closed */ }
    cache.forEach(b => b.close());
    cache.clear();
    ready.clear();
    self.close();
  }
};
