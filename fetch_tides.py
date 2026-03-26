#!/usr/bin/env python3
"""
fetch_tides.py
Fetches the next 24h of high/low tide predictions for Saint John NB
from the Canadian Hydrographic Service (CHS) IWLS API and saves tides.json.

CHS API: https://api-iwls.dfo-mpo.gc.ca/api/v1/
Station: Saint John NB — code 00065
"""

import requests, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE    = "https://api-iwls.dfo-mpo.gc.ca/api/v1"
CODE    = "00065"   # Saint John NB
OUTPUT  = Path(__file__).parent / "tides.json"
HEADERS = {"User-Agent": "dashboard/1.0", "Accept": "application/json"}

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

    # Step 2 — fetch high/low predictions for next 48h
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

    # Step 3 — shape into simple list
    tides = []
    for item in data:
        tides.append({
            "time":   item["eventDate"],        # ISO string UTC
            "type":   item["tideTypecode"],     # "H" or "L"
            "height": item["value"],            # metres
        })

    OUTPUT.write_text(json.dumps(tides, indent=2))
    print(f"Saved tides.json ({len(tides)} events)")

if __name__ == "__main__":
    main()
