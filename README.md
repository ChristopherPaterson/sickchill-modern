# SickChill Modern

A modern, mobile-first reimplementation of a TV show automation manager. Built
from scratch, inspired by SickChill but without the legacy: a clean async API, a
proper service layer, JWT auth, and an installable mobile-first PWA frontend.

This is a **scaffold**. The architecture, auth, data layer, scheduler, API and UI
shell are working and tested. The domain-heavy pieces (indexer metadata lookup,
search providers, post-processing, download-client integration) are defined as
clean interfaces with `TODO` markers, ready to fill in.

## Stack

| Layer      | Choice                                                            |
|------------|------------------------------------------------------------------|
| Backend    | Python 3.12, FastAPI (async), SQLAlchemy 2.0 async, Alembic      |
| Scheduler  | APScheduler (asyncio), shares the API event loop                 |
| Auth       | JWT bearer tokens, bcrypt password hashing                       |
| Frontend   | Vue 3 + Vite + TypeScript, Pinia, Vue Router, PWA                |
| Packaging  | Multi-stage Docker, non-root, single container serves API + UI   |

## Project layout

```
sickchill-modern/
  backend/
    app/
      api/routes/      REST routes (auth, shows, episodes, search, history, settings, system)
      core/            security (JWT, bcrypt)
      db/              async engine, session, declarative base
      models/          SQLAlchemy models (Show, Episode, History, Setting, User)
      schemas/         Pydantic request/response models
      services/        business logic (the service layer SickChill never had)
      providers/       search-provider interface + registry + example stub
      indexers/        metadata-source interface (TVDB/TMDB/TVMaze)
      scheduler/       APScheduler setup + job bodies
      config.py        env-driven settings
      main.py          app entry point (lifespan, CORS, static serving)
    alembic/           database migrations
    tests/             smoke tests
  frontend/
    src/
      api/             axios client + types
      stores/          Pinia stores (auth, shows)
      router/          routes + auth guard
      components/      AppLayout, BottomNav
      views/           Login, Shows, ShowDetail, Calendar, History, Settings
  docker/Dockerfile    one-shot combined image
  docker-compose.yml
```

## Quick start (development)

Two terminals. The Vite dev server proxies `/api` to the backend.

```bash
# Terminal 1: backend
make backend-install
SCM_ADMIN_PASSWORD=changeme make backend-dev      # http://localhost:8080

# Terminal 2: frontend
make frontend-install
make frontend-dev                                  # http://localhost:5173
```

Log in with `admin` / the password you set in `SCM_ADMIN_PASSWORD` (default `admin`).
API docs are at http://localhost:8080/docs.

## Production (Docker, e.g. Synology)

```bash
# Set real secrets in docker-compose.yml first, then:
docker compose build
docker compose up -d                               # http://host:8080
```

The combined image builds the SPA and serves it from FastAPI, so it is a single
container. Data (database + config) persists in the `./data` volume. Mount your
media library as shown in `docker-compose.yml`.

## What is done vs. what to build

**Done and tested**
- Async app boots, health endpoints, OpenAPI docs
- JWT login, bcrypt hashing, auth-guarded routes, first-run admin creation
- Shows/episodes/history/settings CRUD against SQLite (async SQLAlchemy)
- APScheduler wired with daily/backlog/update jobs
- Mobile-first PWA shell: login, shows grid, show detail, history, bottom nav
- Multi-stage non-root Docker, docker-compose

**To build (clean interfaces are in place)**
- `app/indexers/` — implement a TVDB/TMDB client (`Indexer.search` / `get_show`)
- `app/providers/` — implement real search providers (copy `example.py`); the
  contract requires logging failures, never silently swallowing them
- `app/services/search_service.py` — ranking + snatching + download-client handoff
- `app/services/show_service.create_show` — populate metadata + episodes on add
- Post-processing (rename/move downloaded files), notifications
- Calendar/upcoming endpoint and the Settings UI

## Security notes (deliberate fixes over SickChill)

- JWT with a pinned algorithm and expiry; no API key in the URL
- bcrypt password hashing with constant-time verification
- CORS locked to configured origins (not `*`)
- Container runs as a non-root user
- Auto-generated SQL via the ORM (parameterised), no string-built queries
