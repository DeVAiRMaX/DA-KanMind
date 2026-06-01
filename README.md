# KanMind Backend

Django REST Framework backend for the KanMind kanban application.

## Prerequisites

- Python 3.10+

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate      # macOS / Linux
   env\Scripts\activate         # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

The API is available at `http://127.0.0.1:8000/api/`.

## Admin

Create a superuser and open `http://127.0.0.1:8000/admin/`:

```bash
python manage.py createsuperuser
```

## Authentication

Token-based authentication. Register or log in to receive a token, then include it in every request:

```
Authorization: Token <your-token>
```

## API Endpoints

### Auth

| Method | Endpoint | Auth required |
|--------|----------|:---:|
| POST | `/api/registration/` | No |
| POST | `/api/login/` | No |
| GET | `/api/email-check/?email=<email>` | Yes |

### Boards

| Method | Endpoint | Auth required |
|--------|----------|:---:|
| GET, POST | `/api/boards/` | Yes |
| GET, PATCH, DELETE | `/api/boards/<id>/` | Yes |

### Tasks

| Method | Endpoint | Auth required |
|--------|----------|:---:|
| POST | `/api/tasks/` | Yes |
| GET, PATCH, DELETE | `/api/tasks/<id>/` | Yes |
| GET | `/api/tasks/assigned-to-me/` | Yes |
| GET | `/api/tasks/reviewing/` | Yes |

### Comments

| Method | Endpoint | Auth required |
|--------|----------|:---:|
| GET, POST | `/api/tasks/<task_id>/comments/` | Yes |
| DELETE | `/api/tasks/<task_id>/comments/<id>/` | Yes |
