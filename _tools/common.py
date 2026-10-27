"""Shared page shell for generated pages (tools and guides)."""
import json

SITE = "https://thefocusflowlab.com"

def shell(*, path, title, desc, og_title, ld, body, css_depth, extra_head="", scripts=""):
    url = SITE + path
    up = "../" * css_depth
    return f"""<!doctype html>
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
  <meta property="og:image" content="{SITE}/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
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
"""

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

KIT_ASIDE = """      <aside class="kit" aria-label="Free Study Focus Kit">
        <div>
          <h2>Staying focused is the hard part.</h2>
          <p>The free Study Focus Kit has 5 printable worksheets for phone distractions, notes that stick and long study days, plus a free printable study planner.</p>
        </div>
        <a class="btn" href="/#free-kit">Get the free kit</a>
      </aside>"""


TRACKERS = {
    "nclex": ("Free NCLEX-RN 6-week tracker", "A printable test plan tracker for every client needs category, a weekly question log, an error log and a final-week checklist."),
    "mcat": ("Free MCAT 12-week tracker", "A printable tracker for all four sections, a practice exam score log, an error log and a final-week checklist."),
    "teas": ("Free ATI TEAS 4-week tracker", "A printable tracker for reading, math, science and English, a practice test log, an error log and a final-week checklist."),
}

def TRACKER_FORM(exam, indent="        "):
    title, text = TRACKERS[exam]
    html = f'''<aside class="sheet guide-kit tracker-offer" aria-label="{title}">
  <h2 class="tracker-title">{title}</h2>
  <p>{text} Enter your email and it arrives with the free Study Focus Kit.</p>
  <form class="kit-form" id="kit-form" action="https://assets.mailerlite.com/jsonp/2740917/forms/202322886786024656/subscribe" method="post" novalidate>
    <label for="kit-email">Email address</label>
    <div class="kit-row">
      <input type="email" id="kit-email" name="fields[email]" autocomplete="email" required placeholder="you@example.com" aria-describedby="kit-status">
      <button class="btn" type="submit">Send me the tracker</button>
    </div>
    <div class="kit-trap" aria-hidden="true"><label for="kit-website">Leave this empty</label><input type="text" id="kit-website" name="website" tabindex="-1" autocomplete="off"></div>
    <input type="hidden" name="ml-submit" value="1">
    <input type="hidden" name="anticsrf" value="true">
    <p class="kit-status" id="kit-status" role="status" aria-live="polite"></p>
  </form>
  <p class="form-note">You’ll also get a few study emails and occasional planner news. Unsubscribe any time. <a href="/privacy.html#focusflow-lab-email-list-and-shop">How we use your email</a>.</p>
</aside>'''
    return "\n".join(indent + l for l in html.splitlines())
