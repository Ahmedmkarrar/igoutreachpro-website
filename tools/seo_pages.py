"""Renderers for the search pages: competitor alternatives, guides, their hubs and llms.txt.

Content lives in data/alternatives.json and data/guides.json; build.py calls render_all().
Strings may carry **bold** and [label](href) and nothing else.
"""
import re

ALT = "alternatives"
GUIDES = "guides"
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def plain(text):
    return BOLD_RE.sub(r"\1", LINK_RE.sub(r"\1", text))


def rich(text, esc):
    out, last = [], 0
    for m in LINK_RE.finditer(text):
        out.append(esc(text[last:m.start()]))
        label, href = m.group(1), m.group(2)
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        out.append(f'<a href="{esc(href)}"{ext}>{esc(label)}</a>')
        last = m.end()
    out.append(esc(text[last:]))
    return BOLD_RE.sub(r"<b>\1</b>", "".join(out))


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": plain(f["a"])}} for f in faq]}


def crumbs_ld(site, trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": name, "item": f"{site}/{path}".rstrip("/")}
        for i, (name, path) in enumerate(trail, 1)]}


def section(sid, heading, body, narrow=False):
    return f'''<section class="sec" id="{sid}">
  <div class="rule" aria-hidden="true"><span>+</span></div>
  <div class="wrap{' narrow' if narrow else ''}">
    <header class="sec-head brk rv"><h2><i class="dot" aria-hidden="true"></i>{heading}</h2></header>
{body}
  </div>
</section>'''


def faq_block(faq, esc):
    items = "\n".join(f'''      <details>
        <summary>{esc(f["q"])}</summary>
        <div class="ans"><p>{rich(f["a"], esc)}</p></div>
      </details>''' for f in faq)
    return f'    <div class="faq rv">\n{items}\n    </div>'


def sources_block(sources, checked, esc):
    rows = "\n".join(f'      <li><a href="{esc(s["url"])}" target="_blank" rel="noopener nofollow">{esc(s["label"])}</a></li>' for s in sources)
    note = f'<p class="src-note">Checked {esc(checked)}. Prices and features change; check the vendor\'s own site before you buy.</p>' if checked else ""
    return f'    <ol class="srcs rv">\n{rows}\n    </ol>\n    {note}'


def link_cards(items, esc):
    cards = "\n".join(f'      <a class="nlink brk" href="{href}"><span class="mono">{esc(tag)}</span><b>{esc(title)}</b><span class="nl-go">→</span></a>'
                      for href, tag, title in items)
    return f'    <div class="nlinks rv">\n{cards}\n    </div>'


def hero(esc, crumbs, h1_html, lede, meta, ctas):
    trail = "<span>/</span>".join(
        f'<a href="{href}">{esc(name)}</a>' if href else f"<b>{esc(name)}</b>" for name, href in crumbs)
    return f'''<section class="hero sub" id="top">
  <div class="hero-bg" aria-hidden="true"><i class="blob b1"></i><div class="tiles"></div><div class="fade"></div></div>
  <div class="wrap hero-inner">
    <nav class="crumbs rv" aria-label="Breadcrumb">{trail}</nav>
    <h1 class="rv rv-d1">{h1_html}</h1>
    <p class="hero-sub rv rv-d2">{lede}</p>
    <div class="sub-ctas rv rv-d3">{ctas}</div>
    <p class="sub-meta mono rv rv-d4">{meta}</p>
  </div>
</section>'''


def edge_cell(row, side, esc):
    win = row.get("edge") == side
    return f'<td class="{"us " if side == "us" else ""}{"win" if win else ""}">{esc(row[side])}{" <i class=\"edge\">Better</i>" if win else ""}</td>'


def alt_page(a, ctx):
    esc, site, cws = ctx["esc"], ctx["site"], ctx["cws"]
    path = f"{ALT}/{a['slug']}"
    ld = {"@context": "https://schema.org", "@graph": [
        crumbs_ld(site, [("Home", ""), ("Alternatives", ALT), (a["competitor"], path)]),
        {"@type": "WebPage", "name": a["metaTitle"], "url": f"{site}/{path}", "dateModified": a["checked"],
         "about": [{"@type": "SoftwareApplication", "name": a["competitor"]}, {"@type": "SoftwareApplication", "name": "IG Outreach Pro"}]},
        faq_ld(a["faq"])]}
    v = a["verdict"]
    verdict = f'''    <div class="verdict rv">
      <div class="vcard brk"><span class="mono">Pick {esc(a["competitor"])} if</span><ul>{"".join(f"<li>{rich(x, esc)}</li>" for x in v["pickThem"])}</ul></div>
      <div class="vcard us brk"><span class="mono">Pick IG Outreach Pro if</span><ul>{"".join(f"<li>{rich(x, esc)}</li>" for x in v["pickUs"])}</ul></div>
    </div>'''
    rows = "\n".join(f'          <tr><td>{esc(r["feature"])}</td>{edge_cell(r, "them", esc)}{edge_cell(r, "us", esc)}</tr>' for r in a["rows"])
    table = f'''    <div class="cmp rv">
      <table>
        <thead><tr><th></th><th>{esc(a["competitor"])}</th><th class="us">IG Outreach Pro</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>'''
    well = "\n".join(f'      <li class="tip brk rv"><span class="num-pill">0{i}</span><p>{rich(x, esc)}</p></li>' for i, x in enumerate(a["theyDoWell"], 1))
    diff = "\n".join(f"      <p>{rich(p, esc)}</p>" for p in a["difference"])
    steps = "\n".join(f"      <li>{rich(s, esc)}</li>" for s in a["switching"])
    others = [(f"/{ALT}/{o['slug']}", "Comparison", f"{o['competitor']} alternative") for o in ctx["alternatives"] if o["slug"] != a["slug"]][:8]
    ctas = (f'<a class="btn-dark" href="#compare">See the comparison ↓</a>'
            f'<a class="btn-arrow brk" href="{cws}" target="_blank" rel="noopener"><span class="sq"><svg><use href="#i-arrow"/></svg></span><span class="lbl">Add IG Outreach Pro to Chrome</span></a>')
    body = "\n\n".join([
        hero(esc, [("Home", "/"), ("Alternatives", f"/{ALT}"), (a["competitor"], None)],
             f'{esc(a["competitor"])} alternative: <em class="ig">IG Outreach Pro</em>' if not a.get("h1") else esc(a["h1"]),
             rich(a["lede"], esc), f'Checked {esc(a["checked"])} · {len(a["sources"])} sources · we make IG Outreach Pro', ctas),
        section("verdict", "The short answer", verdict),
        section("compare", f'{esc(a["competitor"])} vs IG Outreach Pro, <em>side by side.</em>', table),
        section("well", f'What {esc(a["competitor"])} <em>does well.</em>', f'    <ol class="tips well">\n{well}\n    </ol>'),
        section("difference", "The real difference", f'    <div class="prose rv">\n{diff}\n    </div>', narrow=True),
        section("switch", f'Switching from {esc(a["competitor"])}', f'    <ol class="steps prose rv">\n{steps}\n    </ol>', narrow=True),
        f'<section class="sec" id="customers">\n  <div class="rule" aria-hidden="true"><span>+</span></div>\n{ctx["wall"]("Five customers, on camera. <em>Press play.</em>")}\n</section>',
        section("faq", "Questions", faq_block(a["faq"], esc), narrow=True),
        section("sources", "Sources", sources_block(a["sources"], a["checked"], esc), narrow=True),
        section("more", "More comparisons", link_cards(others, esc)),
    ])
    return ctx["page"](a["metaTitle"], a["metaDescription"], path, ld, body,
                       ("Try it on your own account.", "Set it up in about 5 minutes and run your first campaign in Test Mode."))


def alt_hub(ctx):
    esc, site = ctx["esc"], ctx["site"]
    alts = ctx["alternatives"]
    ld = {"@context": "https://schema.org", "@graph": [
        crumbs_ld(site, [("Home", ""), ("Alternatives", ALT)]),
        {"@type": "CollectionPage", "name": "Instagram DM tool comparisons", "url": f"{site}/{ALT}",
         "hasPart": [{"@type": "WebPage", "name": a["metaTitle"], "url": f"{site}/{ALT}/{a['slug']}"} for a in alts]}]}
    cards = link_cards([(f"/{ALT}/{a['slug']}", "Honest comparison", f"{a['competitor']} alternative") for a in alts], esc)
    body = "\n\n".join([
        hero(esc, [("Home", "/"), ("Alternatives", None)], 'Instagram DM tools, <em class="ig">compared honestly.</em>',
             "Side-by-side comparisons of IG Outreach Pro with the other Instagram outreach and DM automation tools. Each one says where the other tool is the better pick, and links its sources.",
             f"{len(alts)} comparisons · prices checked against each vendor's own site", ""),
        section("all", "Every comparison", cards),
    ])
    return ctx["page"]("Instagram DM Tool Alternatives & Comparisons | IG Outreach Pro",
                       "Honest comparisons of IG Outreach Pro with InstaOutreach, ColdDMs, ManyChat, Inro and other Instagram DM tools: prices, trials, safety and fit.",
                       ALT, ld, body, None)


def guide_page(g, ctx):
    esc, site = ctx["esc"], ctx["site"]
    path = f"{GUIDES}/{g['slug']}"
    ld = {"@context": "https://schema.org", "@graph": [
        crumbs_ld(site, [("Home", ""), ("Guides", GUIDES), (g["title"], path)]),
        {"@type": "Article", "headline": g["title"], "description": g["metaDescription"], "url": f"{site}/{path}",
         "datePublished": g["updatedIso"], "dateModified": g["updatedIso"],
         "author": {"@type": "Organization", "name": "IG Outreach Pro"},
         "publisher": {"@type": "Organization", "name": "IG Outreach Pro", "logo": {"@type": "ImageObject", "url": f"{site}/assets/img/icon-128.png"}},
         "image": f"{site}/assets/img/og.png"},
        faq_ld(g["faq"])]}
    tldr = "".join(f"<li>{rich(x, esc)}</li>" for x in g["tldr"])
    toc = "".join(f'<li><a href="#{s["id"]}">{esc(s["heading"])}</a></li>' for s in g["sections"])
    parts = []
    for s in g["sections"]:
        blk = [f'<h2 id="{s["id"]}">{esc(s["heading"])}</h2>']
        blk += [f"<p>{rich(p, esc)}</p>" for p in s.get("paragraphs", [])]
        if s.get("steps"):
            blk.append("<ol>" + "".join(f"<li>{rich(x, esc)}</li>" for x in s["steps"]) + "</ol>")
        if s.get("list"):
            blk.append("<ul>" + "".join(f"<li>{rich(x, esc)}</li>" for x in s["list"]) + "</ul>")
        if s.get("tip"):
            blk.append(f'<p class="art-tip"><b>Tip.</b> {rich(s["tip"], esc)}</p>')
        parts.append("\n      ".join(blk))
    article = f'''<section class="sec art-sec">
  <div class="wrap art">
    <aside class="art-toc" aria-label="Contents"><p class="mono">Contents</p><ol>{toc}</ol></aside>
    <article class="prose art-body">
      <div class="tldr brk"><p class="mono">The short answer</p><ul>{tldr}</ul></div>
      {"\n      ".join(parts)}
    </article>
  </div>
</section>'''
    by_slug = {x["slug"]: x for x in ctx["guides"]}
    rel = [(f"/{GUIDES}/{r}", f'{by_slug[r]["minutes"]} min read', by_slug[r]["title"]) for r in g.get("related", []) if r in by_slug]
    rel.append(("/instagram-dm-templates", "Free", "Instagram DM templates by niche"))
    blocks = [
        hero(esc, [("Home", "/"), ("Guides", f"/{GUIDES}"), (g["eyebrow"], None)], esc(g["title"]), rich(g["lede"], esc),
             f'{g["minutes"]} min read · updated {esc(g["updated"])}', ""),
        article,
        section("faq", "Questions", faq_block(g["faq"], esc), narrow=True),
    ]
    if g.get("sources"):
        blocks.append(section("sources", "Sources", sources_block(g["sources"], "", esc), narrow=True))
    blocks.append(section("more", "Keep reading", link_cards(rel, esc)))
    return ctx["page"](g["metaTitle"], g["metaDescription"], path, ld, "\n\n".join(blocks), None)


def guide_hub(ctx):
    esc, site = ctx["esc"], ctx["site"]
    gs = ctx["guides"]
    ld = {"@context": "https://schema.org", "@graph": [
        crumbs_ld(site, [("Home", ""), ("Guides", GUIDES)]),
        {"@type": "CollectionPage", "name": "Instagram outreach guides", "url": f"{site}/{GUIDES}",
         "hasPart": [{"@type": "Article", "headline": g["title"], "url": f"{site}/{GUIDES}/{g['slug']}"} for g in gs]}]}
    body = "\n\n".join([
        hero(esc, [("Home", "/"), ("Guides", None)], 'Instagram outreach, <em class="ig">answered.</em>',
             "Plain answers to the questions people ask before they start DMing on Instagram: limits, blocks, follow-ups, scripts and what a setter costs.",
             f"{len(gs)} guides · each one answers in the first lines", ""),
        section("all", "Every guide", link_cards([(f"/{GUIDES}/{g['slug']}", f'{g["minutes"]} min read', g["title"]) for g in gs], esc)),
    ])
    return ctx["page"]("Instagram Outreach Guides: DMs, Limits, Scripts | IG Outreach Pro",
                       "Straight answers on Instagram DM limits, action blocks, cold DMs, follow-ups, spintax and setter costs, written by the team behind IG Outreach Pro.",
                       GUIDES, ld, body, None)


def llms_txt(ctx):
    site = ctx["site"]
    lines = [
        "# IG Outreach Pro",
        "",
        "> A Chrome extension that sends personalized Instagram DMs and follow-ups from your own account, in your own browser.",
        "",
        "Facts:",
        "- Targets: followers or following of any account, people posting a hashtag, or your own imported list (PDF/Excel).",
        "- Every message can differ: spintax plus {firstname}, {fullname} and {username} placeholders, and AI drafting on paid plans.",
        "- Follow-up sequences, reply scanning, duplicate memory of 10,000+ usernames, CSV export.",
        "- Safety controls the user sets: Test Mode, Safe Start warm-up, pacing presets, hourly cap, break schedule, automatic opt-outs in 12 languages.",
        "- Pro is $29.99 a month. Chrome Web Store rating 5.0.",
        "- It does not offer inbound auto-replies, comment-to-DM, an official Meta API connection, proxies or a done-for-you service.",
        "- Automated DMs can conflict with Instagram's terms; no tool can promise an account will not be restricted.",
        "",
        "## Pages",
        f"- [Home]({site}/)",
        f"- [Free Instagram DM templates]({site}/instagram-dm-templates)",
        f"- [Comparisons]({site}/{ALT})",
        f"- [Guides]({site}/{GUIDES})",
        f"- [Support]({site}/support)",
        "",
        "## Guides",
        *[f"- [{g['title']}]({site}/{GUIDES}/{g['slug']}): {g['metaDescription']}" for g in ctx["guides"]],
        "",
        "## Comparisons",
        *[f"- [{a['competitor']} alternative]({site}/{ALT}/{a['slug']}): {a['metaDescription']}" for a in ctx["alternatives"]],
        "",
        "## DM templates by niche",
        *[f"- [{n['title']}]({site}/instagram-dm-templates/{n['slug']})" for n in ctx["niches"].values()],
        "",
    ]
    return "\n".join(lines)


def render_all(ctx, root):
    (root / ALT).mkdir(exist_ok=True)
    (root / GUIDES).mkdir(exist_ok=True)
    if ctx["alternatives"]:
        (root / ALT / "index.html").write_text(alt_hub(ctx))
        for a in ctx["alternatives"]:
            (root / ALT / f"{a['slug']}.html").write_text(alt_page(a, ctx))
    if ctx["guides"]:
        (root / GUIDES / "index.html").write_text(guide_hub(ctx))
        for g in ctx["guides"]:
            (root / GUIDES / f"{g['slug']}.html").write_text(guide_page(g, ctx))
    (root / "llms.txt").write_text(llms_txt(ctx))
