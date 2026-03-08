#!/usr/bin/env python3
“””
fetch_calendar.py
─────────────────
Fetches the public iCloud calendar share link and writes the next
14 days of events to events.json, which GitHub Pages serves statically.

Runs inside a GitHub Action — no CORS issues, no browser involved.
“””

import json, sys, os
from datetime import datetime, date, timedelta
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────

# Add your iCloud public calendar URL(s) here.

# Go to: iPhone → Calendar → tap ⓘ → Share Calendar → Public Calendar → Copy Link

# Replace webcal:// with https://

ICS_URLS = [
“https://p165-caldav.icloud.com/published/2/Mjc1MDE3NTk4Mjc1MDE3NcNKGptmumQbi69riMVJicVrcLZINKkxPaqFq1UjFIYeSXvsQh0mv80XocmmlmSw9gQy8s1oFPN_FK4HFE5pMtU”
]

DAYS_AHEAD = 7
OUTPUT_FILE = Path(**file**).parent / “events.json”

# ──────────────────────────────────────────────────────────────────

def fetch_ics(url):
import requests
url = url.replace(“webcal://”, “https://”)
r = requests.get(url, timeout=20, headers={“User-Agent”: “Pi-Dashboard-GHA/1.0”})
r.raise_for_status()
return r.text

def parse_ics(text, cal_name=“iCloud”):
from icalendar import Calendar
events = []

```
today    = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
end_date = today + timedelta(days=DAYS_AHEAD)

try:
    cal = Calendar.from_ical(text)
except Exception as e:
    print(f"  ICS parse error: {e}", file=sys.stderr)
    return []

cal_name = str(cal.get("X-WR-CALNAME", cal_name))

for component in cal.walk():
    if component.name != "VEVENT":
        continue
    try:
        summary  = str(component.get("SUMMARY", "No title"))
        location = str(component.get("LOCATION", "")) or None
        dtstart  = component.get("DTSTART")
        dtend    = component.get("DTEND")

        if dtstart is None:
            continue

        dt = dtstart.dt
        de = dtend.dt if dtend else None

        all_day = isinstance(dt, date) and not isinstance(dt, datetime)

        if all_day:
            if not (today.date() <= dt < end_date.date()):
                continue
            start_str = dt.isoformat()
            end_str   = de.isoformat() if de else None
            time_str  = "All day"
            sort_key  = dt.isoformat()
        else:
            # Normalise to local naive datetime
            if hasattr(dt, "tzinfo") and dt.tzinfo:
                dt = dt.astimezone().replace(tzinfo=None)
            if de and hasattr(de, "tzinfo") and de.tzinfo:
                de = de.astimezone().replace(tzinfo=None)
            if not (today <= dt < end_date):
                continue
            start_str = dt.isoformat()
            end_str   = de.isoformat() if de else None
            # e.g. "9:30 AM"
            time_str  = dt.strftime("%-I:%M %p")
            sort_key  = dt.isoformat()

        events.append({
            "title":    summary,
            "date":     start_str[:10],
            "time":     time_str,
            "end":      end_str,
            "all_day":  all_day,
            "location": location,
            "calendar": cal_name,
            "_sort":    sort_key,
        })

    except Exception as e:
        print(f"  Skipping event: {e}", file=sys.stderr)

return events
```

def main():
all_events = []
errors = []

```
for url in ICS_URLS:
    print(f"Fetching {url[:70]}…")
    try:
        text = fetch_ics(url)
        evs  = parse_ics(text)
        print(f"  → {len(evs)} events in next {DAYS_AHEAD} days")
        all_events.extend(evs)
    except Exception as e:
        msg = f"Failed to fetch {url[:60]}: {e}"
        print(f"  ERROR: {msg}", file=sys.stderr)
        errors.append(msg)

all_events.sort(key=lambda e: e["_sort"])
for e in all_events:
    del e["_sort"]

output = {
    "events":     all_events,
    "fetched_at": datetime.utcnow().isoformat() + "Z",
    "error":      "; ".join(errors) if errors and not all_events else None,
}

OUTPUT_FILE.write_text(json.dumps(output, indent=2))
print(f"\nWrote {len(all_events)} events to {OUTPUT_FILE}")

if errors and not all_events:
    sys.exit(1)
```

if **name** == “**main**”:
main()
