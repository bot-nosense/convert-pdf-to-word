from __future__ import annotations

import socket


def get_local_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()

    try:
        hostname = socket.gethostname()
        for _, _, _, _, sockaddr in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip_address = sockaddr[0]
            if not ip_address.startswith("127."):
                addresses.add(ip_address)
    except OSError:
        pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip_address = sock.getsockname()[0]
            if not ip_address.startswith("127."):
                addresses.add(ip_address)
    except OSError:
        pass

    return sorted(addresses)
