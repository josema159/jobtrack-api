# JobTrack API

JobTrack is a REST API built with Python and FastAPI for tracking and analyzing job applications.

The project allows users to create an account, authenticate using JWT, manage their own job applications, track application status changes, and view statistics about their job search.

The project was built as a backend-focused portfolio project with an emphasis on API design, authentication, database persistence, testing, containerization, and continuous integration.

---

## Features

### Authentication

- User registration
- User login
- Secure password hashing using Argon2
- JWT access tokens
- Bearer authentication
- Authenticated user endpoint (`/auth/me`)
- User data isolation

### Job Applications

Users can manage their own job applications through a complete REST API:

- Create applications
- List applications
- Retrieve an application by ID
- Update applications using PUT
- Partially update applications using PATCH
- Delete applications

Each application belongs to the authenticated user.

Users cannot access or modify applications owned by other users.

### Application Filtering

Applications can be filtered by:

- Status
- Country
- Company

Example:

```http
GET /applications/?status=interview&country=Germany
```

Company searches support partial case-insensitive matching.

Example:

```http
GET /applications/?company=soft
```

can match:

```text
Microsoft
```

### Pagination

Application results support pagination:

```http
GET /applications/?page=1&limit=10
```

Example response:

```json
{
  "metadata": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  },
  "items": []
}
```

### Application Status History

JobTrack stores the history of status changes for each application.

For example:

```text
interested
    ↓
applied
    ↓
interview
    ↓
offer
```

The history can be retrieved with:

```http
GET /applications/{application_id}/history
```

Example:

```json
[
  {
    "id": 1,
    "from_status": null,
    "to_status": "applied",
    "changed_at": "2026-09-30T10:00:00Z"
  },
  {
    "id": 2,
    "from_status": "applied",
    "to_status": "interview",
    "changed_at": "2026-10-03T15:30:00Z"
  }
]
```

### Statistics

Authenticated users can retrieve statistics about their applications.

```http
GET /statistics/
```

Example:

```json
{
  "total": 10,
  "by_status": {
    "interested": 1,
    "applied": 4,
    "interview": 2,
    "offer": 1,
    "rejected": 2
  },
  "interview_rate": 20.0,
  "offer_rate": 10.0
}
```

Statistics only include applications belonging to the authenticated user.

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

### Database

- PostgreSQL
- SQLAlchemy

### Database Migrations

- Alembic

### Authentication & Security

- JWT
- PyJWT
- OAuth2 Bearer authentication
- Argon2 password hashing
- pwdlib

### Testing

- Pytest
- FastAPI TestClient
- SQLite test database

### DevOps

- Docker
- Docker Compose
- GitHub Actions

---

## Project Structure

```text
jobtrack-api/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── app/
│   ├── routers/
│   │   ├── applications.py
│   │   ├── auth.py
│   │   └── statistics.py
│   │
│   ├── __init__.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
│
├── migrations/
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── helpers.py
│   ├── test_applications.py
│   ├── test_application_history.py
│   ├── test_auth.py
│   └── test_statistics.py
│
├── .dockerignore
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

After starting the application, Swagger UI is available at:

```text
http://localhost:8000/docs
```

OpenAPI documentation is also available at:

```text
http://localhost:8000/redoc
```

---

# Running the Project Locally

## Requirements

Make sure the following are installed:

- Python
- PostgreSQL
- Git

---

## 1. Clone the repository

```bash
git clone https://github.com/josema159/jobtrack-api.git
```

Enter the project directory:

```bash
cd jobtrack-api
```

---

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/jobtrack
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit the `.env` file.

---

## 5. Create the PostgreSQL database

Create a database named:

```text
jobtrack
```

Example using PostgreSQL:

```sql
CREATE DATABASE jobtrack;
```

---

## 6. Apply database migrations

```bash
alembic upgrade head
```

Alembic will create and update the required database structure.

---

## 7. Start the API

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Running with Docker

JobTrack can also run completely using Docker.

Docker Compose starts:

- FastAPI
- PostgreSQL
- Alembic migrations

Build and start the containers:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Docker uses a persistent PostgreSQL volume, so database data remains available after containers are stopped.

Stop the containers:

```bash
docker compose down
```

To also remove the PostgreSQL volume and all Docker database data:

```bash
docker compose down -v
```

---

# Authentication

## Register

```http
POST /auth/register
```

Example:

```json
{
  "email": "user@example.com",
  "password": "Password123"
}
```

---

## Login

```http
POST /auth/login
```

The login endpoint uses OAuth2 form fields:

```text
username = user@example.com
password = Password123
```

The API returns:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

---

## Authenticated Requests

Protected endpoints require:

```http
Authorization: Bearer JWT_TOKEN
```

Example:

```http
GET /applications/
Authorization: Bearer eyJ...
```

Swagger UI also supports authentication through the **Authorize** button.

---

# Application Statuses

Applications can have one of the following statuses:

```text
interested
applied
interview
offer
rejected
```

---

# Main Endpoints

## Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Applications

```text
POST   /applications/
GET    /applications/
GET    /applications/{application_id}
PUT    /applications/{application_id}
PATCH  /applications/{application_id}
DELETE /applications/{application_id}
```

## Application History

```text
GET /applications/{application_id}/history
```

## Statistics

```text
GET /statistics/
```

## System

```text
GET /
GET /health
```

---

# Testing

The project includes automated tests using Pytest.

Tests use an isolated SQLite database instead of the development PostgreSQL database.

Run the complete test suite:

```bash
pytest
```

The test suite covers areas including:

- User registration
- Authentication
- JWT-protected endpoints
- Application creation
- Application retrieval
- Application updates
- Partial updates
- Application deletion
- Pagination
- User data isolation
- Application status history
- Statistics
- Authorization requirements

---

# Continuous Integration

The repository uses GitHub Actions for Continuous Integration.

On every push or pull request to `main`, GitHub automatically:

1. Checks out the repository
2. Installs Python
3. Installs dependencies
4. Runs the automated test suite

This helps detect regressions before changes are integrated.

---

# Database Migrations

Database schema changes are managed with Alembic.

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "Migration description"
```

Review the generated migration before applying it.

Apply all pending migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Rollback one migration:

```bash
alembic downgrade -1
```

---

# Development Status

JobTrack is currently under active development.

Planned improvements include:

- Improved statistics using application status history
- Additional application analytics
- Refresh tokens
- Improved authentication lifecycle
- Additional test coverage
- Cloud deployment
- Production configuration
- API logging and monitoring

---

## Author

**Jose Gomez**

GitHub: [josema159](https://github.com/josema159)

---

## License

This project is currently intended for educational and portfolio purposes.