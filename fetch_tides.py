#!/usr/bin/env python3
"""
fetch_tides.py
Fetches high/low tide predictions for Saint John NB (station 00065)
directly from the official CHS tides.gc.ca station page and writes tides.json.

This page renders the actual daily high/low table server-side, e.g.:
  2026-08-06 (Thu) Time ADT Height (m) Height (ft)
  05:47 7.208 23.6
  12:02 1.531 5.0
  18:13 7.605 25.0
"""

import re, json, requests
from pathlib import Path

URL     = "https://www.tides.gc.ca/en/stations/65"   # Saint John, NB
OUTPUT  = Path(__file__).parent / "tides.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (dashboard/1.0)"}

TZ_OFFSET = {"ADT": "-03:00", "AST": "-04:00"}

DAY_BLOCK_RE = re.compile(
    r'(\d{4}-\d{2}-\d{2})\s*\((\w+)\)\s*Time\s*(A[SD]T)\s*Height\s*\(m\)\s*Height\s*\(ft\)\s*'
    r'((?:\d{2}:\d{2}\s+[\d.]+\s+[\d.]+\s*)+)'
)
EVENT_RE = re.compile(r'(\d{2}:\d{2})\s+([\d.]+)\s+[\d.]+')

def main():
    print(f"Fetching {URL}")
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    html = r.text
    print(f"Got {len(html)} chars")

    # Only look at the section before the per-minute "Hourly Predictions" table,
    # which is a different (much larger) block we don't need.
    cutoff = html.find("Hourly Predictions")
    if cutoff > 0:
        html = html[:cutoff]

    events = []
    for m in DAY_BLOCK_RE.finditer(html):
        date, _weekday, tzabbr, blob = m.groups()
        offset = TZ_OFFSET.get(tzabbr, "-03:00")
        for time_str, height_str in EVENT_RE.findall(blob):
            events.append({
                "time":   f"{date}T{time_str}:00{offset}",
                "height": float(height_str),
            })

    if not events:
        raise RuntimeError("No tide events parsed — page format may have changed")

    print(f"Parsed {len(events)} raw events")

    # Events alternate High/Low (semi-diurnal tide). Determine the first event's
    # type by comparing it to the next one, then alternate through the list.
    first_is_high = events[0]["height"] >= events[1]["height"] if len(events) > 1 else True
    for i, ev in enumerate(events):
        is_high = first_is_high if i % 2 == 0 else not first_is_high
        ev["type"] = "H" if is_high else "L"

    OUTPUT.write_text(json.dumps(events, indent=2))
    print(f"Saved tides.json ({len(events)} events)")
    print(json.dumps(events[:4], indent=2))

if __name__ == "__main__":
    main()
