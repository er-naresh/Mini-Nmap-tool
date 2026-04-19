# Mini-Nmap — Advanced Network Scanner

A beginner-friendly but professional **TCP port scanner** built with Python,
Flask, and a hacker-style web UI. Performs multithreaded port scanning,
service detection, and banner grabbing — all wrapped in a slick terminal
themed dashboard.

> ⚠️ **Legal notice** — Only scan hosts you own or have explicit written
> permission to test. Unauthorized port scanning may be illegal in your
> jurisdiction.

---

## Features

- 🔌 **TCP Port Scanning** — defaults to ports 1–1024, fully customizable
- 🟢 **Status detection** — OPEN / CLOSED with color-coded output
- 🛰 **Service detection** — built-in mapping for 70+ common ports
- 🏷 **Banner grabbing** — best-effort service banner for open ports
- ⚡ **Multithreaded** via `concurrent.futures.ThreadPoolExecutor`
- ⏱ **Timeout handling** + scan duration reporting
- 🌐 **REST API** — `POST /scan` with JSON in/out
- 💾 **Export results** as a JSON file
- 🎨 **Terminal-themed UI** — scanlines, CRT flicker, neon green-on-black

---

## Project structure

```
mini-nmap/
├── app.py               # Flask app + /scan endpoint
├── scanner.py           # Multithreaded scan logic
├── services.py          # Port → service name mapping
├── banner.py            # Banner-grabbing helper
├── requirements.txt
├── templates/
│   └── index.html       # Web UI
└── static/
    ├── style.css        # Hacker terminal theme
    └── script.js        # Frontend logic + fetch/AJAX
```

---

## Setup

Requires **Python 3.10+**.

```bash
# 1. (recommended) create a virtualenv
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. run the app
python app.py
```

Then open <http://127.0.0.1:5000> in your browser.

---

## Using the API directly

`POST /scan`

```json
{
  "target": "scanme.nmap.org",
  "start_port": 1,
  "end_port": 1024,
  "timeout": 1.0
}
```

**Response**

```json
{
  "target": "scanme.nmap.org",
  "duration_seconds": 12.43,
  "stats": { "total": 1024, "open": 3, "closed": 1021 },
  "results": [
    { "port": 22, "status": "OPEN", "service": "SSH", "banner": "SSH-2.0-OpenSSH_6.6.1p1" },
    { "port": 80, "status": "OPEN", "service": "HTTP", "banner": "HTTP/1.1 200 OK" },
    { "port": 23, "status": "CLOSED" }
  ]
}
```

cURL example:

```bash
curl -X POST http://127.0.0.1:5000/scan \
  -H 'Content-Type: application/json' \
  -d '{"target":"127.0.0.1","start_port":20,"end_port":100}'
```

---

## Tuning

- `max_workers` (in `scanner.py`) — thread pool size; default 100
- `timeout` (per-port socket timeout in seconds) — pass in JSON body
- Max range per request is capped at **5000 ports** (see `app.py`)

---

## Safe test target

[`scanme.nmap.org`](http://scanme.nmap.org) is provided by the Nmap project
and explicitly allows scanning for educational purposes.

---

## License

MIT — for educational use.
