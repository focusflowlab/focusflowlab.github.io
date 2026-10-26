"""Copy the shared header and footer into every page.

Run from the repo root:  python _tools/build.py
Each page marks the spots with <!-- site-head --><!-- /site-head --> and
<!-- site-foot --><!-- /site-foot -->. The nav link for the current section
gets aria-current="page".
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
head = (ROOT / "_partials/site-head.html").read_text(encoding="utf-8").strip()
foot = (ROOT / "_partials/site-foot.html").read_text(encoding="utf-8").strip()

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
        continue
    url = url_of(page)
    h = head
    for section in ("/study-plan/", "/tools/", "/guides/"):
        if url.startswith(section):
            h = h.replace(f'<a href="{section}">', f'<a href="{section}" aria-current="page">')
    html = re.sub(r"<!-- site-head -->.*?<!-- /site-head -->", lambda m: f"<!-- site-head -->\n{h}\n<!-- /site-head -->", html, flags=re.S)
    html = re.sub(r"<!-- site-foot -->.*?<!-- /site-foot -->", lambda m: f"<!-- site-foot -->\n{foot}\n<!-- /site-foot -->", html, flags=re.S)
    page.write_text(html, encoding="utf-8", newline="\n")
    print("built", url)
