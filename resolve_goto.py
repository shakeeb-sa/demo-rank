import requests

goto_links = [
    "PASTE_YOUR_99_LINKS_HERE"
]

seen = set()
for link in goto_links:
    token = link.split("url=")[-1][:40]
    if token in seen:
        continue
    seen.add(token)
    try:
        r = requests.get(link, allow_redirects=False, timeout=10)
        loc = r.headers.get("Location", "NO_LOCATION")
        print(loc)
    except Exception as e:
        print("ERROR:", e)