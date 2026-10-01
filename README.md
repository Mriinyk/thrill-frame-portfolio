# Thrill Frame Portfolio

Thrill Frame Portfolio is a Django website for presenting video productions and
photo sessions. Visitors can browse the portfolio, like works, leave comments,
and send a contact request through Telegram or Instagram.

The public website is Ukrainian. Source comments, project documentation, and
developer-facing messages use English.

## Requirements

- Python 3.12 or newer
- Django 5.2.13
- requests 2.27.1

## Setup

From the repository root:

```text
cd thrill_frame_web_portfolio_servis
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```text
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` before running the application. Django loads this
local file automatically; it is ignored by Git:

```text
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

The `.env` file next to `manage.py` selects the settings module:

```text
DJANGO_SETTINGS_MODULE=thrill_frame_web_portfolio_servis.settings.development
```

The development module uses SQLite and enables debug mode. Set
`DJANGO_SETTINGS_MODULE=thrill_frame_web_portfolio_servis.settings.production`
in the hosting provider's environment to use Neon PostgreSQL and production
security settings. Set `ALLOWED_HOSTS` there to the deployed hostnames, without
the URL scheme. `CSRF_TRUSTED_ORIGINS` takes full origins such as
`https://example.com` when needed.

On Windows PowerShell, set them for the current session with:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
$env:DEBUG = "True"
$env:TELEGRAM_BOT_TOKEN = "your-bot-token"
$env:TELEGRAM_CHAT_ID = "your-chat-id"
```

Apply migrations and start the development server:

```text
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser. Create an administrator with
`python manage.py createsuperuser` to manage portfolio content.

The production module always uses `DEBUG=False`. The `testing` module uses an
in-memory SQLite database and can be selected with
`DJANGO_SETTINGS_MODULE=thrill_frame_web_portfolio_servis.settings.testing`.

Before deploying, collect static files with the production settings selected:

```text
python manage.py collectstatic --noinput
```

Django collects both application assets and Django admin assets into
`staticsfile/`; WhiteNoise serves the compressed files in production.

## Render deployment

Create a Render Web Service with the repository root as its root directory.
Use these commands:

Build command:

```text
bash ./thrill_frame_web_portfolio_servis/build.sh
```

Start command:

```text
cd thrill_frame_web_portfolio_servis && gunicorn thrill_frame_web_portfolio_servis.wsgi:application --bind 0.0.0.0:$PORT
```

Set these environment variables in Render, using the values from Neon and the
hostname Render assigns to the service:

```text
DJANGO_SETTINGS_MODULE=thrill_frame_web_portfolio_servis.settings.production
SECRET_KEY=<a new, unique production secret>
ALLOWED_HOSTS=<service-name>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<service-name>.onrender.com
POSTGRES_DB=<Neon database name>
POSTGRES_PORT=5432
POSTGRES_USER=<Neon database user>
POSTGRES_PASSWORD=<Neon database password>
POSTGRES_HOST=<Neon direct endpoint hostname>
POSTGRES_SSLMODE=require
POSTGRES_CHANNEL_BINDING=require
TELEGRAM_BOT_TOKEN=<bot token>
TELEGRAM_CHAT_ID=<chat id>
```

Do not include URL schemes in `ALLOWED_HOSTS`; `CSRF_TRUSTED_ORIGINS` requires
the `https://` scheme. Keep `.env` files out of the repository.

Use the committed `.env.sample` as a checklist for Render's environment
variables; replace every placeholder with a service-specific value before
deploying.

## Tests

Run the test suite from `thrill_frame_web_portfolio_servis`:

```text
python manage.py test
```

Run the style checks before every push:

```text
python -m flake8 thrill_frame_web_portfolio_servis
```

The SQLite database is created locally by Django and is intentionally excluded
from version control. If it was tracked before, remove it from the index with
`git rm --cached db.sqlite3` and commit that change; the local file remains on
disk.
