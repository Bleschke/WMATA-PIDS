#!/usr/bin/env python3
import os, requests
from flask import Flask, jsonify, request, render_template, send_from_directory

WMATA_KEY = os.environ.get("WMATA_API_KEY") or os.environ.get("Ocp_Apim_Subscription_Key") or ""

app = Flask(__name__)

# --- .env persistence helpers ---
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

def _read_env():
    vals = {}
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                vals[k.strip()] = v
    except FileNotFoundError:
        pass
    return vals

def _write_env_key(key, value):
    vals = _read_env()
    if value is None:
        vals.pop(key, None)
    else:
        vals[key] = value
    lines = [f'{k}="{v}"\n' for k, v in vals.items()]
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

# Prefer .env key at startup if present
_env = _read_env()
if _env.get("WMATA_API_KEY"):
    WMATA_KEY = _env["WMATA_API_KEY"]

def wmata_get(url, params=None):
    params = params or {}
    headers = {
        "api_key": WMATA_KEY,
        "Ocp-Apim-Subscription-Key": WMATA_KEY,
        "User-Agent": "WMATA-PIDS-Example/9.0"
    }
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/predictions")
def predictions():
    station = request.args.get("station", "").strip().upper()
    if not station:
        return jsonify({"error": "missing station parameter"}), 400
    url = f"https://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station}"
    try:
        data = wmata_get(url)
    except requests.HTTPError as e:
        return jsonify({"error": "wmata http error", "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "wmata request failed", "detail": str(e)}), 502

    trains = data.get("Trains", [])
    for t in trains:
        t.setdefault("Line", "")
        t.setdefault("Destination", "")
        t.setdefault("DestinationName", t.get("DestinationName", t.get("Destination", "")))
        t.setdefault("Min", "")
        t.setdefault("Car", "")
        t.setdefault("Group", "")
        m = (t.get("Min", "") or "").strip()
        try:
            t["_min_num"] = int(m)
        except Exception:
            t["_min_num"] = 9999 if m not in ("BRD", "ARR") else (-1 if m == "BRD" else 0)
    trains_sorted = sorted(trains, key=lambda x: (str(x.get("Group","Z")), x.get("_min_num", 9999)))
    return jsonify({"station": station, "trains": trains_sorted})

@app.route("/api/stations")
def stations():
    q = (request.args.get("q", "") or "").strip().lower()
    url = "https://api.wmata.com/Rail.svc/json/jStations"
    try:
        data = wmata_get(url)
        items = data.get("Stations", [])
        if q:
            items = [s for s in items if q in (s.get("Name","").lower())]
        results = [
            {
                "name": s.get("Name",""),
                "code": s.get("Code",""),
                "line_codes": [s.get("LineCode1"), s.get("LineCode2"), s.get("LineCode3"), s.get("LineCode4")]
            }
            for s in items
        ]
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": "wmata station lookup failed", "detail": str(e)}), 502

@app.route("/api/incidents")
def incidents():
    """Return WMATA rail incidents (service disruptions/alerts)."""
    url = "https://api.wmata.com/Incidents.svc/json/Incidents"
    try:
        data = wmata_get(url)
        inc = [i for i in data.get("Incidents", []) if (i.get("IncidentType","") or "").upper() == "RAIL"]
        for item in inc:
            lines = []
            raw = item.get("LinesAffected") or ""
            for token in raw.replace("/", ";").split(";"):
                t = token.strip().upper()
                if t in ("RD","OR","SV","BL","YL","GR"):
                    lines.append(t)
            item["_lines"] = lines
            item["_description"] = (item.get("Description","") or "").strip()
        return jsonify({"incidents": inc})
    except Exception as e:
        return jsonify({"error": "wmata incidents failed", "detail": str(e)}), 502

@app.route("/api/config", methods=["GET", "POST"])
def config():
    """
    Read or update server-side WMATA API key at runtime.
    GET  -> returns masked status {has_key, masked, persist_path}
    POST -> accepts JSON {"api_key": "VALUE", "persist": bool}
            Updates in memory and optionally writes .env
    """
    global WMATA_KEY
    if request.method == "GET":
        masked = "*" * len(WMATA_KEY) if WMATA_KEY else ""
        return jsonify({"has_key": bool(WMATA_KEY), "masked": masked, "persist_path": ENV_PATH})
    data = request.get_json(silent=True) or {}
    new_key = (data.get("api_key") or "").strip()
    persist = bool(data.get("persist"))
    WMATA_KEY = new_key
    if persist:
        if new_key:
            _write_env_key("WMATA_API_KEY", new_key)
        else:
            _write_env_key("WMATA_API_KEY", None)
    masked = "*" * len(WMATA_KEY) if WMATA_KEY else ""
    return jsonify({"has_key": bool(WMATA_KEY), "masked": masked, "persisted": persist})

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
