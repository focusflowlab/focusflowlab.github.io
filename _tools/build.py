"""Copy the shared header and footer into every page.

Run from the repo root:  python _tools/build.py
Each page marks the spots with <!-- site-head --><!-- /site-head --> and
<!-- site-foot --><!-- /site-foot -->. The nav link for the current section
gets aria-current="page".
"""
import pathlib, re, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

ASSET = re.compile(r'(href|src)="([^"#:?]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"')

def version_assets(html, base):
    """Add ?v=<hash of the file> to local css/js links so a changed file is never served from a stale browser cache (GitHub Pages caches 10 min).
    Re-run this script after editing any css or js file; the tag only changes when the file's contents change."""
    def one(m):
        ref = m.group(2)
        f = (ROOT / ref.lstrip("/")) if ref.startswith("/") else (base / ref).resolve()
        if not f.is_file():
            return m.group(0)
        return f'{m.group(1)}="{ref}?v={hashlib.sha1(f.read_bytes()).hexdigest()[:8]}"'
    return ASSET.sub(one, html)
head = (ROOT / "_partials/site-head.html").read_text(encoding="utf-8").strip()
foot = (ROOT / "_partials/site-foot.html").read_text(encoding="utf-8").strip()

HUB = {"/planners/": "← All planners", "/study-plan/": "← All study plans", "/tools/": "← All study tools", "/guides/": "← All study guides"}

def url_of(path):
    rel = path.relative_to(ROOT).as_posix()
    return "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)

pages = [p for p in ROOT.rglob("*.html") if not any(part.startswith(("_", ".")) for part in p.relative_to(ROOT).parts)]
# Jekyll layouts (auto-published guides) include the same header and footer.
(ROOT / "_includes").mkdir(exist_ok=True)
(ROOT / "_includes/site-head.html").write_text(head + "\n", encoding="utf-8", newline="\n")
(ROOT / "_includes/site-foot.html").write_text(foot + "\n", encoding="utf-8", newline="\n")

for page in pages:
    html = page.read_text(encoding="utf-8")
    if "<!-- site-head -->" not in html:
        versioned = version_assets(html, page.parent)
        if versioned != html:
            page.write_text(versioned, encoding="utf-8", newline="\n")
        continue
    url = url_of(page)
    h = head
    f = foot
    for section in ("/planners/", "/study-plan/", "/tools/", "/guides/"):
        if url.startswith(section):
            h = h.replace(f'href="{section}" aria-expanded', f'href="{section}" aria-current="page" aria-expanded')
            if url != section:
                f = f'<nav class="container hub-link{" hub-float" if section == "/planners/" else ""}" aria-label="Back to section"><a href="{section}">{HUB[section]}</a></nav>' + chr(10) + foot
    html = re.sub(r"<!-- site-head -->.*?<!-- /site-head -->", lambda m: f"<!-- site-head -->\n{h}\n<!-- /site-head -->", html, flags=re.S)
    html = re.sub(r"<!-- site-foot -->.*?<!-- /site-foot -->", lambda m: f"<!-- site-foot -->\n{f}\n<!-- /site-foot -->", html, flags=re.S)
    page.write_text(version_assets(html, page.parent), encoding="utf-8", newline="\n")
    print("built", url)

# Jekyll layouts and includes (guides) get the same tags; their links are absolute.
for tpl in [*(ROOT / "_layouts").glob("*.html"), *(ROOT / "_includes").glob("*.html")]:
    text = tpl.read_text(encoding="utf-8")
    versioned = version_assets(text, tpl.parent)
    if versioned != text:
        tpl.write_text(versioned, encoding="utf-8", newline="\n")
