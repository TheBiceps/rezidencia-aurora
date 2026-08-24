# -*- coding: utf-8 -*-
# ===========================================================================
#  PAGE GENERATOR — optional.
#
#  The .html files in the parent folder ARE the deliverable and can be edited
#  by hand. This script regenerates all of them from the templates below; it
#  exists so shared chrome (nav, footer, CTA band, <head>) can be changed in
#  one place instead of seven.
#
#  ⚠️  RUNNING THIS OVERWRITES EVERY .html FILE.
#      If you have hand-edited the HTML, either port the change in here first
#      or do not run it at all.
#
#  Usage, from the folder ABOVE `rezidencia/`:
#      python3 rezidencia/_build/build_pages.py
#
#  Set PREVIEW = False below when the site goes live (removes noindex and
#  restores a real robots.txt).
# ===========================================================================
import os
OUT = "rezidencia"

SITE = "https://rezidencia-aurora.sk"
NAME = "Rezidencia Aurora"

# Client-preview build: adds noindex to every page and blocks crawlers in
# robots.txt. Set to False for the real launch.
PREVIEW = True

# Bump this whenever CSS/JS changes so browsers (and the client's phone)
# do not serve a stale cached copy. Appended as ?v= to every asset link.
ASSET_V = "10"

NAV = [
    ("projekt.html", "Projekt"),
    ("byty.html", "Byty"),
    ("lokalita.html", "Lokalita"),
    ("galeria.html", "Galéria"),
    ("kontakt.html", "Kontakt"),
]

I = {
 "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "x": '<path d="M6 6l12 12M18 6L6 18"/>',
 "building": '<path d="M4 21V5a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v16M14 10h5a1 1 0 0 1 1 1v10M4 21h16M8 8h2M8 12h2M8 16h2M17 14h1M17 18h1"/>',
 "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
 "car": '<path d="M5 17H3v-5l2-5h14l2 5v5h-2M5 17a2 2 0 1 0 4 0M15 17a2 2 0 1 0 4 0M9 17h6M5 12h14"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
 "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6.3 6.3l2.8 2.8M14.9 14.9l2.8 2.8M17.7 6.3l-2.8 2.8M9.1 14.9l-2.8 2.8"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.4 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.4 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
 "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/>',
 "camera": '<path d="M14.5 4h-5L8 6H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-4l-1.5-2Z"/><circle cx="12" cy="13" r="3.5"/>',
 "cube": '<path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
 "check": '<path d="m5 13 4 4L19 7"/>',
 "cursor": '<path d="m4 4 7 16 2.5-6.5L20 11 4 4Z"/>',
 "tap": '<path d="M9 11V6a2 2 0 1 1 4 0v8"/><path d="M13 12a2 2 0 1 1 4 0v1M17 13a2 2 0 1 1 4 0v3a5 5 0 0 1-5 5h-2.5a5 5 0 0 1-4.3-2.5L6 15"/>',
 "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
 "rows": '<path d="M3 6h18M3 12h18M3 18h18"/>',
 "sliders": '<path d="M4 6h10M18 6h2M4 12h2M10 12h10M4 18h10M18 18h2"/><circle cx="16" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="16" cy="18" r="2"/>',
 "train": '<rect x="5" y="3" width="14" height="13" rx="3"/><path d="M9 3v13M15 3v13M5 10h14M7 20l-2 2M17 20l2 2"/><circle cx="9" cy="19" r="0"/>',
}

def svg(key, cls="", extra=""):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
            f'{f'class="{cls}" ' if cls else ""}{extra}>{I[key]}</svg>')

def head(title, desc, page, extra=""):
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
{'<meta name="robots" content="noindex, nofollow">' if PREVIEW else ''}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v={ASSET_V}">
{extra}</head>
<body>
<a class="skip-link" href="#main">Preskočiť na obsah</a>
'''

def nav(page, over=False):
    links = "".join(
        f'<a class="nav__link" href="{h}"{" aria-current=\"page\"" if h == page else ""}>{t}</a>'
        for h, t in NAV)
    dlinks = "".join(
        f'<a class="drawer__link" href="{h}"{" aria-current=\"page\"" if h == page else ""}>{t}</a>'
        for h, t in NAV)
    return f'''<header class="nav {"nav--over" if over else "nav--solid"}" data-nav="{"over" if over else "solid"}">
  <div class="nav__inner">
    <a class="brand" href="index.html" aria-label="{NAME} — domov">
      <span class="brand__mark">AURORA</span>
      <span class="brand__sub">Bratislava</span>
    </a>
    <nav class="nav__links" aria-label="Hlavná navigácia">{links}</nav>
    <div class="nav__actions">
      <a class="btn btn--ghost nav__cta" href="kontakt.html">Mám záujem</a>
      <button class="nav__burger" type="button" data-drawer-open aria-expanded="false" aria-controls="drawer" aria-label="Otvoriť menu">{svg("menu")}</button>
    </div>
  </div>
  <div class="readbar"><span data-readbar></span></div>
</header>

<div class="drawer" id="drawer" data-drawer data-open="false" aria-hidden="true">
  <div class="drawer__top">
    <a class="brand" href="index.html"><span class="brand__mark">AURORA</span><span class="brand__sub">Bratislava</span></a>
    <button class="drawer__close" type="button" data-drawer-close aria-label="Zavrieť menu">{svg("x")}</button>
  </div>
  <nav class="drawer__links" aria-label="Mobilná navigácia">{dlinks}</nav>
  <div class="drawer__foot">
    <a href="tel:+421900000000">+421 900 000 000</a>
    <a href="mailto:info@rezidencia-aurora.sk">info@rezidencia-aurora.sk</a>
  </div>
</div>
'''

FOOT = f'''<footer class="foot">
  <div class="shell shell-wide">
    <div class="foot__grid">
      <div>
        <div class="foot__brand">Rezidencia Aurora</div>
        <p style="color:var(--text-inv-muted);max-width:36ch;font-size:.95rem">
          Päťdesiat bytov v Starom Meste. Tichá ulica, výhľad na mesto, päť minút pešo od nábrežia.
        </p>
        <div class="badge-row" style="margin-top:22px">
          <span class="badge">Placeholder 12, Bratislava</span>
        </div>
      </div>
      <div>
        <h4>Navigácia</h4>
        <ul>
          <li><a href="projekt.html">Projekt</a></li>
          <li><a href="byty.html">Ponuka bytov</a></li>
          <li><a href="lokalita.html">Lokalita</a></li>
          <li><a href="galeria.html">Galéria</a></li>
          <li><a href="kontakt.html">Kontakt</a></li>
        </ul>
      </div>
      <div>
        <h4>Predaj</h4>
        <ul>
          <li><a href="tel:+421900000000">+421 900 000 000</a></li>
          <li><a href="mailto:info@rezidencia-aurora.sk">info@rezidencia-aurora.sk</a></li>
          <li><span style="color:var(--text-inv-muted);font-size:.92rem">Po – Pi, 9:00 – 18:00</span></li>
        </ul>
      </div>
    </div>
    <div class="foot__bottom">
      <span>© <span data-year>2026</span> {NAME}. Všetky práva vyhradené.</span>
      <span>Vizualizácie sú ilustračné. Uvedené výmery a ceny sú projektové a nie sú návrhom na uzavretie zmluvy.</span>
    </div>
  </div>
</footer>
'''

def scripts(*extra):
    s = ''.join(f'<script src="assets/js/{n}?v={ASSET_V}"></script>\n'
                for n in ('data.js', 'site.js', 'motion.js'))
    for e in extra:
        s += f'<script src="assets/js/{e}?v={ASSET_V}"></script>\n'
    return s + "</body>\n</html>\n"

def ph(title, note, cls="", ico="camera"):
    return f'''<div class="ph {cls}">{svg(ico)}<b>{title}</b><span>{note}</span></div>'''

def cta_band():
    return f'''<section class="section section--ink">
  <div class="shell">
    <div class="grid-2">
      <div>
        <p class="eyebrow">Rezervácia</p>
        <h2>Vyberte si byt<br>skôr než to<br><em style="font-style:italic;color:var(--sand-2)">urobí niekto iný</em></h2>
      </div>
      <div>
        <p class="lede">Aktuálne je voľných <strong data-count-free>—</strong> z päťdesiatich bytov. Ozvite sa nám a dohodneme si osobnú obhliadku alebo online konzultáciu — prevedieme vás dispozíciami, výhľadmi aj možnosťami financovania.</p>
        <div class="hero__actions" style="margin-top:26px">
          <a class="btn btn--light" href="kontakt.html">Nezáväzne sa informovať {svg("arrow")}</a>
          <a class="btn btn--onink" href="byty.html">Prezrieť ponuku</a>
        </div>
      </div>
    </div>
  </div>
</section>
'''

def page_head(crumb, title, lede, current):
    c = ""
    if crumb:
        c = f'''<nav class="crumbs" aria-label="Omrvinková navigácia" style="margin-bottom:22px">
      <a href="index.html">Domov</a><span aria-hidden="true">/</span><span>{crumb}</span></nav>'''
    return f'''<section class="page-head">
  <div class="shell">
    {c}
    <p class="eyebrow">{current}</p>
    <h1>{title}</h1>
    <p class="lede maxw">{lede}</p>
  </div>
</section>'''

# =============================================================================
# index.html
# =============================================================================

FEATURES = [
 ("building", "Architektúra s mierou", "Sedem podlaží tehlovej hmoty, dve ustúpené podlažia s terasami. Fasáda v teplom pieskovom odtieni, ktorý starne dobre."),
 ("sun", "Svetlo ako materiál", "Okná od podlahy po strop vo všetkých obytných miestnostiach. Väčšina bytov je orientovaná na juh alebo juhozápad."),
 ("leaf", "Zeleň vo vnútrobloku", "Vzrastlá zeleň, vodný prvok a tiché átrium prístupné len rezidentom. Bez prejazdu áut."),
 ("car", "Parkovanie pod domom", "Dve podzemné podlažia, nabíjacie stanice pre elektromobily, pivničné kobky ku každému bytu."),
 ("shield", "Bezpečnosť a súkromie", "Recepcia, kamerový systém, čipový prístup do každého podlažia a do garáže."),
 ("spark", "Pripravené na budúcnosť", "Rekuperácia, podlahové kúrenie, príprava na chladenie a smart-home riadenie v každom byte."),
]

FIGURES = [
 ("50", "Bytov"),
 ("8", "Nadzemných podlaží"),
 ("1 – 5", "Izbové dispozície"),
 ("33 – 178", "m² interiéru"),
]

FAQ = [
 ("Kedy bude projekt dokončený?", "Presný termín odovzdania upresníme v najbližšej aktualizácii. Priebežne informujeme záujemcov e-mailom — stačí nechať kontakt."),
 ("Ako prebieha rezervácia bytu?", "Vyberiete si byt, podpíšeme rezervačnú zmluvu a uhradíte rezervačný poplatok. Byt následne stiahneme z ponuky a pripravíme zmluvu o budúcej kúpnej zmluve."),
 ("V akom štandarde sa byty odovzdávajú?", "Kompletný popis štandardu doplníme. Počítajte s dokončeným povrchom podláh, zariadenou kúpeľňou a pripravenými rozvodmi pre kuchynskú linku."),
 ("Dá sa dispozícia bytu upraviť?", "Áno, klientske zmeny riešime individuálne do uzávierky, ktorú si dohodneme pri podpise zmluvy."),
 ("Je možné kúpiť parkovacie státie?", "Áno. Parkovacie státia a pivničné kobky sa predávajú samostatne k jednotlivým bytom."),
 ("Ponúkate virtuálnu prehliadku?", "Pripravujeme ju. Po dokončení fotodokumentácie sprístupníme 3D prehliadku každej dispozície priamo v detaile bytu."),
]

def index_html():
    feats = "".join(
        f'<article class="feature reveal">{svg(k)}<h3>{t}</h3><p>{d}</p></article>'
        for k, t, d in FEATURES)
    figs = "".join(
        f'<div class="figure"><b{f" data-countup={v}" if v.isdigit() else ""}>{v}</b><span>{l}</span></div>'
        for v, l in FIGURES)
    faq = "".join(
        f'<details><summary>{q}</summary><div class="faq__body"><p>{a}</p></div></details>'
        for q, a in FAQ)

    ld = '''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ApartmentComplex","name":"Rezidencia Aurora",
"numberOfAccommodationUnits":50,"numberOfFloors":8,
"address":{"@type":"PostalAddress","streetAddress":"Placeholder 12","addressLocality":"Bratislava","addressRegion":"Staré Mesto","addressCountry":"SK"},
"url":"''' + SITE + '''/"}
</script>
'''
    return (head(f"{NAME} — 50 bytov v centre Bratislavy",
                 "Päťdesiat bytov v Starom Meste Bratislavy. Vyberte si byt priamo z vizualizácie domu — dispozície, výmery, orientácia a dostupnosť na jednom mieste.",
                 "", ld)
    + nav("index.html", over=True)
    + f'''<main id="main">

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
        <p class="hero__kicker"><span></span> Bratislava · Staré Mesto</p>
      </div>
    </div>
  </div>

  <div class="hero__content">
    <div class="shell shell-wide">
      <h1 class="hero__title">Päťdesiat bytov.<br>Jedna <em>adresa</em>.</h1>
      <p class="hero__sub">Vyberte si byt priamo z vizualizácie domu. Dispozícia, výmera, orientácia aj dostupnosť na jeden pohľad.</p>
      <div class="hero__actions">
        <a class="btn btn--primary" href="byty.html">Ponuka bytov {svg("arrow")}</a>
        <a class="btn btn--ghost" href="projekt.html">O projekte</a>
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

  <a class="hero__cue" href="#o-projekte" aria-label="Prejsť na ďalšiu sekciu">
    <span class="hero__cue-line"></span>
    <span>Posúvajte</span>
  </a>

  <div class="hero__stats">
    <div class="shell shell-wide">
      <div class="hero__stats-grid">
        <div class="hero__stat"><b data-count-free>—</b><span>Voľných bytov</span></div>
        <div class="hero__stat"><b data-countup="8">8</b><span>Podlaží</span></div>
        <div class="hero__stat"><b>1 – 5</b><span>Izieb</span></div>
        <div class="hero__stat"><b>33 – 178</b><span>m² interiéru</span></div>
      </div>
    </div>
  </div>
</section>
<div data-nav-sentinel aria-hidden="true"></div>

<section class="section" id="o-projekte">
  <div class="shell">
    <div class="grid-2">
      <div class="reveal">
        <p class="eyebrow">O projekte</p>
        <h2>Dom, ktorý sa<br>nesnaží prekričať<br>svoje okolie</h2>
      </div>
      <div class="reveal">
        <p class="lede">Aurora stojí v tichej časti Starého Mesta — dosť blízko na to, aby ste všetko zvládli pešo, a dosť ďaleko na to, aby ste v nedeľu ráno počuli vtáky namiesto električky.</p>
        <p>Päťdesiat bytov od kompaktných jednoizbových po päťizbové penthousy s terasami. Každý byt má vlastný vonkajší priestor, väčšina výhľad ponad strechy smerom k hradu.</p>
        <p style="margin-bottom:0"><a class="link-arrow" href="projekt.html">Viac o projekte {svg("arrow")}</a></p>
      </div>
    </div>
  </div>
</section>

<section class="section--ink">
  <div class="shell shell-wide">
    <div class="figures">{figs}</div>
  </div>
</section>

<section class="scrolly" id="dom" data-scrolly aria-label="Dom po podlažiach">
  <div class="scrolly__inner shell shell-wide">
    <div class="scrolly__head">
      <p class="eyebrow">Zdola nahor</p>
      <h2 class="scrolly__title">Dom po<br>podlažiach</h2>
    </div>

    <div class="scrolly__stage" data-stage>
      <div class="scrolly__graphic">
        <svg data-scrolly-facade preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false"></svg>
        <svg class="scrolly__bands" data-scrolly-bands preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false"></svg>
      </div>
      <div class="scrolly__meta">
        <span class="scrolly__time" data-timelabel>Ráno</span>
        <span class="scrolly__no"><b data-stepno>01</b> / 05</span>
      </div>
      <div class="scrolly__rail"><span data-progress></span></div>
    </div>

    <ol class="scrolly__steps">
        <li class="scrolly__step" data-step data-floors="0" data-zoom="1.05">
          <span class="scrolly__kicker">Parter</span>
          <h3>Vstup a spoločné priestory</h3>
          <p>Recepcia, kočikáreň a priamy vstup do podzemných garáží. Jediné miesto, kadiaľ sa do domu vchádza — a jediné, kde sa dom otvára ulici.</p>
        </li>
        <li class="scrolly__step" data-step data-floors="1,2,3,4,5,6" data-zoom="1">
          <span class="scrolly__kicker">1. – 6. podlažie</span>
          <h3>Ťažisko domu</h3>
          <p>Šesť plných podlaží, sedem bytov na každom. Jedno- až štvorizbové dispozície s loggiou, väčšina orientovaná na juh a juhozápad.</p>
        </li>
        <li class="scrolly__step" data-step data-floors="7" data-zoom="1.08">
          <span class="scrolly__kicker">7. podlažie</span>
          <h3>Prvé ustúpenie</h3>
          <p>Hmota sa zužuje o jedno pole na každej strane. Päť bytov získa terasu na streche podlažia pod sebou — a výhľad ponad okolité strechy.</p>
        </li>
        <li class="scrolly__step" data-step data-floors="8" data-zoom="1.12">
          <span class="scrolly__kicker">8. podlažie</span>
          <h3>Tri penthousy</h3>
          <p>Najvyššie podlažie ustupuje ešte raz. Tri byty so 142 až 178 m² interiéru a terasami, z ktorých dovidíte k hradu aj na Dunaj.</p>
        </li>
        <li class="scrolly__step" data-step data-floors="" data-zoom="1">
          <span class="scrolly__kicker">Celý dom</span>
          <h3>Päťdesiat bytov</h3>
          <p>Od 33 m² po 178 m². Každý byt s vlastným vonkajším priestorom, parkovaním pod domom a pivničnou kobkou.</p>
        </li>
    </ol>
  </div>
</section>

<section class="section section--paper2">
  <div class="shell">
    <div style="max-width:56ch;margin-bottom:clamp(36px,5vw,60px)">
      <p class="eyebrow">Štandard</p>
      <h2>Detaily, ktoré<br>cítiť každý deň</h2>
    </div>
    <div class="feature-grid">{feats}</div>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div style="display:flex;flex-wrap:wrap;gap:24px;align-items:flex-end;justify-content:space-between;margin-bottom:clamp(30px,4vw,48px)">
      <div>
        <p class="eyebrow">Aktuálna ponuka</p>
        <h2>Voľné byty</h2>
      </div>
      <a class="link-arrow" href="byty.html">Všetkých 50 bytov {svg("arrow")}</a>
    </div>
    <div class="cards" data-featured></div>
  </div>
</section>

<section class="section section--ink">
  <div class="shell">
    <div class="grid-2">
      <div>
        <p class="eyebrow">Virtuálna prehliadka</p>
        <h2>Prejdite si byt<br>ešte pred<br>obhliadkou</h2>
        <p class="lede" style="margin-top:20px">Pripravujeme 3D prehliadky vzorových dispozícií. Po spustení ich nájdete priamo v detaile každého bytu.</p>
        <p style="margin-top:24px"><a class="btn btn--onink" href="kontakt.html">Chcem vedieť, keď spustíme {svg("arrow")}</a></p>
      </div>
      <div>{ph("Virtuálna prehliadka", "Miesto pre 3D prehliadku (Matterport alebo obdobné riešenie). Sprístupníme po dokončení fotodokumentácie.", "ph--tall ph--ink", "cube")}</div>
    </div>
  </div>
</section>

<section class="section section--paper2">
  <div class="shell">
    <div class="grid-2" style="align-items:start">
      <div class="reveal">
        <p class="eyebrow">Lokalita</p>
        <h2>Päť minút pešo<br>k nábrežiu</h2>
        <p class="lede" style="margin-top:20px">Obchody, škôlka, kaviarne aj zastávka MHD v okruhu pár sto metrov. Autom ste na diaľnici za sedem minút.</p>
        <p style="margin-top:22px"><a class="link-arrow" href="lokalita.html">Preskúmať okolie {svg("arrow")}</a></p>
      </div>
      <div class="reveal">{ph("Mapa okolia", "Doplníme interaktívnu mapu s vyznačenými bodmi záujmu.", "", "pin")}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div style="max-width:52ch;margin-bottom:clamp(28px,4vw,44px)">
      <p class="eyebrow">Časté otázky</p>
      <h2>Čo sa najčastejšie pýtate</h2>
    </div>
    <div class="faq">{faq}</div>
  </div>
</section>

''' + cta_band() + '''
</main>
''' + FOOT
    + '''<script>
/* six available apartments, largest first, on the landing page */
document.addEventListener('DOMContentLoaded', function () {
  var wrap = document.querySelector('[data-featured]');
  if (!wrap) return;
  var picks = APARTMENTS.filter(function (a) { return a.status === 'dostupny'; })
    .sort(function (a, b) { return b.area - a.area; }).slice(0, 6);
  wrap.innerHTML = picks.map(function (a) {
    return '<a class="card" href="byt.html?id=' + encodeURIComponent(a.id) + '">' +
      '<div class="card__top"><div><div class="card__id">' + a.id + '</div>' +
      '<div class="card__type">' + a.type + ' · ' + a.floor + '. NP</div></div>' +
      '<span class="pill pill--' + a.status + '">' + STATUS_LABEL[a.status] + '</span></div>' +
      '<dl class="card__rows">' +
      '<div class="card__row"><dt>Interiér</dt><dd>' + fmtArea(a.area) + ' m²</dd></div>' +
      '<div class="card__row"><dt>' + a.extKind + '</dt><dd>' + fmtArea(a.ext) + ' m²</dd></div>' +
      '<div class="card__row"><dt>Cena</dt><dd class="card__price">' + fmtPrice(a.price, a.status) + '</dd></div>' +
      '</dl></a>';
  }).join('');
});
</script>
'''
    + scripts("building.js"))

# =============================================================================
# byty.html
# =============================================================================

def byty_html():
    floors = "".join(f'<option value="{i}">{i}. NP</option>' for i in range(1, 9))
    ths = [
        ("id", "Byt"), (None, "Dispozícia"), ("floor", "Podlažie"),
        ("area", "Interiér m²"), ("ext", "Exteriér m²"), ("total", "Spolu m²"),
        (None, "Orientácia"), ("status", "Stav"), ("price", "Cena"),
    ]
    head_cells = "".join(
        f'<th scope="col">{f"<button type=\"button\" data-sort=\"{k}\">{t}</button>" if k else t}</th>'
        for k, t in ths) + '<th scope="col"><span class="sr-only">Detail</span></th>'

    return (head(f"Ponuka bytov — {NAME}",
                 "Kompletný prehľad 50 bytov: dispozícia, výmera, podlažie, orientácia, dostupnosť a cena. Filtrujte podľa počtu izieb, podlažia či rozpočtu.",
                 "byty.html")
    + nav("byty.html")
    + f'''<main id="main" data-list>
{page_head("Byty", "Ponuka bytov", "Päťdesiat bytov na ôsmich podlažiach. Filtrujte podľa dispozície, podlažia alebo rozpočtu — a kliknutím sa dostanete na detail s pôdorysom.", "Aktuálna dostupnosť")}

<div class="filters">
  <div class="shell">
    <form class="filters__inner" role="search" aria-label="Filtrovanie bytov" onsubmit="return false">
      <div class="filters__bar">
        <button type="button" class="filters__toggle" data-filter-toggle
                aria-expanded="false" aria-controls="filter-fields">
          {svg("sliders")}<span>Filtre</span>
          <span class="filters__badge" data-filter-badge hidden></span>
        </button>
        <span class="filters__count" data-count aria-live="polite">—</span>
        <button type="button" class="filters__reset" data-reset>Zrušiť filtre</button>
        <div class="toggle" role="group" aria-label="Zobrazenie">
          <button type="button" data-view="table" aria-label="Zobraziť ako tabuľku">{svg("rows")}</button>
          <button type="button" data-view="cards" aria-label="Zobraziť ako karty">{svg("grid")}</button>
        </div>
      </div>

      <div class="filters__scrim" data-filter-scrim hidden></div>

      <div class="filters__fields" id="filter-fields">
      <div class="filters__sheet-head">
        <span>Filtre</span>
        <button type="button" class="filters__sheet-close" data-filter-close aria-label="Zavrieť filtre">{svg("x")}</button>
      </div>
      <div class="field">
        <label for="f-status">Stav</label>
        <select id="f-status"><option value="">Všetky</option><option value="dostupny">Voľné</option><option value="rezervovany">Rezervované</option><option value="predany">Predané</option></select>
      </div>
      <div class="field">
        <label for="f-rooms">Dispozícia</label>
        <select id="f-rooms"><option value="">Všetky</option><option value="1">1-izbový</option><option value="2">2-izbový</option><option value="3">3-izbový</option><option value="4">4-izbový</option><option value="5">Penthouse</option></select>
      </div>
      <div class="field">
        <label for="f-floor">Podlažie</label>
        <select id="f-floor"><option value="">Všetky</option>{floors}</select>
      </div>
      <div class="field">
        <label for="f-area">Min. plocha</label>
        <select id="f-area"><option value="">Bez limitu</option><option value="40">od 40 m²</option><option value="60">od 60 m²</option><option value="80">od 80 m²</option><option value="100">od 100 m²</option><option value="140">od 140 m²</option></select>
      </div>
      <div class="field">
        <label for="f-price">Cena do</label>
        <select id="f-price"><option value="">Bez limitu</option><option value="200000">200 000 €</option><option value="300000">300 000 €</option><option value="400000">400 000 €</option><option value="600000">600 000 €</option><option value="900000">900 000 €</option></select>
      </div>
      <button type="button" class="btn btn--primary filters__apply" data-filter-close>
        Zobraziť <span data-count>—</span>
      </button>
      </div>
    </form>
  </div>
</div>

<section class="section section--tight">
  <div class="shell">
    <div class="table-wrap" data-table>
      <table class="units">
        <caption class="sr-only">Zoznam bytov v projekte {NAME}</caption>
        <thead><tr>{head_cells}</tr></thead>
        <tbody data-rows></tbody>
      </table>
    </div>
    <div class="cards" data-cards hidden></div>
    <div class="empty" data-empty hidden>
      <h3>Žiadny byt nezodpovedá filtrom</h3>
      <p class="lede" style="margin-inline:auto">Skúste uvoľniť niektorý z filtrov — alebo nám napíšte a nájdeme vám najbližšiu alternatívu.</p>
      <p><a class="btn btn--ghost" href="kontakt.html">Napísať nám</a></p>
    </div>
  </div>
</section>

''' + cta_band() + '''
</main>
''' + FOOT + scripts("list.js"))

# =============================================================================
# byt.html
# =============================================================================

def byt_html():
    return (head(f"Detail bytu — {NAME}",
                 "Detail bytu: dispozícia, výmery jednotlivých miestností, orientácia, cena a dostupnosť.",
                 "byt.html", '' if PREVIEW else '<meta name="robots" content="noindex">\n')
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
            <p class="form__note" style="margin-top:14px">
              Orientačná schéma dispozície — prejdite po miestnosti a zvýrazní sa aj v tabuľke.
              Presné pôdorysy vo formáte PDF doplníme.
            </p>
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
              <div>
                <p class="eyebrow" style="margin-bottom:6px">Orientácia</p>
                <p class="compass-card__value" data-orientation>—</p>
              </div>
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
          <p class="form__note" style="margin-top:8px">
            Kliknutím na ktorýkoľvek byt sa presuniete na jeho detail. Šípkami ← → prechádzate dom po poradí.
          </p>
        </div>

        <div class="grid-2" style="gap:16px">
          {ph("Fotografie bytu", "Doplníme po dokončení fotodokumentácie.", "", "camera")}
          {ph("3D prehliadka", "Virtuálnu prehliadku pripravujeme.", "", "cube")}
        </div>

        <div class="detail-nav" data-detailnav></div>
      </div>

      <aside class="aside" data-aside aria-label="Cena a kontakt"></aside>
    </div>
  </div>
</section>

<section class="section section--paper2" data-similar>
  <div class="shell">
    <p class="eyebrow">Podobné byty</p>
    <h2 style="margin-bottom:clamp(26px,4vw,40px)">Rovnaká typológia</h2>
    <div class="cards" data-similar-cards></div>
  </div>
</section>

''' + cta_band() + '''
</main>
''' + FOOT + scripts("building.js", "detail.js"))

# =============================================================================
# projekt.html
# =============================================================================

TIMELINE = [
 ("Fáza 01", "Príprava a povolenia", "Kompletná projektová dokumentácia a povolenia."),
 ("Fáza 02", "Hrubá stavba", "Nosná konštrukcia, stropy, obvodový plášť."),
 ("Fáza 03", "Fasáda a technológie", "Zateplenie, okná, rozvody, vzduchotechnika."),
 ("Fáza 04", "Interiéry a odovzdanie", "Povrchy, zariaďovacie predmety, kolaudácia a odovzdanie kľúčov."),
]

def projekt_html():
    feats = "".join(f'<article class="feature reveal">{svg(k)}<h3>{t}</h3><p>{d}</p></article>' for k, t, d in FEATURES)
    tl = "".join(f'<div class="tl"><dt>{a}</dt><dd><b>{b}</b><span>{c}</span></dd></div>' for a, b, c in TIMELINE)
    return (head(f"Projekt — {NAME}",
                 "O projekte Rezidencia Aurora: architektúra, štandard vyhotovenia, technológie a harmonogram výstavby.",
                 "projekt.html")
    + nav("projekt.html")
    + f'''<main id="main">
{page_head("Projekt", "Dom postavený<br>na detailoch", "Aurora nie je o počte podlaží ani o metroch štvorcových. Je o tom, ako sa v byte býva o päť rokov — keď už novota vyprchá a zostanú materiály, svetlo a ticho.", "Projekt")}

<section class="section--tight">
  <div class="shell">{ph("Vizualizácia projektu", "Miesto pre hlavnú vizualizáciu domu v šírke stránky.", "ph--tall")}</div>
</section>

<section class="section">
  <div class="shell">
    <div class="grid-2">
      <div class="reveal">
        <p class="eyebrow">Architektúra</p>
        <h2>Tehla, sklo,<br>a veľa neba</h2>
      </div>
      <div class="reveal">
        <p class="lede">Hmota domu je rozdelená do troch častí, aby nepôsobila ako jeden blok. Spodných šesť podlaží drží uličnú čiaru, siedme a ôsme ustupujú a vytvárajú terasy s výhľadom nad strechy.</p>
        <p>Fasáda kombinuje tehlový obklad v teplom pieskovom odtieni s kovovými detailmi a sklenenými zábradliami. Materiály sme vyberali podľa toho, ako vyzerajú po desiatich rokoch — nie po desiatich dňoch.</p>
      </div>
    </div>
  </div>
</section>

<section class="section--ink section--tight">
  <div class="shell shell-wide">
    <div class="figures">{"".join(f'<div class="figure"><b>{v}</b><span>{l}</span></div>' for v, l in FIGURES)}</div>
  </div>
</section>

<section class="section section--paper2">
  <div class="shell">
    <div style="max-width:56ch;margin-bottom:clamp(36px,5vw,60px)">
      <p class="eyebrow">Štandard</p>
      <h2>Čo je v cene bytu</h2>
    </div>
    <div class="feature-grid">{feats}</div>
    <p class="form__note" style="margin-top:26px">Detailný popis štandardu vyhotovenia doplníme — pošleme ho na vyžiadanie e-mailom.</p>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="grid-2" style="align-items:start">
      <div>
        <p class="eyebrow">Harmonogram</p>
        <h2>Ako to<br>pôjde ďalej</h2>
        <p class="lede" style="margin-top:20px">Konkrétne termíny upresníme v najbližšej aktualizácii. Ak chcete byť informovaní, nechajte nám e-mail.</p>
      </div>
      <div class="timeline">{tl}</div>
    </div>
  </div>
</section>

<section class="section section--paper2">
  <div class="shell">
    <p class="eyebrow">Dispozície</p>
    <h2 style="margin-bottom:clamp(26px,4vw,40px)">Sedem typológií,<br>päťdesiat bytov</h2>
    <div class="cards" data-layouts></div>
    <p style="margin-top:28px"><a class="link-arrow" href="byty.html">Prezrieť konkrétne byty {svg("arrow")}</a></p>
  </div>
</section>

''' + cta_band() + '''
</main>
''' + FOOT + '''<script>
document.addEventListener('DOMContentLoaded', function () {
  var wrap = document.querySelector('[data-layouts]');
  if (!wrap) return;
  var seen = {};
  APARTMENTS.forEach(function (a) {
    if (!seen[a.layout]) seen[a.layout] = { layout: a.layout, type: a.type, min: a.area, max: a.area, free: 0, n: 0 };
    var s = seen[a.layout];
    s.min = Math.min(s.min, a.area); s.max = Math.max(s.max, a.area);
    s.n++; if (a.status === 'dostupny') s.free++;
  });
  wrap.innerHTML = Object.keys(seen).sort().map(function (k) {
    var s = seen[k];
    return '<a class="card" href="byty.html?rooms=' + (s.type.indexOf('Penthouse') === 0 ? 5 : parseInt(s.type)) + '">' +
      '<div class="card__top"><div><div class="card__id">' + s.layout + '</div>' +
      '<div class="card__type">' + s.type + '</div></div></div>' +
      '<dl class="card__rows">' +
      '<div class="card__row"><dt>Interiér</dt><dd>' + fmtArea(s.min) + ' – ' + fmtArea(s.max) + ' m²</dd></div>' +
      '<div class="card__row"><dt>Počet v dome</dt><dd>' + s.n + '</dd></div>' +
      '<div class="card__row"><dt>Voľné</dt><dd>' + s.free + '</dd></div>' +
      '</dl></a>';
  }).join('');
});
</script>
''' + scripts())

# =============================================================================
# lokalita.html
# =============================================================================

POI = [
 ("Doprava", ["Zastávka MHD — 2 min pešo", "Hlavná stanica — 9 min autom", "Nájazd na diaľnicu — 7 min autom", "Letisko M. R. Štefánika — 20 min autom"]),
 ("Každodenné", ["Potraviny — 3 min pešo", "Lekáreň — 4 min pešo", "Pošta — 6 min pešo", "Fitnes — 5 min pešo"]),
 ("Rodina", ["Materská škola — 5 min pešo", "Základná škola — 8 min pešo", "Detské ihrisko — 3 min pešo", "Pediater — 7 min pešo"]),
 ("Voľný čas", ["Nábrežie Dunaja — 5 min pešo", "Kaviarne a reštaurácie — 2 min pešo", "Mestský park — 6 min pešo", "Historické centrum — 12 min pešo"]),
]

def lokalita_html():
    blocks = "".join(
        '<article class="feature reveal">' + svg("pin") + f'<h3>{t}</h3><ul style="list-style:none;margin:0;padding:0;display:grid;gap:9px">'
        + "".join(f'<li style="font-size:.92rem;color:var(--text-muted)">{x}</li>' for x in items)
        + '</ul></article>'
        for t, items in POI)
    return (head(f"Lokalita — {NAME}",
                 "Kde Rezidencia Aurora stojí: dostupnosť MHD, školy, obchody, nábrežie a historické centrum Bratislavy na dosah.",
                 "lokalita.html")
    + nav("lokalita.html")
    + f'''<main id="main">
{page_head("Lokalita", "Tichá ulica,<br>mesto na dosah", "Adresa, na ktorej sa dá žiť bez auta. Väčšinu vecí, ktoré počas týždňa potrebujete, máte v okruhu desiatich minút chôdze.", "Lokalita")}

<section class="section--tight">
  <div class="shell">
    <div class="map-frame">{ph("Interaktívna mapa", "Sem vložíme mapu s vyznačenou polohou domu a bodmi záujmu (Google Maps / Mapy.cz embed).", "", "pin")}</div>
    <p class="form__note" style="margin-top:14px">Presná adresa: Placeholder 12, 811 01 Bratislava — Staré Mesto.</p>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div style="max-width:56ch;margin-bottom:clamp(36px,5vw,60px)">
      <p class="eyebrow">V okolí</p>
      <h2>Čo máte<br>za rohom</h2>
    </div>
    <div class="feature-grid">{blocks}</div>
    <p class="form__note" style="margin-top:26px">Uvedené vzdialenosti sú orientačné a doplníme ich po finálnom zameraní.</p>
  </div>
</section>

<section class="section section--ink">
  <div class="shell">
    <div class="grid-2">
      <div>
        <p class="eyebrow">Výhľady</p>
        <h2>Ponad strechy<br>Starého Mesta</h2>
        <p class="lede" style="margin-top:20px">Byty od štvrtého podlažia vyššie majú výhľad ponad okolitú zástavbu. Z terás na siedmom a ôsmom podlaží dovidíte k hradu aj na Dunaj.</p>
      </div>
      <div>{ph("Výhľad z bytu", "Doplníme fotografie výhľadov z jednotlivých podlaží.", "ph--tall ph--ink")}</div>
    </div>
  </div>
</section>

''' + cta_band() + '''
</main>
''' + FOOT + scripts())

# =============================================================================
# galeria.html
# =============================================================================

def galeria_html():
    tiles = [
        ("Exteriér — pohľad z ulice", "wide"), ("Vstupná hala", ""), ("Átrium a zeleň", ""),
        ("Vzorový obývací priestor", "wide"), ("Kúpeľňa v štandarde", ""), ("Terasa penthousu", ""),
        ("Podzemná garáž", ""), ("Detail fasády", ""), ("Nočný pohľad", "wide"),
    ]
    g = "".join(ph(t, "Fotografia bude doplnená.", "ph--wide" if c else "") for t, c in tiles)
    return (head(f"Galéria — {NAME}",
                 "Vizualizácie a fotografie projektu Rezidencia Aurora — exteriér, spoločné priestory, vzorové interiéry a výhľady.",
                 "galeria.html")
    + nav("galeria.html")
    + f'''<main id="main">
{page_head("Galéria", "Ako to bude<br>vyzerať", "Vizualizácie exteriéru a spoločných priestorov. Fotografie interiérov a výhľadov dopĺňame priebežne.", "Galéria")}

<section class="section section--tight">
  <div class="shell">
    <div class="gallery">{g}</div>
  </div>
</section>

<section class="section section--paper2">
  <div class="shell center" style="max-width:56ch">
    <p class="eyebrow eyebrow--center">Pripravujeme</p>
    <h2>Virtuálne prehliadky bytov</h2>
    <p class="lede" style="margin-top:18px">Po dokončení fotodokumentácie sprístupníme 3D prehliadku každej dispozície priamo v detaile bytu. Ak chcete vedieť, keď to spustíme, nechajte nám e-mail.</p>
    <p style="margin-top:24px"><a class="btn btn--primary" href="kontakt.html">Dať mi vedieť {svg("arrow")}</a></p>
  </div>
</section>

''' + cta_band() + '''
</main>
''' + FOOT + scripts())

# =============================================================================
# kontakt.html
# =============================================================================

def kontakt_html():
    return (head(f"Kontakt — {NAME}",
                 "Máte záujem o byt v Rezidencii Aurora? Napíšte nám alebo zavolajte — dohodneme si osobnú obhliadku aj online konzultáciu.",
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
            <select id="c-rooms" name="rooms">
              <option value="">Nezáleží</option><option>1-izbový</option><option>2-izbový</option>
              <option>3-izbový</option><option>4-izbový</option><option>Penthouse</option>
            </select></div>
          <div><label for="c-budget">Orientačný rozpočet</label>
            <select id="c-budget" name="budget">
              <option value="">Neuvedené</option><option>do 200 000 €</option><option>200 – 300 000 €</option>
              <option>300 – 450 000 €</option><option>450 – 700 000 €</option><option>nad 700 000 €</option>
            </select></div>
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
            <div><dt>Predaj bytov</dt><dd><a href="tel:+421900000000">+421 900 000 000</a></dd></div>
            <div><dt>E-mail</dt><dd><a href="mailto:info@rezidencia-aurora.sk">info@rezidencia-aurora.sk</a></dd></div>
            <div><dt>Adresa projektu</dt><dd>Placeholder 12<br>811 01 Bratislava — Staré Mesto</dd></div>
            <div><dt>Otváracie hodiny</dt><dd>Pondelok – piatok<br>9:00 – 18:00</dd></div>
          </dl>
        </div>
        <div class="aside__box">
          <p class="eyebrow" style="margin-bottom:10px">Osobná obhliadka</p>
          <p style="font-size:.94rem;color:var(--text-muted);margin:0">
            Radi vám ukážeme projekt osobne — vrátane vzorových materiálov a presných dispozícií.
            Stretnutie si dohodneme telefonicky.
          </p>
        </div>
      </aside>
    </div>
  </div>
</section>
</main>
''' + FOOT + '''<script>
/* prefill the unit field when arriving from an apartment detail page */
document.addEventListener('DOMContentLoaded', function () {
  var byt = new URLSearchParams(location.search).get('byt');
  var el = document.getElementById('c-unit');
  if (byt && el) {
    el.value = byt;
    var msg = document.getElementById('c-msg');
    if (msg && !msg.value) msg.value = 'Mám záujem o byt ' + byt + '. Prosím o viac informácií.';
  }
});
</script>
''' + scripts())

# =============================================================================

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="8" fill="#14120F"/>
  <g fill="#C4AB89">
    <rect x="16" y="20" width="8" height="8"/><rect x="28" y="20" width="8" height="8"/><rect x="40" y="20" width="8" height="8"/>
    <rect x="16" y="32" width="8" height="8"/><rect x="28" y="32" width="8" height="8" opacity=".45"/><rect x="40" y="32" width="8" height="8"/>
    <rect x="16" y="44" width="8" height="8" opacity=".45"/><rect x="28" y="44" width="8" height="8"/><rect x="40" y="44" width="8" height="8"/>
  </g>
</svg>
'''

ROBOTS = ("User-agent: *\nDisallow: /\n" if PREVIEW else
          f"User-agent: *\nAllow: /\nDisallow: /byt.html\n\nSitemap: {SITE}/sitemap.xml\n")

SITEMAP = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f'  <url><loc>{SITE}/{p}</loc><priority>{pr}</priority></url>\n'
              for p, pr in [("", "1.0"), ("byty.html", "0.9"), ("projekt.html", "0.8"),
                            ("lokalita.html", "0.7"), ("galeria.html", "0.6"), ("kontakt.html", "0.7")])
    + '</urlset>\n')

files = {
 "index.html": index_html(),
 "byty.html": byty_html(),
 "byt.html": byt_html(),
 "projekt.html": projekt_html(),
 "lokalita.html": lokalita_html(),
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
