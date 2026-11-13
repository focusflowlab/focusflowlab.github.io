"""Shared page shell for generated pages (tools and guides)."""
import json
from prices import fill

SITE = "https://thefocusflowlab.com"

def shell(*, path, title, desc, og_title, ld, body, css_depth, extra_head="", scripts="", og_image=None, signup=True):
    url = SITE + path
    if signup and 'id="kit-form"' not in body:  # every new page gets the kit signup unless it opts out; page_guard.py checks
        body = body.replace("</main>", KIT_FORM("      ") + "\n    </main>", 1) if "</main>" in body else body + "\n" + KIT_FORM("    ")
    img, iw, ih, card = (og_image, 400, 400, "summary") if og_image else (f"{SITE}/assets/og-image.png", 1200, 630, "summary_large_image")
    up = "../" * css_depth
    return fill(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="FocusFlow Lab">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{img}">
  <meta property="og:image:width" content="{iw}">
  <meta property="og:image:height" content="{ih}">
  <meta name="twitter:card" content="{card}">
  <link rel="icon" href="/assets/icon-64.png" type="image/png">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/bricolage-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/plex-sans.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{up}assets/site.css">{extra_head}
  <script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
  </script>
</head>
<body>
<!-- site-head --><!-- /site-head -->
  <div class="container">
{body}
  </div>

<!-- site-foot --><!-- /site-foot -->{scripts}
</body>
</html>
""")

def crumbs(items):
    """items: list of (name, path). Returns (html, BreadcrumbList)."""
    parts = []
    for i, (name, path) in enumerate(items):
        parts.append(name if i == len(items) - 1 else f'<a href="{path}">{name}</a>')
    html = '    <nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"
    ld = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": "FocusFlow Lab" if i == 0 else n, "item": SITE + p} for i, (n, p) in enumerate(items)]}
    return html, ld

ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "FocusFlow Lab", "url": SITE + "/"}



TRACKERS = {
    "nclex": ("Free NCLEX-RN 6-week tracker", "A printable test plan tracker for every client needs category, a weekly question log, an error log and a final-week checklist."),
    "mcat": ("Free MCAT 12-week tracker", "A printable tracker for all four sections, a practice exam score log, an error log and a final-week checklist."),
    "teas": ("Free ATI TEAS 4-week tracker", "A printable tracker for reading, math, science and English, a practice test log, an error log and a final-week checklist."),
    # names and pages match focusflowlab-products/build_more_trackers.py
    "nclex-pn": ("Free NCLEX-PN 6-week tracker", "A printable test plan tracker for every client needs category, a question bank log, an error log and a final-week checklist."),
    "usmle-step-1": ("Free USMLE Step 1 8-week tracker", "A printable tracker for every organ system, a question bank log, an error log and a final-week checklist."),
    "pance": ("Free PANCE 8-week tracker", "A printable tracker for every organ system on the blueprint, a question bank log, an error log and a final-week checklist."),
    "naplex": ("Free NAPLEX 8-week tracker", "A printable tracker for every content domain, a question bank log, an error log and a final-week checklist."),
    "dat": ("Free DAT 10-week tracker", "A printable tracker for every DAT section, including perceptual ability, a practice test score log, an error log and a final-week checklist."),
    "gre": ("Free GRE 8-week tracker", "A printable tracker for verbal, quant and writing topics, a practice test score log, an error log and a final-week checklist."),
    "gmat": ("Free GMAT 8-week tracker", "A printable tracker for quant, verbal and data insights, a practice test score log, an error log and a final-week checklist."),
    "lsat": ("Free LSAT 12-week tracker", "A printable tracker for every reasoning and reading question type, a timed practice log, an error log and a final-week checklist."),
    "cpa-far": ("Free CPA FAR 10-week tracker", "A printable tracker for every FAR content area, a practice log for multiple choice and simulations, an error log and a final-week checklist."),
    "cpa-aud": ("Free CPA AUD 8-week tracker", "A printable tracker for every AUD content area, a practice log for multiple choice and simulations, an error log and a final-week checklist."),
    "cpa-reg": ("Free CPA REG 8-week tracker", "A printable tracker for every REG content area, a practice log for multiple choice and simulations, an error log and a final-week checklist."),
}

TRACKER_EXAM = {"nclex": "NCLEX-RN", "mcat": "MCAT", "teas": "ATI TEAS", "nclex-pn": "NCLEX-PN", "usmle-step-1": "USMLE Step 1",
                "pance": "PANCE", "naplex": "NAPLEX", "dat": "DAT", "gre": "GRE", "gmat": "GMAT", "lsat": "LSAT",
                "cpa-far": "CPA FAR", "cpa-aud": "CPA AUD", "cpa-reg": "CPA REG"}

def TRACKER_FORM(exam, indent="        "):
    title, text = TRACKERS[exam]
    return SIGNUP_FORM(title, f"{text} Enter your email and it arrives with the free Study Focus Kit.", "Send me the tracker",
                       f'\n      <input type="hidden" name="fields[exam]" value="{TRACKER_EXAM[exam]}">', indent)

def KIT_FORM(indent="        "):
    return SIGNUP_FORM("Free Study Focus Kit", "One printable PDF with five worksheets: phone distractions, notes that stick, mental clutter, long study days and covering your syllabus. Enter your email and it arrives in your inbox.",
                       "Send me the kit", "", indent)

def SIGNUP_FORM(title, text, cta, exam_field, indent):
    html = f'''<aside class="sheet tracker-offer" aria-label="{title}">
  <div class="tracker-copy">
    <h2 class="tracker-title">{title}</h2>
    <p>{text}</p>
  </div>
  <div class="tracker-action">
    <form class="kit-form" id="kit-form" action="https://assets.mailerlite.com/jsonp/2740917/forms/202322886786024656/subscribe" method="post" novalidate>
      <label for="kit-email">Email address</label>
      <div class="kit-row">
        <input type="email" id="kit-email" name="fields[email]" autocomplete="email" required placeholder="you@example.com" aria-describedby="kit-status">
        <button class="btn" type="submit">{cta}</button>
      </div>
      <div class="kit-trap" aria-hidden="true"><label for="kit-website">Leave this empty</label><input type="text" id="kit-website" name="website" tabindex="-1" autocomplete="off"></div>{exam_field}
      <input type="hidden" name="ml-submit" value="1">
      <input type="hidden" name="anticsrf" value="true">
      <p class="kit-status" id="kit-status" role="status" aria-live="polite"></p>
    </form>
    <p class="form-note">You’ll also get a few study emails and occasional planner news. Unsubscribe any time. <a href="/privacy.html#focusflow-lab-email-list-and-shop">How we use your email</a>.</p>
  </div>
</aside>'''
    return "\n".join(indent + l for l in html.splitlines())
