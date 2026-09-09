/* ---------------------------------------------------------------------------
 * P6 — "Virtuálna prehliadka": a walkthrough of the actual apartment
 *
 * The geometry is NOT generated or interpreted. It is reconstructed from the
 * architect's own vector drawing by _build/tour/build_model.py: the structural
 * layer of the PDF is stroked, flood-filled from outside, and the enclosed
 * slivers between each pair of wall faces come back as the wall bodies, with
 * true thickness and with door reveals already cut. Flat H measures 69,8 m²
 * that way against the 69,9 m² printed on the drawing.
 *
 * So every wall you can walk up to is where the architect put it. The one
 * figure a plan cannot carry is ceiling height; 2,65 m is assumed and the model
 * flags it (`ceilingIsAssumed`).
 *
 * Three.js is ~600 KB, so nothing loads until the visitor asks for it.
 * ------------------------------------------------------------------------ */

const THREE_SRC = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
const THREE_SRI = 'sha384-CI3ELBVUz9XQO+97x6nwMDPosPR5XvsxW2ua7N1Xeygeh1IxtgqtCkGfQY9WWdHu';

/* the same warm palette the rest of the site uses */
const MAT = { floor: 0xb08a5c, wall: 0xf2efe9, ceil: 0xfaf8f5, trim: 0xe4ded4 };

let threeReady = null;
function loadThree() {
  if (threeReady) return threeReady;
  threeReady = new Promise((res, rej) => {
    if (window.THREE) return res(window.THREE);
    const s = document.createElement('script');
    s.src = THREE_SRC; s.integrity = THREE_SRI;
    s.crossOrigin = 'anonymous'; s.referrerPolicy = 'no-referrer';
    s.onload = () => res(window.THREE);
    s.onerror = () => rej(new Error('three'));
    document.head.appendChild(s);
  });
  return threeReady;
}

/* --- geometry helpers ----------------------------------------------------- */

/** ray-cast point-in-polygon; used both for the floor and to stop at walls */
function inRing(ring, x, y) {
  let hit = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i], [xj, yj] = ring[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) hit = !hit;
  }
  return hit;
}

function shapeFrom(THREE, ring) {
  const s = new THREE.Shape();
  ring.forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
  s.closePath();
  return s;
}

/** extrude a plan ring upward: the model is drawn in plan (x, y) with y south */
function slab(THREE, ring, depth, material, yTop) {
  const g = new THREE.ExtrudeGeometry(shapeFrom(THREE, ring), { depth, bevelEnabled: false });
  const m = new THREE.Mesh(g, material);
  m.rotation.x = Math.PI / 2;       // plan lies flat
  m.position.y = yTop;
  return m;
}

/* --- the tour ------------------------------------------------------------- */

function buildTour(THREE, host, model) {
  const W = host.clientWidth, H = Math.max(320, Math.round(W * 0.58));
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(W, H);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  host.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf7f4ef);

  const cam = new THREE.PerspectiveCamera(72, W / H, 0.05, 120);
  const EYE = 1.62;

  const mats = {
    floor: new THREE.MeshLambertMaterial({ color: MAT.floor }),
    wall:  new THREE.MeshLambertMaterial({ color: MAT.wall }),
    ceil:  new THREE.MeshLambertMaterial({ color: MAT.ceil }),
  };

  const floorRing = model.floor[0];
  model.floor.forEach(r => {
    const f = slab(THREE, r, 0.04, mats.floor, 0);
    f.receiveShadow = true; scene.add(f);
    scene.add(slab(THREE, r, 0.04, mats.ceil, model.ceiling + 0.04));
  });
  model.walls.forEach(r => {
    const w = slab(THREE, r, model.ceiling, mats.wall, model.ceiling);
    w.castShadow = true; w.receiveShadow = true; scene.add(w);
  });

  /* daylight comes from the terrace side, which on this plan is +y (south) */
  scene.add(new THREE.HemisphereLight(0xffffff, 0xcfc6b8, 0.85));
  const sun = new THREE.DirectionalLight(0xfff0da, 0.75);
  sun.position.set(model.size[0] * 0.35, 6, model.size[1] * 2.2);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  scene.add(sun);

  /* --- where you start: just inside the front door, looking in ------------ */
  const bb = floorRing.reduce((a, [x, y]) => ({
    x0: Math.min(a.x0, x), y0: Math.min(a.y0, y),
    x1: Math.max(a.x1, x), y1: Math.max(a.y1, y),
  }), { x0: 1e9, y0: 1e9, x1: -1e9, y1: -1e9 });

  /* find a standable point near the east end (the entrance is on that side) */
  function standable(px, py) { return inRing(floorRing, px, py); }
  let start = null;
  for (let t = 0.94; t > 0.4 && !start; t -= 0.02) {
    for (let u = 0.2; u <= 0.8; u += 0.05) {
      const x = bb.x0 + (bb.x1 - bb.x0) * t, y = bb.y0 + (bb.y1 - bb.y0) * u;
      if (standable(x, y)) { start = [x, y]; break; }
    }
  }
  if (!start) start = [(bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2];

  const pos = { x: start[0], y: start[1] };
  let yaw = Math.PI / 2, pitch = 0;   // look west, along the flat

  function place() {
    cam.position.set(pos.x, EYE, pos.y);
    cam.rotation.set(0, 0, 0);
    cam.rotateY(yaw); cam.rotateX(pitch);
  }
  place();

  /* --- movement, with the floor polygon as the collision hull ------------- */
  const keys = Object.create(null);
  const SPEED = 2.1, PAD = 0.28;

  function tryMove(dx, dy) {
    /* slide along walls: attempt both axes, then each on its own */
    if (freeAt(pos.x + dx, pos.y + dy)) { pos.x += dx; pos.y += dy; return; }
    if (freeAt(pos.x + dx, pos.y)) { pos.x += dx; return; }
    if (freeAt(pos.x, pos.y + dy)) { pos.y += dy; }
  }
  function freeAt(x, y) {
    /* keep a body's width clear so you cannot graze through a wall corner */
    for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
      if (!inRing(floorRing, x + Math.cos(a) * PAD, y + Math.sin(a) * PAD)) return false;
    }
    return true;
  }

  let dragging = false, lastX = 0, lastY = 0, moving = 0;
  const el = renderer.domElement;
  el.style.touchAction = 'none';
  el.tabIndex = 0;
  el.setAttribute('aria-label',
    'Virtuálna prehliadka bytu. Ťahaním sa rozhliadate, klávesmi W A S D alebo šípkami sa pohybujete.');

  el.addEventListener('pointerdown', e => {
    dragging = true; lastX = e.clientX; lastY = e.clientY;
    el.setPointerCapture(e.pointerId); el.focus();
  });
  el.addEventListener('pointerup', e => {
    dragging = false;
    try { el.releasePointerCapture(e.pointerId); } catch (_) {}
  });
  el.addEventListener('pointermove', e => {
    if (!dragging) return;
    yaw -= (e.clientX - lastX) * 0.005;
    pitch = Math.max(-1.1, Math.min(1.1, pitch - (e.clientY - lastY) * 0.005));
    lastX = e.clientX; lastY = e.clientY;
  });
  el.addEventListener('keydown', e => {
    if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key)) e.preventDefault();
    keys[e.key.toLowerCase()] = true;
  });
  el.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

  host.querySelectorAll('[data-walk]').forEach(b => {
    const dir = +b.dataset.walk;
    const on = e => { e.preventDefault(); moving = dir; };
    const off = () => { moving = 0; };
    b.addEventListener('pointerdown', on);
    b.addEventListener('pointerup', off);
    b.addEventListener('pointerleave', off);
    b.addEventListener('pointercancel', off);
  });

  let last = performance.now(), raf = 0;
  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    let f = moving, s = 0;
    if (keys.w || keys.arrowup) f += 1;
    if (keys.s || keys.arrowdown) f -= 1;
    if (keys.a || keys.arrowleft) s -= 1;
    if (keys.d || keys.arrowright) s += 1;
    if (f || s) {
      const sin = Math.sin(yaw), cos = Math.cos(yaw), k = SPEED * dt;
      tryMove((-sin * f + cos * s) * k, (-cos * f - sin * s) * k);
    }
    place();
    renderer.render(scene, cam);
    raf = requestAnimationFrame(frame);
  }
  raf = requestAnimationFrame(frame);

  const onResize = () => {
    const w = host.clientWidth, h = Math.max(320, Math.round(w * 0.58));
    renderer.setSize(w, h); cam.aspect = w / h; cam.updateProjectionMatrix();
  };
  addEventListener('resize', onResize);

  return () => { cancelAnimationFrame(raf); removeEventListener('resize', onResize); renderer.dispose(); };
}

/* --- mount ---------------------------------------------------------------- */

/* Reconstruction is per apartment type and done one at a time; a flat with no
   model simply gets no tour rather than a broken button.

   EMPTY ON PURPOSE. The walkthrough renders correct geometry but nothing else
   -- no glazing, no materials, no furniture -- and an undressed grey shell has
   no business on a page a buyer sees. The extraction pipeline and the model it
   produces are still live and are the input to the Blender render; put a letter
   back in this list only once the scene is actually dressed. */
const TOUR_FLATS = [];

function mountTour(host, unit) {
  if (!host || !unit || !TOUR_FLATS.includes(unit.letter)) return;
  const letter = unit.letter;

  host.innerHTML = `
    <div class="tour" data-tour="${letter}">
      <div class="tour__head">
        <p class="eyebrow" style="margin:0">Virtuálna prehliadka</p>
        <span class="tour__badge">3D model bytu ${unit.id}</span>
      </div>
      <div class="tour__intro">
        <p>Prejdite sa bytom. Model je postavený priamo z pôdorysu architekta —
           rozmiestnenie miestností, hrúbky stien aj dvere sedia s výkresom.</p>
        <button class="btn btn--primary" type="button" data-tour-start>
          Spustiť prehliadku
        </button>
      </div>
      <div class="tour__stage" data-tour-stage hidden>
        <div class="tour__pad">
          <button class="tour__walk" type="button" data-walk="1" aria-label="Vpred">▲</button>
          <button class="tour__walk" type="button" data-walk="-1" aria-label="Vzad">▼</button>
        </div>
      </div>
      <p class="form__note tour__note" data-tour-note hidden>
        Ťahaním myšou alebo prstom sa rozhliadate, klávesmi W A S D alebo šípkami
        (na mobile tlačidlami) sa pohybujete. Geometria je prevzatá z výkresu;
        svetlá výška 2,65 m je predpoklad, výkres ju neuvádza. Model je bez
        zariadenia a povrchov — slúži na overenie dispozície.
      </p>
    </div>`;

  const root = host.querySelector('[data-tour]');
  const btn = root.querySelector('[data-tour-start]');
  const stage = root.querySelector('[data-tour-stage]');
  const note = root.querySelector('[data-tour-note]');

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    btn.textContent = 'Načítavam…';
    try {
      const [THREE, model] = await Promise.all([
        loadThree(),
        fetch(`assets/tour/flat-${letter}.json`).then(r => {
          if (!r.ok) throw new Error('model');
          return r.json();
        }),
      ]);
      root.querySelector('.tour__intro').remove();
      stage.hidden = false;
      buildTour(THREE, stage, model);
      if (note) note.hidden = false;
    } catch (err) {
      /* a failed tour must not read as a broken page — say so and stay put */
      btn.disabled = false;
      btn.textContent = 'Prehliadku sa nepodarilo načítať';
    }
  });
}
