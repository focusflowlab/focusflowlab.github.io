"""Free keyword research from Google and Bing search suggestions.

Usage: python _tools/keywords.py > _research/keywords.md
Suggestions show what people actually type, ranked by popularity. They have no
search volumes, so treat them as demand signals, not numbers.
"""
import json, sys, time, urllib.parse, urllib.request

SEEDS = [
    "how to study for finals", "finals week", "how to study for multiple exams", "cramming",
    "what do i need on my final", "final grade calculator", "gpa calculator", "weighted grade calculator",
    "study schedule", "study plan", "study timetable", "how many pages a day",
    "flashcards", "spaced repetition", "pomodoro", "study timer",
    "nclex study plan", "mcat study schedule", "usmle step 1 study schedule", "gre study plan", "lsat study schedule",
    "pance study plan", "naplex study plan", "bar exam study schedule", "cpa study plan", "ap exam study plan",
    "fe exam study plan", "how to stop procrastinating studying", "how to focus while studying",
    "active recall", "study planner printable", "exam planner",
]
MODIFIERS = ["", " how", " for", " printable", " free", " in a week", " best"]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", "replace")

def google(q):
    try:
        return json.loads(get("https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q=" + urllib.parse.quote(q)))[1]
    except Exception:
        return []

def bing(q):
    try:
        d = json.loads(get("https://api.bing.com/osjson.aspx?query=" + urllib.parse.quote(q)))
        return d[1]
    except Exception:
        return []

print("# Keyword research: search suggestions (US English)\n")
print("Collected from Google and Bing autocomplete. Order = how often people type it. No volumes.\n")
for seed in SEEDS:
    found = []
    for m in MODIFIERS:
        for s in google(seed + m) + bing(seed + m):
            s = s.strip().lower()
            if s and s not in found:
                found.append(s)
        time.sleep(0.15)
    print(f"## {seed}\n")
    print(", ".join(found[:30]) + "\n")
    sys.stdout.flush()
