# -*- coding: utf-8 -*-
"""Static site generator for klavtarlab.com.  python3 build.py <out_dir>"""
import json, os, shutil, sys
from html import escape as e
from content import LANGS, LANG_NAMES, COMPANY, UI, SERVICES, PROCESS, STACK, WORK

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, "dist"))
SITE = "https://klavtarlab.com"
API = "https://api.klavtarlab.com/lead"
VER = "20261013"
ORDERS = json.load(open(os.path.join(SRC, "orders.json")))
WORK_LIVE = [w for w in WORK if not w.get("hidden")]
PRODUCTS = [w for w in WORK_LIVE if w["kind"] == "product"]
CLIENTS = [w for w in WORK_LIVE if w["kind"] == "client"]


def prefix(lang):
    return "" if lang == "en" else "/" + lang


def home_url(lang):
    return prefix(lang) + "/"


def case_url(lang, slug):
    return f"{prefix(lang)}/work/{slug}/"


MARK = ('<svg viewBox="-16 -16 32 32" aria-hidden="true">' +
        "".join(
            f'<line x1="{6.2*__import__("math").cos(a):.2f}" y1="{6.2*__import__("math").sin(a):.2f}" '
            f'x2="{(6.2+l)*__import__("math").cos(a):.2f}" y2="{(6.2+l)*__import__("math").sin(a):.2f}" '
            f'stroke="{"#2f3beb" if l > 7.5 else "currentColor"}" stroke-width="1.6" stroke-linecap="round"/>'
            for a, l in [((i / 16) * 6.2832 - 1.5708, [4, 6, 9, 5, 7, 3, 8, 5, 4, 6, 9, 4, 7, 5, 3, 6][i]) for i in range(16)]
        ) + "</svg>")

GLYPHS = [
    # agents: node graph
    '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="8" cy="9" r="3.5"/><circle cx="26" cy="9" r="3.5"/><circle cx="17" cy="25" r="3.5"/><path d="M11.5 9h11M10 12l5 10M24 12l-5 10"/></svg>',
    # inside systems: stacked layers with spark
    '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12l12-6 12 6-12 6z"/><path d="M5 18l12 6 12-6"/><path d="M5 23.5l12 6 12-6"/></svg>',
    # private: box with lock
    '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="5" y="8" width="24" height="18" rx="2"/><path d="M5 21h24"/><circle cx="25" cy="23.5" r="1" fill="currentColor"/><path d="M14 15v-2a3 3 0 016 0v2"/><rect x="12.5" y="15" width="9" height="4" rx="1"/></svg>',
    # platforms: window
    '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="4" y="6" width="26" height="22" rx="2"/><path d="M4 12h26M12 12v16"/></svg>',
    # data: bars
    '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 28h24"/><path d="M9 24v-7M15 24V9M21 24v-11M27 24v-4"/></svg>',
    # growth: arrow up chart
    '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 25l8-8 5 5 11-11"/><path d="M22 11h7v7"/></svg>',
]
ARROW = '<svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 11h14M12 5l6 6-6 6"/></svg>'


def head(lang, title, desc, path, og_image="/assets/og.png"):
    base = path[len(prefix(lang)):] if lang != "en" else path
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{prefix(l)}{base}">' for l in LANGS)
    canonical = SITE + path
    return f"""<!doctype html>
<html lang="{UI[lang]['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
{alts}
<link rel="alternate" hreflang="x-default" href="{SITE}{base}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#edeff2">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600&family=Unbounded:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={VER}">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "KLAVTAR Sp. z o.o.", "alternateName": "KLAVTAR Lab", "url": SITE, "email": COMPANY["email"], "telephone": COMPANY["phone"], "taxID": COMPANY["nip"], "address": {"@type": "PostalAddress", "streetAddress": "ul. Siewna 15, lok. C002", "postalCode": "94-250", "addressLocality": "Łódź", "addressCountry": "PL"}}, ensure_ascii=False)}</script>
</head>
<body>
"""


def header(lang, path_for):
    t = UI[lang]
    home = home_url(lang)
    nav = "".join(f'<a href="{home}#{k}">{e(v)}</a>' for k, v in t["nav"])
    langs = "".join(
        f'<a href="{path_for(l)}" hreflang="{l}" lang="{l}"' + (' aria-current="page"' if l == lang else "") + f'>{LANG_NAMES[l]}</a>'
        for l in LANGS)
    return f"""<a class="skip" href="#main">{e(t['skip'])}</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{home}" aria-label="KLAVTAR Lab">{MARK}<span>KLAVTAR <small>Lab</small></span></a>
    <nav class="nav" aria-label="Main">{nav}</nav>
    <div class="langs" aria-label="Language">{langs}</div>
    <a class="btn btn-ink header-cta" href="{home}#contact">{e(t['cta'])}</a>
    <button class="menu-btn" type="button" aria-expanded="false">{e(t['menu'])}</button>
  </div>
</header>
"""


def footer(lang):
    t = UI[lang]
    return f"""<footer class="site-footer">
  <div class="wrap footer-row">
    <div>© 2026 KLAVTAR Sp. z o.o. {e(t['footer_rights'])}</div>
    <div class="footer-legal"><span>KRS {COMPANY['krs']}</span><span>NIP {COMPANY['nip']}</span><span>REGON {COMPANY['regon']}</span><span>{e(COMPANY['address'])}</span></div>
    <div class="footer-legal"><a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a><a href="https://github.com/{COMPANY['github']}" rel="noopener">GitHub</a><a href="https://t.me/{COMPANY['telegram']}" rel="noopener">Telegram</a></div>
  </div>
</footer>
<script src="/assets/site.js?v={VER}" defer></script>
</body>
</html>
"""


def frame(w, shot, lang, href=None, eager=False):
    dom = w.get("domain") or ""
    img = f'<img class="frame-shot" src="/assets/work/{shot}.webp" alt="{e(w["name"])}: {e(w[lang]["kind"])}" width="1440" height="900"{"" if eager else " loading=" + chr(34) + "lazy" + chr(34)} decoding="async">'
    inner = f'<a href="{href}" tabindex="-1" aria-hidden="true">{img}</a>' if href else img
    return f'<figure class="frame reveal"><div class="frame-bar"><i></i><i></i><i></i><span class="addr">{e(dom)}</span></div>{inner}</figure>'


def mini_facts(w, lang):
    return '<dl class="mini-facts">' + "".join(
        f"<div><dt>{e(v)}</dt><dd>{e(l)}</dd></div>" for v, l in w["numbers"][lang]) + "</dl>"


# ---------------------------------------------------------------------------
def build_home(lang):
    t = UI[lang]
    p = home_url(lang)
    html = head(lang, t["title"], t["description"], p)
    html += header(lang, home_url)
    total = sum(ORDERS)
    total_txt = "6 000+" if lang != "en" else "6,000+"

    facts = ""
    for v, label in t["facts"]:
        plain = v == "2022"
        suffix = "+" if v == "6000" else ""
        shown = (v if plain else ("6,000" if lang == "en" and v == "6000" else ("6 000" if v == "6000" else v))) + suffix
        facts += f'<li><b data-count="{v}" data-suffix="{suffix}"{" data-plain=" + chr(34) + "1" + chr(34) if plain else ""}>{shown}</b><span>{e(label)}</span></li>'

    services = ""
    for i, s in enumerate(SERVICES):
        title, desc, proof = s[lang]
        services += f'<li><span class="glyph">{GLYPHS[i]}</span><div><h3>{e(title)}</h3><p>{e(desc)}</p></div><p class="proof"><em>{e(t["proof"])}</em>{e(proof)}</p></li>'

    products = ""
    for w in PRODUCTS:
        d = w[lang]
        cu = case_url(lang, w["slug"])
        products += f"""<article class="product">
  {frame(w, w['shots'][0], lang, cu)}
  <div>
    <h3>{e(w['name'])}</h3>
    <p class="kind">{e(d['kind'])}</p>
    <p class="line">{e(d['line'])}</p>
    {mini_facts(w, lang)}
    <div class="links"><a class="btn btn-ghost" href="{cu}">{e(t['read_case'])}</a><a class="link" href="{w['url']}" rel="noopener" target="_blank">{e(w['domain'])}</a></div>
  </div>
</article>"""

    clients = ""
    for w in CLIENTS:
        d = w[lang]
        cu = case_url(lang, w["slug"])
        chips = "".join(f"<li>{e(s)}</li>" for s in w["chips"][lang])
        thumb_src = f"/assets/work/{w['shots'][0]}.webp" if w["shots"] else f"/assets/work/{w['cover']}.webp"
        site_link = f'<a class="link" href="{w["url"]}" rel="noopener" target="_blank">{e(w["domain"])}</a>' if w.get("url") else ""
        clients += f"""<article class="client">
  <div>
    <h3>{e(w['name'])}</h3>
    <p class="meta"><span>{e(w['legal'])}</span><span>{e(d['location'])}</span><span>{e(t['contract'])} {e(w['contract'])}, {w['year']}</span></p>
  </div>
  <div class="client-body">
    <div>
      <p class="line">{e(d['line'])}</p>
      <ul class="chips">{chips}</ul>
      <div class="links"><a class="btn btn-ghost" href="{cu}">{e(t['read_case'])}</a>{site_link}</div>
    </div>
    <a class="thumb" href="{cu}" tabindex="-1" aria-hidden="true"><img src="{thumb_src}" alt="" loading="lazy" decoding="async"></a>
  </div>
</article>"""

    steps = "".join(f"<li><h3>{e(a)}</h3><p>{e(b)}</p></li>" for a, b in PROCESS[lang])
    stack = "".join(f"<li>{e(s)}</li>" for s in STACK)
    legal = "".join(f"<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>" for a, b in t["legal"])
    company_p = "".join(f"<p>{e(x)}</p>" for x in t["company_text"])
    topics = "".join(f"<option>{e(x)}</option>" for x in t["f_topics"])

    html += f"""<main id="main">
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <h1>{e(t['hero_h1'])}</h1>
      <p class="lead">{e(t['hero_lead'])}</p>
      <div class="hero-actions"><a class="btn btn-ink" href="#contact">{e(t['cta'])}</a><a class="btn btn-ghost" href="#products">{e(t['hero_secondary'])}</a></div>
    </div>
    <figure class="wheel-fig">
      <div class="wheel" id="wheel" data-orders='{json.dumps(ORDERS)}' data-months='{json.dumps(t["months"], ensure_ascii=False)}' data-label="{e(t['wheel_caption'])}" data-orders-word="{e(t['wheel_orders'])}">
        <div class="wheel-center"><b>{total_txt}</b><span>{e(t['wheel_center_label'])}</span></div>
      </div>
      <figcaption>{e(t['wheel_caption'])}</figcaption>
    </figure>
  </div>
</section>

<section class="facts" aria-label="Facts"><div class="wrap"><ul>{facts}</ul></div></section>

<section class="section" id="services">
  <div class="wrap">
    <div class="sec-head"><h2>{e(t['services_h'])}</h2><p class="lead">{e(t['services_lead'])}</p></div>
    <ul class="services">{services}</ul>
  </div>
</section>

<section class="section" id="products">
  <div class="wrap">
    <div class="sec-head"><h2>{e(t['products_h'])}</h2><p class="lead">{e(t['products_lead'])}</p></div>
    {products}
  </div>
</section>

<section class="section" id="clients">
  <div class="wrap">
    <div class="sec-head"><h2>{e(t['clients_h'])}</h2><p class="lead">{e(t['clients_lead'])}</p></div>
    {clients}
  </div>
</section>

<section class="section" id="process">
  <div class="wrap">
    <div class="sec-head solo"><h2>{e(t['process_h'])}</h2></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>

<section class="section" id="stack">
  <div class="wrap">
    <div class="sec-head solo"><h2>{e(t['stack_h'])}</h2></div>
    <ul class="stack">{stack}</ul>
  </div>
</section>

<section class="section" id="company">
  <div class="wrap">
    <div class="sec-head solo"><h2>{e(t['company_h'])}</h2></div>
    <div class="company-grid"><div>{company_p}</div><dl class="legal">{legal}</dl></div>
  </div>
</section>

<section class="section contact" id="contact">
  <div class="wrap contact-grid">
    <div>
      <h2>{e(t['contact_h'])}</h2>
      <p class="lead" style="margin-top:18px">{e(t['contact_lead'])}</p>
      <form class="form" id="lead-form" action="{API}" method="post" data-sending="{e(t['f_sending'])}" data-ok="{e(t['f_ok'])}" data-err="{e(t['f_err'])}" novalidate>
        <div class="field"><label for="f-name">{e(t['f_name'])}</label><input id="f-name" name="name" autocomplete="name" required maxlength="120"></div>
        <div class="field"><label for="f-company">{e(t['f_company'])}</label><input id="f-company" name="company" autocomplete="organization" maxlength="160"></div>
        <div class="field"><label for="f-email">{e(t['f_email'])}</label><input id="f-email" name="email" type="email" autocomplete="email" required maxlength="160"></div>
        <div class="field"><label for="f-topic">{e(t['f_topic'])}</label><select id="f-topic" name="topic">{topics}</select></div>
        <div class="field full"><label for="f-msg">{e(t['f_message'])}</label><textarea id="f-msg" name="message" required maxlength="4000" placeholder="{e(t['f_message_ph'])}"></textarea></div>
        <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
        <div class="form-foot full"><button class="btn btn-ink" type="submit">{e(t['f_send'])}</button><p class="form-note">{e(t['f_consent'])}</p></div>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
    <aside class="direct">
      <h3>{e(t['direct'])}</h3>
      <ul>
        <li><span>Email</span><a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a></li>
        <li><span>Telefon / Phone</span><a href="tel:{COMPANY['phone_href']}">{COMPANY['phone']}</a></li>
        <li><span>Telegram</span><a href="https://t.me/{COMPANY['telegram']}" rel="noopener">@{COMPANY['telegram']}</a></li>
        <li><span>KLAVTAR Sp. z o.o.</span><a href="https://www.google.com/maps/search/?api=1&query=Siewna+15+Łódź" rel="noopener">{e(COMPANY['address'])}</a></li>
      </ul>
    </aside>
  </div>
</section>
</main>
"""
    html += footer(lang)
    return html


def build_case(lang, w, nxt):
    t = UI[lang]
    d = w[lang]
    path = case_url(lang, w["slug"])
    title = f"{w['name']} — {d['kind']} | KLAVTAR Lab"
    og = f"/assets/work/{w['shots'][0]}.webp" if w["shots"] else f"/assets/work/{w['cover']}.webp"
    html = head(lang, title, d["line"], path, og)
    html += header(lang, lambda l: case_url(l, w["slug"]))

    meta = [(t["case_client"], d["client"]), (t["case_location"], d["location"]), (t["case_year"], w["year"]), (t["case_role"], d["role"])]
    if w["kind"] == "client":
        meta.append((t["contract"], w["contract"]))
    status = f'<a class="link" href="{w["url"]}" rel="noopener" target="_blank">{e(w["domain"])}</a>' if w.get("url") else None
    meta_html = "".join(f"<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>" for a, b in meta)
    if status:
        meta_html += f"<div><dt>{e(t['case_status'])}</dt><dd>{status}</dd></div>"

    if w["shots"]:
        cover = frame(w, w["shots"][0], lang, eager=True)
    else:
        cover = f'<div class="cover-img"><img src="/assets/work/{w["cover"]}.webp" alt="" width="1344" height="752"></div>'

    built = "".join(f"<li>{e(x)}</li>" for x in d["built"])
    blocks = f"""<section class="case-block"><h2>{e(t['case_task'])}</h2><div class="body"><p>{e(d['task'])}</p></div></section>
<section class="case-block"><h2>{e(t['case_built'])}</h2><ul class="ticks body">{built}</ul></section>"""
    if w["kind"] == "client":
        stages = "".join(f'<li data-word="{e(t["stage_word"])}"><span>{e(s)}</span></li>' for s in w["stages"][lang])
        blocks += f'<section class="case-block"><h2>{e(t["case_stages"])}</h2><ol class="stage-list body">{stages}</ol></section>'
    nums = "".join(f"<div><dt>{e(v)}</dt><dd>{e(l)}</dd></div>" for v, l in w["numbers"][lang])
    blocks += f'<section class="case-block"><h2>{e(t["case_numbers"])}</h2><dl class="numbers">{nums}</dl></section>'
    if w["shots"] and len(w["shots"]) > 1:
        phone = f'<div class="phone"><img src="/assets/work/{w["mobile"]}.webp" alt="" loading="lazy" decoding="async" width="780" height="1688"></div>' if w.get("mobile") else ""
        blocks += f'<section class="case-block"><h2>{e(t["case_gallery"])}</h2><div class="gallery">{frame(w, w["shots"][1], lang)}{phone}</div></section>'
    stack = "".join(f"<li>{e(s)}</li>" for s in w["stack"])
    blocks += f'<section class="case-block"><h2>{e(t["case_stack"])}</h2><ul class="stack">{stack}</ul></section>'

    html += f"""<main id="main">
<div class="wrap">
  <p class="crumbs"><a href="{home_url(lang)}#{'products' if w['kind'] == 'product' else 'clients'}">{e(t['all_work'])}</a></p>
  <section class="case-hero">
    <p class="kind">{e(t['own_product'] if w['kind'] == 'product' else t['client_project'])}: {e(d['kind'])}</p>
    <h1>{e(w['name'])}</h1>
    <p class="lead">{e(d['line'])}</p>
    <dl class="case-meta">{meta_html}</dl>
  </section>
  <div class="case-cover">{cover}</div>
  {blocks}
  <a class="next-case" href="{case_url(lang, nxt['slug'])}"><span><small>{e(t['next_case'])}</small><strong>{e(nxt['name'])}</strong></span><span class="arrow">{ARROW}</span></a>
</div>
<section class="section contact">
  <div class="wrap contact-grid">
    <div><h2>{e(t['contact_h'])}</h2><p class="lead" style="margin-top:18px">{e(t['contact_lead'])}</p><p style="margin-top:28px"><a class="btn btn-ink" style="background:#fff;color:#12151c;border-color:#fff" href="{home_url(lang)}#contact">{e(t['cta'])}</a></p></div>
    <aside class="direct"><ul><li><span>Email</span><a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a></li><li><span>Telegram</span><a href="https://t.me/{COMPANY['telegram']}" rel="noopener">@{COMPANY['telegram']}</a></li></ul></aside>
  </div>
</section>
</main>
"""
    html += footer(lang)
    return html


def build_404():
    t = UI["en"]
    html = head("en", "Page not found | KLAVTAR Lab", t["description"], "/404.html")
    html += header("en", home_url)
    html += f"""<main id="main"><section class="hero"><div class="wrap"><h1>Page not found</h1><p class="lead" style="margin-top:20px">The page may have moved after the redesign. Start from the home page or open a project.</p><div class="hero-actions"><a class="btn btn-ink" href="/">KLAVTAR Lab</a><a class="btn btn-ghost" href="/#products">{e(t['hero_secondary'])}</a></div></div></section></main>"""
    html += footer("en")
    return html


def write(rel, text):
    path = os.path.join(OUT, rel.lstrip("/"))
    if path.endswith("/"):
        path += "index.html"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    # clean generated dirs (keep .git, CNAME)
    for name in ["assets", "pl", "ru", "work", "index.html", "404.html", "sitemap.xml", "robots.txt"]:
        p = os.path.join(OUT, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    shutil.copytree(os.path.join(SRC, "assets_src" if os.path.isdir(os.path.join(SRC, "assets_src")) else "assets"), os.path.join(OUT, "assets"))
    urls = []
    for lang in LANGS:
        write(home_url(lang), build_home(lang)); urls.append(home_url(lang))
        for i, w in enumerate(WORK_LIVE):
            nxt = WORK_LIVE[(i + 1) % len(WORK_LIVE)]
            write(case_url(lang, w["slug"]), build_case(lang, w, nxt)); urls.append(case_url(lang, w["slug"]))
    write("/404.html", build_404())
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(OUT, "CNAME"), "w") as f:
        f.write("klavtarlab.com\n")
    print("built", len(urls), "pages into", OUT)


if __name__ == "__main__":
    main()
