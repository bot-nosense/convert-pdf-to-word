from __future__ import annotations

from waitress import serve

from .app import create_app
from .config import get_settings
from .network import get_local_ipv4_addresses


def main() -> None:
    settings = get_settings()
    app = create_app(settings)

    print(f"Server listening on http://{settings.host}:{settings.port}")
    print(f"Converter engine: {settings.converter_engine}")
    for ip_address in get_local_ipv4_addresses():
        print(f"LAN URL: http://{ip_address}:{settings.port}")

    serve(app, host=settings.host, port=settings.port, threads=4)


if __name__ == "__main__":
    main()
