import httpx

from app.config import settings

_headers = {
    "apikey": settings.SUPABASE_KEY,
    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

BASE_URL = f"{settings.SUPABASE_URL}/rest/v1"


def get_client() -> httpx.Client:
    """Return a configured httpx client for Supabase REST API."""
    return httpx.Client(base_url=BASE_URL, headers=_headers, timeout=10.0)
