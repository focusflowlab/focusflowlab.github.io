"""Run after changing _tools/prices.py: compares every surface it can reach with the source of truth,
then prints the manual steps for what it cannot change itself.

    python _tools/price_sync.py

Reads Gumroad with the FocusFlow CLI login (APPDATA=$TEMP/gr-ff-appdata, never the default login).
Changes nothing anywhere: it only reads and reports. Exit code 1 if anything it can check is wrong.
"""
import json, os, pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import prices, price_check
from prices import money

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANDING = pathlib.Path(r"F:\Personal Projects\focusflowlab-products\gumroad-landing")
BUNDLE_SLUG = price_check.BUNDLE_SLUG
bad = 0


def say(ok, text):
    global bad
    bad += not ok
    print(("  ok   " if ok else "  FIX  ") + text)


print(f"Source of truth (_tools/prices.py): planner {money(prices.PLANNER)}, bundle {money(prices.BUNDLE)} {prices.CURRENCY}\n")

print("1. Site, JSON-LD, llms.txt, pins, feeds (price_check.py)")
probs = price_check.check(ROOT)
for p in probs:
    say(False, p)
if not probs:
    say(True, "every page, JSON-LD offer, llms.txt line, pin and feed row matches")

print("\n2. Gumroad product prices (read only)")
gr = os.path.expanduser("~/.local/bin/gumroad.exe")
env = dict(os.environ, APPDATA=os.path.join(os.environ.get("TEMP", ""), "gr-ff-appdata"))
try:
    who = subprocess.run([gr, "auth", "status"], capture_output=True, text=True, env=env).stdout
    if "hello@thefocusflowlab.com" not in who:
        raise RuntimeError("not logged in as hello@thefocusflowlab.com (wrong store or no login)")
    out = subprocess.run([gr, "products", "list", "--all", "--json", "--no-input", "--non-interactive", "--jq",
                          "[.products[] | {p: .custom_permalink, price, cur: .currency, pub: .published}]"],
                         capture_output=True, text=True, env=env, check=True).stdout
    for prod in json.loads(out):
        if not prod["pub"]:
            continue
        want = (prices.BUNDLE if prod["p"] == BUNDLE_SLUG else prices.PLANNER) * 100
        ok = prod["price"] == want and prod["cur"].upper() == prices.CURRENCY
        say(ok, f"{prod['p']}: Gumroad {money(prod['price'] / 100)}" + ("" if ok else f", should be {money(want / 100)}: edit it in Gumroad > Products"))
except Exception as e:  # never guess: report and let the owner check by hand
    say(False, f"could not read Gumroad ({e}); check every product price by hand")

print("\n3. Gumroad landing pages (local builds in focusflowlab-products/gumroad-landing/out)")
allowed = {money(prices.PLANNER), money(prices.BUNDLE), money(prices.SEPARATE)}
pages = list((LANDING / "out").glob("*.html")) if (LANDING / "out").exists() else []
for f in pages:
    wrong = sorted(set(price_check.MONEY.findall(f.read_text(encoding="utf-8"))) - allowed)
    if wrong:
        say(False, f"{f.name} shows {wrong}: fix the template/build.py there, rebuild, publish_all.py")
if pages and not bad:
    say(True, f"{len(pages)} local landing pages show only current prices (they mostly link to the site)")
if not pages:
    say(False, "no local landing pages found; check the live Gumroad pages by hand")

print(f"""
4. Manual steps (cannot be changed from here). Do them in this order after a real price change:
  [ ] Gumroad: edit each product price (Products > Edit > Price). Re-run this script until step 2 is all ok.
  [ ] Gumroad landing pages: python build.py and publish_all.py in {LANDING}, then click Buy on one page.
  [ ] Site: python _tools/build.py (must print PAGE GUARD: OK and PRICE CHECK: OK), commit, push,
      python _tools/indexnow.py. Hand-built pages and llms.txt are listed above by price_check if stale.
  [ ] MailerLite: welcome automation emails (active email 203036797906716343) and any draft campaigns:
      search the text for the old prices; pause the workflow to edit.
  [ ] Pinterest catalog: feeds/pinterest-catalog.csv refreshes from the hosted URL; trigger a manual
      refresh in Pinterest Business > Catalogs to see it sooner.
  [ ] Business Hub product feed: feeds/openai-feed.csv (hosted URL refreshes itself; if it is still a
      one-time CSV upload, upload the new file).
  [ ] Pins already published: re-render (python _tools/pins.py, then pin-shots) and replace pins that show
      a price (planner and bundle pins); old pin images keep the old price until replaced.
  [ ] YouTube, Medium, Quora, Product Hunt and other posts that state a price: search and edit.
""")
print("RESULT:", "all checkable surfaces match" if not bad else f"{bad} item(s) to fix above")
sys.exit(1 if bad else 0)
