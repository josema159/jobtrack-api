from tests.helpers import create_user, login_user


def test_register_user(client):
    response = create_user(client)

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "user@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    create_user(client)

    response = create_user(client)

    assert response.status_code == 409


def test_login(client):
    create_user(client)

    response = client.post(
        "/auth/login",
        data={
            "username": "user@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_password(client):
    create_user(client)

    response = client.post(
        "/auth/login",
        data={
            "username": "user@example.com",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401


def test_get_me(client):
    create_user(client)

    headers = login_user(client)

    response = client.get(
        "/auth/me",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"