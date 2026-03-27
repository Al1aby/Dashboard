#!/usr/bin/env python3
"""
fetch_tides.py
Fetches the next 48h of high/low tide predictions for Saint John NB
from the Canadian Hydrographic Service (CHS) IWLS API and saves tides.json.

CHS API: https://api-iwls.dfo-mpo.gc.ca/api/v1/
Station: Saint John NB — code 00065

Notes:
  - The API returns eventDate in local Atlantic time but labels it with Z
    (as if UTC). We strip the Z so the browser displays it correctly as
    local time rather than double-converting.
  - Heights are returned above a geodetic datum (~MSL), not above Chart
    Datum. We fetch the station's MWL height above Chart Datum and subtract
    it so displayed heights match the official Canadian Tide Tables.
"""

import requests, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE    = "https://api-iwls.dfo-mpo.gc.ca/api/v1"
CODE    = "00065"   # Saint John NB
OUTPUT  = Path(__file__).parent / "tides.json"
HEADERS = {"User-Agent": "dashboard/1.0", "Accept": "application/json"}


def get_chart_datum_offset(sid):
    """
    Return the height (m) to subtract from API values to get Chart Datum heights.
    The CHS IWLS API returns water levels above CGVD2013 (Canadian geodetic
    vertical datum). The station heights array lists datums above Chart Datum,
    so the CGVD2013 entry gives the exact conversion offset needed.
    Falls back to 0 if the metadata is unavailable.
    """
    try:
        r = requests.get(f"{BASE}/stations/{sid}", headers=HEADERS, timeout=15)
        r.raise_for_status()
        station = r.json()
        heights = station.get("heights", [])
        print(f"Available height codes: {[h.get('code') for h in heights]}")
        for code in ("CGVD2013", "CGVD28", "MWL", "MSL"):
            for h in heights:
                if h.get("code") == code:
                    offset = float(h["value"])
                    print(f"Using {code} offset: {offset}m above Chart Datum")
                    return offset
    except Exception as e:
        print(f"Warning: could not fetch datum info: {e}")
    print("Warning: no datum offset found, heights will be uncorrected")
    return 0.0


def strip_tz(event_date):
    """
    Strip timezone info from an ISO datetime string.
    The CHS API marks local Atlantic times with Z — removing it lets the
    browser parse the value as local time instead of UTC.
    """
    # Remove trailing Z
    s = event_date
    if s.endswith("Z"):
        s = s[:-1]
    # Remove any +HH:MM or -HH:MM offset that follows the time component
    if "T" in s:
        date_part, time_part = s.split("T", 1)
        time_part = time_part[:8]   # keep HH:MM:SS only
        s = f"{date_part}T{time_part}"
    return s


def main():
    # Step 1 — look up the station's internal UUID
    print(f"Looking up station {CODE}...")
    r = requests.get(f"{BASE}/stations", params={"chs-station-code": CODE}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    stations = r.json()
    if not stations:
        raise RuntimeError(f"Station {CODE} not found")
    sid = stations[0]["id"]
    print(f"Station ID: {sid}")

    # Step 2 — get Chart Datum offset so we can correct the heights
    datum_offset = get_chart_datum_offset(sid)

    # Step 3 — fetch high/low predictions for next 48h
    now    = datetime.now(timezone.utc)
    end    = now + timedelta(hours=48)
    params = {
        "time-series-code": "wlp-hilo",
        "from": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "to":   end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    print(f"Fetching tide predictions {params['from']} → {params['to']}")
    r2 = requests.get(f"{BASE}/stations/{sid}/data", params=params, headers=HEADERS, timeout=15)
    r2.raise_for_status()
    data = r2.json()
    print(f"Got {len(data)} tide events")

    # Step 4 — shape into simple list
    # wlp-hilo returns alternating high/low events; infer type by comparing
    # each value to the next (higher = H, lower = L).
    tides = []
    for i, item in enumerate(data):
        if i + 1 < len(data):
            tide_type = "H" if item["value"] >= data[i + 1]["value"] else "L"
        else:
            tide_type = "H" if item["value"] >= data[i - 1]["value"] else "L"

        tides.append({
            "time":   strip_tz(item["eventDate"]),
            "type":   tide_type,
            "height": round(item["value"] - datum_offset, 2),
        })

    OUTPUT.write_text(json.dumps(tides, indent=2))
    print(f"Saved tides.json ({len(tides)} events)")


if __name__ == "__main__":
    main()
