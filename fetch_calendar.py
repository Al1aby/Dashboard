#!/usr/bin/env python3
"""
fetch_radar.py
──────────────
Fetches the latest radar GIF for station CASBV (Chipman, NB)
from Environment Canada's MSC Datamart and saves it as radar.gif.

The new URL format (post April 2024) uses timestamped filenames,
so we list the directory and grab the most recent Rain file.
"""

import requests, re, sys
from pathlib import Path

STATION   = "CASBV"   # Chipman NB — covers Saint John / Nauwigewauk
INDEX_URL = f"https://dd.weather.gc.ca/today/radar/DPQPE/GIF/{STATION}/"
OUTPUT    = Path(__file__).parent / "radar.gif"
HEADERS   = {"User-Agent": "Mozilla/5.0 (dashboard-bot/1.0)"}

def main():
    print(f"Listing {INDEX_URL}")
    r = requests.get(INDEX_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()

    # Find all Rain (non-contingency) gif filenames
    filenames = re.findall(
        rf'\d{{8}}T\d{{4}}Z_MSC_Radar-DPQPE_{STATION}_Rain\.gif',
        r.text
    )

    if not filenames:
        print("No Rain GIF files found in directory listing", file=sys.stderr)
        sys.exit(1)

    latest = sorted(filenames)[-1]
    url    = INDEX_URL + latest
    print(f"Fetching {url}")

    img = requests.get(url, headers=HEADERS, timeout=15)
    img.raise_for_status()

    OUTPUT.write_bytes(img.content)
    print(f"Saved radar.gif ({len(img.content)} bytes)")

if __name__ == "__main__":
    main()
