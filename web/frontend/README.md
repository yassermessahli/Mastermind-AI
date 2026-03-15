# web/frontend — React Frontend

React + TypeScript + Vite frontend for the Mastermind web app. Communicates with the Django backend via Axios.

---

## Running Locally

```bash
cp .env.example .env.local   # set VITE_API_URL
make frontend-install         # npm install
make frontend-dev             # Vite dev server on http://localhost:5173
```

The backend must be running at the URL specified in `VITE_API_URL`.

---

## Environment Variables

| Variable       | Description                                       | Example                      |
|----------------|---------------------------------------------------|------------------------------|
| `VITE_API_URL` | Base URL for the Django backend API               | `http://localhost:8001`      |

In Docker, `VITE_API_URL` is set to an empty string so Nginx proxies `/api/` requests to the backend container.

---

## Other Commands

```bash
make frontend-build    # production build → dist/
make frontend-lint     # ESLint
make frontend-preview  # preview the production build locally
```
