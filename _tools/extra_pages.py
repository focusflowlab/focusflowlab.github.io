"""Generate /planners/ (printable planner catalogue) and /about/.

Run from the repo root:  python _tools/extra_pages.py && python _tools/build.py
Planner list comes from PLANNERS in exams.py, read with ast (importing exams.py would rewrite the plan pages).
Add a planner by adding its slug to PLANNERS in exams.py and a thumbnail to assets/products/planners/.
"""
import ast, json, pathlib, re
from common import SITE, shell, crumbs, ORG
import planner_extra

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORE = "https://store.thefocusflowlab.com/l/"
tree = ast.parse((ROOT / "_tools/exams.py").read_text(encoding="utf-8"))
def literal(name):
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == name)
EXAMS = {e["slug"]: e for e in literal("EXAMS")}
PLANNERS = literal("PLANNERS")
PLANNERS_MAP = PLANNERS

# (title, weeks label, blurb, store permalink, free plan page, thumbnail slug)
ITEMS = [("Exam Sprint Planner", "14 days", "The two weeks before any exam: exam map, priority grid, four focus blocks a day, a self-test after each.", "exam-sprint-planner", "/#planner", "exam-sprint-planner"),
         ("NCLEX-RN 8-Week Study Planner", "8 weeks", "Exam map weighted to the client-needs categories, practice test log, error log.", "nclex-rn-8-week-planner", "/study-plan/nclex/", "nclex-rn-8-week-planner"),
         ("MCAT 16-Week Study Planner", "16 weeks", "Content review first, full-length tests second, CARS every week.", "mcat-16-week-planner", "/study-plan/mcat/", "mcat-16-week-planner")]
for slug, (weeks, link) in PLANNERS.items():
    e = EXAMS[slug]
    top = ", ".join(n for n, _ in e["topics"][:3])
    ITEMS.append((f"{e['short']} {weeks}-Week Study Planner", f"{weeks} weeks", f"Exam map covering {top} and more, with weekly and daily pages.", link, f"/study-plan/{slug}/", link))

BUNDLE = ("All 14 Exam Planners Bundle", "14 planners", "All 14 exam-specific planners listed below in one purchase: NCLEX-RN and PN, TEAS, NAPLEX, MCAT, USMLE Step 1, PANCE, DAT, GRE, LSAT, GMAT and the three CPA sections. $15 instead of $70 bought one by one. The Exam Sprint Planner is sold separately.", "all-exam-planners-bundle", "/study-plan/", "all-exam-planners-bundle")

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

GROUPS = [("Short on time", ("exam-sprint",)), ("Nursing", ("nclex", "ati-teas")), ("Medicine and health", ("mcat", "usmle", "pance", "naplex", "dat")),
          ("Accounting", ("cpa",)), ("Graduate and law school", ("gre", "gmat", "lsat"))]
def group_of(t):  # shortcut: groups match by thumb-slug prefix, a new exam needs a key here
    return next(n for n, keys in GROUPS if t[5].startswith(keys))

def card(t, price="$5", meta=None, cta="Get the planner", group=True):
    title, dur, blurb, link, plan, thumb = t
    meta = meta or dur
    g = group_of(t) if group else ""
    return f'''        <li class="pc" data-group="{g}" data-name="{title.lower()} {link}">
          <a class="pc-img" href="/planners/{link}/" tabindex="-1" aria-hidden="true"><img src="/assets/products/planners/{thumb}.png" alt="" width="240" height="240" loading="lazy" decoding="async"></a>
          <div class="pc-body">
            <p class="pc-tag">{g or "Bundle"} · {meta}</p>
            <h3><a href="/planners/{link}/">{nowrap_first(title)}</a></h3>
            <p class="pc-blurb">{blurb}</p>
            <div class="pc-buy"><span class="pc-price">{price}</span><a class="btn" href="{STORE}{link}?wanted=true">{cta}</a><a class="text-link" href="/planners/{link}/">Details</a></div>
          </div>
        </li>'''

# same shipping/return blocks as the home-page products, so Google's merchant listing checks pass
_cc = ["US", "GB", "CA", "AU"]
_zero = {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 0, "unitCode": "DAY"}
OFFER_EXTRA = {
    "shippingDetails": {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "USD"},
                        "shippingDestination": {"@type": "DefinedRegion", "addressCountry": _cc},
                        "deliveryTime": {"@type": "ShippingDeliveryTime", "handlingTime": _zero, "transitTime": _zero}},
    "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": _cc,
                                "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays": 14,
                                "returnFees": "https://schema.org/FreeReturn",
                                "refundType": "https://schema.org/FullRefund", "merchantReturnLink": SITE + "/terms.html#planner-refunds"}}

def planners_page():
    path = "/planners/"
    offer_extra = OFFER_EXTRA
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Planners", path)])
    desc = "Printable study planners for NCLEX, MCAT, USMLE, GRE, LSAT, CPA and more. Weekly and daily pages, error log, checklist. $5 each or all 14 for $15."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "Printable study planners", "url": SITE + path, "description": desc, "publisher": ORG,
         "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
             "@type": "Product", "name": t[0], "description": t[2], "url": f"{SITE}/planners/{t[3]}/", "image": f"{SITE}/assets/products/planners/{t[5]}.png",
             "brand": {"@type": "Brand", "name": "FocusFlow Lab"},
             "offers": {"@type": "Offer", "price": "5.00", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": STORE + t[3], **offer_extra}}}
             for i, t in enumerate(ITEMS)] + [{"@type": "ListItem", "position": len(ITEMS) + 1, "item": {
             "@type": "Product", "name": BUNDLE[0], "description": BUNDLE[2], "url": f"{SITE}/planners/{BUNDLE[3]}/", "image": f"{SITE}/assets/products/planners/{BUNDLE[5]}.png",
             "brand": {"@type": "Brand", "name": "FocusFlow Lab"},
             "offers": {"@type": "Offer", "price": "15.00", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": STORE + BUNDLE[3], **offer_extra}}}]}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        crumb_ld]}
    cards = "\n".join(card(t) for t in sorted(ITEMS, key=lambda t: [n for n, _ in GROUPS].index(group_of(t))))
    chips = "".join(f'<button type="button" class="chip" aria-pressed="false" data-filter="{n}">{n}</button>' for n, _ in GROUPS)
    bundle_links = "".join(f'<li><a href="/planners/{i[3]}/">{i[0].replace(" Study Planner", "")}</a></li>' for i in ITEMS[1:])
    faq = "\n".join(f"        <h3>{q}</h3>\n        <p>{a}</p>" for q, a in FAQ)
    body = f"""{crumb_html}

    <main id="main">
      <section class="hero single wash">
        <div>
          <h1>Printable study planners.</h1>
          <p class="lead">One plan per exam, laid out week by week. Print it, pin it up, follow it. $5 each, or all 14 exam planners for $15, with a 14-day no-questions refund.</p>
        </div>
        <a class="scroll-cue" href="#find"><span>All 15 planners below</span><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
      </section>
      <section class="choose" aria-labelledby="choose-title">
        <h2 id="choose-title">Not sure which one to get?</h2>
        <ul class="choose-grid">
          <li><strong>Your exam is within two weeks</strong><p>The Exam Sprint Planner lays out the last 14 days.</p><a class="text-link" href="/planners/exam-sprint-planner/">See the Sprint Planner</a></li>
          <li><strong>One exam, a month or more away</strong><p>Pick your exam below. Each plan matches that exam&rsquo;s length and sections.</p><a class="text-link" href="#find">Find your exam</a></li>
          <li><strong>Two or more exams, or still deciding</strong><p>Three single planners cost $15, the same as the bundle of all 14.</p><a class="text-link" href="/planners/all-exam-planners-bundle/">See the bundle</a></li>
        </ul>
      </section>

      <section class="bundle-band" aria-labelledby="bundle-title">
        <div>
          <p class="pc-tag">Best value</p>
          <h2 id="bundle-title">All 14 exam planners, $15</h2>
          <p>Every exam-specific planner in one purchase, instead of $70 bought one by one. The Exam Sprint Planner is sold separately.</p>
          <div class="pc-buy"><span class="pc-price">$15</span><a class="btn" href="{STORE}{BUNDLE[3]}?wanted=true">Get the bundle</a><a class="text-link" href="/planners/{BUNDLE[3]}/">Details</a></div>
        </div>
        <ul class="bundle-links" aria-label="Planners in the bundle">{bundle_links}</ul>
      </section>

      <section id="find" class="finder" aria-labelledby="find-title">
        <h2 id="find-title">Find your planner</h2>
        <div class="finder-bar">
          <label for="planner-q">Search by exam</label>
          <input id="planner-q" type="search" placeholder="NCLEX, MCAT, CPA, GRE" autocomplete="off">
          <div class="chips" role="group" aria-label="Filter by area"><button type="button" class="chip" aria-pressed="true" data-filter="">All</button>{chips}</div>
        </div>
        <p class="finder-count" id="finder-count" aria-live="polite"></p>
        <ul class="pc-grid" id="pc-grid">
{cards}
        </ul>
        <p class="finder-empty" id="finder-empty" hidden>No planner matches that yet. Try another exam name, or <a href="mailto:hello@thefocusflowlab.com">email us which exam you need</a>.</p>
      </section>
      <script src="/assets/planner-filter.js" defer></script>

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
    return shell(path=path, title="Printable Study Planners: NCLEX, MCAT, GRE, CPA | FocusFlow Lab", desc=desc,
                 og_title="Printable study planners", ld=ld, body=body, css_depth=1, extra_head='\n  <link rel="stylesheet" href="../study-plan/assets/plan.css">')

def about_page():
    path = "/about/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("About", path)])
    desc = "Who runs FocusFlow Lab, why the study plans exist, how they are built from official exam outlines, and how refunds work."
    ld = {"@context": "https://schema.org", "@graph": [{"@type": "AboutPage", "name": "About FocusFlow Lab", "url": SITE + path, "description": desc, "publisher": ORG, "about": {"@id": SITE + "/#org"}}, {**ORG, "logo": SITE + "/assets/logo-512.png", "email": "hello@thefocusflowlab.com", "founder": {"@type": "Person", "name": "Ahsan Raza", "url": SITE + "/about/"}, "sameAs": ["https://www.youtube.com/@YourFocusFlowLab", "https://www.tiktok.com/@focusflowlabofficial", "https://www.pinterest.com/focusflowlabofficial/"]}, crumb_ld]}
    body = f"""{crumb_html}

    <main id="main">
      <header class="doc-head">
        <h1>About FocusFlow Lab</h1>
        <p class="lead">Simple study systems for students: fewer phone distractions, notes that stick, calmer exam weeks.</p>
      </header>
      <div class="doc">
        <nav class="toc" aria-label="On this page"><p>On this page</p><ol><li><a href="#who">Who runs it</a></li><li><a href="#why">Why it exists</a></li><li><a href="#how">How the plans are made</a></li><li><a href="#free">What’s free</a></li><li><a href="#paid">What’s paid</a></li><li><a href="#names">Exam names</a></li><li><a href="#contact">Get in touch</a></li></ol></nav>
        <article class="prose">
<h2 id="who">Who runs it</h2>
<p>FocusFlow Lab is run by Ahsan Raza, a software engineer. I have worked through many of these exams myself, one at a time, over months and years of study, and I have taught many students along the way. What I kept running into is what a good plan needs and what most plans leave out. This site started as a study-focus YouTube channel, and it turns what I learned into free tools, exam study plans, guides and printable planners.</p>
<h2 id="why">Why it exists</h2>
<p>Most people do not fail for lack of effort. They fail to turn an exam date and a long syllabus into a week they can actually follow. So I build plans that start from the exam’s own outline, give each topic hours in proportion to its weight, put practice tests and review on the calendar, and leave a rest day. The free tools handle the arithmetic people usually do badly in their heads: days left, study hours, the grade you need on a final, your pace per question.</p>
<h2 id="how">How the plans are made</h2>
<ul>
<li><strong>Official sources first.</strong> Exam formats, section names and timings come from the exam owner’s own pages. The planner pages show a short “official facts” block, with the month we last checked.</li>
<li><strong>Estimates are labelled.</strong> Where an exam owner does not publish a figure, such as how study time should be shared out, we say it is a rough guide and not an official number. If we could not confirm a fact, we leave it out.</li>
<li><strong>Cross-checked.</strong> Each plan’s weeks, hours and totals are checked against the outline and against each other before it goes live.</li>
<li><strong>Corrected when you tell us.</strong> Exams change. If something is out of date, <a href="mailto:hello@thefocusflowlab.com">email me</a> and I will fix it and note the date.</li>
</ul>
<h2 id="free">What’s free</h2>
<p>The <a href="/study-plan/">study plan generators</a>, the <a href="/tools/">study tools</a> and the <a href="/guides/">guides</a> are free. The tools run in your browser and keep what you type on your own device. The <a href="/#free-kit">Study Focus Kit</a> is free by email.</p>
<h2 id="paid">What’s paid</h2>
<p>The <a href="/planners/">printable planners</a> are $5 each, or $15 for the bundle of all 14 exam planners. They are sold through Gumroad, which handles payment and tax. Each one has a 14-day no-questions refund: email <a href="mailto:hello@thefocusflowlab.com">hello@thefocusflowlab.com</a> within 14 days of buying.</p>
<h2 id="names">Exam names</h2>
<p>Exam names belong to their owners. FocusFlow Lab isn’t affiliated with or endorsed by any exam owner, and nothing here guarantees a score or a pass. Exam details come from the official outlines; where we estimate, we say so.</p>
<h2 id="contact">Get in touch</h2>
<p>Questions, corrections or an exam you’d like a plan for: <a href="mailto:hello@thefocusflowlab.com">hello@thefocusflowlab.com</a>. See also the <a href="/terms.html">terms</a> and the <a href="/privacy.html">privacy policy</a>.</p>
        </article>
      </div>
    </main>"""
    return shell(path=path, title="About FocusFlow Lab: Free Study Tools and Printable Planners", desc=desc, og_title="About FocusFlow Lab", ld=ld, body=body, css_depth=1)

# ---- one page per planner: /planners/<store permalink>/ ----
# Facts below are copied from each product's own Gumroad description; do not add claims that are not in it.
RELATED = literal("RELATED")
_FOR = {  # permalink: (what the plan is for, exam-map wording, trademark / non-affiliation note)
    "nclex-rn-8-week-planner": ("the NCLEX-RN", "Weighted to the client-needs categories.", "NCLEX and NCLEX-RN are registered trademarks of NCSBN. FocusFlow Lab is not affiliated with or endorsed by NCSBN."),
    "nclex-pn-6-week-planner": ("the NCLEX-PN", "Weighted to the client-needs categories.", "NCLEX and NCLEX-PN are registered trademarks of the National Council of State Boards of Nursing (NCSBN). FocusFlow Lab is not affiliated with or endorsed by NCSBN."),
    "ati-teas-4-week-planner": ("the ATI TEAS", "Rough shares by section.", "TEAS and ATI are registered trademarks of Assessment Technologies Institute, LLC. FocusFlow Lab is not affiliated with or endorsed by ATI."),
    "naplex-8-week-planner": ("the NAPLEX", "Rough shares by competency area.", "NAPLEX is a registered trademark of the National Association of Boards of Pharmacy (NABP). FocusFlow Lab is not affiliated with or endorsed by NABP."),
    "pance-8-week-planner": ("the PANCE", "Rough shares by organ system.", "The PANCE is the Physician Assistant National Certifying Exam, run by the National Commission on Certification of Physician Assistants (NCCPA). FocusFlow Lab is not affiliated with or endorsed by the NCCPA."),
    "dat-10-week-planner": ("the DAT", "Rough shares by section.", "DAT is a program of the American Dental Association. FocusFlow Lab is not affiliated with or endorsed by the ADA."),
    "usmle-step-1-8-week-planner": ("USMLE Step 1", "Weighted to the content outline.", "USMLE is a joint program of the Federation of State Medical Boards (FSMB) and the National Board of Medical Examiners (NBME). FocusFlow Lab is not affiliated with or endorsed by either."),
    "gre-8-week-planner": ("the GRE", "Rough shares by area.", "GRE is a registered trademark of ETS. FocusFlow Lab is not affiliated with or endorsed by ETS."),
    "lsat-12-week-planner": ("the LSAT", "Rough shares by question type.", "LSAT is a registered trademark of the Law School Admission Council (LSAC). FocusFlow Lab is not affiliated with or endorsed by LSAC."),
    "gmat-8-week-planner": ("the GMAT", "Rough shares by section.", "GMAT is a registered trademark of the Graduate Management Admission Council (GMAC). FocusFlow Lab is not affiliated with or endorsed by GMAC."),
    "cpa-far-10-week-planner": ("the CPA Exam FAR section", "Rough shares by content area.", ""),
    "cpa-aud-8-week-planner": ("the CPA Exam AUD section", "Rough shares by content area.", ""),
    "cpa-reg-8-week-planner": ("the CPA Exam REG section", "Rough shares by content area.", ""),
    "mcat-16-week-planner": ("the MCAT", "A map of the exam.", "MCAT is a registered trademark of the AAMC. FocusFlow Lab is not affiliated with or endorsed by the AAMC."),
}
_CPA_TM = "CPA is a designation granted by state boards of accountancy. The Uniform CPA Examination is developed by the AICPA. FocusFlow Lab is not affiliated with or endorsed by the AICPA, NASBA or any board of accountancy."
CHECK = "The exam map shows rough shares of the exam. They are planning figures, so check the official outline for the current version."

def planner_detail(t):
    title, dur, blurb, link, plan, thumb = t
    is_bundle, is_sprint, is_mcat = t is BUNDLE, link == "exam-sprint-planner", link == "mcat-16-week-planner"
    path = f"/planners/{link}/"
    price = "$15" if is_bundle else "$5"
    weeks = re.match(r"(\d+)", dur).group(1) if not (is_bundle or is_sprint) else None
    for_, emap, tm = _FOR.get(link, ("", "", ""))
    tm = tm or (_CPA_TM if link.startswith("cpa-") else "Exam names belong to their owners. FocusFlow Lab is not affiliated with or endorsed by any exam owner.")
    if is_bundle:
        h1 = "All 14 Exam Study Planners Bundle"
        lead = "All 14 exam study planners in one purchase. Each has 9 pages, in A4 and US Letter, so you can print the one for your exam tonight."
        inside = [(i[0].replace(" Study Planner", ""), f"{i[1]} plan.") for i in ITEMS[1:]]
        desc = "All 14 exam study planners in one purchase for $15: NCLEX, TEAS, NAPLEX, MCAT, USMLE, PANCE, DAT, GRE, LSAT, GMAT and CPA. A4 and US Letter PDFs, 14-day refund."
        inside_h = "The 14 planners in the bundle"
    elif is_sprint:
        h1 = "Exam Sprint Planner (14 days)"
        lead = "A 14-day printable plan for the two weeks before your exams. Nine pages, in A4 and US Letter, ready to print tonight."
        inside = [("Exam map and priority grid", "Map the exam and set your priorities."), ("Sprint calendar", "Four focus blocks a day across the 14 days."),
                  ("Daily pages", "Each block ends with a self-test."), ("Active-recall tracker", "An active-recall tracker for your sprint.")]
        desc = "A printable 14-day plan for the two weeks before your exams: exam map, priority grid, four focus blocks a day. $5, A4 and Letter PDFs, 14-day refund."
        inside_h = "What is inside"
    else:
        h1 = title
        lead = f"{'An' if weeks == '8' else 'A'} {weeks}-week printable plan for {for_}. Nine pages, in A4 and US Letter, ready to print tonight."
        if is_mcat:
            lead = "A 16-week printable plan for the MCAT. Content review in the first half, full-length tests in the second, CARS every week. Nine pages, in A4 and US Letter."
            inside = [("Exam map", emap), (f"{weeks}-week overview", f"The whole plan across {weeks} weeks."), ("Weekly pages", "One page for each week."),
                      ("Daily focus pages", "Daily pages across the 16 weeks."), ("Full-length test log", "Record your section scores."),
                      ("Error log", "Write down the questions you missed."), ("Test-day checklist", "What to do and bring on the day.")]
        else:
            inside = [("Exam map", emap), (f"{weeks}-week overview", f"The whole plan across {weeks} weeks."), ("Weekly pages", "One page for each week."),
                      ("Daily focus pages", "Four focus blocks a day, with a self-test after each."),
                      ("Practice test log and error log", "Record your scores, and the questions you missed."), ("Test-day checklist", "What to do and bring on the day.")]
        desc = (f"Printable {weeks}-week plan for {for_}: exam map, weekly and daily pages, error log and test-day checklist. $5, A4 and Letter PDFs, 14-day refund."
                if not is_mcat else "Printable 16-week MCAT plan: content review first, full-length tests second, CARS every week. $5, A4 and Letter PDFs, 14-day refund.")
        inside_h = "What is inside"
    buy_text = "Get the bundle" if is_bundle else "Get the planner"
    cards = "\n".join(f'          <li><strong>{a}</strong>{b}</li>' for a, b in inside)
    if is_bundle:
        cards = "\n".join(f'          <li class="pd-link"><a href="/planners/{i[3]}/"><img src="/assets/products/planners/{i[5]}.png" alt="" width="96" height="96" loading="lazy" decoding="async"><span><strong>{i[0].replace(" Study Planner", "")}</strong>{i[1]} · $5 · See details</span></a></li>' for i in sorted(ITEMS[1:], key=lambda t: [n for n, _ in GROUPS].index(group_of(t))))
    day = "" if (is_bundle or is_mcat) else f'''
      <section class="pd-section pd-split" aria-labelledby="day-title">
        <div>
          <h2 id="day-title">Four focus blocks, each ending with a self-test</h2>
          <p>Each daily page splits your study time into four focus blocks. At the end of a block you test yourself before you move on, so you find the gaps while there is still time to fix them.</p>
        </div>
        <div class="sheet day-sheet" aria-label="A study day from the planner">
          <p class="sheet-title">Study day <span>focus blocks</span></p>
          <ol>
            <li><span class="n">01</span><strong>Focus block</strong><label><input type="checkbox"> Self-test</label></li>
            <li><span class="n">02</span><strong>Focus block</strong><label><input type="checkbox"> Self-test</label></li>
            <li><span class="n">03</span><strong>Focus block</strong><label><input type="checkbox"> Self-test</label></li>
            <li><span class="n">04</span><strong>Focus block</strong><label><input type="checkbox"> Self-test</label></li>
          </ol>
          <p class="foot">Four focus blocks a day, each ending with a self-test.</p>
        </div>
      </section>'''
    rel = RELATED.get(plan.strip("/").split("/")[-1], [])
    free_links = f'<a href="{plan}">free study plan for {for_}</a>' if plan.startswith("/study-plan/") and plan != "/study-plan/" else '<a href="/study-plan/">free study plan generators</a>'
    guides = "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in rel)
    sib = ITEMS[:3] if is_bundle else ([i for i in ITEMS if i[3] != link and group_of(i) == group_of(t)] + [i for i in ITEMS if i[3] != link and group_of(i) != group_of(t)])[:3]
    sibs = "\n".join(card(i) for i in sib)
    faq = [("What do I get?", FAQ[0][1])] if not (is_mcat or is_sprint or is_bundle) else [(
        "What do I get?", {"mcat-16-week-planner": "Two printable PDFs, A4 and US Letter, of 9 pages each: an exam map, a 16-week overview, weekly pages, daily focus pages, a full-length test log with section scores, an error log and a test-day checklist.",
                           "exam-sprint-planner": "Two printable PDFs, A4 and US Letter, of 9 pages each: an exam map and priority grid, a sprint calendar with four focus blocks a day, daily pages that end each block with a self-test, and an active-recall tracker."}.get(
            link, "All 14 exam-specific planners as A4 and US Letter PDFs. Each planner has 9 pages: an exam map, a week-by-week overview, weekly and daily focus pages, a practice test log, an error log and a test-day checklist."))]
    fx = None if (is_bundle or is_sprint) else planner_extra.facts(link, PLANNERS_MAP, EXAMS)
    if fx:
        faq += [(q, a) for q, a in fx["faq"]]
        extra = planner_extra.exam_sections(fx, link, for_)
    elif is_sprint:
        faq += planner_extra.SPRINT_FAQ
        extra = planner_extra.sprint_sections()
    else:
        extra = planner_extra.bundle_sections(ITEMS, PLANNERS_MAP, EXAMS)
    faq += FAQ[1:]
    faq_html = "\n".join(f"        <h3>{q}</h3>\n        <p>{a}</p>" for q, a in faq)
    note_exam = "" if (is_bundle or is_sprint) else f"        <p>{CHECK}</p>\n" if emap.startswith("Rough") else ""
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Planners", "/planners/"), (h1.replace(" (14 days)", ""), path)])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Product", "name": title if not is_sprint else "Exam Sprint Planner", "description": desc, "url": SITE + path,
         "image": f"{SITE}/assets/products/planners/{thumb}.png", "brand": {"@type": "Brand", "name": "FocusFlow Lab"},
         "offers": {"@type": "Offer", "price": "15.00" if is_bundle else "5.00", "priceCurrency": "USD", "availability": "https://schema.org/InStock",
                    "url": STORE + link, **OFFER_EXTRA}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        crumb_ld]}
    body = f"""{crumb_html}

    <main id="main">
      <section class="pd-hero wash">
        <div>
          <h1>{nowrap_first(h1)}</h1>
          <p class="lead">{lead}</p>
          <p class="muted byline">Plans by <a href="/about/">Ahsan Raza</a>, built from the official exam outlines.</p>
          <div class="pd-buy"><span class="pd-price">{price}</span><a class="btn" href="{STORE}{link}?wanted=true">{buy_text}</a><a class="btn btn-soft" href="{plan}">{"Free study plans" if is_bundle else "Try the free plan first"}</a></div>
          <ul class="pd-facts"><li>Instant download</li><li>A4 and US Letter PDFs</li><li>14-day no-questions refund</li></ul>
        </div>
        <img src="/assets/products/planners/{thumb}.png" alt="{title} cover" width="400" height="400" decoding="async">
      </section>

      <section class="pd-section" aria-labelledby="inside-title">
        <h2 id="inside-title">{inside_h}</h2>
        <ul class="pd-list">
{cards}
        </ul>
{note_exam}      </section>
{extra}
{day}
      <section class="pd-section reading" aria-labelledby="free-title">
        <h2 id="free-title">Use it with the free plan</h2>
        <div class="reading-body">
        <p>Not sure yet? Our {free_links} builds a week-by-week schedule from your test date and free hours, and the free <a href="/#free-kit">Study Focus Kit</a> includes a printable planner. The paid planner is the same system on paper, with logs and a checklist you can write on.</p>
{f'        <ul>{guides}</ul>' if guides else ''}
        </div>
      </section>

      <section class="pd-section reading faq" aria-labelledby="faq-title">
        <h2 id="faq-title">Questions people ask</h2>
        <div class="prose">
{faq_html}
        </div>
      </section>

{"" if is_bundle else f'''      <section class="pd-section" aria-labelledby="more-title">
        <h2 id="more-title">{"Or buy one at a time" if is_bundle else "More planners"}</h2>
        <ul class="pc-grid">
{sibs}
        </ul>
        <p class="pd-more">{"" if is_bundle else '<a href="/planners/all-exam-planners-bundle/">All 14 exam planners, $15</a> · '}<a href="/planners/">See every planner</a></p>
      </section>''' }
    </main>
    <aside class="page-note" aria-label="About this page">
      <p>{tm}</p>
      <p>Made by FocusFlow Lab. Questions: <a href="mailto:hello@thefocusflowlab.com">hello@thefocusflowlab.com</a>. Purchases are processed by Gumroad; see the <a href="/terms.html">terms</a> and <a href="/privacy.html">privacy policy</a>.</p>
    </aside>"""
    full_title = f"{h1.replace(' (14 days)', '')} ({'PDF' if len(h1) > 30 else 'Printable PDF'}) | FocusFlow Lab" if not is_bundle else "All 14 Exam Study Planners Bundle, $15 | FocusFlow Lab"
    return path, shell(path=path, title=full_title, desc=desc[:160].rsplit(" ", 1)[0] if len(desc) > 160 else desc, og_title=h1, ld=ld, body=body, css_depth=2, og_image=f"{SITE}/assets/products/planners/{thumb}.png",
                       extra_head='\n  <link rel="stylesheet" href="../../study-plan/assets/plan.css">')

def not_found_page():
    body = """    <main id="main">
      <header class="doc-head">
        <h1>Page not found</h1>
        <p class="lead">That page does not exist, or it has moved. Try one of these instead.</p>
      </header>
      <ul class="choose-grid">
        <li><strong>Free study plans</strong><p>Put in your test date and hours, get a week-by-week plan.</p><a class="text-link" href="/study-plan/">All study plans</a></li>
        <li><strong>Printable planners</strong><p>One planner per exam, $5 each or all 14 for $15.</p><a class="text-link" href="/planners/">All planners</a></li>
        <li><strong>Free tools and guides</strong><p>Calculators, timers and short study guides.</p><a class="text-link" href="/tools/">Study tools</a> <a class="text-link" href="/guides/">Study guides</a></li>
      </ul>
    </main>"""
    html = shell(path="/404.html", title="Page not found | FocusFlow Lab", desc="This page could not be found.", og_title="Page not found", ld={"@context": "https://schema.org", "@graph": []},
                 body=body, css_depth=0, extra_head='\n  <meta name="robots" content="noindex">')
    return html.replace('href="assets/', 'href="/assets/').replace('  <link rel="canonical" href="https://thefocusflowlab.com/404.html">\n', '')

pages = [("planners/index.html", planners_page()), ("about/index.html", about_page()), ("404.html", not_found_page())]
pages += [(planner_detail(t)[0].strip("/") + "/index.html", planner_detail(t)[1]) for t in ITEMS + [BUNDLE]]
for rel, html in pages:
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT).as_posix())

# Pinterest catalog feed (upload its URL in Pinterest Business > Catalogs); prices match Gumroad.
import csv
feed = ROOT / "feeds" / "pinterest-catalog.csv"
feed.parent.mkdir(exist_ok=True)
with feed.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "title", "description", "link", "image_link", "price", "availability", "condition", "brand"])
    for t in ITEMS + [BUNDLE]:
        price = "15.00 USD" if t is BUNDLE else "5.00 USD"
        w.writerow([t[3], t[0] + " (Printable PDF)", t[2] + " Printable PDF, A4 and US Letter. Instant download.", STORE + t[3], f"{SITE}/assets/products/planners/{t[5]}.png", price, "in stock", "new", "FocusFlow Lab"])
print("wrote", feed.relative_to(ROOT).as_posix())
