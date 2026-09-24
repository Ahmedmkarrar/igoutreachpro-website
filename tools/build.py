#!/usr/bin/env python3
"""Generate the site's derived pages from data/niches.json.

Run from the repo root:  python3 tools/build.py

Writes:
  assets/js/niches.js                       template data for landing.js
  index.html                                nav / footer / playground blocks between @@ markers
  instagram-dm-templates/index.html         templates hub
  instagram-dm-templates/<slug>.html        one SEO page per niche
  support.html privacy.html terms.html      re-wrapped in the current nav/footer (body copy untouched)
  404.html
  sitemap.xml

Everything is plain static HTML; there is no runtime build step on Vercel.
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.igoutreachpro.com"
CWS = "https://chromewebstore.google.com/detail/ig-outreach-pro/iabflpjdaaaljedkocccimhfjonakcon"
TODAY = datetime.date.today().isoformat()
NICHES = json.loads((ROOT / "data/niches.json").read_text())
HUB = "instagram-dm-templates"

SPIN_RE = re.compile(r"\{([^{}]*\|[^{}]*)\}")
PH_RE = re.compile(r"\{(firstname|fullname|username)\}", re.I)


def esc(t):
    return html.escape(t, quote=True)


def count_variants(text):
    s, total = PH_RE.sub("", text), 1
    while (m := SPIN_RE.search(s)):
        total *= len(m.group(1).split("|"))
        s = s[: m.start()] + "x" + s[m.end():]
    return total


def highlight(text):
    t = esc(text)
    t = re.sub(r"\{(firstname|fullname|username)\}", r'<span class="p">{\1}</span>', t, flags=re.I)
    return re.sub(r"\{([^{}]*\|[^{}]*)\}", r'<span class="s">{\1}</span>', t)


def sprite():
    src = (ROOT / "index.html").read_text()
    return re.search(r'<svg width="0" height="0".*?</svg>', src, re.S).group(0)


# --------------------------------------------------------------------------- shared blocks
def nav(p):
    """p is the link prefix: '' on the home page, '/' everywhere else."""
    return f'''<header class="nav" id="nav">
  <div class="nav-inner">
    <a class="brand" href="{p or '#top'}" aria-label="IG Outreach Pro — home">
      <img src="{p}assets/img/icon-128.png" alt="" width="28" height="28">
      <span class="wm">IG Outreach<b>PRO</b></span>
    </a>
    <nav class="nav-links" id="navLinks" aria-label="Main">
      <a href="{p}#features">Features<sup>01</sup></a>
      <a href="{p}#how">How it works<sup>02</sup></a>
      <a href="{p}#customers">Customers<sup>03</sup></a>
      <a href="{p}#pricing">Pricing<sup>04</sup></a>
      <a href="/{HUB}">Templates<sup>05</sup></a>
      <a class="nav-mobile-only" href="/support">Support</a>
    </nav>
    <div class="nav-actions">
      <a class="btn-ghost-sm brk" href="/support">Support</a>
      <a class="btn-arrow brk" href="{CWS}" target="_blank" rel="noopener">
        <span class="sq"><svg><use href="#i-arrow"/></svg></span><span class="lbl">Start for free</span>
      </a>
      <button class="nav-burger" id="burger" aria-label="Open menu" aria-expanded="false" aria-controls="navLinks"><svg><use href="#i-menu"/></svg></button>
    </div>
  </div>
</header>'''


def footer(p):
    niche_links = "\n".join(
        f'        <a href="/{HUB}/{n["slug"]}">{esc(n["h1"].replace("Instagram DM templates for ", "For ").replace("Influencer outreach DM templates", "Influencer outreach"))} <span>→</span></a>'
        for n in NICHES.values()
    )
    return f'''<footer class="foot">
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-brand">
        <a class="brand" href="{p or '#top'}"><img src="{p}assets/img/icon-128.png" alt="" width="28" height="28"><span class="wm">IG Outreach<b>PRO</b></span></a>
        <p class="foot-tag">Your Instagram setter.</p>
        <a class="yt-link" href="https://www.youtube.com/@Igoutreach_pro" target="_blank" rel="noopener"><svg><use href="#i-play"/></svg>Watch on YouTube</a>
      </div>
      <div class="foot-col">
        <h4>Product</h4>
        <a href="{p}#features">Features <span>→</span></a>
        <a href="{p}#how">How it works <span>→</span></a>
        <a href="{p}#savings">Savings calculator <span>→</span></a>
        <a href="{p}#pricing">Pricing <span>→</span></a>
        <a href="{p}#customers">Customer videos <span>→</span></a>
      </div>
      <div class="foot-col">
        <h4>Free DM templates</h4>
        <a href="/{HUB}">All templates <span>→</span></a>
{niche_links}
      </div>
      <div class="foot-col">
        <h4>Information</h4>
        <a href="{p}#faq">FAQ <span>→</span></a>
        <a href="/support">Support <span>→</span></a>
        <a href="/terms">Terms <span>→</span></a>
        <a href="/privacy">Privacy Policy <span>→</span></a>
        <a href="mailto:highpointscaling@gmail.com">Contact <span>→</span></a>
      </div>
    </div>
    <div class="foot-base">
      <p>© <span id="yr">2026</span> IG Outreach Pro · A Highpoint Scaling product</p>
      <p class="disclaimer">IG Outreach Pro is an independent tool and is not affiliated with, endorsed by, or connected to Instagram or Meta Platforms, Inc. Automating direct messages may conflict with Instagram's terms of service; you are responsible for how you use the extension and the volume you configure. Customer results are individual experiences quoted from their video testimonials and are not a guarantee of similar outcomes.</p>
    </div>
  </div>
</footer>'''


PLAY = '''    <div class="play brk rv">
      <div class="play-edit">
        <div class="play-bar">
          <span class="mono">Template</span>
          <div class="play-ins" aria-label="Insert a placeholder">
            <button type="button" data-insert="{firstname}">{firstname}</button>
            <button type="button" data-insert="{username}">{username}</button>
            <button type="button" data-insert="{Hi|Hey|Yo}">{a|b|c}</button>
          </div>
        </div>
        <label class="sr" for="tpl">Message template</label>
        <textarea id="tpl" spellcheck="false" rows="7"></textarea>
        <div class="play-meta">
          <span><b id="varCount">0</b> unique versions of this message</span>
          <button type="button" class="copy-btn" id="copyTpl">Copy template</button>
        </div>
        <p class="play-hint">Wrap options in <span class="mono">{curly|braces}</span> to spin them. Paste the template straight into IG Outreach Pro; it's the same syntax.</p>
      </div>

      <div class="play-out">
        <div class="phone">
          <div class="phone-top"><span class="phone-notch"></span></div>
          <div class="phone-head"><span class="lr-av" id="pvAv" style="--h:14"></span><div><b id="pvUser">coach.marissa</b><small>Instagram</small></div></div>
          <div class="phone-body" id="pvBody" aria-live="polite"></div>
        </div>
        <button type="button" class="shuffle" id="shuffle"><svg><use href="#i-repeat"/></svg>Shuffle recipients</button>
      </div>
    </div>
'''

TESTIMONIALS = [
    ("4QfbFwU-nrU", 1, "Got rid of two appointment setters", "0:23"),
    ("V023sIzUbjE", 3, "One follower. One day. One lead.", "0:35"),
    ("X1p0nB10GHw", 2, "Hours every day, now done on its own", "0:35"),
    ("KKrw2d9_rZk", 4, "It literally does everything for you", "0:23"),
    ("UbSb2e4Ebhs", 5, "Everything you need is there", "0:25"),
]


def wall(heading="Don't take our word for it. <em>Press play.</em>"):
    tiles = "\n".join(
        f'      <button class="vw" data-video="{vid}" aria-label="Play customer video: {esc(q)}, {d}">'
        f'<img src="/assets/img/testimonial-{n}.jpg" alt="" width="720" height="1280" loading="lazy">'
        f'<video class="vw-loop" muted loop playsinline preload="none" data-src="/assets/video/testimonial-{n}.mp4"></video>'
        f'<span class="vw-live mono">● Customer {i:02d}</span>'
        f'<span class="vw-play"><svg><use href="#i-play"/></svg></span>'
        f'<span class="vw-cap"><b>"{esc(q)}"</b>Watch · {d}</span></button>'
        for i, (vid, n, q, d) in enumerate(TESTIMONIALS, 1))
    return f"""  <div class="wrap vwall-wrap">
    <div class="vwall-head rv">
      <h3>{heading}</h3>
      <div class="vwall-actions">
        <button class="yt-link" type="button" data-video="{TESTIMONIALS[0][0]}"><svg><use href="#i-play"/></svg>Play all 5</button>
        <a class="yt-link" href="https://www.youtube.com/@Igoutreach_pro" target="_blank" rel="noopener">YouTube channel ↗</a>
      </div>
    </div>
    <div class="vwall rv">
{tiles}
    </div>
  </div>"""


MODAL = """<div class="vmodal" id="vmodal" hidden>
  <div class="vm-back" data-close></div>
  <div class="vm-box" role="dialog" aria-modal="true" aria-label="Customer video">
    <div class="vm-bar"><span class="vm-count mono" id="vmCount"></span><button class="vm-x" data-close aria-label="Close video"><svg><use href="#i-x"/></svg></button></div>
    <div class="vm-frame" id="vmFrame"></div>
    <div class="vm-nav"><button type="button" id="vmPrev">← Previous</button><button type="button" id="vmNext">Next customer →</button></div>
  </div>
</div>"""

TAIL = '''<a class="mcta" id="mcta" href="{cws}" target="_blank" rel="noopener">
  <span><b>IG Outreach Pro</b><small>Free · 10 DMs a day · no card</small></span>
  <span class="mcta-go">Add to Chrome</span>
</a>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
{MODAL}
<script src="/assets/js/niches.js" defer></script>
<script src="/assets/js/landing.js" defer></script>
</body>
</html>
'''.replace("{cws}", CWS).replace("{MODAL}", MODAL)


def head(title, desc, path, ld=None, robots="index,follow"):
    canonical = f"{SITE}/{path}".rstrip("/") if path else f"{SITE}/"
    ld_block = f'\n<script type="application/ld+json">\n{json.dumps(ld, indent=1, ensure_ascii=False)}\n</script>' if ld else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#ffffff">
<meta name="robots" content="{robots}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="IG Outreach Pro">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/assets/img/og.png">
<link rel="icon" href="/assets/img/icon-48.png" sizes="48x48">
<link rel="apple-touch-icon" href="/assets/img/icon-128.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fustat:wght@300..700&family=Inter:wght@400..600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/css/landing.css">{ld_block}
</head>'''


def final_cta(title="Your next 10 clients are already on Instagram.", sub="Let the extension message them."):
    return f'''<section class="final-wrap" id="get-started">
  <div class="final rv">
    <div class="final-bg" aria-hidden="true"><i></i><i></i><i></i></div>
    <h2>{title}</h2>
    <p class="final-sub">{sub}</p>
    <a class="btn-dark lg" href="{CWS}" target="_blank" rel="noopener">Start my outreach for free</a>
    <p class="final-fine mono">Free plan · Live in 5 minutes · Cancel anytime</p>
  </div>
</section>'''


def tpl_card(t, i):
    return (f'<article class="tpl-card brk"><h3>{esc(t["name"])}</h3><p class="when">{esc(t["when"])} · '
            f'{count_variants(t["text"]):,} versions</p><pre>{highlight(t["text"])}</pre>'
            f'<div class="tpl-foot"><button class="tpl-copy" data-i="{i}">Copy</button>'
            f'<button class="tpl-try" data-i="{i}">Edit &amp; preview</button></div></article>')


# --------------------------------------------------------------------------- pages
def niche_page(key, n):
    others = [(k, o) for k, o in NICHES.items() if k != key]
    total = sum(count_variants(t["text"]) for t in n["templates"])
    faqs = [
        ("What is spintax?", "Spintax is a way of writing several versions of a message at once. Options go inside curly braces separated by a pipe, like {Hey|Hi|Hello}, and one is picked at random for each person. Placeholders like {firstname} fill in the recipient's details. IG Outreach Pro uses exactly this syntax."),
        ("Can I use these templates without the extension?", "Yes. Pick one option from each set of braces and replace the placeholders by hand. The extension just does that for you automatically, for every person on your list, and follows up on schedule."),
        ("Will sending DMs get my Instagram account banned?", "Nobody can promise it won't, and automated DMs conflict with Instagram's terms. IG Outreach Pro gives you Test Mode, Safe Start warm-up, an hourly cap, scheduled breaks and automatic opt-outs so you can send carefully. Start slow and read the send log."),
        (f"Are these templates free for {n['audience']}?", "Completely. Copy them, edit them, use them however you like. No signup."),
    ]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "DM templates", "item": f"{SITE}/{HUB}"},
            {"@type": "ListItem", "position": 3, "name": n["title"], "item": f"{SITE}/{HUB}/{n['slug']}"}]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]}
    title = f'{n["title"]} (Copy & Paste) — IG Outreach Pro'
    desc = f'{len(n["templates"])} free Instagram DM templates for {n["audience"]} reaching {n["reach"]}. Copy, customise with spintax, and send them at scale with IG Outreach Pro.'
    h1 = n["h1"]
    cards = "\n      ".join(tpl_card(t, i) for i, t in enumerate(n["templates"]))
    tips = "\n".join(f'''      <li class="tip brk rv"><span class="num-pill"><svg><use href="#i-ticket"/></svg>0{i+1}</span><h3>{esc(a)}</h3><p>{esc(b)}</p></li>''' for i, (a, b) in enumerate(n["tips"]))
    other_cards = "\n".join(f'''      <a class="nlink brk" href="/{HUB}/{o["slug"]}"><span class="mono">{len(o["templates"])} templates</span><b>{esc(o["title"].replace("Instagram ", ""))}</b><span class="nl-go">→</span></a>''' for _, o in others)
    faq_html = "\n".join(f'''      <details>
        <summary>{esc(q)}</summary>
        <div class="ans"><p>{esc(a)}</p></div>
      </details>''' for q, a in faqs)
    return f'''{head(title, desc, f"{HUB}/{n['slug']}", ld)}
<body data-niche="{key}">
{sprite()}
{nav("/")}
<main>
<section class="hero sub" id="top">
  <div class="hero-bg" aria-hidden="true"><i class="blob b1"></i><div class="tiles"></div><div class="fade"></div></div>
  <div class="wrap hero-inner">
    <nav class="crumbs rv" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/{HUB}">DM templates</a><span>/</span><b>{esc(n["crumb"])}</b></nav>
    <h1 class="rv rv-d1">{esc(h1.split(" for ")[0]) if " for " in h1 else esc(h1)}{f' for <em class="ig">{esc(h1.split(" for ")[1])}</em>' if " for " in h1 else ""}</h1>
    <p class="hero-sub rv rv-d2">{esc(n["intro"])}</p>
    <div class="sub-ctas rv rv-d3">
      <a class="btn-dark" href="#templates">Get the templates ↓</a>
      <a class="btn-arrow brk" href="{CWS}" target="_blank" rel="noopener"><span class="sq"><svg><use href="#i-arrow"/></svg></span><span class="lbl">Send them automatically</span></a>
    </div>
    <p class="sub-meta mono rv rv-d4">{len(n["templates"])} templates · {total:,} unique message versions · free, no signup</p>
  </div>
</section>

<section class="sec" id="templates">
  <div class="rule" aria-hidden="true"><span>+</span></div>
  <div class="wrap">
    <header class="sec-head brk rv">
      <h2><i class="dot" aria-hidden="true"></i>{len(n["templates"])} templates, <em>ready to paste.</em></h2>
      <p>Purple is a placeholder the extension fills in. Pink is spintax: one option is picked for each person. Replace anything in [square brackets] with your own details.</p>
    </header>
    <div class="tpl-grid rv" id="tplGrid">
      {cards}
    </div>
  </div>
</section>

<section class="sec" id="try">
  <div class="rule" aria-hidden="true"><span>+</span></div>
  <div class="wrap">
    <header class="sec-head brk rv">
      <h2><i class="dot" aria-hidden="true"></i>Make it yours. <em>See every version.</em></h2>
      <p>Edit any template below and shuffle through recipients to see exactly what each person would receive.</p>
    </header>
{PLAY}  </div>
</section>

<section class="sec" id="tips">
  <div class="rule" aria-hidden="true"><span>+</span></div>
  <div class="wrap">
    <header class="sec-head brk rv">
      <h2><i class="dot" aria-hidden="true"></i>How {esc(n["audience"])} get <em>replies, not blocks.</em></h2>
    </header>
    <ol class="tips">
{tips}
    </ol>
  </div>
</section>

<section class="sec" id="scale">
  <div class="rule" aria-hidden="true"><span>+</span></div>
  <div class="wrap">
    <div class="scale brk rv">
      <div>
        <h2>Send these to hundreds of {esc(n["reach"])}. <em>Without typing one.</em></h2>
        <p>IG Outreach Pro finds {esc(n["reach"])} by hashtag, by the followers of an account or from your own list, spins a different version of your template for each one, sends from your own account at the pace you set, and follows up until they answer.</p>
        <ul class="scale-list">
          <li><svg><use href="#i-check"/></svg>Free plan: 1 campaign, 10 DMs a day, no card</li>
          <li><svg><use href="#i-check"/></svg>Same spintax as these templates, so paste and go</li>
          <li><svg><use href="#i-check"/></svg>Test Mode, hourly caps and breaks built in</li>
        </ul>
        <a class="btn-dark" href="{CWS}" target="_blank" rel="noopener">Add to Chrome for free</a>
      </div>
      <div class="scale-vis" aria-hidden="true">
        <div class="bubble out">{esc(n["templates"][0]["text"].split("}")[0].split("|")[0].lstrip("{"))} {esc(n["people"][0][1].split()[0])}! …</div>
        <div class="bubble in">{esc(n["reply"])}</div>
        <div class="bubble out soft">Follow-up #1 scheduled · if no reply</div>
      </div>
    </div>
  </div>
</section>

<section class="sec" id="customers">
  <div class="rule" aria-hidden="true"><span>+</span></div>
{wall("Five customers, on camera. <em>Press play.</em>")}
</section>

<section class="sec" id="faq">
  <div class="rule" aria-hidden="true"><span>+</span></div>
  <div class="wrap narrow">
    <header class="sec-head brk rv"><h2><i class="dot" aria-hidden="true"></i>Questions</h2></header>
    <div class="faq rv">
{faq_html}
    </div>
  </div>
</section>

<section class="sec" id="more">
  <div class="rule" aria-hidden="true"><span>+</span></div>
  <div class="wrap">
    <header class="sec-head brk rv"><h2><i class="dot" aria-hidden="true"></i>More free DM templates</h2></header>
    <div class="nlinks rv">
{other_cards}
    </div>
  </div>
</section>

{final_cta()}
</main>
{footer("/")}
{TAIL}'''


def hub_page():
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Free Instagram DM templates",
          "url": f"{SITE}/{HUB}", "hasPart": [{"@type": "WebPage", "name": n["title"], "url": f"{SITE}/{HUB}/{n['slug']}"} for n in NICHES.values()]}
    total_t = sum(len(n["templates"]) for n in NICHES.values())
    cards = "\n".join(f'''      <a class="hub-card brk rv" href="/{HUB}/{n["slug"]}">
        <span class="mono">{len(n["templates"])} templates · for {esc(n["audience"])}</span>
        <h3>{esc(n["title"])}</h3>
        <pre>{highlight(n["templates"][0]["text"])}</pre>
        <span class="hub-go">Open templates →</span>
      </a>''' for n in NICHES.values())
    return f'''{head("Free Instagram DM Templates (Copy & Paste) — IG Outreach Pro", f"{total_t} free Instagram DM templates for coaches, agencies, real estate agents, brands and local businesses. Spintax-ready, copy and paste.", HUB, ld)}
<body>
{sprite()}
{nav("/")}
<main>
<section class="hero sub" id="top">
  <div class="hero-bg" aria-hidden="true"><i class="blob b1"></i><div class="tiles"></div><div class="fade"></div></div>
  <div class="wrap hero-inner">
    <nav class="crumbs rv" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><b>DM templates</b></nav>
    <h1 class="rv rv-d1">Free Instagram <em class="ig">DM templates</em></h1>
    <p class="hero-sub rv rv-d2">{total_t} copy-and-paste openers and follow-ups, grouped by who you're reaching. Every one is written in spintax, so each person gets different wording.</p>
  </div>
</section>
<section class="sec">
  <div class="wrap">
    <div class="hub-grid">
{cards}
    </div>
  </div>
</section>
{final_cta("Templates are the easy part.", "Let the extension send them for you.")}
</main>
{footer("/")}
{TAIL}'''


def rewrap_legal(name, title_hint):
    path = ROOT / name
    src = path.read_text()
    headpart = src[: src.index("</head>")]
    title = re.search(r"<title>(.*?)</title>", headpart, re.S).group(1)
    desc = re.search(r'name="description" content="(.*?)"', headpart, re.S).group(1)
    body = re.search(r"<main[^>]*>(.*?)</main>", src, re.S).group(1)
    page = f'''{head(html.unescape(title), html.unescape(desc), name.replace(".html", ""))}
<body>
{sprite()}
{nav("/")}
<main class="doc wrap">
{body.strip()}
</main>
{footer("/")}
{TAIL}'''
    path.write_text(page)


def not_found():
    return f'''{head("Page not found — IG Outreach Pro", "This page doesn't exist.", "404", robots="noindex")}
<body>
{sprite()}
{nav("/")}
<main>
<section class="hero sub nf" id="top">
  <div class="hero-bg" aria-hidden="true"><i class="blob b1"></i><div class="tiles"></div><div class="fade"></div></div>
  <div class="wrap hero-inner">
    <p class="nf-code mono">404 · message not delivered</p>
    <h1>This page left you <em class="ig">on read.</em></h1>
    <p class="hero-sub">The link is broken or the page moved. These ones reply every time:</p>
    <div class="sub-ctas">
      <a class="btn-dark" href="/">Back to the homepage</a>
      <a class="btn-arrow brk" href="/{HUB}"><span class="sq"><svg><use href="#i-arrow"/></svg></span><span class="lbl">Free DM templates</span></a>
    </div>
  </div>
</section>
</main>
{footer("/")}
{TAIL}'''


def sitemap():
    urls = [("", "weekly", "1.0"), (HUB, "weekly", "0.9")]
    urls += [(f"{HUB}/{n['slug']}", "monthly", "0.8") for n in NICHES.values()]
    urls += [("support", "monthly", "0.5"), ("privacy", "yearly", "0.3"), ("terms", "yearly", "0.3")]
    rows = "\n".join(f'''  <url>
    <loc>{SITE}/{u}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{c}</changefreq>
    <priority>{p}</priority>
  </url>''' for u, c, p in urls)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{rows}
</urlset>
'''


def replace_block(src, name, content):
    pat = re.compile(rf"<!-- @@{name} -->.*?<!-- /@@{name} -->", re.S)
    assert pat.search(src), f"marker @@{name} missing"
    return pat.sub(lambda _: f"<!-- @@{name} -->\n{content}\n<!-- /@@{name} -->", src)


def main():
    js_data = {k: {f: v[f] for f in ("label", "slug", "crumb", "targets", "people", "reply", "templates")} for k, v in NICHES.items()}
    (ROOT / "assets/js/niches.js").write_text(
        "/* Generated by tools/build.py from data/niches.json. Do not edit by hand. */\n"
        f"window.NICHES = {json.dumps(js_data, ensure_ascii=False, indent=1)};\n")

    idx = (ROOT / "index.html").read_text()
    idx = replace_block(idx, "nav", nav(""))
    idx = replace_block(idx, "footer", footer(""))
    idx = replace_block(idx, "play", PLAY.rstrip("\n"))
    idx = replace_block(idx, "wall", wall())
    idx = replace_block(idx, "modal", MODAL)
    (ROOT / "index.html").write_text(idx)

    (ROOT / HUB).mkdir(exist_ok=True)
    (ROOT / HUB / "index.html").write_text(hub_page())
    for k, n in NICHES.items():
        (ROOT / HUB / f"{n['slug']}.html").write_text(niche_page(k, n))

    for name in ("support.html", "privacy.html", "terms.html"):
        rewrap_legal(name, name)
    (ROOT / "404.html").write_text(not_found())
    (ROOT / "sitemap.xml").write_text(sitemap())
    print(f"built: hub + {len(NICHES)} niche pages, 3 legal pages, 404, sitemap, niches.js")


if __name__ == "__main__":
    main()
