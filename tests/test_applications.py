def test_create_application(client):
    response = client.post(
        "/applications/",
        json={
            "company": "Spotify",
            "position": "Backend Developer",
            "country": "Sweden",
            "status": "applied",
            "job_url": "https://example.com/job",
            "notes": "Test application"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["company"] == "Spotify"
    assert data["position"] == "Backend Developer"
    assert data["status"] == "applied"
    assert data["id"] == 1

def test_get_application(client):
    create_response = client.post(
        "/applications/",
        json={
            "company": "Microsoft",
            "position": "Software Engineer",
            "country": "Ireland",
            "status": "interview"
        }
    )

    application_id = create_response.json()["id"]

    response = client.get(
        f"/applications/{application_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == application_id
    assert data["company"] == "Microsoft"

def test_get_application_not_found(client):
    response = client.get(
        "/applications/999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Application not found"
    }

def test_patch_application(client):
    create_response = client.post(
        "/applications/",
        json={
            "company": "Amazon",
            "position": "Cloud Engineer",
            "country": "Germany",
            "status": "applied"
        }
    )

    application_id = create_response.json()["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={
            "status": "interview"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "interview"

    # Los demás datos deben mantenerse
    assert data["company"] == "Amazon"
    assert data["country"] == "Germany"

def test_delete_application(client):
    create_response = client.post(
        "/applications/",
        json={
            "company": "SAP",
            "position": "Backend Engineer",
            "country": "Germany",
            "status": "applied"
        }
    )

    application_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/applications/{application_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/applications/{application_id}"
    )

    assert get_response.status_code == 404    

def test_application_pagination(client):

    companies = [
        "Spotify",
        "Microsoft",
        "Amazon"
    ]

    for company in companies:
        client.post(
            "/applications/",
            json={
                "company": company,
                "position": "Software Engineer",
                "status": "applied"
            }
        )

    response = client.get(
        "/applications/?page=1&limit=2"
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