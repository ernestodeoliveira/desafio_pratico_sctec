from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


class MockHttpxResponse:
    """Mock for httpx response objects."""

    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class MockHttpxClient:
    """Mock httpx.Client that returns configured responses."""

    def __init__(self, data=None):
        self._data = data or []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get(self, *args, **kwargs):
        return MockHttpxResponse(self._data)

    def post(self, *args, **kwargs):
        return MockHttpxResponse(self._data)

    def patch(self, *args, **kwargs):
        return MockHttpxResponse(self._data)

    def delete(self, *args, **kwargs):
        return MockHttpxResponse(self._data)


@pytest.fixture
def mock_supabase(monkeypatch):
    """Provide a mocked httpx client for Supabase REST calls."""
    mock_fn = MagicMock()
    monkeypatch.setattr("app.crud.get_client", mock_fn)
    return mock_fn


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
