"""Tell Bing, Yandex and other IndexNow engines about every URL in sitemap.xml.
Run after a deploy is live:  python _tools/indexnow.py
"""
import json, pathlib, re, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = "049ab40397b046d44f5205f31df43ac6"
urls = re.findall(r"<loc>(.*?)</loc>", __import__("urllib.request").request.urlopen("https://thefocusflowlab.com/sitemap.xml").read().decode())
body = json.dumps({"host": "thefocusflowlab.com", "key": KEY, "keyLocation": f"https://thefocusflowlab.com/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req) as r:
    print(r.status, len(urls), "urls submitted")
