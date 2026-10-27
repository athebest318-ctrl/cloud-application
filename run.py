import uvicorn
import argparse
from pathlib import Path

from app.config import settings


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    ssl_options = {}
    if settings.https_enabled:
        cert = Path(settings.ssl_certfile)
        key = Path(settings.ssl_keyfile)
        if not cert.is_file():
            raise RuntimeError(f"Certificate not found: {cert}")
        if not key.is_file():
            raise RuntimeError(f"Private key not found: {key}")
        ssl_options = {"ssl_certfile": str(cert), "ssl_keyfile": str(key)}
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=args.port or (settings.https_port if settings.https_enabled else settings.app_port),
        reload=settings.app_env == "development",
        **ssl_options,
    )
