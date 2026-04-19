# services.py — common TCP port → service name mapping (mini /etc/services)

COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    67: "DHCP", 69: "TFTP", 80: "HTTP", 110: "POP3", 111: "RPC",
    119: "NNTP", 123: "NTP", 135: "MS-RPC", 137: "NetBIOS",
    139: "NetBIOS-SSN", 143: "IMAP", 161: "SNMP", 179: "BGP",
    194: "IRC", 389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
    514: "Syslog", 515: "LPD", 587: "SMTP-Submission", 631: "IPP",
    636: "LDAPS", 873: "rsync", 993: "IMAPS", 995: "POP3S",
    1080: "SOCKS", 1194: "OpenVPN", 1433: "MSSQL", 1521: "Oracle",
    1723: "PPTP", 2049: "NFS", 2082: "cPanel", 2083: "cPanel-SSL",
    2375: "Docker", 2376: "Docker-SSL", 3000: "Node/Dev",
    3128: "Squid-Proxy", 3306: "MySQL", 3389: "RDP",
    4444: "Metasploit", 5000: "UPnP/Flask", 5060: "SIP",
    5432: "PostgreSQL", 5500: "VNC", 5601: "Kibana", 5672: "AMQP",
    5900: "VNC", 5984: "CouchDB", 6379: "Redis", 6660: "IRC",
    6667: "IRC", 7001: "WebLogic", 8000: "HTTP-Alt", 8008: "HTTP-Alt",
    8080: "HTTP-Proxy", 8081: "HTTP-Alt", 8443: "HTTPS-Alt",
    8888: "HTTP-Alt", 9000: "SonarQube/PHP-FPM", 9090: "Prometheus",
    9200: "Elasticsearch", 9418: "Git", 11211: "Memcached",
    27017: "MongoDB", 50000: "SAP",
}


def get_service(port: int) -> str:
    """Return the well-known service name for a port, or 'unknown'."""
    return COMMON_SERVICES.get(port, "unknown")
