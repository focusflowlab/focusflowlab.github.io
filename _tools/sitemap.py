"""Write sitemap.xml. Run by build.py (or alone from the repo root: python _tools/sitemap.py).

Pages: every .html page whose canonical link points at itself and that is not noindex (so embeds, 404 and
publisher pages stay out), plus the Jekyll guides in _guides/ (permalink /guides/<name>/).
lastmod: the date of the last commit that really changed the page's source file. Commits that only changed
?v=<hash> asset stamps are ignored. A source with real uncommitted changes gets today's date.
No date is ever invented: a file git does not know yet gets today's date only if it exists on disk now.
"""
import pathlib, re, subprocess, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://thefocusflowlab.com"
STAMP = re.compile(r"\?v=[0-9a-f]+")
CANON = re.compile(r'<link rel="canonical" href="https://thefocusflowlab\.com(/[^"]*)"')


def git(*args):
    return subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def pages():
    out = {}
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT).as_posix()
        if any(part.startswith(("_", ".")) for part in p.relative_to(ROOT).parts):
            continue
        html = p.read_text(encoding="utf-8", errors="replace")
        url = "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)
        m = CANON.search(html)
        if not m or m.group(1) != url or re.search(r'<meta name="robots" content="[^"]*noindex', html):
            continue
        out[rel] = url
    for p in sorted((ROOT / "_guides").glob("*.md")):
        out[p.relative_to(ROOT).as_posix()] = f"/guides/{p.stem}/"
    return out


SHARED = re.compile(r"<!-- (site-head|site-foot) -->.*?<!-- /\1 -->", re.S)


def norm(text):
    """Page content without the shared header/footer (copied into every page by build.py) and asset stamps."""
    return STAMP.sub("", SHARED.sub("", text)).replace("\r\n", "\n").strip()


def last_dates(paths):
    """Per path: date of the newest commit whose normalised content differs from the version before it."""
    history, date = {p: [] for p in paths}, None
    for line in git("log", "--format=@@@%H %cs", "--name-only", "--no-renames", "--", *paths).splitlines():
        if line.startswith("@@@"):
            sha, date = line[3:].split()
        elif line in history:
            history[line].append((sha, date))
    cat = subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def blob(sha, path):
        cat.stdin.write(f"{sha}:{path}\n".encode()); cat.stdin.flush()
        head = cat.stdout.readline().split()
        if head[-1] == b"missing":
            return None  # deleted in that commit
        data = cat.stdout.read(int(head[2])); cat.stdout.read(1)
        return data.decode("utf-8", "replace")

    today, dates = datetime.date.today().isoformat(), {}
    for p in paths:
        versions = [(today, (ROOT / p).read_text(encoding="utf-8", errors="replace"))]
        for sha, d in history[p]:
            text = blob(sha, p)
            versions.append((d, "" if text is None else text))
        dates[p] = versions[-1][0]  # only one version: when it was created
        for (d, a), (_, b) in zip(versions, versions[1:]):
            if norm(a) != norm(b):
                dates[p] = d
                break
    cat.stdin.close(); cat.wait()
    return dates


def main():
    src = pages()
    dates = last_dates(list(src))
    rows = sorted((url, dates[p]) for p, url in src.items())
    assert len({u for u, _ in rows}) == len(rows), "duplicate URL"
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in rows]
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8", newline="\n")
    print(f"sitemap.xml: {len(rows)} URLs")


if __name__ == "__main__":
    main()
