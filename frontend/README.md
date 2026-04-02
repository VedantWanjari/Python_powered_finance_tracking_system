# Finance Tracker — Frontend

A React 18 + TypeScript + Vite frontend for the Python-powered Finance Tracking System.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 18 + TypeScript |
| Build | Vite 5 |
| Styling | Tailwind CSS 3 (dark mode via `class`) |
| Routing | React Router v6 |
| State | Zustand |
| HTTP | Axios (`withCredentials: true`) |
| Charts | Recharts |
| Icons | Lucide React |
| Dates | date-fns |

## Quick Start

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Make sure the Flask backend is running on `http://localhost:5000`.

## Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start dev server (port 3000) |
| `npm run build` | Type-check + production build |
| `npm run preview` | Preview production build |
| `npm run lint` | ESLint check |

## Project Structure

```
src/
├── types/          # TypeScript interfaces
├── services/
│   └── api.ts      # Axios client + all API functions
├── store/
│   └── authStore.ts  # Zustand auth store
├── utils/
│   ├── formatters.ts
│   └── validators.ts
├── components/
│   ├── Common/     # Loading, ErrorAlert, Modal
│   ├── Layout/     # MainLayout, Header, Sidebar, ThemeToggle
│   ├── Auth/       # Login, Register, ProtectedRoute
│   ├── Dashboard/  # Dashboard, KPICard, RecentTransactions
│   ├── Transactions/ # TransactionList, TransactionForm, …
│   └── Analytics/  # TrendChart, CategoryChart, MonthlyReport
└── pages/          # DashboardPage, TransactionsPage, …
```

## API Integration

- All requests go to `/api/*` and are **proxied** to `http://localhost:5000` by Vite.
- Session authentication via HTTP-only cookies — `withCredentials: true` is set globally.
- The Zustand `authStore` calls `fetchMe()` on startup to restore an existing session.

## Dark Mode

Tailwind's `class` strategy is used. Toggle the `dark` class on `<html>` (done by `ThemeToggle`).  
Preference is persisted in `localStorage` under the key `"theme"`.

## Role-based Access

| Feature | viewer | analyst | admin |
|---|---|---|---|
| Dashboard | ✅ | ✅ | ✅ |
| Transactions | ✅ | ✅ | ✅ |
| Trend analytics | ❌ | ✅ | ✅ |
| Monthly report | ❌ | ✅ | ✅ |

Analyst/Admin-only analytics sections display a graceful message instead of an error for viewer-role users.
