# P6 — Prievozská 6, Bratislava

Static site for P6, a single residential building at Prievozská 6,
Bratislava-Ružinov. No build step, no dependencies: plain HTML + one stylesheet
+ a handful of small scripts. Open `index.html` or serve the folder.

**Structure follows the client brief `P6_zmeny.docx` section by section.** The
landing page is one location-first narrative in the brief's order (§1–§16);
`lokalita.html` and `projekt.html` redirect into its chapters. Section numbers
in the HTML comments and in `_build/build_pages.py` are the brief's.

Local preview:

```bash
python3 -m http.server 8123 --directory rezidencia
```

## This is currently a CLIENT PREVIEW build

Every page carries `<meta name="robots" content="noindex, nofollow">` and
`robots.txt` blocks all crawlers, so the link can be shared without the site
turning up in search.

**Before launch:** set `PREVIEW = False` at the top of `_build/build_pages.py`
and re-run it. That removes the noindex tags and restores a real `robots.txt`
with the sitemap reference.

## Deploying

The repo is the site — GitHub Pages serves it straight from `main`. (The repo is still named `rezidencia-aurora` from the placeholder phase; rename it and the URL changes.) To publish
a change:

```bash
cd rezidencia && git add -A && git commit -m "update" && git push
```

Pages rebuilds in about a minute. `.nojekyll` is present so nothing gets
filtered by Jekyll.

## Pages

| File | Purpose |
|---|---|
| `index.html` | The whole narrative: fly-by hero → building picker (`#vyber-bytu`) → orientation map → manifesto → Miletička → business zone → five-minute city → school → Nivy → sport → architecture → community terrace → parameters → standard → units → closing block. Sticky chapter nav (Lokalita / Projekt / Štandard / Byty). |
| `byty.html` | Unit cards with a floor-plan thumbnail; filters exactly per the brief: rooms, floor, area, terrace/balcony, orientation, availability. No table. |
| `byt.html?id=4.03` | Unit detail: specs, the architect's rendered plan, room table, clickable storey plan ("Poloha v dome"), similar units, sticky price bar on phones. |
| `galeria.html` | Photo placeholders for the shots the brief asks for (Miletička, cyclist, Nivy at night, school run, terrace). |
| `kontakt.html` | Contact form + FAQ. `?byt=4.03` prefills the unit; `?katalog=1` prefills a catalogue request (the "Stiahnuť katalóg" CTA lands here until a PDF exists). |
| `lokalita.html`, `projekt.html` | Instant redirects to `index.html#lokalita` / `#projekt` so old links keep working. |

## The one file you edit

**`assets/js/data.js`** holds all 44 apartments. Everything on the site — hero
selector, list, filters, detail pages, counters, parameters — reads from it.

It is **generated from the architect's floor plans** (`1np.pdf`,
`2 az 4 np.pdf`, `5np.pdf` — Ing. arch. Martin Krajči, based on arch. Kullman's
drawings). Every room area is the figure printed on those drawings; nothing is
invented. The header of the file documents each field.

Per the architect's note, kitchen and living room are merged into one figure,
and in one-room flats (E, F, G) the entrance area is merged in as well, because
those spaces are not separated by walls.

### Apartment numbering

`floor.letter` exactly as labelled on the drawings — `3.H` is apartment H on the
3rd floor. 1.NP has 8 flats (A–H); 2.–5.NP have 9 (A–I). The ninth slot on 1.NP
is the entrance lobby and staircase.

| Floors | Source drawing | Notes |
|---|---|---|
| 1.NP | `1np.pdf` | different layout; no flat I; flat H is larger (77,9 m²) |
| 2.–4.NP | `2 az 4 np.pdf` | identical on all three floors |
| 5.NP | `5np.pdf` | as 2.–4.NP except flat A has a smaller entrance hall (4,5 vs 4,9 m²) |

### Floor plans

`assets/plans/*.webp` — the architect's **rendered** plans, furnished and
shaded, imported by `_build/plans/import_renders.py`:

* `flat-<band>-<letter>.webp` — 18 files, shown on each apartment page.
  Apartment A is drawn differently on every band (`1np` / `24np` / `5np`);
  B–I are one drawing shared across 2.–5. NP. 1.NP has no I.
* `floor-1np.webp`, `floor-25np.webp` — the two storey plans, used by
  **"Poloha v dome"** on the apartment page: the flat you are on is marked, the
  others light up on hover and link to their own page
  (`assets/js/floorplan.js`).

These replaced an earlier attempt at cutting per-apartment plans out of the
vector PDFs with clip rectangles. Rectangular crops cannot follow an L-shaped
flat, and the results were rejected; `genplans.py` and its 26 SVGs are gone.

The **PDFs are still the source of truth for the numbers** — `gendata.py`
rebuilds `data.js` from them and asserts each flat's rooms sum to its interior
area. All 44 units' room areas on the new renders match `data.js` exactly,
which is what confirms the renders were mapped to the right apartments.

Identifying which flat is which is not eyeballable: E, F and G are one-room
flats within 0,4 m² of each other. The apartment letters printed at each front
door in the architect's PDFs are what settle it. Left to right along the
courtyard side: **G, F, E**. See `_build/plans/README.md`.

### Still to come from the client — do not invent

| Field | State |
|---|---|
| Prices | `price: null` everywhere → renders "Cena na vyžiadanie" |
| Availability | everything `dostupny`; update as units are reserved or sold |
| Orientation | **needs a site plan with a north arrow.** The field, the filter and the compass were removed rather than guessed |
| EV charging | the parking card says "upresníme". Parking itself is settled: **50 spaces, outdoor, in front of the building — there is no garage** (investor, 2026-09-15). Cellars are 1,5–3,0 m². |
| Standard of finish | six cards are written but flagged as unconfirmed |
| Harmonogram | hidden until `MILESTONES` is filled in |

### The disclaimer is mandatory

`DISCLAIMER` in `_build/build_pages.py` carries the architect's required
wording and appears under every plan, the unit list and the parameters. It must
stay: the building is an existing skeleton being reconstructed, tolerances of
roughly ±5–10 cm are expected, balcony areas are not confirmed by the city, and
the project is being pre-sold without final permits.

## Interaction

Nothing here is decorative-only; each piece is doing a job.

**Hero: scroll-driven fly-by** (`assets/js/fly.js`, `assets/fly/`)
- The footage starts on the architect's own visualisation of P6 (the one on the
  "Vizualizácia" tile) and pushes in toward the planted balconies. The section
  is pinned (`position: sticky`) and ~3.3 viewports tall; scrolling moves the
  camera, and three beats of copy cross-fade over it: the headline, "44 bytov",
  "Komunitná terasa a fitness". Beat timing is `WINDOWS` in `fly.js`.
- **How the footage was made.** The render was cropped to 16:9 and upscaled
  2x in Magnific (ultra-denoiser), then animated from that start frame.
  Three models were tried on the same frame: **Kling 3.0 won** (Kling 2.5
  invented a drone flying past, Veo 3.1 let the building morph). Only the
  first 8.0 s are used; after that the lens starts leaning wide-angle. Around
  3,300 credits in total.
- **Decoding runs in a worker.** `fly-worker.js` gets the MP4, the frame index
  and the canvas (handed over as an OffscreenCanvas); this thread only works
  out where the playhead should be and posts it. On the main thread a keyframe
  group decoding mid-scroll stalled the page for up to 250 ms — exactly under
  the reader's hand.
- **The camera glides toward the scroll position** (`GLIDE_MS` in `fly.js`,
  95 ms, frame-rate independent), and so do the copy beats and the progress
  bar. This is the whole trick for a plain office mouse: a wheel notch jumps
  the page ~114px in one go, about 8 frames of an 8-second clip, so following
  the scroll exactly means the picture lands on one frame, waits, and lands on
  the next — stepping. Measured with Chrome's smooth scrolling switched off
  (`--disable-smooth-scrolling`, which is what such a mouse behaves like):
  following exactly gave jumps of up to 8.7 frames with 70% of refreshes
  showing nothing new; the glide gives 1–2 frames per refresh and **no** still
  refreshes, at the cost of the camera trailing the scroll by ~7 frames of
  footage and settling ~0.3 s after the wheel stops. A trackpad never notices:
  its deltas are already finer than the glide.
- Raising `GLIDE_MS` smooths further and trails more; lowering it tightens and
  starts to step again. 80 / 105 / 140 ms were measured before settling on 95.
- **It is not a seeked `<video>`.** That was the first version, and it moved in
  visible steps: seeks are asynchronous and each must land before the next, so
  on a real scroll gesture the picture changed 25–37 times a second and trailed
  the page. Now `fly.js` fetches the MP4 whole, decodes the frames itself with
  **WebCodecs**, and paints them into a canvas on every display refresh,
  blending the two frames either side of the exact scroll position. When the
  scroll rests it eases onto a whole frame, so a still never shows two frames
  at once.
- **Measured** (headless Chrome): every compositor frame is a different
  picture, 53–60 a second, scrolling down or up at 600–3,000 px/s, on desktop
  and at 390px, with zero frames drawn before they were decoded. Spinning a
  mouse wheel (100px notches every 30–120 ms): 60 fps, no dropped frames,
  worst frame gap 17 ms, and the picture trails the scroll by ~1.4 frames of
  footage. Before the worker it was ~5 frames with 250 ms stalls.
- The section is 380svh (300 on phones) for feel, not for the footage: the
  taller it is, the less film a single wheel notch moves (~7.5 frames).
- **Memory.** All 192 frames as bitmaps would be over a gigabyte at 1600px, so
  frames are decoded a keyframe group (12) at a time and only the group under
  the playhead and its two neighbours are kept. Off screen for 2 s, it drops
  to one group.
- **Assets.** `_build/fly/build_fly.py <master.mp4>` makes everything: 24 fps,
  `hqdn3d` temporal denoise (generated foliage shimmers otherwise), H.264 with
  no B-frames and a keyframe every 12 frames.
  `p6-fly-wide.mp4` 1600x900, 3.3 MB, for desktop and tablets;
  `p6-fly-tall.mp4` 720x900, 1.8 MB, the centre 4:5 of the frame for phones.
  Beside each is a JSON index with the decoder config (codec string + avcC)
  and the byte range of every frame. WebP frame sequences were measured at
  16–24 MB for the same 192 frames, which is why this is not an image
  sequence. After re-running it, bump `ASSET_V`.
- **Fallbacks.** No WebCodecs, an unsupported codec, a decoder error, or no
  first frame within 8 s: the same MP4 goes into the `<video>` and is seeked
  the old way (`.is-video`). Reduced motion, Save-Data or no JS: a normal
  one-screen hero on the poster (the render itself), and the footage is never
  requested.
- **Local testing needs HTTP byte ranges** for the `<video>` fallback.
  `python3 -m http.server` does not serve them, and the fallback then silently
  stays on frame 0. GitHub Pages does.
- **Phones:** the picture takes the top 56% of the pinned screen and the copy
  sits below it on paper, so the text never fights the footage.

**Floor picker** (`#vyber-bytu`, right under the hero; `assets/js/floors.js`)
- The investor's exterior visualisation of P6 (sent 17. 9. 2026), upscaled 2x
  in Magnific with the zero-creativity *ultra-photo* mode so nothing on the
  facade changed; `assets/img/p6-dom-{1280,1920,2560}.webp`. It replaced the
  drawn placeholder facade (`building.js`, deleted).
- Every storey is a hover band. Hover paints it in brand copper (the same
  colour as the storey plans), the other storeys step back slightly, a `3. NP`
  tag appears on the facade, and a card shows **Bytov na podlaží**, **Voľné**,
  **Rezervované**, **Predané** with a status bar. Counts are read from
  `data.js`, so a status change there updates the card.
- **Click a storey and the page dives into it.** Two beats: the camera pushes
  in on the copper band until it nearly spans the stage, then that band opens
  out (a `clip-path` from the zoomed band to the full stage) into the
  architect's plan of the storey while the picture fades to paper. Closing
  runs it backwards. Web Animations API, ~1.2 s; reduced motion swaps
  instantly.
- **Inside the storey** (`.fview`): *Späť na dom*, the storey's name and free
  count, and chips to jump between 1.–5. NP without leaving. Every flat lights
  copper under the pointer with a card (id, status, type, interiér / balkón /
  spolu, price); a click opens `byt.html?id=…`. The plan and its outlines are
  the same ones "Poloha v dome" uses: `floorPlanHTML()` in `floorplan.js`.
- The storey has its own history entry, `#podlazie-3`: the browser's back
  button returns to the building, and a link to that address opens the storey
  directly. A new-tab click on a storey still gets the plain list,
  `byty.html?floor=N`.
- Phones: tapping a storey opens its card; *Pôdorys N. NP* pushes in on the
  band, then the plan takes the page below the chips and pans sideways in its
  rail. Tapping a flat opens a bottom sheet with *Detail bytu*.
- Two traps met on the way: a delayed animation holds its first keyframe, so
  the view must also be `opacity: 0` then, or the band shows as a blank slab
  on the house; and a `clip-path` left on the view clips the fixed-position
  card, so every animation is cancelled once it has run. On phones the stage
  must not keep `place-items: center`: Chrome now applies `justify-self` to
  plain blocks and shrink-wraps the plan to its 660px rail.
- **Two sides, one click.** `VIEWS` in `floors.js` holds the street facade
  (Prievozská, north) and the courtyard facade behind it, each with its own
  picture and its own band geometry, because bands are measured in the pixels
  of their own picture. The turn is a real rotation: the stage rotates to
  edge-on, the picture and the bands are swapped at that point, and it rotates
  back, ~0.7 s in total (instant under reduced motion). The storeys stay live
  on whichever side is showing, and the side is named under the house.
- **The courtyard render is not in yet.** `VIEWS.back.slug` is `null`, so the
  turn button hides itself and the section behaves exactly as before. To
  switch it on: put `p6-dom-back-{1280,1920,2560}.webp` in `assets/img/`, set
  `slug: 'p6-dom-back'`, and **re-measure `x` and `floors` on that picture** —
  the camera sits elsewhere, so the front numbers do not carry over.
- The bands are measured on the 2560x1440 picture against the bottom edge of
  each balcony slab. Ground floor is 1. NP; the roof terrace is not a storey.
  **A different picture means re-measuring them.**
- The picture lives inside the same SVG as the bands, so cropping the viewBox
  moves both together. Phones use a tighter frame on the building
  (`DOM_VIEW.narrow`), which makes a storey a ~32px tall, full-width band.
- Desktop: the card sits in the street to the left of the building, level with
  the storey, and falls back to over the facade when there is no room. Phones:
  first tap opens a bottom sheet; a second tap on the same storey or its
  button opens the storey. (The tap state is tracked apart
  from focus: a tap focuses the link before it clicks.)
- A one-off sweep lights each storey bottom to top the first time the section
  is seen. The picture loads on approach, at the smallest size that is sharp.
- Counters count up when they come into view.

**Maps** (`[data-citymap]`, `assets/js/map.js`)
- Real slippy maps, not schematics: **Leaflet 1.9.4** from cdnjs (SRI-pinned),
  lazy-mounted by an `IntersectionObserver` so the library only downloads when
  a map scrolls into view.
- Tiles are **Esri Gray Canvas** (`Canvas/World_Light_Gray_Base` plus the
  `_Reference` label overlay; the `Dark` pair on ink sections). Chosen because
  it is keyless, muted enough not to fight the palette, and renders Slovak
  place names. *Caveat for production:* Esri's terms expect an ArcGIS
  attribution and are not a guaranteed free tier at volume — if traffic grows,
  move to a paid key (MapTiler / Mapbox) rather than silently leaning on it.
  CARTO was the first choice and now stamps "API KEY REQUIRED" over the tiles.
- `fadeAnimation: false` is deliberate. Leaflet's tile fade-in stalls at
  `opacity: .03` whenever `requestAnimationFrame` is throttled (hidden tab,
  reduced-motion, background render), which looks like broken tiles.

**No dashes in the copy.** Filip's standing rule: no em or en dash anywhere a
reader can see it, in any language. Ranges read "30,1 až 77,9 m²", a pause is a
comma or a full stop, a title separator is `|`. Hyphens inside words
("2-izbový", "Bratislava-Ružinov", "e-mail") are fine. Source comments are not
copy and keep their punctuation.

**Map data — where the numbers come from**
- **Nothing goes in unverified.** The transport and gastronomy entries added on
  18. 9. 2026 were checked against sources outside OpenStreetMap: the lines at
  each stop against **imhd.sk** (Miletičova: 42, 70, 71, 72, N72; Novohradská:
  42, 70, 72, N72; Prievozská adds 66, 96 and N74 plus the regional lines to
  Senec, Šamorín, Modra and Malinovo), and every restaurant against its own
  site or a delivery listing. That caught what raw map data would not:
  **LANOGI GURMAN sits 60 m away in OSM and closed on 1. 10. 2025**, so it is
  not on the site. It also corrected the old mobility copy, which promised tram
  stops "a few minutes away" when the nearest one, Líščie nivy, is about a
  kilometre off.
- Places within ~250 m carry `tight: true`: they keep a dot on the map instead
  of a permanent label, because eight labels inside 250 m pile into an
  unreadable stack around P6. Their names, notes and times live in the list
  beside the map and in the pin's popup.
- POI coordinates in `POIS` were geocoded with **Nominatim**; the `m` (metres)
  and `walk` / `bike` / `car` minutes come from **OSRM**
  (`routing.openstreetmap.de`, `routed-foot` / `routed-bike` / `routed-car`).
  They are *routed* figures, not straight-line estimates — Eurovea is 2.0 km
  and 27 min on foot, not the 11 min a crow-flies guess suggests.
- The values are **baked into `map.js` as constants**: no runtime API calls, no
  keys, no rate limits. The cost is that they are a snapshot — **if a POI is
  added, moved, or the route network changes, re-measure and update `POIS`.**
- The same constants feed three places: the five-minute city, the §2
  orientation map, and the §5 business-zone route. Change them once.
- Modes are **Pešo / Bicyklom / Autom** only. There is no scooter mode and none
  should be added.
- Times colour copper for ≤5 min, light for ≤15, dimmed beyond. Category chips
  filter; the list sorts by real time and links to the pins on hover.
- Apollo Business Center is deliberately **not** pinned on the orientation map:
  at 75 m it lands on the same pixel as P6. It leads the key figures instead.

(The former storey-by-storey scrollytelling section was removed: the brief
rules out claims about setbacks and penthouses until the architecture is
confirmed. Its engine went with `building.js`.)

**Apartment detail**
- The plan is the architect's rendered drawing for that flat, with his own room
  codes and areas on it; the room table beside it repeats the same figures.
- **"Poloha v dome"** (`assets/js/floorplan.js`) is the storey plan for the
  floor the flat is on. The flat you are viewing is marked and is not a link;
  every other flat on the storey is a hit region that lights up on hover and
  goes to its own page, keyboard included. Status only tints on hover — a plan
  pre-painted in three status colours reads as a heat map and buries the
  drawing.
- **Which way the flat looks.** The plan carries Sever / Juh / Východ / Západ
  on its four edges. The client's material still does not state the
  orientation, so it is derived rather than guessed: OpenStreetMap has the
  building at Prievozská 6 (Bratislava Business Center III, the skeleton being
  reconstructed) as a 43.2 x 13.7 m block with its long axis at 70.3°, so the
  long facades face 340.3° (NNW) and 160.3° (SSE); Prievozská runs along the
  NNW side; and the entrance stair on the 1.NP drawing sits bottom left, on the
  street. Bottom of the plan is therefore the street and the north side, top is
  the courtyard and the south side, left is east, right is west. The caption
  says the orientation is approximate and that the architect confirms it. The
  derivation is written out at the top of `floorplan.js` — **re-check it if the
  architect ever supplies a site plan with a north arrow.**
- On phones the storey plan pans in a rail rather than shrinking: it is a 2.3:1
  letterbox, and squeezed to a phone it lands ~145px tall, too small to read
  nine flats off.
- `←` / `→` walk through the building in order.
- **Stiahnuť PDF** downloads the apartment sheet, see below.

**Apartment PDFs** (`assets/pdf/P6-byt-1A.pdf` …, one per apartment)
- Two A4 pages: title, the five key figures (interiér, balkón, spolu, izby,
  podlažie) and the architect's plan; then the room table, price, **možnosť
  dokúpiť** (pivničná kobka 1,5 – 3,0 m², parkovacie miesto pred domom), the
  storey plan with the flat in copper, contact, and the disclaimer on both
  pages. The footer is dated.
- They are **static files: regenerate them after any change to `data.js` or
  the contact details** (the phone and e-mail are still placeholders):
  `python3 rezidencia/_build/build_pages.py` then
  `node rezidencia/_build/pdf/build_pdfs.mjs` (`ONLY=1.B,3.H` for a few).
- How: `build_pages.py` writes a print template, `_build/pdf/karta.html`,
  rendering from the same `APARTMENTS` as `byt.html`; the script prints it once
  per apartment in headless Chrome. The template re-encodes the plans to JPEG
  before printing, because Chrome writes a WebP into a PDF as raw pixels (3 MB
  a file instead of ~700 KB).

  *A compass used to point at the flat's orientation; it was removed because
  nothing in the client's material states which way the building faces, and the
  earlier abstract elevation was replaced by the real storey plan.*

**Virtual walkthrough** (`assets/js/tour.js`, model from `_build/tour/build_model.py`)
- A first-person walk through the actual apartment. The geometry is **not
  generated** — it is reconstructed from the architect's vector PDF, so every
  wall is where he drew it.
- How: the drawing separates by pen weight (structure at 0.96, everything else
  at 0.24). Stroke only the structural layer, flood-fill from outside, and the
  enclosed slivers between each pair of wall faces come back as wall *bodies* —
  true thickness, door reveals already cut.
- Scale: the PDF carries no dimensions or scale bar, so it is solved from the
  printed areas. Flat H's enclosed interior is 69,9 m² by the drawing, which
  fixes **24,71 PDF units per metre**. The export re-measures at 69,8 m². After
  separating rooms: living+kitchen+hall 43,1 (printed 43,0), bedrooms 11,2 and
  10,6 (printed 10,7 and 10,0), store 2,3 (printed 2,2).
- **Ceiling height is the only assumption** — a plan cannot carry it and the
  architect's notes do not state it. 2,65 m, flagged in the model as
  `ceilingIsAssumed` and stated to the visitor.
- Three.js r128 from cdnjs, SRI-pinned, ~600 KB, loaded only when the visitor
  presses the button. The floor polygon doubles as the collision hull.
- **Why not a generated video:** all 51 models in the Freepik/Magnific
  catalogue synthesise pixels from a prompt or an image. None is geometry-aware
  (no 3D, CAD, mesh or depth conditioning), so none can be faithful to a plan —
  two attempts produced convincing footage of a *different* apartment. This is
  a category limit, not a model-choice problem.
- **v1 is a shell:** correct walls and openings, flat colours, no glazing, no
  furniture, no materials. Only flat H is built (`TOUR_FLATS` in `tour.js`).

**Photo tiles** (`photo()` in `_build/build_pages.py`, `.photo` in the CSS)
- One element covers both states. Without `src=` it is a dashed placeholder
  (icon, title, "Fotografia bude doplnená"). With `src=` the image is layered
  on top at `opacity: 0` and **only** promoted — `has-img`, which hides the
  placeholder content and shows the credit — by the image's own `onload`.
- That direction matters. Shipping `has-img` from the build and stripping it in
  `onerror` was the earlier design and it fails silently: `loading="lazy"`
  never requests an image the reader does not scroll to, so no `onerror` ever
  fires and the tile sits there as an empty box. Load-driven promotion means a
  missing, slow, or never-requested file always degrades to the designed
  placeholder.
- **Every photo is currently an AI-generated demo stand-in** — 17 images in
  `assets/img/*.webp` filling all 21 slots (Miletička, the school aerial, the
  terrace, the P6 render, the gallery, both apartment-page tiles and the six
  Štandard tiles). Several depict real named places, so each carries a small
  "Ilustračný obrázok" credit. That label is one constant, `DEMO_IMG` in
  `_build/build_pages.py`: set it to `None` once real photography is in and
  every label goes. Replace an image by dropping a file at the same path.
- `.photo` resets `margin: 0`. photo() emits a `<figure>`, and the browser's
  default `margin: 1em 40px` had been insetting every tile 40px from both sides
  of its column. Ratio tiles (`--wide`, `--tall`, `--air`, `--flush`) also set
  `min-height: 0`: through `aspect-ratio`, a min-height becomes a min-width
  (220px × 16/9 = 391px), which pushed wide tiles off a 375px phone.

**Everywhere**
- Cards, feature tiles and placeholders carry a cursor-following spotlight.
- A reading-progress hairline sits under the navigation.

All of it is gated on `prefers-reduced-motion` and degrades to plain static
layout without JS.

## Optional: the page generator

`_build/build_pages.py` regenerates all seven HTML files from one set of
templates, so shared chrome (nav, footer, CTA band, `<head>`) lives in one
place. `_build/gen_data.py` regenerates the placeholder unit list.

The HTML files are the deliverable and can be edited by hand. **Running the
generator overwrites all of them** — if you have hand-edited the HTML, port
the change into the generator first, or just stop using it.

```bash
python3 rezidencia/_build/build_pages.py    # run from the folder ABOVE rezidencia/
```

**Bump `ASSET_V` in that file whenever you change CSS or JS.** It is appended
to every asset link as `?v=N`, so the client's phone does not keep serving a
cached stylesheet after a deploy.

## Mobile

The phone layout is designed for the phone rather than scaled down from the
desktop one. The landing page measured 12,585px tall on a 375px screen; the
same content now runs about 9,600px, by changing layout rather than shrinking
things.

Audited for horizontal overflow and touch-target size on every page at 320,
375 and 430px — both clean. The only sub-44px control is the consent
checkbox, whose 292x44 label toggles it.

Layout changes made for the phone:

- **The fly-by puts its copy below the picture**, not over it. Over moving
  footage on a 390px screen the text was either unreadable or needed a scrim
  heavy enough to hide the building.
- **The floor list is a horizontal chip rail** instead of eight stacked 52px
  rows — 420px of hero down to about 80.
- **Available units are a snap rail.** Six stacked cards ran to ~1,800px; the
  rail shows the same six in one screen and matches how listings get browsed
  on a phone. `scroll-padding-inline` is required or snap ignores the
  container padding and pins the first card to the screen edge.
- **The stats band goes two-up.** A single black column of four huge numbers
  read as dead space.
- **The apartment detail page gets a fixed price + enquiry bar**, so the CTA
  is not 2,000px up the page.
- Type and section padding step down, `--nav-h` drops to 64px.

Phone-specific behaviour, all in the `MOBILE` blocks at the end of the CSS:

- **Filters are a bottom sheet.** Inline they pinned ~326px of controls under
  the nav and ate half the screen. The sticky bar is now just
  `Filtre · N bytov · Zrušiť`, and the fields slide up over a scrim with an
  apply button.
- **Card view is forced below 760px.** The table has a 940px minimum width;
  horizontally scrolling it on a phone is not a real option, so the
  table/card switch is hidden there. The desktop preference is remembered
  separately and restored when the viewport grows.
- **Tapping a storey on the building opens a bottom sheet** with its counts
  and a full-width *Zobraziť byty* button, so an imprecise tap costs one extra
  tap instead of a wrong page. The floor strip under the picture is the other
  route.
- **The floor plan switches to a portrait 420x520 box** so its labels render
  around 11px rather than 7px.
- `--nav-h` drops to 64px.

Phone polish, audited at 320 / 390 / 430 / 768 px with a coarse pointer
(`/tmp` harness: every page, every width, checking sideways scroll, target size
and spacing, text size, alt text and labels):

- **Form fields are 16px on a phone.** iOS zooms the whole page when a focused
  input is smaller, and it does not zoom back out.
- Small-caps labels grew: `.eyebrow` 11.5 → 13.8px, field labels 10.6 → 12.5px,
  button text 11.8 → 13.1px, photo credits 10.2 → 12.2px, `.point` chips
  13.8 → 15.2px. Body copy was already 16px.
- Targets that sat 1–4px apart now clear 8px: the drawer's links, the chapter
  rail, the footer list. The consent checkbox is 26px inside a 44px row.
- `scroll-padding-top` keeps an in-page link from landing under the fixed bar
  and the chapter rail; horizontal rails get `overscroll-behavior-x: contain`
  so a sideways swipe cannot trigger the browser's back gesture; the tap
  highlight is sand rather than the default grey box.
- **The storey chips moved directly under the building** on phones (order on a
  flex `.shell`, 58px rows). The bands on the picture are only ~32px tall
  there — the house is wide and the screen is not — so the chips are the sure
  route and a band's first tap only opens its card.
- Copy that says "hover" is swapped for a tap wording under `@media (hover:
  none)` (`.on-mouse` / `.on-touch`), not by width.

Two CSS traps worth remembering if this gets extended:

1. `[hidden] { display: none !important; }` is set globally. Any component
   with its own `display` (`.cards` had `display: grid`) otherwise ignores
   `el.hidden = true` — that bug was shipping duplicate cards under the table.
2. **Leaflet stacks its panes at z-index 400–800.** The sticky bar sits at 30,
   so in one shared stacking context the map painted its tiles and labels over
   the navigation as soon as it scrolled under it. `.citymap` carries
   `isolation: isolate` to keep those numbers inside the map's own box.
3. `backdrop-filter` and `transform` both make an element a containing block
   for `position: fixed` descendants. Both had trapped a sheet inside a 68px
   bar. `.filters` drops its blur on mobile for this reason.
4. `aspect-ratio` plus `min-height` gets carried back across the ratio into a
   minimum *width*. It pushed the phone layout 76px sideways once (`.photo`)
   and 37px again (`.picker-stage`). Give narrow boxes an explicit height.
5. `overflow: hidden` on any ancestor of the fly-by's `.fly__pin` breaks
   `position: sticky`. Clip inside the pin, never around it.

## Design system

Tokens are at the top of `assets/css/site.css`.

- **Logo:** `assets/brand/P6_logo.svg`, exactly as delivered by the client
  (white on transparent, 878x672 with a 100-unit empty margin). The build
  inlines its paths (`logo()` in `build_pages.py`) with the margin cropped off
  (`viewBox="100 100 678 472"`) and `fill="currentColor"`, so one file serves
  the ink nav bar, the paper-on-ink footer and mobile menu, the favicon (paper
  mark on an ink tile) and the header of every apartment PDF. Replace that
  file and rebuild; if the new artwork has a different extent, re-measure the
  viewBox. The PDFs then need regenerating too.

- Ink `#14120F`, paper `#F7F4EF`, sand accent `#A98C64`
- Status: available `#4E7355`, reserved `#9A7226`, sold `#8A8079`
- Display type Newsreader (self-hosted in `assets/fonts/`, `size-adjust: 92%` so it sits on
  Cormorant's old metrics), UI type Inter (Google Fonts). Cormorant was dropped because its
  Slovak accents are drawn detached — the circumflex on "ô" floated high above the letter.

## Scripts

| File | Role |
|---|---|
| `data.js` | the 50 units + `SHOW_PRICES` / `BUILDING` switches |
| `site.js` | shared helpers, navigation, drawer, forms |
| `plan.js` | schematic floor plans — full on the detail page, compact thumbnails on cards |
| `map.js` | schematic city map, five-minute city, business-zone route |
| `floors.js` | "Vyberte si byt priamo v dome": storey bands on the visualisation, floor card, dive into the storey plan, flat cards, floor strip |
| `fly.js` | hero fly-by: scroll → playhead, copy beats, progress bar; hands decoding to the worker |
| `fly-worker.js` | the fly-by's decoder: WebCodecs → OffscreenCanvas, off the main thread |
| `motion.js` | reveal, count-up, spotlight, chapter scroll-spy |
| `list.js` | unit cards + the brief's six filters (also exports `unitCardHTML`) |
| `detail.js` | single-unit page, plan, room table, sticky CTA |
| `floorplan.js` | storey plans: outlines + letter→flat mapping, `floorPlanHTML()` for the floor view, `mountFloorPlan()` for "Poloha v dome" |

Load order matters: `data.js → site.js → motion.js → plan.js → (map.js | floors.js | list.js | detail.js)`.

## Notes

- Slovak only. If EN/DE is needed later, the cleanest route is a `/en/` copy
  sharing `assets/`, with the labels in `site.js` and `data.js` lifted into a
  dictionary.
- Keyboard: every storey on the building is a link, and focusing one shows
  its card.
- `prefers-reduced-motion` is respected throughout.
