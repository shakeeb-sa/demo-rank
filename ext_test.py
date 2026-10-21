from patchright.sync_api import sync_playwright
import time, requests

KW = "fee only financial advisor Chicago"
DOMAIN = "virtueam"

def resolve(link):
    try:
        r = requests.get(link, allow_redirects=False, timeout=8)
        return r.headers.get("Location", link)
    except Exception as e:
        return f"ERR:{e}"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context("./chrome-profile", headless=False, no_viewport=True)
    page = ctx.pages[0]
    page.goto("https://www.google.com", wait_until="domcontentloaded")
    box = page.locator("textarea[name=q], input[name=q]").first
    box.click(); box.fill(KW); box.press("Enter")
    page.wait_for_selector("#rso", timeout=15000)
    time.sleep(2)
    page.keyboard.press("Alt+Shift+A")
    time.sleep(3)
    last = 0
    for _ in range(25):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        h = page.evaluate("document.body.scrollHeight")
        if h == last:
            time.sleep(2)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            if page.evaluate("document.body.scrollHeight") == h:
                break
        last = h
    results = page.eval_on_selector_all("#rso a:has(h3)", """
        els => els.map(a => ({
            href: a.href,
            cite: a.querySelector('cite') ? a.querySelector('cite').innerText : ''
        }))
    """)
    matches = []
    for i, r in enumerate(results, 1):
        if DOMAIN in r['cite'].lower():
            matches.append((i, resolve(r['href'])))
    print(f"KEYWORD: {KW}")
    print(f"SCANNED: {len(results)} results")
    if matches:
        for pos, url in matches:
            print(f"  RANK #{pos}: {url}")
    else:
        print(f"  {DOMAIN}.com NOT FOUND (0 HTTP resolves used)")
    input("Press Enter to close...")
    ctx.close()