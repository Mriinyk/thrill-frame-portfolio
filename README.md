# Thrill Frame Portfolio

Thrill Frame Portfolio is a Django website for presenting video productions and
photo sessions. Visitors can browse the portfolio, like works, leave comments,
and send a contact request through Telegram or Instagram.

The public website is Ukrainian. Source comments, project documentation, and
developer-facing messages use English.

## Requirements

- Python 3.12 or newer
- Django 6.1.1
- `requests`

## Setup

From the repository root:

```text
cd thrill_frame_web_portfolio_servis
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```text
python -m pip install --upgrade pip
python -m pip install django requests
```

Set the optional Telegram configuration before running the application:

```text
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

Apply migrations and start the development server:

```text
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser. Create an administrator with
`python manage.py createsuperuser` to manage portfolio content.

## Tests

Run the test suite from `thrill_frame_web_portfolio_servis`:

```text
python manage.py test
```

The SQLite database is created locally by Django and is intentionally excluded
from version control.
