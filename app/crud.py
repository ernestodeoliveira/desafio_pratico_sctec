import logging
from datetime import datetime, timezone
from typing import Optional

from app.supabase_client import supabase

logger = logging.getLogger(__name__)

TABLE = "empreendimentos"


async def create_empreendimento(data: dict) -> dict:
    """Insert a new empreendimento into the database."""
    logger.info("Creating empreendimento: %s", data.get("nome_empreendimento"))
    response = supabase.table(TABLE).insert(data).execute()
    return response.data[0]


async def get_empreendimentos(
    municipio: Optional[str] = None,
    segmento: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> list[dict]:
    """List empreendimentos with optional filters and pagination."""
    query = supabase.table(TABLE).select("*")

    if municipio:
        query = query.eq("municipio", municipio)
    if segmento:
        query = query.eq("segmento", segmento)
    if status:
        query = query.eq("status", status)

    query = query.range(offset, offset + limit - 1)
    response = query.execute()
    logger.info("Listed %d empreendimentos", len(response.data))
    return response.data


async def get_empreendimento_by_id(id: int) -> Optional[dict]:
    """Fetch a single empreendimento by ID."""
    response = supabase.table(TABLE).select("*").eq("id", id).execute()
    if not response.data:
        return None
    return response.data[0]


async def update_empreendimento(id: int, data: dict) -> Optional[dict]:
    """Update an existing empreendimento."""
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    response = supabase.table(TABLE).update(data).eq("id", id).execute()
    if not response.data:
        return None
    logger.info("Updated empreendimento %d", id)
    return response.data[0]


async def delete_empreendimento(id: int) -> bool:
    """Delete an empreendimento by ID."""
    response = supabase.table(TABLE).delete().eq("id", id).execute()
    if not response.data:
        return False
    logger.info("Deleted empreendimento %d", id)
    return True
