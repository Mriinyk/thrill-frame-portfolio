"""Select the settings module from the project-local environment."""

import os
from pathlib import Path

from decouple import AutoConfig


def configure_settings_module():
    config = AutoConfig(search_path=Path(__file__).resolve().parent)
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        config(
            "DJANGO_SETTINGS_MODULE",
            default=(
                "thrill_frame_web_portfolio_servis.settings.development"
            ),
        ),
    )
