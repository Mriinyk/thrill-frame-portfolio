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

Use `DEBUG=False` in production.

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
