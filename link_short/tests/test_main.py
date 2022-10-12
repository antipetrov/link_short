import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import databases

from config import get_settings
from main import app
from hash_creator import hash_creator
settings = get_settings()

@pytest.mark.asyncio
async def test_get_code_200(client, short_code_in_db):
    existing_code, existing_url = short_code_in_db
    response = await client.get(f"/urls/{existing_code}")

    assert response.status_code == 200
    assert response.json()['url'] == existing_url


@pytest.mark.asyncio
async def test_get_code_404(client):
    response = await client.get("/urls/abcd")
    assert response.status_code == 404
    assert response.json() == {"detail": "Code not found"}


@pytest.mark.asyncio
async def test_create_code(client):
    target_url = 'http://ya.ru'

    response = await client.post("/urls/", json={'url': target_url})
    assert response.status_code == 200
    code = response.json()['code']

    read_response = await client.get(f"/urls/{code}")
    assert read_response.status_code == 200
    assert read_response.json()['url'] == target_url


@pytest.mark.asyncio
async def test_update_code(client, short_code_in_db):
    existing_code, existing_url = short_code_in_db
    new_url = 'https://test2.com'
    response = await client.put(f"/urls/{existing_code}", json={'url': new_url})
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    response = await client.get(f"/urls/{existing_code}")
    response.json()['url'] == new_url


@pytest.mark.asyncio
async def test_delete_code(client, short_code_in_db):
    existing_code, existing_url = short_code_in_db
    response = await client.get(f"/urls/{existing_code}")
    assert response.status_code == 200

    response = await client.delete(f"/urls/{existing_code}")
    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}

    response = await client.get(f"/urls/{existing_code}")
    assert response.status_code == 404
