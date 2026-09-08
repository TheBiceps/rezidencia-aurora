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
| `index.html` | The whole narrative: hero → orientation map → manifesto → Miletička → business zone → five-minute city → school → Nivy → sport → architecture → community terrace → parameters → standard → units → closing block. Sticky chapter nav (Lokalita / Projekt / Štandard / Byty). |
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
| Parking, cellars | parameters show "Upresníme" |
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

**Hero**
- Hovering a unit in the facade lights it in its status colour, keeps its whole
  storey bright, dims the rest, and shows a card with type, area, orientation
  and price. Click opens the detail.
- Hovering a **legend** entry (Voľný / Rezervovaný / Predaný) lights every unit
  with that status at once — the fastest read of what's still available.
- A one-off sweep runs bottom-up on first load so the affordance needs no copy.
- On scroll the copy lifts away and the building settles. (There is
  deliberately **no** pointer parallax — drifting the facade under the cursor
  read as wobble, not depth. The layer groups still exist in `mountFacade()`
  if it is ever wanted back.)
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

**Map data — where the numbers come from**
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
confirmed. `initScrolly()` still exists and is a no-op without markup.)

**Apartment detail**
- The plan is the architect's rendered drawing for that flat, with his own room
  codes and areas on it; the room table beside it repeats the same figures.
- **"Poloha v dome"** (`assets/js/floorplan.js`) is the storey plan for the
  floor the flat is on. The flat you are viewing is marked and is not a link;
  every other flat on the storey is a hit region that lights up on hover and
  goes to its own page, keyboard included. Status only tints on hover — a plan
  pre-painted in three status colours reads as a heat map and buries the
  drawing.
- On phones the storey plan pans in a rail rather than shrinking: it is a 2.3:1
  letterbox, and squeezed to a phone it lands ~145px tall, too small to read
  nine flats off.
- `←` / `→` walk through the building in order.

  *A compass used to point at the flat's orientation; it was removed because
  nothing in the client's material states which way the building faces, and the
  earlier abstract elevation was replaced by the real storey plan.*

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
- **Waiting on:** `assets/img/skola-novohradska.jpg` (§7 aerial of Spojená
  škola Novohradská). The markup, alt text and credit are already wired to
  that exact path — dropping the file in is the whole job.

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

- **The hero scroll fade is desktop-only.** On a phone the copy sits *below*
  the picture and is the main content, so fading it on scroll just greyed the
  page out over the blue hero background.
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
- **The legend is tappable**, since hovering it does nothing on a phone.
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
- **Tapping a flat in the facade opens a bottom sheet** with the details and a
  full-width *Zobraziť detail* button. Hotspots are ~28x46px on a 375px screen
  because the building is simply wide relative to a phone; the sheet makes an
  imprecise tap cost one extra tap instead of a wrong page. The floor strip
  under the hero is the precise route.
- **The floor plan switches to a portrait 420x520 box** so its labels render
  around 11px rather than 7px.
- `--nav-h` drops to 64px.

Two CSS traps worth remembering if this gets extended:

1. `[hidden] { display: none !important; }` is set globally. Any component
   with its own `display` (`.cards` had `display: grid`) otherwise ignores
   `el.hidden = true` — that bug was shipping duplicate cards under the table.
2. `backdrop-filter` and `transform` both make an element a containing block
   for `position: fixed` descendants. Both had trapped a sheet inside a 68px
   bar. `.filters` drops its blur on mobile and `.hero__vis` is only
   transformed on desktop for this reason.

## Design system

Tokens are at the top of `assets/css/site.css`.

- Ink `#14120F`, paper `#F7F4EF`, sand accent `#A98C64`
- Status: available `#4E7355`, reserved `#9A7226`, sold `#8A8079`
- Display type Cormorant Garamond, UI type Inter (both Google Fonts, latin-ext)

## Scripts

| File | Role |
|---|---|
| `data.js` | the 50 units + `SHOW_PRICES` / `BUILDING` switches |
| `site.js` | shared helpers, navigation, drawer, forms |
| `plan.js` | schematic floor plans — full on the detail page, compact thumbnails on cards |
| `map.js` | schematic city map, five-minute city, business-zone route |
| `building.js` | placeholder facade geometry, SVG generation, hero selector |
| `motion.js` | reveal, count-up, spotlight, chapter scroll-spy |
| `list.js` | unit cards + the brief's six filters (also exports `unitCardHTML`) |
| `detail.js` | single-unit page, plan, room table, sticky CTA |
| `floorplan.js` | "Poloha v dome" — clickable storey plan, outlines + letter→flat mapping |

Load order matters: `data.js → site.js → motion.js → plan.js → (map.js | building.js | list.js | detail.js)`.

Two facades can appear on one page (hero + scrollytelling), so **SVG gradient
ids are namespaced per mount** (`mountFacade(el, { ns: 'scrolly' })`). Reusing a
plain `id="sky"` would make the second facade silently read the first one's
gradients.

## Notes

- Slovak only. If EN/DE is needed later, the cleanest route is a `/en/` copy
  sharing `assets/`, with the labels in `site.js` and `data.js` lifted into a
  dictionary.
- The scrollytelling section is ~5 viewports tall. If that feels long, drop a
  step in `index.html` — the engine reads however many `[data-step]` elements
  it finds.
- On phones the facade hotspots are ~28px tall — the building is simply wide
  relative to a phone screen. First tap previews, second tap opens, and the
  floor strip under the hero plus the full list page are the reliable paths.
- Keyboard: every unit in the facade is tabbable with a visible focus ring.
- `prefers-reduced-motion` is respected throughout.
