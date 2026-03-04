import httpx

from app.config import settings


def get_client() -> httpx.AsyncClient:
    """Return a configured async httpx client for Supabase REST API."""
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    return httpx.AsyncClient(
        base_url=f"{url}/rest/v1",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        timeout=10.0,
    )
