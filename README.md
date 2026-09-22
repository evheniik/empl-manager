# Empl Manager — Companies / Employees / Projects

Тестове завдання (Python Developer): менеджер компаній — REST API з CRUD для
компаній, працівників і проєктів + React-фронтенд. Мутації (Create/Update/Delete)
доступні тільки автентифікованим користувачам (OAuth2 password flow + JWT).

## Стек

- **Backend:** Python 3.14, FastAPI, SQLAlchemy 2.0 (sync), Alembic, psycopg3, PostgreSQL 16
- **Auth:** OAuth2 password flow + JWT (`pwdlib` + `pyjwt`, без passlib). Токен
  кладеться в **httpOnly cookie** (`access_token`); Bearer-заголовок теж
  підтримується для API/Swagger.
- **Frontend:** Vite + React (без UI-бібліотек і state-менеджерів, `fetch`)
- **Пакетний менеджер:** `uv` (backend), `npm` (frontend)
- **Deploy:** Docker Compose — весь застосунок на порту **8080**

## Quickstart (Docker)

```bash
cp .env.example .env   # за потреби змінити SECRET_KEY / паролі
docker compose up --build
```

- UI: http://localhost:8080
- API: http://localhost:8080/api/v1/companies
- Swagger: http://localhost:8080/docs
- Health: http://localhost:8080/health

Логін адміністратора (створюється сидером автоматично):

| Поле     | Значення            |
|----------|---------------------|
| Email    | `admin@example.com` |
| Password | `admin123`          |

Backend-контейнер при старті сам виконує `alembic upgrade head` і сидер
(видно в `docker logs empl_manager-backend-1`).

## API (контракт)

Префікс: `/api/v1`.

| Метод | Шлях | Auth | Опис |
|-------|------|------|------|
| GET | `/health` | — | Health check (без префікса) |
| POST | `/api/v1/auth/login` | — | OAuth2 form (`username`=email, `password`) → `{access_token, token_type}` + httpOnly cookie |
| POST | `/api/v1/auth/logout` | — | Очищує auth-cookie |
| GET | `/api/v1/auth/me` | ✓ | Поточний користувач (з cookie або Bearer) |
| GET | `/api/v1/companies?skip=&limit=` | — | Список компаній |
| GET | `/api/v1/companies/{id}` | — | Компанія з вкладеними `employees` і `projects` |
| POST / PUT / DELETE | `/api/v1/companies[/{id}]` | ✓ | CRUD-мутації |
| GET | `/api/v1/employees?company_id=&skip=&limit=` | — | Список працівників (фільтр за компанією) |
| GET | `/api/v1/employees/{id}` | — | Працівник |
| POST / PUT / DELETE | `/api/v1/employees[/{id}]` | ✓ | CRUD-мутації |
| GET | `/api/v1/projects?company_id=&skip=&limit=` | — | Список проєктів (фільтр за компанією) |
| GET | `/api/v1/projects/{id}` | — | Проєкт |
| POST / PUT / DELETE | `/api/v1/projects[/{id}]` | ✓ | CRUD-мутації |

Помилки: `404` — сутності немає, `401` — немає/невалідний токен,
`409` — дублікат email працівника.

Приклад:

```bash
# Логін: токен у httpOnly cookie + у тілі відповіді
curl -c /tmp/cookies -X POST http://localhost:8080/api/v1/auth/login \
  -d "username=admin@example.com&password=admin123"
# → {"access_token":"...","token_type":"bearer"}

# Публічний список
curl http://localhost:8080/api/v1/companies

# Мутація з cookie-авторизацією
curl -c /tmp/cookies -X POST http://localhost:8080/api/v1/auth/login \
  -d "username=admin@example.com&password=admin123"
curl -b /tmp/cookies -X POST http://localhost:8080/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme","description":"...","website":"https://acme.example"}'
```

## Локальна розробка

### Backend

```bash
# 1. Postgres (тимчасовий контейнер для dev)
docker run -d --name empl_pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=empl_manager \
  -p 5432:5432 postgres:16

# 2. Залежності та env
cd backend
uv sync
cp ../.env.example .env   # або ../.env — DATABASE_URL вже вказує на localhost

# 3. Міграції + сидер
uv run alembic upgrade head
uv run python -m app.db.seed

# 4. Запуск API
uv run uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173 (API проксується на localhost:8000)
```

Залогініться admin-креденшелами з Quickstart — з'являться кнопки
створення/редагування/видалення. Без логіну списки видно, мутації сховані.

### Тести

```bash
cd backend
uv run pytest -v
```

Тести використовують окрему БД `empl_manager_test` на тому ж Postgres
(створюється автоматично) і не чіпають основну БД. Має бути зелено: 33 тести
(auth + CRUD companies/employees/projects, 404/401/409, фільтри `company_id`).

## Env-змінні

Див. `.env.example` (повний список, скопіюйте в `.env`):

| Змінна | Default | Опис |
|--------|---------|------|
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/empl_manager` | Рядок підключення до БД (у compose перевизначається на хост `db`) |
| `SECRET_KEY` | `change-me-please-use-at-least-32-bytes-long` | Ключ підпису JWT — **змінити в продакшені** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Час життя токена |
| `ADMIN_EMAIL` | `admin@example.com` | Email admin-користувача (сидер) |
| `ADMIN_PASSWORD` | `admin123` | Пароль admin-користувача (сидер) |
| `COOKIE_SECURE` | `false` | `Secure` атрибут auth-cookie (true на HTTPS) |
| `POSTGRES_USER` | `postgres` | Юзер Postgres (сервіс `db` у compose) |
| `POSTGRES_PASSWORD` | `postgres` | Пароль Postgres (сервіс `db`) |
| `POSTGRES_DB` | `empl_manager` | Ім'я БД (сервіс `db`) |

## Структура проєкту

```
.
├── docker-compose.yml      # db (postgres:16) + backend + frontend (nginx на 8080)
├── .env.example            # усі env-змінні з дефолтами
├── backend/
│   ├── Dockerfile          # python:3.14-slim + uv
│   ├── entrypoint.sh       # wait-for-db → alembic upgrade head → seed → uvicorn
│   ├── alembic/            # міграції (alembic.ini поруч)
│   └── app/
│       ├── main.py         # FastAPI app, CORS, /health, router /api/v1
│       ├── api/
│       │   ├── router.py   # агрегуючий APIRouter
│       │   ├── deps.py     # get_current_user, oauth2_scheme
│       │   └── routes/     # auth.py, companies.py, employees.py, projects.py
│       ├── core/           # config.py (Settings), security.py (pwdlib + pyjwt)
│       ├── db/             # base.py, session.py, seed.py
│       ├── models/         # company.py, employee.py, project.py, user.py
│       ├── schemas/        # Pydantic v2-схеми (Create/Update/Read)
│       ├── services/       # бізнес-логіка (валідації, 404/409)
│       └── crud/           # чистий шар доступу до БД
│   └── tests/              # pytest: conftest + test_auth/companies/employees/projects
└── frontend/
    ├── Dockerfile          # multi-stage: node:22 build → nginx:alpine
    ├── nginx.conf          # статика + proxy /api/, /health, /docs, /openapi.json
    └── src/
        ├── api.js          # fetch-обгортка: credentials include, обробка помилок
        ├── AuthContext.jsx # login/logout, токен у стані
        ├── App.jsx         # роутер + навігація
        └── pages/          # LoginPage, CompaniesPage, EmployeesPage, ProjectsPage
```

## Модель даних

- `Company` 1:N `Employee` (`company_id`, `ondelete="CASCADE"`,
  `cascade="all, delete-orphan"`) — видалення компанії видаляє її
  працівників і проєкти.
- `Company` 1:N `Project` — аналогічно.
- `Employee.email` — unique (дублікат → `409`).
- PK скрізь — UUID (`uuid4`, генерується застосунком).
