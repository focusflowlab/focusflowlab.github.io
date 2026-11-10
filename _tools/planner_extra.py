"""Per-planner detail copy for /planners/<slug>/ pages: facts come from the exam configs
(exams.py EXAMS and the hand-built NCLEX and MCAT plan pages), so every page differs and nothing is invented.
Used by extra_pages.py."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = "These are rough planning figures, not official numbers: check the official exam outline for the current version."
HAND = {"nclex-rn-8-week-planner": ("nclex", 8, "NCLEX-RN", "The NCLEX-RN is a computerized adaptive test: it gives you between 85 and 150 questions in up to 5 hours, and the questions get harder or easier as you answer. The topics follow the client-needs categories of the NCSBN test plan."),
        "mcat-16-week-planner": ("mcat", 16, "MCAT", None)}


def _first_p(html):
    return re.search(r"<p>(.*?)</p>", html, re.S).group(1).strip()


def facts(link, planners, exams):
    """Return dict(weeks, topics, hrs, review, intro, faq) for an exam planner, else None."""
    slug = next((s for s, (w, l) in planners.items() if l == link), None)
    if slug:
        e = exams[slug]
        h = e["config"]["recommendedHours"]
        return dict(weeks=planners[slug][0], topics=e["topics"], hrs=(h["min"], h["max"]), review=e["config"]["reviewShare"],
                    intro=_first_p(e["how"]), faq=e["faq"], short=e["short"])
    if link in HAND:
        page, weeks, short, intro = HAND[link]
        h = (ROOT / f"study-plan/{page}/index.html").read_text(encoding="utf-8")
        topics = [(n, int(w)) for n, w in re.findall(r"name: '([^']+)', weight: (\d+)", h)]
        m = re.search(r"recommendedHours: \{ min: (\d+), max: (\d+) \}", h)
        rv = float(re.search(r"reviewShare: ([\d.]+)", h).group(1))
        faq = [(q, re.sub(r"<[^>]+>", "", a).strip()) for q, a in re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", h, re.S)][:2]
        if intro is None:
            intro = re.search(r"<p>(The MCAT has four scored sections.*?)</p>", h, re.S).group(1)
        return dict(weeks=weeks, topics=topics, hrs=(int(m.group(1)), int(m.group(2))), review=rv, intro=intro, faq=faq, short=short)
    return None


def _span(a, b):
    return f"Week {a}" if a == b else f"Weeks {a} to {b}"


def exam_sections(f, link, for_):
    w = f["weeks"]
    rv = max(1, min(w - 1, round(w * f["review"])))
    lo, hi = f["hrs"]
    per = f"{max(1, round(lo / w))} to {round(hi / w)}"
    rows = "".join(f"<tr><th scope=\"row\">{n}</th><td>{p}%</td></tr>" for n, p in f["topics"])
    note = "" if link == "mcat-16-week-planner" else f"<p class=\"pd-note\">{CHECK}</p>"
    extra_mcat = "<li><strong>CARS every week.</strong> Keep a little CARS practice in every week, because it is a skill that fades if you leave it.</li>" if link == "mcat-16-week-planner" else ""
    mc = link == "mcat-16-week-planner"
    col = "Share of the exam score" if mc else "Rough share of study time"
    lead_in = "The four sections are scored equally, so the planner gives each one a full share of your time:" if mc else "These are the rough shares the planner works from:"
    blocks = "the daily pages give you a page for each study day" if link == "mcat-16-week-planner" else "the daily pages split each study day into four focus blocks that end with a self-test"
    return f"""
      <section class="pd-section reading" aria-labelledby="about-title">
        <h2 id="about-title">About {for_}</h2>
        <div class="reading-body">
          <p>{f['intro']}</p>
          <p>This {w}-week planner turns that into a calendar you can write on: the weekly overview shows the whole plan, and {blocks}.</p>
        </div>
      </section>

      <section class="pd-section reading" aria-labelledby="weeks-title">
        <h2 id="weeks-title">How to use the {w} weeks</h2>
        <div class="reading-body">
          <ul class="pd-steps">
            <li><strong>{_span(1, rv)}: content review.</strong> Take one or two topics a day and finish each day with practice questions on what you covered.</li>
            <li><strong>{_span(rv + 1, w)}: practice and review.</strong> Move to timed sets and full practice tests, write every miss in the error log, and keep going back to your weakest areas.</li>
            {extra_mcat}<li><strong>The last days.</strong> Work through the test-day checklist and keep the final day light.</li>
          </ul>
        </div>
      </section>

      <section class="pd-section reading" aria-labelledby="hours-title">
        <h2 id="hours-title">Where the study hours go</h2>
        <div class="reading-body">
          <p>The exam map splits your time across the areas of the exam. {lead_in}</p>
          <table class="pd-table"><thead><tr><th scope="col">Area</th><th scope="col">{col}</th></tr></thead><tbody>{rows}</tbody></table>
          {note}
          <p>Most people planning for {for_} put in about {lo} to {hi} hours in total, which is roughly {per} hours a week over {w} weeks. That is a planning range, not an official figure: start from your own score and target.</p>
        </div>
      </section>"""


def sprint_sections():
    return """
      <section class="pd-section reading" aria-labelledby="weeks-title">
        <h2 id="weeks-title">How to use the 14 days</h2>
        <div class="reading-body">
          <ul class="pd-steps">
            <li><strong>Day 1: map and priorities.</strong> Write down every topic the exam covers, then rank them by how much of the exam they are and how shaky you feel on each.</li>
            <li><strong>Days 2 to 11: work down the list.</strong> Four focus blocks a day, each ending with a self-test. Spend the most blocks on heavy topics you are weak on.</li>
            <li><strong>Days 12 and 13: fix the gaps.</strong> Redo the questions you missed and use the active-recall tracker to see what has not stuck.</li>
            <li><strong>Day 14: stay light.</strong> A short review and your test-day preparation. New material now costs more than it gives.</li>
          </ul>
        </div>
      </section>

      <section class="pd-section reading" aria-labelledby="sprint-title">
        <h2 id="sprint-title">When a sprint is the right plan</h2>
        <div class="reading-body">
          <p>Use it when your exam is two weeks away or less, when several exams fall close together, or when you have already studied and need a tight final stretch. It will not replace months of preparation. If your exam is further out, the <a href="/planners/">exam-specific planners</a> give you a longer, week-by-week plan.</p>
        </div>
      </section>"""


SPRINT_FAQ = [("Is 14 days enough to study for an exam?", "It depends on your starting point and the exam. Two weeks is enough to focus what you already know and close the biggest gaps, but not to learn a whole subject from scratch. Be honest about where you are on day 1."),
              ("What if my exam is more than two weeks away?", "Use the planner built for your exam, which spreads the work over 4 to 16 weeks, or start with the free study plan generator for your exam.")]


def bundle_sections(items, planners, exams):
    rows = ""
    for t in items[1:]:
        f = facts(t[3], planners, exams)
        hrs = f"{f['hrs'][0]} to {f['hrs'][1]}" if f else "-"
        rows += f"<tr><th scope=\"row\"><a href=\"/planners/{t[3]}/\">{t[0].replace(' Study Planner', '')}</a></th><td>{t[1]}</td><td>{hrs}</td></tr>"
    return f"""
      <section class="pd-section reading" aria-labelledby="table-title">
        <h2 id="table-title">What each planner covers</h2>
        <div class="reading-body">
          <p>Every planner has the same nine-page layout, with the exam map, plan length and topics set for that exam. Open any of them to see the details.</p>
          <table class="pd-table"><thead><tr><th scope="col">Planner</th><th scope="col">Plan length</th><th scope="col">Typical total hours</th></tr></thead><tbody>{rows}</tbody></table>
          <p class="pd-note">Hours are rough planning ranges for each exam, not official figures.</p>
        </div>
      </section>

      <section class="pd-section reading" aria-labelledby="worth-title">
        <h2 id="worth-title">Is the bundle worth it?</h2>
        <div class="reading-body">
          <p>Each planner costs $5, so the bundle pays for itself once you need three. It suits students who sit more than one exam, such as the three CPA sections, or anyone who is still deciding between exams. If you only need one exam, buy that planner on its own.</p>
        </div>
      </section>"""
