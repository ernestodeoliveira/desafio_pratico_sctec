from typing import Optional
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


class MockHttpxResponse:
    """Mock for httpx response objects."""

    def __init__(self, data: list, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def json(self) -> list:
        return self._data

    def raise_for_status(self) -> None:
        pass


class MockHttpxClient:
    """Mock async httpx client that returns configured responses."""

    def __init__(self, data: Optional[list] = None):
        self._data = data or []

    async def __aenter__(self) -> "MockHttpxClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        pass

    async def get(self, *args: object, **kwargs: object) -> MockHttpxResponse:
        return MockHttpxResponse(self._data)

    async def post(self, *args: object, **kwargs: object) -> MockHttpxResponse:
        return MockHttpxResponse(self._data)

    async def patch(self, *args: object, **kwargs: object) -> MockHttpxResponse:
        return MockHttpxResponse(self._data)

    async def delete(self, *args: object, **kwargs: object) -> MockHttpxResponse:
        return MockHttpxResponse(self._data)


@pytest.fixture
def mock_supabase(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Provide a mocked async httpx client for Supabase REST calls."""
    mock_fn = MagicMock()
    monkeypatch.setattr("app.crud.get_client", mock_fn)
    return mock_fn


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


SAMPLE_EMPREENDIMENTO: dict = {
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
