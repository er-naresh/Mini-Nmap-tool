# banner.py — best-effort banner grabbing for an open TCP port

import socket


def grab_banner(ip: str, port: int, timeout: float = 1.5) -> str | None:
    """
    Connect to (ip, port) and try to read a service banner.

    For HTTP-style ports we send a minimal GET request to nudge a response.
    For most other text protocols (SSH, FTP, SMTP, POP3, IMAP) the server
    sends a greeting line as soon as the connection is accepted.
    """
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            sock.settimeout(timeout)

            # HTTP-style ports need a probe to return a response
            if port in (80, 8000, 8008, 8080, 8081, 8888):
                sock.sendall(
                    b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n"
                )

            data = sock.recv(1024)
            if not data:
                return None

            # Decode safely and return first non-empty line
            text = data.decode(errors="replace").strip()
            first_line = text.splitlines()[0] if text else None
            return first_line[:200] if first_line else None
    except Exception:
        # Banner grabbing is best-effort — never break the scan
        return None
