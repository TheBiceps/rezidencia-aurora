# Rezidencia Aurora — website

Static site for a single residential building in Bratislava. No build step, no
dependencies: plain HTML + one stylesheet + four small scripts. Open
`index.html` or serve the folder.

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

The repo is the site — GitHub Pages serves it straight from `main`. To publish
a change:

```bash
cd rezidencia && git add -A && git commit -m "update" && git push
```

Pages rebuilds in about a minute. `.nojekyll` is present so nothing gets
filtered by Jekyll.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Landing page. Hero = interactive facade; hovering / tapping a unit shows its card, clicking opens the detail. |
| `byty.html` | Full unit list. Filter by status, layout, floor, area, price. Table ⇄ card view, sortable columns. Accepts `?floor=`, `?rooms=`, `?status=`. |
| `byt.html?id=4.03` | Single-unit detail: specs, schematic plan, room areas, price, prev/next, similar units. |
| `projekt.html` | About the building, standard, timeline, layout typologies. |
| `lokalita.html` | Location, amenities, views. |
| `galeria.html` | Gallery. |
| `kontakt.html` | Contact form. Accepts `?byt=4.03` to prefill. |

## The one file you edit

**`assets/js/data.js`** holds all 50 units. Everything on the site — hero
selector, list, filters, detail pages, counters — reads from it. Field
documentation is in the header of that file.

Two switches live at the top:

- `SHOW_PRICES` — set to `false` to render "Na vyžiadanie" everywhere instead of prices.
- `BUILDING` — name, address, floor/unit counts.

Per-unit, `price: null` renders "Cena na vyžiadanie" for just that unit.

⚠️ The current 50 records are **placeholder data** generated for layout
purposes. Replace them with the real unit list.

## Placeholders still to fill

- **Building visualisation.** `assets/js/building.js` draws the facade as SVG
  from the same geometry that positions the clickable hotspots, so the two
  cannot drift apart. When the real render arrives, put it behind
  `.hero__vis` and keep this file for the hotspot layer only — then nudge the
  `ART` constants at the top until the rects land on the real windows.
- **Photos and virtual tours.** Every `.ph` block is a labelled placeholder
  tile. Search the HTML for `class="ph` to find them all.
- **Floor plans.** `planSVG()` in `assets/js/detail.js` draws a schematic from
  `roomList`. Swap it for the real PDF/PNG plans when available.
- **Map.** `lokalita.html` has a `.map-frame` ready for a Maps embed.
- **Contact form.** `initForms()` in `assets/js/site.js` currently just shows
  the success state. Point it at a real endpoint (Formspree / API / CRM webhook).
- **Copy and figures.** Project name, street address, phone, e-mail, timeline,
  distances and the standard description are all placeholder text.
- **Domain.** Canonical/OG URLs and `sitemap.xml` use
  `https://rezidencia-aurora.sk`.

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

**Scrollytelling — "Dom po podlažiach"** (`[data-scrolly]` on the landing page)
- The building is pinned while five steps scroll past; each highlights the
  storeys it talks about.
- The sky runs from late morning to dusk across the section and the windows
  light up as it gets dark — driven by `setSkyTime()` in `building.js`.
- Steps, sky and the progress rail all come off one shared scroll loop
  (`onFrame` in `motion.js`), so there is a single rAF per frame.

**Apartment detail**
- Hovering a room in the plan highlights its row in the table, and vice versa.
- A clickable elevation shows where the flat sits in the building; every other
  unit is one click away, colour-coded by status.
- A compass points at the flat's orientation.
- `←` / `→` walk through the building in order.

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
| `building.js` | facade geometry, SVG generation, sky/time, hero selector |
| `motion.js` | reveal, count-up, parallax, spotlight, scrollytelling |
| `list.js` | filtering, sorting, table ⇄ card views |
| `detail.js` | single-unit page, plan, compass, position map |

Load order matters: `data.js → site.js → motion.js → building.js → page script`.

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
