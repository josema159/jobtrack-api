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

def test_create_application(client):
    headers = create_authenticated_user(client)

    response = client.post(
        "/applications/",
        json={
            "company": "Spotify",
            "position": "Backend Developer",
            "country": "Sweden",
            "status": "applied",
            "job_url": "https://example.com/job",
            "notes": "Test application"
        },
        headers=headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["company"] == "Spotify"
    assert data["position"] == "Backend Developer"
    assert data["status"] == "applied"
    assert data["id"] == 1

def test_get_application(client):
    headers = create_authenticated_user(client)

    create_response = client.post(
        "/applications/",
        json={
            "company": "Microsoft",
            "position": "Software Engineer",
            "country": "Ireland",
            "status": "interview"
        },
        headers=headers
    )

    application_id = create_response.json()["id"]

    response = client.get(
        f"/applications/{application_id}",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == application_id
    assert data["company"] == "Microsoft"

def test_get_application_not_found(client):
    headers = create_authenticated_user(client)

    response = client.get(
        "/applications/999",
        headers=headers
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Application not found"
    }

def test_patch_application(client):
    headers = create_authenticated_user(client)

    create_response = client.post(
        "/applications/",
        json={
            "company": "Amazon",
            "position": "Cloud Engineer",
            "country": "Germany",
            "status": "applied"
        },
        headers=headers
    )

    application_id = create_response.json()["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={
            "status": "interview"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "interview"

    # PATCH no debe modificar los demás campos.
    assert data["company"] == "Amazon"
    assert data["position"] == "Cloud Engineer"
    assert data["country"] == "Germany"

def test_delete_application(client):
    headers = create_authenticated_user(client)

    create_response = client.post(
        "/applications/",
        json={
            "company": "SAP",
            "position": "Backend Engineer",
            "country": "Germany",
            "status": "applied"
        },
        headers=headers
    )

    application_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/applications/{application_id}",
        headers=headers
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/applications/{application_id}",
        headers=headers
    )

    assert get_response.status_code == 404

def test_application_pagination(client):
    headers = create_authenticated_user(client)

    companies = [
        "Spotify",
        "Microsoft",
        "Amazon"
    ]

    for company in companies:
        response = client.post(
            "/applications/",
            json={
                "company": company,
                "position": "Software Engineer",
                "status": "applied"
            },
            headers=headers
        )

        assert response.status_code == 201

    response = client.get(
        "/applications/?page=1&limit=2",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["metadata"]["page"] == 1
    assert data["metadata"]["limit"] == 2
    assert data["metadata"]["total"] == 3
    assert data["metadata"]["total_pages"] == 2
    assert data["metadata"]["has_next"] is True
    assert data["metadata"]["has_previous"] is False

    assert len(data["items"]) == 2

def test_user_cannot_access_another_users_application(client):
    # Usuario A
    user_a_headers = create_authenticated_user(
        client,
        email="usera@example.com"
    )

    # Usuario A crea una postulación.
    create_response = client.post(
        "/applications/",
        json={
            "company": "Spotify",
            "position": "Backend Developer",
            "country": "Sweden",
            "status": "applied"
        },
        headers=user_a_headers
    )

    assert create_response.status_code == 201

    application_id = create_response.json()["id"]

    # Usuario B
    user_b_headers = create_authenticated_user(
        client,
        email="userb@example.com"
    )

    # Usuario B intenta consultar la postulación de A.
    response = client.get(
        f"/applications/{application_id}",
        headers=user_b_headers
    )

    assert response.status_code == 404    

def test_application_requires_authentication(client):
    response = client.get(
        "/applications/"
    )

    assert response.status_code == 401    

def test_statistics(client):
    headers = create_authenticated_user(client)

    applications = [
        {
            "company": "Spotify",
            "position": "Backend Developer",
            "status": "applied"
        },
        {
            "company": "Microsoft",
            "position": "Software Engineer",
            "status": "applied"
        },
        {
            "company": "Amazon",
            "position": "Cloud Engineer",
            "status": "interview"
        },
        {
            "company": "Google",
            "position": "Backend Engineer",
            "status": "offer"
        }
    ]

    for application in applications:
        response = client.post(
            "/applications/",
            json=application,
            headers=headers
        )

        assert response.status_code == 201

    response = client.get(
        "/statistics/",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 4

    assert data["by_status"]["interested"] == 0
    assert data["by_status"]["applied"] == 2
    assert data["by_status"]["interview"] == 1
    assert data["by_status"]["offer"] == 1
    assert data["by_status"]["rejected"] == 0

    assert data["interview_rate"] == 25.0
    assert data["offer_rate"] == 25.0    

def test_statistics_only_include_current_user_applications(client):
    user_a_headers = create_authenticated_user(
        client,
        email="usera@example.com"
    )

    user_b_headers = create_authenticated_user(
        client,
        email="userb@example.com"
    )

    # Usuario A: 2 aplicaciones
    client.post(
        "/applications/",
        json={
            "company": "Spotify",
            "position": "Backend Developer",
            "status": "applied"
        },
        headers=user_a_headers
    )

    client.post(
        "/applications/",
        json={
            "company": "Microsoft",
            "position": "Software Engineer",
            "status": "interview"
        },
        headers=user_a_headers
    )

    # Usuario B: 1 aplicación
    client.post(
        "/applications/",
        json={
            "company": "Amazon",
            "position": "Cloud Engineer",
            "status": "rejected"
        },
        headers=user_b_headers
    )

    response = client.get(
        "/statistics/",
        headers=user_a_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["by_status"]["applied"] == 1
    assert data["by_status"]["interview"] == 1
    assert data["by_status"]["rejected"] == 0    

def test_statistics_with_no_applications(client):
    headers = create_authenticated_user(client)

    response = client.get(
        "/statistics/",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["interview_rate"] == 0
    assert data["offer_rate"] == 0

    assert data["by_status"] == {
        "interested": 0,
        "applied": 0,
        "interview": 0,
        "offer": 0,
        "rejected": 0
    }    

def test_application_creates_initial_status_history(client):
    headers = create_authenticated_user(client)

    create_response = client.post(
        "/applications/",
        json={
            "company": "Spotify",
            "position": "Backend Developer",
            "status": "applied"
        },
        headers=headers
    )

    application_id = create_response.json()["id"]

    response = client.get(
        f"/applications/{application_id}/history",
        headers=headers
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["from_status"] is None
    assert history[0]["to_status"] == "applied"    

def test_patch_status_creates_history(client):
    headers = create_authenticated_user(client)

    create_response = client.post(
        "/applications/",
        json={
            "company": "Microsoft",
            "position": "Software Engineer",
            "status": "applied"
        },
        headers=headers
    )

    application_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/applications/{application_id}",
        json={
            "status": "interview"
        },
        headers=headers
    )

    assert patch_response.status_code == 200

    response = client.get(
        f"/applications/{application_id}/history",
        headers=headers
    )

    history = response.json()

    assert len(history) == 2

    assert history[0]["from_status"] is None
    assert history[0]["to_status"] == "applied"

    assert history[1]["from_status"] == "applied"
    assert history[1]["to_status"] == "interview"

def test_patch_without_status_does_not_create_history(client):
    headers = create_authenticated_user(client)

    create_response = client.post(
        "/applications/",
        json={
            "company": "Amazon",
            "position": "Cloud Engineer",
            "status": "applied"
        },
        headers=headers
    )

    application_id = create_response.json()["id"]

    client.patch(
        f"/applications/{application_id}",
        json={
            "notes": "Technical interview next week"
        },
        headers=headers
    )

    response = client.get(
        f"/applications/{application_id}/history",
        headers=headers
    )

    history = response.json()

    assert len(history) == 1
    assert history[0]["to_status"] == "applied"

def test_user_cannot_access_another_users_history(client):
    user_a_headers = create_authenticated_user(
        client,
        email="usera@example.com"
    )

    create_response = client.post(
        "/applications/",
        json={
            "company": "Google",
            "position": "Backend Engineer",
            "status": "interested"
        },
        headers=user_a_headers
    )

    application_id = create_response.json()["id"]

    user_b_headers = create_authenticated_user(
        client,
        email="userb@example.com"
    )

    response = client.get(
        f"/applications/{application_id}/history",
        headers=user_b_headers
    )

    assert response.status_code == 404        