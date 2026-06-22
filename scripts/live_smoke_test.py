"""Live smoke test — validates RSS feed and chapter fetch against real akknovel.com.

Usage:
    python scripts/live_smoke_test.py [SERIES_URL]

Exit 0 if all checks pass, exit 1 with descriptive message otherwise.
"""
import os
import sys
import re

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

SERIES_URL = os.environ.get(
    "SERIES_URL",
    sys.argv[1] if len(sys.argv) > 1
    else "https://www.akknovel.com/series/after-rebirth-i-was-forced-to-become-the-mafia-princess",
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.akknovel.com/",
}


def check(label, condition, detail=""):
    status = "OK" if condition else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return condition


def main():
    all_pass = True
    slug = SERIES_URL.rstrip("/").split("/series/")[-1]
    rss_url = f"https://www.akknovel.com/series/{slug}/feed"

    print(f"=== A.R.C. Live Smoke Test ===")
    print(f"Series: {SERIES_URL}")
    print(f"RSS:    {rss_url}\n")

    # Step 1: RSS feed
    print("[1] RSS Feed")
    try:
        r = requests.get(rss_url, headers=HEADERS, timeout=15)
        all_pass &= check("HTTP 200", r.status_code == 200, f"got {r.status_code}")
        ct = r.headers.get("content-type", "")
        all_pass &= check("XML content-type", "xml" in ct, ct)
        all_pass &= check("Contains <item> elements", "<item>" in r.text)
        items = re.findall(r"<link>(.*?)</link>", r.text)
        chapter_urls = [u for u in items if "/chapter-" in u]
        all_pass &= check("Has chapter URLs", len(chapter_urls) > 0, f"found {len(chapter_urls)}")
    except Exception as e:
        all_pass = False
        check("RSS request", False, str(e))

    # Step 2: Fetch a chapter
    print("\n[2] Chapter Page")
    if chapter_urls:
        ch_url = chapter_urls[0]
        try:
            r = requests.get(ch_url, headers=HEADERS, timeout=15)
            all_pass &= check("HTTP 200", r.status_code == 200, f"got {r.status_code}")
            all_pass &= check("Has article#chapter-content", "chapter-content" in r.text)
            all_pass &= check("Has _pageData", "_pageData" in r.text)
            has_btn = "btn" in r.text and "grid-cols-2" in r.text
            all_pass &= check("Has nav buttons", has_btn)
        except Exception as e:
            all_pass = False
            check("Chapter request", False, str(e))
    else:
        all_pass = False
        check("Chapter URLs available", False, "no URLs from RSS")

    # Step 3: Cloudflare check
    print("\n[3] Cloudflare")
    if chapter_urls:
        try:
            r = requests.get(chapter_urls[0], headers=HEADERS, timeout=15)
            blocked = "Just a moment..." in r.text or "cf-browser-verification" in r.text
            all_pass &= check("NOT blocked by Cloudflare", not blocked)
        except Exception as e:
            all_pass = False
            check("Cloudflare check", False, str(e))

    print(f"\n=== {'ALL PASSED' if all_pass else 'SOME CHECKS FAILED'} ===")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
