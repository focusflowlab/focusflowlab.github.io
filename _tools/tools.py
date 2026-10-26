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
       faq=[("How is the score I need worked out?", "Needed score = (target grade − current grade × (1 − final weight)) ÷ final weight, with the weight as a decimal. So a final worth 25% uses 0.25."),
            ("What if the answer is over 100%?", "Then the target can’t be reached on the final alone, unless your course has extra credit. Try the next grade down to see what is reachable."),
            ("Does it work for weighted categories?", "If your grade comes from several weighted categories, work out your current grade first with the weighted grade calculator, then use that number here.")],
       script="final-grade.js"),
  dict(slug="gpa-calculator", name="GPA calculator", tag="Grades",
       title="GPA Calculator: Semester and Cumulative GPA (4.0 Scale)",
       desc="Work out your semester GPA from letter grades and credits on the US 4.0 scale, and your new cumulative GPA. Free, saves in your browser.",
       h1="Work out your GPA.",
       lead="Add your courses, credits and letter grades. Your GPA updates as you type.",
       card="Semester and cumulative GPA on the 4.0 scale.",
       go="Calculate my GPA",
       tool="""        <form class="sheet" id="gpa-form" novalidate aria-label="GPA calculator">
          <p class="sheet-title">This semester</p>
          <div class="row-head" aria-hidden="true"><span>Course</span><span>Credits</span><span>Grade</span><span></span></div>
          <ol class="tool-rows" id="gpa-rows"></ol>
          <div class="sheet-actions"><button class="btn btn-soft" type="button" id="add-course">Add a course</button></div>
          <fieldset><legend>Past GPA (optional, for cumulative)</legend>
            <div class="fields fields-2b">
              <div><label for="prevGpa">Current cumulative GPA</label><input type="number" id="prevGpa" min="0" max="4" step="0.01" placeholder="3.40" inputmode="decimal"></div>
              <div><label for="prevCredits">Credits so far</label><input type="number" id="prevCredits" min="0" step="1" placeholder="45" inputmode="numeric"></div>
            </div>
          </fieldset>
          <div class="count-result" aria-live="polite">
            <dl class="totals">
              <div><dt>Semester GPA</dt><dd id="r-term">–</dd></div>
              <div><dt>Credits</dt><dd id="r-credits">0</dd></div>
              <div><dt>Cumulative GPA</dt><dd id="r-cum">–</dd></div>
            </dl>
          </div>
        </form>""",
       how="""<p>GPA is an average of grade points, weighted by credits, so a 4-credit course counts more than a 1-credit one. This calculator uses the common US 4.0 scale: A = 4.0, A− = 3.7, B+ = 3.3, B = 3.0, and so on down to F = 0.</p>
          <ul>
            <li><strong>Check your school’s scale.</strong> Some schools give A+ a 4.3, and some don’t use plus or minus grades. Your transcript or student handbook says which.</li>
            <li><strong>For cumulative GPA,</strong> add your current GPA and the credits it covers. The calculator combines them with this semester.</li>
            <li><strong>Pass/fail courses</strong> usually don’t count toward GPA, so leave them out.</li>
          </ul>""",
       faq=[("How is GPA calculated?", "Multiply each course’s grade points by its credits, add those up, and divide by the total credits. A 3-credit A (4.0) and a 4-credit B (3.0) give (12 + 12) ÷ 7 = 3.43."),
            ("Does an A+ count as 4.3?", "At some schools, yes. This calculator uses 4.0 for an A+, which is the most common rule. Check your school’s policy."),
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
       desc="Add your subjects and exam dates, set your daily hours, and get a week-by-week study schedule that gives nearer exams more time. Free and printable.",
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
       faq=[("How does it decide hours per subject?", "Each study day, subjects with an upcoming exam share your hours. A subject’s share grows with the work it needs (Light, Normal, Heavy) and as its exam gets closer."),
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
          <div class="fields">
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
          </ul>""",
       faq=[("How are pages per day worked out?", "Pages left ÷ reading days before the deadline, rounded up. Review days and rest days aren’t counted as reading days."),
            ("Does it count today?", "Yes. The plan starts today and ends the day before your deadline."),
            ("Is my plan saved?", "Yes, in this browser only, so you can come back and update the pages you’ve read.")],
       script="reading-planner.js"),
  dict(slug="flashcards", name="Flashcards", tag="Memory",
       title="Free Flashcards with Spaced Repetition (No Sign-up)",
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
{t.get('after', '')}

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
    desc = "Free study tools that run in your browser: final grade and GPA calculators, a study schedule maker, flashcards, a focus timer and more. No sign-up."
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
    return shell(path=path, title="Free Study Tools: GPA, Final Grade, Flashcards and More", desc=desc, og_title="Free study tools from FocusFlow Lab",
                 ld=ld, body=body, css_depth=1, extra_head=PLAN_CSS.replace("../../", "../"))

(ROOT / "tools").mkdir(exist_ok=True)
(ROOT / "tools/index.html").write_text(index_page(), encoding="utf-8", newline="\n")
for t in TOOLS:
    out = ROOT / "tools" / t["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tool_page(t), encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT).as_posix())
