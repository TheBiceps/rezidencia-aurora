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
import os
OUT = "rezidencia"

SITE = "https://prievozska6.sk"          # placeholder domain — confirm with client
NAME = "P6"
ADDRESS = "Prievozská 6, 821 09 Bratislava-Ružinov"
EMAIL = "info@prievozska6.sk"            # placeholder
PHONE = "+421 900 000 000"               # placeholder

# Client-preview build: noindex everywhere, robots blocks crawlers.
PREVIEW = True

# Bump whenever CSS/JS changes — appended as ?v= to every asset link.
ASSET_V = "21"

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
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
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
    <a class="brand" href="index.html" aria-label="{NAME} — domov">
      <span class="brand__mark">P6</span>
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
    <a class="brand" href="index.html"><span class="brand__mark">P6</span><span class="brand__sub">Prievozská 6</span></a>
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
        <div class="foot__brand">P6</div>
        <p style="color:var(--text-inv-muted);max-width:38ch;font-size:.95rem">
          Mestské bývanie na Prievozskej 6. Miletička, škola, biznis zóna, Nivy aj nové centrum Bratislavy v prirodzenom dosahu.
        </p>
        <div class="badge-row" style="margin-top:22px">
          <span class="badge">{ADDRESS}</span>
        </div>
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
          <li><span style="color:var(--text-inv-muted);font-size:.92rem">Po – Pi, 9:00 – 18:00</span></li>
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
    s = ''.join(f'<script src="assets/js/{n}?v={ASSET_V}"></script>\n' for n in ('data.js', 'site.js', 'motion.js', 'plan.js'))
    for e in extra:
        s += f'<script src="assets/js/{e}?v={ASSET_V}"></script>\n'
    return s + "</body>\n</html>\n"

def photo(title, cap, cls="", ico="camera"):
    return f'<div class="photo {cls}">{svg(ico)}<b>{title}</b><span class="photo__cap">{cap}</span></div>'

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
 ("Je možné kúpiť parkovacie státie?", "Áno. Parkovacie státia a pivničné kobky sa predávajú samostatne k jednotlivým bytom."),
 ("Ponúkate virtuálnu prehliadku?", "Pripravujeme ju. Po dokončení fotodokumentácie sprístupníme 3D prehliadku každej dispozície priamo v detaile bytu."),
 ("Ako získam katalóg?", "Napíšte nám cez formulár a katalóg vám pošleme e-mailom hneď, ako bude pripravený."),
]

# §13 — six cards, one concrete benefit each, two sentences at most.
# ⚠️ Standard is NOT yet confirmed by the project — the page says so.
STANDARD = [
 ("Svetlo a okná",                    "Veľkoformátové okná s izolačným trojsklom. Viac denného svetla v izbách, menej hluku z ulice.",                        "detail: okenný profil a sklo"),
 ("Vykurovanie a chladenie",          "Podlahové kúrenie v celom byte s prípravou na chladenie. Stála teplota bez radiátorov na stenách.",                 "detail: podlahové kúrenie"),
 ("Kúpeľne",                          "Veľkoformátový obklad a zabudované zariaďovacie predmety. Kúpeľňa pripravená na bývanie od prvého dňa.",           "detail: obklad kúpeľne"),
 ("Podlahy a interiérové dvere",      "Drevené podlahy v obytných miestnostiach a dvere v jednotnom dizajne. Jeden detail od predsiene po spálňu.",        "detail: podlaha a dvere"),
 ("Parkovanie a nabíjanie",           "Parkovacie státie v garáži pod domom s prípravou na nabíjanie elektromobilu. Auto pod domom, nie na ulici.",        "detail: garáž a nabíjanie"),
 ("Bezpečnosť a spoločné priestory",  "Čipový vstup do domu a garáže, kamerový systém v spoločných priestoroch. Kočikáreň a kobky pod uzamknutím.",        "detail: vstup a spoločné priestory"),
]

# §12 — categories the brief wants listed here; values pending real data.
PARAMS = [
 ("Počet bytov", None), ("Počet podlaží", None), ("Parkovacie miesta", None), ("Typológie", None),
 ("Výmery bytov", None), ("Pivničné kobky", None), ("Terasy a balkóny", None),
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
        <div class="std__photo">Fotografia materiálu<br>{cap}</div>
        <div class="std__body"><h3>{t}</h3><p>{d}</p></div>
      </article>''' for t, d, cap in STANDARD)

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

    return (head("P6 — Domov medzi Miletičkou a Downtownom",
                 "Mestské bývanie na Prievozskej 6. Trh, škola, práca, Nivy aj nové centrum Bratislavy v prirodzenom dosahu.",
                 "", ld)
    + nav("index.html", over=True)
    + f'''<main id="main">

<!-- §1 Hero ============================================================ -->
<section class="hero">
  <div class="hero__vis" data-picker>
    <svg data-facade preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false"></svg>
    <div class="hero__scrim"></div>
    <div class="picker" role="group" aria-label="Interaktívny výber bytu z vizualizácie domu">
      <svg data-hotspots preserveAspectRatio="xMidYMid meet"></svg>
    </div>
    <div class="tip" data-tip data-show="false" role="status" aria-live="polite"></div>
    <div class="hero__top">
      <div class="shell shell-wide">
        <p class="hero__kicker"><span></span> Ilustračná vizualizácia · reálnu vizualizáciu P6 doplníme</p>
      </div>
    </div>
  </div>

  <div class="hero__content">
    <div class="shell shell-wide">
      <h1 class="hero__title">Domov medzi<br>Miletičkou a <em>Downtownom</em></h1>
      <p class="hero__sub">Mestské bývanie na Prievozskej 6. Trh, škola, práca, Nivy aj nové centrum Bratislavy v prirodzenom dosahu.</p>
      <div class="hero__actions">
        <a class="btn btn--primary" href="byty.html?status=dostupny">Pozrieť dostupné byty {svg("arrow")}</a>
        <a class="btn btn--ghost" href="#lokalita">Objaviť lokalitu</a>
      </div>

      <div style="display:flex;flex-wrap:wrap;gap:14px 30px;align-items:center;margin-top:30px;max-width:660px">
        <div class="legend">
          <button type="button" class="legend__item" data-legend="dostupny"><span class="legend__dot legend__dot--ok"></span>Voľný</button>
          <button type="button" class="legend__item" data-legend="rezervovany"><span class="legend__dot legend__dot--warn"></span>Rezervovaný</button>
          <button type="button" class="legend__item" data-legend="predany"><span class="legend__dot legend__dot--off"></span>Predaný</button>
        </div>
        <span class="picker__hint">{svg("cursor")} Vyberte byt priamo vo fasáde</span>
      </div>

      <div class="floorstrip-wrap" style="margin-top:26px">
        <p class="eyebrow">Alebo podľa podlažia</p>
        <div class="floorstrip" data-floorstrip></div>
      </div>
    </div>
  </div>

  <a class="hero__cue" href="#lokalita" aria-label="Prejsť na lokalitu">
    <span class="hero__cue-line"></span>
    <span>Posúvajte</span>
  </a>
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
      <div class="citymap__scroll" data-map-scroll><div data-map-stage></div></div>
      <span class="citymap__note">Schematická mapa · sever hore</span>
    </div>
    <p class="citymap__hint">{svg("swipe")} Potiahnite mapu do strán</p>

    <div class="keyfigs" style="margin-top:clamp(26px,3vw,40px)">
      <div class="keyfig"><b>5–10 min</b><span>škola, trh a biznis centrá</span></div>
      <div class="keyfig"><b>do 2 km</b><span>Nivy, Downtown, šport a Dunaj</span></div>
      <div class="keyfig"><b>10–15 min</b><span>letisko Bratislava autom</span></div>
      <div class="keyfig"><b>45–55 min</b><span>letisko Schwechat autom</span></div>
    </div>
    <p class="form__note" style="margin-top:12px">Uvedené časy sú orientačné.</p>
  </div>
</section>

<!-- §3 Hlavný manifest ================================================ -->
<section class="section section--ink manifest">
  <div class="shell">
    <div class="grid-2" style="align-items:end">
      <h2>Menej času<br>na cestách.<br><em>Viac času<br>na život.</em></h2>
      <p class="lede">{txt(
        "Kvalita bývania sa neukazuje iba vo výmere bytu. Ukazuje sa každé ráno – v ceste do práce, do školy, na nákup alebo za športom. P6 približuje všetko, čo tvorí každodenný mestský život.",
        "Kvalita bývania sa ukazuje každé ráno – v ceste do práce, do školy či na nákup. P6 približuje všetko, čo tvorí mestský život.")}</p>
    </div>
  </div>
</section>

<!-- §4 Miletička ======================================================= -->
<section class="section">
  <div class="shell shell-wide">
    {photo("Trhovisko Miletičova", "Fotografia · autentická, nie render", "photo--wide reveal")}
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
          <li class="point">približne 10 minút pešo</li>
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
        "Prievozská, Plynárenská a Mlynské nivy tvoria hlavnú biznis zónu Bratislavy. Apollo Business Center II sa nachádza prakticky v susedstve P6. Twin City, Nivy Tower, CBC a Sky Park sú dostupné pešo, bicyklom alebo kolobežkou.",
        "Prievozská, Plynárenská a Mlynské nivy tvoria hlavnú biznis zónu Bratislavy. Apollo Business Center II je prakticky v susedstve; Twin City, Nivy Tower, CBC a Sky Park sú na dosah pešo či bicyklom.")}</p>
    </div>
    <ol class="route" data-route></ol>
    <p class="form__note" style="margin-top:18px">Časy sú orientačné, počítané z P6 po bežných mestských trasách.</p>
  </div>
</section>

<!-- §6 Päťminútové mesto ============================================== -->
<section class="section section--ink" id="patminutove-mesto">
  <div class="shell shell-wide">
    <div style="max-width:60ch;margin-bottom:clamp(24px,3vw,36px)">
      <p class="eyebrow">Päťminútové mesto</p>
      <h2>Prepnite si spôsob dopravy.<br>Mesto sa prispôsobí.</h2>
    </div>
    <div class="fivemin" data-citymap="interactive" data-theme="dark">
      <div>
        <div class="fivemin__controls">
          <div class="seg" role="group" aria-label="Spôsob dopravy">
            <button type="button" data-mode="pesi" aria-pressed="true">Pešo</button>
            <button type="button" data-mode="bicykel" aria-pressed="false">Bicyklom</button>
            <button type="button" data-mode="kolobezka" aria-pressed="false">Kolobežkou</button>
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
          <div class="citymap__scroll" data-map-scroll><div data-map-stage></div></div>
          <span class="citymap__note">medená = do 5 min · svetlá = do 15 min</span>
        </div>
        <p class="citymap__hint" style="color:var(--text-inv-muted)">{svg("swipe")} Potiahnite mapu do strán</p>
      </div>
      <div>
        <p class="reach__summary" data-reach-summary></p>
        <ol class="reach" data-reach-list></ol>
        <p class="form__note" style="margin-top:14px;color:var(--text-inv-muted)">Časy sú orientačné.</p>
      </div>
    </div>
  </div>
</section>

<!-- §7 Rodina a škola ================================================= -->
<section class="section">
  <div class="shell shell-wide">
    <div class="grid-2" style="align-items:center">
      <div class="reveal">{photo("Rodič a dieťa", "Fotografia · cesta do školy", "photo--tall")}</div>
      <div class="reveal">
        <p class="eyebrow">Rodina a škola</p>
        <h2>Najkratšia cesta do školy je tá, ktorú prejdete pešo</h2>
        <p class="lede" style="margin-top:18px">{txt(
          "Spojená škola Novohradská sa nachádza v širšom susedstve P6. Každodenná cesta do školy preto nemusí znamenať ranné státie v aute ani ďalšiu cestu cez mesto.",
          "Spojená škola Novohradská je v širšom susedstve P6. Cesta do školy nemusí znamenať ranné státie v aute.")}</p>
        <ul class="points">
          <li class="point">základná škola</li>
          <li class="point">gymnázium</li>
          <li class="point">medzinárodné programy</li>
          <li class="point">približne 5–8 minút pešo</li>
        </ul>
        <p class="form__note" style="margin-top:14px">Informácie o medzinárodných programoch uvádzame podľa aktuálnej ponuky školy.</p>
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
      <article class="mob__card reveal">{svg("tram")}<h3>MHD</h3><p>Zastávky električiek a autobusov pár minút pešo od domu. Do centra aj na vlakovú stanicu bez auta.</p></article>
      <article class="mob__card reveal">{svg("bus")}<h3>Autobusová stanica</h3><p>Nivy – regionálne aj medzinárodné linky. Približne 15 minút pešo alebo pár minút bicyklom.</p></article>
      <article class="mob__card reveal">{svg("bike")}<h3>Cyklistické spojenia</h3><p>Cyklotrasy smerom na nábrežie a do centra. Bicykel alebo kolobežka ako každodenná voľba.</p></article>
      <article class="mob__card reveal">{svg("road")}<h3>Diaľnica a letiská</h3><p>Nájazd na D1 v blízkosti. Letisko Bratislava 10–15 min, Schwechat 45–55 min autom.</p></article>
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
      <div class="sport__item"><b>Zimný štadión Ondreja Nepelu</b><span>hokej a koncerty · <em>≈ 7 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Národný futbalový štadión</b><span>futbal · <em>≈ 9 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Fitness centrá</b><span>v okolí P6 · <em>≈ 6 min</em> pešo</span></div>
      <div class="sport__item"><b>Štrkovecké jazero</b><span>beh, korčule, oddych · <em>≈ 8 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Dunajská promenáda</b><span>beh a prechádzky · <em>≈ 10 min</em> bicyklom</span></div>
      <div class="sport__item"><b>Cyklistické spojenia</b><span>na nábrežie, do centra aj na Nivy</span></div>
    </div>
    <p class="form__note" style="margin-top:14px;color:var(--text-inv-muted)">Časy sú orientačné.</p>
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
    <div style="margin-top:clamp(30px,4vw,52px)">{photo("Vizualizácia P6", "Vizualizácia · s panorámou Downtownu", "photo--wide reveal", "cube")}</div>
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
      <div class="reveal">{photo("Komunitná terasa", "Fotografia · večerná atmosféra", "photo--ink photo--tall", "sun")}</div>
    </div>
  </div>
</section>

<!-- §12 Parametre projektu ============================================ -->
<section class="section section--paper2">
  <div class="shell shell-wide">
    <div style="max-width:56ch;margin-bottom:clamp(24px,3vw,36px)">
      <p class="eyebrow">Parametre projektu</p>
      <h2>Čísla, ktoré doplníme<br>po schválení projektu</h2>
    </div>
    <dl class="params">{params}</dl>
    <p class="form__note" style="margin-top:14px">Parametre zverejníme po schválení projektovej dokumentácie.</p>
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
    <p class="form__note" style="margin-top:16px">Ponuka v ukážke je ilustračná a nahradíme ju reálnym zoznamom bytov.</p>
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
''' + scripts("map.js", "building.js", "list.js"))

# ---------------------------------------------------------------- byty

def byty_html():
    floors = "".join(f'<option value="{i}">{i}. NP</option>' for i in range(1, 9))
    return (head(f"Byty — {NAME}",
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
        <span class="filters__count" data-count aria-live="polite">—</span>
        <button type="button" class="filters__reset" data-reset>Zrušiť filtre</button>
      </div>

      <div class="filters__scrim" data-filter-scrim hidden></div>
      <div class="filters__fields" id="filter-fields">
      <div class="filters__sheet-head"><span>Filtre</span>
        <button type="button" class="filters__sheet-close" data-filter-close aria-label="Zavrieť filtre">{svg("x")}</button></div>
      <div class="field"><label for="f-rooms">Počet izieb</label>
        <select id="f-rooms"><option value="">Všetky</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5 a viac</option></select></div>
      <div class="field"><label for="f-floor">Podlažie</label>
        <select id="f-floor"><option value="">Všetky</option>{floors}</select></div>
      <div class="field"><label for="f-area">Výmera</label>
        <select id="f-area"><option value="">Bez limitu</option><option value="40">od 40 m²</option><option value="60">od 60 m²</option><option value="80">od 80 m²</option><option value="100">od 100 m²</option><option value="140">od 140 m²</option></select></div>
      <div class="field"><label for="f-ext">Terasa alebo balkón</label>
        <select id="f-ext"><option value="">Všetky</option><option value="Terasa">Terasa</option><option value="Balkón">Balkón</option><option value="Predzáhradka">Predzáhradka</option></select></div>
      <div class="field"><label for="f-orient">Svetová orientácia</label>
        <select id="f-orient"><option value="">Všetky</option><option value="Juh">Juh</option><option value="Západ">Západ</option><option value="Východ">Východ</option><option value="Sever">Sever</option></select></div>
      <div class="field"><label for="f-status">Dostupnosť</label>
        <select id="f-status"><option value="">Všetky</option><option value="dostupny">Voľné</option><option value="rezervovany">Rezervované</option><option value="predany">Predané</option></select></div>
      <button type="button" class="btn btn--primary filters__apply" data-filter-close>Zobraziť <span data-count>—</span></button>
      </div>
    </form>
  </div>
</div>

<section class="section section--tight">
  <div class="shell shell-wide">
    <div class="ucards" data-cards></div>
    <div class="empty" data-empty hidden>
      <h3>Žiadny byt nezodpovedá filtrom</h3>
      <p class="lede" style="margin-inline:auto">Skúste uvoľniť niektorý z filtrov — alebo nám napíšte a nájdeme vám najbližšiu alternatívu.</p>
      <p><a class="btn btn--ghost" href="kontakt.html">Napísať nám</a></p>
    </div>
    <p class="form__note" style="margin-top:20px">Ponuka v ukážke je ilustračná a nahradíme ju reálnym zoznamom bytov.</p>
  </div>
</section>

''' + final_block() + '''
</main>
''' + FOOT + scripts("list.js"))

# ---------------------------------------------------------------- byt

def byt_html():
    return (head(f"Detail bytu — {NAME}",
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
            <p class="eyebrow">Pôdorys</p>
            <div class="plan" data-plan></div>
            <p class="form__note" style="margin-top:14px">Orientačná schéma dispozície — prejdite po miestnosti a zvýrazní sa aj v tabuľke. Presné pôdorysy doplníme.</p>
          </div>
          <div class="stack" style="gap:26px">
            <div>
              <p class="eyebrow">Výmery miestností</p>
              <table class="rooms" data-rooms>
                <thead><tr><th scope="col">Miestnosť</th><th scope="col">Plocha</th></tr></thead>
                <tbody></tbody>
                <tfoot><tr><td>Interiér spolu</td><td>—</td></tr></tfoot>
              </table>
            </div>
            <div class="compass-card">
              <div class="compass" data-compass></div>
              <div><p class="eyebrow" style="margin-bottom:6px">Orientácia</p><p class="compass-card__value" data-orientation>—</p></div>
            </div>
          </div>
        </div>

        <div>
          <p class="eyebrow">Poloha v dome</p>
          <div class="mini" data-mini></div>
          <div class="legend legend--tight">
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--ok"></span>Voľný</span>
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--warn"></span>Rezervovaný</span>
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--off"></span>Predaný</span>
            <span class="legend__item legend__item--static"><span class="legend__dot legend__dot--this"></span>Tento byt</span>
          </div>
          <p class="form__note" style="margin-top:8px">Kliknutím na iný byt sa presuniete na jeho detail. Šípkami ← → prechádzate dom po poradí. Schéma domu je ilustračná.</p>
        </div>

        <div class="grid-2" style="gap:16px">
          {photo("Fotografie bytu", "Doplníme po fotodokumentácii", "", "camera")}
          {photo("3D prehliadka", "Pripravujeme", "", "cube")}
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
''' + FOOT + scripts("building.js", "list.js", "detail.js"))

# ---------------------------------------------------------------- redirects

def redirect_html(target, title):
    return f'''<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=index.html{target}">
<link rel="canonical" href="{SITE}/{target}">
<title>{title} — {NAME}</title>
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
        ("Miletička ráno", "photo--wide"), ("Cyklista na Prievozskej", ""), ("Vizualizácia P6", ""),
        ("Nivy večer", "photo--wide"), ("Cesta do školy", ""), ("Apollo a biznis zóna", ""),
        ("Komunitná terasa", "photo--wide"), ("Dunajská promenáda", ""), ("Vzorový interiér", ""),
    ]
    g = "".join(f'<div class="{"gallery__wide" if c else ""}">{photo(t, "Fotografia bude doplnená", c or "")}</div>' for t, c in tiles)
    return (head(f"Galéria — {NAME}",
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
    return (head(f"Kontakt — {NAME}",
                 "Dohodnite si konzultáciu alebo si vyžiadajte katalóg. Napíšte nám, aký byt na Prievozskej 6 hľadáte.",
                 "kontakt.html")
    + nav("kontakt.html")
    + f'''<main id="main">
{page_head("Kontakt", "Povedzte nám,<br>čo hľadáte", "Napíšte nám počet izieb, orientáciu alebo rozpočet — a my sa ozveme s konkrétnymi bytmi, ktoré tomu zodpovedajú.", "Kontakt")}

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
          <div><label for="c-unit">Byt, ktorý vás zaujal</label><input id="c-unit" name="unit" type="text" placeholder="napr. 4.03 — alebo nechajte prázdne"></div>
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
            <div><dt>Otváracie hodiny</dt><dd>Pondelok – piatok<br>9:00 – 18:00</dd></div>
          </dl>
        </div>
        <div class="aside__box">
          <p class="eyebrow" style="margin-bottom:10px">Osobná obhliadka</p>
          <p style="font-size:.94rem;color:var(--text-muted);margin:0">Radi vám ukážeme projekt osobne — vrátane vzorových materiálov a presných dispozícií. Stretnutie si dohodneme telefonicky.</p>
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

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="8" fill="#14120F"/>
  <text x="32" y="41" text-anchor="middle" font-family="Georgia,serif" font-size="30" fill="#F7F4EF">P6</text>
  <circle cx="50" cy="16" r="5" fill="#B87333"/>
</svg>
'''

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
 "favicon.svg": FAVICON,
 "robots.txt": ROBOTS,
 "sitemap.xml": SITEMAP,
}

for name, content in files.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{name}: {len(content):>7} bytes")
