# Python-Powered Finance Tracking System

A production-grade REST API backend for personal finance tracking, built with **Flask + MySQL + SQLAlchemy**.

This project was built as a submission for the **Python Developer Intern** assignment. It satisfies every core requirement of the spec — financial records CRUD, analytics/summaries, role-based access (viewer / analyst / admin), input validation, error handling, and a full test suite — plus several optional enhancements (pagination, search, CSV/JSON export, audit logging, in-memory analytics cache).

---

## 🔖 Assumptions Made

The assignment left several design decisions open. Here is what was assumed and why:

| Decision | Assumption & Reasoning |
|----------|------------------------|
| **Auth mechanism** | Session cookies (Flask signed cookies) over JWT. Simpler to implement correctly for a single-server app; sessions can be invalidated instantly without a token blacklist. |
| **Database for production** | MySQL 8.0. The schema uses only standard SQL so it also works with PostgreSQL without changes. |
| **Database for tests** | SQLite in-memory, so the test suite runs with zero external dependencies (`pytest tests/ -v`). |
| **Amount precision** | `DECIMAL(10, 2)` — up to 99 999 999.99, which comfortably covers personal finance amounts. |
| **Tags storage** | JSON string in a `Text` column (not a native JSON column) for portability between MySQL and SQLite. |
| **Role model** | Three-level hierarchy (viewer < analyst < admin) that inherits upward. Admin gets everything analyst gets; analyst gets everything viewer gets. |
| **Soft-delete for users** | Deactivating a user sets `is_active = False` rather than deleting the row, so their transaction history and audit trail remain intact. |
| **Caching** | In-memory `threading.Lock`-protected dict with TTL instead of Redis, to avoid an extra infrastructure dependency. The interface is Redis-compatible for a future upgrade. |
| **Audit logging** | Every create / update / delete on transactions and users writes an append-only row to `audit_logs`. Audit write failures never break the main operation. |
| **Pagination cap** | `MAX_PAGE_SIZE = 100` prevents accidentally fetching the entire database in one request. |
| **`budget_month` field** | Stored as `"YYYY-MM"` string rather than a date range to allow transactions to be explicitly tagged to a budget period that may differ from their actual date. |

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
# Login (saves session cookie to cookies.txt)
curl -c cookies.txt -b cookies.txt -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@1234"}'

# Create a transaction (uses the session cookie saved above)
curl -b cookies.txt -X POST http://localhost:5000/api/transactions/ \
  -H "Content-Type: application/json" \
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

```text
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

---

## 🖥️ API Reference

> Make sure the server is running (`python run.py`) before executing these commands.  
> All requests that require authentication use a session cookie stored in `cookies.txt`.

---

### 🔐 Authentication

**Register**
```bash
curl -c cookies.txt -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"Pass@1234"}'
```

**Login**
```bash
curl -c cookies.txt -b cookies.txt -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Pass@1234"}'
```

**View your profile**
```bash
curl -b cookies.txt http://localhost:5000/api/auth/me
```

**Update your profile**
```bash
curl -b cookies.txt -X PUT http://localhost:5000/api/auth/me \
  -H "Content-Type: application/json" \
  -d '{"email":"newemail@example.com","username":"alice_new"}'
```

**Logout**
```bash
curl -b cookies.txt -X POST http://localhost:5000/api/auth/logout
```

---

### 💸 Transactions

**Create a record**
```bash
curl -b cookies.txt -X POST http://localhost:5000/api/transactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "transaction_type": "expense",
    "date": "2024-03-15",
    "description": "Grocery shopping",
    "category_id": 1,
    "notes": "Weekly groceries",
    "tags": ["food", "weekly"]
  }'
```
> `transaction_type` must be `"income"` or `"expense"`

**View all records (paginated)**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/?page=1&per_page=20"
```

**View a single record by ID**
```bash
curl -b cookies.txt http://localhost:5000/api/transactions/42
```

**Update a record**
```bash
curl -b cookies.txt -X PUT http://localhost:5000/api/transactions/42 \
  -H "Content-Type: application/json" \
  -d '{"amount": 650, "description": "Updated grocery run", "category_id": 2}'
```

**Delete a record**
```bash
curl -b cookies.txt -X DELETE http://localhost:5000/api/transactions/42
```

---

### 🔍 Filter Records

**By date range**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/?date_from=2024-01-01&date_to=2024-03-31"
```

**By category**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/?category_id=1"
```

**By type**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/?transaction_type=expense"
```

**By amount range**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/?amount_min=100&amount_max=1000"
```

**By tag**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/?tags=food"
```

**Search by keyword**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/search?q=grocery"
```

**Combine multiple filters**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/?date_from=2024-01-01&date_to=2024-12-31&transaction_type=expense&category_id=1&sort_by=amount&sort_order=desc&page=1&per_page=10"
```

**All filter parameters**

| Parameter | Example | Description |
|-----------|---------|-------------|
| `date_from` | `2024-01-01` | Start date (YYYY-MM-DD) |
| `date_to` | `2024-12-31` | End date (YYYY-MM-DD) |
| `transaction_type` | `income` / `expense` | Type of transaction |
| `category_id` | `1` | Category ID |
| `amount_min` | `100` | Minimum amount |
| `amount_max` | `5000` | Maximum amount |
| `search` | `grocery` | Keyword in description |
| `tags` | `food` | Tag filter |
| `sort_by` | `date` / `amount` | Sort field |
| `sort_order` | `asc` / `desc` | Sort direction |
| `page` | `1` | Page number |
| `per_page` | `20` | Records per page |

---

### 📤 Export & Bulk

**Export as CSV**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/export/csv?date_from=2024-01-01&date_to=2024-12-31&transaction_type=expense" \
  -o transactions.csv
```

**Export as JSON**
```bash
curl -b cookies.txt "http://localhost:5000/api/transactions/export/json?date_from=2024-01-01&date_to=2024-12-31" \
  -o transactions.json
```

**Bulk create transactions** *(analyst / admin only)*
```bash
curl -b cookies.txt -X POST http://localhost:5000/api/transactions/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {"amount": 200, "transaction_type": "expense", "date": "2024-03-01", "description": "Coffee"},
      {"amount": 3000, "transaction_type": "income",  "date": "2024-03-05", "description": "Salary"}
    ]
  }'
```

---

### 📊 Analytics & Reports

**Dashboard summary**
```bash
curl -b cookies.txt http://localhost:5000/api/analytics/dashboard
```

**Category breakdown**
```bash
curl -b cookies.txt "http://localhost:5000/api/analytics/categories?start_date=2024-01-01&end_date=2024-03-31"
```

**Monthly breakdown**
```bash
curl -b cookies.txt http://localhost:5000/api/analytics/monthly/2024/3
```

**Budget status**
```bash
curl -b cookies.txt "http://localhost:5000/api/analytics/budget?month=2024-03"
```

**Trend analysis — last N months** *(analyst / admin only)*
```bash
curl -b cookies.txt "http://localhost:5000/api/analytics/trends?months=6"
```

**Full report** *(analyst / admin only)*
```bash
curl -b cookies.txt "http://localhost:5000/api/analytics/report?months=3"
```

---

### 👥 User Management *(admin only)*

**List all users**
```bash
curl -b cookies.txt "http://localhost:5000/api/users/?page=1&per_page=20"
```

**View a specific user**
```bash
curl -b cookies.txt http://localhost:5000/api/users/5
```

**Update a user's role or status**
```bash
curl -b cookies.txt -X PUT http://localhost:5000/api/users/5 \
  -H "Content-Type: application/json" \
  -d '{"role": "analyst", "is_active": true}'
```
> `role` must be `viewer`, `analyst`, or `admin`

**Deactivate a user**
```bash
curl -b cookies.txt -X DELETE http://localhost:5000/api/users/5
```

**View a user's audit log**
```bash
curl -b cookies.txt "http://localhost:5000/api/users/5/audit-log?page=1&per_page=20"
```

---

### 🛠️ One-Time CLI Setup

```bash
# Initialize database tables
flask init-db

# Create an admin user interactively
flask create-admin

# Seed default categories and a demo user with sample transactions
flask seed-data

# Full setup in one command (tables + categories + admin/Admin@1234)
python setup_db.py
```

