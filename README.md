# Dashboard

A personal home dashboard displaying weather, calendar events, tides, radar, and moon phase for the Maritimes region of New Brunswick, Canada.

![Dark dashboard layout](https://via.placeholder.com/800x450/0c0f14/f0c060?text=Dashboard)

## Features

- **Live clock** — updates every second
- **Today's events** — pulled from iCloud calendar, color-coded past/current/future
- **Weather** — current conditions + 7-day forecast + next 6 hours (Open-Meteo)
- **Radar** — live RainViewer radar overlay on an interactive Leaflet map
- **Tides** — next 4 high/low tide events for Saint John, NB (CHS API)
- **Moon phase** — icon, name, and illumination percentage (calculated locally)
- **6-day calendar strip** — compact view of upcoming events

## Layout

```
┌──────────────────┬───────────────────────────┐
│  Clock           │  Weather  │  Radar map     │
│  Today's events  ├───────────────────────────┤
│  Moon / Tides    │  6-day calendar strip      │
└──────────────────┴───────────────────────────┘
```

## How It Works

The dashboard is a single static `index.html` file. Two Python scripts run on a schedule via GitHub Actions every 15 minutes and commit updated data files back to the repo. The page fetches those files on load and polls every few minutes.

```
GitHub Actions (every 15 min)
  ├── fetch_calendar.py  →  events.json  (iCloud ICS)
  └── fetch_tides.py     →  tides.json   (CHS IWLS API)
        ↓
    git commit + push

Browser (index.html)
  ├── ./events.json       — calendar events
  ├── ./tides.json        — tide predictions
  ├── Open-Meteo API      — weather (free, no key)
  └── RainViewer API      — radar tiles (free, no key)
```

## Running Locally

**Requirements:** Python 3.12+, any modern browser

```bash
# Install Python dependencies
pip install requests icalendar python-dateutil

# Fetch data
python fetch_calendar.py   # → events.json
python fetch_tides.py      # → tides.json

# Serve the page (required for fetch() to work with local files)
python -m http.server 8000
# Open http://localhost:8000
```

## Configuration

Everything is hardcoded for a specific location — edit these to relocate:

| What | File | Variable/Line |
|------|------|---------------|
| iCloud calendar URL | `fetch_calendar.py` | `CALENDAR_URL` |
| Tide station | `fetch_tides.py` | `CODE = "00065"` (Saint John NB) |
| Weather location | `index.html` | `LAT`, `LON` constants |
| Temperature unit | `index.html` | `UNITS = "C"` (change to `"F"`) |

No API keys or secrets are required — all data sources are free and public.

## Data Files

**`events.json`** — written by `fetch_calendar.py`
```json
{
  "events": [
    {
      "title": "Event Name",
      "date": "2026-03-28",
      "time": "9:30 AM",
      "end": "2026-03-28T10:00:00",
      "all_day": false,
      "location": "123 Main St",
      "calendar": "Personal"
    }
  ],
  "fetched_at": "2026-03-26T11:37:56Z",
  "error": null
}
```

**`tides.json`** — written by `fetch_tides.py`
```json
[
  { "time": "2026-03-26T18:30:00Z", "type": "H", "height": 6.25 },
  { "time": "2026-03-27T00:45:00Z", "type": "L", "height": 0.81 }
]
```

## GitHub Actions Workflow

`.github/workflows/fetch-calendar.yml` runs every 15 minutes:

1. Runs `fetch_calendar.py` and `fetch_tides.py`
2. Commits any changed `events.json` / `tides.json` with `[skip ci]`
3. Uses `git pull --rebase` before pushing to handle concurrent runs

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Maps | [Leaflet.js](https://leafletjs.com/) v1.9.4 |
| Radar tiles | [RainViewer](https://www.rainviewer.com/api.html) |
| Basemap | CartoDB Dark Matter |
| Weather | [Open-Meteo](https://open-meteo.com/) |
| Tides | [CHS IWLS API](https://api-iwls.dfo-mpo.gc.ca/) |
| Calendar | iCloud public share link (ICS) |
| Automation | GitHub Actions |
| Fonts | Google Fonts (Playfair Display, Karla, Inconsolata) |
