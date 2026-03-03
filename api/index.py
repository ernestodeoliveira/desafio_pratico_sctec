"""
Vercel serverless entry-point.
Single self-contained file -- NO imports from ``app/``.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Literal, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator

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


def _get_client() -> httpx.Client:
    """Return a configured httpx client for the Supabase REST API."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    return httpx.Client(
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
    "Abdon Batista", "Abelardo Luz", "Agrol\u00e2ndia", "Agron\u00f4mica", "\u00c1gua Doce",
    "\u00c1guas de Chapec\u00f3", "\u00c1guas Frias", "\u00c1guas Mornas", "Alfredo Wagner",
    "Alto Bela Vista", "Anchieta", "Angelina", "Anita Garibaldi", "Anit\u00e1polis",
    "Ant\u00f4nio Carlos", "Api\u00fana", "Arabut\u00e3", "Araquari", "Ararangu\u00e1", "Armaz\u00e9m",
    "Arroio Trinta", "Arvoredo", "Ascurra", "Atalanta", "Aurora",
    "Balne\u00e1rio Arroio do Silva", "Balne\u00e1rio Barra do Sul", "Balne\u00e1rio Cambori\u00fa",
    "Balne\u00e1rio Gaivota", "Balne\u00e1rio Pi\u00e7arras", "Balne\u00e1rio Rinc\u00e3o", "Bandeirante",
    "Barra Bonita", "Barra Velha", "Bela Vista do Toldo", "Belmonte",
    "Benedito Novo", "Bigua\u00e7u", "Blumenau", "Bocaina do Sul",
    "Bom Jardim da Serra", "Bom Jesus", "Bom Jesus do Oeste", "Bom Retiro",
    "Bombinhas", "Botuver\u00e1", "Bra\u00e7o do Norte", "Bra\u00e7o do Trombudo",
    "Brun\u00f3polis", "Brusque", "Ca\u00e7ador", "Caibi", "Calmon", "Cambori\u00fa",
    "Campo Alegre", "Campo Belo do Sul", "Campo Er\u00ea", "Campos Novos",
    "Canelinha", "Canoinhas", "Cap\u00e3o Alto", "Capinzal", "Capivari de Baixo",
    "Catanduvas", "Caxambu do Sul", "Celso Ramos", "Cerro Negro",
    "Chapad\u00e3o do Lageado", "Chapec\u00f3", "Cocal do Sul", "Conc\u00f3rdia",
    "Cordilheira Alta", "Coronel Freitas", "Coronel Martins", "Correia Pinto",
    "Corup\u00e1", "Crici\u00fama", "Cunha Por\u00e3", "Cunhata\u00ed", "Curitibanos", "Descanso",
    "Dion\u00edsio Cerqueira", "Dona Emma", "Doutor Pedrinho", "Entre Rios", "Ermo",
    "Erval Velho", "Faxinal dos Guedes", "Flor do Sert\u00e3o", "Florian\u00f3polis",
    "Formosa do Sul", "Forquilhinha", "Fraiburgo", "Frei Rog\u00e9rio", "Galv\u00e3o",
    "Garopaba", "Garuva", "Gaspar", "Governador Celso Ramos", "Gr\u00e3o-Par\u00e1",
    "Gravatal", "Guabiruba", "Guaraciaba", "Guaramirim", "Guaruj\u00e1 do Sul",
    "Guatambu", "Herval d'Oeste", "Ibiam", "Ibicar\u00e9", "Ibirama", "I\u00e7ara",
    "Ilhota", "Imaru\u00ed", "Imbituba", "Imbuia", "Indaial", "Iomer\u00ea", "Ipira",
    "Ipor\u00e3 do Oeste", "Ipua\u00e7u", "Ipumirim", "Iraceminha", "Irani", "Irati",
    "Irine\u00f3polis", "It\u00e1", "Itai\u00f3polis", "Itaja\u00ed", "Itapema", "Itapiranga",
    "Itapo\u00e1", "Ituporanga", "Jabor\u00e1", "Jacinto Machado", "Jaguaruna",
    "Jaragu\u00e1 do Sul", "Jardin\u00f3polis", "Joa\u00e7aba", "Joinville", "Jos\u00e9 Boiteux",
    "Jupi\u00e1", "Lacerd\u00f3polis", "Lages", "Laguna", "Lajeado Grande", "Laurentino",
    "Lauro M\u00fcller", "Lebon R\u00e9gis", "Leoberto Leal", "Lind\u00f3ia do Sul", "Lontras",
    "Luiz Alves", "Luzerna", "Macieira", "Mafra", "Major Gercino",
    "Major Vieira", "Maracaj\u00e1", "Maravilha", "Marema", "Massaranduba",
    "Matos Costa", "Meleiro", "Mirim Doce", "Modelo", "Monda\u00ed", "Monte Carlo",
    "Monte Castelo", "Morro da Fuma\u00e7a", "Morro Grande", "Navegantes",
    "Nova Erechim", "Nova Itaberaba", "Nova Trento", "Nova Veneza",
    "Novo Horizonte", "Orleans", "Otac\u00edlio Costa", "Ouro", "Ouro Verde",
    "Paial", "Painel", "Palho\u00e7a", "Palma Sola", "Palmeira", "Palmitos",
    "Papanduva", "Para\u00edso", "Passo de Torres", "Passos Maia", "Paulo Lopes",
    "Pedras Grandes", "Penha", "Peritiba", "Pescaria Brava", "Petrol\u00e2ndia",
    "Pinhalzinho", "Pinheiro Preto", "Piratuba", "Planalto Alegre", "Pomerode",
    "Ponte Alta", "Ponte Alta do Norte", "Ponte Serrada", "Porto Belo",
    "Porto Uni\u00e3o", "Pouso Redondo", "Praia Grande",
    "Presidente Castello Branco", "Presidente Get\u00falio", "Presidente Nereu",
    "Princesa", "Quilombo", "Rancho Queimado", "Rio das Antas", "Rio do Campo",
    "Rio do Oeste", "Rio do Sul", "Rio dos Cedros", "Rio Fortuna",
    "Rio Negrinho", "Rio Rufino", "Riqueza", "Rodeio", "Romel\u00e2ndia", "Salete",
    "Saltinho", "Salto Veloso", "Sang\u00e3o", "Santa Cec\u00edlia", "Santa Helena",
    "Santa Rosa de Lima", "Santa Rosa do Sul", "Santa Terezinha",
    "Santa Terezinha do Progresso", "Santiago do Sul",
    "Santo Amaro da Imperatriz", "S\u00e3o Bento do Sul", "S\u00e3o Bernardino",
    "S\u00e3o Bonif\u00e1cio", "S\u00e3o Carlos", "S\u00e3o Crist\u00f3v\u00e3o do Sul", "S\u00e3o Domingos",
    "S\u00e3o Francisco do Sul", "S\u00e3o Jo\u00e3o Batista", "S\u00e3o Jo\u00e3o do Itaperi\u00fa",
    "S\u00e3o Jo\u00e3o do Oeste", "S\u00e3o Jo\u00e3o do Sul", "S\u00e3o Joaquim", "S\u00e3o Jos\u00e9",
    "S\u00e3o Jos\u00e9 do Cedro", "S\u00e3o Jos\u00e9 do Cerrito", "S\u00e3o Louren\u00e7o do Oeste",
    "S\u00e3o Ludgero", "S\u00e3o Martinho", "S\u00e3o Miguel da Boa Vista",
    "S\u00e3o Miguel do Oeste", "S\u00e3o Pedro de Alc\u00e2ntara", "Saudades", "Schroeder",
    "Seara", "Serra Alta", "Sider\u00f3polis", "Sombrio", "Sul Brasil", "Tai\u00f3",
    "Tangar\u00e1", "Tigrinhos", "Tijucas", "Timb\u00e9 do Sul", "Timb\u00f3",
    "Timb\u00f3 Grande", "Tr\u00eas Barras", "Treviso", "Treze de Maio", "Treze T\u00edlias",
    "Trombudo Central", "Tubar\u00e3o", "Tun\u00e1polis", "Turvo", "Uni\u00e3o do Oeste",
    "Urubici", "Urupema", "Urussanga", "Varge\u00e3o", "Vargem", "Vargem Bonita",
    "Vidal Ramos", "Videira", "Vitor Meireles", "Witmarsum", "Xanxer\u00ea",
    "Xavantina", "Xaxim", "Zort\u00e9a",
]

SEGMENTOS: list[str] = [
    "Tecnologia", "Com\u00e9rcio", "Ind\u00fastria", "Servi\u00e7os", "Agroneg\u00f3cio",
]

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class EmpreendimentoCreate(BaseModel):
    """Schema for creating a new empreendimento."""

    nome_empreendimento: str
    nome_empreendedor: str
    municipio: str
    segmento: Literal["Tecnologia", "Com\u00e9rcio", "Ind\u00fastria", "Servi\u00e7os", "Agroneg\u00f3cio"]
    email: Optional[EmailStr] = None
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
                f"Munic\u00edpio '{v}' n\u00e3o \u00e9 um munic\u00edpio v\u00e1lido de Santa Catarina"
            )
        return v


class EmpreendimentoUpdate(BaseModel):
    """Schema for fully updating an empreendimento."""

    nome_empreendimento: str
    nome_empreendedor: str
    municipio: str
    segmento: Literal["Tecnologia", "Com\u00e9rcio", "Ind\u00fastria", "Servi\u00e7os", "Agroneg\u00f3cio"]
    email: Optional[EmailStr] = None
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
                f"Munic\u00edpio '{v}' n\u00e3o \u00e9 um munic\u00edpio v\u00e1lido de Santa Catarina"
            )
        return v


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
    with _get_client() as client:
        response = client.post(f"/{TABLE}", json=data)
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

    with _get_client() as client:
        response = client.get(f"/{TABLE}", params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info("Listed %d empreendimentos", len(result))
        return result


async def get_empreendimento_by_id(id: int) -> Optional[dict]:
    """Fetch a single empreendimento by ID."""
    with _get_client() as client:
        response = client.get(f"/{TABLE}", params={"id": f"eq.{id}", "select": "*"})
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return data[0]


async def update_empreendimento(id: int, data: dict) -> Optional[dict]:
    """Update an existing empreendimento."""
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    with _get_client() as client:
        response = client.patch(
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
    with _get_client() as client:
        response = client.delete(
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
        "Permite opera\u00e7\u00f5es CRUD completas com valida\u00e7\u00e3o de munic\u00edpios, "
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
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "API Empreendimentos SC"}


@app.post(
    "/empreendimentos/",
    response_model=EmpreendimentoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Empreendimentos"],
    summary="Criar empreendimento",
    description="Cria um novo empreendimento com valida\u00e7\u00e3o de munic\u00edpio e segmento.",
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
    description="Lista empreendimentos com filtros opcionais por munic\u00edpio, segmento e status, com pagina\u00e7\u00e3o.",
)
async def list_all(
    municipio: Optional[str] = Query(None, description="Filtrar por munic\u00edpio de SC"),
    segmento: Optional[str] = Query(None, description="Filtrar por segmento"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por status (ativo/inativo)"),
    limit: int = Query(10, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para pagina\u00e7\u00e3o"),
):
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
    description="Retorna um empreendimento espec\u00edfico pelo seu ID.",
)
async def get_by_id(id: int):
    logger.info("GET /empreendimentos/%d", id)
    result = await get_empreendimento_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="Empreendimento n\u00e3o encontrado")
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
        raise HTTPException(status_code=404, detail="Empreendimento n\u00e3o encontrado")
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
        raise HTTPException(status_code=404, detail="Empreendimento n\u00e3o encontrado")
