import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
from app.main import app


@pytest.fixture
def mock_groq_response():
    mock_choice = MagicMock()
    mock_choice.message.content = "def test_example():\n    assert 1 + 1 == 2\n"
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    return mock_completion


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_generate_valid_input(mock_groq_response):
    with patch("app.main.get_groq_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_groq_response
        mock_client_factory.return_value = mock_client
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/generate", json={"code": "def add(a, b):\n    return a + b"})
    assert response.status_code == 200
    assert "tests" in response.json()


@pytest.mark.asyncio
async def test_generate_empty_input():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/generate", json={"code": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_oversized_input():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/generate", json={"code": "x" * 2001})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_groq_error():
    with patch("app.main.get_groq_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API failure")
        mock_client_factory.return_value = mock_client
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/generate", json={"code": "def add(a, b):\n    return a + b"})
    assert response.status_code == 500
    assert "Groq API error" in response.json()["detail"]