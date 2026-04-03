# API Documentation

Base URL: `http://localhost:5000`

All endpoints return JSON with this envelope:
```json
{
  "status":    "success" | "error",
  "message":   "Human-readable message",
  "data":      { ... } | null,
  "timestamp": "2024-03-15T10:30:00Z"
}
```

Error responses additionally include `error_id` (UUID for log correlation) and optionally `errors` (field-level validation errors).

---

## Authentication

Session-based. Login sets an HTTP-only signed cookie. Include the cookie on all subsequent requests.

### POST /api/auth/register
Create a new account.

**Request:**
```json
{
  "username": "vedant",
  "email": "vedant@example.com",
  "password": "Secure@123"
}
```
Password rules: ≥8 chars, 1 uppercase, 1 digit, 1 special character.

**Response 201:**
```json
{
  "status": "success",
  "data": { "id": 1, "username": "vedant", "email": "vedant@example.com", "role": "viewer" }
}
```

---

### POST /api/auth/login
Authenticate and receive a session cookie.

**Request:**
```json
{ "username": "vedant", "password": "Secure@123" }
```

**Response 200:** Returns user object + sets `session` cookie.

---

### POST /api/auth/logout
Clear session. **Auth required.**

---

### GET /api/auth/me
Return current user's profile. **Auth required.**

---

### PUT /api/auth/me
Update email or username. **Auth required.**

**Request (all optional):**
```json
{ "email": "new@example.com", "username": "newname" }
```

---

## Transactions

### GET /api/transactions/
List transactions with filters. **Auth required.**

**Query params:**

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default 1) |
| `per_page` | int | Items per page (default 20, max 100) |
| `sort_by` | string | `date` \| `amount` \| `created` |
| `sort_order` | string | `asc` \| `desc` |
| `date_from` | date | YYYY-MM-DD |
| `date_to` | date | YYYY-MM-DD |
| `transaction_type` | string | `income` \| `expense` |
| `category_id` | int | Filter by category |
| `amount_min` | float | Minimum amount |
| `amount_max` | float | Maximum amount |
| `search` | string | Full-text search on description + notes |
| `tags` | string | Comma-separated tag names |

**Response 200:**
```json
{
  "status": "success",
  "data": [ { "id": 1, "amount": 150.00, "transaction_type": "expense", ... } ],
  "pagination": { "total": 50, "page": 1, "per_page": 20, "total_pages": 3, "has_next": true, "has_prev": false }
}
```

---

### POST /api/transactions/
Create a transaction. **Auth required.**

**Request:**
```json
{
  "amount": 150.00,
  "transaction_type": "expense",
  "date": "2024-03-15",
  "description": "Grocery run",
  "category_id": 1,
  "notes": "Weekly shop at Tesco",
  "tags": ["food", "weekly"],
  "is_recurring": false
}
```

**Response 201:** Returns created transaction object.

---

### GET /api/transactions/:id
Get a single transaction. **Auth required.** Only the owner can access.

---

### PUT /api/transactions/:id
Update a transaction. **Auth required.** All fields optional.

---

### DELETE /api/transactions/:id
Delete a transaction permanently. **Auth required.**

---

### POST /api/transactions/bulk
Bulk create transactions. **Analyst+ required.**

**Request:**
```json
{
  "transactions": [
    { "amount": 100, "transaction_type": "expense", "date": "2024-03-01", "description": "Item 1" },
    { "amount": 200, "transaction_type": "expense", "date": "2024-03-02", "description": "Item 2" }
  ]
}
```

---

### GET /api/transactions/export/csv
Download transactions as CSV. **Auth required.**

Same filter query params as list endpoint. Returns `Content-Disposition: attachment` response.

---

### GET /api/transactions/export/json
Download transactions as JSON file. **Auth required.**

---

### GET /api/transactions/search?q=
Full-text search on description and notes. **Auth required.**

---

## Analytics

### GET /api/analytics/dashboard
High-level financial summary. **Auth required.** Cached 5 min.

**Response:**
```json
{
  "data": {
    "total_income": 5000.00,
    "total_expenses": 1200.00,
    "net_balance": 3800.00,
    "transaction_count": 15,
    "recent_transactions": [ ... ]
  }
}
```

---

### GET /api/analytics/trends?months=6
Month-over-month trend. **Analyst+ required.**

**Response:**
```json
{
  "data": [
    { "month": "2024-01", "income": 5000, "expenses": 1200, "net": 3800 },
    { "month": "2024-02", "income": 5000, "expenses": 1500, "net": 3500 }
  ]
}
```

---

### GET /api/analytics/categories
Expense breakdown by category. **Auth required.**

Optional: `?start_date=2024-01-01&end_date=2024-03-31`

**Response:**
```json
{
  "data": [
    { "category_id": 1, "category_name": "Food", "total": 450.00, "percentage": 37.5 }
  ]
}
```

---

### GET /api/analytics/monthly/:year/:month
Monthly summary. **Auth required.**

Example: `GET /api/analytics/monthly/2024/3`

---

### GET /api/analytics/budget?month=2024-03
Budget vs actual for a given month. **Auth required.**

---

### GET /api/analytics/report
Comprehensive report (dashboard + trends + categories). **Analyst+ required.**

---

## User Management (Admin only)

### GET /api/users/
List all users. Paginated.

### GET /api/users/:id
Get a specific user.

### PUT /api/users/:id
Update role or active status.

```json
{ "role": "analyst", "is_active": true }
```

### DELETE /api/users/:id
Deactivate (soft-delete) a user.

### GET /api/users/:id/audit-log
Return the user's audit trail (paginated).

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request / validation failed |
| 401 | Not authenticated (no session) |
| 403 | Authenticated but insufficient role |
| 404 | Resource not found |
| 409 | Conflict (e.g. duplicate username) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Rate Limits

Default: **100 requests per minute** per IP address (configurable via `RATELIMIT_DEFAULT` in `.env`).
