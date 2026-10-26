# Design: FocusFlow Lab

The locked system. Every page reads this first and shares it. Change it on purpose; the file is the rule.

## System
- Genre: playful (soft and bright)
- Direction: soft and bright study desk. Light paper, flat mint and teal washes, white cards that float on soft shadows, pill controls, navy ink, one teal accent, mono numerals for dates, hours and prices.
- Shapes: Split Studio (`/`), Long Document (`/privacy.html`, `/terms.html`), tool page with the plan sheet beside the headline (`/study-plan/*`)
- Theme: brand (FocusFlow teal #2a9d8f / #3cc2b2, navy ink)
- Axes: light/grotesk-sans/chromatic-teal · posture: split

## Files
- `assets/site.css`, one file: self-hosted fonts (`assets/fonts/`), then the tokens block (every colour, face, space and type step, light and dark: the source of truth), then the floor rules, then chrome, controls, home and legal layouts. Every page links it.
- `study-plan/assets/plan.css`: the generator form and timetable only. Loads after `site.css`.

## Tokens (roles)
```css
--color-paper / --color-paper-2 (sheets) / --color-paper-3
--color-ink (navy) / --color-ink-2 / --color-muted
--color-rule / --color-rule-strong
--color-accent (teal) / --color-accent-ink (links, hovers) / --color-accent-wash / --color-on-accent / --color-focus
--color-phase-review / -practice / -final (plan timetable only)
--font-display: Bricolage Grotesque 700 · --font-body: IBM Plex Sans 400/600 · --font-mono: IBM Plex Mono 500 (numbers only)
--radius-card: 20px · --radius-control: 14px · pills for buttons and nav · --shadow-card / --shadow-lift · flat washes (--color-wash-mint, -teal, -sun), never gradients · --container: 1120px
```

## Building pages
- Header and footer live in `_partials/`. After any change run `python _tools/build.py` (it copies them into every page with `<!-- site-head -->` / `<!-- site-foot -->` markers).
- Exam planners: edit `_tools/exams.py`, then `python _tools/exams.py`. Tools: `_tools/tools.py`. Guides: `_tools/guides.py`. Run each from `_tools/`, then run `build.py`.
- Folders starting with `_` are not published by GitHub Pages.

## Components
- Masthead: sticky frosted bar on desktop; wordmark left; pill links (Study plans, Tools, Guides, Free kit) and a teal pill for the Sprint planner.
- Sheet: `paper-2`, hairline all round, 4px teal head rule, a sheet title with a hairline under it.
- Ruled list: hairline rows, mono `01` numerals in teal ink.
- Rows: link index set as timetable rows (name, note, action).
- Panels: big rounded sections in a flat wash (`.panel-mint`, `.panel-teal`). Cards (`.cards`) for exams, tools and guides lift on hover.
- Footer: soft panel with link columns and every exam trademark notice. Exam pages also keep their own notice in `.page-note`.

## Controls
- Primary: teal fill, 6px radius, 48px tall, one per screen.
- Secondary: quiet outline (`.btn-quiet`) or a bold text link.

## Motion
- Calm. One fade-up reveal for sections below the fold (`data-reveal`, `assets/site.js`), card lift on hover. Content is visible without scripting; reduced motion turns it all off.

## Copy
- Plain, human, second person. No dashes in copy, no dot-joined meta, no labels in capitals.
- Never invent numbers, testimonials, reviews or logos. Exam trademark disclaimers stay on every exam page.
