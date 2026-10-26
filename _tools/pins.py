"""Build Pinterest pin pages (1000x1500) in the site style, then screenshot them.

  python _tools/pins.py            # writes _pins/*.html
  node _tools/pin-shots.mjs        # renders assets/pins/*.png (needs puppeteer-core)

Each pin: a headline, one line, a visual (product mockup, tool sketch or page list) and the URL.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_pins"
OUT.mkdir(exist_ok=True)

PINS = [
  # slug, board, title (pin), headline, line, visual kind, visual data, link
  dict(slug="nclex-rn-plan", board="Exam Study Plans", headline="Your NCLEX-RN study plan, week by week", line="Free generator. Put in your test date and hours.", kind="weeks", data=["Content review", "Content review", "Practice + review", "Practice + review", "Final week"], link="/study-plan/nclex/",
       title="Free NCLEX-RN Study Plan Generator", desc="Put in your NCLEX-RN date and the hours you have, get a week-by-week plan weighted to the client-needs categories. Free, prints cleanly."),
  dict(slug="nclex-pn-plan", board="Exam Study Plans", headline="NCLEX-PN study plan in a minute", line="Weighted to the PN test plan. Free and printable.", kind="weeks", data=["Content review", "Content review", "Mixed questions", "Mixed questions", "Final week"], link="/study-plan/nclex-pn/",
       title="Free NCLEX-PN Study Plan Generator", desc="A free week-by-week NCLEX-PN plan built from your exam date and free hours, with extra time on the areas you feel shaky in."),
  dict(slug="mcat-plan", board="Exam Study Plans", headline="Plan your MCAT prep week by week", line="All four sections. CARS every week.", kind="weeks", data=["Content review", "Content review", "Full-length + review", "Full-length + review", "Final week"], link="/study-plan/mcat/",
       title="Free MCAT Study Schedule Generator", desc="A free MCAT schedule across Chem/Phys, CARS, Bio/Biochem and Psych/Soc, with full-length tests in the weeks they belong."),
  dict(slug="usmle-plan", board="Exam Study Plans", headline="Your Step 1 dedicated period, planned", line="Systems-based, with daily question blocks.", kind="weeks", data=["Systems review", "Systems review", "Mixed blocks", "Self-assessment", "Final week"], link="/study-plan/usmle-step-1/",
       title="Free USMLE Step 1 Study Schedule Generator", desc="Plan your USMLE Step 1 dedicated period: systems-based review, daily timed question blocks and self-assessments in the right weeks."),
  dict(slug="gre-plan", board="Exam Study Plans", headline="GRE prep, laid out week by week", line="Verbal, quant and the essay. Free.", kind="weeks", data=["Quant + verbal review", "Quant + verbal review", "Timed sections", "Practice test", "Final week"], link="/study-plan/gre/",
       title="Free GRE Study Plan Generator", desc="A free week-by-week GRE plan across verbal, quant and the Issue essay, with practice tests in the second half."),
  dict(slug="lsat-plan", board="Exam Study Plans", headline="LSAT prep, planned week by week", line="Logical reasoning, reading and blind review.", kind="weeks", data=["Question types", "Question types", "Timed sections", "Practice test", "Final week"], link="/study-plan/lsat/",
       title="Free LSAT Study Schedule Generator", desc="A free LSAT schedule built around logical reasoning and reading comprehension, with timed sections and blind review every week."),
  dict(slug="focus-timer", board="Free Study Tools", headline="One focus block at a time", line="25, 45 or 50 minutes. A self-test at the end.", kind="timer", data="25:00", link="/tools/focus-timer/",
       title="Free Focus Timer for Studying", desc="A free study timer: pick a 25, 45 or 50 minute focus block, take a short break, and end each block with a quick self-test."),
  dict(slug="exam-countdown", board="Free Study Tools", headline="How many study hours do you really have?", line="Days feel like a lot. Hours tell the truth.", kind="stats", data=[("42", "days left"), ("30", "study days"), ("90", "study hours")], link="/tools/exam-countdown/",
       title="Exam Countdown: Study Hours Left Before Your Exam", desc="Put in your exam date and daily hours to see the real number of study hours you have left. Free, no sign-up."),
  dict(slug="spaced-review", board="Free Study Tools", headline="Review it before you forget it", line="Review dates 1, 3, 7, 14 and 30 days out.", kind="dates", data=["Day 1", "Day 3", "Day 7", "Day 14", "Day 30"], link="/tools/spaced-review/",
       title="Spaced Repetition Review Calendar", desc="Add each topic the day you study it and get review dates 1, 3, 7, 14 and 30 days later, ready to add to your calendar."),
  dict(slug="phone-guide", board="Study Tips and Focus", headline="Stop checking your phone while studying", line="Willpower loses. Distance and friction win.", kind="steps", data=["Put the phone in another room", "Add friction to every check", "Check it only in breaks"], link="/guides/stop-checking-phone-while-studying/",
       title="How to Stop Checking Your Phone While Studying", desc="Willpower loses to a phone within reach. Use distance and friction instead: a simple guide with a free printable worksheet."),
  dict(slug="highlighting-guide", board="Study Tips and Focus", headline="Why highlighting fails", line="And how to take notes you remember.", kind="steps", data=["Turn notes into questions", "Cover the answers and recall", "Review again in a few days"], link="/guides/active-recall-notes/",
       title="Why Highlighting Fails (and What to Do Instead)", desc="Highlighting feels productive but does little for memory. Turn your notes into questions and use active recall instead."),
  dict(slug="brain-dump-guide", board="Study Tips and Focus", headline="Clear your head before you study", line="A 3-minute brain dump.", kind="steps", data=["Set a 3-minute timer", "Write down everything on your mind", "Sort: now, later, let go"], link="/guides/brain-dump-before-studying/",
       title="How to Clear Mental Clutter Before Studying", desc="A 3-minute brain dump gets the noise out of your head before a study session. Here is how to do it."),
  dict(slug="rereading-guide", board="Study Tips and Focus", headline="Re-reading won't finish your syllabus", line="Read once, then test yourself.", kind="steps", data=["Read a section once", "Close the book and recall", "Check, then move on"], link="/guides/stop-rereading-cover-syllabus-faster/",
       title="Why Re-reading Won't Finish Your Syllabus", desc="Re-reading feels safe but is slow. Cover your syllabus faster with retrieval practice and a weekly plan."),
  dict(slug="marathon-guide", board="Study Tips and Focus", headline="Why exam marathons fail", line="Study in 90-minute blocks instead.", kind="steps", data=["Set a sharp 90-minute timer", "Step away from your desk", "Switch topics between blocks"], link="/guides/why-exam-marathons-fail/",
       title="Why Exam Study Marathons Fail (and What to Do Instead)", desc="Long study marathons burn you out. Work in 90-minute focus blocks, take real breaks and switch topics between them."),
  dict(slug="focus-kit", board="Study Tips and Focus", headline="5 free study focus worksheets", line="Phone distractions, notes, clutter, syllabus, focus reset.", kind="steps", data=["Stop phone distractions", "Take notes you remember", "Clear mental clutter", "Cover your syllabus faster", "Reset your focus"], link="/#free-kit",
       title="Free Study Focus Kit: 5 Printable Worksheets", desc="Five free printable worksheets, one for each FocusFlow study system. Enter your email and the kit arrives in your inbox."),
]

CSS = """
@font-face { font-family: "Bricolage Grotesque"; font-weight: 700; src: url("../assets/fonts/bricolage-700.woff2"); }
@font-face { font-family: "IBM Plex Sans"; font-weight: 400 600; src: url("../assets/fonts/plex-sans.woff2"); }
@font-face { font-family: "IBM Plex Mono"; font-weight: 500; src: url("../assets/fonts/plex-mono-500.woff2"); }
:root { --ink: #14213d; --muted: #4f6072; --teal: #1f8a7d; --teal-ink: #176b62; --mint: #dff3ee; --paper: #fbfdfc; --sun: #fbf3dc; }
* { box-sizing: border-box; margin: 0; }
html, body { width: 1000px; height: 1500px; }
body { background: var(--mint); color: var(--ink); font-family: "IBM Plex Sans", sans-serif; }
.pin { position: relative; width: 1000px; height: 1500px; padding: 80px 72px; display: flex; flex-direction: column; overflow: hidden; }
.blob { position: absolute; right: -180px; top: -160px; width: 620px; height: 620px; border-radius: 50%; background: var(--sun); }
.brand { position: relative; display: flex; align-items: center; gap: 16px; font: 700 34px "Bricolage Grotesque"; }
.brand img { width: 64px; height: 64px; border-radius: 16px; }
h1 { position: relative; margin-top: 64px; font: 700 96px/1.0 "Bricolage Grotesque"; letter-spacing: -0.02em; max-width: 860px; }
.line { position: relative; margin-top: 28px; font-size: 38px; line-height: 1.3; color: var(--muted); max-width: 820px; }
.card { position: relative; margin-top: auto; background: var(--paper); border-radius: 36px; padding: 44px; box-shadow: 0 30px 60px -24px rgba(20,40,60,.35); }
.url { position: relative; margin-top: 40px; display: inline-block; align-self: flex-start; padding: 18px 30px; border-radius: 999px; background: var(--teal); color: #fff; font: 600 32px "IBM Plex Sans"; }
.row { display: grid; grid-template-columns: 120px 1fr; align-items: center; gap: 20px; padding: 18px 0; border-bottom: 2px solid #e3ecea; font-size: 32px; }
.row:last-child { border-bottom: 0; }
.row b { font: 500 34px "IBM Plex Mono"; color: var(--teal-ink); }
.bar { height: 16px; border-radius: 8px; background: var(--teal); }
.timer { text-align: center; font: 500 220px/1 "IBM Plex Mono"; color: var(--ink); padding: 30px 0; }
.chips { display: flex; justify-content: center; gap: 16px; }
.chips span { padding: 14px 28px; border-radius: 999px; background: var(--mint); font-size: 30px; }
.chips span.on { background: var(--teal); color: #fff; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center; }
.stats b { display: block; font: 500 120px/1 "IBM Plex Mono"; color: var(--teal-ink); }
.stats span { font-size: 30px; color: var(--muted); }
.dates { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.dates div { padding: 28px 8px; border-radius: 22px; background: var(--mint); text-align: center; font: 500 34px "IBM Plex Mono"; color: var(--teal-ink); }
.step { display: grid; grid-template-columns: 76px 1fr; gap: 22px; align-items: center; padding: 20px 0; border-bottom: 2px solid #e3ecea; font-size: 36px; }
.step:last-child { border-bottom: 0; }
.step i { display: grid; place-items: center; width: 64px; height: 64px; border-radius: 50%; background: var(--mint); font: 500 28px "IBM Plex Mono"; font-style: normal; color: var(--teal-ink); }
"""

def visual(p):
    k, d = p["kind"], p["data"]
    if k == "weeks":
        widths = [92, 80, 70, 60, 40]
        return "".join(f'<div class="row"><b>Wk {i+1}</b><div><div style="font-size:30px;margin-bottom:10px">{t}</div><div class="bar" style="width:{widths[i]}%;{"background:#e0a83a" if i in (2,3) else ("background:#5c6f99" if i==4 else "")}"></div></div></div>' for i, t in enumerate(d))
    if k == "timer":
        return f'<div style="text-align:center;font-size:32px;color:var(--muted)">Focus block</div><div class="timer">{d}</div><div class="chips"><span class="on">25 min</span><span>45 min</span><span>50 min</span></div>'
    if k == "stats":
        return '<div class="stats">' + "".join(f"<div><b>{n}</b><span>{l}</span></div>" for n, l in d) + "</div>"
    if k == "dates":
        return '<div style="font-size:32px;margin-bottom:24px">Cardiac drugs, chapter 4</div><div class="dates">' + "".join(f"<div>{x}</div>" for x in d) + "</div>"
    return "".join(f'<div class="step"><i>{i+1:02d}</i><span>{t}</span></div>' for i, t in enumerate(d))

for p in PINS:
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="pin">
<div class="blob"></div>
<div class="brand"><img src="../assets/logo-512.png" alt="">FocusFlow Lab</div>
<h1>{p['headline']}</h1>
<p class="line">{p['line']}</p>
<div class="card">{visual(p)}</div>
<span class="url">thefocusflowlab.com</span>
</div></body></html>"""
    (OUT / f"{p['slug']}.html").write_text(html, encoding="utf-8")

meta = [{k: p[k] for k in ("slug", "board", "title", "desc")} | {"link": "https://thefocusflowlab.com" + p["link"]} for p in PINS]
(OUT / "pins.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
print(len(PINS), "pins")
