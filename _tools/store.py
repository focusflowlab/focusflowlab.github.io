"""Turn the planner buy buttons on or off.

  python _tools/store.py closed   # buttons say "Opening soon", point to the free kit form
  python _tools/store.py open     # buttons go to the Lemon Squeezy checkout

Each buy button carries its checkout link in data-checkout, so nothing is lost
while the store is closed. Product data for Google switches between
PreOrder and InStock to match.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "study-plan/nclex/index.html", "study-plan/mcat/index.html"]
OPEN_TEXT = "Get the planner"
CLOSED_TEXT = "Opening soon: get notified"

state = sys.argv[1] if len(sys.argv) > 1 else ""
if state not in ("open", "closed"):
    sys.exit(__doc__)

BTN = re.compile(r'<a class="btn( btn-soft)?"([^>]*?) href="([^"]+)"([^>]*?)>(Get the planner|Opening soon: get notified)</a>')

for rel in PAGES:
    f = ROOT / rel
    s = f.read_text(encoding="utf-8")

    def swap(m):
        attrs = m.group(2) + m.group(4)
        href = m.group(3)
        checkout = re.search(r'data-checkout="([^"]+)"', attrs)
        url = checkout.group(1) if checkout else href
        attrs = re.sub(r'\s*data-checkout="[^"]+"', "", attrs)
        if state == "open":
            return f'<a class="btn"{attrs} href="{url}" data-checkout="{url}">{OPEN_TEXT}</a>'
        kit = "#free-kit" if rel == "index.html" else "/#free-kit"
        return f'<a class="btn btn-soft"{attrs} href="{kit}" data-checkout="{url}">{CLOSED_TEXT}</a>'

    s, n = BTN.subn(swap, s)
    old, new = ("https://schema.org/InStock", "https://schema.org/PreOrder") if state == "closed" else ("https://schema.org/PreOrder", "https://schema.org/InStock")
    s = s.replace(old, new)
    f.write_text(s, encoding="utf-8", newline="\n")
    print(f"{rel}: {n} button(s) {state}")
