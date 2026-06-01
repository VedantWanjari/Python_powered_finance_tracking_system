# Frontend Setup Guide

This guide explains how to run and deploy the static frontend in `docs/`.

## Files

- `docs/index.html` - UI shell and sections
- `docs/css/style.css` - frontend styling
- `docs/js/api-client.js` - API communication helper
- `docs/js/app.js` - state management and UI logic

## Run Frontend Locally

1. Start backend:

```bash
python run.py
```

2. Serve static files from repository root:

```bash
python -m http.server 8000
```

3. Open:

- `http://localhost:8000/docs/`

The frontend uses `http://localhost:5000` as default API URL.

## Authentication

- Uses Flask session cookies.
- Login and registration are available in the UI.
- All API calls send credentials with `fetch(..., { credentials: "include" })`.

## GitHub Pages Deployment

1. Ensure workflow exists: `.github/workflows/deploy.yml`.
2. In GitHub repository settings, enable **Pages** with source **GitHub Actions**.
3. Push to `main` to trigger deployment.

## Notes for Portfolio Demos

- GitHub Pages serves only frontend static files.
- Backend API must run separately (local machine or your own deployment).
- If backend is hosted elsewhere, update `localStorage.apiBaseUrl` in browser dev tools or adjust `DEFAULT_BASE_URL` in `docs/js/api-client.js`.
