import csv, random, time
from urllib.parse import urlparse
from patchright.sync_api import sync_playwright

DOMAIN = "virtueam.com"

def is_own(url):
    try:
        host = urlparse(url).netloc.lower().removeprefix("www.")
        return host == DOMAIN or host.endswith("." + DOMAIN)
    except Exception:
        return False

def check(page, kw):
    q = kw.replace(" ", "+")
    page.goto(f"https://www.google.com/search?q={q}&num=10&hl=en&gl=us",
              wait_until="domcontentloaded", timeout=30000)
    if "/sorry/" in page.url:
        return "BLOCKED", None
    try:
        page.wait_for_selector("#rso", timeout=8000)
    except Exception:
        return "NO_RESULTS", None
    links = page.eval_on_selector_all(
        "#rso h3",
        "els => els.map(h => { const a = h.closest('a'); return a ? a.href : null; })"
    )
    links = [l for l in links if l]
    for i, link in enumerate(links, 1):
        if is_own(link):
            return i, link
    return "NOT_IN_TOP_10", None

def main():
    with open("keywords.csv", newline="", encoding="utf-8") as f:
        kws = [r[0].strip() for r in csv.reader(f) if r and r[0].strip()]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/130.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = ctx.new_page()
        for i, kw in enumerate(kws, 1):
            print(f"[{i}/{len(kws)}] {kw}")
            try:
                pos, url = check(page, kw)
                print(f"   -> position: {pos}   url: {url}")
            except Exception as e:
                print(f"   -> ERROR: {e}")
            time.sleep(random.uniform(3, 6))
        browser.close()

if __name__ == "__main__":
    main()