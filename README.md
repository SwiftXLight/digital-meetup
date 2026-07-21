# Digital Meetup

A Django landing page for the **Digital Meetup** event with a public registration flow and Django Admin for content management.

## Links

| Resource | URL |
|----------|-----|
| Live site | https://digital-meetup-rt7w.onrender.com/ *(update if your Render URL differs)* |
| Repository | https://github.com/SwiftXLight/digital-meetup |
| Admin panel | https://digital-meetup-rt7w.onrender.com/admin/ |

> Admin credentials are **not** stored in this repository. Share them separately with the reviewer (see [Admin access](#admin-access) below).

---

## Features

- Public landing page: event info, speakers, schedule, FAQ, registration form
- Server-side validation and duplicate-email protection (one email per event)
- Post-Redirect-Get (PRG) after successful registration
- Django Admin with search, filters, ordering, image previews, CSV export
- `seed_demo_data` management command for quick demo content
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
│   └── management/commands/  # ensure_superuser, seed_demo_data
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

### 7. Load demo content (optional)

Populate the landing page with sample event data:

```bash
python manage.py seed_demo_data
```

This creates:

- One event (**Digital Meetup 2026**) with schedule items
- Two published speakers and one unpublished draft speaker
- Two published FAQs and one unpublished draft FAQ

The command is **idempotent**: if the demo event already exists, it skips and prints a warning. To replace demo data:

```bash
python manage.py seed_demo_data --force
```

To remove demo data only:

```bash
python manage.py seed_demo_data --clear
```

Images are not uploaded by the seed script — the site shows placeholder graphics until you add cover/speaker photos in admin (see [Media files on Render](#media-files-on-render-free-tier) below).

### 8. Run development server

```bash
python manage.py runserver
```

Open:

- Landing page: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

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

- **Build:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py ensure_superuser && python manage.py seed_demo_data`
- **Start:** `gunicorn config.wsgi:application`

Migrations, superuser creation, and demo seeding run in the build step because Render free tier does not support Shell or `preDeployCommand`.

### Demo content on Render

**Automatic (recommended):** each deploy runs `seed_demo_data` at the end of the build. The command is **idempotent** — it creates the demo event, speakers, schedule, and FAQs only if **Digital Meetup 2026** is not already in the database. Later deploys skip seeding and leave your data unchanged.

To populate a **fresh** Render database: push this repo and redeploy (or trigger **Manual Deploy** in the Render dashboard). After the build finishes, open your live site — you should see event text, speakers, schedule, and FAQ (placeholder images until you upload photos in admin).

**Manual (without redeploy):** if the site is already deployed but empty, seed from your machine using Render’s **External Database URL**:

```bash
# Git Bash / macOS / Linux
export DATABASE_URL="postgresql://..."   # Render → PostgreSQL → External Database URL
export DJANGO_SETTINGS_MODULE=config.settings.production
export SECRET_KEY=any-temp-value-for-local-run
export ALLOWED_HOSTS=localhost

python manage.py seed_demo_data
```

```powershell
# PowerShell
$env:DATABASE_URL = "postgresql://..."
$env:DJANGO_SETTINGS_MODULE = "config.settings.production"
$env:SECRET_KEY = "any-temp-value-for-local-run"
$env:ALLOWED_HOSTS = "localhost"

python manage.py seed_demo_data
```

Use `--force` only if you want to **replace** existing demo rows. Seeding is **text only** (no image files), so the landing page works on Render free tier without persistent media.

**To disable auto-seed on deploy:** remove `&& python manage.py seed_demo_data` from `buildCommand` in `render.yaml`.

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
| Ephemeral media on Render free tier | See [Media files on Render](#media-files-on-render-free-tier) below. |
| No email confirmation | Registrations are saved to the database only; no email is sent to participants. |
| No spam protection | Registration form has CSRF protection but no CAPTCHA or rate limiting. |
| Render free tier cold starts | Service sleeps after inactivity; first request may take ~30–60 seconds. |
| Migrations in build step | On free tier, migrations run during `buildCommand` instead of a dedicated pre-deploy hook. |

### Media files on Render (free tier)

On Render’s **free** web tier, the filesystem is **ephemeral**: files written to `MEDIA_ROOT` (event covers, speaker photos) live on the container disk and **may disappear after a redeploy, restart, or instance swap**. PostgreSQL data (events, text fields, registrations) persists; only uploaded binary files are at risk.

This project intentionally uses **placeholder images** in templates when no upload is present, and `seed_demo_data` seeds text content without attaching files — so the landing page stays usable even without persistent media.

**What we would do in a real project (or with more time):**

| Approach | When to use | Notes |
|----------|-------------|-------|
| **Object storage (recommended)** | Production on any PaaS | Store uploads in **S3**, **Cloudflare R2**, or **Backblaze B2** via `django-storages` + `boto3`. Media survives deploys; CDN-friendly; standard for Django production. |
| **Render persistent disk** | Stay on Render, few uploads | Mount a paid persistent disk at e.g. `/var/data/media` and set `MEDIA_ROOT`. Simpler than S3, but tied to one host and not ideal for multi-instance scaling. |
| **External image URLs** | Marketing-heavy sites | Keep images on a CMS/CDN; store URLs in the model instead of `ImageField` uploads. |
| **Commit static marketing assets** | Fixed branding only | Ship hero/speaker images under `static/` (versioned in git). Good for logos; bad for admin-uploaded content. |

**Concrete next steps for this codebase:**

1. Add `django-storages` and configure `DEFAULT_FILE_STORAGE` to S3/R2 in `production.py`.
2. Move secrets (`AWS_ACCESS_KEY_ID`, `AWS_STORAGE_BUCKET_NAME`, etc.) to Render environment variables.
3. Optionally add image validation/thumbnails (Pillow or `easy-thumbnails`) before upload.
4. Keep WhiteNoise for **static** files; use object storage only for **media** uploads.

For this test assignment, ephemeral media on the free tier is an accepted trade-off and is documented here for reviewers.

---

## Optional extras

| Extra | Status |
|-------|--------|
| Docker Compose for local PostgreSQL | Implemented |
| Demo data seed command | Implemented (`seed_demo_data`) |
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
