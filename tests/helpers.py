def create_user(
    client,
    email="user@example.com",
    password="Password123"
):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )


def login_user(
    client,
    email="user@example.com",
    password="Password123"
):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def create_authenticated_user(
    client,
    email="user@example.com",
    password="Password123"
):
    create_user(
        client,
        email,
        password
    )

    return login_user(
        client,
        email,
        password
    )