import pytest
from unittest.mock import MagicMock

from tests.conftest import SAMPLE_EMPREENDIMENTO


class MockResponse:
    def __init__(self, data):
        self.data = data


class MockQueryBuilder:
    def __init__(self, data):
        self._data = data

    def insert(self, data):
        return self

    def select(self, *args):
        return self

    def update(self, data):
        return self

    def delete(self):
        return self

    def eq(self, field, value):
        return self

    def range(self, start, end):
        return self

    def execute(self):
        return MockResponse(self._data)


def _mock_table(data):
    """Create a mock supabase.table() that returns chained query builder."""
    mock_client = MagicMock()
    mock_client.table.return_value = MockQueryBuilder(data)
    return mock_client


@pytest.mark.asyncio
async def test_create_empreendimento(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([SAMPLE_EMPREENDIMENTO])

    payload = {
        "nome_empreendimento": "Tech Solutions SC",
        "nome_empreendedor": "João Silva",
        "municipio": "Florianópolis",
        "segmento": "Tecnologia",
        "email": "joao@example.com",
        "status": "ativo",
    }
    response = await client.post("/empreendimentos/", json=payload)
    assert response.status_code == 201
    assert response.json()["nome_empreendimento"] == "Tech Solutions SC"


@pytest.mark.asyncio
async def test_create_invalid_municipio(client):
    payload = {
        "nome_empreendimento": "Test",
        "nome_empreendedor": "Test",
        "municipio": "Cidade Inexistente",
        "segmento": "Tecnologia",
    }
    response = await client.post("/empreendimentos/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_empreendimentos(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([SAMPLE_EMPREENDIMENTO])

    response = await client.get("/empreendimentos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_by_id(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([SAMPLE_EMPREENDIMENTO])

    response = await client.get("/empreendimentos/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_not_found(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([])

    response = await client.get("/empreendimentos/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_empreendimento(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([SAMPLE_EMPREENDIMENTO])

    payload = {
        "nome_empreendimento": "Tech Solutions SC Updated",
        "nome_empreendedor": "João Silva",
        "municipio": "Florianópolis",
        "segmento": "Tecnologia",
        "email": "joao@example.com",
        "status": "ativo",
    }
    response = await client.put("/empreendimentos/1", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_empreendimento(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([SAMPLE_EMPREENDIMENTO])

    response = await client.delete("/empreendimentos/1")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_not_found(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([])

    response = await client.delete("/empreendimentos/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_with_filters(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([SAMPLE_EMPREENDIMENTO])

    response = await client.get(
        "/empreendimentos/?municipio=Florianópolis&segmento=Tecnologia&status=ativo"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_with_pagination(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([SAMPLE_EMPREENDIMENTO])

    response = await client.get("/empreendimentos/?limit=5&offset=10")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_without_email(client, mock_supabase):
    sample_no_email = {**SAMPLE_EMPREENDIMENTO, "email": None}
    mock_supabase.table.return_value = MockQueryBuilder([sample_no_email])

    payload = {
        "nome_empreendimento": "Test",
        "nome_empreendedor": "Test",
        "municipio": "Florianópolis",
        "segmento": "Tecnologia",
    }
    response = await client.post("/empreendimentos/", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] is None


@pytest.mark.asyncio
async def test_create_invalid_segmento(client):
    payload = {
        "nome_empreendimento": "Test",
        "nome_empreendedor": "Test",
        "municipio": "Florianópolis",
        "segmento": "Mineração",
    }
    response = await client.post("/empreendimentos/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_not_found(client, mock_supabase):
    mock_supabase.table.return_value = MockQueryBuilder([])

    payload = {
        "nome_empreendimento": "Test",
        "nome_empreendedor": "Test",
        "municipio": "Florianópolis",
        "segmento": "Tecnologia",
    }
    response = await client.put("/empreendimentos/999", json=payload)
    assert response.status_code == 404
