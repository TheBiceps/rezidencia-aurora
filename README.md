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
| `byt.html?id=4.03` | Unit detail: specs, plan linked to the room table, compass, position map, similar units, sticky price bar on phones. |
| `galeria.html` | Photo placeholders for the shots the brief asks for (Miletička, cyclist, Nivy at night, school run, terrace). |
| `kontakt.html` | Contact form + FAQ. `?byt=4.03` prefills the unit; `?katalog=1` prefills a catalogue request (the "Stiahnuť katalóg" CTA lands here until a PDF exists). |
| `lokalita.html`, `projekt.html` | Instant redirects to `index.html#lokalita` / `#projekt` so old links keep working. |

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

## What the brief demands and what is still pending

Done exactly as the brief states:

- Copy for every section, verbatim where the brief supplies it.
- Fictional figures (50 bytov / 8 podlaží / 33–178 m²) removed from all copy,
  the hero, meta tags and schema.org. §12 lists the parameter categories with
  *Upresníme* until real values exist.
- §15 Harmonogram hidden. Set `MILESTONES` in `_build/build_pages.py` to show
  the five-milestone table and its chapter link.
- Interim CTAs after location and after the project; three CTAs in the close.
- Alternating light/dark chapters; higher contrast on small text; wider
  content on large monitors; tighter vertical rhythm; sticky chapter nav;
  mobile keeps the figures, the map, the route and the unit rail horizontally
  scrollable and ships shortened copy (`.long` / `.short`).

Still placeholder — the client must supply these:

- **Real visualisation of P6 with the Downtown panorama** (brief §1). The hero
  keeps the generated facade as an *illustrative* stand-in, labelled as such.
  It is also what powers the interactive unit selector; both are demo geometry.
- **Photos**: Miletička (authentic, not a render), cyclist, Nivy at night,
  school run, community terrace, material shots for the six standard cards.
- **Project parameters** (§12) and the real **unit list** for `data.js`.
- **Standard** (§13) — six cards are written concretely but the building's
  actual standard is unconfirmed; the section says so on the page.
- **Harmonogram dates** (§15).
- **Catalogue PDF** (§16) — wire the href in `final_block()`.
- **Map distances**: `assets/js/map.js` holds each place's km estimate from
  Prievozská 6; every time on the page derives from it. Verify before launch.
  Positions on the map are schematic, not geographic.
- Domain, e-mail and phone are placeholders (`prievozska6.sk`).
- International programmes at Novohradská are listed only as a category —
  the brief says use school-confirmed information only.

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

**Five-minute city** (`[data-citymap="interactive"]`, `assets/js/map.js`)
- Toggle Pešo / Bicyklom / Kolobežkou / Autom; every place on the map gets a
  time, copper for ≤5 min, light for ≤15, dimmed beyond. Category chips
  filter. The list on the right sorts by time and links to the dots on hover.
- The same component draws the static orientation map in §2.
- The business-zone route (§5) reads its times from the same km data.

(The former storey-by-storey scrollytelling section was removed: the brief
rules out claims about setbacks and penthouses until the architecture is
confirmed. `initScrolly()` still exists and is a no-op without markup.)

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
| `plan.js` | schematic floor plans — full on the detail page, compact thumbnails on cards |
| `map.js` | schematic city map, five-minute city, business-zone route |
| `building.js` | placeholder facade geometry, SVG generation, hero selector |
| `motion.js` | reveal, count-up, spotlight, chapter scroll-spy |
| `list.js` | unit cards + the brief's six filters (also exports `unitCardHTML`) |
| `detail.js` | single-unit page, compass, position map, sticky CTA |

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
