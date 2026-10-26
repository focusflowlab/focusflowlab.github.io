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
]

REFS = {
  "stop-checking-phone-while-studying": "Ward, A. F., Duke, K., Gneezy, A., &amp; Bos, M. W. (2017). Brain drain: The mere presence of one’s own smartphone reduces available cognitive capacity. <em>Journal of the Association for Consumer Research</em>, 2(2).",
  "active-recall-notes": "Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., &amp; Willingham, D. T. (2013). Improving students’ learning with effective learning techniques. <em>Psychological Science in the Public Interest</em>, 14(1).",
  "brain-dump-before-studying": "Masicampo, E. J., &amp; Baumeister, R. F. (2011). Consider it done! Plan making can eliminate the cognitive effects of unfulfilled goals. <em>Journal of Personality and Social Psychology</em>, 101(4).",
  "stop-rereading-cover-syllabus-faster": "Karpicke, J. D., &amp; Roediger, H. L. (2008). The critical importance of retrieval for learning. <em>Science</em>, 319(5865).",
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

def guide_page(g):
    path = f"/guides/{g['slug']}/"
    crumb_html, crumb_ld = crumbs([("Home", "/"), ("Guides", "/guides/"), (g["h1"][0].upper() + g["h1"][1:], path)])
    heads = [(slug(h), h) for h, _ in g["sections"]]
    toc = "\n".join(f'          <li><a href="#{i}">{h}</a></li>' for i, h in heads)
    secs = "\n".join(f'        <h2 id="{slug(h)}">{h}</h2>\n        {body}' for h, body in g["sections"])
    ld = {"@context": "https://schema.org", "@graph": [
      {"@type": "Article", "headline": g["title"], "description": g["desc"], "url": SITE + path, "datePublished": PUBLISHED, "dateModified": PUBLISHED,
       "author": ORG, "publisher": ORG, "image": f"https://i.ytimg.com/vi/{g['video']}/hqdefault.jpg", "mainEntityOfPage": SITE + path},
      crumb_ld]}
    body = f"""{crumb_html}

    <main id="main">
      <header class="doc-head guide-head">
        <span class="card-tag">{g['tag']}</span>
        <h1>{g['h1']}</h1>
        <p class="lead">{g['lead']}</p>
        <p>By FocusFlow Lab. Published <time datetime="{PUBLISHED}">26 October 2026</time>.</p>
      </header>
      <div class="doc">
        <nav class="toc" aria-label="On this page">
          <p>On this page</p>
          <ol>
{toc}
          <li><a href="#watch">Watch the video</a></li>
          </ol>
        </nav>
        <article class="prose">
{secs}
        <h2 id="watch">Watch the video</h2>
        <a class="video" href="https://www.youtube.com/watch?v={g['video']}" data-video="{g['video']}">
          <span class="video-frame"><img src="https://i.ytimg.com/vi/{g['video']}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" decoding="async"></span>
          <span class="video-title">Watch on the FocusFlow Lab YouTube channel</span></a>
        <aside class="sheet guide-kit">
          <p><strong>Want this on paper?</strong> The free Study Focus Kit has a printable worksheet for this system, plus four more.</p>
          <a class="btn" href="/#free-kit">Get the free kit</a>
        </aside>
        <p class="refs"><strong>Source:</strong> {REFS[g['slug']]}</p>
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
          <p class="lead">Short, practical guides to the FocusFlow systems. Each one goes with a video and a worksheet in the free kit.</p>
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
