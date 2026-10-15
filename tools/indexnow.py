#!/usr/bin/env python3
"""Tell IndexNow engines (Bing, Yandex, Naver, Seznam and others) which all.exposed URLs changed.

    python tools/indexnow.py            # every URL in sitemap.xml
    python tools/indexnow.py --dry-run  # print what would be sent

The key is the 32-character hex file <key>.txt at the repo root, published at
https://all.exposed/<key>.txt. Run it after a deploy, never before: the engines
fetch the key file and the pages. Sends only URLs; no personal data.
"""
import json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "all.exposed"
ENDPOINT = "https://api.indexnow.org/indexnow"


def key():
    keys = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem) and p.read_text().strip() == p.stem]
    if len(keys) != 1:
        sys.exit(f"indexnow: expected one key file <32 hex>.txt at repo root, found {len(keys)}")
    return keys[0].stem


def sitemap_urls():
    path = ROOT / "sitemap.xml"
    if not path.exists():
        sys.exit("indexnow: sitemap.xml is missing")
    text = path.read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", text)


def main():
    dry_run = "--dry-run" in sys.argv
    k = key()
    urls = [u for u in sitemap_urls() if u.startswith(f"https://{HOST}/")]
    if not urls:
        print("indexnow: nothing to submit")
        return
    print(f"{'[dry run] Would submit' if dry_run else 'Submitting'} {len(urls)} URLs to IndexNow as {HOST}.")
    if dry_run:
        for u in urls:
            print(f"  {u}")
        return
    body = json.dumps({
        "host": HOST,
        "key": k,
        "keyLocation": f"https://{HOST}/{k}.txt",
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req) as resp:
        print(f"IndexNow: {resp.status} {resp.reason}")


if __name__ == "__main__":
    main()
