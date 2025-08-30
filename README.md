# WMATA PIDS v9 (Unofficial Demo)

Features:
- Real-time arrivals (per-station predictions)
- Two-column by platform group (checkbox)
- Custom banner or auto WMATA incidents
- Analytics overlay (counts per line, soonest arrivals, totals by group)
- Full screen + TV mode (click button or press **F** for fullscreen, **T** to toggle TV mode)
- API key UI with **green/red status dot**, **Save**, **Clear**, and optional **Persist to .env**
- Person icon next to the car count (16px)

## Run (Windows)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install flask requests
python app.py
```

Open: `http://localhost:5000/?station=F02`

Set API key via the toolbar (or use an environment variable). If you **Persist to .env**, it will be saved in the app folder and loaded on next start.
