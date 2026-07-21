# Digital Meetup

A Django landing page for the **Digital Meetup** event with a public registration flow and Django Admin for content management.

## Links

| Resource | URL |
|----------|-----|
| Live site | https://digital-meetup-rt7w.onrender.com/ *(update if your Render URL differs)* |
| Repository | https://github.com/SwiftXLight/digital-meetup |
| Admin panel | https://digital-meetup-rt7w.onrender.com//admin/ |

> Admin credentials are **not** stored in this repository. Share them separately with the reviewer (see [Admin access](#admin-access) below).

---

## Features

- Public landing page: event info, speakers, schedule, FAQ, registration form
- Server-side validation and duplicate-email protection (one email per event)
- Post-Redirect-Get (PRG) after successful registration
- Django Admin with search, filters, ordering, image previews, CSV export
- PostgreSQL locally and in production
- Deployed on Render (free tier)

---

## Architecture decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| App layout | Single app `event/` under project `config/` | One bounded context; keeps the 6–7h scope manageable |
| Active event | `Event.get_active()` returns latest event by date/time | Assignment targets a single-event landing page, not multi-event routing |
| Registration uniqueness | DB `UniqueConstraint(event, email)` + form `clean_email()` | Defense in depth; friendly error before DB integrity error |
| Registration flow | Post-Redirect-Get to `/register/success/` | Prevents duplicate submissions on page refresh |
| Settings split | `base.py` / `local.py` / `production.py` | Clean separation of dev and production config |
| Environment config | `django-environ` + `.env` (gitignored) | Secrets stay out of git |
| Static files (production) | WhiteNoise + `collectstatic` | No separate static server on Render |
| Media files (production) | Local filesystem (`MEDIA_ROOT`) | Simple setup; see [Known limitations](#known-limitations) for free-tier caveat |
| CSS / UI | Bootstrap 5 via CDN + minimal custom CSS | Fast to build; assignment does not require custom design |
| Local PostgreSQL | Docker Compose | Easy, reproducible local database setup |

### Project structure

```
digital-meetup/
├── config/                 # Django project settings, URLs, WSGI
│   └── settings/
│       ├── base.py
│       ├── local.py
│       └── production.py
├── event/                  # Models, forms, views, admin, services, tests
├── templates/              # Base and event templates
├── static/event/           # Custom CSS and placeholder image
├── docker-compose.yml      # Local PostgreSQL
├── render.yaml             # Render Blueprint (web + PostgreSQL)
├── requirements.txt
└── manage.py
```

---

## System requirements

- Python 3.11+ (3.13 used on Render)
- PostgreSQL 14+
- Git
- Docker (recommended for local PostgreSQL)

---

## Local setup

### 1. Clone and create virtualenv

```bash
git clone https://github.com/SwiftXLight/digital-meetup.git
cd digital-meetup
python -m venv .venv
```

**Windows (Git Bash):**
```bash
source .venv/Scripts/activate
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a real `SECRET_KEY` and `POSTGRES_PASSWORD`. Ensure the password in `DATABASE_URL` matches `POSTGRES_PASSWORD`.

### 4. Start PostgreSQL

```bash
docker compose up -d
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create admin user

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

Open:

- Landing page: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Seed content in admin (Event, Speakers, Schedule, FAQs) to populate the landing page.

---

## Running tests

```bash
python manage.py test
```

Tests cover:

1. Home page returns HTTP 200
2. Unpublished speakers/FAQs are hidden on the public page
3. Schedule item time validation (`end_time` must be after `start_time`)
4. Successful registration creates a DB record and redirects to success page
5. Duplicate email registration is blocked

---

## Production deployment (Render)

The project includes a [`render.yaml`](render.yaml) Blueprint that creates:

- Python web service (`gunicorn`)
- PostgreSQL database

### Deploy steps

1. Push the repository to GitHub
2. In Render: **New → Blueprint** → connect the repo
3. Approve the Blueprint (creates web service + database)
4. In the web service **Environment**, set (if not auto-filled):
   - `ALLOWED_HOSTS` = `your-app.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://your-app.onrender.com`
   - `DJANGO_SUPERUSER_USERNAME` = `admin`
   - `DJANGO_SUPERUSER_PASSWORD` = *(strong password)*
   - `DJANGO_SUPERUSER_EMAIL` = *(optional)*

`RENDER_EXTERNAL_HOSTNAME` is set automatically by Render and is used for `ALLOWED_HOSTS` / CSRF when present.

### Build / start commands (from `render.yaml`)

- **Build:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py ensure_superuser`
- **Start:** `gunicorn config.wsgi:application`

Migrations and superuser creation run in the build step because Render free tier does not support Shell or `preDeployCommand`.

### Create admin without Shell (free tier)

**Option A — environment variables (recommended):** set `DJANGO_SUPERUSER_*` vars and redeploy. The `ensure_superuser` command creates the account if it does not exist.

**Option B — local machine against production DB:** copy the **External Database URL** from Render PostgreSQL → run `python manage.py createsuperuser` locally with `DATABASE_URL` and `DJANGO_SETTINGS_MODULE=config.settings.production`.

---

## Admin access

Template for submission *(fill in and send separately, not in git)*:

```
URL:      https://digital-meetup.onrender.com/admin/
Username: admin
Password: <provided separately>
```

---

## Known limitations

| Limitation | Notes |
|------------|-------|
| Single active event | Public site shows one event (`Event.get_active()`). Multiple events can exist in admin, but only the latest by date is displayed. |
| Ephemeral media on Render free tier | Uploaded images may be lost after redeploy or restart. Database content persists. Persistent disk requires a paid Render plan. |
| No email confirmation | Registrations are saved to the database only; no email is sent to participants. |
| No spam protection | Registration form has CSRF protection but no CAPTCHA or rate limiting. |
| Render free tier cold starts | Service sleeps after inactivity; first request may take ~30–60 seconds. |
| Migrations in build step | On free tier, migrations run during `buildCommand` instead of a dedicated pre-deploy hook. |

---

## Optional extras

| Extra | Status |
|-------|--------|
| Docker Compose for local PostgreSQL | Implemented |
| Email confirmation | Not implemented |
| Spam protection (CAPTCHA) | Not implemented |
| Image optimization | Not implemented |
| Privacy policy page | Not implemented |
| Human-readable URLs (slugs) | Not implemented |
| SEO meta tags | Not implemented |
| Linter / formatter (ruff, pre-commit) | Not implemented |
| CI for tests on pull request | Not implemented |

---

## Environment variables

See [`.env.example`](.env.example) for the full list.

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | Yes | `True` locally, `False` in production |
| `ALLOWED_HOSTS` | Yes | Comma-separated hostnames |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `DJANGO_SETTINGS_MODULE` | Yes | `config.settings.local` or `config.settings.production` |
| `CSRF_TRUSTED_ORIGINS` | Production | HTTPS origins, e.g. `https://your-app.onrender.com` |
| `DJANGO_SUPERUSER_USERNAME` | Production | Admin username for first deploy |
| `DJANGO_SUPERUSER_PASSWORD` | Production | Admin password for first deploy |
| `DJANGO_SUPERUSER_EMAIL` | Optional | Admin email |
| `POSTGRES_PASSWORD` | Local Docker | Password for local PostgreSQL container |

---

## License

Test assignment project — no license specified.
