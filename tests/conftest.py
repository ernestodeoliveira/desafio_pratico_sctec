from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


class MockResponse:
    """Mock for Supabase query responses."""

    def __init__(self, data):
        self.data = data


class MockQuery:
    """Mock for Supabase query builder chain."""

    def __init__(self, data=None):
        self._data = data or []

    def insert(self, data):
        self._inserted = data
        return self

    def select(self, *args):
        return self

    def update(self, data):
        self._updated = data
        return self

    def delete(self):
        return self

    def eq(self, field, value):
        return self

    def range(self, start, end):
        return self

    def execute(self):
        return MockResponse(self._data)


@pytest.fixture
def mock_supabase(monkeypatch):
    """Provide a mocked supabase client."""
    mock_client = MagicMock()
    monkeypatch.setattr("app.crud.get_supabase", lambda: mock_client)
    return mock_client


@pytest_asyncio.fixture
async def client():
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


SAMPLE_EMPREENDIMENTO = {
    "id": 1,
    "nome_empreendimento": "Tech Solutions SC",
    "nome_empreendedor": "João Silva",
    "municipio": "Florianópolis",
    "segmento": "Tecnologia",
    "email": "joao@example.com",
    "status": "ativo",
    "created_at": "2026-03-03T12:00:00+00:00",
    "updated_at": "2026-03-03T12:00:00+00:00",
}
