"""
Vercel serverless entry-point.
Single self-contained file -- NO imports from ``app/``.
"""

import logging
import os
import re
from datetime import datetime, timezone
from typing import Literal, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supabase httpx client (lazy env-var read, no dotenv)
# ---------------------------------------------------------------------------
TABLE = "empreendimentos"


def _get_client() -> httpx.AsyncClient:
    """Return a configured async httpx client for the Supabase REST API."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
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


# ---------------------------------------------------------------------------
# Municipalities constant (295 SC municipalities)
# ---------------------------------------------------------------------------
MUNICIPIOS_SC: list[str] = [
    "Abdon Batista", "Abelardo Luz", "Agrolândia", "Agronômica", "Água Doce",
    "Águas de Chapecó", "Águas Frias", "Águas Mornas", "Alfredo Wagner",
    "Alto Bela Vista", "Anchieta", "Angelina", "Anita Garibaldi", "Anitápolis",
    "Antônio Carlos", "Apiúna", "Arabutã", "Araquari", "Araranguá", "Armazém",
    "Arroio Trinta", "Arvoredo", "Ascurra", "Atalanta", "Aurora",
    "Balneário Arroio do Silva", "Balneário Barra do Sul", "Balneário Camboriú",
    "Balneário Gaivota", "Balneário Piçarras", "Balneário Rincão", "Bandeirante",
    "Barra Bonita", "Barra Velha", "Bela Vista do Toldo", "Belmonte",
    "Benedito Novo", "Biguaçu", "Blumenau", "Bocaina do Sul",
    "Bom Jardim da Serra", "Bom Jesus", "Bom Jesus do Oeste", "Bom Retiro",
    "Bombinhas", "Botuverá", "Braço do Norte", "Braço do Trombudo",
    "Brunópolis", "Brusque", "Caçador", "Caibi", "Calmon", "Camboriú",
    "Campo Alegre", "Campo Belo do Sul", "Campo Erê", "Campos Novos",
    "Canelinha", "Canoinhas", "Capão Alto", "Capinzal", "Capivari de Baixo",
    "Catanduvas", "Caxambu do Sul", "Celso Ramos", "Cerro Negro",
    "Chapadão do Lageado", "Chapecó", "Cocal do Sul", "Concórdia",
    "Cordilheira Alta", "Coronel Freitas", "Coronel Martins", "Correia Pinto",
    "Corupá", "Criciúma", "Cunha Porã", "Cunhataí", "Curitibanos", "Descanso",
    "Dionísio Cerqueira", "Dona Emma", "Doutor Pedrinho", "Entre Rios", "Ermo",
    "Erval Velho", "Faxinal dos Guedes", "Flor do Sertão", "Florianópolis",
    "Formosa do Sul", "Forquilhinha", "Fraiburgo", "Frei Rogério", "Galvão",
    "Garopaba", "Garuva", "Gaspar", "Governador Celso Ramos", "Grão-Pará",
    "Gravatal", "Guabiruba", "Guaraciaba", "Guaramirim", "Guarujá do Sul",
    "Guatambu", "Herval d'Oeste", "Ibiam", "Ibicaré", "Ibirama", "Içara",
    "Ilhota", "Imaruí", "Imbituba", "Imbuia", "Indaial", "Iomerê", "Ipira",
    "Iporã do Oeste", "Ipuaçu", "Ipumirim", "Iraceminha", "Irani", "Irati",
    "Irineópolis", "Itá", "Itaiópolis", "Itajaí", "Itapema", "Itapiranga",
    "Itapoá", "Ituporanga", "Jaborá", "Jacinto Machado", "Jaguaruna",
    "Jaraguá do Sul", "Jardinópolis", "Joaçaba", "Joinville", "José Boiteux",
    "Jupiá", "Lacerdópolis", "Lages", "Laguna", "Lajeado Grande", "Laurentino",
    "Lauro Müller", "Lebon Régis", "Leoberto Leal", "Lindóia do Sul", "Lontras",
    "Luiz Alves", "Luzerna", "Macieira", "Mafra", "Major Gercino",
    "Major Vieira", "Maracajá", "Maravilha", "Marema", "Massaranduba",
    "Matos Costa", "Meleiro", "Mirim Doce", "Modelo", "Mondaí", "Monte Carlo",
    "Monte Castelo", "Morro da Fumaça", "Morro Grande", "Navegantes",
    "Nova Erechim", "Nova Itaberaba", "Nova Trento", "Nova Veneza",
    "Novo Horizonte", "Orleans", "Otacílio Costa", "Ouro", "Ouro Verde",
    "Paial", "Painel", "Palhoça", "Palma Sola", "Palmeira", "Palmitos",
    "Papanduva", "Paraíso", "Passo de Torres", "Passos Maia", "Paulo Lopes",
    "Pedras Grandes", "Penha", "Peritiba", "Pescaria Brava", "Petrolândia",
    "Pinhalzinho", "Pinheiro Preto", "Piratuba", "Planalto Alegre", "Pomerode",
    "Ponte Alta", "Ponte Alta do Norte", "Ponte Serrada", "Porto Belo",
    "Porto União", "Pouso Redondo", "Praia Grande",
    "Presidente Castello Branco", "Presidente Getúlio", "Presidente Nereu",
    "Princesa", "Quilombo", "Rancho Queimado", "Rio das Antas", "Rio do Campo",
    "Rio do Oeste", "Rio do Sul", "Rio dos Cedros", "Rio Fortuna",
    "Rio Negrinho", "Rio Rufino", "Riqueza", "Rodeio", "Romelândia", "Salete",
    "Saltinho", "Salto Veloso", "Sangão", "Santa Cecília", "Santa Helena",
    "Santa Rosa de Lima", "Santa Rosa do Sul", "Santa Terezinha",
    "Santa Terezinha do Progresso", "Santiago do Sul",
    "Santo Amaro da Imperatriz", "São Bento do Sul", "São Bernardino",
    "São Bonifácio", "São Carlos", "São Cristóvão do Sul", "São Domingos",
    "São Francisco do Sul", "São João Batista", "São João do Itaperiú",
    "São João do Oeste", "São João do Sul", "São Joaquim", "São José",
    "São José do Cedro", "São José do Cerrito", "São Lourenço do Oeste",
    "São Ludgero", "São Martinho", "São Miguel da Boa Vista",
    "São Miguel do Oeste", "São Pedro de Alcântara", "Saudades", "Schroeder",
    "Seara", "Serra Alta", "Siderópolis", "Sombrio", "Sul Brasil", "Taió",
    "Tangará", "Tigrinhos", "Tijucas", "Timbé do Sul", "Timbó",
    "Timbó Grande", "Três Barras", "Treviso", "Treze de Maio", "Treze Tílias",
    "Trombudo Central", "Tubarão", "Tunápolis", "Turvo", "União do Oeste",
    "Urubici", "Urupema", "Urussanga", "Vargeão", "Vargem", "Vargem Bonita",
    "Vidal Ramos", "Videira", "Vitor Meireles", "Witmarsum", "Xanxerê",
    "Xavantina", "Xaxim", "Zortéa",
]

SEGMENTOS: list[str] = [
    "Tecnologia", "Comércio", "Indústria", "Serviços", "Agronegócio",
]

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class _EmpreendimentoBase(BaseModel):
    """Shared fields and validators for empreendimento schemas."""

    nome_empreendimento: str
    nome_empreendedor: str
    municipio: str
    segmento: Literal["Tecnologia", "Comércio", "Indústria", "Serviços", "Agronegócio"]
    email: Optional[str] = None
    status: Literal["ativo", "inativo"] = "ativo"

    @field_validator("nome_empreendimento", "nome_empreendedor")
    @classmethod
    def validate_nome(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 255:
            raise ValueError("Nome deve ter entre 1 e 255 caracteres")
        return v

    @field_validator("municipio")
    @classmethod
    def validate_municipio(cls, v: str) -> str:
        if v not in MUNICIPIOS_SC:
            raise ValueError(
                f"Município '{v}' não é um município válido de Santa Catarina"
            )
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not _EMAIL_RE.match(v):
            raise ValueError("Formato de email inválido")
        return v


class EmpreendimentoCreate(_EmpreendimentoBase):
    """Schema for creating a new empreendimento."""


class EmpreendimentoUpdate(_EmpreendimentoBase):
    """Schema for fully updating an empreendimento."""


class EmpreendimentoResponse(BaseModel):
    """Schema for empreendimento API responses."""

    id: int
    nome_empreendimento: str
    nome_empreendedor: str
    municipio: str
    segmento: str
    email: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------


async def create_empreendimento(data: dict) -> dict:
    """Insert a new empreendimento into the database."""
    logger.info("Creating empreendimento: %s", data.get("nome_empreendimento"))
    async with _get_client() as client:
        response = await client.post(f"/{TABLE}", json=data)
        response.raise_for_status()
        return response.json()[0]


async def get_empreendimentos(
    municipio: Optional[str] = None,
    segmento: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> list[dict]:
    """List empreendimentos with optional filters and pagination."""
    params: dict = {"select": "*", "order": "id.asc"}

    if municipio:
        params["municipio"] = f"eq.{municipio}"
    if segmento:
        params["segmento"] = f"eq.{segmento}"
    if status:
        params["status"] = f"eq.{status}"

    headers = {"Range": f"{offset}-{offset + limit - 1}"}

    async with _get_client() as client:
        response = await client.get(f"/{TABLE}", params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info("Listed %d empreendimentos", len(result))
        return result


async def get_empreendimento_by_id(id: int) -> Optional[dict]:
    """Fetch a single empreendimento by ID."""
    async with _get_client() as client:
        response = await client.get(f"/{TABLE}", params={"id": f"eq.{id}", "select": "*"})
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return data[0]


async def update_empreendimento(id: int, data: dict) -> Optional[dict]:
    """Update an existing empreendimento."""
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    async with _get_client() as client:
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
    async with _get_client() as client:
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


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
async def root() -> dict:
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
async def create(data: EmpreendimentoCreate) -> EmpreendimentoResponse:
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
) -> list[EmpreendimentoResponse]:
    logger.info(
        "GET /empreendimentos/ - filters: municipio=%s, segmento=%s, status=%s",
        municipio, segmento, status_filter,
    )
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
async def get_by_id(id: int) -> EmpreendimentoResponse:
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
async def update(id: int, data: EmpreendimentoUpdate) -> EmpreendimentoResponse:
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
async def delete(id: int) -> Response:
    logger.info("DELETE /empreendimentos/%d", id)
    deleted = await delete_empreendimento(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Empreendimento não encontrado")
