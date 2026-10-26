# Design: FocusFlow Lab

The locked system. Every page reads this first and shares it. Change it on purpose; the file is the rule.

## System
- Genre: editorial
- Direction: a printed study timetable. Cool ruled paper, navy ink, one teal accent, mono numerals for dates, hours and prices.
- Shapes: Split Studio (`/`), Long Document (`/privacy.html`, `/terms.html`), tool page with the plan sheet beside the headline (`/study-plan/*`)
- Theme: brand (FocusFlow teal #2a9d8f / #3cc2b2, navy ink)
- Axes: light/grotesk-sans/chromatic-teal · posture: split

## Files
- `assets/tokens.css`: every colour, face, space and type step (light and dark). The source of truth.
- `assets/base.css`: the floor rules (box sizing, overflow-x clip, focus ring, reduced motion).
- `assets/site.css`: stamp, chrome (masthead, colophon), controls, home and legal layouts. Every page links it.
- `study-plan/assets/plan.css`: the generator form and timetable only. Loads after `site.css`.

## Tokens (roles)
```css
--color-paper / --color-paper-2 (sheets) / --color-paper-3
--color-ink (navy) / --color-ink-2 / --color-muted
--color-rule / --color-rule-strong
--color-accent (teal) / --color-accent-ink (links, hovers) / --color-accent-wash / --color-on-accent / --color-focus
--color-phase-review / -practice / -final (plan timetable only)
--font-display: Bricolage Grotesque 700 · --font-body: IBM Plex Sans 400/600 · --font-mono: IBM Plex Mono 500 (numbers only)
--radius-card: 6px · hairline rules, no shadows · --container: 1120px
```

## Components
- Masthead: wordmark left, three links right (Study plans, Free focus kit, Sprint planner), hairline below.
- Sheet: `paper-2`, hairline all round, 4px teal head rule, a sheet title with a hairline under it.
- Ruled list: hairline rows, mono `01` numerals in teal ink.
- Rows: link index set as timetable rows (name, note, action).
- Bands: each home section opens on a 2px ink rule.
- Colophon: wordmark, contact, links. Trademark disclaimers live here on exam pages.

## Controls
- Primary: teal fill, 6px radius, 48px tall, one per screen.
- Secondary: quiet outline (`.btn-quiet`) or a bold text link.

## Motion
- Still. Colour changes on hover only; nothing animates in. Reduced motion ends everything at once.

## Copy
- Plain, human, second person. No dashes in copy, no dot-joined meta, no labels in capitals.
- Never invent numbers, testimonials, reviews or logos. Exam trademark disclaimers stay on every exam page.
