# Repository Guidelines

## Project Structure & Module Organization

This repository is a Cranfield information retrieval system with a FastAPI backend and Vue 3 frontend. Backend source lives in `backend/app/`: `main.py` wires the API, `engine.py` coordinates data and indexing, `routers/` exposes `/api` endpoints, and `core/` contains search, parsing, indexing, TF-IDF, Soundex, and highlighting logic. Frontend code lives in `frontend/src/`, with reusable views in `components/`, API calls in `api.js`, and global styles in `style.css`. Cranfield input files are in `data/`. Report sources, figures, and document scripts are in `report/`; packaged artifacts belong in `dist/`.

## Build, Test, and Development Commands

- `uv sync`: install Python dependencies from `pyproject.toml` and `uv.lock`.
- `uv run python -m uvicorn app.main:app --port 8000 --reload --app-dir backend`: run the backend API locally.
- `cd frontend && bun install`: install frontend dependencies.
- `cd frontend && bun run dev`: start Vite; it proxies `/api` to `localhost:8000`.
- `cd frontend && bun run build`: create the production frontend build.
- `./pack.sh`: create the packaged zip under `dist/`.
- `cd report && uv run --with python-docx build_docx.py`: rebuild `report.docx`.

## Coding Style & Naming Conventions

Use Python 3.12 syntax. Follow existing backend style: 4-space indentation, snake_case functions and variables, PascalCase classes, and package-relative imports inside `backend/app`. Vue files use `<script setup>`, 2-space indentation in templates/styles, PascalCase component filenames such as `BooleanSearch.vue`, and camelCase JavaScript identifiers. Keep generated report outputs and binary artifacts out of source changes unless explicitly needed.

## Testing Guidelines

There is no formal test suite configured yet. For backend changes, run the API and verify `GET /api/health` plus affected `/api/search/*` or `/api/index/*` endpoints. For frontend changes, run `bun run build` and manually check the affected Vite view. For ranking changes, compare representative Boolean, phrase, expanded, and Soundex queries against the Cranfield data.

## Commit & Pull Request Guidelines

Recent history uses Conventional Commits, for example `feat(eval): ...`, `docs(report): ...`, `refactor(report-build): ...`, and `chore: ...`. Keep subjects imperative and scoped when useful. Pull requests should describe behavior changes, list commands run, note generated files updated, and include screenshots or clips for UI changes.

## Security & Configuration Tips

Do not commit local virtualenvs, downloaded NLTK data, caches, or large demo media. The backend currently enables permissive CORS for local coursework use; tighten it before deploying outside a trusted environment.
