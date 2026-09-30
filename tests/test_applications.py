from tests.helpers import create_authenticated_user

def test_create_application(client,auth_headers):
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
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["company"] == "Spotify"
    assert data["position"] == "Backend Developer"
    assert data["status"] == "applied"
    assert data["id"] == 1

def test_get_application(client,auth_headers):

    create_response = client.post(
        "/applications/",
        json={
            "company": "Microsoft",
            "position": "Software Engineer",
            "country": "Ireland",
            "status": "interview"
        },
        headers=auth_headers
    )

    application_id = create_response.json()["id"]

    response = client.get(
        f"/applications/{application_id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == application_id
    assert data["company"] == "Microsoft"

def test_get_application_not_found(client,auth_headers):
    
    response = client.get(
        "/applications/999",
        headers=auth_headers
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Application not found"
    }

def test_patch_application(client,auth_headers):

    create_response = client.post(
        "/applications/",
        json={
            "company": "Amazon",
            "position": "Cloud Engineer",
            "country": "Germany",
            "status": "applied"
        },
        headers=auth_headers
    )

    application_id = create_response.json()["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={
            "status": "interview"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "interview"

    # PATCH no debe modificar los demás campos.
    assert data["company"] == "Amazon"
    assert data["position"] == "Cloud Engineer"
    assert data["country"] == "Germany"

def test_delete_application(client,auth_headers):

    create_response = client.post(
        "/applications/",
        json={
            "company": "SAP",
            "position": "Backend Engineer",
            "country": "Germany",
            "status": "applied"
        },
        headers=auth_headers
    )

    application_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/applications/{application_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/applications/{application_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 404

def test_application_pagination(client,auth_headers):

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
            headers=auth_headers
        )

        assert response.status_code == 201

    response = client.get(
        "/applications/?page=1&limit=2",
        headers=auth_headers
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

def test_update_application(client, auth_headers):
    create_response = client.post(
        "/applications/",
        json={
            "company": "Spotify",
            "position": "Backend Developer",
            "country": "Sweden",
            "status": "applied",
            "notes": "Original notes"
        },
        headers=auth_headers
    )

    assert create_response.status_code == 201

    application_id = create_response.json()["id"]

    response = client.put(
        f"/applications/{application_id}",
        json={
            "company": "Spotify",
            "position": "Senior Backend Developer",
            "country": "Sweden",
            "status": "interview",
            "job_url": "https://example.com/job",
            "notes": "Technical interview scheduled"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == application_id
    assert data["company"] == "Spotify"
    assert data["position"] == "Senior Backend Developer"
    assert data["status"] == "interview"
    assert data["notes"] == "Technical interview scheduled"

    get_response = client.get(
        f"/applications/{application_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 200
    assert get_response.json()["status"] == "interview"