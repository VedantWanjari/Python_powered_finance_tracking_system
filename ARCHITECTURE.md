# Architecture Decision Record

## Overview

This document explains the key architectural decisions made in the Finance Tracking System backend and the reasoning behind each choice.

---

## 1. Flask App Factory Pattern

**Decision**: Use `create_app(config_name)` instead of a module-level `app` object.

**Reasoning**:
- Multiple app instances can coexist (e.g. one using MySQL for production, one using SQLite for tests)
- Avoids circular imports: routes import `db` from `app`, which needs to exist before blueprints are registered
- Standard pattern in professional Flask codebases

---

## 2. Service Layer (Business Logic Separation)

**Decision**: All database queries and business rules live in `app/services/`, not in route handlers.

**Reasoning**:
- Routes only parse HTTP input and format HTTP output — no SQL
- Services are testable without an HTTP client (pure function calls)
- Easy to swap Flask for FastAPI or add a CLI interface without rewriting logic
- Single Responsibility Principle: each class has one job

---

## 3. Session-Based Authentication (vs JWT)

**Decision**: Flask session cookies (server-side signed cookies) instead of stateless JWT tokens.

**Reasoning**:
- Simpler to implement correctly — no token refresh logic, no expiry edge cases
- Sessions can be invalidated instantly (just clear the server-side session)
- JWT's stateless nature is a benefit for distributed systems, but this is a single-server app
- Flask sessions are cryptographically signed with `SECRET_KEY` so they cannot be tampered with

---

## 4. Custom Exception Hierarchy

**Decision**: `ResourceNotFound`, `Forbidden`, `ValidationError`, etc. all extend `AppError`.

**Reasoning**:
- Service methods raise typed exceptions; route handlers catch them with a single `except AppError`
- The global error handler maps each subclass to the correct HTTP status code
- No Flask imports needed in service code — pure Python domain objects

---

## 5. In-Memory Analytics Cache (vs Redis)

**Decision**: A custom `threading.Lock`-protected dict with TTL instead of Redis.

**Reasoning**:
- Redis adds an external infrastructure dependency (installation, configuration, connection management)
- For a single-process deployment, an in-memory cache eliminates the network round-trip
- The `AnalyticsCache` interface is identical to what a Redis adapter would expose — swapping it in later is a one-file change
- Cache is invalidated per-user on every write operation, keeping data fresh

---

## 6. Role Hierarchy (viewer < analyst < admin)

**Decision**: Three roles with inherited permissions instead of a flat permission list.

**Reasoning**:
- Mirrors real-world finance team structures (read-only stakeholders, analysts, admins)
- Hierarchy simplifies `require_role(*roles)` — "analyst or above" covers both analyst and admin
- Easy to extend: adding a "manager" role between analyst and admin is a small change

---

## 7. SQLite for Tests, MySQL for Production

**Decision**: `TestingConfig` uses `sqlite:///:memory:`, `DevelopmentConfig` uses MySQL.

**Reasoning**:
- Tests run without any external database service (CI/CD friendly, zero-setup for new contributors)
- SQLite and MySQL differ in some advanced features but are identical for standard CRUD + aggregations
- JSON tags are stored as `Text` (not native JSON type) for portability between both engines

---

## 8. Marshmallow for Validation (vs WTForms or Manual)

**Decision**: Marshmallow v3 schemas with `@validate_schema` decorator.

**Reasoning**:
- Separation of validation from route logic (decorator applies schema, route reads `g.validated_data`)
- Rich built-in field types: `fields.Email`, `fields.Date`, `fields.Decimal` with automatic coercion
- `@post_load` enables cross-field validation (e.g. `is_recurring` requires `recurring_frequency`)
- The same schema can validate both creation and partial updates (with `load_default=None`)

---

## 9. Audit Logging

**Decision**: Append-only `audit_logs` table written after every sensitive operation.

**Reasoning**:
- Compliance requirement for financial systems (who changed what, when)
- Debugging tool: full modification history for any transaction or user
- Failure to write an audit log must never break the main operation (wrapped in `try/except`)

---

## 10. Pagination on All List Endpoints

**Decision**: Every list endpoint accepts `page` and `per_page` parameters.

**Reasoning**:
- Unbounded queries on large datasets cause memory spikes and slow responses
- Consistent pagination metadata in every response lets front-end clients build generic list components
- `MAX_PAGE_SIZE = 100` prevents clients from accidentally fetching the entire database

---

## Scalability Considerations

| Concern | Current approach | Future upgrade path |
|---------|-----------------|---------------------|
| Caching | In-memory dict | Drop-in Redis adapter |
| Database | Single MySQL instance | Read replicas + connection pooling |
| Auth | Session cookies | Add JWT support for mobile clients |
| File export | In-memory CSV/JSON | Celery task + S3 presigned URLs |
| Rate limiting | In-process counter | Redis-backed limiter |
