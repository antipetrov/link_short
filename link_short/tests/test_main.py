import pytest


@pytest.mark.asyncio
async def test_get_code_200(client, short_code_in_db):
    existing_code, existing_url, code_id = short_code_in_db
    response = await client.get(f"/urls/{existing_code}")

    assert response.status_code == 200
    assert response.json()['url'] == existing_url


@pytest.mark.asyncio
async def test_get_code_stats(client, short_code_in_db, short_code_stat_in_db):
    existing_code, existing_url, code_id = short_code_in_db
    response = await client.get(f"/urls/{existing_code}/stats")

    assert response.status_code == 200
    assert response.json()['count'] == 1

    await client.get(f"/urls/{existing_code}")

    response = await client.get(f"/urls/{existing_code}/stats")
    assert response.json()['count'] == 2


@pytest.mark.asyncio
async def test_get_code_stats_yesterday(client, short_code_in_db, short_code_stat_in_db_yesterday):
    existing_code, existing_url, code_id = short_code_in_db
    response = await client.get(f"/urls/{existing_code}/stats")

    assert response.status_code == 200
    assert response.json()['count'] == 0

    await client.get(f"/urls/{existing_code}")

    response = await client.get(f"/urls/{existing_code}/stats")
    assert response.json()['count'] == 1


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
    existing_code, existing_url, code_id = short_code_in_db
    new_url = 'https://test2.com'
    response = await client.put(f"/urls/{existing_code}", json={'url': new_url})
    assert response.status_code == 200
    assert response.json()['updated'] == True

    response = await client.get(f"/urls/{existing_code}")
    response.json()['url'] == new_url


@pytest.mark.asyncio
async def test_delete_code(client, short_code_in_db):
    existing_code, existing_url, code_id = short_code_in_db
    response = await client.get(f"/urls/{existing_code}")
    assert response.status_code == 200

    response = await client.delete(f"/urls/{existing_code}")
    assert response.status_code == 200
    assert response.json()['deleted'] == True

    response = await client.get(f"/urls/{existing_code}")
    assert response.status_code == 404
