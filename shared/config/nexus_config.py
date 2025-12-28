"""Nexus connection configuration utilities."""

import os


def get_nexus_server_url() -> str:
    """Get Nexus server URL from environment or default.

    Returns:
        Nexus server URL
    """
    return os.getenv("NEXUS_SERVER_URL", "http://localhost:8080")


def get_nexus_api_key() -> str | None:
    """Get Nexus API key from environment.

    Returns:
        Nexus API key or None if not set
    """
    return os.getenv("NEXUS_API_KEY")





