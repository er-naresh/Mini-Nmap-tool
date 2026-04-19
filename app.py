# app.py — Flask entrypoint for Mini-Nmap

import socket
import time
import ipaddress

from flask import Flask, jsonify, render_template, request

from scanner import scan_range

app = Flask(__name__)


def _validate(target: str, start: int, end: int) -> str | None:
    """Return an error string if inputs are invalid, else None."""
    if not target or not target.strip():
        return "Target IP/host is required"
    if not (1 <= start <= 65535) or not (1 <= end <= 65535):
        return "Ports must be between 1 and 65535"
    if start > end:
        return "start_port must be <= end_port"
    if (end - start) > 5000:
        return "Range too large (max 5000 ports per scan)"
    # Try parsing as IP for stricter check; otherwise allow hostnames
    try:
        ipaddress.ip_address(target)
    except ValueError:
        # Not an IP — accept as hostname (DNS will validate later)
        if any(c.isspace() for c in target):
            return "Invalid hostname"
    return None


@app.route("/")
def index():
    """Serve the frontend UI."""
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    """
    Run a port scan.

    Expected JSON body:
      {
        "target": "192.168.1.1",
        "start_port": 1,
        "end_port": 1024,
        "timeout": 1.0          # optional
      }
    """
    data = request.get_json(silent=True) or {}
    target = str(data.get("target", "")).strip()
    try:
        start_port = int(data.get("start_port", 1))
        end_port = int(data.get("end_port", 1024))
        timeout = float(data.get("timeout", 1.0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numeric inputs"}), 400

    err = _validate(target, start_port, end_port)
    if err:
        return jsonify({"error": err}), 400

    started = time.time()
    try:
        results = scan_range(
            target,
            start_port,
            end_port,
            timeout=timeout,
            max_workers=100,
        )
    except socket.gaierror:
        return jsonify({"error": f"Could not resolve host '{target}'"}), 400
    except Exception as exc:  # pragma: no cover - defensive
        return jsonify({"error": f"Scan failed: {exc}"}), 500

    duration = round(time.time() - started, 3)
    open_ports = [r for r in results if r["status"] == "OPEN"]

    return jsonify({
        "target": target,
        "start_port": start_port,
        "end_port": end_port,
        "duration_seconds": duration,
        "stats": {
            "total": len(results),
            "open": len(open_ports),
            "closed": len(results) - len(open_ports),
        },
        "results": results,
    })


if __name__ == "__main__":
    # Bind to 127.0.0.1 by default — change to 0.0.0.0 if you want LAN access
    app.run(host="127.0.0.1", port=5000, debug=True)
