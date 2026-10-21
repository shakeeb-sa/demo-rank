from patchright.sync_api import sync_playwright
import time, requests

KW = "fee only financial advisor Chicago"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context("./chrome-profile", headless=False, no_viewport=True)
    page = ctx.pages[0]
    page.goto("https://www.google.com", wait_until="domcontentloaded")
    box = page.locator("textarea[name=q], input[name=q]").first
    box.click(); box.fill(KW); box.press("Enter")
    page.wait_for_selector("#rso", timeout=15000)
    time.sleep(3)
    page.keyboard.press("Alt+Shift+A")
    time.sleep(5)
    last = 0
    for _ in range(40):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)
        h = page.evaluate("document.body.scrollHeight")
        if h == last:
            time.sleep(3)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            if page.evaluate("document.body.scrollHeight") == h:
                break
        last = h
    links = page.eval_on_selector_all("#rso a:has(h3)", "els => els.map(a => a.href)")
    print("TOTAL LINKS:", len(links))
    seen = set()
    for i, link in enumerate(links, 1):
        token = link.split("url=")[-1][:40]
        if token in seen: continue
        seen.add(token)
        try:
            r = requests.get(link, allow_redirects=False, timeout=10)
            loc = r.headers.get("Location", link)
        except Exception as e:
            loc = f"ERR: {e}"
        print(f"{i:3d}. {loc}")
    input("Press Enter to close...")
    ctx.close()