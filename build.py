#!/usr/bin/env python3
"""Static site builder: shared header/footer/head + page content -> .html, sitemap, robots, link check.
Run: python3 build.py   (edit CONFIG and page content here; never edit generated .html directly)"""
import re, json, pathlib, sys
ROOT = pathlib.Path(__file__).parent
CONFIG = dict(
    brand="Aurelia Verde", url="https://www.example.com", email="hello@example.com",
    phone="+91 00000 00000", address="Studio address, City, Country", hours="Mon to Sat, 10am to 6pm",
    ga_id="",            # GA4 id like G-XXXXXXX (public, not a secret). Loads only after cookie consent.
    form_endpoint="",    # e.g. Formspree/Web3Forms URL. Empty = falls back to opening the visitor's email app.
    social=dict(Instagram="https://www.instagram.com/", Pinterest="https://www.pinterest.com/", LinkedIn="https://www.linkedin.com/"),
)
B = CONFIG["brand"]
NAV = [("index.html","Home"),("about.html","About Us"),("collections.html","Collections"),("contact.html","Contact Us"),("faqs.html","FAQs")]
CTA = ("contact.html", "Enquire now")   # the ONE primary action used sitewide

def img(name, alt, ratio, w, h, cls=""):
    return (f'<figure class="ph {ratio} {cls}" data-label="Replace: assets/img/{name} ({w}x{h})">'
            f'<img src="assets/img/{name}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>')
def cta(label=None): return f'<a class="btn" href="{CTA[0]}">{label or CTA[1]}</a>'
def link(href, text): return f'<a class="tlink" href="{href}">{text}</a>'

def page(file, title, desc, body, noindex=False, first_img=""):
    nav = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if h==file else ""}>{t}</a></li>' for h,t in NAV)
    foot = "".join(f'<li><a href="{h}">{t}</a></li>' for h,t in NAV)
    soc = "".join(f'<li><a href="{u}" rel="noopener" target="_blank">{n}</a></li>' for n,u in CONFIG["social"].items())
    full = f"{title} | {B}"
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title><meta name="description" content="{desc}">
<meta name="theme-color" content="#0A4F3A">
<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{CONFIG["url"]}/{file}">'}
<meta property="og:type" content="website"><meta property="og:site_name" content="{B}"><meta property="og:title" content="{full}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{CONFIG["url"]}/{file}">
<meta property="og:image" content="{CONFIG["url"]}/assets/img/og-image.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/Panchang-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/Author-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/styles.css">
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="hdr"><div class="wrap hdr-in">
<a class="logo" href="index.html" aria-label="{B} home">{B}</a>
<button class="burger" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span></span><span></span></button>
<nav id="nav" class="nav" aria-label="Main"><ul>{nav}</ul>{cta("Enquire")}</nav>
</div></header>
<main id="main">{body}</main>
<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div><p class="logo">{B}</p><p class="muted">Handmade objects for the table, the hearth and the desk, made slowly and made to last.</p></div>
<div><h2>Explore</h2><ul>{foot}</ul></div>
<div><h2>Contact</h2><ul><li><a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a></li><li>{CONFIG["phone"]}</li><li>{CONFIG["address"]}</li></ul></div>
<div><h2>Follow</h2><ul>{soc}</ul></div></div>
<div class="ftr-base"><p>&copy; <span data-year>2026</span> {B}. All rights reserved.</p>
<ul><li><a href="privacy.html">Privacy policy</a></li><li><a href="terms.html">Terms &amp; conditions</a></li></ul></div>
</div></footer>
<div class="cookie" role="dialog" aria-label="Cookie consent" hidden><p>We use cookies for anonymous analytics only if you agree. See our <a href="privacy.html">privacy policy</a>.</p>
<div><button class="btn btn-sm" data-consent="yes">Accept</button><button class="btn btn-sm btn-ghost" data-consent="no">Decline</button></div></div>
<script>window.SITE={json.dumps(dict(gaId=CONFIG["ga_id"],endpoint=CONFIG["form_endpoint"],email=CONFIG["email"]))};</script>
<script src="js/main.js" defer></script>
</body></html>'''

COLL = [
 ("table","The Table","Stoneware, linen and brass for meals worth lingering over.",[("Stoneware dinner set","Hand-thrown, glazed in deep green."),("Linen table runner","Stonewashed, naturally dyed."),("Brass serving spoons","Cast, then hand-polished.")]),
 ("hearth","The Hearth","Warmth for slower evenings: wool, wax and clay.",[("Beeswax candle trio","Poured in small batches."),("Wool throw","Woven on heritage looms."),("Ceramic vessel","One of a kind, never repeated.")]),
 ("study","The Study","Quiet, tactile tools for thinking and writing.",[("Leather desk mat","Vegetable-tanned, ages beautifully."),("Walnut pen tray","Joined by hand, oiled not lacquered."),("Bound notebook","Sewn spine, cotton paper.")]),
]
def card(c, i, n, d):
    return (f'<article class="card" data-cat="{c}">{img(f"{c}-{i+1}.jpg", f"{n}, from the {c} collection", "r45", 800, 1000)}'
            f'<h3>{n}</h3><p>{d}</p></article>')

pages = {}
# HOME
pages["index.html"] = ("Handmade objects for considered living", f"{B} makes handcrafted homeware in small batches. Discover collections for the table, the hearth and the study.", f'''
<section class="hero"><div class="wrap hero-in">
<div class="hero-copy"><h1>Objects made slowly, kept for life.</h1>
<p class="lead">{B} is a small studio making stoneware, linen, wool and brass for homes that value craft over volume.</p>
<div class="actions">{cta()}{link("collections.html","See the collections")}</div></div>
<figure class="ph arch hero-img"><video autoplay muted loop playsinline preload="auto" poster="assets/img/hero.jpg" width="1200" height="1500" aria-label="A styled table setting with green stoneware and brass"><source src="assets/video/hero.webm" type="video/webm"><source src="assets/video/hero.mp4" type="video/mp4"></video></figure>
</div></section>
<section class="sec cream"><div class="wrap split">
<h2>A studio, not a factory.</h2>
<div><p>Every piece begins with a sketch and ends in the hands of a maker we know by name. We work in runs of dozens, not thousands, so each object carries the small variations that prove it was made, not manufactured.</p>{link("about.html","Read our story")}</div></div></section>
<section class="sec cream tight"><div class="wrap"><h2>Featured collections</h2><div class="grid3">'''
+ "".join(f'<a class="fcard" href="collections.html#{c}">{img(f"collection-{c}.jpg", f"{n} collection", "arch", 800, 1000)}<h3>{n}</h3><p>{d}</p></a>' for c,n,d,_ in COLL) +
f'''</div></div></section>
<section class="sec deep"><div class="wrap"><h2>Why choose us</h2><div class="grid3 why">
<div><h3>Made by named hands</h3><p>Each maker signs their work, and you can ask who made yours.</p></div>
<div><h3>Materials with provenance</h3><p>Local clay, European linen, responsibly sourced wool and solid brass.</p></div>
<div><h3>Repairable by design</h3><p>We mend what we make, so a chip or a fray is never the end.</p></div></div></div></section>
<section class="sec cream"><div class="wrap"><h2>Highlighted pieces</h2><div class="grid4">'''
+ "".join(card(c,0,p[0][0],p[0][1]) for c,_,_,p in COLL) + card("table",1,COLL[0][3][1][0],COLL[0][3][1][1]) +
f'''</div></div></section>
<section class="sec beige"><div class="wrap narrow center"><p class="quote">Own less, choose well, and let things grow old with you.</p><p>Our philosophy is simple: fewer objects, made better, used daily.</p></div></section>
<section class="sec emerald center"><div class="wrap narrow"><h2>Furnish a room worth coming home to.</h2><p class="lead">Tell us what you are looking for and we will reply within two working days.</p>{cta()}</div></section>''')

# ABOUT
pages["about.html"] = ("About Us", f"The story, philosophy and craft behind {B}, a small studio making handcrafted homeware.", f'''
<section class="sec emerald pagehead"><div class="wrap"><h1>Made by hand, in the open.</h1><p class="lead">{B} began at a single kiln and a borrowed workbench. It has grown, but not by much, on purpose.</p></div></section>
<section class="sec cream"><div class="wrap split"><div><h2>Our story</h2><p>We started with a simple frustration: homes full of objects nobody loved and nobody could repair. So we set out to make fewer, better things with people we could look in the eye.</p><p>Today the studio is a small team of ceramicists, weavers and metalworkers who still sign their work.</p></div>{img("story.jpg","Craftspeople working in the studio","r45",900,1125)}</div></section>
<section class="sec deep"><div class="wrap grid2"><div><h2>Philosophy</h2><p>Slow production, honest materials and a finish that improves with use.</p></div><div><h2>Vision</h2><p>A home in which every object has a story you can tell, and a maker you can name.</p></div></div></section>
<section class="sec cream"><div class="wrap"><h2>The craft</h2><ol class="steps"><li><h3>Sketch</h3><p>Forms are drawn and tested in clay or wood before anything is committed.</p></li><li><h3>Make</h3><p>Pieces are thrown, woven or cast in small runs by one maker from start to finish.</p></li><li><h3>Finish</h3><p>Glazes are fired, wool washed, brass polished, each by hand.</p></li><li><h3>Inspect</h3><p>Anything that falls short of our standard stays in the studio.</p></li></ol></div></section>
<section class="sec beige"><div class="wrap"><h2>What we value</h2><div class="grid3"><div><h3>Care</h3><p>For materials, makers and the people who use what we make.</p></div><div><h3>Longevity</h3><p>Objects should outlast trends and be repairable.</p></div><div><h3>Honesty</h3><p>Clear about where things come from and what they cost to make.</p></div></div></div></section>
<section class="sec emerald center"><div class="wrap narrow"><h2>Talk to the people who make it.</h2>{cta()}</div></section>''')

# COLLECTIONS
det = "".join(f'''<section class="sec {"cream" if i%2==0 else "beige"} coll" id="{c}"><div class="wrap split {"rev" if i%2 else ""}">{img(f"detail-{c}.jpg", f"Pieces from {n}", "r45", 900, 1125)}<div><h2>{n}</h2><p>{d}</p><ul class="plist">{"".join(f"<li><strong>{a}</strong> {b}</li>" for a,b in p)}</ul>{link("contact.html","Ask about this collection")}</div></div></section>''' for i,(c,n,d,p) in enumerate(COLL))
allcards = "".join(card(c,i,a,b) for c,n,d,p in COLL for i,(a,b) in enumerate(p))
pages["collections.html"] = ("Collections", f"Browse {B} collections for the table, the hearth and the study, all handmade in small batches.", f'''
<section class="sec emerald pagehead"><div class="wrap"><h1>Collections</h1><p class="lead">Three collections, each built around a room and the way it is lived in.</p></div></section>
<section class="sec cream"><div class="wrap"><div class="filters" role="group" aria-label="Filter by collection"><button class="chip on" data-filter="all" aria-pressed="true">All</button>'''
+ "".join(f'<button class="chip" data-filter="{c}" aria-pressed="false">{n}</button>' for c,n,_,_ in COLL) +
f'</div><div class="grid3 products">{allcards}</div></div></section>{det}'
f'<section class="sec emerald center"><div class="wrap narrow"><h2>Found something you like?</h2><p class="lead">We can share availability, materials and lead times.</p>{cta()}</div></section>')

# CONTACT
pages["contact.html"] = ("Contact Us", f"Get in touch with {B} about collections, commissions or trade enquiries.", f'''
<section class="sec emerald pagehead"><div class="wrap"><h1>Let&rsquo;s talk.</h1><p class="lead">Questions about a piece, a commission or trade orders. We reply within two working days.</p></div></section>
<section class="sec cream"><div class="wrap split contact">
<div><h2>Studio</h2><ul class="info"><li><strong>Email</strong> <a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a></li><li><strong>Phone</strong> {CONFIG["phone"]}</li><li><strong>Visit</strong> {CONFIG["address"]}</li><li><strong>Hours</strong> {CONFIG["hours"]}</li></ul>
<ul class="info">{"".join(f'<li><a href="{u}" rel="noopener" target="_blank">{n}</a></li>' for n,u in CONFIG["social"].items())}</ul></div>
<form class="form" novalidate aria-describedby="fstatus">
<div class="field"><label for="name">Name</label><input id="name" name="name" autocomplete="name" required minlength="2"><span class="err" aria-live="polite"></span></div>
<div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required><span class="err" aria-live="polite"></span></div>
<div class="field"><label for="phone">Phone <span class="opt">(optional)</span></label><input id="phone" name="phone" type="tel" autocomplete="tel" pattern="[0-9+()\\-\\s]{{7,18}}"><span class="err" aria-live="polite"></span></div>
<div class="field"><label for="message">Message</label><textarea id="message" name="message" rows="5" required minlength="10"></textarea><span class="err" aria-live="polite"></span></div>
<div class="hp" aria-hidden="true"><label>Leave empty<input name="company" tabindex="-1" autocomplete="off"></label></div>
<button class="btn" type="submit">Send message</button><p id="fstatus" class="status" role="status"></p></form></div></section>''')

# FAQ
faqs = [("How long does an order take?","Most pieces are made to order and ship within three to five weeks. We confirm the exact time when you enquire."),
("Do you ship internationally?","Yes. Ceramics and glass are packed in recycled, protective materials, and we share shipping costs before you commit."),
("Can I request a custom piece?","Yes. Send us a note about size, colour and use, and we will let you know what is possible."),
("How should I care for my pieces?","Each piece ships with care instructions. In general, wash gently, dry fully and avoid harsh chemicals."),
("What if something arrives damaged?","Tell us within seven days with a photo and we will repair or replace it."),
("Do you offer trade pricing?","We work with designers, hotels and retailers. Use the enquiry form and mention trade.")]
pages["faqs.html"] = ("FAQs", f"Answers about ordering, shipping, custom work and care from {B}.", f'''
<section class="sec emerald pagehead"><div class="wrap"><h1>Questions, answered.</h1></div></section>
<section class="sec cream"><div class="wrap narrow"><div class="acc">'''
+ "".join(f'<div class="acc-item"><h2><button aria-expanded="false" aria-controls="p{i}" id="b{i}">{q}<span class="pm" aria-hidden="true"></span></button></h2><div class="acc-panel" id="p{i}" role="region" aria-labelledby="b{i}"><div><p>{a}</p></div></div></div>' for i,(q,a) in enumerate(faqs)) +
f'</div><p class="after">Still unsure? {link("contact.html","Ask us directly")}.</p></div></section>')

# LEGAL + 404
def legal(h, secs): return f'<section class="sec emerald pagehead"><div class="wrap"><h1>{h}</h1><p class="muted">Last updated: September 2026</p></div></section><section class="sec cream"><div class="wrap narrow legal">' + "".join(f"<h2>{a}</h2><p>{b}</p>" for a,b in secs) + "</div></section>"
pages["privacy.html"] = ("Privacy policy", f"How {B} collects, uses and protects your personal information.", legal("Privacy policy",[
("What we collect","Details you send through our contact form (name, email, phone, message). If you accept cookies, anonymous usage data through analytics."),
("How we use it","To reply to your enquiry and to improve the website. We do not sell your data."),
("Cookies","Analytics cookies are set only after you accept. You can decline or clear cookies at any time."),
("Your rights","You can ask us to access, correct or delete your data at "+CONFIG["email"]+"."),
("Contact",f"Questions about this policy? Email {CONFIG['email']}.")]))
pages["terms.html"] = ("Terms & conditions", f"Terms governing use of the {B} website and orders.", legal("Terms &amp; conditions",[
("Use of this site","Content is provided for information and belongs to "+B+". Please do not copy it without permission."),
("Orders and pricing","Enquiries are not binding until we confirm an order and price in writing."),
("Handmade goods","Each piece is handmade, so slight variation in colour, size and finish is expected."),
("Returns and repairs","Report damage within seven days of delivery. We repair or replace damaged items."),
("Liability","Our liability is limited to the value of the order, to the extent permitted by law.")]))
pages["404.html"] = ("Page not found", "The page you are looking for does not exist.", f'<section class="sec emerald center pagehead full"><div class="wrap narrow"><h1>This page has gone missing.</h1><p class="lead">The link may be old or mistyped. Head back to the start.</p>{cta("Back to home").replace(CTA[0],"index.html")}</div></section>')

def main():
    for f,(t,d,b) in pages.items():
        (ROOT/f).write_text(page(f,t,d,b,noindex=(f=="404.html")), encoding="utf-8")
    urls = [f for f in pages if f!="404.html"]
    (ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f'<url><loc>{CONFIG["url"]}/{u}</loc></url>\n' for u in urls)+'</urlset>\n')
    (ROOT/"robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {CONFIG["url"]}/sitemap.xml\n')
    bad = 0
    for f in pages:
        html = (ROOT/f).read_text(encoding="utf-8")
        for h in re.findall(r'(?:href|src)="([^"]+)"', html):
            if re.match(r'(https?:|mailto:|#)', h): continue
            p, _, a = h.partition("#")
            if p and not (ROOT/p).exists() and not p.startswith("assets/"): print("BROKEN", f, h); bad += 1
            if a and p and a not in (ROOT/p).read_text(encoding="utf-8"): print("BAD ANCHOR", f, h); bad += 1
    print("built", len(pages), "pages;", "broken links:", bad); sys.exit(bad>0)
main()
