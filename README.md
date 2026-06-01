# Python-Powered Finance Tracking System

A portfolio-ready finance tracking project with:
- **Flask REST API backend** (session-based auth)
- **Static dashboard frontend** in `docs/` for GitHub Pages

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

## Demo Credentials

After `setup_db.py`, default admin user:
- username: `admin`
- password: `Admin@1234`

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

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
