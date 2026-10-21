from patchright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir="./chrome-profile",
        headless=False,
        no_viewport=True
    )
    page = ctx.pages[0]
    page.goto("https://chromewebstore.google.com/detail/dbkkfpfndpelicmjdpfacabhjffgoacl", wait_until="domcontentloaded")
    input("Install the extension in the window, then press Enter here to close...")
    ctx.close()