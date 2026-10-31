# Demo access

The deployment can seed a non-administrator demo account and sample
transactions during `python setup_db.py`.

## Credentials

Configure `DEMO_PASSWORD` in the deployment environment. The account is:

```text
Username: demo
Role: analyst
Password: the value of DEMO_PASSWORD
```

The password is intentionally not stored in this repository. For Render,
open the service's **Environment** settings, add `DEMO_PASSWORD`, and redeploy.
The setup script is idempotent: it creates the demo user and sample
transactions only when they do not already exist.

Log in through Swagger at `POST /api/auth/login`. Swagger will retain the
session cookie for subsequent authorized requests.
