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

KIT_ASIDE = """      <aside class="kit">
        <div>
          <h2>Staying focused is the hard part.</h2>
          <p>The free Study Focus Kit has 5 printable worksheets for phone distractions, notes that stick and long study days.</p>
        </div>
        <a class="btn" href="/#free-kit">Get the free kit</a>
      </aside>"""
