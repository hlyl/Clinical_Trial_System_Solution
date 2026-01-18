"""Main entry point for CTSR API."""

import uvicorn
from api.config import get_settings


def main():
    """Run the CTSR API server."""
    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )


if __name__ == "__main__":
    main()
