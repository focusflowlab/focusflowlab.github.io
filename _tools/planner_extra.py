"""Per-planner detail copy for /planners/<slug>/ pages: facts come from the exam configs
(exams.py EXAMS and the hand-built NCLEX and MCAT plan pages), so every page differs and nothing is invented.
Used by extra_pages.py."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = "These are rough planning figures, not official numbers: check the official exam outline for the current version."
HAND = {"nclex-rn-8-week-planner": ("nclex", 8, "NCLEX-RN", "The NCLEX-RN is a computerized adaptive test: it gives you between 85 and 150 questions in up to 5 hours, and the questions get harder or easier as you answer. The topics follow the client-needs categories of the NCSBN test plan."),
        "mcat-16-week-planner": ("mcat", 16, "MCAT", None)}


# Facts confirmed on official pages in Nov 2026; anything not confirmed is left out. Update when the owner changes the exam.
_AICPA = ("AICPA: what is tested on the CPA Exam", "https://www.aicpa-cima.com/resources/download/learn-what-is-tested-on-the-cpa-exam")
_CPA_SCORE = ("AICPA: CPA Exam scoring", "https://www.aicpa-cima.com/resources/article/learn-more-about-cpa-exam-scoring-and-pass-rates")
_CPA_COMMON = "Each section is 4 hours with two multiple-choice testlets and three task-based simulation testlets. It is scored 0 to 99, you need 75 to pass, and the score is not a percentage or a curve; multiple-choice and simulations count equally."
OFFICIAL = {
    "mcat-16-week-planner": (["230 questions in four sections: Chem/Phys 59 questions in 95 minutes, CARS 53 in 90 minutes, Bio/Biochem 59 in 95 minutes and Psych/Soc 59 in 95 minutes.",
                              "About 6 hours 15 minutes of testing, and about 7 hours 30 minutes in the seat with breaks.",
                              "You can take it up to 3 times in a testing year, 4 times over 2 consecutive years and 7 times in your lifetime."],
                             [("AAMC: what is on the MCAT exam", "https://students-residents.aamc.org/whats-mcat-exam/publication-chapters/whats-mcat-exam"), ("AAMC: testing attempt limits", "https://students-residents.aamc.org/register-mcat-exam/publication-chapters/testing-attempt-limits")]),
    "usmle-step-1-8-week-planner": (["Step 1 is one 8-hour test day. Since 14 May 2026 it runs as 30-minute blocks of up to 20 questions each; before that it was 60-minute blocks of up to 40.",
                                     "Step 1 has been reported pass or fail only since 26 January 2022."],
                                    [("USMLE: Step 1", "https://www.usmle.org/step-exams/step-1"), ("USMLE: examination results and scoring", "https://www.usmle.org/scores-transcripts/examination-results-and-scoring")]),
    "nclex-rn-8-week-planner": (["The NCLEX-RN gives you between 85 and 150 questions, with up to 5 hours to finish.",
                                 "You can retake it up to 8 times a year, at least 45 days apart, unless your jurisdiction sets a stricter limit."],
                                [("NCSBN: NCLEX candidate bulletin", "https://www.ncsbn.org/public-files/NCLEX_Examination_Candidate_Bulletin_April_2026.pdf")]),
    "cpa-far-10-week-planner": ([_CPA_COMMON + " FAR has 50 multiple-choice questions and 7 simulations.",
                                 "FAR content areas: Financial Reporting 30 to 40%, Select Balance Sheet Accounts 30 to 40%, Select Transactions 25 to 35%."],
                                [_AICPA, _CPA_SCORE, ("ThisWayToCPA: what every candidate should know about FAR", "https://www.thiswaytocpa.com/work-experience/articles/skill-development/going-farther-what-every-cpa-candidate-should-know-about-far/")]),
    "cpa-aud-8-week-planner": ([_CPA_COMMON + " AUD has 78 multiple-choice questions and 7 simulations."], [_AICPA, _CPA_SCORE]),
    "cpa-reg-8-week-planner": ([_CPA_COMMON + " REG has 72 multiple-choice questions and 8 simulations."], [_AICPA, _CPA_SCORE]),
    "ati-teas-4-week-planner": (["170 questions in 209 minutes across four sections: Reading 45 questions in 55 minutes, Math 38 in 57 minutes, Science 50 in 60 minutes and English and Language Usage 37 in 37 minutes.",
                                 "Some of those questions are unscored practice items, so not every question counts toward your score."],
                                [("ATI: TEAS exam details", "https://www.atitesting.com/teas/exam-details")]),
    "dat-10-week-planner": (["280 questions in four tests: Survey of the Natural Sciences 100, Perceptual Ability 90, Reading Comprehension 50 and Quantitative Reasoning 40.",
                             "There must be at least 60 days between attempts."],
                            [("ADA: Dental Admission Test", "https://www.ada.org/education/testing/exams/dental-admission-test-dat")]),
    "pance-8-week-planner": (["The current NCCPA blueprint took effect in January 2025. It gives one percentage per area, and says the shares may vary slightly on each exam."],
                             [("NCCPA: PANCE blueprint", "https://www.nccpa.net/become-certified/pance-blueprint/")]),
    "naplex-8-week-planner": (["225 questions in 6 hours, on the computer.", "Results are reported as pass or fail, with no numeric score."],
                              [("NABP: take the NAPLEX", "https://nabp.pharmacy/programs/examinations/naplex/take-the-naplex-exam/")]),
    "lsat-12-week-planner": (["Four sections of 35 minutes each with a 10-minute break after the second. Two Logical Reasoning sections and one Reading Comprehension section are scored, and the fourth is unscored.",
                              "Argumentative Writing is separate: 50 minutes in total, with 15 minutes of prewriting and 35 minutes of writing.",
                              "LSAC has announced the LSAT will change from August 2027, so check the current format before you test."],
                             [("LSAC: LSAT FAQs", "https://www.lsac.org/lsat/frequently-asked-questions-about-lsat"), ("LSAC: the 2027 LSAT change", "https://www.lsac.org/blog/starting-august-2027-lsat-will-look-little-different-still-test-same-skills-same-ways")]),
    "gre-8-week-planner": (["About 1 hour 58 minutes in five sections. Analytical Writing comes first: one task in 30 minutes.",
                            "Verbal Reasoning has two sections (12 questions in 18 minutes, then 15 in 23) and Quantitative Reasoning has two (12 questions in 21 minutes, then 15 in 26).",
                            "Verbal and Quant adapt at the section level: how you do on the first section sets the difficulty of the second."],
                           [("ETS: GRE General Test structure", "https://www.ets.org/gre/test-takers/general-test/prepare/test-structure.html")]),
    "gmat-8-week-planner": (["64 questions in 2 hours 15 minutes across three sections: Quantitative Reasoning, Verbal Reasoning and Data Insights.",
                             "You choose the section order, and you can review and change up to 3 answers in each section. The total score runs from 205 to 805."],
                            [("GMAC: GMAT Focus exam policies", "https://mba.com/exams/gmat-focus-edition/register/exam-policies")]),
    "nclex-pn-6-week-planner": (["The NCLEX-PN gives you between 85 and 205 questions, with up to 5 hours to finish.",
                                 "Retakes need at least 45 days between attempts, and some jurisdictions allow fewer attempts a year than the standard limit."],
                                [("NCSBN: NCLEX candidate bulletin", "https://www.ncsbn.org/public-files/NCLEX_Examination_Candidate_Bulletin_April_2026.pdf")]),
}


def official_block(link):
    if link not in OFFICIAL:
        return ""
    items, srcs = OFFICIAL[link]
    lis = "".join(f"<li>{i}</li>" for i in items)
    src = ", ".join(f'<a href="{u}" rel="noopener">{n}</a>' for n, u in srcs)
    return f'<h3 class="pd-sub">The exam at a glance</h3><ul class="pd-bullets">{lis}</ul><p class="pd-note">Checked against the official pages in November 2026; the exam owner can change these. Sources: {src}.</p>'


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
          {official_block(link)}
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
          <p>Each planner costs $5, so any three cost the same $15 as the bundle. The bundle starts saving you money from the fourth planner. It suits students who sit more than one exam, such as the three CPA sections plus another test, or anyone who is still deciding between exams. If you only need one exam, buy that planner on its own.</p>
        </div>
      </section>"""
