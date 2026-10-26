"""Generate /tools/ pages.  Run: python _tools/tools.py && python _tools/build.py"""
import pathlib
from common import shell, crumbs, ORG, SITE, KIT_ASIDE

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN_CSS = '\n  <link rel="stylesheet" href="../../study-plan/assets/plan.css">'

def faq_block(faq):
    items = "\n".join(f"          <details><summary>{q}</summary>\n            <p>{a}</p></details>" for q, a in faq)
    return f"""      <section class="reading faq">
        <h2>Questions people ask</h2>
        <div class="prose">
{items}
        </div>
      </section>"""

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def app_ld(name, path, desc):
    return {"@type": "WebApplication", "name": name, "url": SITE + path, "description": desc, "applicationCategory": "EducationalApplication",
            "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": ORG}

TOOLS = [
  dict(slug="focus-timer", name="Focus timer", tag="Focus",
       title="Free Focus Timer for Studying: Focus Blocks and Breaks",
       desc="A free study focus timer. Pick a 25, 45 or 50 minute focus block, take a short break, and end each block with a quick self-test.",
       h1="One focus block at a time.",
       lead="Pick a block length, put your phone in another room, press start.",
       card="Focus blocks with a break and a self-test prompt at the end.",
       go="Start a block",
       tool="""        <div class="sheet timer" aria-label="Focus timer">
          <p class="sheet-title"><span id="phase">Focus block</span></p>
          <p class="timer-time mono" id="time" role="timer" aria-live="off">25:00</p>
          <div class="timer-actions">
            <button class="btn" type="button" id="start">Start</button>
            <button class="btn btn-soft" type="button" id="reset">Reset</button>
          </div>
          <div class="timer-set">
            <fieldset><legend>Focus</legend>
              <div class="seg"><label><input type="radio" name="focus" value="25" checked> 25 min</label><label><input type="radio" name="focus" value="45"> 45 min</label><label><input type="radio" name="focus" value="50"> 50 min</label></div>
            </fieldset>
            <fieldset><legend>Break</legend>
              <div class="seg"><label><input type="radio" name="break" value="5" checked> 5 min</label><label><input type="radio" name="break" value="10"> 10 min</label></div>
            </fieldset>
          </div>
          <label class="check"><input type="checkbox" id="sound" checked> Chime when a block ends</label>
          <div class="selftest" id="selftest" hidden>
            <p><strong>Block done. Before your break:</strong> close your notes and write down three things you just learned. Check them after.</p>
          </div>
          <p class="muted timer-count" id="done-count"></p>
        </div>""",
       how="""<p>A focus block is a set stretch of time where you do one thing: no phone, no switching tabs, no “quick check”. Short blocks with breaks are easier to start than a vague evening of studying.</p>
          <ul>
            <li><strong>Start with 25 minutes</strong> if focusing is hard right now. Move up to 45 or 50 as it gets easier.</li>
            <li><strong>End each block with a self-test.</strong> Writing down what you just learned, without looking, shows what actually went in.</li>
            <li><strong>Take the break.</strong> Stand up, get water, look at something far away. Skipping breaks makes the next block worse.</li>
          </ul>
          <p>The Exam Sprint Planner uses four of these blocks a day.</p>""",
       faq=[("Is 25 minutes the right length?", "It’s a good place to start. Many people settle on 45 or 50 minutes once focusing gets easier. Pick the longest block you can keep without checking your phone."),
            ("Does the timer keep running in the background?", "Yes. It counts from the clock, so it stays right if you switch tabs. Keep this tab open."),
            ("Does it save anything?", "Only the count of blocks you finish today, in this browser.")],
       script="focus-timer.js"),
  dict(slug="exam-countdown", name="Exam countdown", tag="Planning",
       title="Exam Countdown Calculator: Study Hours Left Before Your Exam",
       desc="How many days, study days and real study hours do you have before your exam? Put in the date and your daily hours to find out.",
       h1="How much time do you really have?",
       lead="Days until an exam feel like a lot. Study hours tell the truth.",
       card="Days and real study hours left before your exam.",
       go="Count my hours",
       tool="""        <form class="sheet" id="countdown-form" novalidate aria-label="Exam countdown">
          <p class="sheet-title">Your exam</p>
          <div class="fields">
            <div><label for="examDate">Exam date</label><input type="date" id="examDate" name="examDate" required></div>
            <div><label for="hoursPerDay">Hours a day</label><input type="number" id="hoursPerDay" min="0.5" max="14" step="0.5" value="3" inputmode="decimal"></div>
            <div><label for="daysPerWeek">Days a week</label><select id="daysPerWeek"><option>3</option><option>4</option><option selected>5</option><option>6</option><option>7</option></select></div>
          </div>
          <div class="sheet-actions"><button class="btn" type="submit">Count my hours</button></div>
          <p class="error" id="countdown-error" role="alert"></p>
          <div id="countdown-result" class="count-result" hidden aria-live="polite">
            <dl class="totals">
              <div><dt>Days left</dt><dd id="r-days"></dd></div>
              <div><dt>Study days</dt><dd id="r-study"></dd></div>
              <div><dt>Study hours</dt><dd id="r-hours"></dd></div>
            </dl>
            <p class="muted">That’s <span id="r-weeks"></span>. <span id="r-tip"></span></p>
            <p><a href="/study-plan/">Turn these hours into a week-by-week plan</a></p>
          </div>
        </form>""",
       how="""<p>“Six weeks left” sounds like plenty. At three hours a day, five days a week, it’s 90 hours, and every topic, practice test and review day has to fit inside them.</p>
          <ul>
            <li><strong>Count hours, not days.</strong> Hours are what you spend. Days include work, classes and sleep.</li>
            <li><strong>Be honest about days a week.</strong> A plan that assumes seven study days usually breaks in week one.</li>
            <li><strong>Leave the last day free.</strong> Rest before an exam is part of the plan, not time lost.</li>
          </ul>""",
       faq=[("How is the number of study days worked out?", "Days left times the days a week you study, divided by seven, rounded."),
            ("Does it count today?", "It counts from today to the day before the exam."),
            ("Is my date saved?", "Yes, in this browser only, so the countdown is there next time you open the page.")],
       script="exam-countdown.js"),
  dict(slug="spaced-review", name="Spaced review calendar", tag="Memory",
       title="Spaced Repetition Calendar: Free Review Schedule Maker",
       desc="Add a topic and the day you studied it. Get review dates 1, 3, 7, 14 and 30 days later, and add them to Google, Apple or Outlook calendar.",
       h1="Review it before you forget it.",
       lead="Add each topic the day you study it. Get the dates to review it again.",
       card="When to review a topic again so it sticks.",
       go="Make my calendar",
       tool="""        <div class="review-tool">
          <form class="sheet" id="review-form" novalidate aria-label="Add a topic">
            <p class="sheet-title">Add a topic</p>
            <div class="fields fields-2">
              <div><label for="topic">Topic</label><input type="text" id="topic" maxlength="80" placeholder="Cardiac drugs, chapter 4…" autocomplete="off"></div>
              <div><label for="studied">First studied</label><input type="date" id="studied"></div>
            </div>
            <div class="sheet-actions"><button class="btn" type="submit">Add topic</button></div>
            <p class="error" id="review-error" role="alert"></p>
          </form>
          <p class="muted" id="review-empty">Your topics and review dates show up here.</p>
          <div id="review-list" class="review-list" aria-live="polite"></div>
          <div class="sheet-actions" id="review-actions" hidden>
            <button class="btn" type="button" id="download-ics">Add to my calendar (.ics)</button>
            <button class="btn btn-quiet" type="button" id="clear-all">Clear all</button>
          </div>
        </div>""",
       how="""<p>Memory fades fast after you first learn something, and each review slows the fade. Spacing reviews further apart each time is one of the best-supported study methods there is.</p>
          <ul>
            <li><strong>Recall first, then check.</strong> On a review day, write or say what you remember before opening your notes.</li>
            <li><strong>Keep reviews short.</strong> Ten minutes of active recall beats an hour of re-reading.</li>
            <li><strong>Miss one? Do it the next day</strong> and keep the rest of the dates.</li>
          </ul>
          <p>The dates here use a common schedule: 1, 3, 7, 14 and 30 days after you first study a topic.</p>""",
       faq=[("How do I get the dates into my calendar?", "Press “Add to my calendar” to download a .ics file, then open it or import it into Google Calendar, Apple Calendar or Outlook."),
            ("Are my topics saved?", "Yes, in this browser only. Nothing is sent anywhere."),
            ("Why these gaps?", "1, 3, 7, 14 and 30 days is a common, simple schedule. Exact gaps matter less than reviewing more than once, with recall instead of re-reading.")],
       script="spaced-review.js"),
]

def tool_page(t):
    path = f"/tools/{t['slug']}/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Tools", "/tools/"), (t["name"], path)])
    ld = {"@context": "https://schema.org", "@graph": [app_ld(t["name"], path, t["desc"]), crumb_ld, faq_ld(t["faq"])]}
    body = f"""{crumb_html}

    <main id="main">
      <section class="hero tool-hero">
        <div>
          <h1>{t['h1']}</h1>
          <p class="lead">{t['lead']}</p>
          <p class="hero-note">Free, no sign-up. Works in your browser.</p>
        </div>
{t['tool']}
      </section>

      <section class="reading">
        <h2>How to use it</h2>
        <div class="prose">
          {t['how']}
        </div>
      </section>

{faq_block(t['faq'])}

{KIT_ASIDE}
    </main>"""
    return shell(path=path, title=t["title"] + " | FocusFlow Lab" if len(t["title"]) < 45 else t["title"], desc=t["desc"], og_title=t["name"] + " from FocusFlow Lab",
                 ld=ld, body=body, css_depth=2, extra_head=PLAN_CSS,
                 scripts=f'\n<script src="/assets/tools/{t["script"]}" defer></script>')

def index_page():
    path = "/tools/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Tools", path)])
    cards = "\n".join(f'        <li><a href="{t["slug"]}/"><span class="card-tag">{t["tag"]}</span><h2 class="card-name">{t["name"]}</h2><span class="card-note">{t["card"]}</span><span class="card-go">{t["go"]}</span></a></li>' for t in TOOLS)
    desc = "Free study tools that run in your browser: a focus timer, an exam countdown in real study hours and a spaced repetition review calendar."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "Free study tools", "url": SITE + path, "description": desc, "publisher": ORG}, crumb_ld]}
    body = f"""{crumb_html}

    <main id="main">
      <section class="hero single wash">
        <div>
          <h1>Free study tools.</h1>
          <p class="lead">Small tools that run in your browser. No sign-up, nothing to install.</p>
        </div>
      </section>
      <ul class="cards">
{cards}
        <li><a href="/study-plan/"><span class="card-tag">Planning</span><h2 class="card-name">Exam study plans</h2><span class="card-note">Week-by-week plans for the NCLEX, MCAT, USMLE Step 1, GRE and LSAT.</span><span class="card-go">Pick an exam</span></a></li>
      </ul>
    </main>"""
    return shell(path=path, title="Free Study Tools: Focus Timer, Countdown, Review Calendar", desc=desc, og_title="Free study tools from FocusFlow Lab",
                 ld=ld, body=body, css_depth=1, extra_head=PLAN_CSS.replace("../../", "../"))

(ROOT / "tools").mkdir(exist_ok=True)
(ROOT / "tools/index.html").write_text(index_page(), encoding="utf-8", newline="\n")
for t in TOOLS:
    out = ROOT / "tools" / t["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tool_page(t), encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT).as_posix())
