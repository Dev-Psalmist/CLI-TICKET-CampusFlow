# CampusFlow Vercel Web App

This folder is the Vercel deployment root for the CampusFlow migration.

## Runtime
- FastAPI application: `app.py`
- Dependencies: `requirements.txt`
- Browser UI: `templates/index.html`, `static/app.css`, `static/app.js`
- Existing ticket data preserved in `seed_tickets.json`

## Required Vercel environment variables
- `DATABASE_URL`: Neon/Postgres connection string (required for persistent production ticket storage)
- At least one AI provider key: `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENROUTER_API_KEY`

The application deliberately refuses to fall back to local SQLite on Vercel because Vercel Functions do not provide durable local disk storage.

## Local development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```
