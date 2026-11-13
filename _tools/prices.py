"""Single source of truth for planner prices. Change prices HERE only, then run python _tools/price_sync.py.

Copy in generators and _partials uses tokens like [[P]]; fill() turns them into the real amounts.
price_check.py fails the build if any page, JSON-LD, llms.txt, pin or feed shows another amount.
"""
PLANNER = 5          # one planner, USD
BUNDLE = 15          # all exam planners in one purchase, USD
BUNDLE_COUNT = 14    # planners in the bundle
CURRENCY = "USD"

SEPARATE = PLANNER * BUNDLE_COUNT   # the bundle's planners bought one by one


def money(n):
    return f"${n:g}" if n == int(n) else f"${n:.2f}"


def decimal(n):
    return f"{n:.2f}"


_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
# "Three single planners cost $15, the same as the bundle": only true when the bundle is a whole number of planners.
PARITY = BUNDLE / PLANNER
PARITY_OK = PARITY == int(PARITY) and int(PARITY) in _WORDS

TOKENS = {
    "[[P]]": money(PLANNER),
    "[[B]]": money(BUNDLE),
    "[[ALL]]": money(SEPARATE),
    "[[PN]]": decimal(PLANNER),
    "[[BN]]": decimal(BUNDLE),
    "[[CUR]]": CURRENCY,
    "[[PARITY]]": _WORDS[int(PARITY)] if PARITY_OK else "[[PARITY-COPY-NEEDS-REWRITE]]",
    "[[NEXT]]": {2: "third", 3: "fourth", 4: "fifth", 5: "sixth", 6: "seventh"}[int(PARITY)] if PARITY_OK else "[[PARITY-COPY-NEEDS-REWRITE]]",
}
TOKENS["[[Parity]]"] = TOKENS["[[PARITY]]"].capitalize() if PARITY_OK else TOKENS["[[PARITY]]"]


def fill(text):
    for k, v in TOKENS.items():
        text = text.replace(k, v)
    return text
