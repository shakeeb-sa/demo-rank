from patchright.sync_api import sync_playwright
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context("./chrome-profile", headless=False, no_viewport=True)
    page = ctx.pages[0]
    page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=20000)
    print("OK:", page.title())
    ctx.close()