# Event Management — Docker, Tests, API

## Installing using GitHub
```
git clone https://github.com/Paul-Starodub/event_management
cd event_management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Stack: Django 6, DRF, JWT (SimpleJWT), Postgres, Redis, Celery.  
Seed data: created automatically on `web` startup (3 users and 5 events).

### Requirements
- `.env` file (Open file .env.sample and change environment variables to yours. Also rename file extension to .env)

## Run and stop via Docker

### Start services
```bash
docker compose up --build
```

On `web` start:
- DB migrations;
- `seed_simple` runs (current configuration runs it every start — events will be added);
- dev server at `http://localhost:8000/`.


### Stop and remove containers
```bash
docker compose down
```

## Tests (via Docker)
```bash
docker compose exec web python manage.py test
```

## Access
- Admin: `http://localhost:8000/admin/`
- Superuser: `user1` / `password123`

## API Docs
- Swagger UI: `http://localhost:8000/api/doc/swagger/`
- Redoc: `http://localhost:8000/api/doc/redoc/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Endpoints and examples
Base URL: `http://localhost:8000`

### Users and authentication
- Register user (public)
  - POST `/api/users/`
  - Body:
    ```json
    {"username": "new_user", "email": "new_user@example.com", "password": "strongpassword"}
    ```
  - Example:
    ```bash
    curl -X POST http://localhost:8000/api/users/ \
      -H "Content-Type: application/json" \
      -d '{"username":"new_user","email":"new_user@example.com","password":"strongpassword"}'
    ```

- Login (get JWT)
  - POST `/api/users/login/`
  - Body:
    ```json
    {"username":"user1","password":"password123"}
    ```
  - Example:
    ```bash
    curl -X POST http://localhost:8000/api/users/login/ \
      -H "Content-Type: application/json" \
      -d '{"username":"user1","password":"password123"}'
    ```
  - Response contains `access` and `refresh`.

- Refresh token
  - POST `/api/users/token/refresh/`
    ```bash
    curl -X POST http://localhost:8000/api/users/token/refresh/ \
      -H "Content-Type: application/json" \
      -d '{"refresh":"<REFRESH_TOKEN>"}'
    ```

- Verify token
  - POST `/api/users/token/verify/`

- Logout (blacklist refresh)
  - POST `/api/users/logout/`
    ```bash
    curl -X POST http://localhost:8000/api/users/logout/ \
      -H "Content-Type: application/json" \
      -d '{"refresh":"<REFRESH_TOKEN>"}'
    ```

- Current user (requires Bearer token)
  - GET `/api/users/me/`
    ```bash
    curl http://localhost:8000/api/users/me/ \
      -H "Authorization: Bearer <ACCESS_TOKEN>"
    ```
  - PATCH `/api/users/me/` — partial update

- Users list (short fields)
  - GET `/api/users/all/`

### Events
Router: `/api/events/` (ModelViewSet). By default requires authentication (see `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES`).

- List events (JWT required)
  - GET `/api/events/`
    ```bash
    curl http://localhost:8000/api/events/ \
      -H "Authorization: Bearer <ACCESS_TOKEN>"
    ```

- Create event (organizer = current user)
  - POST `/api/events/`
  - Body:
    ```json
    {
      "title": "Conf 2025",
      "description": "Annual conf",
      "date": "2025-12-31T10:00:00Z",
      "location": "NYC"
    }
    ```
  - Example:
    ```bash
    curl -X POST http://localhost:8000/api/events/ \
      -H "Authorization: Bearer <ACCESS_TOKEN>" \
      -H "Content-Type: application/json" \
      -d '{"title":"Conf 2025","description":"Annual conf","date":"2025-12-31T10:00:00Z","location":"NYC"}'
    ```

- Retrieve/update/delete event
  - GET `/api/events/{id}/`
  - PATCH/PUT/DELETE `/api/events/{id}/`

- Register participants
  - POST `/api/events/{id}/register/`
  - Body:
    ```json
    {"participant_ids": [2, 3, 4]}
    ```
  - Example:
    ```bash
    curl -X POST http://localhost:8000/api/events/1/register/ \
      -H "Authorization: Bearer <ACCESS_TOKEN>" \
      -H "Content-Type: application/json" \
      -d '{"participant_ids":[2,3,4]}'
    ```
  - Celery email task is queued in background (if `celery` is running).

- Unregister participants
  - POST `/api/events/{id}/unregister/`
  - Body:
    ```json
    {"participant_ids": [2, 3]}
    ```

- Event participants list
  - GET `/api/events/{id}/participants/`

## Celery
Registration endpoint (`/api/events/{id}/register/`) queues `send_registration_email`.

## Tips & troubleshooting
- In the current configuration, the seeder runs on every `web` start and adds new events (dates shift). This is intentional for demo.


