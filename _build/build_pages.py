# -*- coding: utf-8 -*-
# ===========================================================================
#  PAGE GENERATOR — optional.
#
#  The .html files in the parent folder ARE the deliverable and can be edited
#  by hand. This script regenerates all of them from the templates below; it
#  exists so shared chrome (nav, footer, <head>) can be changed in one place.
#
#  ⚠️  RUNNING THIS OVERWRITES EVERY .html FILE.
#
#  Usage, from the folder ABOVE `rezidencia/`:
#      python3 rezidencia/_build/build_pages.py
#
#  Page order and copy follow the client brief P6_zmeny.docx section by
#  section; the section numbers in the comments below are the brief's.
# ===========================================================================
import json
import os
import re
OUT = "rezidencia"

SITE = "https://prievozska6.sk"          # placeholder domain — confirm with client
NAME = "P6"
ADDRESS = "Prievozská 6, 821 09 Bratislava-Ružinov"

# Every photo on the site is currently an AI-generated stand-in, several of real
# named places (Miletička, the school, Nivy, the Danube). They carry a small
# "illustrative" credit so nobody takes them for photographs of those places.
# Set to None once the real photography is in and the labels all disappear.
DEMO_IMG = "Ilustračný obrázok"
EMAIL = "info@prievozska6.sk"            # placeholder
PHONE = "+421 900 000 000"               # placeholder

# Client-preview build: noindex everywhere, robots blocks crawlers.
PREVIEW = True

# Bump whenever CSS/JS changes — appended as ?v= to every asset link.
ASSET_V = "61"

# Mandated by the architect (Ing. arch. Martin Krajči) — must stay visible
# wherever plans or areas are shown.
DISCLAIMER = ("Uvedené výmery sú orientačné a vychádzajú z podkladov architekta. "
              "Ide o rekonštrukciu existujúceho skeletu, preto sú možné odchýlky "
              "a plochy sa môžu zmeniť. Výmery balkónov nie sú definitívne potvrdené. "
              "Investor si vyhradzuje právo na zmeny.")

# Brief §15: show the milestone table only with confirmed dates; otherwise
# leave the section out. Fill in to render it, e.g.
#   MILESTONES = [("Spustenie predaja", "jar 2026"), ("Začiatok výstavby", "leto 2026"),
#                 ("Hrubá stavba", "2027"), ("Kolaudácia", "2028"), ("Odovzdávanie bytov", "2028")]
MILESTONES = None

NAV = [
    ("index.html#lokalita", "Lokalita"),
    ("index.html#projekt", "Projekt"),
    ("byty.html", "Byty"),
    ("galeria.html", "Galéria"),
    ("kontakt.html", "Kontakt"),
]

I = {
 "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "x": '<path d="M6 6l12 12M18 6L6 18"/>',
 "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 "camera": '<path d="M14.5 4h-5L8 6H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-4l-1.5-2Z"/><circle cx="12" cy="13" r="3.5"/>',
 "cube": '<path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
 "check": '<path d="m5 13 4 4L19 7"/>',
 "cursor": '<path d="m4 4 7 16 2.5-6.5L20 11 4 4Z"/>',
 "swipe": '<path d="M4 12h13M13 8l4 4-4 4"/>',
 "sliders": '<path d="M4 6h10M18 6h2M4 12h2M10 12h10M4 18h10M18 18h2"/><circle cx="16" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="16" cy="18" r="2"/>',
 "tram": '<rect x="5" y="3" width="14" height="13" rx="3"/><path d="M5 10h14M9 20l-2 2M15 20l2 2M9 16v4M15 16v4"/>',
 "bus": '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M8 18v2M16 18v2M8 14h.01M16 14h.01"/>',
 "bike": '<circle cx="6" cy="17" r="3.5"/><circle cx="18" cy="17" r="3.5"/><path d="M6 17 9.5 9h4l3 8M12 9l2-4h3"/>',
 "road": '<path d="M4 21 9 3h6l5 18M12 6v3M12 12v3M12 18v3"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
}

# The project logo exactly as the client delivered it (assets/brand/P6_logo.svg:
# white on transparent, with 100 units of empty margin all round). It is inlined
# rather than linked so it takes the text colour of wherever it sits — ink in
# the bar, paper in the footer — and the viewBox crops that margin off, which
# is the mark's measured extent (100,100 → 778,572).
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "brand", "P6_logo.svg"),
          encoding="utf-8") as _f:
    LOGO_PATHS = re.findall(r' d="([^"]+)"', _f.read())
LOGO_VIEWBOX = "100 100 678 472"

def logo(cls="logo", label=None, fill="currentColor"):
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    paths = "".join(f'<path d="{d}"/>' for d in LOGO_PATHS)
    return (f'<svg class="{cls}" viewBox="{LOGO_VIEWBOX}" fill="{fill}" {a11y} focusable="false">'
            f'{paths}</svg>')

def svg(key, cls="", extra=""):
    c = f'class="{cls}" ' if cls else ""
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" {c}{extra}>{I[key]}</svg>')

def txt(long, short=None):
    """Brief: shorten copy on phones. Both versions ship; CSS picks."""
    if not short:
        return long
    return f'<span class="long">{long}</span><span class="short">{short}</span>'

# ---------------------------------------------------------------- chrome

def head(title, desc, page, extra=""):
    noindex = '<meta name="robots" content="noindex, nofollow">' if PREVIEW else ""
    return f'''<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}/{page}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="sk_SK">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/{page}">
<meta name="theme-color" content="#14120F">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{noindex}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" href="assets/fonts/newsreader-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v={ASSET_V}">
{extra}</head>
<body>
<a class="skip-link" href="#main">Preskočiť na obsah</a>
'''

def nav(page, over=False):
    def cur(h): return ' aria-current="page"' if h == page else ""
    links = "".join(f'<a class="nav__link" href="{h}"{cur(h)}>{t}</a>' for h, t in NAV)
    dlinks = "".join(f'<a class="drawer__link" href="{h}"{cur(h)}>{t}</a>' for h, t in NAV)
    return f'''<header class="nav {"nav--over" if over else "nav--solid"}" data-nav="{"over" if over else "solid"}">
  <div class="nav__inner">
    <a class="brand" href="index.html" aria-label="{NAME}, domov">
      <span class="brand__mark">{logo("brand__logo")}</span>
      <span class="brand__sub">Prievozská 6</span>
    </a>
    <nav class="nav__links" aria-label="Hlavná navigácia">{links}</nav>
    <div class="nav__actions">
      <a class="btn btn--ghost nav__cta" href="kontakt.html">Dohodnúť konzultáciu</a>
      <button class="nav__burger" type="button" data-drawer-open aria-expanded="false" aria-controls="drawer" aria-label="Otvoriť menu">{svg("menu")}</button>
    </div>
  </div>
  <div class="readbar"><span data-readbar></span></div>
</header>

<div class="drawer" id="drawer" data-drawer data-open="false" aria-hidden="true">
  <div class="drawer__top">
    <a class="brand" href="index.html" aria-label="{NAME}, domov"><span class="brand__mark">{logo("brand__logo")}</span><span class="brand__sub">Prievozská 6</span></a>
    <button class="drawer__close" type="button" data-drawer-close aria-label="Zavrieť menu">{svg("x")}</button>
  </div>
  <nav class="drawer__links" aria-label="Mobilná navigácia">{dlinks}</nav>
  <div class="drawer__foot">
    <a href="tel:{PHONE.replace(' ', '')}">{PHONE}</a>
    <a href="mailto:{EMAIL}">{EMAIL}</a>
  </div>
</div>
'''

FOOT = f'''<footer class="foot">
  <div class="shell shell-wide">
    <div class="foot__grid">
      <div>
        <div class="foot__brand">{logo("foot__logo", NAME)}</div>
        <p style="color:var(--text-inv-muted);max-width:38ch;font-size:.95rem">
          Mestské bývanie na Prievozskej 6. Miletička, škola, biznis zóna, Nivy aj nové centrum Bratislavy v prirodzenom dosahu.
        </p>
        <address class="foot__addr">{ADDRESS}</address>
      </div>
      <div>
        <h4>Navigácia</h4>
        <ul>
          <li><a href="index.html#lokalita">Lokalita</a></li>
          <li><a href="index.html#projekt">Projekt</a></li>
          <li><a href="index.html#standard">Štandard</a></li>
          <li><a href="byty.html">Byty</a></li>
          <li><a href="galeria.html">Galéria</a></li>
          <li><a href="kontakt.html">Kontakt</a></li>
        </ul>
      </div>
      <div>
        <h4>Predaj</h4>
        <ul>
          <li><a href="tel:{PHONE.replace(' ', '')}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><span style="color:var(--text-inv-muted);font-size:.92rem">Po až Pi, 9:00 až 18:00</span></li>
        </ul>
      </div>
    </div>
    <div class="foot__bottom">
      <span>© <span data-year>2026</span> {NAME}, Prievozská 6. Všetky práva vyhradené.</span>
      <span>Vizualizácie sú ilustračné. Uvedené časy a vzdialenosti sú orientačné. Informácie na stránke nie sú návrhom na uzavretie zmluvy.</span>
    </div>
  </div>
</footer>
'''

def scripts(*extra):
    s = ''.join(f'<script src="assets/js/{n}?v={ASSET_V}"></script>\n' for n in ('data.js', 'site.js', 'motion.js'))
    for e in extra:
        s += f'<script src="assets/js/{e}?v={ASSET_V}"></script>\n'
    return s + "</body>\n</html>\n"

def photo(title, cap, cls="", ico="camera", src=None, alt="", credit=None):
    """Photo tile that degrades to a designed placeholder.

    The tile ships as the placeholder and only becomes a photo frame once the
    image actually decodes (`has-img` is added by onload, never by the build).
    Doing it the other way round -- shipping `has-img` and stripping it on
    error -- leaves an empty box whenever the load never happens at all, which
    is exactly what `loading="lazy"` does to anything below the fold."""
    img = cred = ""
    if src:
        # version the URL like the CSS/JS: replacing a photo in place otherwise
        # leaves returning visitors (and the Pages CDN) on the cached old file
        if not src.startswith(("http:", "https:", "data:")) and "?" not in src:
            src = f"{src}?v={ASSET_V}"
        img = (f'<img class="photo__img" src="{src}" alt="{alt}" loading="lazy" decoding="async"'
               f' onload="this.closest(\'.photo\').classList.add(\'has-img\')"'
               f' onerror="this.remove()">')
        if credit:
            cred = f'<figcaption class="photo__credit">{credit}</figcaption>'
    return (f'<figure class="{("photo " + cls).strip()}">{img}{svg(ico)}<b>{title}</b>'
            f'<span class="photo__cap">{cap}</span>{cred}</figure>')

def page_head(crumb, title, lede, current):
    c = f'''<nav class="crumbs" aria-label="Omrvinková navigácia" style="margin-bottom:22px">
      <a href="index.html">Domov</a><span aria-hidden="true">/</span><span>{crumb}</span></nav>''' if crumb else ""
    return f'''<section class="page-head">
  <div class="shell">
    {c}
    <p class="eyebrow">{current}</p>
    <h1>{title}</h1>
    <p class="lede maxw">{lede}</p>
  </div>
</section>'''

def cta_slim(text, primary=("Pozrieť dostupné byty", "byty.html?status=dostupny"), secondary=("Dohodnúť konzultáciu", "kontakt.html"), cls="section--paper2"):
    return f'''<section class="cta-slim {cls}">
  <div class="shell cta-slim__inner">
    <p class="cta-slim__text">{text}</p>
    <div class="cta-slim__actions">
      <a class="btn btn--primary" href="{primary[1]}">{primary[0]} {svg("arrow")}</a>
      <a class="btn btn--ghost" href="{secondary[1]}">{secondary[0]}</a>
    </div>
  </div>
</section>
'''

# Brief §16 — the closing block, also reused under the unit list and detail.
def final_block():
    return f'''<section class="section section--ink final" id="kontakt-cta">
  <div class="shell">
    <div class="grid-2">
      <div>
        <p class="eyebrow">Ďalší krok</p>
        <h2>Objavte bývanie<br>v správnej<br><em style="font-style:italic;color:var(--sand-2)">vzdialenosti</em></h2>
      </div>
      <div>
        <p class="lede">Povedzte nám, aký byt hľadáte. Predstavíme vám dostupné dispozície, orientáciu, exteriérové priestory aj ďalší postup.</p>
        <div class="final__actions">
          <a class="btn btn--light" href="byty.html?status=dostupny">Pozrieť dostupné byty {svg("arrow")}</a>
          <a class="btn btn--onink" href="kontakt.html">Dohodnúť konzultáciu</a>
          <a class="btn btn--onink" href="kontakt.html?katalog=1">Stiahnuť katalóg</a>
        </div>
      </div>
    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------- content

FAQ = [
 ("Ako prebieha rezervácia bytu?", "Vyberiete si byt, podpíšeme rezervačnú zmluvu a uhradíte rezervačný poplatok. Byt stiahneme z ponuky a pripravíme zmluvu o budúcej kúpnej zmluve."),
 ("Dá sa dispozícia bytu upraviť?", "Áno, klientske zmeny riešime individuálne do uzávierky, ktorú si dohodneme pri podpise zmluvy."),
 ("Je možné kúpiť parkovacie státie?", "Áno. Pred domom je 50 parkovacích miest. Parkovacie státia a pivničné kobky sa predávajú samostatne k jednotlivým bytom."),
 ("Ponúkate virtuálnu prehliadku?", "Pripravujeme ju. Po dokončení fotodokumentácie sprístupníme 3D prehliadku každej dispozície priamo v detaile bytu."),
 ("Ako získam katalóg?", "Napíšte nám cez formulár a katalóg vám pošleme e-mailom hneď, ako bude pripravený."),
]

# §13 — six cards, one concrete benefit each, two sentences at most.
# ⚠️ Standard is NOT yet confirmed by the project — the page says so.
# The brief names only the card TOPICS. Parking and common spaces are now as the
# investor stated them (WhatsApp, 2026-09-15): no garage — 50 spaces in front of
# the building; chip entry, community terrace, gym. EV charging is unconfirmed,
# so it is marked "upresníme" rather than promised.
STANDARD = [
 ("Svetlo a okná",                    "Veľkoformátové okná s izolačným trojsklom. Viac denného svetla v izbách, menej hluku z ulice.",                        "detail: okenný profil a sklo", "std-okna"),
 ("Vykurovanie a chladenie",          "Podlahové kúrenie v celom byte s prípravou na chladenie. Stála teplota bez radiátorov na stenách.",                 "detail: podlahové kúrenie", "std-kurenie"),
 ("Kúpeľne",                          "Veľkoformátový obklad a zabudované zariaďovacie predmety. Kúpeľňa pripravená na bývanie od prvého dňa.",           "detail: obklad kúpeľne", "std-kupelna"),
 ("Podlahy a interiérové dvere",      "Drevené podlahy v obytných miestnostiach a dvere v jednotnom dizajne. Jeden detail od predsiene po spálňu.",        "detail: podlaha a dvere", "std-podlahy"),
 ("Parkovanie a nabíjanie",           "50 parkovacích miest priamo pred domom. Možnosť nabíjania elektromobilov upresníme.",                               "detail: parkovanie pred domom", "std-parkovanie"),
 ("Bezpečnosť a spoločné priestory",  "Čipový vstup do domu. Obyvatelia majú k dispozícii komunitnú terasu a fitness.",                                   "detail: čipový vstup do domu", "std-vstup"),
]

# §12 — categories the brief wants listed here; values pending real data.
# From the architect's floor plans. Anything not on the drawings stays None.
PARAMS = [
 ("Počet bytov", "44"),
 ("Počet podlaží", "5 nadzemných"),
 ("Typológie", "1- až 3-izbové"),
 ("Výmery bytov", "30,1 až 77,9 m²"),
 ("Balkóny", "8,5 až 18,3 m²"),
 ("Parkovacie miesta", "50, pred domom"),
 ("Pivničné kobky", "1,5 až 3,0 m²"),
]

def index_html():
    ld = '''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ApartmentComplex","name":"P6",
"address":{"@type":"PostalAddress","streetAddress":"Prievozská 6","addressLocality":"Bratislava","addressRegion":"Ružinov","postalCode":"821 09","addressCountry":"SK"},
"url":"''' + SITE + '''/"}
</script>
'''
    chapters = [("#lokalita", "Lokalita"), ("#projekt", "Projekt"), ("#standard", "Štandard"), ("#byty", "Byty")]
    if MILESTONES: chapters.append(("#harmonogram", "Harmonogram"))
    chap = "".join(f'<a class="chapters__link" href="{h}">{t}</a>' for h, t in chapters)

    std = "".join(f'''<article class="std__card reveal">
        {photo("Fotografia materiálu", cap, "photo--flush", "camera",
               src=f"assets/img/{img}.webp", alt=f"{t}, ilustračný detail", credit=DEMO_IMG)}
        <div class="std__body"><h3>{t}</h3><p>{d}</p></div>
      </article>''' for t, d, cap, img in STANDARD)

    params = "".join(
        f'<div class="params__item"><dt>{k}</dt><dd{"" if v else " class=\"is-tbd\""}>{v or "Upresníme"}</dd></div>'
        for k, v in PARAMS)

    harmonogram = ""
    if MILESTONES:
        rows = "".join(f'<div class="tl"><dt>{k}</dt><dd><b>{v}</b></dd></div>' for k, v in MILESTONES)
        harmonogram = f'''<section class="section section--paper2" id="harmonogram">
  <div class="shell"><div class="grid-2" style="align-items:start">
    <div><p class="eyebrow">Harmonogram</p><h2>Míľniky projektu</h2></div>
    <div class="timeline">{rows}</div>
  </div></div>
</section>
'''

    return (head("P6 | Domov medzi Miletičkou a Downtownom",
                 "Mestské bývanie na Prievozskej 6. Trh, škola, práca, Nivy aj nové centrum Bratislavy v prirodzenom dosahu.",
                 "", ld)
    + nav("index.html", over=True)
    + f'''<main id="main">

<!-- §1 Hero — scroll-driven fly-by of the real visualisation ============ -->
<!-- Without JS, or with reduced motion, this is an ordinary one-screen hero on
     the render's first frame. fly.js adds .is-live, which makes the section
     tall and lets the scroll position drive the video. -->
<section class="fly" data-fly aria-label="P6, Prievozská 6"
         data-fly-wide="assets/fly/p6-fly-wide" data-fly-tall="assets/fly/p6-fly-tall" data-fly-v="{ASSET_V}">
  <div class="fly__pin">
    <div class="fly__media">
      <img class="fly__poster" src="assets/fly/poster-1600.webp?v={ASSET_V}"
           srcset="assets/fly/poster-960.webp?v={ASSET_V} 960w, assets/fly/poster-1600.webp?v={ASSET_V} 1600w"
           sizes="100vw" width="1600" height="900" fetchpriority="high"
           alt="Vizualizácia bytového domu P6 na Prievozskej ulici: päťpodlažný dom so zelenými balkónmi a strešnou terasou">
      <canvas class="fly__canvas" data-fly-canvas aria-hidden="true"></canvas>
      <video class="fly__video" data-fly-video muted playsinline preload="none" aria-hidden="true" tabindex="-1"></video>
      <div class="fly__scrim" aria-hidden="true"></div>
      <span class="fly__label">Vizualizácia</span>
    </div>

    <div class="fly__copy">
      <div class="shell shell-wide">
        <div class="fly__beat is-on" data-beat="0">
          <p class="hero__kicker"><span></span> Prievozská 6 · Bratislava-Ružinov</p>
          <h1 class="hero__title">Domov medzi<br>Miletičkou a <em>Downtownom</em></h1>
          <p class="hero__sub">Mestské bývanie na Prievozskej 6. Trh, škola, práca, Nivy aj nové centrum Bratislavy v prirodzenom dosahu.</p>
          <div class="hero__actions">
            <a class="btn btn--light" href="byty.html?status=dostupny">Pozrieť dostupné byty {svg("arrow")}</a>
            <a class="btn btn--onink" href="#vyber-bytu">Vybrať byt v dome</a>
          </div>
        </div>
        <div class="fly__beat" data-beat="1">
          <p class="eyebrow">Projekt</p>
          <p class="fly__big">44 bytov</p>
          <p class="fly__line">1- až 3-izbové, každý s vlastným balkónom.</p>
        </div>
        <div class="fly__beat" data-beat="2">
          <p class="eyebrow">Pre obyvateľov</p>
          <p class="fly__big">Komunitná terasa a fitness</p>
          <div class="hero__actions">
            <a class="btn btn--light" href="byty.html?status=dostupny">Pozrieť dostupné byty {svg("arrow")}</a>
          </div>
        </div>
      </div>
    </div>

    <div class="fly__progress" aria-hidden="true"><span data-fly-bar></span></div>
    <a class="hero__cue fly__cue" href="#vyber-bytu" aria-label="Prejsť na výber bytu">
      <span class="hero__cue-line"></span>
      <span>Posúvajte</span>
    </a>
  </div>
</section>

<!-- §1b Apartment picker — the investor's visualisation of the facade, every
     storey a hover band with its free / reserved / sold count (floors.js). -->
<section class="section picker-sec" id="vyber-bytu">
  <div class="shell shell-wide">
    <div class="picker-sec__head">
      <div>
        <p class="eyebrow">Výber bytu</p>
        <h2>Vyberte si byt priamo v dome</h2>
      </div>
      <p class="picker-sec__note">
        <span class="on-mouse">Prejdite myšou po podlažiach domu a uvidíte, koľko bytov je na nich voľných. Kliknutím otvoríte pôdorys podlažia a vyberiete si byt.</span>
        <span class="on-touch">Ťuknite na podlažie a uvidíte, koľko bytov je na ňom voľných. Ďalším ťuknutím otvoríte pôdorys podlažia a vyberiete si byt.</span>
      </p>
    </div>

    <div class="bldg" data-bldg>
      <svg class="bldg__svg" viewBox="0 0 2560 1440" preserveAspectRatio="xMidYMid slice"
           role="group" aria-label="Vizualizácia domu P6, výber podlažia">
        <image class="bldg__img" data-bldg-img width="2560" height="1440" preserveAspectRatio="none"
               data-src-sm="assets/img/p6-dom-1280.webp?v={ASSET_V}"
               data-src-md="assets/img/p6-dom-1920.webp?v={ASSET_V}"
               data-src-lg="assets/img/p6-dom-2560.webp?v={ASSET_V}"/>
        <g data-floors></g>
      </svg>
      <noscript><img class="bldg__fallback" src="assets/img/p6-dom-1920.webp?v={ASSET_V}" width="1920" height="1080"
           alt="Vizualizácia bytového domu P6 z Prievozskej ulice"></noscript>
      <span class="bldg__label">Vizualizácia</span>
      <div class="tip tip--floor" data-tip data-show="false" role="status" aria-live="polite"></div>
    </div>

    <div class="picker-sec__foot">
      <div class="legend">
        <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--ok"></span>Voľný</span>
        <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--warn"></span>Rezervovaný</span>
        <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--off"></span>Predaný</span>
      </div>
      <span class="picker__hint">{svg("cursor")} <span data-bldg-hint>Vyberte podlažie priamo na dome</span></span>
    </div>

    <div class="floorstrip-wrap" style="margin-top:26px">
      <p class="eyebrow">Alebo podľa podlažia</p>
      <div class="floorstrip" data-floorstrip></div>
    </div>
  </div>
</section>
<div data-nav-sentinel aria-hidden="true"></div>

<nav class="chapters" data-chapters aria-label="Kapitoly">
  <div class="shell shell-wide chapters__inner">
    <span class="chapters__label">Kapitoly</span>
    {chap}
  </div>
</nav>

<!-- §2 Okamžitá orientácia ============================================ -->
<section class="section" id="lokalita">
  <div class="shell shell-wide">
    <div style="max-width:60ch;margin-bottom:clamp(24px,3vw,36px)">
      <p class="eyebrow">Okamžitá orientácia</p>
      <h2>Všetko podstatné<br>v správnej vzdialenosti</h2>
    </div>
    <div class="citymap" data-citymap="static" data-theme="light">
      <div data-map-stage></div>
      <span class="citymap__note">Časy merané po reálnych trasách z Prievozskej 6</span>
    </div>

    <div class="keyfigs" style="margin-top:clamp(26px,3vw,40px)">
      <div class="keyfig"><b>2 min</b><span>pešo na zastávku MHD Miletičova</span></div>
      <div class="keyfig"><b>75 m</b><span>Apollo Business Center II</span></div>
      <div class="keyfig"><b>7 min</b><span>pešo do školy Novohradská</span></div>
      <div class="keyfig"><b>do 1,5 km</b><span>Nivy, Nivy Tower, CBC, Twin City, Sky Park</span></div>
      <div class="keyfig"><b>15 až 20 min</b><span>autom na letisko Bratislava</span></div>
    </div>
  </div>
</section>

<!-- §3 Hlavný manifest ================================================ -->
<section class="section section--ink manifest">
  <div class="shell">
    <div class="grid-2" style="align-items:end">
      <h2>Menej času<br>na cestách.<br><em>Viac času<br>na život.</em></h2>
      <p class="lede">{txt(
        "Kvalita bývania sa neukazuje iba vo výmere bytu. Ukazuje sa každé ráno, v ceste do práce, do školy, na nákup alebo za športom. P6 približuje všetko, čo tvorí každodenný mestský život.",
        "Kvalita bývania sa ukazuje každé ráno, v ceste do práce, do školy či na nákup. P6 približuje všetko, čo tvorí mestský život.")}</p>
    </div>
  </div>
</section>

<!-- §4 Miletička ======================================================= -->
<section class="section">
  <div class="shell shell-wide">
    {photo("Trhovisko Miletičova", "Fotografia · autentická, nie render", "photo--wide reveal",
           src="assets/img/mileticka.webp", credit=DEMO_IMG,
           alt="Trhovisko Miletičova: rady stánkov s ovocím, zeleninou a kvetmi")}
    <div class="grid-2" style="margin-top:clamp(30px,4vw,52px);align-items:start">
      <div class="reveal">
        <p class="eyebrow">Každodenný život</p>
        <h2>Niektorí kupujú potraviny.<br>Iní si kupujú ráno.</h2>
      </div>
      <div class="reveal">
        <p class="lede">{txt(
          "Trhovisko Miletičova je jedným z miest, ktoré dávajú Bratislave jej charakter. Čerstvé potraviny, kvety, pekárne, lokálni predajcovia a sobotný ranný rytmus. Z P6 nemusí byť návšteva trhu programom. Môže byť prirodzenou súčasťou každého týždňa.",
          "Trhovisko Miletičova dáva Bratislave charakter: čerstvé potraviny, kvety, pekárne, lokálni predajcovia. Z P6 je návšteva trhu prirodzenou súčasťou týždňa.")}</p>
        <ul class="points">
          <li class="point">čerstvé potraviny</li>
          <li class="point">lokálni predajcovia</li>
          <li class="point">13 minút pešo · 7 minút bicyklom</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- §5 Práca a biznis zóna ============================================ -->
<section class="section section--paper2">
  <div class="shell shell-wide">
    <div class="grid-2" style="align-items:start;margin-bottom:clamp(30px,4vw,52px)">
      <div class="reveal">
        <p class="eyebrow">Práca a biznis zóna</p>
        <h2>Bývajte bližšie k tomu,<br>čo tvorí váš deň</h2>
      </div>
      <p class="lede reveal">{txt(
        "Prievozská, Plynárenská a Mlynské nivy tvoria hlavnú biznis zónu Bratislavy. Apollo Business Center II sa nachádza prakticky v susedstve P6. Twin City, Nivy Tower, CBC a Sky Park sú dostupné pešo alebo na bicykli.",
        "Prievozská, Plynárenská a Mlynské nivy tvoria hlavnú biznis zónu Bratislavy. Apollo Business Center II je prakticky v susedstve; Twin City, Nivy Tower, CBC a Sky Park sú na dosah pešo či na bicykli.")}</p>
    </div>
    <ol class="route" data-route></ol>
  </div>
</section>

<!-- §6 Päťminútové mesto ============================================== -->
<section class="section section--ink" id="patminutove-mesto">
  <div class="shell shell-wide">
    <div style="max-width:60ch;margin-bottom:clamp(24px,3vw,36px)">
      <p class="eyebrow">Päťminútové mesto</p>
      <h2>Prepnite si spôsob dopravy.<br>Mesto sa prispôsobí.</h2>
      <p class="lede" style="margin-top:18px">Zastávka MHD je pred domom, kaviareň, brunch bar, indická reštaurácia aj sushi do troch minút pešo. Vyberte si kategóriu a mapa ukáže, čo máte naozaj po ruke.</p>
    </div>
    <div class="fivemin" data-citymap="interactive" data-theme="dark">
      <div>
        <div class="fivemin__controls">
          <div class="seg" role="group" aria-label="Spôsob dopravy">
            <button type="button" data-mode="pesi" aria-pressed="true">Pešo</button>
            <button type="button" data-mode="bicykel" aria-pressed="false">Bicyklom</button>
            <button type="button" data-mode="auto" aria-pressed="false">Autom</button>
          </div>
          <div class="chips" role="group" aria-label="Kategórie">
            <button type="button" class="chip" data-cat="all" aria-pressed="true">Všetko</button>
            <button type="button" class="chip" data-cat="praca" aria-pressed="false">Práca</button>
            <button type="button" class="chip" data-cat="skola" aria-pressed="false">Škola</button>
            <button type="button" class="chip" data-cat="doprava" aria-pressed="false">Doprava</button>
            <button type="button" class="chip" data-cat="nakupy" aria-pressed="false">Nákupy</button>
            <button type="button" class="chip" data-cat="sport" aria-pressed="false">Šport</button>
            <button type="button" class="chip" data-cat="gastro" aria-pressed="false">Gastronómia</button>
            <button type="button" class="chip" data-cat="volnycas" aria-pressed="false">Voľný čas</button>
          </div>
        </div>
        <div class="citymap citymap--dark citymap--interactive">
          <div data-map-stage></div>
          <span class="citymap__note">medená = do 5 min · sivá = do 15 min</span>
        </div>
      </div>
      <div>
        <ol class="reach" data-reach-list></ol>
        <p class="form__note" style="margin-top:14px;color:var(--text-inv-muted)">
          Kliknutím na miesto sa naň mapa priblíži.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- §7 Rodina a škola ================================================= -->
<section class="section">
  <div class="shell shell-wide">
    <div class="reveal">{photo(
      "Spojená škola Novohradská", "Fotografia bude doplnená",
      "photo--air", "camera",
      src="assets/img/skola-novohradska.webp",
      alt="Letecký pohľad na areál Spojenej školy Novohradská: školské budovy, bežecký ovál, ihrisko a detské ihrisko, 547 m od P6",
      credit=DEMO_IMG)}</div>

    <div class="grid-2" style="align-items:start;margin-top:clamp(28px,4vw,48px)">
      <div class="reveal">
        <p class="eyebrow">Rodina a škola</p>
        <h2>Najkratšia cesta do školy je tá, ktorú prejdete pešo</h2>
      </div>
      <div class="reveal">
        <p class="lede">{txt(
          "Spojená škola Novohradská je od P6 vzdialená 547 metrov, sedem minút pešo. Každodenná cesta do školy preto nemusí znamenať ranné státie v aute ani ďalšiu cestu cez mesto.",
          "Spojená škola Novohradská je 547 metrov od P6, sedem minút pešo. Cesta do školy nemusí znamenať ranné státie v aute.")}</p>
        <ul class="points">
          <li class="point">základná škola</li>
          <li class="point">gymnázium</li>
          <li class="point">športový areál s bežeckým oválom a ihriskami</li>
          <li class="point"><b>547 m</b> · 7 minút pešo · 4 minúty bicyklom</li>
        </ul>
        <p class="form__note" style="margin-top:14px">
          Vzdialenosť meraná po reálnej pešej trase z Prievozskej 6. Konkrétnu ponuku odborov
          a medzinárodných programov uvádzame podľa informácií školy.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- §8 Nivy a mobilita ================================================ -->
<section class="section section--paper2">
  <div class="shell shell-wide">
    <div class="grid-2" style="align-items:start;margin-bottom:clamp(30px,4vw,48px)">
      <div class="reveal">
        <p class="eyebrow">Nivy a mobilita</p>
        <h2>Mesto, ktoré odchádza<br>aj prichádza</h2>
      </div>
      <p class="lede reveal">{txt(
        "Autobusová stanica Nivy prepája P6 s mestom, regiónmi aj zahraničím. Blízkosť MHD, cyklistických spojení a diaľničného systému dáva obyvateľom slobodu vybrať si dopravu podľa konkrétneho dňa.",
        "Autobusová stanica Nivy prepája P6 s mestom, regiónmi aj zahraničím. MHD, cyklotrasy a diaľnica dávajú slobodu vybrať si dopravu podľa dňa.")}</p>
    </div>
    <div class="mob">
      <article class="mob__card reveal">{svg("bus")}<h3>Zastávka pred domom</h3><p>Zastávka Miletičova je 2 minúty pešo od vchodu. Stoja na nej linky 42, 70, 71, 72 a nočná N72. Zastávka Novohradská je 4 minúty pešo.</p></article>
      <article class="mob__card reveal">{svg("bus")}<h3>Autobusová stanica Nivy</h3><p>Regionálne aj medzinárodné linky, približne 15 minút pešo. Prímestské spoje na Senec, Šamorín, Modru či Malinovo stoja aj na Prievozskej, 7 minút pešo.</p></article>
      <article class="mob__card reveal">{svg("bike")}<h3>Cyklistické spojenia</h3><p>Cyklotrasy smerom na nábrežie a do centra. Na bicykli ste v Downtowne za pár minút.</p></article>
      <article class="mob__card reveal">{svg("road")}<h3>Diaľnica a letiská</h3><p>Nájazd na D1 v blízkosti. Letisko Bratislava 10 až 15 min, Schwechat 45 až 55 min autom.</p></article>
    </div>
  </div>
</section>

<!-- §9 Šport a voľný čas ============================================== -->
<section class="section section--ink sport">
  <div class="shell shell-wide">
    <div style="max-width:60ch">
      <p class="eyebrow">Šport a voľný čas</p>
      <h2>Každé mesto má energiu.<br>Bratislava hrá hokej.</h2>
    </div>
  </div>
  <div class="ticker" aria-hidden="true">
    <div class="ticker__track">
      <span class="ticker__item">Zimný štadión Ondreja Nepelu</span><span class="ticker__item">Národný futbalový štadión</span><span class="ticker__item">Fitness centrá</span><span class="ticker__item">Štrkovecké jazero</span><span class="ticker__item">Dunajská promenáda</span><span class="ticker__item">Cyklistické spojenia</span>
      <span class="ticker__item">Zimný štadión Ondreja Nepelu</span><span class="ticker__item">Národný futbalový štadión</span><span class="ticker__item">Fitness centrá</span><span class="ticker__item">Štrkovecké jazero</span><span class="ticker__item">Dunajská promenáda</span><span class="ticker__item">Cyklistické spojenia</span>
    </div>
  </div>
  <div class="shell shell-wide">
    <div class="sport__grid">
      <div class="sport__item"><b>Zimný štadión Ondreja Nepelu</b><span>hokej a koncerty · 1,9 km · <em>11 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Národný futbalový štadión</b><span>futbal · 2,5 km · <em>14 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Štrkovecké jazero</b><span>beh, korčule, oddych · 2,2 km · <em>12 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Dunajská promenáda</b><span>beh a prechádzky · 3,1 km · <em>16 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Sky Park</b><span>park a bežecké okruhy · 1,5 km · <em>9 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Cyklistické spojenia</b><span>na nábrežie, do centra aj na Nivy</span></div>
    </div>
    <p class="form__note" style="margin-top:14px;color:var(--text-inv-muted)">Merané po reálnych cyklotrasách z P6.</p>
  </div>
</section>

''' + cta_slim("Máte predstavu o okolí? Pozrite si, čo je v ňom voľné.", cls="") + f'''
<!-- §10 Architektúra P6 =============================================== -->
<section class="section section--paper2" id="projekt">
  <div class="shell shell-wide">
    <div class="grid-2" style="align-items:start">
      <div class="reveal">
        <p class="eyebrow">Architektúra P6</p>
        <h2>Pokojný dom<br>v dynamickej<br>časti mesta</h2>
      </div>
      <div class="reveal">
        <p class="lede">{txt(
          "Architektúra P6 má vytvoriť pokojný rámec pre každodenný život. Dôležité sú prirodzené svetlo, zrozumiteľné dispozície, súkromie bytov a exteriérové priestory orientované tam, kde ich obyvatelia skutočne využijú.",
          "Architektúra P6 má vytvoriť pokojný rámec pre každodenný život: prirodzené svetlo, zrozumiteľné dispozície, súkromie a exteriéry tam, kde ich naozaj využijete.")}</p>
        <p class="form__note">Materiály fasády, členenie podlaží a orientáciu bytov doplníme po potvrdení architektonického riešenia.</p>
      </div>
    </div>
    <div style="margin-top:clamp(30px,4vw,52px)">{photo("Strešná terasa P6", "Vizualizácia · strešná komunitná terasa po západe slnka", "photo--32 reveal", "cube",
           src="assets/img/p6-terasa-1024.webp", credit="Vizualizácia",
           alt="Vizualizácia strešnej komunitnej terasy P6 po západe slnka: pergoly, vyvýšené záhony, sedenie a tlmené osvetlenie")}</div>
  </div>
</section>

<!-- §11 Komunitná terasa ============================================== -->
<section class="section section--ink">
  <div class="shell shell-wide">
    <div class="grid-2" style="align-items:center">
      <div class="reveal">
        <p class="eyebrow">Komunitná terasa</p>
        <h2>Domov by sa nemal končiť<br>pri vašich dverách</h2>
        <p class="lede" style="margin-top:18px">{txt(
          "Komunitná terasa rozširuje bývanie o spoločný priestor na rozhovor, oddych, prácu, stretnutie susedov alebo pokojný večer nad mestom.",
          "Komunitná terasa rozširuje bývanie o spoločný priestor na rozhovor, oddych, prácu či pokojný večer nad mestom.")}</p>
        <ul class="points">
          <li class="point">pergola</li><li class="point">zeleň</li><li class="point">sedenie</li>
          <li class="point">grilovanie</li><li class="point">priestor pre deti</li><li class="point">večerná atmosféra</li>
        </ul>
        <p class="form__note" style="margin-top:14px;color:var(--text-inv-muted)">Konkrétne vybavenie terasy upresníme podľa finálneho projektu.</p>
      </div>
      <div class="reveal">{photo("Komunitná terasa", "Fotografia · večerná atmosféra", "photo--ink photo--tall", "sun",
           src="assets/img/terasa.webp", credit=DEMO_IMG,
           alt="Strešná komunitná terasa večer: pergola, zeleň, spoločný stôl a svetelné girlandy")}</div>
    </div>
  </div>
</section>

<!-- §12 Parametre projektu ============================================ -->
<section class="section section--paper2">
  <div class="shell shell-wide">
    <div style="max-width:56ch;margin-bottom:clamp(24px,3vw,36px)">
      <p class="eyebrow">Parametre projektu</p>
      <h2>Dom v číslach</h2>
    </div>
    <dl class="params">{params}</dl>
    <p class="form__note" style="margin-top:14px">Počty, podlažnosť a výmery vychádzajú z pôdorysov architekta. {DISCLAIMER}</p>
  </div>
</section>

<!-- §13 Štandard ======================================================= -->
<section class="section" id="standard">
  <div class="shell shell-wide">
    <div style="max-width:56ch;margin-bottom:clamp(24px,3vw,36px)">
      <p class="eyebrow">Štandard</p>
      <h2>Čo je v cene bytu</h2>
    </div>
    <div class="std">{std}</div>
    <p class="form__note" style="margin-top:16px">Štandard vyhotovenia upresníme podľa finálnej projektovej dokumentácie.</p>
  </div>
</section>

''' + cta_slim("Poznáte projekt. Ďalší krok je vybrať si byt.", cls="section--paper2") + f'''
<!-- §14 Byty ============================================================ -->
<section class="section" id="byty">
  <div class="shell shell-wide">
    <div style="display:flex;flex-wrap:wrap;gap:20px;align-items:flex-end;justify-content:space-between;margin-bottom:clamp(24px,3vw,36px)">
      <div>
        <p class="eyebrow">Byty</p>
        <h2>Dostupné byty</h2>
      </div>
      <a class="link-arrow" href="byty.html">Všetky byty a filtre {svg("arrow")}</a>
    </div>
    <div class="ucards ucards--rail" data-featured></div>
    <p class="rail-hint">{svg("swipe")} Potiahnite pre ďalšie byty</p>
    <p class="form__note" style="margin-top:16px">{DISCLAIMER}</p>
  </div>
</section>

{harmonogram}''' + final_block() + '''
</main>
''' + FOOT
    + '''<script>
/* §14: six available units with plan thumbnails, largest first */
document.addEventListener('DOMContentLoaded', function () {
  var wrap = document.querySelector('[data-featured]');
  if (!wrap) return;
  var picks = APARTMENTS.filter(function (a) { return a.status === 'dostupny'; })
    .sort(function (a, b) { return b.area - a.area; }).slice(0, 6);
  wrap.innerHTML = picks.map(function (a) { return unitCardHTML(a); }).join('');
});
</script>
''' + scripts("map.js", "floorplan.js", "floors.js", "list.js", "fly.js"))

# ---------------------------------------------------------------- byty

def byty_html():
    floors = "".join(f'<option value="{i}">{i}. NP</option>' for i in range(1, 6))
    return (head(f"Byty | {NAME}",
                 "Prehľad bytov na Prievozskej 6 s pôdorysom, výmerou, orientáciou a dostupnosťou. Filtrujte podľa izieb, podlažia, výmery, exteriéru, orientácie a dostupnosti.",
                 "byty.html")
    + nav("byty.html")
    + f'''<main id="main" data-list>
{page_head("Byty", "Byty", "Každá karta ukazuje pôdorys, počet izieb, interiér, exteriér, orientáciu, podlažie a dostupnosť. Filtrujte podľa toho, čo je pre vás dôležité.", "Ponuka bytov")}

<div class="filters">
  <div class="shell">
    <form class="filters__inner" role="search" aria-label="Filtrovanie bytov" onsubmit="return false">
      <div class="filters__bar">
        <button type="button" class="filters__toggle" data-filter-toggle aria-expanded="false" aria-controls="filter-fields">
          {svg("sliders")}<span>Filtre</span><span class="filters__badge" data-filter-badge hidden></span>
        </button>
        <span class="filters__count" data-count aria-live="polite">…</span>
        <button type="button" class="filters__reset" data-reset>Zrušiť filtre</button>
      </div>

      <div class="filters__scrim" data-filter-scrim hidden></div>
      <div class="filters__fields" id="filter-fields">
      <div class="filters__sheet-head"><span>Filtre</span>
        <button type="button" class="filters__sheet-close" data-filter-close aria-label="Zavrieť filtre">{svg("x")}</button></div>
      <div class="field"><label for="f-rooms">Počet izieb</label>
        <select id="f-rooms"><option value="">Všetky</option><option value="1">1-izbový</option><option value="2">2-izbový</option><option value="3">3-izbový</option></select></div>
      <div class="field"><label for="f-floor">Podlažie</label>
        <select id="f-floor"><option value="">Všetky</option>{floors}</select></div>
      <div class="field"><label for="f-area">Výmera</label>
        <select id="f-area"><option value="">Bez limitu</option><option value="35">od 35 m²</option><option value="45">od 45 m²</option><option value="55">od 55 m²</option><option value="65">od 65 m²</option><option value="75">od 75 m²</option></select></div>
      <div class="field"><label for="f-status">Dostupnosť</label>
        <select id="f-status"><option value="">Všetky</option><option value="dostupny">Voľné</option><option value="rezervovany">Rezervované</option><option value="predany">Predané</option></select></div>
      <button type="button" class="btn btn--primary filters__apply" data-filter-close>Zobraziť <span data-count>…</span></button>
      </div>
    </form>
  </div>
</div>

<section class="section section--tight">
  <div class="shell shell-wide">
    <div class="ucards" data-cards></div>
    <div class="empty" data-empty hidden>
      <h3>Žiadny byt nezodpovedá filtrom</h3>
      <p class="lede" style="margin-inline:auto">Skúste uvoľniť niektorý z filtrov. Alebo nám napíšte a nájdeme vám najbližšiu alternatívu.</p>
      <p><a class="btn btn--ghost" href="kontakt.html">Napísať nám</a></p>
    </div>
    <p class="form__note" style="margin-top:20px">{DISCLAIMER}</p>
  </div>
</section>

''' + final_block() + '''
</main>
''' + FOOT + scripts("list.js"))

# ---------------------------------------------------------------- byt

def byt_html():
    return (head(f"Detail bytu | {NAME}",
                 "Detail bytu: dispozícia, výmery jednotlivých miestností, orientácia, cena a dostupnosť.",
                 "byt.html")
    + nav("byty.html")
    + f'''<main id="main" data-detail>
<section class="page-head">
  <div class="shell">
    <nav class="crumbs" aria-label="Omrvinková navigácia" style="margin-bottom:22px">
      <a href="index.html">Domov</a><span aria-hidden="true">/</span>
      <a href="byty.html">Byty</a><span aria-hidden="true">/</span>
      <span data-crumb>Detail</span>
    </nav>
    <div data-head></div>
  </div>
</section>

<section class="section section--tight" style="padding-top:0">
  <div class="shell">
    <div class="detail">
      <div class="stack">
        <dl class="spec" data-spec></dl>

        <div class="planwrap">
          <div>
            <div class="plan__head">
              <p class="eyebrow" style="margin:0">Pôdorys</p>
              <a class="link-arrow" data-plan-download href="#" download>Stiahnuť pôdorys {svg("arrow")}</a>
            </div>
            <div class="plan" data-plan></div>
            <p class="form__note" style="margin-top:14px">{DISCLAIMER}</p>
          </div>
          <div class="stack" style="gap:26px">
            <div>
              <p class="eyebrow">Výmery miestností</p>
              <table class="rooms" data-rooms>
                <thead><tr><th scope="col">Miestnosť</th><th scope="col">Plocha</th></tr></thead>
                <tbody data-rooms-in></tbody>
                <tbody class="rooms__sum"><tr><td>Interiér spolu</td><td data-sum-in>…</td></tr></tbody>
                <tbody data-rooms-ext></tbody>
                <tfoot><tr><td>Spolu</td><td data-sum-all>…</td></tr></tfoot>
              </table>
            </div>
          </div>
        </div>

        <div>
          <p class="eyebrow">Poloha v dome</p>
          <div data-floorplan></div>
          <div class="legend legend--tight">
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--ok"></span>Voľný</span>
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--warn"></span>Rezervovaný</span>
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--off"></span>Predaný</span>
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--this"></span>Tento byt</span>
          </div>
          <p class="form__note" style="margin-top:8px">Kliknutím na iný byt na podlaží sa presuniete na jeho detail. Šípkami ← → prechádzate dom po poradí.</p>
        </div>

        <div data-tourslot></div>

        <div class="grid-2" style="gap:16px">
          {photo("Fotografie bytu", "Doplníme po fotodokumentácii", "", "camera",
                 src="assets/img/byt-spalna.webp", credit=DEMO_IMG,
                 alt="Ilustračná spálňa: manželská posteľ, dubová podlaha, okno so záclonou")}
          {photo("Vzorový interiér", "Doplníme po dokončení vzorového bytu", "", "sun",
                 src="assets/img/interier.webp", credit=DEMO_IMG,
                 alt="Ilustračná obývačka s jedálňou a balkónom")}
        </div>

        <div class="detail-nav" data-detailnav></div>
      </div>

      <aside class="aside" data-aside aria-label="Cena a kontakt"></aside>
    </div>
  </div>
</section>

<section class="section section--paper2" data-similar>
  <div class="shell shell-wide">
    <p class="eyebrow">Podobné byty</p>
    <h2 style="margin-bottom:clamp(26px,4vw,40px)">Rovnaká typológia</h2>
    <div class="ucards ucards--rail" data-similar-cards></div>
  </div>
</section>

''' + final_block() + '''
</main>

<div class="sticky-cta" data-sticky-cta hidden></div>
''' + FOOT + scripts("list.js", "floorplan.js", "tour.js", "detail.js"))

# ---------------------------------------------------------------- redirects

def karta_html():
    """Print template for the per-apartment PDF (assets/pdf/P6-byt-1A.pdf …).

    Not a page of the site: _build/pdf/build_pdfs.mjs opens it once per
    apartment in headless Chrome and prints it to A4. It renders from the same
    APARTMENTS data as byt.html, so the PDF cannot disagree with the page, and it
    carries the architect's disclaimer on both sheets because both show areas.
    """
    return f'''<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<base href="../../">
<title>P6 — karta bytu</title>
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v={ASSET_V}">
<style>
  @page {{ size: A4; margin: 0; }}
  html, body {{ margin: 0; padding: 0; background: #fff; }}
  body.karta {{ font-family: var(--f-ui); color: var(--ink); font-size: 9pt; line-height: 1.45;
    -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .sheet {{ width: 210mm; height: 297mm; box-sizing: border-box; padding: 13mm 16mm 11mm;
    display: flex; flex-direction: column; overflow: hidden; break-after: page; }}
  .sheet:last-child {{ break-after: auto; }}

  .k-head {{ display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 4.5mm; border-bottom: .25mm solid var(--line); }}
  .k-brand {{ display: flex; align-items: center; gap: 4mm; }}
  .k-logo {{ height: 7mm; width: auto; display: block; color: var(--ink); }}
  .k-brand span, .k-doc {{ font-size: 6.4pt; letter-spacing: .26em; text-transform: uppercase; color: var(--text-muted); }}
  .k-doc {{ color: var(--sand-ink); font-weight: 500; }}

  .k-eyebrow {{ margin: 0 0 3mm; font-size: 6.6pt; letter-spacing: .22em; text-transform: uppercase;
    color: var(--sand-ink); font-weight: 500; }}
  .k-title {{ margin-top: 9mm; }}
  .k-title h1 {{ margin: 0; font-family: var(--f-display); font-weight: 300; font-size: 50pt;
    line-height: .95; letter-spacing: -.012em; }}
  .k-lede {{ margin: 3mm 0 0; font-size: 11pt; color: var(--text-muted); }}

  .k-spec {{ display: grid; grid-template-columns: repeat(5, 1fr); margin: 8mm 0 0;
    border: .25mm solid var(--line); }}
  .k-spec div {{ padding: 3mm 4mm 3.4mm; }}
  .k-spec div + div {{ border-left: .25mm solid var(--line); }}
  .k-spec dt {{ font-size: 5.8pt; letter-spacing: .2em; text-transform: uppercase; color: var(--text-muted); }}
  .k-spec dd {{ margin: 1.4mm 0 0; font-family: var(--f-display); font-size: 17pt; line-height: 1; white-space: nowrap; }}
  .k-spec small {{ font-family: var(--f-ui); font-size: 6.5pt; color: var(--text-muted); }}

  .k-plan {{ flex: 1; min-height: 0; margin: 8mm 0 0; padding: 7mm; box-sizing: border-box;
    background: var(--paper-2); border-radius: 1.4mm; display: flex; flex-direction: column; }}
  .k-plan__label {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4mm; }}
  .k-plan__label .k-eyebrow {{ margin: 0; }}
  .k-plan__box {{ flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }}
  .k-plan__box img {{ max-width: 100%; max-height: 100%; object-fit: contain; display: block; background: #fff; }}

  .k-note {{ margin: 4mm 0 0; font-size: 6.8pt; line-height: 1.5; color: var(--text-muted); }}
  .k-foot {{ margin-top: auto; padding-top: 3mm; border-top: .25mm solid var(--line);
    display: flex; justify-content: space-between; gap: 6mm; font-size: 6.4pt; color: var(--text-muted); }}
  .k-gap {{ height: 5mm; flex: none; }}

  .k-cols {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 12mm; margin-top: 9mm; }}
  .k-rooms {{ width: 100%; border-collapse: collapse; font-size: 8.6pt; }}
  .k-rooms th {{ text-align: left; font-size: 5.8pt; letter-spacing: .2em; text-transform: uppercase;
    color: var(--text-muted); font-weight: 500; padding: 0 0 2.2mm; border-bottom: .25mm solid var(--ink); }}
  .k-rooms th:last-child, .k-rooms td:last-child {{ text-align: right; white-space: nowrap; }}
  .k-rooms td {{ padding: 2.1mm 0; border-bottom: .25mm solid var(--line); font-variant-numeric: tabular-nums; }}
  .k-rooms .is-sum td {{ font-weight: 600; }}
  .k-rooms .is-total td {{ font-weight: 600; border-bottom: 0; border-top: .25mm solid var(--ink); }}

  .k-price {{ margin: 0; font-family: var(--f-display); font-size: 22pt; line-height: 1.05; }}
  .k-extras {{ display: grid; gap: 2.5mm; }}
  .k-extra {{ border: .25mm solid var(--line); border-radius: 1.2mm; padding: 3mm 3.6mm; }}
  .k-extra b {{ display: block; font-weight: 600; font-size: 8.6pt; }}
  .k-extra span {{ display: block; margin-top: .6mm; color: var(--text-muted); font-size: 8pt; }}
  .k-small {{ margin: 3mm 0 0; font-size: 7.4pt; line-height: 1.5; color: var(--text-muted); }}

  .k-where {{ margin-top: 9mm; }}
  .k-where .fplan {{ margin: 0; }}
  .k-where .fplan__cap {{ font-size: 6.6pt; margin-top: 2mm; }}
  /* the flat itself in brand copper, as on the site's hover — on paper there is
     no hover, so the one flat that matters has to carry the colour */
  .k-where .fplan__unit.is-active polygon {{ fill: rgba(184, 115, 51, .38); stroke: var(--copper); stroke-width: 1.6; }}
  .k-where .fplan__unit.is-active .fplan__tag circle {{ fill: var(--copper); stroke: var(--copper); }}

  .k-contact {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 12mm; margin-top: 8mm;
    padding-top: 5mm; border-top: .25mm solid var(--line); }}
  .k-contact p {{ margin: 0; }}
  .k-contact__big {{ font-family: var(--f-display); font-size: 15pt; line-height: 1.2; }}
</style>
</head>
<body class="karta">
<main data-karta></main>
<script src="assets/js/data.js?v={ASSET_V}"></script>
<script src="assets/js/site.js?v={ASSET_V}"></script>
<script src="assets/js/floorplan.js?v={ASSET_V}"></script>
<script>
(async () => {{
  const DISCLAIMER = {json.dumps(DISCLAIMER, ensure_ascii=False)};
  const PHONE = {json.dumps(PHONE)}, EMAIL = {json.dumps(EMAIL)};
  const WEB = {json.dumps(SITE.replace("https://", ""))};
  const ADDRESS = {json.dumps(ADDRESS, ensure_ascii=False)};

  const id = new URLSearchParams(location.search).get('id');
  const a = APARTMENTS.find(u => u.id === id);
  const root = document.querySelector('[data-karta]');
  if (!a) {{ root.textContent = 'Byt ' + id + ' sa nenašiel'; window.__kartaReady = 'missing'; return; }}
  document.title = `P6 — Byt ${{a.id}}, karta bytu`;

  const today = new Date().toLocaleDateString('sk-SK');
  const head = `<header class="k-head">
      <div class="k-brand">{logo("k-logo", "P6")}<span>Prievozská 6 · Bratislava-Ružinov</span></div>
      <div class="k-doc">Karta bytu ${{a.id}}</div>
    </header>`;
  const foot = n => `<footer class="k-foot">
      <span>P6 · ${{ADDRESS}}</span><span>Údaje k ${{today}}</span><span>${{n}} / 2</span>
    </footer>`;
  const sold = a.status === 'predany';

  root.innerHTML = `
  <section class="sheet">
    ${{head}}
    <div class="k-title">
      <p class="k-eyebrow">P6 · Prievozská 6 · ${{a.floor}}. nadzemné podlažie</p>
      <h1>Byt ${{a.id}}</h1>
      <p class="k-lede">${{a.type}} · ${{a.floor}}. nadzemné podlažie · byt ${{a.letter}}</p>
    </div>
    <dl class="k-spec">
      <div><dt>Interiér</dt><dd>${{fmtArea(a.area)}} <small>m²</small></dd></div>
      <div><dt>${{a.extKind}}</dt><dd>${{fmtArea(a.ext)}} <small>m²</small></dd></div>
      <div><dt>Spolu</dt><dd>${{fmtArea(a.total)}} <small>m²</small></dd></div>
      <div><dt>Izby</dt><dd>${{a.rooms}}</dd></div>
      <div><dt>Podlažie</dt><dd>${{a.floor}}. NP</dd></div>
    </dl>
    <figure class="k-plan">
      <div class="k-plan__label"><p class="k-eyebrow">Pôdorys</p><p class="k-eyebrow">Byt ${{a.id}}</p></div>
      <div class="k-plan__box"><img src="${{a.plan}}" alt="Pôdorys bytu ${{a.id}}"></div>
    </figure>
    <p class="k-note">${{DISCLAIMER}}</p>
    <div class="k-gap"></div>
    ${{foot(1)}}
  </section>

  <section class="sheet">
    ${{head}}
    <div class="k-cols">
      <div>
        <p class="k-eyebrow">Výmery miestností</p>
        <table class="k-rooms">
          <thead><tr><th>Miestnosť</th><th>Plocha</th></tr></thead>
          <tbody>
            ${{a.roomList.map(r => `<tr><td>${{r.name}}</td><td>${{fmtArea1(r.area)}} m²</td></tr>`).join('')}}
            <tr class="is-sum"><td>Interiér spolu</td><td>${{fmtArea(a.area)}} m²</td></tr>
            ${{a.ext > 0 ? `<tr><td>${{a.extKind}}</td><td>${{fmtArea1(a.ext)}} m²</td></tr>` : ''}}
            <tr class="is-total"><td>Spolu</td><td>${{fmtArea(a.total)}} m²</td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <p class="k-eyebrow">${{sold ? 'Stav bytu' : 'Cena vrátane DPH'}}</p>
        <p class="k-price">${{sold ? 'Predané' : fmtPrice(a.price, a.status)}}</p>
        <p class="k-eyebrow" style="margin-top:8mm">Možnosť dokúpiť</p>
        <div class="k-extras">
          <div class="k-extra"><b>Pivničná kobka</b><span>plocha 1,5 až 3,0 m²</span></div>
          <div class="k-extra"><b>Parkovacie miesto</b><span>vonkajšie státie priamo pred domom, 50 miest</span></div>
        </div>
        <p class="k-small">Pivničná kobka aj parkovacie miesto sa k bytu dokupujú samostatne. Cenu a dostupnosť vám oznámime na vyžiadanie.</p>
      </div>
    </div>

    <div class="k-where">
      <p class="k-eyebrow">Poloha v dome</p>
      <div data-floorplan></div>
    </div>

    <div class="k-contact">
      <div>
        <p class="k-eyebrow">Predaj bytov</p>
        <p class="k-contact__big">${{PHONE}}</p>
        <p>${{EMAIL}} · ${{WEB}}</p>
      </div>
      <div>
        <p class="k-eyebrow">Adresa projektu</p>
        <p>${{ADDRESS}}</p>
      </div>
    </div>
    <p class="k-note">${{DISCLAIMER}}</p>
    <div class="k-gap"></div>
    ${{foot(2)}}
  </section>`;

  const where = root.querySelector('[data-floorplan]');
  mountFloorPlan(where, a.id);
  /* a PDF has nowhere to go: the neighbours stay drawn, but not as links */
  where.querySelectorAll('a[href]').forEach(n => n.removeAttribute('href'));
  where.querySelectorAll('img').forEach(i => {{ i.loading = 'eager'; }});

  await document.fonts.ready;
  await Promise.all([...document.images].map(i => i.decode().catch(() => {{}})));
  /* Chrome writes a WebP into a PDF as raw pixels, about 3 MB a page; a JPEG it
     embeds as is. So re-encode each picture to JPEG before printing. */
  await Promise.all([...document.images].map(async i => {{
    const c = document.createElement('canvas');
    c.width = i.naturalWidth; c.height = i.naturalHeight;
    const g = c.getContext('2d');
    g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height);
    g.drawImage(i, 0, 0);
    i.src = c.toDataURL('image/jpeg', 0.86);
    await i.decode().catch(() => {{}});
  }}));
  window.__kartaReady = true;
}})();
</script>
</body>
</html>
'''


def redirect_html(target, title):
    return f'''<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=index.html{target}">
<link rel="canonical" href="{SITE}/{target}">
<title>{title} | {NAME}</title>
<script>location.replace('index.html{target}');</script>
</head>
<body style="font-family:Inter,sans-serif;padding:40px">
<p>Sekcia je súčasťou hlavnej stránky. <a href="index.html{target}">Pokračovať na {title}</a>.</p>
</body>
</html>
'''

# ---------------------------------------------------------------- galéria

def galeria_html():
    tiles = [
        ("Miletička ráno", "photo--wide", "mileticka"),
        ("Cyklista na Prievozskej", "", "cyklista"),
        ("Vizualizácia P6", "", "vizualizacia-p6"),
        ("Nivy večer", "photo--wide", "nivy"),
        ("Cesta do školy", "", "cesta-do-skoly"),
        ("Apollo a biznis zóna", "", "biznis-zona"),
        ("Komunitná terasa", "photo--wide", "terasa"),
        ("Dunajská promenáda", "", "dunaj"),
        ("Vzorový interiér", "", "interier"),
    ]
    g = "".join(
        f'<div class="{"gallery__wide" if c else ""}">'
        f'{photo(t, "Fotografia bude doplnená", c or "", src=f"assets/img/{img}.webp", alt=t, credit="Vizualizácia" if img == "vizualizacia-p6" else DEMO_IMG)}'
        f'</div>' for t, c, img in tiles)
    return (head(f"Galéria | {NAME}",
                 "Fotografie a vizualizácie: Miletička, biznis zóna, Nivy, cesta do školy, komunitná terasa a vizualizácia P6.",
                 "galeria.html")
    + nav("galeria.html")
    + f'''<main id="main">
{page_head("Galéria", "Miesto, kde budete<br>bývať", "Fotografie okolia a vizualizácie domu. Miletička, cyklista, Nivy večer, cesta do školy a komunitná terasa dopĺňame priebežne.", "Galéria")}

<section class="section section--tight">
  <div class="shell shell-wide">
    <div class="gallery">{g}</div>
  </div>
</section>

<section class="section section--paper2">
  <div class="shell center" style="max-width:56ch">
    <p class="eyebrow eyebrow--center">Pripravujeme</p>
    <h2>Virtuálne prehliadky bytov</h2>
    <p class="lede" style="margin-top:18px">Po dokončení fotodokumentácie sprístupníme 3D prehliadku každej dispozície priamo v detaile bytu.</p>
    <p style="margin-top:24px"><a class="btn btn--primary" href="kontakt.html">Dať mi vedieť {svg("arrow")}</a></p>
  </div>
</section>

''' + final_block() + '''
</main>
''' + FOOT + scripts())

# ---------------------------------------------------------------- kontakt

def kontakt_html():
    faq = "".join(f'<details><summary>{q}</summary><div class="faq__body"><p>{a}</p></div></details>' for q, a in FAQ)
    return (head(f"Kontakt | {NAME}",
                 "Dohodnite si konzultáciu alebo si vyžiadajte katalóg. Napíšte nám, aký byt na Prievozskej 6 hľadáte.",
                 "kontakt.html")
    + nav("kontakt.html")
    + f'''<main id="main">
{page_head("Kontakt", "Povedzte nám,<br>čo hľadáte", "Napíšte nám počet izieb, orientáciu alebo rozpočet a my sa ozveme s konkrétnymi bytmi, ktoré tomu zodpovedajú.", "Kontakt")}

<section class="section section--tight" style="padding-top:0">
  <div class="shell">
    <div class="detail">
      <form class="form" data-form novalidate>
        <div class="form__ok" data-form-ok role="status">
          {svg("check")}
          <span><strong>Ďakujeme, správu máme.</strong><br>Ozveme sa vám do jedného pracovného dňa.</span>
        </div>
        <div class="form__row">
          <div><label for="c-name">Meno a priezvisko *</label><input id="c-name" name="name" type="text" autocomplete="name" required></div>
          <div><label for="c-phone">Telefón</label><input id="c-phone" name="phone" type="tel" autocomplete="tel" placeholder="+421"></div>
        </div>
        <div class="form__row">
          <div><label for="c-email">E-mail *</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
          <div><label for="c-unit">Byt, ktorý vás zaujal</label><input id="c-unit" name="unit" type="text" placeholder="napr. 4.03, alebo nechajte prázdne"></div>
        </div>
        <div class="form__row">
          <div><label for="c-rooms">Preferovaná dispozícia</label>
            <select id="c-rooms" name="rooms"><option value="">Nezáleží</option><option>1-izbový</option><option>2-izbový</option><option>3-izbový</option><option>4-izbový</option><option>5 a viac izieb</option></select></div>
          <div><label for="c-topic">Čo potrebujete</label>
            <select id="c-topic" name="topic"><option value="konzultacia">Konzultáciu</option><option value="katalog">Katalóg</option><option value="obhliadka">Osobnú obhliadku</option><option value="ine">Iné</option></select></div>
        </div>
        <div><label for="c-msg">Správa</label><textarea id="c-msg" name="message" placeholder="Čo je pre vás dôležité? Výhľad, terasa, podlažie, termín…"></textarea></div>
        <div class="consent">
          <input id="c-gdpr" name="gdpr" type="checkbox" required>
          <label for="c-gdpr">Súhlasím so spracovaním osobných údajov na účely vybavenia mojej požiadavky. *</label>
        </div>
        <div>
          <button class="btn btn--primary" type="submit">Odoslať správu {svg("arrow")}</button>
          <p class="form__note" style="margin:14px 0 0">Odpovedáme do jedného pracovného dňa. Váš kontakt neposkytujeme tretím stranám.</p>
        </div>
      </form>

      <aside class="aside" aria-label="Kontaktné údaje">
        <div class="aside__box">
          <dl class="contact-list">
            <div><dt>Predaj bytov</dt><dd><a href="tel:{PHONE.replace(' ', '')}">{PHONE}</a></dd></div>
            <div><dt>E-mail</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
            <div><dt>Adresa projektu</dt><dd>Prievozská 6<br>821 09 Bratislava-Ružinov</dd></div>
            <div><dt>Otváracie hodiny</dt><dd>Pondelok až piatok<br>9:00 až 18:00</dd></div>
          </dl>
        </div>
        <div class="aside__box">
          <p class="eyebrow" style="margin-bottom:10px">Osobná obhliadka</p>
          <p style="font-size:.94rem;color:var(--text-muted);margin:0">Radi vám ukážeme projekt osobne, vrátane vzorových materiálov a presných dispozícií. Stretnutie si dohodneme telefonicky.</p>
        </div>
      </aside>
    </div>
  </div>
</section>

<section class="section section--paper2">
  <div class="shell">
    <div style="max-width:52ch;margin-bottom:clamp(24px,3vw,36px)">
      <p class="eyebrow">Časté otázky</p>
      <h2>Čo sa najčastejšie pýtate</h2>
    </div>
    <div class="faq">{faq}</div>
  </div>
</section>
</main>
''' + FOOT + '''<script>
/* prefill from the detail page (?byt=4.03) or the catalogue CTA (?katalog=1) */
document.addEventListener('DOMContentLoaded', function () {
  var q = new URLSearchParams(location.search);
  var byt = q.get('byt'), unit = document.getElementById('c-unit'), msg = document.getElementById('c-msg'), topic = document.getElementById('c-topic');
  if (byt && unit) {
    unit.value = byt;
    if (msg && !msg.value) msg.value = 'Mám záujem o byt ' + byt + '. Prosím o viac informácií.';
  }
  if (q.get('katalog')) {
    if (topic) topic.value = 'katalog';
    if (msg && !msg.value) msg.value = 'Prosím o zaslanie katalógu P6.';
  }
});
</script>
''' + scripts())

# ---------------------------------------------------------------- static

# the logo in paper on an ink tile; 44 wide leaves the mark legible at 16px
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<rect width="64" height="64" rx="10" fill="#14120F"/>'
           f'<svg x="10" y="16.7" width="44" height="30.6" viewBox="{LOGO_VIEWBOX}" fill="#F7F4EF">'
           + "".join(f'<path d="{d}"/>' for d in LOGO_PATHS) + '</svg></svg>\n')

ROBOTS = ("User-agent: *\nDisallow: /\n" if PREVIEW else
          f"User-agent: *\nAllow: /\nDisallow: /byt.html\n\nSitemap: {SITE}/sitemap.xml\n")

SITEMAP = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f'  <url><loc>{SITE}/{p}</loc><priority>{pr}</priority></url>\n'
              for p, pr in [("", "1.0"), ("byty.html", "0.9"), ("galeria.html", "0.6"), ("kontakt.html", "0.7")])
    + '</urlset>\n')

files = {
 "index.html": index_html(),
 "byty.html": byty_html(),
 "byt.html": byt_html(),
 "lokalita.html": redirect_html("#lokalita", "Lokalita"),
 "projekt.html": redirect_html("#projekt", "Projekt"),
 "galeria.html": galeria_html(),
 "kontakt.html": kontakt_html(),
 "_build/pdf/karta.html": karta_html(),
 "favicon.svg": FAVICON,
 "robots.txt": ROBOTS,
 "sitemap.xml": SITEMAP,
}

for name, content in files.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{name}: {len(content):>7} bytes")
