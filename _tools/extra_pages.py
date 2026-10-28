"""Generate /planners/ (printable planner catalogue) and /about/.

Run from the repo root:  python _tools/extra_pages.py && python _tools/build.py
Planner list comes from PLANNERS in exams.py, read with ast (importing exams.py would rewrite the plan pages).
Add a planner by adding its slug to PLANNERS in exams.py and a thumbnail to assets/products/planners/.
"""
import ast, json, pathlib, re
from common import SITE, shell, crumbs, ORG

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORE = "https://store.thefocusflowlab.com/l/"
tree = ast.parse((ROOT / "_tools/exams.py").read_text(encoding="utf-8"))
def literal(name):
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == name)
EXAMS = {e["slug"]: e for e in literal("EXAMS")}
PLANNERS = literal("PLANNERS")

# (title, weeks label, blurb, store permalink, free plan page, thumbnail slug)
ITEMS = [("Exam Sprint Planner", "14 days", "The two weeks before any exam: exam map, priority grid, four focus blocks a day, a self-test after each.", "exam-sprint-planner", "/#planner", "exam-sprint-planner"),
         ("NCLEX-RN 8-Week Study Planner", "8 weeks", "Exam map weighted to the client-needs categories, practice test log, error log.", "nclex-rn-8-week-planner", "/study-plan/nclex/", "nclex-rn-8-week-planner"),
         ("MCAT 16-Week Study Planner", "16 weeks", "Content review first, full-length tests second, CARS every week.", "mcat-16-week-planner", "/study-plan/mcat/", "mcat-16-week-planner")]
for slug, (weeks, link) in PLANNERS.items():
    e = EXAMS[slug]
    ITEMS.append((f"{e['short']} {weeks}-Week Study Planner", f"{weeks} weeks", f"Exam map with rough shares by area, {weeks}-week overview, weekly and daily pages, practice test and error logs.", link, f"/study-plan/{slug}/", link))

FAQ = [
    ("What do I get?", "Two printable PDFs, A4 and US Letter, of 9 pages each: an exam map, a week-by-week overview, a weekly page, a daily focus page with four focus blocks and a self-test after each, a practice test log, an error log and a test-day checklist. Print as many copies of the weekly and daily pages as you need."),
    ("How do I receive it?", "Right after payment you get a download page, and a receipt with the download link is emailed to you. Nothing is shipped."),
    ("Is this an official plan from the exam owner?", "No. These are study planners made by FocusFlow Lab and are not affiliated with or endorsed by any exam owner. Exam shares are rough planning figures, so check the official exam outline for the current version."),
    ("Can you promise I will pass?", "No. A planner helps you organise your time. It can’t guarantee any score."),
    ("What if it isn’t useful?", "Email hello@thefocusflowlab.com within 14 days of buying and you’ll get a full refund, no questions asked."),
    ("Is there a free option?", "Yes. The free study plan generators build a week-by-week schedule for each exam, and the free Study Focus Kit includes a printable study planner."),
]

def nowrap_first(title):
    """Keep a hyphenated first word such as NCLEX-RN on one line."""
    first, _, rest = title.partition(" ")
    return f'<span class="nw">{first}</span> {rest}' if "-" in first else title

def card(t):
    title, dur, blurb, link, plan, thumb = t
    url = STORE + link
    return f'''        <li class="planner-card">
          <img src="/assets/products/planners/{thumb}.png" alt="{title} cover" width="400" height="400" loading="lazy" decoding="async">
          <h2>{nowrap_first(title)}</h2>
          <p>{blurb}</p>
          <p class="product-meta">{dur} · 9 pages · A4 + US Letter PDFs</p>
          <div class="buy"><p class="price">$5</p><a class="btn" href="{url}">Get the planner</a></div>
          <p><a class="text-link" href="{plan}">Free plan for this exam</a></p>
        </li>'''

def planners_page():
    path = "/planners/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Planners", path)])
    desc = "Printable study planners for NCLEX, MCAT, USMLE, GRE, LSAT, CPA and more. Weekly and daily pages, an error log and a test-day checklist. $5 each, 14-day refund."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "Printable study planners", "url": SITE + path, "description": desc, "publisher": ORG,
         "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
             "@type": "Product", "name": t[0], "description": t[2], "url": STORE + t[3], "image": f"{SITE}/assets/products/planners/{t[5]}.png",
             "brand": {"@type": "Brand", "name": "FocusFlow Lab"},
             "offers": {"@type": "Offer", "price": "5.00", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": STORE + t[3]}}}
             for i, t in enumerate(ITEMS)]}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        crumb_ld]}
    cards = "\n".join(card(t) for t in ITEMS)
    faq = "\n".join(f"        <h3>{q}</h3>\n        <p>{a}</p>" for q, a in FAQ)
    body = f"""{crumb_html}

    <main id="main">
      <section class="hero single wash">
        <div>
          <h1>Printable study planners.</h1>
          <p class="lead">One plan per exam, laid out week by week. Print it, pin it up, follow it. $5 each, with a 14-day no-questions refund.</p>
        </div>
      </section>
      <ul class="planner-grid">
{cards}
      </ul>
      <section class="reading">
        <h2>Free first</h2>
        <p>Every exam on this site also has a <a href="/study-plan/">free study plan generator</a>, and the <a href="/#free-kit">free Study Focus Kit</a> includes a printable study planner. The paid planners are the same system on paper, with logs and a checklist you can write on.</p>
      </section>
      <section class="reading faq">
        <h2>Questions people ask</h2>
        <div class="prose">
{faq}
        </div>
      </section>
    </main>
    <aside class="page-note" aria-label="About this page">
      <p>Made by FocusFlow Lab. Questions: <a href="mailto:hello@thefocusflowlab.com">hello@thefocusflowlab.com</a>. Exam names belong to their owners; FocusFlow Lab isn’t affiliated with or endorsed by any exam owner. Purchases are processed by Gumroad; see the <a href="/terms.html">terms</a> and <a href="/privacy.html">privacy policy</a>.</p>
    </aside>"""
    return shell(path=path, title="Printable Study Planners for NCLEX, MCAT, USMLE, GRE and More | FocusFlow Lab", desc=desc,
                 og_title="Printable study planners", ld=ld, body=body, css_depth=1, extra_head='\n  <link rel="stylesheet" href="../study-plan/assets/plan.css">')

def about_page():
    path = "/about/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("About", path)])
    desc = "Who runs FocusFlow Lab, how the free study tools work, how to get help and how refunds work."
    ld = {"@context": "https://schema.org", "@graph": [{"@type": "AboutPage", "name": "About FocusFlow Lab", "url": SITE + path, "description": desc, "publisher": ORG}, crumb_ld]}
    body = f"""{crumb_html}

    <main id="main">
      <header class="doc-head">
        <h1>About FocusFlow Lab</h1>
        <p class="lead">Simple study systems for students: fewer phone distractions, notes that stick, calmer exam weeks.</p>
      </header>
      <div class="doc">
        <article class="prose">
<h2>Who runs it</h2>
<p>FocusFlow Lab is run by Ahsan Raza in Lahore, Pakistan. It started as a study-focus YouTube channel, and this site turns the same ideas into free tools, exam study plans, guides and printable planners.</p>
<h2>What’s free</h2>
<p>The <a href="/study-plan/">study plan generators</a>, the <a href="/tools/">study tools</a> and the <a href="/guides/">guides</a> are free. The tools run in your browser and keep what you type on your own device. The <a href="/#free-kit">Study Focus Kit</a> is free by email.</p>
<h2>What’s paid</h2>
<p>The <a href="/planners/">printable planners</a> are $5 each. They are sold through Gumroad, which handles payment and tax. Each one has a 14-day no-questions refund: email <a href="mailto:hello@thefocusflowlab.com">hello@thefocusflowlab.com</a> within 14 days of buying.</p>
<h2>Exam names</h2>
<p>Exam names belong to their owners. FocusFlow Lab isn’t affiliated with or endorsed by any exam owner, and nothing here guarantees a score or a pass. Exam details come from the official outlines; where we estimate, we say so.</p>
<h2>Get in touch</h2>
<p>Questions, corrections or an exam you’d like a plan for: <a href="mailto:hello@thefocusflowlab.com">hello@thefocusflowlab.com</a>. See also the <a href="/terms.html">terms</a> and the <a href="/privacy.html">privacy policy</a>.</p>
        </article>
      </div>
    </main>"""
    return shell(path=path, title="About FocusFlow Lab: Free Study Tools and Printable Planners", desc=desc, og_title="About FocusFlow Lab", ld=ld, body=body, css_depth=1)

for rel, html in (("planners", planners_page()), ("about", about_page())):
    out = ROOT / rel / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT).as_posix())
