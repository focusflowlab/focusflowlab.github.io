"""Generate /tools/ pages.  Run: python _tools/tools.py && python _tools/build.py"""
import pathlib, json, html
from common import shell, crumbs, ORG, SITE, KIT_FORM

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
       title="Pomodoro Timer for Studying: Free Online Focus Timer",
       desc="A free online study timer: 25/5 Pomodoro-style blocks or 45 and 50 minute focus blocks, with breaks and a quick self-test after each one.",
       h1="A Pomodoro timer for studying.",
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
       how="""<p>A focus block is a set stretch of time where you do one thing: no phone, no switching tabs, no “quick check”. Short blocks with breaks are easier to start than a vague evening of studying. The 25-minute block with a 5-minute break is the classic Pomodoro-style rhythm; 50 and 10 suits longer study sessions.</p>
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
            <p><a href="https://thefocusflowlab.com/study-plan/" target="_blank" rel="noopener">Turn these hours into a week-by-week plan</a></p>
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
  dict(slug="test-time-calculator", name="Test time calculator", tag="Exam day",
       title="Test Time Calculator: Minutes Per Question and Pacing Checkpoints",
       desc="Enter your test time and number of questions to get minutes per question and checkpoints to check your pace during the exam.",
       h1="How long can you spend on each question?",
       lead="Put in the time and the number of questions. Get your pace and checkpoints.",
       card="Minutes per question and pacing checkpoints.",
       go="Work out my pace",
       tool="""        <form class="sheet" id="pace-form" novalidate aria-label="Test time calculator">
          <p class="sheet-title">Your test</p>
          <div class="fields">
            <div><label for="totalMin">Total time (minutes)</label><input type="number" id="totalMin" min="1" max="1000" step="1" value="120" inputmode="numeric"></div>
            <div><label for="questions">Number of questions</label><input type="number" id="questions" min="1" max="1000" step="1" value="60" inputmode="numeric"></div>
            <div><label for="reviewPct">Keep for review (%)</label><select id="reviewPct"><option>0</option><option>5</option><option selected>10</option><option>15</option><option>20</option></select></div>
          </div>
          <div class="sheet-actions"><button class="btn" type="submit">Work out my pace</button></div>
          <p class="error" id="pace-error" role="alert"></p>
          <div id="pace-result" class="count-result" hidden aria-live="polite">
            <dl class="totals">
              <div><dt>Per question</dt><dd id="r-min"></dd></div>
              <div><dt>In seconds</dt><dd id="r-sec"></dd></div>
              <div><dt>Review time</dt><dd id="r-review"></dd></div>
            </dl>
            <p class="muted">Checkpoints: <span id="r-points"></span></p>
            <p><a href="https://thefocusflowlab.com/study-plan/" target="_blank" rel="noopener">Build a free study plan for your exam</a></p>
          </div>
        </form>""",
       how="""<p>Divide the time by the questions and you have your average. The number is only useful if you check it while you test, so the calculator also gives checkpoints: where you should be a quarter, half and three quarters of the way through.</p>
          <ul>
            <li><strong>Keep time for review.</strong> Setting aside 5 to 15 percent lets you go back to flagged questions.</li>
            <li><strong>Averages are not limits.</strong> Some questions take 30 seconds and some take three minutes. Move on from the ones that stall you.</li>
            <li><strong>Practise with a clock.</strong> Do timed practice sets at this pace before test day so it feels normal.</li>
            <li><strong>Check the official rules.</strong> Your exam may have timed sections, breaks or a different number of scored questions. Use the numbers from the exam owner.</li>
          </ul>""",
       faq=[("How is minutes per question worked out?", "Total time minus the review time you keep, divided by the number of questions."),
            ("Does this work for any exam?", "Yes, for any test with one time limit. For tests with separate timed sections, run it once per section."),
            ("Is anything saved?", "Only your last numbers, in this browser. Nothing is sent anywhere.")],
       script="test-time.js"),
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
  dict(slug="final-grade-calculator", name="Final grade calculator", tag="Grades",
       title="Final Grade Calculator: What Do I Need on My Final?",
       desc="Find the score you need on your final exam to get the course grade you want. Put in your current grade, the final's weight and your target.",
       h1="What do you need on your final?",
       lead="Your current grade, the final’s weight, your target. That’s all it takes.",
       card="The score you need on the final to reach your target grade.",
       go="Work it out",
       tool="""        <form class="sheet" id="final-form" novalidate aria-label="Final grade calculator">
          <p class="sheet-title">Your course</p>
          <div class="fields">
            <div><label for="current">Current grade (%)</label><input type="number" id="current" min="0" max="150" step="0.1" placeholder="82" inputmode="decimal"></div>
            <div><label for="weight">Final is worth (%)</label><input type="number" id="weight" min="1" max="99" step="0.5" placeholder="30" inputmode="decimal"></div>
            <div><label for="target">Grade you want (%)</label><input type="number" id="target" min="0" max="150" step="0.1" placeholder="85" inputmode="decimal"></div>
          </div>
          <div class="sheet-actions"><button class="btn" type="submit">Work it out</button></div>
          <p class="error" id="final-error" role="alert"></p>
          <div id="final-result" class="count-result" hidden aria-live="polite">
            <dl class="totals"><div><dt>You need on the final</dt><dd id="r-need"></dd></div></dl>
            <p class="muted" id="r-note"></p>
            <table class="mini-table"><thead><tr><th>For a final grade of</th><th>You need</th></tr></thead><tbody id="r-table"></tbody></table>
          </div>
        </form>""",
       how="""<p>Your course grade is a weighted average: everything before the final counts for part of it, and the final counts for the rest. If the final is worth 30%, your work so far is worth the other 70%.</p>
          <p>The score you need is: <strong>(target − current × (1 − final weight)) ÷ final weight</strong>. For example, with 82% now, a final worth 30% and a target of 85%, you need 92% on the final.</p>
          <ul>
            <li><strong>Check the weight in your syllabus.</strong> A final worth 20% and one worth 40% need very different scores.</li>
            <li><strong>Use your current grade as a percentage.</strong> If your school shows letters, use the percentage behind the letter.</li>
            <li><strong>Then plan backwards.</strong> The <a href="/tools/exam-countdown/">exam countdown</a> shows how many study hours you have left.</li>
          </ul>""",
       faq=[("What do I need on my final to pass?", "Set “Grade you want” to your course’s pass mark, often 60% or 70% (check your syllabus). The calculator shows the score you need on the final to reach it."),
            ("What do I need on my final to get an A?", "Put 90 as the grade you want, or check the table under the result: it lists the score you need for an A, B, C and D at once."),
            ("How is the score I need worked out?", "Needed score = (target grade − current grade × (1 − final weight)) ÷ final weight, with the weight as a decimal. So a final worth 25% uses 0.25."),
            ("What if the answer is over 100%?", "Then the target can’t be reached on the final alone, unless your course has extra credit. Try the next grade down to see what is reachable."),
            ("Does it work for weighted categories?", "If your grade comes from several weighted categories, work out your current grade first with the weighted grade calculator, then use that number here.")],
       script="final-grade.js"),
  dict(slug="gpa-calculator", name="GPA calculator", tag="Grades",
       title="GPA Calculator: Weighted, Cumulative and How to Raise It",
       desc="Free GPA calculator for college and high school: semester GPA, weighted GPA for Honors and AP classes, cumulative GPA, and the GPA you need to raise it.",
       h1="Work out your GPA.",
       lead="Add your courses, credits and letter grades. Your GPA updates as you type.",
       card="Semester, weighted and cumulative GPA, and how to raise it.",
       go="Calculate my GPA",
       tool="""        <form class="sheet" id="gpa-form" novalidate aria-label="GPA calculator">
          <p class="sheet-title">This semester</p>
          <div class="row-head gpa-head" aria-hidden="true"><span>Course</span><span>Credits</span><span>Grade</span><span>Level</span><span></span></div>
          <ol class="tool-rows gpa-rows" id="gpa-rows"></ol>
          <div class="sheet-actions"><button class="btn btn-soft" type="button" id="add-course">Add a course</button></div>
          <p class="error" id="gpa-error" role="alert"></p>
          <fieldset><legend>Past GPA (optional, for cumulative)</legend>
            <div class="fields fields-2b">
              <div><label for="prevGpa">Current cumulative GPA</label><input type="number" id="prevGpa" min="0" max="5" step="0.01" placeholder="3.40" inputmode="decimal"></div>
              <div><label for="prevCredits">Credits so far</label><input type="number" id="prevCredits" min="1" max="1000" step="0.5" placeholder="45" inputmode="numeric"></div>
            </div>
          </fieldset>
          <div class="count-result" aria-live="polite">
            <dl class="totals">
              <div><dt>Semester GPA</dt><dd id="r-term">–</dd></div>
              <div><dt>Weighted GPA</dt><dd id="r-weighted">–</dd></div>
              <div><dt>Credits</dt><dd id="r-credits">0</dd></div>
              <div><dt>Cumulative GPA</dt><dd id="r-cum">–</dd></div>
            </dl>
          </div>
          <fieldset><legend>Raise my GPA (optional)</legend>
            <div class="fields fields-2b">
              <div><label for="targetGpa">Target cumulative GPA</label><input type="number" id="targetGpa" min="0" max="5" step="0.01" placeholder="3.50" inputmode="decimal"></div>
              <div><label for="nextCredits">Credits next term</label><input type="number" id="nextCredits" min="1" max="100" step="0.5" placeholder="15" inputmode="numeric"></div>
            </div>
            <p class="gpa-need" id="r-need" aria-live="polite"></p>
          </fieldset>
        </form>""",
       how="""<p>GPA is an average of grade points, weighted by credits, so a 4-credit course counts more than a 1-credit one. This calculator uses the common US 4.0 scale: A = 4.0, A− = 3.7, B+ = 3.3, B = 3.0, and so on down to F = 0.</p>
          <p><strong>Weighted GPA</strong> is common in US high schools: Honors classes usually get an extra 0.5 and AP or IB classes an extra 1.0, so an A in an AP class counts as 5.0. Set each course’s level to see it. Schools differ, so check yours.</p>
          <ul>
            <li><strong>Check your school’s scale.</strong> Some schools give A+ a 4.3, and some don’t use plus or minus grades. Your transcript or student handbook says which.</li>
            <li><strong>For cumulative GPA,</strong> add your current GPA and the credits it covers. The calculator combines them with this semester.</li>
            <li><strong>Pass/fail courses</strong> usually don’t count toward GPA, so leave them out.</li>
            <li><strong>To raise your GPA,</strong> put your target and next term’s credits under “Raise my GPA”. It shows the GPA you need next term.</li>
          </ul>""",
       faq=[("How is GPA calculated?", "Multiply each course’s grade points by its credits, add those up, and divide by the total credits. A 3-credit A (4.0) and a 4-credit B (3.0) give (12 + 12) ÷ 7 = 3.43."),
            ("Does an A+ count as 4.3?", "At some schools, yes. This calculator uses 4.0 for an A+, which is the most common rule. Check your school’s policy."),
            ("How do I calculate a weighted GPA for Honors and AP classes?", "Add 0.5 to the grade points of Honors classes and 1.0 to AP or IB classes, then average by credits as usual. An A in an AP class becomes 5.0. Many high schools use this scale, but check yours."),
            ("How much can I raise my GPA in one semester?", "It depends on how many credits you already have. Put your target and next term’s credits under “Raise my GPA” to see the GPA you’d need. The more credits behind you, the slower your GPA moves."),
            ("Can I use it for UK, Canadian or Australian grades?", "Only if your school reports a 4.0-scale GPA. UK degree classifications and Australian GPA scales work differently, so this calculator won’t match them.")],
       script="gpa.js"),
  dict(slug="weighted-grade-calculator", name="Weighted grade calculator", tag="Grades",
       title="Weighted Grade Calculator: Course Grade from Categories",
       desc="Work out your course grade from weighted categories like homework, quizzes, midterm and final. Leave ungraded work blank to see your grade so far.",
       h1="Your course grade, from the syllabus.",
       lead="Add each category’s weight and your score. Leave anything not graded yet blank.",
       card="Your course grade from weighted categories.",
       go="Add my scores",
       tool="""        <form class="sheet" id="wg-form" novalidate aria-label="Weighted grade calculator">
          <p class="sheet-title">Categories</p>
          <div class="row-head" aria-hidden="true"><span>Category</span><span>Weight %</span><span>Score %</span><span></span></div>
          <ol class="tool-rows" id="wg-rows"></ol>
          <div class="sheet-actions"><button class="btn btn-soft" type="button" id="add-category">Add a category</button></div>
          <p class="error" id="wg-error" role="alert"></p>
          <div class="count-result" aria-live="polite">
            <dl class="totals">
              <div><dt>Grade</dt><dd id="r-grade">–</dd></div>
              <div><dt>Weights entered</dt><dd id="r-weight">0%</dd></div>
              <div><dt>Graded so far</dt><dd id="r-done">0%</dd></div>
            </dl>
            <p class="muted" id="r-note"></p>
          </div>
        </form>""",
       how="""<p>Most courses don’t average every score equally. Your syllabus sets a weight for each category, like homework 20% and the final 40%, and your grade is the weighted average.</p>
          <ul>
            <li><strong>Copy the weights from your syllabus.</strong> They should add up to 100%.</li>
            <li><strong>Use the category average as the score.</strong> If you have five quizzes, enter their average.</li>
            <li><strong>Leave future work blank</strong> to see your grade on what’s been marked so far. Then use the <a href="/tools/final-grade-calculator/">final grade calculator</a> to see what you need on the final.</li>
          </ul>""",
       faq=[("How is a weighted grade calculated?", "Multiply each category score by its weight, add them up, and divide by the total weight of the graded categories."),
            ("What if my weights don’t add up to 100%?", "The calculator still gives your grade on the work entered so far. If they add up to more than 100%, check your syllabus, as a weight is probably wrong."),
            ("Is my data saved?", "Yes, in this browser only, so your categories are there next time.")],
       script="weighted-grade.js"),
  dict(slug="study-schedule-maker", name="Study schedule maker", tag="Planning",
       title="Study Schedule Maker: Free Weekly Plan for All Your Exams",
       desc="Free study schedule and study timetable maker: add your subjects and exam dates and get weekly hours per subject, with more time for nearer exams.",
       h1="A study schedule for all your exams.",
       lead="Add each subject and its exam date. You get hours per subject for every week.",
       card="Weekly hours per subject, up to each exam.",
       go="Make my schedule",
       tool="""        <form class="sheet" id="ss-form" novalidate aria-label="Study schedule maker">
          <p class="sheet-title">Your exams</p>
          <div class="row-head" aria-hidden="true"><span>Subject</span><span>Exam date</span><span>Work needed</span><span></span></div>
          <ol class="tool-rows" id="ss-rows"></ol>
          <div class="sheet-actions"><button class="btn btn-soft" type="button" id="add-subject">Add a subject</button></div>
          <div class="fields fields-2b" style="margin-top:var(--space-md)">
            <div><label for="ssHours">Study hours a day</label><input type="number" id="ssHours" min="0.5" max="14" step="0.5" value="3" inputmode="decimal"></div>
            <div><label for="ssDays">Days a week</label><select id="ssDays"><option>3</option><option>4</option><option selected>5</option><option>6</option><option>7</option></select></div>
          </div>
          <div class="sheet-actions"><button class="btn" type="submit">Make my schedule</button></div>
          <p class="error" id="ss-error" role="alert"></p>
        </form>""",
       after="""      <section id="ss-result" class="plan ss-plan" hidden aria-live="polite">
        <div class="plan-head"><h2>Your study schedule</h2><button class="btn btn-soft no-print" type="button" id="ss-print">Print or save as PDF</button></div>
        <ul class="ss-exams" id="ss-exams"></ul>
        <div class="table-scroll"><table class="mini-table ss-table" id="ss-table"></table></div>
        <p class="muted">Hours are rounded to half-hour blocks. Subjects drop off the schedule after their exam.</p>
      </section>""",
       how="""<p>The schedule shares out your daily hours among the subjects whose exams haven’t happened yet. Two things decide each subject’s share: how much work you said it needs, and how close its exam is. Nearer exams get more time, so you don’t run out of days on the first one.</p>
          <ul>
            <li><strong>Be honest about hours.</strong> Three real hours beat six planned ones.</li>
            <li><strong>Mark your hardest subjects as Heavy.</strong> They get about three times the time of a Light one.</li>
            <li><strong>Turn hours into blocks.</strong> Use the <a href="/tools/focus-timer/">focus timer</a> to work through each subject’s hours one block at a time.</li>
          </ul>""",
       faq=[("Is this a study timetable maker?", "Yes. It makes a printable week-by-week study timetable for all your subjects. Press “Print or save as PDF” to keep it."),
            ("How does it decide hours per subject?", "Each study day, subjects with an upcoming exam share your hours. A subject’s share grows with the work it needs (Light, Normal, Heavy) and as its exam gets closer."),
            ("Can I save or print it?", "Press “Print or save as PDF”. Your subjects and dates also stay in this browser for next time."),
            ("What about big exams like the NCLEX or MCAT?", "For a single big exam, the exam-specific study plans are a better fit. They follow that exam’s content outline.")],
       script="study-schedule.js"),
  dict(slug="reading-planner", name="Reading planner", tag="Planning",
       title="Reading Planner: How Many Pages a Day to Finish on Time",
       desc="Put in your page count and deadline. Get how many pages to read a day, a day-by-day page plan and review days before the deadline.",
       h1="How many pages a day?",
       lead="Your page count and deadline in, a day-by-day reading plan out.",
       card="Pages a day to finish a book or reading list on time.",
       go="Plan my reading",
       tool="""        <form class="sheet" id="reading-form" novalidate aria-label="Reading planner">
          <p class="sheet-title">Your reading</p>
          <div class="fields fields-date">
            <div><label for="totalPages">Total pages</label><input type="number" id="totalPages" min="1" max="20000" step="1" placeholder="320" inputmode="numeric"></div>
            <div><label for="pagesRead">Already read</label><input type="number" id="pagesRead" min="0" step="1" placeholder="0" inputmode="numeric"></div>
            <div><label for="deadline">Finish by</label><input type="date" id="deadline"></div>
          </div>
          <div class="fields fields-2b" style="margin-top:var(--space-sm)">
            <div><label for="readDays">Reading days a week</label><select id="readDays"><option>3</option><option>4</option><option selected>5</option><option>6</option><option>7</option></select></div>
            <div><label class="check" style="margin-top:28px"><input type="checkbox" id="reviewDays" checked> Keep the last 2 days for review</label></div>
          </div>
          <div class="sheet-actions"><button class="btn" type="submit">Plan my reading</button></div>
          <p class="error" id="reading-error" role="alert"></p>
          <div id="reading-result" class="count-result" hidden aria-live="polite">
            <dl class="totals">
              <div><dt>Pages a day</dt><dd id="r-per"></dd></div>
              <div><dt>Reading days</dt><dd id="r-days"></dd></div>
              <div><dt>Pages left</dt><dd id="r-left"></dd></div>
            </dl>
            <div class="table-scroll"><table class="mini-table"><thead><tr><th>Day</th><th>Pages</th></tr></thead><tbody id="r-table"></tbody></table></div>
          </div>
        </form>""",
       how="""<p>The planner spreads the pages you have left evenly across your reading days, then keeps the last two days for review if you want them. Rest days are skipped, so the daily number is what you really have to read.</p>
          <ul>
            <li><strong>Read once, properly.</strong> Close the book after each section and write down the main points from memory. The <a href="/guides/stop-rereading-cover-syllabus-faster/">re-reading guide</a> explains why this beats a second read.</li>
            <li><strong>Use the review days</strong> to recall, not re-read: skim your notes and test yourself on the main points.</li>
            <li><strong>Behind schedule?</strong> Put in the pages you’ve read so far and the plan resets from today.</li>
          </ul>
          <h3>Pages a day: some quick examples</h3>
          <div class="table-scroll"><table class="mini-table"><thead><tr><th scope="col">Pages left</th><th scope="col">Reading days</th><th scope="col">Pages a day</th></tr></thead>
          <tbody><tr><td>300</td><td>10</td><td>30</td></tr><tr><td>300</td><td>15</td><td>20</td></tr><tr><td>300</td><td>20</td><td>15</td></tr><tr><td>600</td><td>20</td><td>30</td></tr></tbody></table></div>
          <p>Count only days you will really read. A 300-page book due in three weeks with five reading days a week is 15 reading days, so 20 pages a day. If the daily number looks too big, start earlier or ask whether every chapter needs a full read. For a textbook, read the headings and summary first, then read the sections that matter most.</p>""",
       faq=[("How many pages a day should I read?", "Enough to finish by your deadline with a couple of days spare for review. Put in your page count and deadline above and the planner works it out."),
            ("How are pages per day worked out?", "Pages left ÷ reading days before the deadline, rounded up. Review days and rest days aren’t counted as reading days."),
            ("Does it count today?", "Yes. The plan starts today and ends the day before your deadline."),
            ("Is my plan saved?", "Yes, in this browser only, so you can come back and update the pages you’ve read.")],
       script="reading-planner.js"),
  dict(slug="flashcards", name="Flashcards", tag="Memory",
       title="Online Flashcards: Free Flashcard Maker with Spaced Repetition",
       desc="Make flashcards and review them with spaced repetition: cards you know come back later, cards you miss come back tomorrow. Free, works in your browser.",
       h1="Flashcards that come back at the right time.",
       lead="Write the card, test yourself, and the spacing is done for you.",
       card="Make flashcards and review them with spaced repetition.",
       go="Make cards",
       tool="""        <div class="fc-tool">
          <form class="sheet" id="fc-add" novalidate aria-label="Add a flashcard">
            <p class="sheet-title">New card <span><span id="fc-count">0</span> cards, <span id="fc-due">0</span> due</span></p>
            <label for="fcFront">Front (question)</label>
            <textarea id="fcFront" rows="2" maxlength="300" placeholder="What does furosemide do?"></textarea>
            <label for="fcBack" style="margin-top:var(--space-sm)">Back (answer)</label>
            <textarea id="fcBack" rows="2" maxlength="600" placeholder="Loop diuretic: blocks sodium and chloride reabsorption in the loop of Henle."></textarea>
            <div class="sheet-actions"><button class="btn btn-soft" type="submit">Add card</button><button class="btn" type="button" id="fc-start" disabled>Nothing due today</button></div>
            <p class="error" id="fc-error" role="alert"></p>
          </form>
          <div class="sheet fc-study" id="fc-study" hidden aria-live="polite">
            <p class="sheet-title">Review <span id="fc-left"></span></p>
            <p class="fc-front" id="fc-front"></p>
            <div id="fc-back-wrap" hidden><p class="fc-back" id="fc-back"></p></div>
            <div class="sheet-actions"><button class="btn" type="button" id="fc-reveal">Show answer</button></div>
            <div class="sheet-actions" id="fc-rate" hidden><button class="btn btn-soft" type="button" id="fc-again">Missed it</button><button class="btn" type="button" id="fc-good">Got it</button></div>
          </div>
          <p class="muted" id="fc-done" hidden>All done for today. Come back tomorrow for the next due cards.</p>
        </div>""",
       after="""      <section class="reading fc-deck">
        <h2>Your cards</h2>
        <div>
          <p class="muted" id="fc-empty">No cards yet. Add your first one above.</p>
          <ul class="fc-list" id="fc-list"></ul>
          <p id="fc-status" class="visually-hidden" role="status"></p>
          <div class="sheet-actions"><button class="btn btn-soft" type="button" id="fc-export">Download my cards</button><label class="btn btn-soft fc-import">Import cards<input type="file" id="fc-import" accept="application/json,.json" hidden></label></div>
          <p class="muted">Cards are saved in this browser only. Download them to back them up or move them to another device.</p>
        </div>
      </section>""",
       how="""<p>Testing yourself is one of the most effective ways to remember things, and spacing the tests out makes it stick longer. Each card starts due today. Get it right and it comes back after 1 day, then 3, 7, 14, 30 and 60. Miss it and it comes back tomorrow.</p>
          <ul>
            <li><strong>One idea per card.</strong> “What does furosemide do?” beats a card with five drug facts on it.</li>
            <li><strong>Answer before you flip.</strong> Say or write the answer first, then check. Be strict with “Got it”.</li>
            <li><strong>Review a little every day.</strong> Ten minutes daily beats an hour once a week.</li>
          </ul>""",
       faq=[("Where are my cards stored?", "In this browser only. Nothing is sent anywhere. Use “Download my cards” to keep a backup or move them to another device."),
            ("How does the spacing work?", "Cards you get right come back after 1, 3, 7, 14, 30 and then 60 days. Cards you miss come back tomorrow, and once more before you finish today."),
            ("Can I import cards?", "You can import a file you downloaded from this page. Other apps use different formats, so their files won’t import.")],
       script="flashcards.js"),
  dict(slug="practice-score-tracker", name="Practice score tracker", tag="Exams",
       title="Practice Score Tracker: Find Weak Topics and Plan Your Hours",
       desc="Log practice question sets by topic for 14 exams. See accuracy per topic, your trend, and a suggested split of next week’s study hours. Free, saved in your browser.",
       h1="Where should your hours go next?",
       lead="Log each practice set. See your weak topics and a suggested split of next week’s hours.",
       card="Log practice scores and see where to spend your hours.",
       go="Track my scores",
       tool="""        <form class="sheet" id="sc-form" novalidate aria-label="Add a practice set">
          <p class="sheet-title">Add a practice set</p>
          <div class="fields fields-2b">
            <div><label for="sc-exam">Exam</label><select id="sc-exam"></select></div>
            <div><label for="sc-topic">Topic</label><select id="sc-topic"></select></div>
          </div>
          <div class="fields fields-date" style="margin-top:var(--space-sm)">
            <div><label for="sc-right">Right</label><input type="number" id="sc-right" min="0" max="5000" step="1" inputmode="numeric" placeholder="32"></div>
            <div><label for="sc-total">Out of</label><input type="number" id="sc-total" min="1" max="5000" step="1" inputmode="numeric" placeholder="40"></div>
            <div><label for="sc-date">Date</label><input type="date" id="sc-date"></div>
          </div>
          <div class="fields" style="margin-top:var(--space-sm)"><div><label for="sc-note">Note (optional)</label><input type="text" id="sc-note" maxlength="60" placeholder="Question bank, set 3"></div></div>
          <div class="sheet-actions"><button class="btn" type="submit">Add this set</button></div>
          <p class="error" id="sc-error" role="alert"></p>
          <div class="fields fields-2b" style="margin-top:var(--space-md)">
            <div><label for="sc-target">Your target accuracy (%)</label><input type="number" id="sc-target" min="1" max="100" step="1" inputmode="numeric" value="75"></div>
            <div><label for="sc-hours">Study hours next week</label><input type="number" id="sc-hours" min="0" max="100" step="0.5" inputmode="decimal" value="20"></div>
          </div>
        </form>""",
       after="""      <section class="plan sc-result" aria-labelledby="sc-title" aria-live="polite">
        <div class="plan-head"><h2 id="sc-title">Your scores</h2></div>
        <dl class="totals">
          <div><dt>Overall accuracy</dt><dd id="sc-overall">-</dd></div>
          <div><dt>Questions logged</dt><dd id="sc-count">0</dd></div>
          <div><dt>Trend</dt><dd id="sc-trend">-</dd></div>
        </dl>
        <p id="sc-advice" class="sc-advice"></p>
        <p id="sc-plan" class="sc-plan" hidden><a class="btn btn-soft" id="sc-plan-link" href="/study-plan/">Build my plan with these weak topics</a></p>
        <div class="table-scroll"><table class="mini-table sc-table">
          <thead><tr><th scope="col">Topic</th><th scope="col">Your accuracy</th><th scope="col">Status</th><th scope="col">Plan share</th><th scope="col">Suggested share</th></tr></thead>
          <tbody id="sc-table"></tbody></table></div>
        <p class="muted">Plan share is the rough weight in the exam outline, not an official number. Suggested share raises topics below your target and gives topics with no data a small boost, until you test them.</p>
        <h3>Your entries</h3>
        <p id="sc-empty" class="muted">Nothing logged for this exam yet.</p>
        <ul class="sc-list" id="sc-list"></ul>
        <div class="sheet-actions no-print"><button class="btn btn-soft" type="button" id="sc-csv">Download as CSV</button><button class="btn btn-quiet" type="button" id="sc-clear">Delete this exam’s scores</button></div>
      </section>""",
       how="""<p>After each practice set, add how many you got right and the topic. The table shows your accuracy per topic and where your next week’s hours should go.</p>
          <ul>
            <li><strong>Log the topic, not just the total.</strong> A 70% overall can hide one topic at 40%.</li>
            <li><strong>Small sets are noisy.</strong> Under about 20 questions in a topic, treat the number as a hint, not a verdict.</li>
            <li><strong>Prefer a spreadsheet?</strong> <a href="/assets/templates/practice-score-log.xlsx" download>Download the practice score log</a> (Excel or Google Sheets, with a % right chart).</li>
            <li><strong>Redo what you missed.</strong> Pair this with the <a href="/tools/error-log/">error log</a> so each miss gets a retest date.</li>
            <li><strong>Feed it back into your plan.</strong> Use the suggested split to set next week’s hours in the <a href="/study-plan/">free exam study plan</a>.</li>
          </ul>""",
       faq=[("Where are my scores stored?", "In this browser only. Nothing is sent anywhere. Use “Download as CSV” to keep a copy or move to another device."),
            ("How is the suggested share worked out?", "Each topic starts from its rough weight in the exam outline. A topic below your target accuracy gets a larger share, in proportion to how far below it is. A topic with no data gets a small boost until you test it. Then the shares are scaled to add up to 100%."),
            ("Are the topic weights official?", "No. They are the rough shares the free plan generators use, based on each exam’s published outline. Check the official outline for the current version."),
            ("What target should I use?", "Use your own practice-test goal. If you are unsure, 70 to 80% is a common planning target, but it is not an official passing mark for any exam."),
            ("Which exams does it cover?", "NCLEX-RN, NCLEX-PN, ATI TEAS, MCAT, USMLE Step 1, PANCE, NAPLEX, DAT, GRE, GMAT, LSAT and the three CPA sections.")],
       script="score-tracker.js", pre="exam-topics.js"),
  dict(slug="error-log", name="Error log", tag="Exams",
       title="Error Log: Track Missed Questions and Why You Missed Them",
       desc="A free online error log for exam prep. Record each missed question, why you missed it and your fix, get a retest date, and see which kind of mistake costs you most.",
       h1="Turn every miss into a retest.",
       lead="Write down what you missed and why. Get a retest date for each one.",
       card="Log missed questions, the reason, and a retest date.",
       go="Open the log",
       tool="""        <form class="sheet" id="el-form" novalidate aria-label="Add a missed question">
          <p class="sheet-title">Add a miss</p>
          <div class="fields fields-2b">
            <div><label for="el-exam">Exam</label><select id="el-exam"></select></div>
            <div><label for="el-topic">Topic</label><select id="el-topic"></select></div>
          </div>
          <div class="fields" style="margin-top:var(--space-sm)"><div><label for="el-what">What did you miss?</label><input type="text" id="el-what" maxlength="120" placeholder="Heparin antidote"></div></div>
          <div class="fields fields-2b" style="margin-top:var(--space-sm)">
            <div><label for="el-reason">Why did you miss it?</label><select id="el-reason"></select></div>
            <div><label for="el-fix">What will you do about it? (optional)</label><input type="text" id="el-fix" maxlength="120" placeholder="Make 5 flashcards"></div>
          </div>
          <div class="sheet-actions"><button class="btn" type="submit">Add to the log</button></div>
          <p class="error" id="el-error" role="alert"></p>
        </form>""",
       after="""      <section class="plan sc-result" aria-labelledby="el-title" aria-live="polite">
        <div class="plan-head"><h2 id="el-title">Your log</h2></div>
        <dl class="totals">
          <div><dt>Logged</dt><dd id="el-total">0</dd></div>
          <div><dt>Still open</dt><dd id="el-open">0</dd></div>
          <div><dt>Due to retest</dt><dd id="el-due">0</dd></div>
        </dl>
        <p id="el-insight" class="sc-advice"></p>
        <dl class="alloc" id="el-bars" aria-label="Misses by reason"></dl>
        <h3>To review</h3>
        <p id="el-empty" class="muted">Nothing open. Add a miss above.</p>
        <ul class="sc-list el-list" id="el-list"></ul>
        <div class="sheet-actions no-print"><button class="btn btn-soft" type="button" id="el-csv">Download as CSV</button></div>
      </section>""",
       how="""<p>An error log works when each miss is sorted by its cause, because each cause has a different fix. Write what you missed, pick the reason, and the log gives you a retest date.</p>
          <ul>
            <li><strong>Knowledge gap:</strong> relearn it from the source and retest it after a week.</li>
            <li><strong>Misread the question or a careless slip:</strong> retest in two days, and add a check step before you answer.</li>
            <li><strong>Ran out of time:</strong> practise timed blocks. The <a href="/tools/test-time-calculator/">test time calculator</a> gives you checkpoints.</li>
            <li><strong>Guessed and got lucky:</strong> count it as a miss, because you did not know it.</li>
          </ul>
          <p>Log every miss for a few days, then look at the bars. If most are careless slips, more content review will not help.</p>""",
       faq=[("Where is my log stored?", "In this browser only. Nothing is sent anywhere. Use “Download as CSV” to keep a copy."),
            ("What should I write in the log?", "A few words: the concept or the question, the reason you missed it, and one concrete step to fix it. Long notes do not get reviewed."),
            ("How are retest dates set?", "Knowledge gaps come back after 7 days, so you have time to relearn them first. Misreads, careless slips and guesses come back after 2 days, and timing and approach errors after 3. These are planning defaults, so change your own plan if you need to."),
            ("Does the log replace practice questions?", "No. It tells you what to practise next. Pair it with the practice score tracker to see which topics are weak.")],
       script="error-log.js", pre="exam-topics.js"),
]

RELATED = {
    "practice-score-tracker": ["error-log", "exam-countdown", "test-time-calculator"],
    "error-log": ["practice-score-tracker", "spaced-review", "flashcards"],
    "test-time-calculator": ["exam-countdown", "focus-timer", "study-schedule-maker"],
    "focus-timer": ["exam-countdown", "study-schedule-maker", "flashcards"],
    "exam-countdown": ["study-schedule-maker", "test-time-calculator", "focus-timer"],
    "spaced-review": ["flashcards", "reading-planner", "focus-timer"],
    "final-grade-calculator": ["weighted-grade-calculator", "gpa-calculator", "exam-countdown"],
    "gpa-calculator": ["final-grade-calculator", "weighted-grade-calculator", "study-schedule-maker"],
    "weighted-grade-calculator": ["final-grade-calculator", "gpa-calculator", "study-schedule-maker"],
    "study-schedule-maker": ["exam-countdown", "focus-timer", "reading-planner"],
    "reading-planner": ["study-schedule-maker", "spaced-review", "flashcards"],
    "flashcards": ["spaced-review", "focus-timer", "reading-planner"],
}

def related_block(t):
    by_slug = {x["slug"]: x for x in TOOLS}
    items = "\n".join(
        f'          <li><a href="/tools/{s}/"><span class="card-tag">{by_slug[s]["tag"]}</span><span class="card-name">{by_slug[s]["name"]}</span><span class="card-note">{by_slug[s]["card"]}</span><span class="card-go">{by_slug[s]["go"]}</span></a></li>'
        for s in RELATED.get(t["slug"], []) if s in by_slug)
    return f"""      <section class="band related" aria-labelledby="related-title">
        <h2 id="related-title">Related tools</h2>
        <ul class="cards">
{items}
        </ul>
      </section>"""

# Next-step box per tool: (heading, text, button label, button href, text-link label, text-link href)
GRADES = ("Finals coming up?", "Turn your grade target into a study plan. The Exam Sprint Planner is a printable 14-day plan with four focus blocks a day and a self-test after each. [[P]], 14-day no-questions refund.",
          "See the planners", "/planners/", "Free guide: how to study for finals in a week.", "/guides/how-to-study-for-finals-in-a-week/")
# GPA and weighted-grade tools get no planner pitch: free guide and free plans only.
GRADES_FREE = ("Finals coming up?", "Turn your grade target into a study plan. Read how to cover a course in the last week, or build a free week-by-week plan for your exam.",
               "Finals in a week: the guide", "/guides/how-to-study-for-finals-in-a-week/", "Free exam study plans.", "/study-plan/")
PLAN = ("Know your exam date? Get the plan.", "Pick your exam for a free week-by-week study plan, or print one.",
        "Free exam study plans", "/study-plan/", "See the [[P]] printable planners.", "/planners/")
NEXT_STEP = {
    "practice-score-tracker": ("Turn the weak topics into a plan.", "Pick your exam for a free week-by-week plan, then use your suggested split to set each week’s hours. You can also add the plan to your calendar.",
                               "Free exam study plans", "/study-plan/", "See the [[P]] printable planners.", "/planners/"),
    "error-log": ("Turn misses into a plan.", "Pick your exam for a free week-by-week plan, or print the error log pages that come with the planners.",
                  "Free exam study plans", "/study-plan/", "See the [[P]] printable planners.", "/planners/"),
    "final-grade-calculator": GRADES, "gpa-calculator": GRADES_FREE, "weighted-grade-calculator": GRADES_FREE,
    "exam-countdown": PLAN, "test-time-calculator": PLAN, "study-schedule-maker": PLAN, "reading-planner": PLAN,
    "spaced-review": ("Studying for a big exam?", "Reviews need dates to fit into. Build a free week-by-week plan for your exam, or print one.",
                      "Free exam study plans", "/study-plan/", "See the [[P]] printable planners.", "/planners/"),
    "flashcards": ("Studying for a big exam?", "Cards work best inside a plan. Build a free week-by-week study plan for your exam, or print one.",
                   "Free exam study plans", "/study-plan/", "See the [[P]] printable planners.", "/planners/"),
    "focus-timer": ("Take the focus blocks offline.", "The printable planners have daily pages with four focus blocks and a self-test after each. [[P]] each, 14-day no-questions refund.",
                    "See the planners", "/planners/", "Or build a free exam study plan.", "/study-plan/"),
}

def next_step_block(t):
    h, text, btn, href, link_label, link_href = NEXT_STEP[t["slug"]]
    return f"""      <aside class="kit" aria-label="Next step">
        <div>
          <h2>{h}</h2>
          <p>{text} <a href="{link_href}">{link_label}</a></p>
        </div>
        <a class="btn" href="{href}">{btn}</a>
      </aside>"""

def feedback_block(t):
    subject = f"Feedback: {t['name']}".replace(" ", "%20")
    return f"""      <aside class="feedback" aria-label="Feedback">
        <p><strong>Something not right, or a tool you wish we had?</strong> Tell us and we’ll fix or build it.</p>
        <a class="btn btn-soft" href="mailto:hello@thefocusflowlab.com?subject={subject}">Send feedback</a>
      </aside>"""

EMBEDS = {"final-grade-calculator": 820, "gpa-calculator": 1000, "weighted-grade-calculator": 800, "test-time-calculator": 760, "reading-planner": 760, "exam-countdown": 720}

def embed_snippet(t):
    h = EMBEDS[t["slug"]]
    return (f'<iframe src="{SITE}/embed/{t["slug"]}/" title="{t["name"]} by FocusFlow Lab" width="100%" height="{h}" '
            f'style="border:0;max-width:640px" loading="lazy"></iframe>\n'
            f'<p style="font-size:14px">Free <a href="{SITE}/tools/{t["slug"]}/">{t["name"].lower()}</a> by FocusFlow Lab</p>')

def embed_block(t):
    if t["slug"] not in EMBEDS:
        return ""
    import html as _h
    return f"""      <section class="reading embed-box" aria-labelledby="embed-title">
        <h2 id="embed-title">Add this calculator to your site</h2>
        <div class="prose">
          <p>Teachers, tutors and student blogs can use this {t['name'].lower()} for free. Paste this code into your page:</p>
          <textarea id="embed-code" class="embed-code" rows="4" readonly aria-label="Embed code">{_h.escape(embed_snippet(t))}</textarea>
          <p><button class="btn btn-soft" type="button" data-copy="embed-code">Copy the code</button> <span class="copy-status" role="status" aria-live="polite"></span></p>
        </div>
      </section>"""

def embed_page(t):
    url = f"{SITE}/tools/{t['slug']}/"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t['name']} | FocusFlow Lab</title>
  <meta name="robots" content="noindex">
  <link rel="canonical" href="{url}">
  <link rel="stylesheet" href="../../assets/site.css">
  <link rel="stylesheet" href="../../study-plan/assets/plan.css">
</head>
<body class="embed">
  <main id="main" class="embed-main">
    <h1 class="visually-hidden">{t['name']}</h1>
{t['tool']}
    <p class="embed-credit">Free <a href="{url}" target="_blank" rel="noopener">{t['name'].lower()}</a> by FocusFlow Lab</p>
  </main>
<script src="/assets/tools/field.js" defer></script>
<script src="/assets/tools/{t['script']}" defer></script>
</body>
</html>
"""

EXAMPLES = {"final-grade-calculator": ["final-form", {"current": "82", "weight": "30", "target": "85"}], "gpa-calculator": ["gpa-form", {"prevGpa": "3.2", "prevCredits": "45", "targetGpa": "3.3", "nextCredits": "15"}], "exam-countdown": ["countdown-form", {"examDate": "+42", "hoursPerDay": "3", "daysPerWeek": "5"}], "reading-planner": ["reading-form", {"totalPages": "420", "pagesRead": "60", "deadline": "+21", "readDays": "6"}]}

def example_button(t):
    if t['slug'] not in EXAMPLES:
        return ''
    form, vals = EXAMPLES[t['slug']]
    return f'\n          <p class="example-row"><button class="btn btn-soft" type="button" data-example-for="{form}" data-example=\'{html.escape(json.dumps(vals))}\'>Try an example</button> <span class="example-note">Fills in sample numbers so you can see how it works.</span></p>'

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
          <p class="hero-note">Free, no sign-up. Works in your browser.</p>{example_button(t)}
        </div>
{t['tool']}
      </section>
{t.get('after', '')}

      <section class="reading">
        <h2>How to use it</h2>
        <div class="prose">
          {t['how']}
        </div>
      </section>

{faq_block(t['faq'])}

{related_block(t)}

{embed_block(t)}

{feedback_block(t)}

{next_step_block(t)}

{KIT_FORM("      ")}
    </main>"""
    return shell(path=path, title=t["title"] + " | FocusFlow Lab" if len(t["title"]) < 45 else t["title"], desc=t["desc"], og_title=t["name"] + " from FocusFlow Lab",
                 ld=ld, body=body, css_depth=2, extra_head=PLAN_CSS,
                 scripts=(f'\n<script src="/assets/tools/{t["pre"]}" defer></script>' if t.get("pre") else "") + '\n<script src="/assets/tools/field.js" defer></script>' + f'\n<script src="/assets/tools/{t["script"]}" defer></script>')

def index_page():
    path = "/tools/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Tools", path)])
    cards = "\n".join(f'        <li><a href="{t["slug"]}/"><span class="card-tag">{t["tag"]}</span><h2 class="card-name">{t["name"]}</h2><span class="card-note">{t["card"]}</span><span class="card-go">{t["go"]}</span></a></li>' for t in TOOLS)
    desc = "Free study tools that run in your browser: final grade and GPA calculators, a study schedule maker, flashcards, a focus timer and more. No sign-up."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "Free study tools", "url": SITE + path, "description": desc, "publisher": ORG,
         "mainEntity": {"@type": "ItemList", "itemListElement": [
           {"@type": "ListItem", "position": i + 1, "name": t["name"], "url": f"{SITE}/tools/{t['slug']}/"} for i, t in enumerate(TOOLS)]}}, crumb_ld]}
    body = f"""{crumb_html}

    <main id="main">
      <section class="hero single wash">
        <div>
          <h1>Free study tools.</h1>
          <p class="lead">Small tools that run in your browser. No sign-up, nothing to install.</p>
        </div>
      </section>
      <div class="plan-search guide-filter" data-filter-for="tool-cards" data-chips data-noun="tool" hidden>
        <label for="tool-search-input">Search tools</label>
        <input type="search" id="tool-search-input" placeholder="Try gpa, timer, flashcards or schedule" autocomplete="off" aria-describedby="tool-search-count">
        <div class="filter-chips" role="group" aria-label="Filter by category"></div>
        <p class="plan-search-count" id="tool-search-count" role="status" aria-live="polite"></p>
        <p class="plan-search-empty" hidden>No tool matches that yet. <a href="mailto:hello@thefocusflowlab.com?subject=Tool%20request">Tell us what you’d like us to build</a>.</p>
      </div>
      <ul class="cards" id="tool-cards">
{cards}
        <li><a href="/study-plan/"><span class="card-tag">Planning</span><h2 class="card-name">Exam study plans</h2><span class="card-note">Week-by-week plans for 14 exams, from the NCLEX and MCAT to the GMAT and CPA.</span><span class="card-go">Pick an exam</span></a></li>
      </ul>
      <section class="reading">
        <h2>Which tool do you need?</h2>
        <div class="prose">
          <p><strong>Worried about grades?</strong> The <a href="/tools/weighted-grade-calculator/">weighted grade calculator</a> shows where you stand in a course, the <a href="/tools/final-grade-calculator/">final grade calculator</a> shows what you need on the final, and the <a href="/tools/gpa-calculator/">GPA calculator</a> shows how the semester changes your GPA.</p>
          <p><strong>Exams coming up?</strong> Start with the <a href="/tools/exam-countdown/">exam countdown</a> to see your real study hours, then share them out with the <a href="/tools/study-schedule-maker/">study schedule maker</a>. For one big exam, use a <a href="/study-plan/">study plan</a> for that exam instead.</p>
          <p><strong>Need it to stick?</strong> Make <a href="/tools/flashcards/">flashcards</a>, plan reviews with the <a href="/tools/spaced-review/">spaced review calendar</a>, and get through set reading with the <a href="/tools/reading-planner/">reading planner</a>. Then sit down with the <a href="/tools/focus-timer/">focus timer</a> and do one block at a time.</p>
          <p>Everything you type stays in your browser. Nothing is sent to us.</p>
        </div>
      </section>
    </main>"""
    return shell(path=path, title="Free Study Tools: GPA, Final Grade, Flashcards and More", desc=desc, og_title="Free study tools from FocusFlow Lab",
                 ld=ld, body=body, css_depth=1, extra_head=PLAN_CSS.replace("../../", "../"))

(ROOT / "tools").mkdir(exist_ok=True)
(ROOT / "tools/index.html").write_text(index_page(), encoding="utf-8", newline="\n")
for t in TOOLS:
    out = ROOT / "tools" / t["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tool_page(t), encoding="utf-8", newline="\n")
    if t["slug"] in EMBEDS:
        emb = ROOT / "embed" / t["slug"] / "index.html"
        emb.parent.mkdir(parents=True, exist_ok=True)
        emb.write_text(embed_page(t), encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT).as_posix())
