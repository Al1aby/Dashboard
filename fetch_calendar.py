#!/usr/bin/env python3
"""
fetch_calendar.py
─────────────────
Fetches the public iCloud calendar share link and writes the next
7 days of events (including recurring events) to events.json.
"""

import json, sys
from datetime import datetime, date, timedelta
from pathlib import Path

ICS_URLS = [
    "https://p165-caldav.icloud.com/published/2/Mjc1MDE3NTk4Mjc1MDE3NcNKGptmumQbi69riMVJicVrcLZINKkxPaqFq1UjFIYeSXvsQh0mv80XocmmlmSw9gQy8s1oFPN_FK4HFE5pMtU"
]

DAYS_AHEAD  = 7
OUTPUT_FILE = Path(__file__).parent / "events.json"


def fetch_ics(url):
    import requests
    url = url.replace("webcal://", "https://")
    r = requests.get(url, timeout=20, headers={"User-Agent": "Pi-Dashboard-GHA/1.0"})
    r.raise_for_status()
    return r.text


def parse_ics(text, cal_name="iCloud"):
    from icalendar import Calendar
    from icalendar.cal import Component
    try:
        from dateutil.rrule import rruleset, rrulestr
        HAS_DATEUTIL = True
    except ImportError:
        HAS_DATEUTIL = False

    today    = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today + timedelta(days=DAYS_AHEAD)
    events   = []

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
            rrule    = component.get("RRULE")
            exdates  = component.get("EXDATE")

            if dtstart is None:
                continue

            dt = dtstart.dt
            de = dtend.dt if dtend else None
            all_day = isinstance(dt, date) and not isinstance(dt, datetime)

            # Calculate event duration
            if de:
                if all_day:
                    duration = de - dt
                else:
                    duration = (de if isinstance(de, datetime) else datetime.combine(de, datetime.min.time())) - \
                               (dt if isinstance(dt, datetime) else datetime.combine(dt, datetime.min.time()))
            else:
                duration = timedelta(hours=1)

            # Build list of occurrence datetimes to check
            occurrences = []

            if rrule and HAS_DATEUTIL:
                # Expand the recurrence rule
                try:
                    # Normalise dtstart to naive datetime for rrulestr
                    if all_day:
                        dt_naive = datetime.combine(dt, datetime.min.time())
                    else:
                        dt_naive = dt.replace(tzinfo=None) if hasattr(dt, 'tzinfo') and dt.tzinfo else dt

                    rule_str = "DTSTART:" + dt_naive.strftime("%Y%m%dT%H%M%S") + "\n"
                    rule_str += "RRULE:" + rrule.to_ical().decode()

                    # Collect excluded dates
                    excluded = set()
                    if exdates:
                        exdate_list = exdates if isinstance(exdates, list) else [exdates]
                        for exd in exdate_list:
                            for exdt in (exd.dts if hasattr(exd, 'dts') else [exd]):
                                exdt_val = exdt.dt if hasattr(exdt, 'dt') else exdt
                                if isinstance(exdt_val, date) and not isinstance(exdt_val, datetime):
                                    excluded.add(datetime.combine(exdt_val, datetime.min.time()))
                                elif isinstance(exdt_val, datetime):
                                    excluded.add(exdt_val.replace(tzinfo=None))

                    rset = rrulestr(rule_str, ignoretz=True)
                    for occ in rset.between(today - timedelta(days=1), end_date, inc=True):
                        if occ not in excluded:
                            occurrences.append(occ)
                except Exception as e:
                    print(f"  rrule expand error: {e}", file=sys.stderr)
                    # Fall back to just checking the base event
                    occurrences = [datetime.combine(dt, datetime.min.time()) if all_day else
                                   (dt.replace(tzinfo=None) if hasattr(dt, 'tzinfo') and dt.tzinfo else dt)]
            else:
                # Non-recurring event — just use the start date
                if all_day:
                    occurrences = [datetime.combine(dt, datetime.min.time())]
                else:
                    occurrences = [dt.replace(tzinfo=None) if hasattr(dt, 'tzinfo') and dt.tzinfo else dt]

            # Emit one entry per occurrence that falls in our window
            for occ in occurrences:
                if not (today <= occ < end_date):
                    continue

                if all_day:
                    start_str = occ.date().isoformat()
                    end_d     = (occ + duration).date()
                    end_str   = end_d.isoformat()
                    time_str  = "All day"
                    sort_key  = start_str
                else:
                    start_str = occ.isoformat()
                    end_str   = (occ + duration).isoformat()
                    time_str  = occ.strftime("%-I:%M %p")
                    sort_key  = start_str

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


def main():
    all_events = []
    errors     = []

    for url in ICS_URLS:
        print(f"Fetching {url[:70]}…")
        try:
            text = fetch_ics(url)
            evs  = parse_ics(text)
            print(f"  → {len(evs)} events (including recurring)")
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


if __name__ == "__main__":
    main()
