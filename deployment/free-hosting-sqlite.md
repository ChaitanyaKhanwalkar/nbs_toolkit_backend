# Free Hosting With Bundled SQLite

This note covers lightweight backend hosting where the FastAPI app reads the
bundled SQLite database from the repository package.

It does not change scientific data, write migrations at startup, deploy Azure,
or deploy the Flutter frontend.

## Bundled Database

The bundled database path is:

```text
backend/data/narmada_nbs_canonical.db
```

If `DATABASE_URL` is not set, the backend falls back to this file using a
Linux-safe `pathlib` path. If `DATABASE_URL` is set, that value still takes
priority.

## Start Command

Use this start command on Render, Koyeb, or a similar Linux host:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

Set the service root or working directory to `backend` so `app.main:app` resolves
correctly.

## Environment Variables

Required:

```text
APP_ENV=production
CORS_ALLOW_ORIGINS=<frontend URL or * for temporary smoke testing>
```

Optional:

```text
DATABASE_URL=<override only if not using bundled SQLite>
LOG_LEVEL=INFO
```

Do not commit secrets. The bundled SQLite path needs no database password.

## Read-Only Safety

The backend does not run startup migrations or seeders. SQLite is used as a
read-only scientific evidence store by the API/repository layer; unknown removal
values remain unknown and are not converted to 0%.
