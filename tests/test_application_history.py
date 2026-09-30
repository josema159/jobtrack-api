from tests.helpers import create_authenticated_user

def test_application_creates_initial_status_history(client,auth_headers):

    create_response = client.post(
        "/applications/",
        json={
            "company": "Spotify",
            "position": "Backend Developer",
            "status": "applied"
        },
        headers=auth_headers
    )

    application_id = create_response.json()["id"]

    response = client.get(
        f"/applications/{application_id}/history",
        headers=auth_headers
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["from_status"] is None
    assert history[0]["to_status"] == "applied"    

def test_patch_status_creates_history(client,auth_headers):

    create_response = client.post(
        "/applications/",
        json={
            "company": "Microsoft",
            "position": "Software Engineer",
            "status": "applied"
        },
        headers=auth_headers
    )

    application_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/applications/{application_id}",
        json={
            "status": "interview"
        },
        headers=auth_headers
    )

    assert patch_response.status_code == 200

    response = client.get(
        f"/applications/{application_id}/history",
        headers=auth_headers
    )

    history = response.json()

    assert len(history) == 2

    assert history[0]["from_status"] is None
    assert history[0]["to_status"] == "applied"

    assert history[1]["from_status"] == "applied"
    assert history[1]["to_status"] == "interview"

def test_patch_without_status_does_not_create_history(client,auth_headers):

    create_response = client.post(
        "/applications/",
        json={
            "company": "Amazon",
            "position": "Cloud Engineer",
            "status": "applied"
        },
        headers=auth_headers
    )

    application_id = create_response.json()["id"]

    client.patch(
        f"/applications/{application_id}",
        json={
            "notes": "Technical interview next week"
        },
        headers=auth_headers
    )

    response = client.get(
        f"/applications/{application_id}/history",
        headers=auth_headers
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