import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.supabase_client import get_client

logger = logging.getLogger(__name__)

TABLE = "empreendimentos"


async def create_empreendimento(data: dict[str, Any]) -> dict[str, Any]:
    """Insert a new empreendimento into the database."""
    logger.info("Creating empreendimento: %s", data.get("nome_empreendimento"))
    async with get_client() as client:
        response = await client.post(f"/{TABLE}", json=data)
        response.raise_for_status()
        return response.json()[0]


async def get_empreendimentos(
    municipio: Optional[str] = None,
    segmento: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List empreendimentos with optional filters and pagination."""
    params: dict[str, str] = {"select": "*", "order": "id.asc"}

    if municipio:
        params["municipio"] = f"eq.{municipio}"
    if segmento:
        params["segmento"] = f"eq.{segmento}"
    if status:
        params["status"] = f"eq.{status}"

    headers = {"Range": f"{offset}-{offset + limit - 1}"}

    async with get_client() as client:
        response = await client.get(f"/{TABLE}", params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info("Listed %d empreendimentos", len(result))
        return result


async def get_empreendimento_by_id(id: int) -> Optional[dict[str, Any]]:
    """Fetch a single empreendimento by ID."""
    async with get_client() as client:
        response = await client.get(f"/{TABLE}", params={"id": f"eq.{id}", "select": "*"})
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return data[0]


async def update_empreendimento(id: int, data: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Update an existing empreendimento."""
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    async with get_client() as client:
        response = await client.patch(
            f"/{TABLE}",
            params={"id": f"eq.{id}"},
            json=data,
        )
        response.raise_for_status()
        result = response.json()
        if not result:
            return None
        logger.info("Updated empreendimento %d", id)
        return result[0]


async def delete_empreendimento(id: int) -> bool:
    """Delete an empreendimento by ID."""
    async with get_client() as client:
        response = await client.delete(
            f"/{TABLE}",
            params={"id": f"eq.{id}"},
        )
        response.raise_for_status()
        result = response.json()
        if not result:
            return False
        logger.info("Deleted empreendimento %d", id)
        return True
