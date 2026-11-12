"""Generate /exam-facts/: exam formats at a glance, from the checked facts in planner_extra.OFFICIAL.
Run: cd _tools && python exam_facts.py && cd .. && python _tools/build.py"""
import pathlib, json
from common import shell, crumbs, ORG, SITE
from planner_extra import OFFICIAL

ROOT = pathlib.Path(__file__).resolve().parent.parent
# key in OFFICIAL, exam name, free plan, planner page
EXAMS = [("nclex-rn-8-week-planner", "NCLEX-RN", "nclex"), ("nclex-pn-6-week-planner", "NCLEX-PN", "nclex-pn"),
         ("ati-teas-4-week-planner", "ATI TEAS", "teas"), ("mcat-16-week-planner", "MCAT", "mcat"),
         ("usmle-step-1-8-week-planner", "USMLE Step 1", "usmle-step-1"), ("pance-8-week-planner", "PANCE", "pance"),
         ("naplex-8-week-planner", "NAPLEX", "naplex"), ("dat-10-week-planner", "DAT", "dat"),
         ("gre-8-week-planner", "GRE", "gre"), ("gmat-8-week-planner", "GMAT", "gmat"), ("lsat-12-week-planner", "LSAT", "lsat"),
         ("cpa-far-10-week-planner", "CPA FAR", "cpa-far"), ("cpa-aud-8-week-planner", "CPA AUD", "cpa-aud"), ("cpa-reg-8-week-planner", "CPA REG", "cpa-reg")]

path = "/exam-facts/"
crumb_html, crumb_ld = crumbs([("Home", "/"), ("Exam facts", path)])
desc = "Question counts, test length and scoring for 14 exams, with retake rules where the owner publishes them (NCLEX, MCAT, USMLE, GRE, LSAT, CPA and more), checked against each exam owner’s official page."
secs, toc = [], []
for key, name, slug in EXAMS:
    items, srcs = OFFICIAL[key]
    lis = "".join(f"<li>{i}</li>" for i in items)
    src = ", ".join(f'<a href="{u}" rel="noopener">{n}</a>' for n, u in srcs)
    sid = slug
    toc.append(f'          <li><a href="#{sid}">{name}</a></li>')
    secs.append(f'''        <h2 id="{sid}">{name}</h2>
        <ul>{lis}</ul>
        <p>Sources: {src}. Make a schedule with the free <a href="/study-plan/{slug}/">{name} study plan generator</a>.</p>''')
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebPage", "name": "Exam formats at a glance", "url": SITE + path, "description": desc, "publisher": ORG, "datePublished": "2026-11-10", "dateModified": "2026-11-12"},
    crumb_ld]}
body = f"""{crumb_html}

    <main id="main">
      <header class="doc-head guide-head">
        <span class="card-tag">Reference</span>
        <h1>Exam formats at a glance: questions, time and retakes</h1>
        <p class="lead">What each exam owner publishes about test length, structure and scoring, for 14 exams in one place.</p>
        <p>By FocusFlow Lab. Checked against the official pages in November 2026.</p>
      </header>
      <div class="doc">
        <nav class="toc" aria-label="On this page">
          <p>On this page</p>
          <ol>
{chr(10).join(toc)}
          </ol>
        </nav>
        <article class="prose">
        <p>Exam owners change formats, so treat this page as a starting point and confirm on the official site before you book. Each section links to its sources. FocusFlow Lab is independent of every exam owner listed here. To turn a test length into minutes per question, use the <a href="/tools/test-time-calculator/">test time calculator</a>. For how long people usually prepare, see <a href="/guides/how-long-to-study-for-exams/">how long to study for each exam</a>.</p>
{chr(10).join(secs)}
        </article>
      </div>
    </main>"""
out = ROOT / "exam-facts" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(shell(path=path, title="Exam Formats at a Glance: Questions, Time, Retakes", desc=desc, og_title="Exam formats at a glance", ld=ld, body=body, css_depth=1), encoding="utf-8", newline="\n")
print("wrote", out)
