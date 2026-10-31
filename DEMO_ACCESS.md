# Demo access

The deployment can seed demo accounts for all three roles and sample
transactions during `python setup_db.py`.

## Credentials

Configure `ADMIN_PASSWORD`, `DEMO_PASSWORD`, and `VIEWER_PASSWORD` in the
deployment environment. The seeded accounts are:

| Username | Role | Password environment variable |
| --- | --- | --- |
| `admin` | admin | `ADMIN_PASSWORD` |
| `demo` | analyst | `DEMO_PASSWORD` |
| `viewer` | viewer | `VIEWER_PASSWORD` |

Passwords are intentionally not stored in this repository. For Render, open
the service's **Environment** settings, add all three variables, and redeploy.
The setup script is idempotent: it creates missing accounts, synchronizes an
existing account's password when its environment variable changes, and creates
sample transactions only when they do not already exist.

Log in through Swagger at `POST /api/auth/login`. Swagger will retain the
session cookie for subsequent authorized requests.

For local development, `flask --app run seed-data` creates all three accounts
with these temporary credentials:

| Username | Role | Password |
| --- | --- | --- |
| `admin` | admin | `Admin@1234` |
| `demo` | analyst | `Demo@1234` |
| `viewer` | viewer | `Viewer@1234` |
