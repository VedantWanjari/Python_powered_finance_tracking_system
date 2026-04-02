# Python-Powered Finance Tracking System

A production-grade REST API backend for personal finance tracking, built with **Flask + MySQL + SQLAlchemy**.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | Flask 3.0 |
| ORM | SQLAlchemy 2.0 via Flask-SQLAlchemy |
| Database | MySQL 8.0 (PyMySQL driver) |
| Password hashing | bcrypt |
| Validation | Marshmallow 3 |
| Rate limiting | Flask-Limiter |
| Testing | pytest + SQLite in-memory |

---

## ⚡ Quick Start

### 1 — Clone and create a virtual environment
```bash
git clone <repo-url>
cd Python_powered_finance_tracking_system
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### 3 — Configure the environment
```bash
cp .env.example .env
# Edit .env and fill in your MySQL credentials and a secret key
```

### 4 — Create the MySQL database
```sql
CREATE DATABASE finance_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5 — Initialise the schema and seed defaults
```bash
python setup_db.py
```
This creates all tables, seeds 10 default categories, and creates an admin account:
- **username**: `admin`  **password**: `Admin@1234`

> ⚠️ Change the admin password after your first login!

### 6 — Start the server
```bash
python run.py
# or: flask run
```

Server runs at **http://localhost:5000**

---

## 🔑 First API Call

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@1234"}'

# Create a transaction (use the session cookie returned above)
curl -X POST http://localhost:5000/api/transactions/ \
  -H "Content-Type: application/json" \
  -b cookies.txt -c cookies.txt \
  -d '{
    "amount": 5000,
    "transaction_type": "income",
    "date": "2024-03-01",
    "description": "Monthly salary"
  }'
```

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Single test file
pytest tests/test_auth.py -v
```

Tests use **SQLite in-memory** – no MySQL required.

---

## 📁 Project Structure

```
.
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── config.py            # Dev / Test / Prod config
│   ├── models/              # SQLAlchemy ORM models
│   ├── routes/              # Flask blueprints (API endpoints)
│   ├── services/            # Business logic layer
│   ├── validators/          # Marshmallow input validation
│   ├── middleware/          # Auth, RBAC, error handling, logging
│   ├── cache/               # In-memory analytics cache
│   └── utils/               # Helpers: logger, response formatter
├── tests/                   # pytest test suite
├── run.py                   # Entry point + CLI commands
├── setup_db.py              # One-time DB initialisation
├── requirements.txt
├── .env.example
├── ARCHITECTURE.md
└── api_documentation.md
```

---

## 🔐 User Roles

| Role | Permissions |
|------|------------|
| **viewer** | Read own transactions, basic analytics |
| **analyst** | viewer + trends, reports, bulk import, exports |
| **admin** | analyst + user management, audit logs |

---

## 📡 API Overview

| Method | Path | Description | Role |
|--------|------|-------------|------|
| POST | `/api/auth/register` | Register | Public |
| POST | `/api/auth/login` | Login | Public |
| POST | `/api/auth/logout` | Logout | Auth |
| GET | `/api/auth/me` | Get profile | Auth |
| PUT | `/api/auth/me` | Update profile | Auth |
| GET | `/api/transactions/` | List + filter | Auth |
| POST | `/api/transactions/` | Create | Auth |
| GET | `/api/transactions/:id` | Get one | Auth |
| PUT | `/api/transactions/:id` | Update | Auth |
| DELETE | `/api/transactions/:id` | Delete | Auth |
| POST | `/api/transactions/bulk` | Bulk create | Analyst+ |
| GET | `/api/transactions/export/csv` | CSV export | Auth |
| GET | `/api/transactions/export/json` | JSON export | Auth |
| GET | `/api/transactions/search?q=` | Search | Auth |
| GET | `/api/analytics/dashboard` | KPI summary | Auth |
| GET | `/api/analytics/trends` | Month-over-month | Analyst+ |
| GET | `/api/analytics/categories` | Category breakdown | Auth |
| GET | `/api/analytics/monthly/:y/:m` | Monthly summary | Auth |
| GET | `/api/analytics/budget?month=` | Budget status | Auth |
| GET | `/api/analytics/report` | Full report | Analyst+ |
| GET | `/api/users/` | List users | Admin |
| GET | `/api/users/:id` | Get user | Admin |
| PUT | `/api/users/:id` | Update role/status | Admin |
| DELETE | `/api/users/:id` | Deactivate | Admin |
| GET | `/api/users/:id/audit-log` | Audit trail | Admin |

See `api_documentation.md` for full request/response examples.

