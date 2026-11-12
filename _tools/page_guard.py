"""Fail loudly when a public page is missing what every page needs.

Run: python _tools/page_guard.py [root]   (build.py runs it last; exit code 1 on any problem)
"""
import pathlib, re, sys

# Pages that may skip the signup form, with the reason.
NO_SIGNUP = {
    "/404.html": "error page",
    "/privacy.html": "legal page",
    "/terms.html": "legal page",
    "/publisher/privacy/": "legal page for the TikTok app",
    "/publisher/terms/": "legal page for the TikTok app",
    "/about/": "about page links to the kit instead",
    "/planners/": "shop page, Buy buttons are the call to action",
    "/exam-facts/": "reference table",
}
NO_SITEMAP = {"/404.html": "error page"}
BANNED = re.compile(r"\bAI\b|artificial intelligence|ChatGPT|\bLLM\b|Lahore|Pakistan", re.I)


def url_of(root, path):
    rel = path.relative_to(root).as_posix()
    return "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)


def visible_text(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


def check(root):
    root = pathlib.Path(root)
    sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
    problems = []
    for page in sorted(root.rglob("*.html")):
        if any(part.startswith(("_", ".")) for part in page.relative_to(root).parts):
            continue
        html = page.read_text(encoding="utf-8")
        if "<!-- site-head -->" not in html:
            continue  # embeds, verification files and other non-site pages
        url = url_of(root, page)
        planner = url.startswith("/planners/") and url != "/planners/"
        miss = []
        if not re.search(r"<title>[^<]{5,}</title>", html): miss.append("title")
        if not re.search(r'<meta name="description" content="[^"]{20,}"', html): miss.append("meta description")
        if 'rel="canonical"' not in html and url not in NO_SITEMAP: miss.append("canonical")
        if 'class="site-nav' not in html and "<nav" not in html: miss.append("nav")
        if url not in NO_SITEMAP and f"/{url.lstrip('/')}</loc>" not in sitemap and not 'noindex' in html: miss.append("sitemap entry")
        if url not in NO_SIGNUP and not planner and 'id="kit-form"' not in html: miss.append("signup form (or add to NO_SIGNUP with a reason)")
        if url.startswith(("/study-plan/", "/guides/")) and url.count("/") > 2 and 'href="/study-plan/' not in html: miss.append("link to /study-plan/ hub")
        m = BANNED.search(visible_text(html))
        if m: miss.append(f"banned text {m.group(0)!r}")
        if miss:
            problems.append(f"{url}: missing/bad -> {', '.join(miss)}")
    return problems


if __name__ == "__main__":
    probs = check(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent)
    for p in probs:
        print("PAGE GUARD FAIL", p)
    print(f"PAGE GUARD: {len(probs)} problem page(s)" if probs else "PAGE GUARD: OK")
    sys.exit(1 if probs else 0)
