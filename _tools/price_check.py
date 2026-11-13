"""Fail when any price anywhere differs from _tools/prices.py.

Run: python _tools/price_check.py [root]   (build.py runs it last; exit code 1 on any problem)
Checks: generator sources hold no literal prices; every $amount on published pages, llms.txt, pins and
feeds is one of the current prices; every JSON-LD offer and feed row has the right price for its product.
"""
import pathlib, re, sys, csv, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import prices
from prices import money, decimal

BUNDLE_SLUG = "all-exam-planners-bundle"
MONEY = re.compile(r"\$\d+(?:,\d{3})*(?:\.\d\d)?")


def check(root):
    root = pathlib.Path(root)
    allowed = {money(prices.PLANNER), money(prices.BUNDLE), money(prices.SEPARATE)}
    offer = {decimal(prices.PLANNER), decimal(prices.BUNDLE), "0"}
    probs = []
    if not prices.PARITY_OK:
        probs.append("prices.py: bundle is not a whole number (2-6) of planners; rewrite the [[Parity]]/[[PARITY]]/[[NEXT]] copy in planner_extra.py and extra_pages.py")

    # 1. sources: tokens only
    for f in [*(root / "_tools").glob("*.py"), *(root / "_partials").glob("*.html")]:
        if f.name in ("prices.py", "price_check.py", "price_sync.py", "make_templates.py"):
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\$\d|\"price\":\s*\"[1-9]|\d\.\d\d USD", line):
                probs.append(f"{f.relative_to(root).as_posix()}:{n}: literal price in a source, use a [[token]] from prices.py")

    # 2. published text
    files = [p for p in root.rglob("*.html") if not any(x.startswith(".") or x in ("_tools", "_partials", "_research", "_includes", "_layouts") for x in p.relative_to(root).parts)]
    files += [root / "llms.txt", *(root / "feeds").glob("*.csv"), *(root / "_pins").glob("*.json")]
    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(root).as_posix()
        if "[[" in text and "]]" in text and re.search(r"\[\[[A-Za-z-]+\]\]", text):
            probs.append(f"{rel}: unfilled price token {re.search(r'\[\[[A-Za-z-]+\]\]', text).group(0)}")
        for m in sorted(set(MONEY.findall(text)) - allowed):
            line = text[:text.find(m)].count("\n") + 1
            probs.append(f"{rel}:{line}: shows {m}, current prices are {sorted(allowed)}")
        for m in re.finditer(r'"price":\s*"([^"]+)"', text):
            if m.group(1) not in offer:
                probs.append(f"{rel}: JSON-LD price {m.group(1)}, expected one of {sorted(offer)}")
        # a planner page's own Product offer must be its own price
        pm = re.match(r"planners/([^/]+)/index\.html$", rel)
        if pm:
            want = decimal(prices.BUNDLE if pm.group(1) == BUNDLE_SLUG else prices.PLANNER)
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
                for node in json.loads(block).get("@graph", [json.loads(block)]):
                    if node.get("@type") == "Product" and node.get("offers", {}).get("price") not in (want, None):
                        probs.append(f"{rel}: Product offer {node['offers']['price']}, expected {want}")
        if f.suffix == ".csv":
            rows = list(csv.DictReader(text.splitlines()))
            for r in rows:
                rid, pr = r.get("id") or r.get("item_id"), r.get("price")
                want = f"{decimal(prices.BUNDLE if rid == BUNDLE_SLUG else prices.PLANNER)} {prices.CURRENCY}"
                if pr != want:
                    probs.append(f"{rel}: {rid} price {pr!r}, expected {want!r}")
    return probs


if __name__ == "__main__":
    probs = check(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent)
    for p in probs:
        print("PRICE CHECK FAIL", p)
    print(f"PRICE CHECK: {len(probs)} problem(s)" if probs else f"PRICE CHECK: OK (planner {money(prices.PLANNER)}, bundle {money(prices.BUNDLE)})")
    sys.exit(1 if probs else 0)
