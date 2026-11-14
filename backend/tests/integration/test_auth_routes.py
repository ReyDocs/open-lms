import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_dev_login_and_me(client):
    login_resp = await client.post(
        "/api/v1/auth/dev-login",
        json={
            "email": "teacher.alice@openlms.edu",
            "role": "teacher",
            "full_name": "Alice Teacher",
        },
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["user"]["role"] == "teacher"

    # Test /auth/me
    token = token_data["access_token"]
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    user = me_resp.json()
    assert user["email"] == "teacher.alice@openlms.edu"
    assert user["role"] == "teacher"


@pytest.mark.asyncio
async def test_refresh_token(client):
    login_resp = await client.post(
        "/api/v1/auth/dev-login",
        json={"email": "student.bob@openlms.edu", "role": "student"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert "access_token" in new_tokens
    assert new_tokens["refresh_token"] != refresh_token
