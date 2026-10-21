from patchright.sync_api import sync_playwright
import time, random

DOMAIN = "virtueam.com"
KEYWORD = "fee only financial advisor Chicago"
seen_tokens = set()

def is_own(u):
    return DOMAIN in u.lower()

def resolve(ctx, href):
    if "google.com/goto?url=" not in href:
        return href
    token = href.split("url=")[1][:40]
    if token in seen_tokens:
        return None
    seen_tokens.add(token)
    try:
        r = ctx.request.get(href, max_redirects=0, timeout=15000)
        return r.headers.get("location", href)
    except Exception:
        return href

with sync_playwright() as p:
    b = p.chromium.launch(headless=False)
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/130.0.0.0 Safari/537.36",
        locale="en-US", viewport={"width": 1366, "height": 900}
    )
    page = ctx.new_page()
    global_pos = 0
    found = False
    start = 0
    while True:
        url = f"https://www.google.com/search?q={KEYWORD.replace(' ', '+')}&start={start}&hl=en&gl=us"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if "/sorry/" in page.url:
            print("CAPTCHA — solve it in the window, then wait…")
            page.wait_for_url("**/search**", timeout=180000)
        try:
            page.wait_for_selector("#rso", timeout=8000)
        except Exception:
            print(f"No results container on start={start}; stopping.")
            break
        links = page.eval_on_selector_all(
            "#rso a:has(h3)",
            "els => els.map(a => a.href)"
        )
        if not links:
            print(f"No organic results on start={start}; stopping.")
            break
        print(f"\n--- Page start={start} ({len(links)} links) ---")
        for href in links:
            global_pos += 1
            real = resolve(ctx, href)
            if real is None:
                continue
            marker = "  <-- VIRTUEAM" if is_own(real) else ""
            print(f"{global_pos:3d}. {real}{marker}")
            if is_own(real):
                found = True
        start += 10
        time.sleep(random.uniform(2, 5))
    print("\n=== SUMMARY ===")
    print(f"Keyword: {KEYWORD}")
    print(f"Total results scanned: {global_pos}")
    print(f"virtueam.com found: {found}")
    b.close()