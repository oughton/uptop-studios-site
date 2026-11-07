#!/usr/bin/env python3
"""Static site builder for Up Top Studios.

    python3 build.py            -> preview build into docs/ (noindex, for GitHub Pages)
    python3 build.py --prod     -> production build into dist/ (indexable)

Page bodies live in src/pages/*.html. Shortcodes:
    {{root}}                                   relative path to site root
    <pic name="x" alt="..." sizes="..." eager> responsive <img> from assets/img/x-{800,1600,2400}.webp
    <gal name="x" alt="..." class="wide">      gallery tile that opens the lightbox
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = "--prod" in sys.argv
OUT = os.path.join(HERE, "dist" if PROD else "docs")
SITE_URL = "https://www.uptopstudios.co.uk"
EMAIL = "dan@uptopstudios.co.uk"
INSTAGRAM = "https://www.instagram.com/up_top_studio/"
IMG_DIR = os.path.join(HERE, "src", "assets", "img")

NAV = [
    ("podcast-studio/", "Podcasts"),
    ("corporate-video/", "Corporate video"),
    ("recording/", "Music"),
    ("studio-hire/", "Studio hire"),
    ("the-studio/", "The studio"),
    ("pricing/", "Pricing"),
]

BUSINESS = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": SITE_URL + "/#business",
    "name": "Up Top Studios",
    "description": "Video podcast, corporate video and music recording studio near St Albans, Hertfordshire, around 25 minutes from central London.",
    "url": SITE_URL + "/",
    "email": EMAIL,
    "image": SITE_URL + "/assets/img/og-image.jpg",
    "logo": SITE_URL + "/assets/img/uptop-logo.png",
    "priceRange": "££",
    "address": {"@type": "PostalAddress", "addressLocality": "St Albans", "addressRegion": "Hertfordshire", "addressCountry": "GB"},
    "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in ["Hertfordshire", "London", "Bedfordshire", "Buckinghamshire"]],
    "sameAs": [INSTAGRAM],
    "knowsAbout": ["Video podcast production", "Corporate video", "Talking head video", "Music recording", "Mixing", "Studio hire", "Photography"],
}

PAGES = [
    dict(slug="", file="home", title="Podcast & Video Studio near St Albans, Herts | Up Top Studios",
         desc="Professional video podcast, corporate video and recording studio near St Albans, Hertfordshire. Multi-camera production 25 minutes from London. Trusted by ITV and Apple.",
         schema=["business", "faq"]),
    dict(slug="podcast-studio/", file="podcast", title="Video Podcast Studio Hertfordshire | St Albans | Up Top Studios",
         desc="Multi-camera video podcast studio near St Albans, Herts. Engineer, lighting, broadcast-quality audio and fast edits included. Half-day and full-day packages.",
         crumb="Video podcast studio", service="Video podcast production", schema=["faq"]),
    dict(slug="corporate-video/", file="corporate", title="Corporate Video & Talking Head Studio Hertfordshire | Up Top Studios",
         desc="Talking head, interview and branded content filming in a private, naturally lit studio near St Albans. Fully crewed or dry hire. 25 min from London.",
         crumb="Corporate video", service="Corporate video production", schema=["faq"]),
    dict(slug="recording/", file="recording", title="Recording Studio St Albans, Hertfordshire | Up Top Studios",
         desc="Professional recording, mixing and production studio near St Albans. Two live rooms, vintage Yamaha PM1000 console, UAD Apollo, classic mics, amps and synths.",
         crumb="Music recording", service="Music recording and mixing", schema=[]),
    dict(slug="studio-hire/", file="hire", title="Studio Hire St Albans | Photo, Film & Dry Hire Hertfordshire | Up Top Studios",
         desc="Hire a versatile, naturally lit studio near St Albans for photography, filming, podcasts and rehearsals. Dry hire from competitive hourly and day rates.",
         crumb="Studio hire", service="Studio hire", schema=["faq"]),
    dict(slug="the-studio/", file="studio", title="The Studio: Spaces, Kit & Getting Here | Up Top Studios",
         desc="Tour Up Top Studios: podcast sets, two live rooms, control room and full equipment list. Easy train links from St Albans, Harpenden and Hemel Hempstead.",
         crumb="The studio", schema=[]),
    dict(slug="pricing/", file="pricing", title="Studio Prices & Packages | Podcast, Video & Recording | Up Top Studios",
         desc="Transparent pricing for video podcasts, corporate filming, music recording and dry hire near St Albans, Hertfordshire. Half-day and full-day packages.",
         crumb="Pricing", schema=["faq"]),
    dict(slug="contact/", file="contact", title="Contact & Book | Up Top Studios, St Albans, Hertfordshire",
         desc="Tell us about your podcast, video or recording project. We reply within one working day. Studio viewings welcome.",
         crumb="Contact", schema=[]),
]


def rel_root(slug):
    depth = slug.count("/")
    return "../" * depth if depth else "./"


def srcset(name):
    widths = [w for w in (800, 1600, 2400) if os.path.exists(os.path.join(IMG_DIR, f"{name}-{w}.webp"))]
    if not widths:
        raise SystemExit(f"missing image: {name}")
    return widths


def pic(m, root):
    a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    eager = re.search(r"\beager\b", m.group(1))
    widths = srcset(a["name"])
    ss = ", ".join(f"{root}assets/img/{a['name']}-{w}.webp {w}w" for w in widths)
    mid = 1600 if 1600 in widths else widths[-1]
    attrs = 'fetchpriority="high"' if eager else 'loading="lazy"'
    cls = f' class="{a["class"]}"' if "class" in a else ""
    style = f' style="object-position:{a["pos"]}"' if "pos" in a else ""
    return (f'<img src="{root}assets/img/{a["name"]}-{mid}.webp" srcset="{ss}" '
            f'sizes="{a.get("sizes", "(min-width: 900px) 50vw, 100vw")}" alt="{a["alt"]}" {attrs} decoding="async"{cls}{style}>')


def gal(m, root):
    a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    widths = srcset(a["name"])
    full = f"{root}assets/img/{a['name']}-{1600 if 1600 in widths else widths[-1]}.webp"
    cls = f' class="{a["class"]}"' if "class" in a else ""
    return (f'<button type="button"{cls} data-full="{full}" aria-label="View larger: {a["alt"]}">'
            f'<img src="{root}assets/img/{a["name"]}-800.webp" alt="{a["alt"]}" loading="lazy" decoding="async"></button>')


def faq_schema(body):
    qs = re.findall(r"<summary>(.*?)</summary>\s*<div>(.*?)</div>", body, re.S)
    strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip(q),
                            "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qs]}


def layout(p, body):
    root = rel_root(p["slug"])
    canonical = SITE_URL + "/" + p["slug"]
    nav = "".join(
        f'<li><a href="{root}{href}"{" aria-current=\"page\"" if href == p["slug"] else ""}>{label}</a></li>'
        for href, label in NAV)
    schemas = []
    if "business" in p["schema"]:
        schemas.append(BUSINESS)
    if "faq" in p["schema"]:
        schemas.append(faq_schema(body))
    if p.get("crumb"):
        schemas.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": p["crumb"], "item": canonical}]})
    if p.get("service"):
        schemas.append({"@context": "https://schema.org", "@type": "Service", "serviceType": p["service"],
                        "name": p["service"] + " near St Albans, Hertfordshire",
                        "provider": {"@id": SITE_URL + "/#business"},
                        "areaServed": ["Hertfordshire", "London"], "url": canonical})
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    robots = "index, follow" if PROD else "noindex, nofollow"

    return f"""<!doctype html>
<html lang="en-GB" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{p['title']}</title>
<meta name="description" content="{p['desc']}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#faf8f4">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Up Top Studios">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{p['title']}">
<meta property="og:description" content="{p['desc']}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700&display=swap">
<link rel="stylesheet" href="{root}assets/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{root}" aria-label="Up Top Studios home"><img src="{root}assets/img/uptop-logo.png" alt="Up Top Studios" width="560" height="120"></a>
    <nav aria-label="Main"><ul class="nav-links">{nav}</ul></nav>
    <a class="btn btn-primary nav-cta" href="{root}contact/">Check availability</a>
    <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="mobile-menu"><span></span></button>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu">
  <ul>{nav}<li><a href="{root}contact/">Contact</a></li></ul>
  <a class="btn btn-primary" href="{root}contact/">Check availability</a>
  <p class="muted" style="margin-top:20px">Or email <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</div>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{root}assets/img/uptop-logo.png" alt="Up Top Studios" width="560" height="120" loading="lazy">
        <p>A podcast, video and recording studio set in the Hertfordshire countryside near St Albans. About 25 minutes from central London.</p>
      </div>
      <div><h4>Services</h4><ul>
        <li><a href="{root}podcast-studio/">Video podcasts</a></li>
        <li><a href="{root}corporate-video/">Corporate &amp; talking head</a></li>
        <li><a href="{root}recording/">Music recording &amp; mixing</a></li>
        <li><a href="{root}studio-hire/">Photo, film &amp; dry hire</a></li></ul></div>
      <div><h4>Studio</h4><ul>
        <li><a href="{root}the-studio/">Spaces &amp; kit</a></li>
        <li><a href="{root}the-studio/#getting-here">Getting here</a></li>
        <li><a href="{root}pricing/">Pricing</a></li>
        <li><a href="{root}contact/">Contact</a></li></ul></div>
      <div><h4>Get in touch</h4><ul>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><a href="{INSTAGRAM}" rel="noopener" target="_blank">Instagram</a></li>
        <li>St Albans, Hertfordshire</li></ul></div>
    </div>
    <div class="footer-base"><span>© <span id="yr">2026</span> Up Top Studios</span><span>Podcast studio · Video studio · Recording studio · Hertfordshire</span></div>
  </div>
</footer>
<div class="sticky-cta"><a class="btn btn-primary" href="{root}contact/">Check availability</a><a class="btn btn-dark" href="{root}pricing/">Prices</a></div>
<script src="{root}assets/js/site.js" defer></script>
</body>
</html>
"""


def main():
    if os.path.exists(OUT):
        for entry in os.listdir(OUT):
            if entry == "CNAME":
                continue
            path = os.path.join(OUT, entry)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    shutil.copytree(os.path.join(HERE, "src", "assets"), os.path.join(OUT, "assets"), dirs_exist_ok=True)
    for p in PAGES:
        root = rel_root(p["slug"])
        body = open(os.path.join(HERE, "src", "pages", p["file"] + ".html"), encoding="utf-8").read()
        body = body.replace("{{root}}", root).replace("{{email}}", EMAIL)
        body = re.sub(r"<pic\s+([^>]*)>", lambda m: pic(m, root), body)
        body = re.sub(r"<gal\s+([^>]*)>", lambda m: gal(m, root), body)
        d = os.path.join(OUT, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(layout(p, body))
    # 404
    nf = dict(slug="", title="Page not found | Up Top Studios", desc="Page not found.", schema=[])
    body = ('<section class="section"><div class="wrap center"><h1>Page not found</h1>'
            '<p class="lead">That page has moved or no longer exists.</p>'
            '<a class="btn btn-primary" href="/">Back to home</a></div></section>')
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(layout(nf, body))
    # sitemap + robots
    urls = "".join(f"<url><loc>{SITE_URL}/{p['slug']}</loc></url>" for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n" if PROD else "User-agent: *\nDisallow: /\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"built {len(PAGES)} pages -> {OUT} ({'production' if PROD else 'preview, noindex'})")


if __name__ == "__main__":
    main()
