import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.crud import (
    create_empreendimento,
    delete_empreendimento,
    get_empreendimento_by_id,
    get_empreendimentos,
    update_empreendimento,
)
from app.schemas import EmpreendimentoCreate, EmpreendimentoResponse, EmpreendimentoUpdate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Empreendimentos SC",
    description=(
        "API REST para gerenciamento de empreendimentos em Santa Catarina. "
        "Permite operações CRUD completas com validação de municípios, "
        "segmentos e filtros por query parameters."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "API Empreendimentos SC"}


@app.post(
    "/empreendimentos/",
    response_model=EmpreendimentoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Empreendimentos"],
    summary="Criar empreendimento",
    description="Cria um novo empreendimento com validação de município e segmento.",
)
async def create(data: EmpreendimentoCreate):
    logger.info("POST /empreendimentos/ - %s", data.nome_empreendimento)
    result = await create_empreendimento(data.model_dump(exclude_none=True))
    return result


@app.get(
    "/empreendimentos/",
    response_model=list[EmpreendimentoResponse],
    tags=["Empreendimentos"],
    summary="Listar empreendimentos",
    description="Lista empreendimentos com filtros opcionais por município, segmento e status, com paginação.",
)
async def list_all(
    municipio: Optional[str] = Query(None, description="Filtrar por município de SC"),
    segmento: Optional[str] = Query(None, description="Filtrar por segmento"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por status (ativo/inativo)"),
    limit: int = Query(10, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
):
    logger.info("GET /empreendimentos/ - filters: municipio=%s, segmento=%s, status=%s", municipio, segmento, status_filter)
    results = await get_empreendimentos(
        municipio=municipio,
        segmento=segmento,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return results


@app.get(
    "/empreendimentos/{id}",
    response_model=EmpreendimentoResponse,
    tags=["Empreendimentos"],
    summary="Buscar empreendimento por ID",
    description="Retorna um empreendimento específico pelo seu ID.",
)
async def get_by_id(id: int):
    logger.info("GET /empreendimentos/%d", id)
    result = await get_empreendimento_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="Empreendimento não encontrado")
    return result


@app.put(
    "/empreendimentos/{id}",
    response_model=EmpreendimentoResponse,
    tags=["Empreendimentos"],
    summary="Atualizar empreendimento",
    description="Atualiza completamente um empreendimento existente.",
)
async def update(id: int, data: EmpreendimentoUpdate):
    logger.info("PUT /empreendimentos/%d", id)
    result = await update_empreendimento(id, data.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Empreendimento não encontrado")
    return result


@app.delete(
    "/empreendimentos/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Empreendimentos"],
    summary="Remover empreendimento",
    description="Remove um empreendimento pelo ID.",
)
async def delete(id: int):
    logger.info("DELETE /empreendimentos/%d", id)
    deleted = await delete_empreendimento(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Empreendimento não encontrado")
