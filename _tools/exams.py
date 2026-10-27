"""Generate the newer exam plan pages from one template.

Run from the repo root:  python _tools/exams.py && python _tools/build.py
Edit the EXAMS data below, never the generated pages by hand.
JS task strings use typographic apostrophes (’) only, so single quotes never break them.
"""
import json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = "2026-10-26"

EXAMS = [
  {
    "slug": "nclex-pn",
    "short": "NCLEX-PN",
    "title": "NCLEX-PN Study Plan Generator: Free Weekly Schedule",
    "desc": "Put in your NCLEX-PN date and free hours. Get a week-by-week plan weighted to the PN client-needs categories, with extra time on your weak areas.",
    "og_title": "NCLEX-PN study plan generator",
    "h1": "Your NCLEX-PN weeks, planned in a minute.",
    "lead": "Put in your test date and the hours you really have. You get a week-by-week plan that follows the PN test plan.",
    "date_label": "Exam date", "legend": "Where do you feel shaky? (optional)", "button": "Build my plan",
    "days_default": 5, "hours_default": 3,
    "config": {"id": "nclex-pn", "shortName": "NCLEX-PN", "maxDays": 180, "reviewShare": 0.4, "recommendedHours": {"min": 80, "max": 180}},
    "topics": [("Coordinated Care", 21), ("Safety and Infection Control", 13), ("Pharmacological Therapies", 13), ("Psychosocial Integrity", 12), ("Reduction of Risk Potential", 12), ("Basic Care and Comfort", 10), ("Physiological Adaptation", 10), ("Health Promotion", 9)],
    "tasks": """{
        review: (days) => [
          'Read up on one or two of this week’s categories each study day.',
          `End each day with 40 to 60 questions on what you covered, about ${days * 50} this week.`,
          'Start an error log: why you missed it, not just the answer.'
        ],
        practice: (days) => [
          `Do 60 to 100 mixed questions per study day, about ${days * 80} this week.`,
          'Read every rationale, even on the ones you got right.',
          'Take one timed practice test and note your weakest category.',
          'Open each day with 20 minutes on your error log.'
        ],
        final: () => [
          'Keep it light: 40 to 60 questions a day and your error log. Nothing new.',
          'Go over medication safety, infection control and scope of practice.',
          'Confirm your ID, test center and start time.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>The NCLEX-PN is a computer-adaptive test for practical and vocational nurses. Like the RN exam, it picks each question based on your earlier answers, so it rewards judgment over memorized facts.</p>
          <ol>
            <li><strong>Content review, the first 40% or so.</strong> One or two categories a day, each day ending with questions on what you read.</li>
            <li><strong>Practice and review, most of the middle.</strong> Mixed question sets daily, every rationale read, one timed practice test a week.</li>
            <li><strong>Final week.</strong> About 60% of your usual hours, your error log, and a day off before the exam.</li>
          </ol>
          <p>Topic hours follow the midpoints of the client-needs ranges on the NCLEX-PN test plan, so Coordinated Care gets the most time. Any area you tick as shaky gets 50% more.</p>
          <p>Check the current test plan at <a href="https://www.ncsbn.org/" rel="noopener">ncsbn.org</a> before you rely on it.</p>""",
    "faq": [
      ("How long should I study for the NCLEX-PN?", "Many grads give it 4 to 8 weeks at around 2 to 4 hours a day. If you work full time, a longer, lighter plan is easier to keep."),
      ("How many practice questions a day?", "Around 60 to 100 once content review is done. Reading every rationale matters more than the raw number."),
      ("Is this an official NCLEX-PN plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to NCSBN."),
    ],
    "note": "NCLEX® and NCLEX-PN® are registered trademarks of the National Council of State Boards of Nursing (NCSBN). FocusFlow Lab isn’t affiliated with or endorsed by NCSBN.",
    "tag": "Nursing",
  },
  {
    "slug": "usmle-step-1",
    "short": "USMLE Step 1",
    "title": "USMLE Step 1 Study Schedule Generator: Free Plan",
    "desc": "Put in your USMLE Step 1 date and daily hours. Get a week-by-week systems-based schedule with question blocks and self-assessments built in.",
    "og_title": "USMLE Step 1 study schedule generator",
    "h1": "Your Step 1 dedicated period, week by week.",
    "lead": "Put in your test date and your study hours. You get a systems-based schedule with daily question blocks and self-assessments.",
    "date_label": "Test date", "legend": "Which areas worry you? (optional)", "button": "Build my schedule",
    "days_default": 6, "hours_default": 8,
    "config": {"id": "usmle-step-1", "shortName": "Step 1", "maxDays": 365, "reviewShare": 0.45, "recommendedHours": {"min": 250, "max": 500}},
    "topics": [("General principles", 18), ("Nervous system and behavior", 15), ("Reproductive and endocrine", 12), ("Cardiovascular", 9), ("Musculoskeletal and skin", 9), ("Respiratory", 8), ("Renal and urinary", 8), ("Gastrointestinal", 8), ("Blood, lymph and immune", 8)],
    "tasks": """{
        review: (days) => [
          'Cover this week’s systems in order, biggest first.',
          `Do one or two timed blocks of questions a day on those systems, about ${days * 60} this week.`,
          'Review every block the same day and add misses to your flashcards.',
          'Do your flashcard reviews first thing, before new material.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one NBME self-assessment, timed, in one sitting.' : 'Take one practice exam in your question bank, timed.',
          `Do 2 or 3 random timed blocks a day, about ${days * 100} questions this week.`,
          'Spend the morning after an assessment reviewing it fully.',
          'Aim the rest of the week at your weakest systems.'
        ],
        final: () => [
          'Take your last self-assessment about a week before the test.',
          'Light review only: flashcards, missed questions, high-yield facts.',
          'Confirm your permit, ID, test center and start time.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>Step 1 is a one-day, roughly eight-hour exam and is now scored pass or fail. Questions mix basic science with the organ systems, so the schedule is built around systems, with general principles (biochemistry, genetics, immunology, microbiology and pharmacology) as its own block.</p>
          <ol>
            <li><strong>Systems review, a bit under half.</strong> Each week covers a few systems, with timed question blocks on them every day.</li>
            <li><strong>Mixed practice, the rest.</strong> Random timed blocks across all systems, with a self-assessment every week or two.</li>
            <li><strong>Final week.</strong> Your last self-assessment about a week out, light review, and a day off before the test.</li>
          </ol>
          <p>Topic hours roughly follow the share of each system in the USMLE content outline. Any area you tick as a worry gets 50% more time. These weights are rough, not official.</p>
          <p>Check the current content outline and rules at <a href="https://www.usmle.org/" rel="noopener">usmle.org</a> before you rely on them.</p>""",
    "faq": [
      ("How long is a Step 1 dedicated period?", "Many students take 4 to 8 weeks of dedicated study at 8 to 10 hours a day, after building a base during the preclinical years."),
      ("How many practice questions should I do?", "Many students finish one full question bank, roughly 3,000 to 4,000 questions, and review each block the same day."),
      ("Is this an official USMLE schedule?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to the FSMB or NBME."),
    ],
    "note": "USMLE® is a joint program of the Federation of State Medical Boards (FSMB) and the National Board of Medical Examiners (NBME). FocusFlow Lab isn’t affiliated with or endorsed by either.",
    "tag": "Medicine",
  },
  {
    "slug": "gre",
    "short": "GRE",
    "title": "GRE Study Plan Generator: Free Week-by-Week Schedule",
    "desc": "Put in your GRE date and the hours you have. Get a week-by-week plan across verbal, quant and the essay, with practice tests in the right weeks.",
    "og_title": "GRE study plan generator",
    "h1": "Your GRE prep, laid out week by week.",
    "lead": "Put in your test date and the hours you can give it. You get a plan across verbal, quant and the essay.",
    "date_label": "Test date", "legend": "Which areas worry you? (optional)", "button": "Build my plan",
    "days_default": 5, "hours_default": 2,
    "config": {"id": "gre", "shortName": "GRE", "maxDays": 270, "reviewShare": 0.5, "recommendedHours": {"min": 40, "max": 120}},
    "topics": [("Reading comprehension", 16), ("Data analysis", 14), ("Algebra", 14), ("Arithmetic", 12), ("Text completion", 12), ("Geometry", 10), ("Sentence equivalence", 10), ("Analytical writing", 6), ("Vocabulary", 6)],
    "tasks": """{
        review: (days) => [
          'Learn or relearn this week’s topics, one or two a day.',
          `Finish each day with practice questions on what you covered, about ${days * 20} this week.`,
          'Learn 10 to 15 new words a day and review the old ones.',
          'Keep a list of every question type that trips you up.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one full practice test, timed, in one sitting.' : 'Do timed mixed sections: one verbal, one quant.',
          'Review every miss: content gap, misread or timing?',
          'Write one Issue essay, timed at 30 minutes.',
          'Spend the rest of the week on your weakest question type.'
        ],
        final: () => [
          'Take your last practice test about five days before the test.',
          'Light review only: vocabulary, formulas and your miss list.',
          'Confirm your ID, test center or home setup, and start time.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>The GRE General Test is just under two hours: two Verbal Reasoning sections, two Quantitative Reasoning sections and one Analytical Writing task, “Analyze an Issue”.</p>
          <ol>
            <li><strong>Content review, the first half.</strong> Quant topics and verbal question types, a couple a day, with practice questions to finish.</li>
            <li><strong>Practice, the second half.</strong> A full practice test every other week, timed sections in between, and one timed essay a week.</li>
            <li><strong>Final week.</strong> Your last practice test about five days out, light review, and a day off before the test.</li>
          </ol>
          <p>Quant and verbal get about the same total time, with less for the essay. Any area you tick as a worry gets 50% more.</p>
          <p>Use the free official practice tests from ETS, and check current rules at <a href="https://www.ets.org/gre.html" rel="noopener">ets.org/gre</a>.</p>""",
    "faq": [
      ("How long should I study for the GRE?", "Many people study for 1 to 3 months and put in around 40 to 120 hours, depending on their starting score and target."),
      ("How many practice tests should I take?", "At least the free official ones, spaced out across the second half of your prep, with a full review of each."),
      ("Is this an official GRE plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to ETS."),
    ],
    "note": "GRE® is a registered trademark of ETS. FocusFlow Lab isn’t affiliated with or endorsed by ETS.",
    "tag": "Grad school",
  },
  {
    "slug": "lsat",
    "short": "LSAT",
    "title": "LSAT Study Schedule Generator: Free Weekly Plan",
    "desc": "Put in your LSAT date and the hours you have. Get a week-by-week schedule for logical reasoning, reading comprehension and the writing sample.",
    "og_title": "LSAT study schedule generator",
    "h1": "Your LSAT prep, planned week by week.",
    "lead": "Put in your test date and the hours you can give it. You get a schedule built around logical reasoning and reading.",
    "date_label": "Test date", "legend": "Which areas worry you? (optional)", "button": "Build my schedule",
    "days_default": 5, "hours_default": 2.5,
    "config": {"id": "lsat", "shortName": "LSAT", "maxDays": 365, "reviewShare": 0.45, "recommendedHours": {"min": 120, "max": 300}},
    "topics": [("Reading comprehension", 26), ("Flaw and assumption", 20), ("Strengthen and weaken", 14), ("Inference questions", 12), ("Other reasoning questions", 10), ("Method and parallel", 8), ("Timing drills", 6), ("Argumentative writing", 4)],
    "tasks": """{
        review: (days) => [
          'Learn this week’s question types, one or two a day.',
          `Drill each type untimed first, then timed, about ${days * 15} questions this week.`,
          'Do two reading passages every study day.',
          'Write down why each wrong answer is wrong, not just the right one.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one full practice test, timed, in one sitting.' : 'Do two timed sections: one reasoning, one reading.',
          'Blind review: redo the hard questions untimed before checking answers.',
          'Spend the rest of the week on your weakest question type.',
          'Write one practice argumentative essay.'
        ],
        final: () => [
          'Take your last full practice test about five days before the test.',
          'Light review only: your notes on question types and common traps.',
          'Check your ID, test setup and start time.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>The LSAT has four multiple-choice sections: two scored Logical Reasoning, one scored Reading Comprehension and one unscored section. There’s also a separate, unscored Argumentative Writing sample that schools see. Since 2024 there are no logic games.</p>
          <ol>
            <li><strong>Learn the question types, a bit under half.</strong> One or two types a day, untimed first, then timed, plus daily reading passages.</li>
            <li><strong>Timed practice, the rest.</strong> A full practice test every other week, timed sections in between, and blind review of every hard question.</li>
            <li><strong>Final week.</strong> Your last practice test about five days out, light review, and a day off before the test.</li>
          </ol>
          <p>Logical reasoning gets about two thirds of the time because it’s two of the three scored sections. Any area you tick as a worry gets 50% more.</p>
          <p>Use the official practice tests on LawHub, and check current rules at <a href="https://www.lsac.org/" rel="noopener">lsac.org</a>.</p>""",
    "faq": [
      ("How long should I study for the LSAT?", "Many people study for 2 to 4 months, often around 120 to 300 hours, depending on their starting score and target."),
      ("What is blind review?", "After a timed section, redo the questions you weren’t sure of without a timer and before seeing answers. It shows whether misses come from reasoning or from time pressure."),
      ("Is this an official LSAT plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to LSAC."),
    ],
    "note": "LSAT® is a registered trademark of the Law School Admission Council (LSAC). FocusFlow Lab isn’t affiliated with or endorsed by LSAC.",
    "tag": "Law school",
  },
  {
    "slug": "pance",
    "short": "PANCE",
    "title": "PANCE Study Plan Generator: Free Weekly Schedule",
    "desc": "Put in your PANCE date and study hours. Get a week-by-week plan weighted to the organ systems on the NCCPA blueprint, with extra time on your weak areas.",
    "og_title": "PANCE study plan generator",
    "h1": "Your PANCE study plan, week by week.",
    "lead": "Put in your exam date and the hours you have. You get a plan across the organ systems, heaviest first.",
    "date_label": "Exam date", "legend": "Which systems feel shaky? (optional)", "button": "Build my plan",
    "days_default": 6, "hours_default": 5,
    "config": {"id": "pance", "shortName": "PANCE", "maxDays": 270, "reviewShare": 0.45, "recommendedHours": {"min": 150, "max": 350}},
    "topics": [("Cardiovascular", 13), ("Pulmonary", 10), ("Gastrointestinal and nutrition", 9), ("Musculoskeletal", 8), ("Endocrine", 7), ("EENT", 7), ("Neurologic", 7), ("Reproductive", 7), ("Infectious disease", 6), ("Psychiatry and behavioral", 6), ("Dermatologic", 5), ("Genitourinary", 5), ("Hematologic", 5), ("Renal", 5)],
    "tasks": """{
        review: (days) => [
          'Review this week’s organ systems, biggest first.',
          `Finish each day with questions on what you covered, about ${days * 50} this week.`,
          'Keep an error log: the diagnosis or treatment you missed, and why.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one timed practice exam in a single sitting.' : `Do mixed question blocks across all systems, about ${days * 80} this week.`,
          'Review every question, including the ones you got right.',
          'Spend the rest of the week on your two weakest systems.',
          'Open each day with 20 minutes on your error log.'
        ],
        final: () => [
          'Light review only: your error log and high-yield tables.',
          'Confirm your exam appointment, ID and test centre.',
          'No new material in the last two days.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>The PANCE tests what new physician assistants need across the organ systems, along with tasks like history-taking, diagnosis and pharmacology. Cardiovascular and pulmonary carry the most questions, so they get the most time here.</p>
          <ol>
            <li><strong>Systems review, a bit under half.</strong> A few systems a week, each day ending with questions on what you covered.</li>
            <li><strong>Mixed practice, the rest.</strong> Question blocks across all systems, a timed practice exam every other week, and focused work on your weakest areas.</li>
            <li><strong>Final week.</strong> Error log and high-yield review, nothing new, and a day off before the exam.</li>
          </ol>
          <p>Topic hours follow the rough share of each organ system on the NCCPA content blueprint. Any system you tick as shaky gets 50% more time. These shares are rough, not official.</p>
          <p>Check the current blueprint at <a href="https://www.nccpa.net/" rel="noopener">nccpa.net</a> before you rely on it.</p>""",
    "faq": [
      ("How long should I study for the PANCE?", "Many students give it 4 to 12 weeks after graduation, often around 150 to 350 hours, depending on how their rotations went."),
      ("How many practice questions should I do?", "Many students work through one full question bank and take a few timed practice exams, reviewing every question."),
      ("Is this an official PANCE plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to the NCCPA."),
    ],
    "note": "The PANCE is the Physician Assistant National Certifying Exam, run by the National Commission on Certification of Physician Assistants (NCCPA). FocusFlow Lab isn’t affiliated with or endorsed by the NCCPA.",
    "tag": "Medicine",
  },
  {
    "slug": "naplex",
    "short": "NAPLEX",
    "title": "NAPLEX Study Plan Generator: Free Weekly Schedule",
    "desc": "Put in your NAPLEX date and study hours. Get a week-by-week plan weighted to the NAPLEX competency areas, with calculations practice every week.",
    "og_title": "NAPLEX study plan generator",
    "h1": "Your NAPLEX study plan, week by week.",
    "lead": "Put in your exam date and the hours you have. You get a plan weighted to the NAPLEX areas, with calculations every week.",
    "date_label": "Exam date", "legend": "Which areas feel shaky? (optional)", "button": "Build my plan",
    "days_default": 6, "hours_default": 5,
    "config": {"id": "naplex", "shortName": "NAPLEX", "maxDays": 270, "reviewShare": 0.45, "recommendedHours": {"min": 120, "max": 300}},
    "topics": [("Treatment plans", 35), ("Patient data and assessment", 18), ("Drug characteristics", 14), ("Calculations", 14), ("Compounding and dispensing", 11), ("Practice and medication-use systems", 8)],
    "tasks": """{
        review: (days) => [
          'Review this week’s drug classes and disease states, biggest first.',
          `Do calculations every study day, about ${days * 10} problems this week.`,
          'End each day with questions on what you covered.',
          'Keep an error log: the drug fact or step you missed, and why.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one timed practice exam in a single sitting.' : `Do mixed question sets, about ${days * 60} questions this week.`,
          'Keep calculations going daily: 10 problems before anything else.',
          'Spend the rest of the week on your weakest area.',
          'Review your error log before each session.'
        ],
        final: () => [
          'Light review only: top drugs, your error log and key calculations.',
          'Confirm your appointment, ID and test centre.',
          'No new material in the last two days.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>The NAPLEX tests whether you can practise safely as a new pharmacist. Building and managing treatment plans is the biggest area, so it gets the most time. Calculations show up every week because they’re easy points that fade without practice.</p>
          <ol>
            <li><strong>Content review, a bit under half.</strong> Disease states and drug classes, with daily calculations and questions on what you covered.</li>
            <li><strong>Mixed practice, the rest.</strong> Timed practice exams every other week, mixed question sets in between, and focused work on your weakest area.</li>
            <li><strong>Final week.</strong> Light review, nothing new, and a day off before the exam.</li>
          </ol>
          <p>Topic hours follow the rough share of each competency area on the NAPLEX blueprint. Any area you tick as shaky gets 50% more time. These shares are rough, not official.</p>
          <p>Check the current blueprint at <a href="https://nabp.pharmacy/" rel="noopener">nabp.pharmacy</a> before you rely on it.</p>""",
    "faq": [
      ("How long should I study for the NAPLEX?", "Many graduates study for 4 to 8 weeks, often around 120 to 300 hours, starting soon after finishing their program."),
      ("How do I get better at NAPLEX calculations?", "Do a small set every day rather than a big block once a week, and write out every step. Most calculation misses come from units and rounding."),
      ("Is this an official NAPLEX plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to NABP."),
    ],
    "note": "NAPLEX® is a registered trademark of the National Association of Boards of Pharmacy (NABP). FocusFlow Lab isn’t affiliated with or endorsed by NABP.",
    "tag": "Pharmacy",
  },
  {
    "slug": "cpa-far",
    "short": "CPA FAR",
    "title": "CPA FAR Study Plan Generator: Free Weekly Schedule",
    "desc": "Put in your CPA FAR exam date and study hours. Get a week-by-week plan across the three FAR content areas, with practice questions and simulations built in.",
    "og_title": "CPA FAR study plan generator",
    "h1": "Your CPA FAR study plan, week by week.",
    "lead": "Put in your exam date and the hours you have. You get a plan across the FAR areas, with simulations in the second half.",
    "date_label": "Exam date", "legend": "Which areas feel shaky? (optional)", "button": "Build my plan",
    "days_default": 5, "hours_default": 2.5,
    "config": {"id": "cpa-far", "shortName": "FAR", "maxDays": 270, "reviewShare": 0.55, "recommendedHours": {"min": 100, "max": 180}},
    "topics": [("Financial reporting", 35), ("Select balance sheet accounts", 35), ("Select transactions", 30)],
    "tasks": """{
        review: (days) => [
          'Work through this week’s topics, one or two a study day.',
          `Do multiple-choice questions on each topic the same day, about ${days * 30} this week.`,
          'Keep an error log: the rule you missed, and why.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one timed practice exam, multiple choice and simulations.' : 'Do timed simulations on your weakest topics.',
          `Do mixed multiple-choice sets, about ${days * 40} questions this week.`,
          'Review every miss and re-work the simulation steps.',
          'Re-read your error log at the start of each session.'
        ],
        final: () => [
          'Light review only: your error log and formulas.',
          'Confirm your Notice to Schedule, appointment and ID.',
          'No new topics in the last two days.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>FAR (Financial Accounting and Reporting) is one of the three core CPA sections and usually the one people find longest. It has multiple-choice questions and task-based simulations, so the plan adds simulations once you’ve covered the content.</p>
          <ol>
            <li><strong>Content review, a bit over half.</strong> One or two topics a day, each ending with multiple-choice questions on what you covered.</li>
            <li><strong>Practice, the rest.</strong> Timed practice exams every other week, simulations on your weak topics, and mixed question sets.</li>
            <li><strong>Final week.</strong> Light review, nothing new, and a day off before the exam.</li>
          </ol>
          <p>Topic hours follow the rough midpoints of the three FAR content areas in the AICPA blueprint. Any area you tick as shaky gets 50% more time. These shares are rough, not official.</p>
          <p>Check the current blueprint at <a href="https://www.aicpa-cima.com/" rel="noopener">aicpa-cima.com</a> before you rely on it.</p>""",
    "faq": [
      ("How many hours should I study for FAR?", "Many candidates plan around 100 to 180 hours for FAR, more than for the other sections, spread over 8 to 12 weeks while working."),
      ("Can I study for FAR while working full time?", "Yes. Set fewer hours a day and more weeks: 2 to 3 hours on weekdays and a longer session at the weekend is a common pattern."),
      ("Is this an official CPA plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to the AICPA, NASBA or any state board."),
    ],
    "note": "CPA is a designation granted by state boards of accountancy. The Uniform CPA Examination is developed by the AICPA. FocusFlow Lab isn’t affiliated with or endorsed by the AICPA, NASBA or any board of accountancy.",
    "tag": "Accounting",
  },
  {
    "slug": "teas",
    "short": "ATI TEAS",
    "title": "TEAS Study Plan Generator: Free Weekly TEAS 7 Schedule",
    "desc": "Put in your ATI TEAS test date and study hours. Get a week-by-week plan across reading, math, science and English, weighted to the TEAS 7 question counts.",
    "og_title": "TEAS study plan generator",
    "h1": "Your TEAS study plan, week by week.",
    "lead": "Put in your test date and the hours you have. You get a plan across all four TEAS sections, with science getting the most time.",
    "date_label": "Test date", "legend": "Which sections feel shaky? (optional)", "button": "Build my plan",
    "days_default": 5, "hours_default": 1.5,
    "config": {"id": "teas", "shortName": "TEAS", "maxDays": 180, "reviewShare": 0.55, "recommendedHours": {"min": 30, "max": 80}},
    "topics": [("Science", 29), ("Reading", 26), ("Math", 23), ("English and language usage", 22)],
    "tasks": """{
        review: (days) => [
          'Review this week’s sections, science first if it’s on the list.',
          `End each study day with practice questions on what you covered, about ${days * 20} this week.`,
          'Keep an error log: the fact or step you missed, and why.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one full timed practice test.' : 'Do timed section practice on your weakest section.',
          `Do mixed question sets, about ${days * 30} questions this week.`,
          'Review every miss, including lucky guesses.',
          'Re-read your error log at the start of each session.'
        ],
        final: () => [
          'Light review only: your error log and math formulas.',
          'Check your test appointment, ID and what you can bring.',
          'No new topics in the last two days.',
          'Rest the day before and sleep early.'
        ]
      }""",
    "how": """<p>The ATI TEAS is the entrance exam many nursing and allied health programs use. TEAS 7 has four sections: reading, math, science and English and language usage. Science has the most questions, so it gets the most time.</p>
          <ol>
            <li><strong>Content review, about half.</strong> Each study day covers one area and ends with practice questions on it.</li>
            <li><strong>Practice, the rest.</strong> Full timed practice tests every other week and timed sets on your weakest section.</li>
            <li><strong>Final week.</strong> Light review, nothing new, and rest before test day.</li>
          </ol>
          <p>Section hours follow the share of questions in each TEAS 7 section. Any section you tick as shaky gets 50% more time. Your program may set its own minimum score, so check it.</p>
          <p>Check the current test details at <a href="https://www.atitesting.com/teas" rel="noopener">atitesting.com</a> before you rely on it.</p>""",
    "faq": [
      ("How long should I study for the TEAS?", "Most people plan 4 to 8 weeks at 1 to 2 hours a day. If your math or science is rusty, give yourself the longer end."),
      ("Which TEAS section is hardest?", "Science is the largest section and the one most people find hardest, because it covers anatomy and physiology, biology, chemistry and scientific reasoning."),
      ("Is this an official TEAS plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to ATI."),
    ],
    "note": "TEAS and ATI are registered trademarks of Assessment Technologies Institute, LLC. FocusFlow Lab isn’t affiliated with or endorsed by ATI.",
    "tag": "Nursing",
  },
  {
    "slug": "dat",
    "short": "DAT",
    "title": "DAT Study Schedule Generator: Free Weekly Plan",
    "desc": "Put in your DAT test date and study hours. Get a week-by-week plan across biology, general and organic chemistry, perceptual ability, reading and quantitative reasoning.",
    "og_title": "DAT study schedule generator",
    "h1": "Your DAT study schedule, week by week.",
    "lead": "Put in your test date and the hours you have. You get a plan across every DAT section, with perceptual ability practice every week.",
    "date_label": "Test date", "legend": "Which sections feel shaky? (optional)", "button": "Build my plan",
    "days_default": 6, "hours_default": 4,
    "config": {"id": "dat", "shortName": "DAT", "maxDays": 180, "reviewShare": 0.5, "recommendedHours": {"min": 200, "max": 350}},
    "topics": [("Biology", 20), ("Perceptual ability", 20), ("General chemistry", 15), ("Organic chemistry", 15), ("Reading comprehension", 15), ("Quantitative reasoning", 15)],
    "tasks": """{
        review: (days) => [
          'Review this week’s sections, biggest first.',
          'Do one perceptual ability set every study day, even in content weeks.',
          `End each day with questions on what you covered, about ${days * 30} this week.`,
          'Keep an error log: the concept you missed, and why.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one full-length timed practice test.' : 'Do timed section practice on your weakest two sections.',
          `Do mixed question sets, about ${days * 40} questions this week.`,
          'Review every miss before moving on.',
          'Keep perceptual ability practice going daily.'
        ],
        final: () => [
          'Light review only: your error log and formulas.',
          'Check your Prometric appointment and ID.',
          'No new topics in the last two days.',
          'Rest the day before and sleep early.'
        ]
      }""",
    "how": """<p>The Dental Admission Test has four parts: the Survey of the Natural Sciences (biology, general chemistry and organic chemistry), perceptual ability, reading comprehension and quantitative reasoning. Perceptual ability is a skill, not content, so the plan practises it every week.</p>
          <ol>
            <li><strong>Content review, about half.</strong> Science and math content by section, with questions at the end of each day and a daily perceptual ability set.</li>
            <li><strong>Practice, the rest.</strong> Full-length practice tests every other week and timed work on your weakest sections.</li>
            <li><strong>Final week.</strong> Light review, nothing new, and rest before test day.</li>
          </ol>
          <p>Section hours are rough shares based on the question counts and how much content each section covers. They aren’t official. Any section you tick as shaky gets 50% more time.</p>
          <p>Check the current test details at <a href="https://www.ada.org/education/testing/dental-admission-test" rel="noopener">ada.org</a> before you rely on it.</p>""",
    "faq": [
      ("How long should I study for the DAT?", "Many students plan around 2 to 3 months at 4 or more hours a day, roughly 200 to 350 hours, depending on how recently they took the sciences."),
      ("How do I get better at perceptual ability?", "Practise it a little every day rather than in big blocks. The question types follow patterns, and short daily practice builds speed."),
      ("Is this an official DAT plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to the American Dental Association."),
    ],
    "note": "DAT is a program of the American Dental Association. FocusFlow Lab isn’t affiliated with or endorsed by the ADA.",
    "tag": "Dentistry",
  },
  {
    "slug": "gmat",
    "short": "GMAT",
    "title": "GMAT Study Plan Generator: Free Weekly GMAT Focus Schedule",
    "desc": "Put in your GMAT test date and study hours. Get a week-by-week plan across Quantitative Reasoning, Verbal Reasoning and Data Insights, with practice exams built in.",
    "og_title": "GMAT study plan generator",
    "h1": "Your GMAT study plan, week by week.",
    "lead": "Put in your test date and the hours you have. You get a plan across all three GMAT sections, with practice exams in the second half.",
    "date_label": "Test date", "legend": "Which sections feel shaky? (optional)", "button": "Build my plan",
    "days_default": 5, "hours_default": 2,
    "config": {"id": "gmat", "shortName": "GMAT", "maxDays": 180, "reviewShare": 0.5, "recommendedHours": {"min": 80, "max": 150}},
    "topics": [("Quantitative Reasoning", 34), ("Verbal Reasoning", 33), ("Data Insights", 33)],
    "tasks": """{
        review: (days) => [
          'Work through this week’s question types, one or two a study day.',
          `Do untimed practice on each type the same day, about ${days * 15} questions this week.`,
          'Keep an error log: the question type, why you missed it, and the fix.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one full timed practice exam.' : 'Do timed sets on your weakest section.',
          `Do mixed timed sets, about ${days * 20} questions this week.`,
          'Review every miss and every slow question.',
          'Re-read your error log at the start of each session.'
        ],
        final: () => [
          'Light review only: your error log.',
          'Check your appointment, ID, or online test setup.',
          'No new material in the last two days.',
          'Rest the day before and sleep early.'
        ]
      }""",
    "how": """<p>The GMAT Focus Edition has three equally scored sections: Quantitative Reasoning, Verbal Reasoning and Data Insights. Time is split evenly across them, with extra for any section you mark as shaky.</p>
          <ol>
            <li><strong>Question types first, about half.</strong> Learn each type, then practise it untimed the same day.</li>
            <li><strong>Timed practice, the rest.</strong> A full practice exam every other week and timed sets on your weakest section.</li>
            <li><strong>Final week.</strong> Light review, nothing new, and rest before test day.</li>
          </ol>
          <p>Any section you tick as shaky gets 50% more time.</p>
          <p>Check the current test details at <a href="https://www.mba.com/exams/gmat-exam" rel="noopener">mba.com</a> before you rely on it.</p>""",
    "faq": [
      ("How many hours should I study for the GMAT?", "Many test takers plan around 80 to 150 hours over 2 to 3 months. Your starting score and target decide where you land in that range."),
      ("Should I take practice exams early?", "Take one at the start to see where you are, then about one every two weeks once you’ve covered the question types."),
      ("Is this an official GMAT plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to GMAC."),
    ],
    "note": "GMAT is a registered trademark of the Graduate Management Admission Council (GMAC). FocusFlow Lab isn’t affiliated with or endorsed by GMAC.",
    "tag": "Business school",
  },
  {
    "slug": "cpa-aud",
    "short": "CPA AUD",
    "title": "CPA AUD Study Plan Generator: Free Weekly Schedule",
    "desc": "Put in your CPA AUD exam date and study hours. Get a week-by-week plan across the four AUD content areas, with practice questions and simulations built in.",
    "og_title": "CPA AUD study plan generator",
    "h1": "Your CPA AUD study plan, week by week.",
    "lead": "Put in your exam date and the hours you have. You get a plan across the AUD areas, with simulations in the second half.",
    "date_label": "Exam date", "legend": "Which areas feel shaky? (optional)", "button": "Build my plan",
    "days_default": 5, "hours_default": 2.5,
    "config": {"id": "cpa-aud", "shortName": "AUD", "maxDays": 270, "reviewShare": 0.55, "recommendedHours": {"min": 90, "max": 150}},
    "topics": [("Performing further procedures and obtaining evidence", 35), ("Assessing risk and developing a planned response", 30), ("Ethics, professional responsibilities and general principles", 20), ("Forming conclusions and reporting", 15)],
    "tasks": """{
        review: (days) => [
          'Work through this week’s topics, one or two a study day.',
          `Do multiple-choice questions on each topic the same day, about ${days * 30} this week.`,
          'Keep an error log: the standard or step you missed, and why.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one timed practice exam, multiple choice and simulations.' : 'Do timed simulations on your weakest area.',
          `Do mixed multiple-choice sets, about ${days * 40} questions this week.`,
          'Review every miss and re-work the simulation steps.',
          'Re-read your error log at the start of each session.'
        ],
        final: () => [
          'Light review only: your error log and report wording.',
          'Confirm your Notice to Schedule, appointment and ID.',
          'No new topics in the last two days.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>AUD (Auditing and Attestation) is one of the three core CPA sections. It tests the audit process from planning to the report, plus ethics and independence, with multiple-choice questions and task-based simulations.</p>
          <ol>
            <li><strong>Content review, a bit over half.</strong> One or two topics a day, each ending with multiple-choice questions.</li>
            <li><strong>Practice, the rest.</strong> Timed practice exams every other week, simulations on your weak areas, and mixed question sets.</li>
            <li><strong>Final week.</strong> Light review, nothing new, and a day off before the exam.</li>
          </ol>
          <p>Area hours follow the rough midpoints of the four AUD content areas in the AICPA blueprint. These shares are rough, not official. Any area you tick as shaky gets 50% more time.</p>
          <p>Check the current blueprint at <a href="https://www.aicpa-cima.com/" rel="noopener">aicpa-cima.com</a> before you rely on it.</p>""",
    "faq": [
      ("How many hours should I study for AUD?", "Many candidates plan around 90 to 150 hours for AUD, spread over 6 to 10 weeks while working."),
      ("Is AUD easier than FAR?", "Most candidates find AUD has less material than FAR, but it’s more about judgement and wording, so practise reading questions carefully."),
      ("Is this an official CPA plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to the AICPA, NASBA or any state board."),
    ],
    "note": "CPA is a designation granted by state boards of accountancy. The Uniform CPA Examination is developed by the AICPA. FocusFlow Lab isn’t affiliated with or endorsed by the AICPA, NASBA or any board of accountancy.",
    "tag": "Accounting",
  },
  {
    "slug": "cpa-reg",
    "short": "CPA REG",
    "title": "CPA REG Study Plan Generator: Free Weekly Schedule",
    "desc": "Put in your CPA REG exam date and study hours. Get a week-by-week plan across tax, business law and ethics, with practice questions and simulations built in.",
    "og_title": "CPA REG study plan generator",
    "h1": "Your CPA REG study plan, week by week.",
    "lead": "Put in your exam date and the hours you have. You get a plan across the REG areas, with the tax areas getting the most time.",
    "date_label": "Exam date", "legend": "Which areas feel shaky? (optional)", "button": "Build my plan",
    "days_default": 5, "hours_default": 2.5,
    "config": {"id": "cpa-reg", "shortName": "REG", "maxDays": 270, "reviewShare": 0.55, "recommendedHours": {"min": 90, "max": 150}},
    "topics": [("Federal taxation of entities", 28), ("Federal taxation of individuals", 27), ("Business law", 20), ("Ethics, professional responsibilities and federal tax procedures", 15), ("Federal taxation of property transactions", 10)],
    "tasks": """{
        review: (days) => [
          'Work through this week’s topics, one or two a study day.',
          `Do multiple-choice questions on each topic the same day, about ${days * 30} this week.`,
          'Keep an error log: the rule or number you missed, and why.'
        ],
        practice: (days, weekIndex) => [
          weekIndex % 2 === 0 ? 'Take one timed practice exam, multiple choice and simulations.' : 'Do timed tax simulations on your weakest area.',
          `Do mixed multiple-choice sets, about ${days * 40} questions this week.`,
          'Review every miss and re-work the simulation steps.',
          'Re-read your error log at the start of each session.'
        ],
        final: () => [
          'Light review only: your error log and key tax limits.',
          'Confirm your Notice to Schedule, appointment and ID.',
          'No new topics in the last two days.',
          'Take the day before off. Rest, eat well, sleep early.'
        ]
      }""",
    "how": """<p>REG (Taxation and Regulation) is one of the three core CPA sections. Most of it is federal taxation of individuals and entities, with business law and ethics making up the rest.</p>
          <ol>
            <li><strong>Content review, a bit over half.</strong> One or two topics a day, each ending with multiple-choice questions.</li>
            <li><strong>Practice, the rest.</strong> Timed practice exams every other week, tax simulations on your weak areas, and mixed question sets.</li>
            <li><strong>Final week.</strong> Light review, nothing new, and a day off before the exam.</li>
          </ol>
          <p>Area hours follow the rough midpoints of the five REG content areas in the AICPA blueprint. These shares are rough, not official. Any area you tick as shaky gets 50% more time.</p>
          <p>Check the current blueprint at <a href="https://www.aicpa-cima.com/" rel="noopener">aicpa-cima.com</a> before you rely on it.</p>""",
    "faq": [
      ("How many hours should I study for REG?", "Many candidates plan around 90 to 150 hours for REG, spread over 6 to 10 weeks while working."),
      ("Should I memorise tax numbers for REG?", "Learn the rules and how to apply them first. Keep a short list of the limits and thresholds that come up most and review it in the final week."),
      ("Is this an official CPA plan?", "No. It’s a free planning tool from FocusFlow Lab, and it isn’t connected to the AICPA, NASBA or any state board."),
    ],
    "note": "CPA is a designation granted by state boards of accountancy. The Uniform CPA Examination is developed by the AICPA. FocusFlow Lab isn’t affiliated with or endorsed by the AICPA, NASBA or any board of accountancy.",
    "tag": "Accounting",
  },
]

GUIDE_LINK = {
  "nclex": '''
          <p>More detail: <a href="/guides/how-to-study-for-the-nclex/">how to study for the NCLEX</a>, with a 6-week plan.</p>''',
  "mcat": '''
          <p>More detail: <a href="/guides/mcat-study-schedule-3-months/">a 3-month MCAT study schedule</a>, week by week.</p>''',
  "teas": '''
          <p>More detail: <a href="/guides/how-to-study-for-the-teas/">how to study for the TEAS</a>, section by section.</p>''',
}

STICK = """<p>A plan that survives week two beats a perfect one that doesn’t.</p>
          <ul>
            <li>Study at the same time each day. Your phone goes in another room for that block.</li>
            <li>Keep a log of every miss and why. Re-read it before each study day.</li>
            <li>When you miss a day, don’t double up. Carry on from where the plan says you are.</li>
          </ul>"""

def page(e):
    url = f"https://thefocusflowlab.com/study-plan/{e['slug']}/"
    cfg = dict(e["config"])
    cfg_js = json.dumps(cfg)[:-1] + ",\n      topics: " + json.dumps([{"name": n, "weight": w} for n, w in e["topics"]]) + ",\n      tasks: " + e["tasks"] + "\n    }"
    ld = {"@context": "https://schema.org", "@graph": [
      {"@type": "WebApplication", "name": e["og_title"][0].upper() + e["og_title"][1:], "url": url, "applicationCategory": "EducationalApplication",
       "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
       "publisher": {"@type": "Organization", "@id": "https://thefocusflowlab.com/#org", "name": "FocusFlow Lab", "url": "https://thefocusflowlab.com/"}, "dateModified": TODAY},
      {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "FocusFlow Lab", "item": "https://thefocusflowlab.com/"},
        {"@type": "ListItem", "position": 2, "name": "Study plans", "item": "https://thefocusflowlab.com/study-plan/"},
        {"@type": "ListItem", "position": 3, "name": e["short"], "item": url}]},
      {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in e["faq"]]}]}
    days_opts = "".join(f"<option{' selected' if d == e['days_default'] else ''}>{d}</option>" for d in range(3, 8))
    faq_html = "\n".join(f"          <details><summary>{html.escape(q, False)}</summary>\n            <p>{html.escape(a, False)}</p></details>" for q, a in e["faq"])
    faq_html += "\n          <details><summary>Can I save the plan?</summary>\n            <p>Use “Print or save as PDF” and choose Save as PDF. Your answers also stay in this browser for next time.</p></details>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e['title']}</title>
  <meta name="description" content="{e['desc']}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="FocusFlow Lab">
  <meta property="og:title" content="{e['og_title']}">
  <meta property="og:description" content="{e['desc']}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://thefocusflowlab.com/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/icon-64.png" type="image/png">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/bricolage-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/plex-sans.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../../assets/site.css">
  <link rel="stylesheet" href="../assets/plan.css">
  <script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
  </script>
</head>
<body>
<!-- site-head --><!-- /site-head -->
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/study-plan/">Study plans</a> / {e['short']}</nav>

    <main id="main">
      <section class="hero">
        <div>
          <h1>{e['h1']}</h1>
          <p class="lead">{e['lead']}</p>
          <p class="hero-note">Free, no sign-up. Your answers stay in this browser.</p>
        </div>

        <form id="plan-form" class="sheet" novalidate aria-label="Plan sheet">
          <p class="sheet-title">Plan sheet</p>
          <div class="fields">
            <div>
              <label for="examDate">{e['date_label']}</label>
              <input type="date" id="examDate" name="examDate" required>
            </div>
            <div>
              <label for="hoursPerDay">Hours a day</label>
              <input type="number" id="hoursPerDay" name="hoursPerDay" min="0.5" max="14" step="0.5" value="{e['hours_default']}" inputmode="decimal">
            </div>
            <div>
              <label for="daysPerWeek">Days a week</label>
              <select id="daysPerWeek" name="daysPerWeek">
                {days_opts}
              </select>
            </div>
          </div>
          <fieldset>
            <legend>{e['legend']}</legend>
            <div class="topics" id="weak-areas"></div>
          </fieldset>
          <div class="sheet-actions"><button class="btn" type="submit">{e['button']}</button></div>
          <p class="error" id="form-error" role="alert"></p>
        </form>
      </section>

      <section id="plan" class="plan" aria-live="polite"></section>

      <section class="reading">
        <h2>How the plan is put together</h2>
        <div class="prose">
          {e['how']}{GUIDE_LINK.get(e['slug'], '')}
        </div>
      </section>

      <section class="reading">
        <h2>What makes a plan stick</h2>
        <div class="prose">
          {STICK}
        </div>
      </section>

      <section class="reading faq">
        <h2>Questions people ask</h2>
        <div class="prose">
{faq_html}
        </div>
      </section>

      <aside class="kit" aria-label="Free Study Focus Kit">
        <div>
          <h2>Staying focused is the hard part.</h2>
          <p>The free Study Focus Kit has 5 printable worksheets for phone distractions, notes that stick and long study days, plus a free printable study planner.</p>
        </div>
        <a class="btn" href="/#free-kit">Get the free kit</a>
      </aside>
    </main>
    <aside class="page-note" aria-label="About this page">
      <p>Made by FocusFlow Lab. Last reviewed October 2026. Questions or corrections: <a href="mailto:hello@thefocusflowlab.com">hello@thefocusflowlab.com</a></p>
      <p>{e['note']}</p>
    </aside>
  </div>

<!-- site-foot --><!-- /site-foot -->
  <script>
    window.EXAM_CONFIG = {cfg_js};
  </script>
  <script src="../assets/plan.js" defer></script>
</body>
</html>
"""

for e in EXAMS:
    out = ROOT / "study-plan" / e["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(e), encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT).as_posix())
