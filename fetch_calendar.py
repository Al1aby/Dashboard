#!/usr/bin/env python3
"""
fetch_radar.py — fetches latest CASBV radar GIF from MSC Datamart
"""

import requests, re, sys
from pathlib import Path

STATION = "CASBV"
OUTPUT  = Path(__file__).parent / "radar.gif"
HEADERS = {"User-Agent": "Mozilla/5.0 (dashboard-bot/1.0)"}

# Try both known URL patterns
INDEX_URLS = [
    f"https://dd.weather.gc.ca/today/radar/DPQPE/GIF/{STATION}/",
    f"https://dd.weather.gc.ca/radar/DPQPE/GIF/{STATION}/",
]

def main():
    html = None
    used_url = None

    for url in INDEX_URLS:
        print(f"Trying {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            print(f"  Status: {r.status_code}")
            if r.status_code == 200:
                html = r.text
                used_url = url
                break
        except Exception as e:
            print(f"  Error: {e}")

    if not html:
        print("ERROR: Could not reach any radar index URL", file=sys.stderr)
        sys.exit(1)

    # Print first 500 chars of HTML so we can see the actual filename format
    print("--- Directory listing snippet ---")
    print(html[:800])
    print("--- end snippet ---")

    # Match any .gif file in the listing
    filenames = re.findall(r'[\w\-]+\.gif', html)
    print(f"All GIFs found: {filenames[:10]}")

    # Filter to Rain (non-contingency) files
    rain_files = [f for f in filenames if 'Rain' in f and 'Contingency' not in f]
    print(f"Rain GIFs: {rain_files[:5]}")

    if not rain_files:
        # Fall back to any gif
        rain_files = [f for f in filenames if f.endswith('.gif')]

    if not rain_files:
        print("ERROR: No GIF files found", file=sys.stderr)
        sys.exit(1)

    latest = sorted(rain_files)[-1]
    img_url = used_url + latest
    print(f"Fetching {img_url}")

    img = requests.get(img_url, headers=HEADERS, timeout=15)
    img.raise_for_status()

    OUTPUT.write_bytes(img.content)
    print(f"Saved radar.gif ({len(img.content)} bytes)")

if __name__ == "__main__":
    main()
