from tests.helpers import create_authenticated_user

def test_statistics(client,auth_headers):

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
            headers=auth_headers
        )

        assert response.status_code == 201

    response = client.get(
        "/statistics/",
        headers=auth_headers
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

def test_statistics_with_no_applications(client,auth_headers):

    response = client.get(
        "/statistics/",
        headers=auth_headers
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
