# Python-Powered Finance Tracking System

A portfolio-ready finance tracking project with:
- **Flask REST API backend** (session-based auth)
- **Static dashboard frontend** in `docs/` for GitHub Pages
- Transaction CRUD, bulk import, CSV/JSON export, filters, search, and pagination
- Role-based access control, audit logging, analytics, and in-memory caching
- Explainable insights including savings rate, average expense, top category, and trends
- Automated regression tests for authentication, transactions, validation, and analytics

## GitHub Pages Frontend

This repository is configured to host the frontend from `docs/` via GitHub Pages.

- Main UI entry: `docs/index.html`
- Styling: `docs/css/style.css`
- App logic: `docs/js/app.js`
- API layer: `docs/js/api-client.js`

> The frontend calls your Flask API (default: `http://localhost:5000`) and uses cookies for authenticated requests.

## Quick Start (Local)

### 1) Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export ADMIN_PASSWORD='Use-a-strong-local-password'
python setup_db.py
python run.py
```

Backend runs on **http://localhost:5000**.

### 2) Frontend setup

Use any static server from repository root, for example:

```bash
python -m http.server 8000
```

Open **http://localhost:8000/docs/** and use the UI.

The setup script creates the `admin` account only when `ADMIN_PASSWORD` is set.
Never commit `.env` or share this password.

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

The project also includes a GitHub Actions workflow that runs the test suite on
pushes and pull requests.

## GitHub Pages Deployment

- Workflow: `.github/workflows/deploy.yml`
- Pages content: `docs/`
- Jekyll config: `docs/_config.yml`
- Additional Pages settings: `.github/pages/config.yml`

Enable Pages in repository settings to deploy from GitHub Actions.

## Portfolio Sharing Notes

- Share your repository URL and GitHub Pages URL.
- Mention that backend runs separately (locally or on your own host).
- Include API base URL details when demoing.

## Project Structure

```text
.
├── app/
├── tests/
├── docs/
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js
│   ├── js/api-client.js
│   └── _config.yml
├── .github/
│   ├── workflows/deploy.yml
│   └── pages/config.yml
├── run.py
├── setup_db.py
└── requirements.txt
```
