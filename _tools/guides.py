"""Generate /guides/ pages.  Run: cd _tools && python guides.py && cd .. && python _tools/build.py"""
import pathlib, re
from common import shell, crumbs, ORG, SITE, TRACKER_FORM

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLISHED = "2026-10-26"

def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

GUIDES = [
  dict(slug="stop-checking-phone-while-studying", tag="Focus", video="PS4G5gRFrBU",
       title="How to Stop Checking Your Phone While Studying",
       h1="How to stop checking your phone while studying",
       desc="Willpower loses to a phone within reach. Here is how to use distance and friction so you stop checking your phone while you study.",
       lead="Willpower loses to a phone within reach. Distance and friction win.",
       card="Use distance and friction instead of willpower.",
       sections=[
         ("Why willpower keeps losing", """<p>Every time your phone lights up, part of your attention goes with it, even if you don’t pick it up. Researchers at the University of Texas found that people did worse on attention and memory tasks when their phone was simply on the desk, face down and silent, than when it was in another room (Ward et al., 2017).</p>
<p>So the goal isn’t to resist the phone better. It’s to make checking it slow and awkward enough that you don’t bother.</p>"""),
         ("Put distance between you and it", """<p>The simplest barrier is space. Before a focus block, put the phone in another room, or at least in a bag across the room. If you need it for two-factor codes or emergencies, leave it where you can hear a call but can’t see the screen.</p>
<p>Face down on the desk doesn’t count. It’s still in reach, and still pulling at you.</p>"""),
         ("Add friction to every check", """<p>Make each check take a few extra steps:</p>
<ul>
<li>Put the phone in a drawer, a zipped bag or a box with a lid.</li>
<li>Turn on Focus mode or Do Not Disturb, and allow only calls from a few people.</li>
<li>Log out of the one app you open without thinking, for the length of the block.</li>
</ul>
<p>Each step is small. Together they turn “just checking” into a decision, and most of the time you’ll decide not to.</p>
<p>The same idea applies on a laptop, where a site blocker is easy to switch off. <a href="/guides/why-website-blockers-fail/">Why website blockers fail</a> covers what to do instead.</p>"""),
         ("Give your brain a time to check", """<p>Checking is easier to skip when you know when you can do it. Study in set blocks, then check your phone in the break. The <a href="/tools/focus-timer/">focus timer</a> does this for you: a 25 to 50 minute block, then a short break.</p>"""),
         ("Write down what pulls you away", """<p>Keep a scrap of paper next to you. When you feel the urge to check, write down why: a message you’re waiting for, boredom, a hard question. After a few days you’ll see a pattern, and you can plan for it. The free Study Focus Kit has a worksheet for exactly this.</p>"""),
       ]),
  dict(slug="active-recall-notes", tag="Memory", video="Sbtml3TtQK0",
       title="Why Highlighting Fails and How to Take Notes You Remember",
       h1="Why highlighting fails, and how to take notes you remember",
       desc="Highlighting feels productive but does little for memory. Here is how to turn your notes into questions and use active recall instead.",
       lead="Highlighting feels like work. It mostly isn’t. Here’s what to do instead.",
       card="Turn notes into questions and test yourself.",
       sections=[
         ("The problem with highlighting", """<p>In a well-known review of ten common study methods, John Dunlosky and colleagues rated highlighting and re-reading as low utility: they don’t do much for long-term memory (Dunlosky et al., 2013). Highlighting feels productive because the page looks worked on, but your brain only had to decide what looked important, not remember it.</p>"""),
         ("What works better: active recall", """<p>Active recall means pulling information out of your memory instead of reading it again. Each time you recall something, it gets easier to recall the next time. The same review rated practice testing as one of the two most useful methods.</p>"""),
         ("Turn your notes into questions", """<ol>
<li>Split your page: a narrow column on the left, notes on the right.</li>
<li>After a lecture or chapter, write a question in the left column for each main point. “What are the three causes of…?”, not “Causes”.</li>
<li>To review, cover the right side and answer each question out loud or on paper.</li>
<li>Check, and mark the ones you missed. Those are your next review.</li>
</ol>"""),
         ("Keep it short", """<p>You don’t need beautiful notes. A question you can answer in ten seconds is better than a paragraph you’ll never read again. If you’re copying a sentence word for word, stop and ask what question it answers.</p>"""),
         ("Space the reviews out", """<p>Answering the questions once helps. Answering them again a day later, then a few days later, helps much more. The <a href="/tools/spaced-review/">spaced review calendar</a> gives you the dates and adds them to your calendar.</p>"""),
       ]),
  dict(slug="brain-dump-before-studying", tag="Focus", video="RVNiYBN6BOo",
       title="How to Clear Mental Clutter Before Studying: The Brain Dump",
       h1="How to clear mental clutter before studying",
       desc="A 3-minute brain dump gets the noise out of your head before a study session. Here is how to do it and what to do with the list after.",
       lead="Three minutes on paper before you start, so your head is free for the work.",
       card="A 3-minute brain dump before you start.",
       sections=[
         ("Why your mind wanders at the start", """<p>The first ten minutes of a study session are when unfinished things pop up: the email you didn’t send, the form that’s due, what’s for dinner. Each one is small, but they keep coming back because your brain doesn’t want to forget them.</p>
<p>Writing them down tells your brain they’re safe somewhere else. A study by E. J. Masicampo and Roy Baumeister found that making a specific plan for an unfinished task cut down how often it intruded on people’s thoughts during later work (Masicampo &amp; Baumeister, 2011).</p>"""),
         ("How to do a brain dump", """<ol>
<li>Set a timer for three minutes.</li>
<li>Write down everything on your mind: tasks, worries, ideas, reminders. No order, no full sentences.</li>
<li>When the timer ends, stop, even if more is coming.</li>
</ol>"""),
         ("Sort the list in one minute", """<p>Go down the list and mark each item:</p>
<ul>
<li><strong>Now:</strong> takes under two minutes. Do it before you study, then cross it off.</li>
<li><strong>Later:</strong> give it a time, like “after dinner” or “Saturday morning”.</li>
<li><strong>Let go:</strong> things you can’t act on today. Writing them down was enough.</li>
</ul>"""),
         ("Then start, straight away", """<p>Pick the first study task and start a focus block right away, before anything new comes up. The <a href="/tools/focus-timer/">focus timer</a> is built for this. If something new pops into your head during the block, add it to the list and keep going.</p>"""),
       ]),
  dict(slug="stop-rereading-cover-syllabus-faster", tag="Planning", video="cajWz2utoaM",
       title="Why Re-reading Won’t Finish Your Syllabus (and What Will)",
       h1="Why re-reading won’t finish your syllabus",
       desc="Re-reading feels safe but is slow and does little for memory. Here is how to cover your syllabus faster with retrieval practice and a weekly plan.",
       lead="Re-reading feels safe. It’s also the slowest way through a syllabus.",
       card="Cover more ground with retrieval, not re-reading.",
       sections=[
         ("Why re-reading feels like it works", """<p>The second time you read a chapter, it feels familiar, and familiar feels like knowing. But recognizing something on the page isn’t the same as being able to recall it in an exam. In one well-known experiment, students who practiced recalling material remembered far more a week later than students who kept re-studying it (Karpicke &amp; Roediger, 2008).</p>"""),
         ("Read once, then test", """<ol>
<li>Read a section once, carefully.</li>
<li>Close the book and write down the main points from memory.</li>
<li>Open it again and check. Add what you missed in a different colour.</li>
<li>Move on. Don’t read it again until a review day.</li>
</ol>
<p>This is slower per page the first time, but you won’t need three more passes.</p>"""),
         ("Use past papers early", """<p>Past papers and practice questions show you what the exam actually asks. Look at a few before you start a topic, then study with those questions in mind. You’ll spend less time on details that never come up.</p>"""),
         ("Plan by the week, not the day", """<p>List every topic, then spread them across the weeks you have, with the biggest and weakest first. A weekly target bends when a day goes wrong. A daily schedule usually breaks. The <a href="/tools/exam-countdown/">exam countdown</a> shows how many study hours you really have, and the <a href="/study-plan/">study plan generators</a> lay out the weeks for big exams.</p>"""),
         ("Review on a schedule", """<p>Come back to each topic a day later, a few days later and a couple of weeks later, recalling first each time. The <a href="/tools/spaced-review/">spaced review calendar</a> gives you the dates.</p>"""),
       ]),
  dict(slug="how-to-study-for-finals-in-a-week", tag="Finals", date="2026-10-27",
       title="Study for Finals in a Week: A Day-by-Day Plan",
       h1="How to study for finals in a week",
       desc="A day-by-day plan for studying for finals in one week: sort your exams, learn by recall, practise under time pressure, and sleep before the exam.",
       lead="Seven days, several exams. Here’s a plan that fits, day by day.",
       card="A day-by-day plan for the last week before finals.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("Start with the numbers", """<p>A week sounds like a lot until you count it. Five study days at five hours is 25 hours, shared between every exam you have. Put your exam dates and daily hours into the <a href="/tools/exam-countdown/">exam countdown</a> to see your real total before you plan anything.</p>
<p>Then check what each exam is worth to you. The <a href="/tools/final-grade-calculator/">final grade calculator</a> shows the score you need on each final for the grade you want. An exam where you need 60% to keep an A gets less time than one where you need 85% to pass.</p>"""),
         ("Day 7: sort everything", """<ul>
<li>List every exam, its date and the topics it covers. Use the syllabus or review sheet, not memory.</li>
<li>Mark each topic: know it, shaky, or haven’t learned it.</li>
<li>Find past papers or practice questions for every exam. These decide what you study.</li>
<li>Put your exams into the <a href="/tools/study-schedule-maker/">study schedule maker</a> to split your hours across subjects.</li>
</ul>"""),
         ("Days 6 to 4: learn by recall", """<p>Work through the shaky and unlearned topics, biggest first. For each one, read it once, close your notes, and write down what you remember. Then check and fill the gaps. This is slower than re-reading, but it’s the part that sticks.</p>
<p>Switch subjects during the day instead of spending a whole day on one. Mixing topics feels harder, but it helps you tell similar problems apart on the exam.</p>
<p>Work in focus blocks with short breaks. The <a href="/tools/focus-timer/">focus timer</a> runs 25, 45 or 50 minute blocks.</p>"""),
         ("Days 3 and 2: practise like the exam", """<ul>
<li>Do past papers or practice sets under time pressure, with your notes closed.</li>
<li>Mark them straight away. For every mistake, write down why: didn’t know it, misread it, or ran out of time.</li>
<li>Spend the rest of the day on the mistakes, not on what you already got right.</li>
</ul>"""),
         ("Day 1: review and rest", """<p>No new topics. Go through your mistake list, recall the main formulas and points from memory, and stop early. Sleep matters more than one more hour of studying: memory consolidates while you sleep, and a tired brain loses marks on easy questions.</p>"""),
         ("If you have two exams close together", """<p>Study for the first exam in the morning and the second in the afternoon until the first is done, then switch fully to the second. The <a href="/guides/how-to-study-for-multiple-exams/">guide to studying for multiple exams</a> covers this in more detail.</p>"""),
       ]),
  dict(slug="how-to-study-for-multiple-exams", tag="Finals", date="2026-10-27",
       title="How to Study for Multiple Exams in the Same Week",
       h1="How to study for multiple exams in the same week",
       desc="Several exams in one week? Split your hours by what each exam needs, study more than one subject a day, and switch focus as each exam passes.",
       lead="Three exams, one week. Split the time on purpose, not by panic.",
       card="Split your time across several exams without panic.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("Don’t study in exam order", """<p>The common mistake is studying for the first exam until it’s over, then starting the second. By then the third has no time left. Spread your study across every exam from the start, with more time for the ones that are sooner or harder.</p>"""),
         ("Weigh each exam", """<p>Give each exam a weight from two things: how much work it needs, and how much the grade matters. A heavy subject where you’re borderline gets the most hours. A light one where you’re safe gets the least. The <a href="/tools/final-grade-calculator/">final grade calculator</a> tells you where you’re safe.</p>
<p>The <a href="/tools/study-schedule-maker/">study schedule maker</a> does this split for you: add each subject, its exam date and how much work it needs, and it shares out your daily hours, with more time for the exam that comes first.</p>"""),
         ("Mix subjects in the same day", """<p>Study two or three subjects each day instead of one. Mixed practice feels harder while you’re doing it, but it leads to better results on the test. In one study, students who mixed different kinds of maths problems scored far higher a week later than students who practised one kind at a time.</p>"""),
         ("Switch focus as exams pass", """<p>The day before each exam, give it most of your time and keep the others ticking over with short recall sessions. After the exam, drop it completely and move its hours to the next one.</p>"""),
         ("Keep each day realistic", """<ul>
<li>Plan in focus blocks, for example four to six blocks of 45 minutes with breaks.</li>
<li>Start each day with a short review of yesterday’s topics, from memory.</li>
<li>Stop at a set time. Sleep is when today’s studying sticks.</li>
</ul>"""),
       ]),
  dict(slug="does-cramming-work", tag="Finals", date="2026-10-27",
       title="Does Cramming Work? How to Cram If You Must",
       h1="Does cramming work?",
       desc="Cramming gets some facts through one exam but fades fast. Here’s what research says, and how to cram better if you’re out of time.",
       lead="It can get you through tomorrow. It won’t get you through the course.",
       card="What research says, and how to cram better if you must.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("The short answer", """<p>Cramming can get you through a test the next day. But what you cram fades fast, and spreading the same study time over several days works better. In one flashcard study, spacing beat cramming for 90% of students, yet most of them believed cramming had worked better. Cramming feels effective because the material feels familiar while you’re doing it.</p>"""),
         ("Why it feels like it works", """<p>When you’ve just read something five times, it feels easy to recognise. Recognising isn’t the same as recalling it in an exam, with nothing in front of you. That gap is why crammed material can vanish when you see the question.</p>"""),
         ("If you have to cram tonight", """<ol>
<li><strong>Pick what’s worth points.</strong> Look at past papers or the review sheet and cover those topics first.</li>
<li><strong>Test yourself instead of re-reading.</strong> Read a section once, close the book, write what you remember, then check.</li>
<li><strong>Do practice questions.</strong> Even a few past questions show you what the exam wants.</li>
<li><strong>Take short breaks</strong> every 45 to 50 minutes. The <a href="/tools/focus-timer/">focus timer</a> keeps you honest.</li>
<li><strong>Sleep.</strong> An all-nighter costs you on the easy questions. Stop in time to get some sleep.</li>
</ol>"""),
         ("The same 6 hours, two ways", """<p>Say you have six hours to give one exam. Here is how cramming and spacing use them:</p>
<div class="table-scroll"><table class="mini-table">
<thead><tr><th scope="col">Plan</th><th scope="col">How the hours are used</th><th scope="col">What you get</th></tr></thead>
<tbody>
<tr><td>Cram</td><td>6 hours the night before</td><td>One long read-through. Familiar by morning, but no practice at recalling it, and little time to repeat anything.</td></tr>
<tr><td>Spaced</td><td>Three 2-hour sessions over three days: learn and test, review and test, test again</td><td>Each topic is recalled three times, with a night’s sleep between. Weak spots show up while you can still fix them.</td></tr>
</tbody></table></div>
<p>The hours are the same. The spaced plan only needs you to start three days earlier. If you have just one night, use the cram steps above and still test yourself instead of re-reading.</p>"""),
         ("Common questions", """<p><strong>Is it better to cram or sleep?</strong> If you have to choose, sleep. Staying up all night costs you attention on the exam itself, and you can’t recall what you can’t think clearly about.</p>
<p><strong>Can I cram for an exam I’ll need again later?</strong> You can pass tomorrow, but it won’t last. Cumulative exams, such as a final or a board exam, need spaced review from the start. The <a href="/guides/how-long-to-study-for-exams/">study hours guide</a> shows typical prep times.</p>
<p><strong>How many days before an exam should I start?</strong> More than one, and ideally enough to review each topic at least twice. The <a href="/tools/exam-countdown/">exam countdown calculator</a> shows how many study days you have left, and the <a href="/guides/how-to-create-a-study-schedule/">study schedule guide</a> turns them into a plan.</p>"""),
         ("Next time, space it out", """<p>Study the same hours across more days instead. Review each topic a day later, a few days later and a week later. The <a href="/tools/spaced-review/">spaced review calendar</a> and <a href="/tools/flashcards/">flashcards</a> do the scheduling for you.</p>"""),
       ]),
  dict(slug="stop-procrastinating-studying", tag="Focus", date="2026-10-27",
       title="How to Stop Procrastinating and Start Studying",
       h1="How to stop procrastinating and start studying",
       desc="Procrastination is about how a task feels, not laziness. Make the first step tiny, set an if-then plan, and remove the easiest escape.",
       lead="It’s not laziness. It’s how the task feels. Change that, and starting gets easier.",
       card="Make starting easy: tiny first steps and if-then plans.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions and starting a study session.",
       sections=[
         ("Why you put it off", """<p>Research on procrastination keeps finding the same pattern: we delay tasks that feel unpleasant, especially when the reward is far away and something easier is close at hand. A big, vague task like “study for biology” is all three: unpleasant, far from any reward, and competing with your phone.</p>"""),
         ("Make the first step tiny", """<p>“Study for biology” is hard to start. “Write down what I remember about cell respiration for five minutes” isn’t. Shrink the first step until it feels almost silly. Once you’ve started, carrying on is much easier than starting was.</p>"""),
         ("Use an if-then plan", """<p>Decide exactly when and where you’ll start: “If it’s 7pm, then I sit at my desk and open chapter 4.” Plans like this, called implementation intentions, made people noticeably more likely to follow through on their goals across many studies.</p>"""),
         ("Remove the easy escape", """<p>Put your phone in another room before you start. If it’s within reach, checking it will always be easier than studying. The <a href="/guides/stop-checking-phone-while-studying/">phone guide</a> has more ways to add distance.</p>"""),
         ("Start with a timer", """<p>Commit to one focus block, not the whole evening. The <a href="/tools/focus-timer/">focus timer</a> runs 25, 45 or 50 minutes. When it ends, you can stop. Most of the time you won’t want to.</p>"""),
         ("Clear your head first", """<p>If other worries keep pulling you away, spend three minutes writing them all down before you start. The <a href="/guides/brain-dump-before-studying/">brain dump guide</a> shows how.</p>"""),
       ]),
  dict(slug="how-long-to-study-for-exams", tag="Planning", date="2026-10-27",
       title="How Long to Study for the NCLEX, MCAT, USMLE, GRE",
       h1="How long should you study for each exam?",
       desc="Typical study hours and weeks for the NCLEX, TEAS, MCAT, USMLE Step 1, PANCE, NAPLEX, DAT, GRE, GMAT, LSAT and CPA, side by side, and how to turn them into a plan.",
       lead="The common ranges for 14 exams in one table, and how to work out where you fit.",
       card="Study hours for 14 exams, side by side.",
       kit="The free Study Focus Kit has printable worksheets for planning and long study days.",
       sections=[
         ("The numbers", """<p>These are the ranges students and prep programs commonly plan around. They are starting points, not rules: your background, your target score and how recently you studied the material move you up or down the range.</p>
<div class="table-scroll"><table class="mini-table">
<thead><tr><th scope="col">Exam</th><th scope="col">Test length</th><th scope="col">Common prep time</th><th scope="col">Hours, roughly</th></tr></thead>
<tbody>
<tr><td><a href="/study-plan/nclex/">NCLEX-RN</a></td><td>85 to 150 questions, up to 5 hours</td><td>6 to 8 weeks</td><td>150 to 300</td></tr>
<tr><td><a href="/study-plan/nclex-pn/">NCLEX-PN</a></td><td>85 to 150 questions, up to 5 hours</td><td>5 to 8 weeks</td><td>120 to 250</td></tr>
<tr><td><a href="/study-plan/teas/">ATI TEAS</a></td><td>170 questions, about 3.5 hours</td><td>4 to 8 weeks</td><td>30 to 80</td></tr>
<tr><td><a href="/study-plan/mcat/">MCAT</a></td><td>230 questions, about 7.5 hours with breaks</td><td>3 to 6 months</td><td>300 to 500</td></tr>
<tr><td><a href="/study-plan/usmle-step-1/">USMLE Step 1</a></td><td>Up to 280 questions, one 8-hour day</td><td>6 to 8 weeks dedicated</td><td>300 to 600</td></tr>
<tr><td><a href="/study-plan/pance/">PANCE</a></td><td>300 questions, 5 hours</td><td>6 to 12 weeks</td><td>150 to 350</td></tr>
<tr><td><a href="/study-plan/naplex/">NAPLEX</a></td><td>225 questions, 6 hours</td><td>6 to 10 weeks</td><td>120 to 300</td></tr>
<tr><td><a href="/study-plan/dat/">DAT</a></td><td>About 4.5 hours</td><td>2 to 3 months</td><td>200 to 350</td></tr>
<tr><td><a href="/study-plan/gre/">GRE</a></td><td>About 2 hours</td><td>1 to 3 months</td><td>60 to 150</td></tr>
<tr><td><a href="/study-plan/gmat/">GMAT</a></td><td>64 questions, 2 hours 15 minutes</td><td>2 to 3 months</td><td>80 to 150</td></tr>
<tr><td><a href="/study-plan/lsat/">LSAT</a></td><td>Four 35-minute sections plus writing</td><td>3 to 6 months</td><td>150 to 300</td></tr>
<tr><td><a href="/study-plan/cpa-far/">CPA FAR</a></td><td>4 hours</td><td>8 to 12 weeks</td><td>100 to 180</td></tr>
<tr><td><a href="/study-plan/cpa-aud/">CPA AUD</a></td><td>4 hours</td><td>6 to 10 weeks</td><td>90 to 150</td></tr>
<tr><td><a href="/study-plan/cpa-reg/">CPA REG</a></td><td>4 hours</td><td>6 to 10 weeks</td><td>90 to 150</td></tr>
</tbody></table></div>
<p>Test lengths come from each exam’s official site and can change, so check before you book. Each exam name links to a free plan that turns your own date and hours into a week-by-week schedule.</p>"""),
         ("Where you fit in the range", """<ul>
<li><strong>Use the low end</strong> if you studied the material recently, your practice scores are already near your target, or the exam is pass/fail and you’re comfortably passing practice tests.</li>
<li><strong>Use the high end</strong> if it’s been years since the coursework, your first practice test is well below your target, or you’re aiming for a competitive score.</li>
<li><strong>Take a practice test first.</strong> It tells you more than any table. Plan from the gap between that score and your target.</li>
</ul>"""),
         ("Turn hours into weeks", """<p>Divide your hours by what you can really study each week. 200 hours at 4 hours a day, 5 days a week, is 10 weeks. If that runs past your test date, either add hours per week or move the date. The <a href="/tools/exam-countdown/">exam countdown</a> shows how many study hours you have left before a date.</p>"""),
         ("Spread it out", """<p>The same hours spread over more weeks beat the same hours crammed into fewer. Spacing your review out over time is one of the most reliable findings in learning research. Leave the last few days light, and sleep properly before the exam.</p>"""),
       ]),
  dict(slug="how-to-study-for-the-nclex", tag="Exam plans", signup="nclex", date="2026-10-28",
       title="How to Study for the NCLEX: A 4 to 8 Week Plan That Works",
       h1="How to study for the NCLEX",
       desc="How to study for the NCLEX-RN in 4 to 8 weeks: how the exam works, how to split your time across the client needs categories, and a week-by-week plan.",
       lead="How the exam works, where your hours should go, and a plan you can start this week.",
       card="A 4 to 8 week NCLEX plan, weighted to the test plan.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the NCLEX works", """<p>The NCLEX-RN is a computerized adaptive test. It gives you between 85 and 150 questions in up to 5 hours, and each question adapts to how you answered the last one. Since April 2023 it has been the Next Generation NCLEX, which includes case studies that test clinical judgment across several linked questions.</p>
<p>Because the test adapts, you can’t cram a few topics and hope they come up. You need steady practice across all of it, and the habit of reasoning through each question.</p>"""),
         ("Split your time by the test plan", """<p>NCSBN publishes the share of questions in each client needs category. The biggest are Management of Care and Pharmacological and Parenteral Therapies, so they deserve the most hours. Smaller areas still need regular practice because every category appears on the exam.</p>
<p>Start with a practice assessment to find your weak categories, then give those extra time. The free <a href="/study-plan/nclex/">NCLEX study plan generator</a> does this split for you from your exam date and hours.</p>
<p>Prefer paper? The <a href="/planners/nclex-rn-8-week-planner/">NCLEX-RN 8-week planner</a> and the <a href="/planners/nclex-pn-6-week-planner/">NCLEX-PN 6-week planner</a> have an exam map, weekly and daily pages and an error log for $5 each. They are independent study materials, not from NCSBN.</p>"""),
         ("A 6-week plan", """<ul>
<li><strong>Weeks 1 to 3: content plus questions.</strong> Review one or two categories a day, biggest first. End each day with 50 to 75 practice questions on what you covered, and read every rationale, including for questions you got right.</li>
<li><strong>Weeks 4 and 5: mixed practice.</strong> Do larger blocks of mixed questions, including case studies. Keep an error log: the concept you missed and why. Review that log instead of re-reading notes.</li>
<li><strong>Week 6: readiness and rest.</strong> One or two readiness assessments early in the week, then light review of your error log. No new content in the last two days, and rest the day before.</li>
</ul>
<p>Only have 4 weeks? Keep the same order and shorten each part. Have 8? Stretch the first part and add more mixed practice.</p>"""),
         ("How many hours a day", """<p>Most people plan around 150 to 300 hours in total, often 3 to 5 hours a day for 6 to 8 weeks. If you’re working, fewer hours over more weeks is fine. The <a href="/guides/how-long-to-study-for-exams/">study hours guide</a> compares the NCLEX with other exams.</p>"""),
         ("What makes the difference", """<ul>
<li><strong>Rationales over scores.</strong> Understanding why an answer is right teaches you more than the percentage.</li>
<li><strong>Focus blocks.</strong> Work in 45 to 50 minute blocks with your phone in another room. The <a href="/tools/focus-timer/">focus timer</a> helps.</li>
<li><strong>Spaced review.</strong> Come back to weak topics after a day, a few days and a week. The <a href="/tools/spaced-review/">spaced review calendar</a> schedules it.</li>
</ul>"""),
       ]),
  dict(slug="mcat-study-schedule-3-months", tag="Exam plans", signup="mcat", video="afsZPhkmd4M", date="2026-10-28",
       title="MCAT Study Schedule: A 3-Month Plan, Week by Week",
       h1="A 3-month MCAT study schedule",
       desc="A 3-month MCAT study schedule: how to split time across the four sections, when to take full-length practice exams, and how many hours to plan.",
       lead="Twelve weeks, four sections. Here’s how to divide them.",
       card="A 12-week MCAT schedule with practice exams in the right place.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the MCAT is built", """<p>The MCAT has four sections, each scored from 118 to 132 for a total of 472 to 528: Chemical and Physical Foundations, Critical Analysis and Reasoning Skills (CARS), Biological and Biochemical Foundations, and Psychological, Social and Biological Foundations. With breaks, test day is about 7.5 hours.</p>"""),
         ("Before you start: take a diagnostic", """<p>Take one full-length practice exam, untimed if you need to, before planning anything. It shows which sections need the most time. Many students plan 300 to 500 hours in total; your diagnostic tells you where in that range you are.</p>"""),
         ("Weeks 1 to 6: content", """<ul>
<li>Review content by section, giving the most time to your weakest.</li>
<li>Do CARS passages every week from the start. Reading skill builds slowly, so it can’t wait until the end.</li>
<li>End each day with practice questions on what you covered, and keep an <a href=\"/guides/mcat-error-log-template/\">error log</a>.</li>
<li>Use flashcards for facts like amino acids, hormones and equations, reviewed a little every day. The free <a href="/tools/flashcards/">flashcards</a> space the reviews for you.</li>
</ul>"""),
         ("Weeks 7 to 11: practice exams", """<ul>
<li>Take one full-length practice exam a week, at the same time of day as your real test.</li>
<li>Spend at least as long reviewing each exam as taking it. Every miss goes in the error log with the reason.</li>
<li>On other days, go back to the content behind your misses, and keep CARS practice going.</li>
</ul>
<p>The official AAMC practice exams are closest to the real test, so save some for these weeks.</p>"""),
         ("Week 12: taper", """<p>One last practice exam early in the week, then light review of your error log. No new content in the last two days. Sleep well the night before; test day is long.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 3 months? The free <a href="/study-plan/mcat/">MCAT study schedule generator</a> builds the same structure from your test date and daily hours, with CARS every week and practice exams where they belong.</p>"""),
       ]),
  dict(slug="mcat-error-log-template", tag="Exam plans", signup="mcat", date="2026-11-02",
       title="MCAT Error Log Template: How to Track and Fix Your Mistakes",
       h1="An MCAT error log template, and how to use it",
       desc="A simple MCAT error log template with three reasons for every miss, plus how to read it each week so your practice questions change what you do next.",
       lead="A short log of why you miss questions shows patterns that re-doing the question never will.",
       card="A simple error log template and how to review it each week.",
       sections=[
         ("What an MCAT error log does", """<p>An error log is a running list of the questions you get wrong, with the reason you got each one wrong. Re-doing a missed question fixes that question. Logging the reason shows the pattern behind many of them, and a pattern is something you can change.</p>
<p>Keep it short enough to finish. If filling in a row takes longer than the question did, you will stop by week three.</p>"""),
         ("The template", """<p>Copy these columns into a notebook or a spreadsheet. The first row is an example.</p>
<div class="table-scroll"><table class="mini-table template-table">
<thead><tr><th scope="col">Date</th><th scope="col">Source</th><th scope="col">Section</th><th scope="col">Topic</th><th scope="col">Why (C, M or T)</th><th scope="col">Next time I will</th></tr></thead>
<tbody>
<tr><td>Example</td><td>Practice exam</td><td>Bio/Biochem</td><td>Enzyme inhibition graph</td><td>M</td><td>Say what each axis shows before I read the answers</td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</tbody></table></div>
<p class="download-row"><a class="btn" href="/assets/templates/mcat-error-log-template.xlsx" download>Download the spreadsheet (.xlsx)</a> <a class="btn btn-soft" href="/assets/templates/mcat-error-log-template.csv" download>Download as CSV</a></p>
<p>The spreadsheet works in Excel, Numbers and Google Sheets (upload it to Google Drive, or use File, then Import). It has drop-down lists for the section and the reason, fills in a retest date for you (7 days after a content gap, 2 days after the others), and counts your reasons on a second tab.</p>
<p>Prefer to keep it online? The free <a href="/tools/error-log/">error log tool</a> does the same job for any exam and saves in your browser. Prefer paper? The free MCAT tracker has a printable version of this log. You can get it with the form at the end of this page.</p>"""),
         ("The three reasons", """<p>Pick one letter for every miss. If two apply, pick the one you can fix first.</p>
<ul>
<li><strong>C, content gap.</strong> You didn’t know the fact or concept, or couldn’t recall it.</li>
<li><strong>M, misread.</strong> You knew the content but misread the question or the passage, or fell for a tempting wrong answer.</li>
<li><strong>T, timing.</strong> You rushed, guessed or ran out of time.</li>
</ul>"""),
         ("What to log", """<ul>
<li>Every question you miss, from question sets and from full-length practice exams.</li>
<li>Questions you guessed and got right. A lucky guess is still a gap.</li>
<li>For CARS, one line on why the wrong answer was tempting.</li>
</ul>
<p>One line per row. The last column matters most: a rule you can follow the next time you see the same thing.</p>"""),
         ("Read it once a week", """<p>At the end of each week, count the letters.</p>
<ul>
<li><strong>Mostly C:</strong> go back to that content, then test yourself on it with <a href="/tools/flashcards/">flashcards</a> or the <a href="/tools/spaced-review/">spaced review calendar</a>.</li>
<li><strong>Mostly M:</strong> slow down on the question stem. Put the question in your own words before you look at the choices.</li>
<li><strong>Mostly T:</strong> practise in shorter timed sets, then build up to full sections.</li>
</ul>
<p>These are starting points. Your own pattern matters more than any rule.</p>"""),
         ("Where it fits in your schedule", """<p>Fill in the log right after every question set and every full-length exam, and spend at least as long reviewing as you spent testing. The <a href="/guides/mcat-study-schedule-3-months/">3-month MCAT schedule</a> shows where the practice exams go, and the free <a href="/study-plan/mcat/">MCAT study schedule generator</a> builds the same structure from your test date.</p>
<p>Prefer paper? The <a href="/planners/mcat-16-week-planner/">MCAT 16-week planner</a> has an error log page, a full-length test log and a weekly page for $5.</p>"""),
       ]),
  dict(slug="how-to-study-for-the-teas", tag="Exam plans", signup="teas", date="2026-10-28",
       title="How to Study for the TEAS 7: Sections, Timing and a 4-Week Plan",
       h1="How to study for the TEAS",
       desc="How to study for the ATI TEAS 7: what each section covers, how long it takes, and a 4-week plan that gives science and math the time they need.",
       lead="What’s on each section, and a 4-week plan to cover it.",
       card="A 4-week TEAS plan, section by section.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("What’s on the TEAS 7", """<p>The ATI TEAS 7 has 170 questions in 209 minutes, across four sections:</p>
<ul>
<li><strong>Reading:</strong> 45 questions in 55 minutes. Key ideas, craft and structure, and using information from more than one source.</li>
<li><strong>Math:</strong> 38 questions in 57 minutes. Numbers, algebra, measurement and data. An on-screen calculator is provided.</li>
<li><strong>Science:</strong> 50 questions in 60 minutes. Human anatomy and physiology, biology, chemistry and scientific reasoning.</li>
<li><strong>English and language usage:</strong> 37 questions in 37 minutes. Grammar, spelling, punctuation and vocabulary.</li>
</ul>
<p>Science is the largest section, and anatomy and physiology is the biggest part of it, so it usually needs the most study time.</p>"""),
         ("Know your target score", """<p>Each nursing program sets its own minimum TEAS score, and some look at section scores too. Check your program’s requirement first, so you know how much you need to improve.</p>"""),
         ("A 4-week plan", """<ul>
<li><strong>Week 1:</strong> take a practice test to find your weak sections, then start science, beginning with anatomy and physiology.</li>
<li><strong>Week 2:</strong> more science, plus math every day. Short daily math practice works better than one long session.</li>
<li><strong>Week 3:</strong> reading and English, keeping up a little science and math. Do timed section practice.</li>
<li><strong>Week 4:</strong> a full timed practice test early in the week, then review your mistakes. Light review only in the last two days.</li>
</ul>
<p>Most people plan 30 to 80 hours in total, about 1 to 2 hours a day. The free <a href="/study-plan/teas/">TEAS study plan generator</a> builds this from your own test date and hours.</p>
<p>Prefer paper? The <a href="/planners/ati-teas-4-week-planner/">ATI TEAS 4-week planner</a> has an exam map, weekly and daily pages and an error log for $5. It is independent study material, not from ATI.</p>"""),
         ("Study smarter, not longer", """<ul>
<li>Test yourself instead of re-reading. Read a topic once, close the book, write what you remember, then check.</li>
<li>Use <a href="/tools/flashcards/">flashcards</a> for anatomy terms and science facts.</li>
<li>Time yourself. The English section gives you about a minute per question, so pace matters.</li>
</ul>"""),
       ]),
  dict(slug="cpa-study-schedule", tag="Exam plans", date="2026-10-28",
       title="CPA Study Schedule: How to Plan All Four Sections",
       h1="CPA study schedule: how to plan all four sections",
       desc="A CPA study schedule for all four sections: the exam structure, the order to take FAR, AUD, REG and your discipline, hours per section, and free plans.",
       lead="Four sections, one credit window. Here’s how to order them and how long to give each.",
       card="Plan all four CPA sections: order, hours and timeline.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the CPA Exam is structured", """<p>Since January 2024, the CPA Exam has three core sections that everyone takes, plus one discipline section you choose:</p>
<ul>
<li><strong>Core:</strong> Financial Accounting and Reporting (FAR), Auditing and Attestation (AUD), and Taxation and Regulation (REG).</li>
<li><strong>Discipline (pick one):</strong> Business Analysis and Reporting (BAR), Information Systems and Controls (ISC), or Tax Compliance and Planning (TCP).</li>
</ul>
<p>Each section is a 4-hour exam, and you need a score of 75 to pass. You take them one at a time, in any order, and must pass all four within your state’s credit window. That window used to be 18 months in every state; many states now allow 30 months. Check your own board of accountancy’s rules before you plan.</p>"""),
         ("Which order to take them in", """<p>There’s no required order, but these approaches work well for most candidates:</p>
<ul>
<li><strong>FAR first</strong> if you have the most time now. It’s usually the longest section, and it gives you a base for the others.</li>
<li><strong>Pair related sections.</strong> REG and TCP overlap on tax, and FAR and BAR overlap on financial reporting, so taking them back to back saves review time.</li>
<li><strong>Put your busiest work season on your shortest section,</strong> or leave a gap. Don’t start FAR in the middle of busy season.</li>
</ul>"""),
         ("How long each section takes", """<div class="table-scroll"><table class="mini-table">
<thead><tr><th scope="col">Section</th><th scope="col">Common study hours</th><th scope="col">Weeks, studying part time</th><th scope="col">Free plan</th></tr></thead>
<tbody>
<tr><td>FAR</td><td>100 to 180</td><td>8 to 12</td><td><a href="/study-plan/cpa-far/">FAR study plan</a></td></tr>
<tr><td>AUD</td><td>90 to 150</td><td>6 to 10</td><td><a href="/study-plan/cpa-aud/">AUD study plan</a></td></tr>
<tr><td>REG</td><td>90 to 150</td><td>6 to 10</td><td><a href="/study-plan/cpa-reg/">REG study plan</a></td></tr>
<tr><td>Discipline (BAR, ISC or TCP)</td><td>roughly 80 to 150</td><td>6 to 10</td><td>Use the <a href="/tools/study-schedule-maker/">study schedule maker</a></td></tr>
</tbody></table></div>
<p>These are common planning ranges, not official figures. Your accounting background and how recently you studied each topic move you up or down.</p>
<p>The free section plans and the printable planners below cover FAR, AUD and REG. There is no plan or planner for the discipline sections (BAR, ISC or TCP) yet, so use the study schedule maker for yours.</p>
<p>Prefer paper? There is a printable planner for each section: <a href="/planners/cpa-far-10-week-planner/">FAR</a>, <a href="/planners/cpa-aud-8-week-planner/">AUD</a> and <a href="/planners/cpa-reg-8-week-planner/">REG</a>, $5 each. They are independent study materials, not from the AICPA.</p>"""),
         ("A full timeline", """<p>Studying part time while working, most candidates finish all four sections in about 12 to 18 months:</p>
<ol>
<li><strong>Months 1 to 3:</strong> FAR. Book your exam date before you start, so the plan has an end.</li>
<li><strong>Months 4 to 6:</strong> AUD or REG.</li>
<li><strong>Months 7 to 9:</strong> the other core section.</li>
<li><strong>Months 10 to 12:</strong> your discipline section, paired with the core section it overlaps most.</li>
</ol>
<p>Leave a week or two between sections to rest, and keep a buffer before your credit window closes in case you need to retake one.</p>"""),
         ("Plan each section week by week", """<p>Each free section plan builds a week-by-week schedule from your exam date and the hours you have, weighted to the AICPA blueprint, with simulations in the second half:</p>
<ul>
<li><a href="/study-plan/cpa-far/">CPA FAR study plan</a></li>
<li><a href="/study-plan/cpa-aud/">CPA AUD study plan</a></li>
<li><a href="/study-plan/cpa-reg/">CPA REG study plan</a></li>
</ul>
<p>Studying while working is mostly a focus problem. Short, protected blocks with your phone in another room beat long, distracted evenings. The <a href="/tools/focus-timer/">Pomodoro timer</a> helps.</p>"""),
       ]),
  dict(slug="usmle-step-1-study-schedule", tag="Exam plans", date="2026-11-02",
       title="USMLE Step 1 Study Schedule: An 8-Week Dedicated Plan",
       h1="A USMLE Step 1 study schedule for your dedicated period",
       desc="An 8-week USMLE Step 1 study schedule: how the exam is built now, how to split systems and question blocks, and when to take self-assessments.",
       lead="Step 1 is pass/fail, so the aim is to cover everything and pass with room to spare. Here is an 8-week way to do it.",
       card="An 8-week Step 1 schedule built around systems and daily question blocks.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How Step 1 works now", """<p>Step 1 results have been reported as pass or fail only since 26 January 2022, so there is no three-digit score to chase. It is taken in a single 8-hour session.</p>
<p>The question format changed in 2026. For exams on or after 14 May 2026, the USMLE lists fourteen 30-minute blocks of up to 20 questions each, with at least 55 minutes of break time. Before that date it was seven 60-minute blocks of up to 40 questions. Check <a href="https://www.usmle.org/step-exams/step-1" rel="noopener">usmle.org</a> for the format on your test date, because it can change again.</p>"""),
         ("Plan for passing, not for a score", """<p>With a pass/fail result, the useful question is “where am I weakest?”, not “how high can I go?”. Aim to touch every system at least twice and to spend extra time where your practice results are lowest.</p>
<p>Take one self-assessment early. It shows where to start and gives you a baseline to compare later ones against.</p>"""),
         ("Weeks 1 to 5: systems, one at a time", """<ul>
<li>Study one organ system at a time, such as cardiovascular, respiratory, renal and so on, with the basic science behind it: physiology, pathology and pharmacology together.</li>
<li>Do a timed block of practice questions every day, then review every question, right or wrong, before moving on.</li>
<li>Keep an <a href="/tools/error-log/">error log</a> with one line per miss: a content gap, a misread, or a timing problem.</li>
<li>Review flashcards for drugs, pathways and findings a little every day. The free <a href="/tools/flashcards/">flashcards</a> space the reviews for you.</li>
</ul>"""),
         ("Weeks 6 and 7: mixed blocks and self-assessment", """<ul>
<li>Switch to mixed blocks that cover several systems at once, because the real exam does not announce the topic.</li>
<li>Take a full-length self-assessment under test conditions, at the time of day your exam is booked.</li>
<li>Spend as long reviewing it as taking it, and send what you learn back into the systems you are weakest in.</li>
</ul>"""),
         ("Week 8: taper", """<p>One more self-assessment early in the week, then your error log and short question sets. Keep the last two days light, check your test centre route and ID, and sleep. A full-length exam the day before only adds fatigue.</p>"""),
         ("How many hours?", """<p>Many students use 4 to 8 weeks of dedicated study, with 8 to 10 hours a day on study days. That is a common planning range, not an official figure, and it depends on how recently you finished the basic science courses. If you are short on time, cut the weeks and keep the daily question blocks.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 8 weeks? The free <a href="/study-plan/usmle-step-1/">USMLE Step 1 study schedule generator</a> builds a systems-based plan from your exam date and daily hours.</p>
<p>Prefer paper? The <a href="/planners/usmle-step-1-8-week-planner/">USMLE Step 1 8-week planner</a> has an exam map, weekly and daily pages and an error log for $5. It is independent study material and is not affiliated with or endorsed by the USMLE.</p>"""),
       ]),
  dict(slug="lsat-study-schedule-12-weeks", tag="Exam plans", date="2026-11-02",
       title="LSAT Study Schedule: A 12-Week Plan, Week by Week",
       h1="A 12-week LSAT study schedule",
       desc="A 12-week LSAT study schedule for the current format: logical reasoning and reading comprehension, timed sections, blind review and full practice tests.",
       lead="The LSAT now has two question types that are scored. Here is how to spend twelve weeks on them.",
       card="A 12-week LSAT schedule built on timed sections and blind review.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("What is on the LSAT now", """<p>LSAC describes the current test as four 35-minute multiple-choice sections: two scored Logical Reasoning sections, one scored Reading Comprehension section, and one unscored section of either type. The Analytical Reasoning section, often called logic games, was retired after the June 2024 test.</p>
<p>LSAT Argumentative Writing is a separate, unscored writing sample taken online. You still need an approved sample on file for your score to be released. LSAC has also announced a format change from August 2027 that moves the unscored questions into the scored sections, so check <a href="https://www.lsac.org/" rel="noopener">lsac.org</a> for your test date.</p>"""),
         ("Weeks 1 to 3: learn the question types", """<ul>
<li>Take one full practice test first, untimed if you need to, to see where you start.</li>
<li>For Logical Reasoning, learn the common types, such as assumption, flaw, strengthen and weaken, and practise each without a clock.</li>
<li>For Reading Comprehension, practise summarising each paragraph in a few words, then the passage’s main point.</li>
<li>Start an <a href="/tools/error-log/">error log</a> now: one line per miss, with the reason.</li>
</ul>"""),
         ("Weeks 4 to 8: timed sections and blind review", """<ul>
<li>Do timed 35-minute sections several times a week, mixing Logical Reasoning and Reading Comprehension.</li>
<li>Use blind review: before you check answers, go back to every question you missed or felt unsure about and re-do it without a clock. Then check, and write down what changed.</li>
<li>Drill the question type that costs you the most points each week, then test it again in a timed set.</li>
</ul>"""),
         ("Weeks 9 to 11: full practice tests", """<ul>
<li>Take one full test a week under test conditions, at the time of day your exam is booked.</li>
<li>Spend at least as long reviewing the test as taking it.</li>
<li>Use official LSAC practice tests where you can, because they are closest to the real thing.</li>
</ul>"""),
         ("Week 12: taper", """<p>One last full test early in the week, then error-log review and a few short timed sets. Rest the last two days. Complete your writing sample ahead of time so nothing delays your score.</p>"""),
         ("How many hours?", """<p>Many students plan roughly 100 to 300 hours in total, spread over two to six months. That is a common estimate, not an official number. Starting score, target score and time between tests all move it, so use your first practice test to judge where you fall.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 12 weeks? The free <a href="/study-plan/lsat/">LSAT study schedule generator</a> builds this structure from your test date and daily hours.</p>
<p>Prefer paper? The <a href="/planners/lsat-12-week-planner/">LSAT 12-week planner</a> has an exam map, weekly and daily pages, a practice test log and an error log for $5. It is independent study material and is not affiliated with or endorsed by LSAC.</p>"""),
       ]),
  dict(slug="gre-study-plan-8-weeks", tag="Exam plans", date="2026-11-02",
       title="GRE Study Plan: 8 Weeks for the Shorter Test",
       h1="An 8-week GRE study plan",
       desc="An 8-week GRE study plan for the shorter test: the current format, verbal and quant review, timed sections, the essay and full practice tests.",
       lead="The GRE is about two hours long now. Here is how to prepare for it in eight weeks.",
       card="An 8-week GRE plan for verbal, quant and the essay.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the GRE is built now", """<p>Since 22 September 2023 the GRE General Test runs about 1 hour 58 minutes. ETS lists one 30-minute “Analyze an Issue” writing task first, then two Verbal Reasoning sections (12 questions in 18 minutes, 15 questions in 23 minutes) and two Quantitative Reasoning sections (12 questions in 21 minutes, 15 questions in 26 minutes).</p>
<p>Verbal and Quantitative are adaptive by section: how you do on the first section of each measure affects the difficulty of the second. Check <a href="https://www.ets.org/gre" rel="noopener">ets.org/gre</a> for the current format before you register.</p>"""),
         ("Weeks 1 and 2: diagnose and review", """<ul>
<li>Take one full practice test first to see where you stand on verbal and quant.</li>
<li>Review the quant topics you are rusty on, usually arithmetic, algebra, geometry and data analysis, and work them untimed.</li>
<li>Read something dense every day, and learn new words from context rather than from long lists.</li>
</ul>"""),
         ("Weeks 3 to 5: build speed", """<ul>
<li>Practise Reading Comprehension, Text Completion and Sentence Equivalence in short timed sets.</li>
<li>Do timed quant sets, and learn to skip a question that is eating your time and come back to it.</li>
<li>Write one essay a week from week 3, 30 minutes, then reread it and cut anything that does not support your point.</li>
<li>Keep an <a href="/tools/error-log/">error log</a> with the reason for each miss.</li>
</ul>"""),
         ("Weeks 6 and 7: full practice tests", """<ul>
<li>Take a full-length practice test each week, essay included, at the time of day of your real test.</li>
<li>Spend as long reviewing as testing, and send what you learn back to your weakest topics.</li>
<li>Use the official ETS practice material where possible, because its questions are the closest to the real test.</li>
</ul>"""),
         ("Week 8: taper", """<p>One last practice test early in the week, then your error log and a few short timed sets. No new topics in the last two days. Check your ID and test-centre or at-home setup, and sleep.</p>"""),
         ("How many hours?", """<p>Many students plan about 50 to 120 hours over 6 to 12 weeks. That is a common estimate, not an official figure. A strong starting score or a lower target needs fewer; a long break from maths needs more.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 8 weeks? The free <a href="/study-plan/gre/">GRE study plan generator</a> builds this structure from your test date and daily hours.</p>
<p>Prefer paper? The <a href="/planners/gre-8-week-planner/">GRE 8-week planner</a> has an exam map, weekly and daily pages, a practice test log and an error log for $5. It is independent study material and is not affiliated with or endorsed by ETS.</p>"""),
       ]),
  dict(slug="naplex-study-plan-8-weeks", tag="Exam plans", date="2026-11-02",
       title="NAPLEX Study Plan: An 8-Week Schedule by Content Domain",
       h1="An 8-week NAPLEX study plan",
       desc="An 8-week NAPLEX study plan built on the current NABP content outline: how the exam is weighted, what to study each week, calculations and practice tests.",
       lead="The NAPLEX outline changed in May 2025. Here is an 8-week plan weighted to where the questions are.",
       card="An 8-week NAPLEX plan weighted to the current content outline.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the NAPLEX is built", """<p>NABP describes the NAPLEX as a 6-hour, 225-question computerised exam. Results are reported as pass or fail, and candidates get five attempts.</p>
<p>The content outline for exams on or after 1 May 2025 has five domains. Weights are shares of the roughly 200 scored questions:</p>
<ul>
<li>Person-Centered Assessment and Treatment Planning: 40% (about 80 questions)</li>
<li>Foundational Knowledge for Pharmacy Practice: 25% (about 50)</li>
<li>Medication Use Process: 25% (about 50)</li>
<li>Professional Practice: 5% (about 10)</li>
<li>Pharmacy Management and Leadership: 5% (about 10)</li>
</ul>
<p>Check <a href="https://nabp.pharmacy/programs/examinations/naplex/take-the-naplex-exam/" rel="noopener">nabp.pharmacy</a> for the outline that applies to your test date.</p>"""),
         ("Spend time where the questions are", """<p>Two thirds of the scored questions sit in treatment planning and the medication use process, so most of your hours should go to therapeutics, patient cases and the dispensing and monitoring steps. The two 5% domains still deserve a pass or two, but not weeks.</p>"""),
         ("Weeks 1 and 2: baseline and foundations", """<ul>
<li>Take a practice exam first to see which domains are weakest.</li>
<li>Review foundational science that supports therapeutics: pharmacology, pharmacokinetics, and pharmaceutics.</li>
<li>Start a daily set of calculations. Write out every step; most misses come from units and rounding.</li>
<li>Start an <a href="/tools/error-log/">error log</a>: one line per miss, with the reason.</li>
</ul>"""),
         ("Weeks 3 to 6: therapeutics by body system", """<ul>
<li>Go through therapeutics one system or condition group at a time, with guideline-based first-line choices, monitoring and patient counselling.</li>
<li>Work case-style questions every day, because treatment planning questions ask you to choose among options for a patient.</li>
<li>Keep reviewing drug facts and doses with the free <a href="/tools/flashcards/">flashcards</a>, a little each day.</li>
<li>Add a short pass through the medication use process: prescription checks, dispensing, interactions and safety.</li>
</ul>"""),
         ("Week 7: full-length practice", """<ul>
<li>Take a timed full-length practice exam at the time of day of your booking.</li>
<li>Review every miss and send what you learn back into the domain it came from.</li>
<li>Skim professional practice and management topics once.</li>
</ul>"""),
         ("Week 8: taper", """<p>One more mixed practice set early in the week, then your error log and calculations. Keep the last two days light, check your ID and test-centre details, and sleep.</p>"""),
         ("How many hours?", """<p>Many graduates study for 4 to 8 weeks, often around 120 to 300 hours. That is a common planning range, not an official figure. If you are short on time, shorten the therapeutics weeks and keep the daily calculations and practice questions.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 8 weeks? The free <a href="/study-plan/naplex/">NAPLEX study plan generator</a> builds a plan from your exam date and daily hours.</p>
<p>Prefer paper? The <a href="/planners/naplex-8-week-planner/">NAPLEX 8-week planner</a> has an exam map, weekly and daily pages and an error log for $5. It is independent study material and is not affiliated with or endorsed by NABP.</p>"""),
       ]),
  dict(slug="pance-study-plan-8-weeks", tag="Exam plans", date="2026-11-02",
       title="PANCE Study Plan: 8 Weeks by Organ System",
       h1="An 8-week PANCE study plan",
       desc="An 8-week PANCE study plan built on the NCCPA blueprint: the 300-question format, how organ systems are weighted, weekly focus and practice exams.",
       lead="The PANCE is five hours and 300 questions. Here is an 8-week plan weighted to the NCCPA blueprint.",
       card="An 8-week PANCE plan weighted to the NCCPA blueprint.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the PANCE is built", """<p>NCCPA lists the PANCE as a five-hour exam of 300 multiple-choice questions in five blocks of 60 questions, with 60 minutes per block. There are 45 minutes of break time in total between blocks, and you manage it yourself. A 15-minute tutorial comes first. Once you leave a block or its time runs out, you cannot go back to it.</p>
<p>The blueprint effective January 2025 splits the exam two ways, by medical content and by task. Check <a href="https://www.nccpa.net/become-certified/pance-blueprint/" rel="noopener">nccpa.net</a> for the version that applies to your test date.</p>"""),
         ("Where the questions are", """<p>Largest medical content shares: Cardiovascular 11%, Pulmonary 9%, Gastrointestinal/Nutrition 8% and Musculoskeletal 8%. Infectious Diseases, Neurologic, Psychiatry/Behavioral Science and Reproductive are 7% each. Professional Practice is 6%, and the rest are 4 to 6% each. NCCPA notes that up to 8 to 10% of the exam covers general surgical topics, 12 to 15% focuses on pediatric patients, and the percentages may vary slightly.</p>
<p>By task, the biggest are Formulating Most Likely Diagnosis (18%), History Taking and Physical Examination (16%), Clinical Intervention (16%) and Pharmaceutical Therapeutics (15%). So practise deciding what is going on and what to do, not just recalling facts.</p>"""),
         ("Weeks 1 and 2: baseline and the big systems", """<ul>
<li>Take a practice exam first to see which systems are weakest.</li>
<li>Start with cardiovascular and pulmonary, the two biggest shares.</li>
<li>Do a block of practice questions daily and review every one, right or wrong.</li>
<li>Start an <a href="/tools/error-log/">error log</a>: one line per miss, with the reason.</li>
</ul>"""),
         ("Weeks 3 to 6: the remaining systems", """<ul>
<li>Take about two systems a week, ordered by weight and by your weak spots: GI, musculoskeletal, infectious disease, neurologic, psychiatry, reproductive, then the smaller ones.</li>
<li>For each condition, learn presentation, the most likely diagnosis, first-line management and key drugs.</li>
<li>Use the free <a href="/tools/flashcards/">flashcards</a> for drugs and classic findings, a little each day.</li>
<li>Fit in pediatrics and surgical topics alongside each system.</li>
</ul>"""),
         ("Week 7: full-length practice", """<ul>
<li>Take a timed 300-question practice exam in five blocks with a 45-minute break budget, at the time of day of your booking.</li>
<li>Review every miss and send what you learn back to the weakest systems and tasks.</li>
<li>Skim professional practice topics once.</li>
</ul>"""),
         ("Week 8: taper", """<p>One more mixed question set early in the week, then your error log. Keep the last two days light. Bring two valid IDs with matching names, arrive at least 30 minutes early, and sleep.</p>"""),
         ("How many hours?", """<p>Many students give the PANCE 4 to 12 weeks after graduation, often around 150 to 350 hours, depending on how their rotations went. That is a common planning range, not an official figure. If you are short on time, cut weeks from the middle and keep the daily question blocks.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 8 weeks? The free <a href="/study-plan/pance/">PANCE study plan generator</a> builds a plan from your exam date and daily hours.</p>
<p>Prefer paper? The <a href="/planners/pance-8-week-planner/">PANCE 8-week planner</a> has an exam map, weekly and daily pages and an error log for $5. It is independent study material and is not affiliated with or endorsed by NCCPA.</p>"""),
       ]),
  dict(slug="gmat-study-plan-8-weeks", tag="Exam plans", date="2026-11-02",
       title="GMAT Study Plan: An 8-Week Schedule for the Focus Edition",
       h1="An 8-week GMAT study plan",
       desc="An 8-week GMAT Focus Edition study plan: the three-section format, how to split Quant, Verbal and Data Insights, timed practice and full tests.",
       lead="The GMAT Focus Edition has three sections and about two hours of testing. Here is an 8-week plan for it.",
       card="An 8-week GMAT Focus Edition plan across Quant, Verbal and Data Insights.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the GMAT Focus Edition is built", """<p>GMAC lists three 45-minute sections, 2 hours 15 minutes of testing in all: Quantitative Reasoning (21 questions), Verbal Reasoning (23 questions) and Data Insights (20 questions). You can take the sections in any order and take one optional 10-minute break. You can bookmark questions and change up to three answers per section.</p>
<p>The total score runs from 205 to 805, and the three sections count equally. Data sufficiency now sits in Data Insights, and Verbal no longer has sentence correction. Check <a href="https://www.mba.com/exams/gmat-focus-edition/about/exam-structure" rel="noopener">mba.com</a> for your test date.</p>"""),
         ("Because sections count equally", """<p>Verbal, Quant and Data Insights each carry a third of the total, so your weakest section is usually the best place to add hours. Take one practice test first and rank the three.</p>"""),
         ("Weeks 1 and 2: baseline and fundamentals", """<ul>
<li>Take a full practice test to see where you stand.</li>
<li>Review quant basics: arithmetic, algebra, word problems. Work untimed.</li>
<li>Learn the Data Insights question types: data sufficiency, table analysis, graphics interpretation, multi-source reasoning and two-part analysis.</li>
<li>Start an <a href="/tools/error-log/">error log</a> with the reason for each miss.</li>
</ul>"""),
         ("Weeks 3 to 5: build speed by section", """<ul>
<li>Do timed sets for each section, about two minutes a question on average.</li>
<li>For Verbal, practise reading comprehension and critical reasoning, and note why wrong options are wrong.</li>
<li>Learn to move on from a question that is costing too much time. You can only change three answers per section.</li>
<li>Give extra sessions to your weakest section.</li>
</ul>"""),
         ("Weeks 6 and 7: full practice tests", """<ul>
<li>Take a full test each week at the time of day of your booking.</li>
<li>Try different section orders to see which suits you.</li>
<li>Spend as long reviewing as testing. Use official GMAC practice material where you can.</li>
</ul>"""),
         ("Week 8: taper", """<p>One last full test early in the week, then error-log review and short timed sets. Keep the last two days light, check your ID and test setup, and sleep.</p>"""),
         ("How many hours?", """<p>Many students plan about 80 to 150 hours over 6 to 12 weeks. That is a common planning range, not an official figure. A high starting score or a modest target needs fewer; a long break from maths needs more.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 8 weeks? The free <a href="/study-plan/gmat/">GMAT study plan generator</a> builds a plan from your test date and daily hours.</p>
<p>Prefer paper? The <a href="/planners/gmat-8-week-planner/">GMAT 8-week planner</a> has an exam map, weekly and daily pages and an error log for $5. It is independent study material and is not affiliated with or endorsed by GMAC.</p>"""),
       ]),
  dict(slug="dat-study-schedule-10-weeks", tag="Exam plans", date="2026-11-02",
       title="DAT Study Schedule: A 10-Week Plan for the Four Tests",
       h1="A 10-week DAT study schedule",
       desc="A 10-week DAT study schedule: the four tests, how long each runs, sciences review, perceptual ability practice and full-length mock tests.",
       lead="The DAT has four timed tests and a lot of science. Here is a 10-week schedule that covers all four.",
       card="A 10-week DAT schedule across sciences, perceptual ability, reading and quantitative reasoning.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the DAT is built", """<p>The ADA lists four multiple-choice tests: Survey of the Natural Sciences (100 questions, 90 minutes), Perceptual Ability (90 questions, 60 minutes), Reading Comprehension (50 questions, 60 minutes) and Quantitative Reasoning (40 questions, 45 minutes). The sciences cover biology, general chemistry and organic chemistry.</p>
<p>Scores run from 200 to 600, and there is no official passing score. The ADA introduced a new scoring system on 1 March 2025, and the content specifications have been updated recently, so read the current candidate guide at <a href="https://www.ada.org/education/testing/exams/dental-admission-test-dat" rel="noopener">ada.org</a> before you plan.</p>"""),
         ("Give each test its own time", """<p>Sciences is the biggest test, so it gets the most hours. Perceptual Ability is the one most students have not seen before, so it needs short daily practice from the start. Reading Comprehension and Quantitative Reasoning need regular timed sets rather than long study blocks.</p>"""),
         ("Weeks 1 and 2: baseline and plan", """<ul>
<li>Take a full practice test to see which tests and which science subjects are weakest.</li>
<li>Start 20 to 30 minutes of Perceptual Ability every day, such as keyhole, angle ranking, hole punching, cube counting and pattern folding.</li>
<li>Start an <a href="/tools/error-log/">error log</a> with the reason for each miss.</li>
</ul>"""),
         ("Weeks 3 to 7: sciences, rotating subjects", """<ul>
<li>Rotate biology, general chemistry and organic chemistry through the week so none goes cold.</li>
<li>Practise questions after every topic, then review wrong answers before moving on.</li>
<li>Keep drilling with the free <a href="/tools/flashcards/">flashcards</a> for reactions, mechanisms and terms.</li>
<li>Do a timed Reading Comprehension passage and a Quantitative Reasoning set several times a week.</li>
</ul>"""),
         ("Weeks 8 and 9: full-length tests", """<ul>
<li>Take a full-length mock test each week in the real order and timings, at the time of day of your booking.</li>
<li>Spend as long reviewing as testing, and send what you learn back to the weakest subjects.</li>
<li>Use official ADA practice materials where you can.</li>
</ul>"""),
         ("Week 10: taper", """<p>One last mock early in the week, then your error log and short timed sets. No new topics in the last two days. Check your ID and test-centre details, and sleep.</p>"""),
         ("How many hours?", """<p>Many students plan around 2 to 3 months at 4 or more hours a day, roughly 200 to 350 hours, depending on how recently they took the sciences. That is a common estimate, not an official figure.</p>"""),
         ("Make it fit your dates", """<p>Not exactly 10 weeks? The free <a href="/study-plan/dat/">DAT study plan generator</a> builds a plan from your test date and daily hours.</p>
<p>Prefer paper? The <a href="/planners/dat-10-week-planner/">DAT 10-week planner</a> has an exam map, weekly and daily pages and an error log for $5. It is independent study material and is not affiliated with or endorsed by the ADA.</p>"""),
       ]),
  dict(slug="how-to-create-a-study-schedule", tag="Planning", date="2026-11-10",
       title="How to Create a Study Schedule That You Will Follow",
       h1="How to create a study schedule you will follow",
       desc="Build a study schedule in five steps: list your exams, count the hours you really have, split them by need, plan breaks and leave slack. Free tool included.",
       lead="Five steps, about twenty minutes, and a schedule that survives a bad day.",
       card="Five steps to a schedule that survives a bad day.",
       kit="The free Study Focus Kit has printable worksheets for planning and long study days.",
       sections=[
         ("Start from the dates, not the subjects", """<p>Write down every exam or deadline with its date. Count the days between today and each one. A schedule only works backwards from a date, so this list comes first, before any timetable.</p>"""),
         ("Count the hours you really have", """<p>Take each day and subtract classes, work, meals, travel and sleep. What is left is your real study time, and it is almost always less than you hoped. Plan on the real number. A schedule built on the hours you wish you had fails by day three.</p>"""),
         ("Split the hours by need", """<p>Give each subject a share of the hours based on two things: how much you still have to learn, and how many marks it carries. Weak and heavy subjects get the most time. Then split each subject into small, named tasks such as “chapter 4 practice questions” instead of “study biology”.</p>
<p class="download-row"><a class="btn btn-soft" href="/assets/templates/study-schedule-template.xlsx" download>Download a weekly schedule spreadsheet (.xlsx)</a></p>
<p>The <a href="/tools/study-schedule-maker/">study schedule maker</a> does this split for you from your subjects, exam dates and daily hours. For a big exam with a blueprint, the <a href="/study-plan/">free exam study plans</a> weight the topics for you.</p>"""),
         ("Plan in blocks with breaks", """<p>Work in blocks of 25 to 50 minutes with a 5 to 10 minute break, and put the hardest task in your best-energy block. Mix two or three subjects in a day instead of one, and end each day with a short recall of what you covered. The <a href="/tools/focus-timer/">focus timer</a> runs the blocks.</p>"""),
         ("Leave slack and review it weekly", """<ul>
<li>Leave one catch-up block each week, or about 20% of your hours empty, for the plan that slips.</li>
<li>Look at the schedule every Sunday. Move what you missed instead of deleting it.</li>
<li>Add spaced review: come back to each topic after a day, a few days and a week. The <a href="/tools/spaced-review/">spaced review calendar</a> sets those dates.</li>
</ul>
<p>If you are short of time, the <a href="/guides/how-to-study-for-finals-in-a-week/">finals-in-a-week guide</a> shows how to cut a plan down.</p>"""),
       ]),
  dict(slug="how-to-calculate-what-you-need-on-your-final", tag="Finals", date="2026-11-10",
       title="What Do I Need on My Final? The Formula and Examples",
       h1="What do I need on my final to get the grade I want?",
       desc="Work out the score you need on your final exam with one formula, two worked examples, and what to do when the answer is over 100%.",
       lead="One formula, two worked examples, and what to do when the answer is over 100%.",
       card="The formula for the score you need, with examples.",
       kit="The free Study Focus Kit has printable worksheets for planning and long study days.",
       sections=[
         ("The formula", """<p>You need three numbers: your current grade, the weight of the final (as a percentage of the course) and the grade you want. Then:</p>
<p><strong>Needed score = (target − current × (1 − weight)) ÷ weight</strong></p>
<p>Use decimals for the percentages: a 30% final has a weight of 0.30. The current grade must be the grade on everything before the final.</p>
<p class="download-row"><a class="btn btn-soft" href="/assets/templates/final-grade-template.xlsx" download>Download the final grade spreadsheet (.xlsx)</a></p>
<p>The <a href="/tools/final-grade-calculator/">final grade calculator</a> does this in one step. If your course has several weighted categories, work out the current grade with the <a href="/tools/weighted-grade-calculator/">weighted grade calculator</a> first.</p>"""),
         ("Example 1: a score you can reach", """<p>You have 78% going into a final worth 40%, and you want an 80% overall.</p>
<p>(80 − 78 × 0.60) ÷ 0.40 = (80 − 46.8) ÷ 0.40 = <strong>83%</strong> on the final.</p>"""),
         ("Example 2: a score that cannot be reached", """<p>You have 85% going into a final worth 30%, and you want a 90% overall.</p>
<p>(90 − 85 × 0.70) ÷ 0.30 = (90 − 59.5) ÷ 0.30 = <strong>101.7%</strong>.</p>
<p>Anything over 100% means that grade is out of reach unless the course offers extra credit. Check the next grade down: for an 88% overall the same sum gives 95%.</p>"""),
         ("What to do with the number", """<ul>
<li><strong>Under 60%:</strong> comfortable. Review the basics and keep the exam low stress.</li>
<li><strong>60 to 90%:</strong> a normal study plan. Give the exam the hours you would give any final.</li>
<li><strong>Over 90%:</strong> it will take your best work. Put this exam first in your schedule, and check with your teacher whether rounding or extra credit applies.</li>
</ul>
<p>With several finals, share your time by this number: the exam that needs the highest score gets the most hours. The <a href="/guides/how-to-study-for-multiple-exams/">multiple exams guide</a> shows the split.</p>"""),
         ("Check your syllabus", """<p>Some courses drop the lowest score, scale grades or round up. This formula assumes none of that, so treat the answer as a close estimate and confirm with your instructor.</p>"""),
       ]),
  dict(slug="how-to-study-for-the-nclex-pn", tag="Exam plans", video="4ktmRGfJkuI", date="2026-11-10",
       title="How to Study for the NCLEX-PN: A 6-Week Plan",
       h1="How to study for the NCLEX-PN",
       desc="How to study for the NCLEX-PN in 5 to 8 weeks: how the exam works, how it differs from the NCLEX-RN, where to spend your hours and a week-by-week plan.",
       lead="How the PN exam works, how it differs from the RN exam, and a plan you can start this week.",
       card="A 6-week NCLEX-PN plan built on the test plan.",
       kit="The free Study Focus Kit has printable worksheets for phone distractions, notes and long study days.",
       sections=[
         ("How the NCLEX-PN works", """<p>The NCLEX-PN is a computerized adaptive test for practical and vocational nurses. It gives you between 85 and 150 questions in up to 5 hours, and each question adapts to how you answered the last one. It includes Next Generation NCLEX items, so expect case studies as well as standard multiple-choice questions.</p>
<p>The test stops when it is confident of your result, so the number of questions you get says nothing about how you did. Do not read anything into it.</p>"""),
         ("How it differs from the NCLEX-RN", """<ul>
<li>The length rules are the same as the <a href="/guides/how-to-study-for-the-nclex/">NCLEX-RN</a>: 85 to 150 questions in up to 5 hours.</li>
<li>The test plan is written for the scope of practical nursing, so the weighting differs from the RN exam.</li>
<li>The same client needs categories apply, so the study method is the same. Only the emphasis shifts. Read the current PN test plan at <a href="https://www.ncsbn.org/" rel="noopener">ncsbn.org</a> and weight your hours by it.</li>
</ul>"""),
         ("A 6-week plan", """<ul>
<li><strong>Weeks 1 to 3: content plus questions.</strong> Review one or two categories a day. End each day with 40 to 60 practice questions on what you covered, and read every rationale.</li>
<li><strong>Weeks 4 and 5: mixed practice.</strong> Do larger mixed blocks, including case studies. Keep an error log of the concept you missed and why, and review it instead of re-reading notes.</li>
<li><strong>Week 6: readiness and rest.</strong> One or two readiness assessments early in the week, then light review of your error log. No new content in the last two days.</li>
</ul>
<p>The free <a href="/study-plan/nclex-pn/">NCLEX-PN study plan generator</a> turns your exam date and daily hours into this schedule. Prefer paper? The <a href="/planners/nclex-pn-6-week-planner/">NCLEX-PN 6-week planner</a> is $5 and independent of NCSBN.</p>"""),
         ("How many hours", """<p>Many graduates plan around 120 to 250 hours in total over 5 to 8 weeks. That is a common planning range, not an official figure. A recent graduate with good practice scores sits at the low end. A long gap since school sits at the high end. See the <a href="/guides/how-long-to-study-for-exams/">study hours guide</a> for other exams.</p>"""),
         ("Test week", """<p>Know the route to the test centre, bring the ID your registration requires, sleep, and eat. If you do not pass, NCSBN requires at least 45 days before a retake, and some jurisdictions allow fewer attempts a year, so check with your board.</p>"""),
       ]),
  dict(slug="how-to-pace-yourself-on-a-timed-exam", tag="Exam plans", date="2026-11-10",
       title="How to Pace Yourself on a Timed Exam: Minutes Per Question",
       h1="How to pace yourself on a timed exam",
       desc="Work out minutes per question, set checkpoints and decide what to skip. Pacing examples for the GMAT, PANCE and NAPLEX, plus a free calculator.",
       lead="Minutes per question, checkpoints to check on the clock, and what to do when you fall behind.",
       card="Minutes per question and checkpoints for any timed test.",
       kit="The free Study Focus Kit has printable worksheets for planning and long study days.",
       sections=[
         ("Start with minutes per question", """<p>Divide the time you have by the number of questions. Then take off a review buffer, 5 to 10% of the time, for flagged questions. The <a href="/tools/test-time-calculator/">test time calculator</a> does the sum and gives you checkpoints.</p>"""),
         ("Three examples", """<ul>
<li><strong>GMAT:</strong> 64 questions in 2 hours 15 minutes is about 2 minutes 6 seconds each, before any review time.</li>
<li><strong>PANCE:</strong> 300 questions in 5 hours is exactly 1 minute each, so pace is tight and quick decisions matter.</li>
<li><strong>NAPLEX:</strong> 225 questions in 6 hours is about 1 minute 36 seconds each.</li>
</ul>
<p>Question counts and times can change, so confirm them on the exam body’s site before you plan. The exam guides link to each one.</p>"""),
         ("Set checkpoints", """<p>Do not check the clock after every question. Check at the quarter marks. At 25%, 50% and 75% of the questions you should be at 25%, 50% and 75% of your working time. If you are more than a few minutes behind, speed up on the next block instead of panicking.</p>"""),
         ("Decide what to skip", """<ul>
<li>If you are not close to an answer after about twice your average time, make your best guess, flag it if the exam allows, and move on.</li>
<li>An easy question left unanswered costs the same as a hard one. Bank the easy points first.</li>
<li>Never leave a question blank if there is no penalty for a wrong answer.</li>
</ul>
<p>Check each exam’s rules on flagging and going back, because some do not let you return to earlier questions.</p>"""),
         ("Practise the pace", """<p>Do timed question blocks in your last weeks, at real exam pace, and review the ones you rushed. Pace is a skill that improves with practice. For the planning side, see the <a href="/guides/how-long-to-study-for-exams/">study hours guide</a>.</p>"""),
       ]),
  dict(slug="study-schedule-template", tag="Planning", date="2026-11-11",
       title="Free Study Schedule Template: Spreadsheet, Printable and Exam Versions",
       h1="Free study schedule template (spreadsheet and printable)",
       desc="A free weekly study schedule template as a spreadsheet, a printable plan pack, and ready-made schedules for the MCAT, LSAT, GRE, GMAT, NCLEX and more.",
       lead="A weekly spreadsheet, a printable plan pack and ready-made schedules for the big exams, all free.",
       card="Free spreadsheet, printable and exam-ready schedules.",
       kit="The free Study Focus Kit has printable worksheets for planning and long study days.",
       sections=[
         ("Pick the template that fits", """<ul>
<li><strong>Any course or several exams:</strong> the weekly spreadsheet below. You type in your subjects and hours.</li>
<li><strong>One big exam with a date:</strong> the free <a href="/study-plan/">exam study plan generator</a>. It builds a week-by-week schedule from your test date and daily hours, and you can print it.</li>
<li><strong>Finals week:</strong> the <a href="/guides/how-to-study-for-finals-in-a-week/">finals-in-a-week guide</a> and the <a href="/tools/study-schedule-maker/">study schedule maker</a>.</li>
</ul>"""),
         ("Weekly study schedule spreadsheet", """<p>An hourly grid from 6:00 to 22:00, Monday to Sunday. List your subjects on the second tab, pick one for each hour on the first, and the sheet counts the hours per subject for you. Plan your breaks in it too. It works in Excel, Google Sheets and LibreOffice.</p>
<p class="download-row"><a class="btn btn-soft" href="/assets/templates/study-schedule-template.xlsx" download>Download the weekly schedule spreadsheet (.xlsx)</a></p>
<p>Not sure how many hours to give each subject? Follow the five steps in <a href="/guides/how-to-create-a-study-schedule/">how to create a study schedule</a> first, then type the numbers in.</p>"""),
         ("Printable plan for your exam", """<p>Choose your exam on the <a href="/study-plan/">study plan page</a>, enter your test date and hours, and use “Print my full plan pack”. You get a cover page, an overview, weekly pages, a first week day by day, error log pages and a checklist, with your own dates on them.</p>"""),
         ("Ready-made schedules for each exam", """<p>If you want to see a finished schedule before you build your own:</p>
<ul>
<li><a href="/guides/mcat-study-schedule-3-months/">MCAT study schedule (3 months)</a></li>
<li><a href="/guides/lsat-study-schedule-12-weeks/">LSAT study schedule (12 weeks)</a></li>
<li><a href="/guides/gre-study-plan-8-weeks/">GRE study plan (8 weeks)</a> and <a href="/guides/gmat-study-plan-8-weeks/">GMAT study plan (8 weeks)</a></li>
<li><a href="/guides/usmle-step-1-study-schedule/">USMLE Step 1 study schedule</a></li>
<li><a href="/guides/how-to-study-for-the-nclex/">NCLEX-RN</a> and <a href="/guides/how-to-study-for-the-nclex-pn/">NCLEX-PN</a>, <a href="/guides/how-to-study-for-the-teas/">TEAS</a></li>
<li><a href="/guides/cpa-study-schedule/">CPA exam schedule</a></li>
<li><a href="/guides/dat-study-schedule-10-weeks/">DAT</a>, <a href="/guides/naplex-study-plan-8-weeks/">NAPLEX</a> and <a href="/guides/pance-study-plan-8-weeks/">PANCE</a></li>
</ul>
<p>Each one shows the week-by-week split, and each links to the generator so you can fit it to your own date.</p>"""),
         ("Make any template work", """<ul>
<li>Plan from the exam date backwards, and leave one catch-up block a week.</li>
<li>Put a practice-question or recall block in every day, not only at the end.</li>
<li>Track what you get wrong. The <a href="/tools/error-log/">error log</a> and <a href="/tools/practice-score-tracker/">practice score tracker</a> show which topics need more hours, and the plan generator can use them.</li>
</ul>"""),
       ]),
]

REFS = {
  "study-schedule-template": "Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., &amp; Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. <em>Psychological Bulletin</em>, 132(3).",
  "how-to-create-a-study-schedule": "Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., &amp; Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. <em>Psychological Bulletin</em>, 132(3).",
  "how-to-calculate-what-you-need-on-your-final": "Weighted-average grade formula. Check your syllabus for the weights and any drop, scaling or rounding rules.",
  "how-to-study-for-the-nclex-pn": "NCSBN. NCLEX-PN test plan, Next Generation NCLEX information and candidate bulletin, ncsbn.org.",
  "how-to-pace-yourself-on-a-timed-exam": "GMAC, mba.com. NCCPA, nccpa.net. NABP, nabp.pharmacy. Confirm current test lengths on each site.",
  "gmat-study-plan-8-weeks": "GMAC. GMAT Focus Edition exam structure, mba.com.",
  "dat-study-schedule-10-weeks": "American Dental Association. Dental Admission Test (DAT) 2026 Candidate Guide and exam page, ada.org.",
  "pance-study-plan-8-weeks": "NCCPA. PANCE content blueprint (effective January 2025) and What to Expect on Test Day, nccpa.net.",
  "naplex-study-plan-8-weeks": "NABP. Take the NAPLEX exam, nabp.pharmacy. NABP. NAPLEX Content Outline, effective for exams beginning May 1, 2025, nabp.pharmacy.",
  "usmle-step-1-study-schedule": "USMLE. Step 1 exam content and format, usmle.org/step-exams/step-1. USMLE. Examination results and scoring, usmle.org.",
  "lsat-study-schedule-12-weeks": "LSAC. LSAT format and changes, lsac.org/lsat. LSAC. LSAT Argumentative Writing, lsac.org.",
  "gre-study-plan-8-weeks": "ETS. GRE General Test content and structure, ets.org/gre.",
  "cpa-study-schedule": "AICPA &amp; CIMA. CPA Exam blueprints and CPA Evolution, aicpa-cima.com. NASBA. CPA Exam information and credit window rules by jurisdiction, nasba.org.",
  "how-to-study-for-the-nclex": "NCSBN. NCLEX-RN test plan and Next Generation NCLEX information, ncsbn.org.",
  "mcat-study-schedule-3-months": "AAMC. What’s on the MCAT exam, and official MCAT practice exams, students-residents.aamc.org.",
  "mcat-error-log-template": "AAMC. Official MCAT practice exams, students-residents.aamc.org.",
  "how-to-study-for-the-teas": "ATI. About the ATI TEAS 7, atitesting.com/teas.",
  "how-long-to-study-for-exams": "Test details: NCSBN (ncsbn.org), ATI (atitesting.com), AAMC (aamc.org), USMLE (usmle.org), NCCPA (nccpa.net), NABP (nabp.pharmacy), ADA (ada.org), ETS (ets.org), GMAC (mba.com), LSAC (lsac.org), AICPA (aicpa-cima.com).<br>Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., &amp; Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. <em>Psychological Bulletin</em>, 132(3).",
  "stop-checking-phone-while-studying": "Ward, A. F., Duke, K., Gneezy, A., &amp; Bos, M. W. (2017). Brain drain: The mere presence of one’s own smartphone reduces available cognitive capacity. <em>Journal of the Association for Consumer Research</em>, 2(2).",
  "active-recall-notes": "Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., &amp; Willingham, D. T. (2013). Improving students’ learning with effective learning techniques. <em>Psychological Science in the Public Interest</em>, 14(1).",
  "brain-dump-before-studying": "Masicampo, E. J., &amp; Baumeister, R. F. (2011). Consider it done! Plan making can eliminate the cognitive effects of unfulfilled goals. <em>Journal of Personality and Social Psychology</em>, 101(4).",
  "stop-rereading-cover-syllabus-faster": "Karpicke, J. D., &amp; Roediger, H. L. (2008). The critical importance of retrieval for learning. <em>Science</em>, 319(5865).",
  "how-to-study-for-finals-in-a-week": "Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., &amp; Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. <em>Psychological Bulletin</em>, 132(3).<br>Rohrer, D., &amp; Taylor, K. (2007). The shuffling of mathematics problems improves learning. <em>Instructional Science</em>, 35(6).",
  "how-to-study-for-multiple-exams": "Rohrer, D., &amp; Taylor, K. (2007). The shuffling of mathematics problems improves learning. <em>Instructional Science</em>, 35(6).",
  "does-cramming-work": "Kornell, N. (2009). Optimising learning using flashcards: Spacing is more effective than cramming. <em>Applied Cognitive Psychology</em>, 23(9).",
  "stop-procrastinating-studying": "Steel, P. (2007). The nature of procrastination: A meta-analytic and theoretical review of quintessential self-regulatory failure. <em>Psychological Bulletin</em>, 133(1).<br>Gollwitzer, P. M., &amp; Sheeran, P. (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. <em>Advances in Experimental Social Psychology</em>, 38.",
}

VIDEO_SCRIPT = """
<script>
  document.querySelectorAll('.video[data-video]').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + link.dataset.video + '?autoplay=1&rel=0';
      frame.title = link.querySelector('.video-title').textContent;
      frame.allow = 'autoplay; encrypted-media; picture-in-picture';
      frame.allowFullscreen = true;
      link.querySelector('.video-frame').replaceChildren(frame);
      link.replaceWith(...link.childNodes);
    }, { once: true });
  });
</script>"""

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def nice_date(iso):
    return f"{int(iso[8:10])} {MONTHS[int(iso[5:7]) - 1]} {iso[:4]}"

def KIT_BOX(g):
    return f'''        <aside class="sheet guide-kit" aria-label="Free Study Focus Kit">
          <p><strong>Want this on paper?</strong> {g.get("kit", "The free Study Focus Kit has a printable worksheet for this system, plus four more.")}</p>
          <a class="btn" href="/#free-kit">Get the free kit</a>
        </aside>'''

RELATED = {
    "stop-checking-phone-while-studying": [("Why website blockers fail", "/guides/why-website-blockers-fail/"), ("Focus timer", "/tools/focus-timer/"), ("Stop procrastinating while studying", "/guides/stop-procrastinating-studying/")],
    "study-schedule-template": [("Study schedule maker", "/tools/study-schedule-maker/"), ("All free exam study plans", "/study-plan/"), ("Printable planners", "/planners/")],
    "how-to-create-a-study-schedule": [("Study schedule maker", "/tools/study-schedule-maker/"), ("All free exam study plans", "/study-plan/"), ("Printable planners", "/planners/")],
    "how-to-calculate-what-you-need-on-your-final": [("Final grade calculator", "/tools/final-grade-calculator/"), ("Weighted grade calculator", "/tools/weighted-grade-calculator/"), ("GPA calculator", "/tools/gpa-calculator/")],
    "how-to-study-for-the-nclex-pn": [("NCLEX-PN study plan generator", "/study-plan/nclex-pn/"), ("How to study for the NCLEX-RN", "/guides/how-to-study-for-the-nclex/"), ("NCLEX-PN 6-week printable planner", "/planners/nclex-pn-6-week-planner/")],
    "how-to-pace-yourself-on-a-timed-exam": [("Test time calculator", "/tools/test-time-calculator/"), ("Exam formats at a glance", "/exam-facts/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("All free exam study plans", "/study-plan/")],
    "gmat-study-plan-8-weeks": [("GMAT study plan generator", "/study-plan/gmat/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("GMAT 8-week printable planner", "/planners/")],
    "dat-study-schedule-10-weeks": [("DAT study plan generator", "/study-plan/dat/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("DAT 10-week printable planner", "/planners/")],
    "pance-study-plan-8-weeks": [("PANCE study plan generator", "/study-plan/pance/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("PANCE 8-week printable planner", "/planners/")],
    "naplex-study-plan-8-weeks": [("NAPLEX study plan generator", "/study-plan/naplex/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("NAPLEX 8-week printable planner", "/planners/")],
    "usmle-step-1-study-schedule": [("USMLE Step 1 study plan generator", "/study-plan/usmle-step-1/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("USMLE Step 1 8-week printable planner", "/planners/")],
    "lsat-study-schedule-12-weeks": [("LSAT study plan generator", "/study-plan/lsat/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("LSAT 12-week printable planner", "/planners/")],
    "gre-study-plan-8-weeks": [("GRE study plan generator", "/study-plan/gre/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("GRE 8-week printable planner", "/planners/")],
    "how-to-study-for-the-nclex": [("NCLEX-RN study plan generator", "/study-plan/nclex/"), ("NCLEX-PN study plan generator", "/study-plan/nclex-pn/"), ("How to study for the NCLEX-PN", "/guides/how-to-study-for-the-nclex-pn/"), ("NCLEX-RN 8-week printable planner", "/planners/")],
    "how-to-study-for-the-teas": [("TEAS study plan generator", "/study-plan/teas/"), ("How to study for the NCLEX", "/guides/how-to-study-for-the-nclex/"), ("Printable planners", "/planners/")],
    "cpa-study-schedule": [("CPA FAR plan generator", "/study-plan/cpa-far/"), ("CPA AUD plan generator", "/study-plan/cpa-aud/"), ("CPA REG plan generator", "/study-plan/cpa-reg/"), ("CPA FAR 10-week printable planner", "/planners/")],
    "how-long-to-study-for-exams": [("All free exam study plans", "/study-plan/"), ("Exam formats at a glance", "/exam-facts/"), ("How to pace a timed exam", "/guides/how-to-pace-yourself-on-a-timed-exam/"), ("How to create a study schedule", "/guides/how-to-create-a-study-schedule/"), ("Exam countdown calculator", "/tools/exam-countdown/"), ("Printable planners", "/planners/")],
    "mcat-error-log-template": [("MCAT study plan generator", "/study-plan/mcat/"), ("A 3-month MCAT study schedule", "/guides/mcat-study-schedule-3-months/"), ("MCAT 16-week printable planner", "/planners/")],
    "mcat-study-schedule-3-months": [("MCAT study plan generator", "/study-plan/mcat/"), ("How long to study for each exam", "/guides/how-long-to-study-for-exams/"), ("MCAT 16-week printable planner", "/planners/")],
}

def related_block(slug):
    if slug not in RELATED:
        return ""
    return '<p class="related-links"><strong>Related:</strong> ' + " · ".join(f'<a href="{u}">{t}</a>' for t, u in RELATED[slug]) + "</p>"

def guide_page(g):
    path = f"/guides/{g['slug']}/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Guides", "/guides/"), (g["h1"][0].upper() + g["h1"][1:], path)])
    heads = [(slug(h), h) for h, _ in g["sections"]]
    toc = "\n".join(f'          <li><a href="#{i}">{h}</a></li>' for i, h in heads)
    secs = "\n".join(f'        <h2 id="{slug(h)}">{h}</h2>\n        {body}' for h, body in g["sections"])
    ld = {"@context": "https://schema.org", "@graph": [
      {"@type": "Article", "headline": g["title"], "description": g["desc"], "url": SITE + path, "datePublished": g.get("date", PUBLISHED), "dateModified": g.get("date", PUBLISHED),
       "author": ORG, "publisher": ORG, "image": (f"https://i.ytimg.com/vi/{g['video']}/hqdefault.jpg" if g.get("video") else SITE + "/assets/og-image.png"), "mainEntityOfPage": SITE + path},
      crumb_ld]}
    watch_toc = '          <li><a href="#watch">Watch the video</a></li>' if g.get("video") else ""
    watch = (f"""        <h2 id="watch">Watch the video</h2>
        <a class="video" href="https://www.youtube.com/watch?v={g['video']}" data-video="{g['video']}">
          <span class="video-frame"><img src="https://i.ytimg.com/vi/{g['video']}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" decoding="async"></span>
          <span class="video-title">Watch on the FocusFlow Lab YouTube channel</span></a>""" if g.get("video") else "")
    body = f"""{crumb_html}

    <main id="main">
      <header class="doc-head guide-head">
        <span class="card-tag">{g['tag']}</span>
        <h1>{g['h1']}</h1>
        <p class="lead">{g['lead']}</p>
        <p>By FocusFlow Lab. Published <time datetime="{g.get('date', PUBLISHED)}">{nice_date(g.get('date', PUBLISHED))}</time>.</p>
      </header>
      <div class="doc">
        <nav class="toc" aria-label="On this page">
          <p>On this page</p>
          <ol>
{toc}
{watch_toc}
          </ol>
        </nav>
        <article class="prose">
{secs}
{watch}
{related_block(g["slug"])}
{TRACKER_FORM(g["signup"]) if g.get("signup") else KIT_BOX(g)}
        <p class="refs"><strong>{"Sources" if "<br>" in REFS[g['slug']] else "Source"}:</strong> {REFS[g['slug']]}</p>
        </article>
      </div>
    </main>"""
    title = g["title"] if len(g["title"]) > 52 else g["title"] + " | FocusFlow Lab"
    return shell(path=path, title=title, desc=g["desc"], og_title=g["title"], ld=ld, body=body, css_depth=2, scripts=VIDEO_SCRIPT)

def index_page():
    path = "/guides/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Guides", path)])
    desc = "Short, practical study guides from FocusFlow Lab: stop phone distractions, take notes you remember, clear mental clutter and cover your syllabus faster."
    cards = "\n".join(f'        <li><a href="{g["slug"]}/"><span class="card-tag">{g["tag"]}</span><h2 class="card-name">{g["h1"][0].upper() + g["h1"][1:]}</h2><span class="card-note">{g["card"]}</span><span class="card-go">Read the guide</span></a></li>' for g in GUIDES)
    ld = {"@context": "https://schema.org", "@graph": [
      {"@type": "CollectionPage", "name": "Study guides", "url": SITE + path, "description": desc, "publisher": ORG,
       "hasPart": [{"@type": "Article", "headline": g["title"], "url": f"{SITE}/guides/{g['slug']}/"} for g in GUIDES]}, crumb_ld]}
    body = f"""{crumb_html}

    <main id="main">
      <section class="hero single wash">
        <div>
          <h1>Study guides.</h1>
          <p class="lead">Short, practical guides to studying: focus, memory, planning and finals. Most go with a FocusFlow video.</p>
        </div>
      </section>
      <div class="plan-search guide-filter" data-filter-for="guide-cards" data-chips hidden>
        <label for="guide-search-input">Search guides</label>
        <input type="search" id="guide-search-input" placeholder="Try phone, finals, nclex or memory" autocomplete="off" aria-describedby="guide-search-count">
        <div class="filter-chips" role="group" aria-label="Filter by category"></div>
        <p class="plan-search-count" id="guide-search-count" role="status" aria-live="polite"></p>
        <p class="plan-search-empty" hidden>No guide matches that yet. <a href="mailto:hello@thefocusflowlab.com?subject=Guide%20request">Tell us what you’d like a guide on</a>.</p>
      </div>
      <ul class="cards" id="guide-cards">
{cards}
{{% for g in site.guides reversed %}}
        <li><a href="{{{{ g.url }}}}"><span class="card-tag">{{{{ g.tag | default: "Study system" }}}}</span><h2 class="card-name">{{{{ g.title }}}}</h2><span class="card-note">{{{{ g.card | default: g.lead }}}}</span><span class="card-go">Read the guide</span></a></li>
{{% endfor %}}
      </ul>
    </main>"""
    return shell(path=path, title="Study Guides: Focus, Memory and Exam Planning | FocusFlow Lab", desc=desc, og_title="Study guides from FocusFlow Lab",
                 ld=ld, body=body, css_depth=1, extra_head='\n  <link rel="stylesheet" href="../study-plan/assets/plan.css">')

(ROOT / "guides").mkdir(exist_ok=True)
# Front matter so Jekyll adds auto-published video guides (_guides/*.md) to the list.
(ROOT / "guides/index.html").write_text("---\n---\n" + index_page(), encoding="utf-8", newline="\n")
for g in GUIDES:
    out = ROOT / "guides" / g["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(guide_page(g), encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT).as_posix())
