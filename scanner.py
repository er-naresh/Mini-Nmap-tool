# scanner.py — multithreaded TCP port scanner

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from services import get_service
from banner import grab_banner


def scan_port(ip: str, port: int, timeout: float = 1.0) -> dict:
    """
    Attempt a TCP connect to (ip, port). Returns a dict:
      { "port": int, "status": "OPEN"|"CLOSED", "service": str, "banner": str|None }
    Banner is only attempted on OPEN ports.
    """
    result = {"port": port, "status": "CLOSED"}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            # connect_ex returns 0 on success (port open)
            if sock.connect_ex((ip, port)) == 0:
                result["status"] = "OPEN"
                result["service"] = get_service(port)
                banner = grab_banner(ip, port, timeout=timeout)
                if banner:
                    result["banner"] = banner
    except socket.gaierror:
        # DNS / address error — propagate so the caller can report it
        raise
    except Exception:
        # Any other socket error → port treated as CLOSED
        pass
    return result


def scan_range(
    ip: str,
    start_port: int,
    end_port: int,
    timeout: float = 1.0,
    max_workers: int = 100,
    on_progress: Callable[[dict], None] | None = None,
) -> list[dict]:
    """
    Scan a range of TCP ports concurrently using a thread pool.
    Returns a list of result dicts sorted by port number.
    """
    # Resolve hostname once up front (raises socket.gaierror on bad host)
    socket.gethostbyname(ip)

    results: list[dict] = []
    ports = range(start_port, end_port + 1)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_port = {
            pool.submit(scan_port, ip, p, timeout): p for p in ports
        }
        for future in as_completed(future_to_port):
            res = future.result()
            results.append(res)
            if on_progress:
                on_progress(res)

    results.sort(key=lambda r: r["port"])
    return results
