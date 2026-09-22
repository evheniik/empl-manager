# Empl Manager — Companies / Employees / Projects

Python Developer test task: a company manager — REST API with CRUD for
companies, employees, and projects + a React frontend. Mutations
(Create/Update/Delete) are available only to authenticated users
(OAuth2 password flow + JWT).

## Stack

- **Backend:** Python 3.14, FastAPI, SQLAlchemy 2.0 (sync), Alembic, psycopg3, PostgreSQL 16
- **Auth:** OAuth2 password flow + JWT (`pwdlib` + `pyjwt`, no passlib). The token
  is stored in an **httpOnly cookie** (`access_token`); the Bearer header is also
  supported for API/Swagger usage.
- **Frontend:** Vite + React (no UI libraries or state managers, plain `fetch`)
- **Package managers:** `uv` (backend), `npm` (frontend)
- **Deploy:** Docker Compose — the whole app on port **8080**

## Quickstart (Docker)

```bash
cp .env.example .env   # change SECRET_KEY / passwords if needed
docker compose up --build
```

- UI: http://localhost:8080
- API: http://localhost:8080/api/v1/companies
- Swagger: http://localhost:8080/docs
- Health: http://localhost:8080/health

Admin login (created automatically by the seeder):

| Field    | Value               |
|----------|---------------------|
| Email    | `admin@example.com` |
| Password | `admin123`          |

On startup the backend container runs `alembic upgrade head` and the seeder
itself (see `docker logs empl_manager-backend-1`).

## API (contract)

Prefix: `/api/v1`.

| Method | Path | Auth | Description |
|-------|------|------|------|
| GET | `/health` | — | Health check (no prefix) |
| POST | `/api/v1/auth/login` | — | OAuth2 form (`username`=email, `password`) → `{access_token, token_type}` + httpOnly cookie |
| POST | `/api/v1/auth/logout` | — | Clears the auth cookie |
| GET | `/api/v1/auth/me` | ✓ | Current user (from cookie or Bearer) |
| GET | `/api/v1/companies?skip=&limit=` | — | List companies |
| GET | `/api/v1/companies/{id}` | — | Company with nested `employees` and `projects` |
| POST / PUT / DELETE | `/api/v1/companies[/{id}]` | ✓ | CRUD mutations |
| GET | `/api/v1/employees?company_id=&skip=&limit=` | — | List employees (filter by company) |
| GET | `/api/v1/employees/{id}` | — | Single employee |
| POST / PUT / DELETE | `/api/v1/employees[/{id}]` | ✓ | CRUD mutations |
| GET | `/api/v1/projects?company_id=&skip=&limit=` | — | List projects (filter by company) |
| GET | `/api/v1/projects/{id}` | — | Single project |
| POST / PUT / DELETE | `/api/v1/projects[/{id}]` | ✓ | CRUD mutations |

Errors: `404` — entity not found, `401` — missing/invalid token,
`409` — duplicate employee email.

Example:

```bash
# Login: token in httpOnly cookie + response body
curl -c /tmp/cookies -X POST http://localhost:8080/api/v1/auth/login \
  -d "username=admin@example.com&password=admin123"
# → {"access_token":"...","token_type":"bearer"}

# Public list
curl http://localhost:8080/api/v1/companies

# Mutation with cookie auth
curl -c /tmp/cookies -X POST http://localhost:8080/api/v1/auth/login \
  -d "username=admin@example.com&password=admin123"
curl -b /tmp/cookies -X POST http://localhost:8080/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme","description":"...","website":"https://acme.example"}'
```

## Local development

### Backend

```bash
# 1. Postgres (temporary dev container)
docker run -d --name empl_pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=empl_manager \
  -p 5432:5432 postgres:16

# 2. Dependencies and env
cd backend
uv sync
cp ../.env.example .env   # or ../.env — DATABASE_URL already points to localhost

# 3. Migrations + seeder
uv run alembic upgrade head
uv run python -m app.db.seed

# 4. Run the API
uv run uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173 (API proxied to localhost:8000)
```

Log in with the admin credentials from Quickstart — create/edit/delete buttons
will appear. Without login, lists are visible but mutations are hidden.

### Tests

```bash
cd backend
uv run pytest -v
```

Tests use a separate `empl_manager_test` database on the same Postgres
(created automatically) and do not touch the main DB. Expect green: 33 tests
(auth + CRUD companies/employees/projects, 404/401/409, `company_id` filters).

## Environment variables

See `.env.example` (full list, copy it to `.env`):

| Variable | Default | Description |
|--------|---------|------|
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/empl_manager` | DB connection string (overridden to host `db` in compose) |
| `SECRET_KEY` | `change-me-please-use-at-least-32-bytes-long` | JWT signing key — **change in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime |
| `ADMIN_EMAIL` | `admin@example.com` | Admin user email (seeder) |
| `ADMIN_PASSWORD` | `admin123` | Admin user password (seeder) |
| `COOKIE_SECURE` | `false` | `Secure` attribute of the auth cookie (true on HTTPS) |
| `POSTGRES_USER` | `postgres` | Postgres user (compose `db` service) |
| `POSTGRES_PASSWORD` | `postgres` | Postgres password (compose `db` service) |
| `POSTGRES_DB` | `empl_manager` | DB name (compose `db` service) |

## Project structure

```
.
├── docker-compose.yml      # db (postgres:16) + backend + frontend (nginx on 8080)
├── .env.example            # all env vars with defaults
├── backend/
│   ├── Dockerfile          # python:3.14-slim + uv
│   ├── entrypoint.sh       # wait-for-db → alembic upgrade head → seed → uvicorn
│   ├── alembic/            # migrations (alembic.ini next to it)
│   └── app/
│       ├── main.py         # FastAPI app, CORS, /health, router /api/v1
│       ├── api/
│       │   ├── router.py   # aggregating APIRouter
│       │   ├── deps.py     # get_current_user, oauth2_scheme
│       │   └── routes/     # auth.py, companies.py, employees.py, projects.py
│       ├── core/           # config.py (Settings), security.py (pwdlib + pyjwt)
│       ├── db/             # base.py, session.py, seed.py
│       ├── models/         # company.py, employee.py, project.py, user.py
│       ├── schemas/        # Pydantic v2 schemas (Create/Update/Read)
│       ├── services/       # business logic (validations, 404/409)
│       └── crud/           # pure DB access layer
│   └── tests/              # pytest: conftest + test_auth/companies/employees/projects
└── frontend/
    ├── Dockerfile          # multi-stage: node:22 build → nginx:alpine
    ├── nginx.conf          # static + proxy /api/, /health, /docs, /openapi.json
    └── src/
        ├── api.js          # fetch wrapper: credentials include, error handling
        ├── AuthContext.jsx # login/logout, token in state
        ├── App.jsx         # router + navigation
        └── pages/          # LoginPage, CompaniesPage, EmployeesPage, ProjectsPage
```

## Data model

- `Company` 1:N `Employee` (`company_id`, `ondelete="CASCADE"`,
  `cascade="all, delete-orphan"`) — deleting a company deletes its
  employees and projects.
- `Company` 1:N `Project` — same as above.
- `Employee.email` — unique (duplicate → `409`).
- PKs everywhere — UUID (`uuid4`, generated by the app).
