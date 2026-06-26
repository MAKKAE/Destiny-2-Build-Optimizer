"""PyInstaller entry point — starts the embedded uvicorn server."""

import sys

import uvicorn


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    if len(sys.argv) >= 3:
        host = sys.argv[1]
        port = int(sys.argv[2])

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()
