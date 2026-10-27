"""Generate /guides/ pages.  Run: cd _tools && python guides.py && cd .. && python _tools/build.py"""
import pathlib, re
from common import shell, crumbs, ORG, SITE

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
<p>Each step is small. Together they turn “just checking” into a decision, and most of the time you’ll decide not to.</p>"""),
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
       title="How to Study for Finals in a Week: A Day-by-Day Plan",
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
       title="Does Cramming Work? What to Do If You Have to Cram",
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
       title="How Long Should You Study for Each Exam? NCLEX, MCAT, USMLE and More",
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
]

REFS = {
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
        <aside class="sheet guide-kit" aria-label="Free Study Focus Kit">
          <p><strong>Want this on paper?</strong> {g.get("kit", "The free Study Focus Kit has a printable worksheet for this system, plus four more.")}</p>
          <a class="btn" href="/#free-kit">Get the free kit</a>
        </aside>
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
      <ul class="cards">
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
